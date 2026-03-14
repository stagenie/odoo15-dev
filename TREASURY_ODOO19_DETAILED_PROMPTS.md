# PROMPTS DETAILLES - Migration Tresorerie Odoo 15 vers Odoo 19
# Analyse complete de 15 modules → 7 modules consolides

---

## TABLE DE CONSOLIDATION

| Module Odoo 19 | Modules Odoo 15 fusionnes | Prompt |
|---|---|---|
| `adi_treasury` | `adi_treasury` | PROMPT 1 |
| `adi_treasury_bank` | `adi_treasury_bank` + `adi_bank_payment_mode` | PROMPT 2 |
| `adi_treasury_cashcount` | `adi_treasury_cashcount` + `_extended` + `_init` | PROMPT 3 |
| `adi_treasury_dashboard` | `adi_treasury_dashboard` + `_extended` + `_balance_display` | PROMPT 4 |
| `adi_treasury_control` | `adi_treasury_transfer_control` + `_access` + `_payment_partner_restrict` + `adi_transfert_control` | PROMPT 5 |
| `adi_treasury_enhanced` | `adi_treasury_enhanced` | PROMPT 6 |
| `adi_cash_expense` | `adi_cash_expense` | PROMPT 7 |

---

## PROMPT 1 — Module Core : `adi_treasury`

Creer un module Odoo 19 `adi_treasury` (version 19.0.1.0.0) de gestion de tresorerie avancee.
Categorie: Accounting/Treasury. Licence: LGPL-3. Dependances: base, account.
Dependance externe Python: num2words.
Ce module doit etre une application (application=True).

### Modeles a creer :

#### 1. treasury.cash (Caisse)
Champs :
- `name` (Char, required, tracking) - Nom de la caisse
- `code` (Char, required, tracking) - Code unique
- `currency_id` (Many2one res.currency, required)
- `company_id` (Many2one res.company, required, default=lambda self: self.env.company)
- `responsible_id` (Many2one res.users) - Responsable principal
- `user_ids` (Many2many res.users) - Utilisateurs autorises
- `current_balance` (Monetary, computed, stored) - Solde actuel calcule depuis les operations et clotures
- `last_closing_balance` (Monetary) - Solde a la derniere cloture
- `state` (Selection: open/closed/locked, tracking)
- `last_closing_date` (Datetime, readonly)
- `opening_date` (Date, required)
- `auto_close_days` (Integer, default=1) - Jours avant auto-fermeture
- `require_closing` (Boolean, default=True)
- `max_amount` (Monetary) - Montant maximum autorise
- `journal_id` (Many2one account.journal, required, domain=[('type','=','cash')])
- `active` (Boolean, default=True)
- `location` (Char) - Emplacement physique
- `notes` (Text)
- `color` (Integer)
- `operation_count` (Integer, computed)
- `transfer_count` (Integer, computed)
- `closing_count` (Integer, computed)
- `days_since_closing` (Integer, computed, stored)
- `is_closing_late` (Boolean, computed, stored)
- `has_pending_closing` (Boolean, computed, stored)
- `last_closing_id` (Many2one treasury.cash.closing, computed, stored)
- `transfer_out_ids`, `transfer_in_ids` (One2many treasury.transfer)
- `operation_ids` (One2many treasury.cash.operation)
- `closing_ids` (One2many treasury.cash.closing)

Contraintes SQL :
- journal_id + company_id unique
- code + company_id unique
- max_amount >= 0

Methodes :
- `_compute_current_balance()` : calcul depuis les operations et dernieres clotures validees
- `_compute_days_since_closing()` : jours depuis derniere cloture
- `_cron_update_days_since_closing()` : job cron journalier
- `action_open()`, `action_close_temporary()`, `action_lock()` : transitions d'etat
- `action_create_operation()` : cree une operation avec auto-cloture
- `action_create_closing()` : cree une nouvelle cloture
- `action_initialize_balance()` : initialise le solde
- `action_view_transfers()`, `action_view_closings()`, `action_view_journal()`

#### 2. treasury.cash.operation (Operation de caisse)
Champs :
- `name` (Char, readonly, sequence auto : OPC/YYYY/00001)
- `cash_id` (Many2one treasury.cash, required)
- `operation_type` (Selection: in/out, required, tracking)
- `category_id` (Many2one treasury.operation.category, required, tracking)
- `amount` (Monetary, required, >0)
- `currency_id` (Many2one, related=cash_id.currency_id)
- `date` (Datetime, required, default=now)
- `description` (Text)
- `reference` (Char) - Numero facture/bon
- `payment_id` (Many2one account.payment, readonly) - Paiement associe
- `is_manual` (Boolean, default=False) - Creation manuelle
- `state` (Selection: draft/posted/cancel, tracking)
- `closing_id` (Many2one treasury.cash.closing, readonly)
- `attachment_ids` (Many2many ir.attachment)
- `attachment_count` (Integer, computed)
- `user_id` (Many2one res.users, readonly, default=current)
- `transfer_id` (Many2one treasury.transfer, readonly)
- `is_collected` (Boolean) - Marque comme encaisse
- `collected_date` (Datetime, readonly)
- `collected_by` (Many2one res.users, readonly)
- `partner_id` (Many2one res.partner)
- `observations` (Text)
- `is_today`, `is_this_week`, `is_this_month` (Boolean, computed) - Filtres de date

Methodes :
- `action_post()` : comptabilise, verifie le solde pour les sorties
- `action_cancel()`, `action_draft()` : transitions
- `action_mark_collected()`, `action_unmark_collected()` : marquage encaissement
- `create_from_payment()` : cree depuis un account.payment
- `create_manual_operation_with_closing()` : cree avec auto-cloture

Contraintes :
- amount > 0
- Verification solde pour operations sortantes

#### 3. treasury.cash.closing (Cloture de caisse)
Champs :
- `name` (Char, readonly, sequence auto : CLO/code/date/number)
- `cash_id` (Many2one treasury.cash, required)
- `closing_date` (Date, required, default=today)
- `closing_number` (Integer, readonly) - Numero journalier sequentiel
- `period_start` (Datetime, computed, stored)
- `period_end` (Datetime, computed, stored)
- `balance_start` (Monetary, computed, stored) - Solde d'ouverture (depuis cloture precedente)
- `balance_end_theoretical` (Monetary, computed, stored) - balance_start + entrees - sorties
- `balance_end_real` (Monetary) - Solde comptage reel
- `balance_end_real_manual` (Boolean) - Flag modification manuelle
- `difference` (Monetary, computed, stored) - real - theoretical
- `total_in` (Monetary, computed, stored)
- `total_out` (Monetary, computed, stored)
- `operation_ids` (One2many treasury.cash.operation)
- `line_ids` (One2many treasury.cash.closing.line)
- `adjustment_operation_id` (Many2one treasury.cash.operation, readonly)
- `state` (Selection: draft/confirmed/validated/cancel, tracking)
- `user_id` (Many2one, readonly)
- `validated_by` (Many2one, readonly)
- `notes` (Text)
- `manual_operation_count`, `automatic_operation_count`, `draft_manual_operation_count` (Integer, computed)

Methodes :
- `create()` : auto-numerotation, sequence journaliere, chargement operations
- `action_load_operations()` : charge les operations non assignees pour la periode
- `_create_operations_from_payments()` : cree des operations depuis les account.payment
- `_compute_closing_lines()` : cree les lignes de detail avec solde cumulatif
- `action_confirm()` : confirme la cloture
- `action_validate()` : finalise, cree operation d'ajustement si ecart
- `action_back_to_draft()` : retour brouillon avec validations
- `action_cancel()` : annule avec verifications de securite
- `action_print_report()` : impression rapport
- `action_create_manual_operation()` : cree operation manuelle dans la cloture
- `_sync_balance_end_real()` : synchronise le solde reel avec le theorique

Contrainte : une seule cloture en attente par caisse

#### 4. treasury.cash.closing.line (Ligne de cloture)
Champs :
- `closing_id` (Many2one, ondelete=cascade)
- `sequence` (Integer, default=10)
- `date` (Datetime)
- `operation_id` (Many2one treasury.cash.operation)
- `partner_id` (Many2one res.partner)
- `category_id` (Many2one treasury.operation.category)
- `operation_type` (Selection: initial/in/out)
- `description` (Text)
- `reference` (Char)
- `amount_in` (Monetary)
- `amount_out` (Monetary)
- `cumulative_balance` (Monetary) - Solde cumulatif running

#### 5. treasury.safe (Coffre-fort)
Champs :
- `name` (Char, required)
- `code` (Char, required, unique par company)
- `currency_id` (Many2one, required)
- `company_id` (Many2one, required)
- `responsible_ids` (Many2many res.users, required) - Plusieurs responsables
- `current_balance` (Monetary, computed, stored)
- `state` (Selection: active/locked)
- `location` (Char)
- `max_capacity` (Monetary)
- `is_initialized` (Boolean, readonly) - Flag premiere operation
- `active` (Boolean, default=True)
- `notes` (Text)
- `transfer_in_ids`, `transfer_out_ids` (One2many)
- `operation_ids` (One2many)
- `transfer_count` (Integer, computed)
- `last_operation_date` (Datetime, computed, stored)

Methodes : action_lock(), action_unlock(), action_view_transfers(), action_create_operation()

#### 6. treasury.safe.operation (Operation de coffre)
Champs :
- `name` (Char, readonly, sequence auto)
- `safe_id` (Many2one, required)
- `operation_type` (Selection: initial/bank_in/bank_out/adjustment/other_in/other_out, required)
- `amount` (Monetary, required)
- `date` (Datetime, required, default=now)
- `bank_reference` (Char)
- `description` (Text, required)
- `state` (Selection: draft/confirmed/done/cancel)
- `balance_before`, `balance_after` (Monetary, computed)
- `user_id`, `validated_by` (Many2one res.users, readonly)

Contrainte : une seule operation initiale par coffre

#### 7. treasury.transfer (Transfert)
Champs :
- `name` (Char, readonly, sequence auto)
- `transfer_type` (Selection: cash_to_cash/cash_to_safe/safe_to_cash/safe_to_safe, required)
- `cash_from_id`, `cash_to_id` (Many2one treasury.cash)
- `safe_from_id`, `safe_to_id` (Many2one treasury.safe)
- `cash_operation_out_id`, `cash_operation_in_id` (Many2one treasury.cash.operation, readonly)
- `amount` (Monetary, required, >0)
- `currency_id` (Many2one, computed depuis source)
- `date` (Datetime, required, default=now)
- `description` (Text)
- `state` (Selection: draft/confirm/done/cancel)
- `user_id`, `validated_by` (Many2one res.users, readonly)
- `balance_before_from`, `balance_after_from`, `balance_before_to`, `balance_after_to` (Monetary, computed et stored)
- `color` (Integer)

Methodes :
- `action_confirm()` : confirme, verifie soldes, cree operations appariees
- `action_done()` : termine le transfert
- `action_cancel()` : annule, supprime operations liees
- `_create_cash_operations()` : cree les operations d'entree/sortie
- `_check_transfer_consistency()` : validation par type
- `amount_to_text()` : convertit montant en lettres (francais, via num2words)

#### 8. treasury.operation.category (Categorie d'operation)
Champs :
- `name` (Char, required, translatable)
- `code` (Char, required, unique)
- `operation_type` (Selection: in/out/both, required)
- `sequence` (Integer, default=10)
- `active` (Boolean, default=True)
- `is_customer_payment` (Boolean)
- `is_vendor_payment` (Boolean)

#### 9. account.payment (Extension)
Champs ajoutes :
- `journal_type` (Selection, related=journal_id.type, readonly)
- `treasury_operation_id` (Many2one treasury.cash.operation, readonly)
- `is_cash_collected` (Boolean)
- `cash_id` (Many2one treasury.cash)

Surcharges :
- `action_post()` : cree l'operation de tresorerie si journal de type cash
- `action_cancel()` : annule l'operation associee
- `action_mark_cash_collected()` : marque comme encaisse

### Donnees initiales (data/treasury_data.xml) :
Categories d'operations predefinies :
- VENTE (in), PAY_CLIENT (in), PAY_FOURN (out), REFUND_CUSTOMER (out), REFUND_SUPPLIER (in)
- AJUST (both), INITIAL (in), TRANSFER_IN (in), TRANSFER_OUT (out)

Job Cron : mise a jour quotidienne des jours depuis derniere cloture

### Securite :
Groupes : `group_treasury_user`, `group_treasury_manager` (implique user)
Regles d'acces :
- Users : acces aux caisses/coffres/operations ou ils sont autorises (user_ids, responsible_id, create_uid)
- Managers : acces complet a tout

### Menu principal :
Menu "Tresorerie" (sequence 45) avec sous-menus :
- Caisses et Coffres > Caisses, Coffres-forts
- Operations et Mouvements > Transferts, Operations de caisse, Clotures de caisse, Operations coffre (managers)
- Configuration > Categories d'operations

### Vues :
- Toutes les entites : vues tree, form, kanban et search
- Clotures : formulaire avec onglets "Toutes les Operations" et "Operations Manuelles"
- Transferts : formulaire avec soldes avant/apres, montant en lettres
- Caisses : formulaire avec boutons smart (Journal, Transferts, Operations, Clotures)
- Decorations : rouge si solde negatif, vert si positif

### Rapports :
- Rapport de cloture de caisse (QWeb PDF)
- Rapport de transfert (QWeb PDF)
- Rapport d'operations de caisse

---

## PROMPT 2 — Module Bancaire : `adi_treasury_bank`

Creer un module Odoo 19 `adi_treasury_bank` (version 19.0.1.0.0) de gestion bancaire.
Categorie: Accounting/Treasury. Dependances: base, account, adi_treasury.
Application: True.

### Modeles a creer :

#### 1. treasury.bank (Compte bancaire)
Champs :
- `name` (Char, required, tracking)
- `code` (Char, required, tracking)
- `active` (Boolean, default=True, tracking)
- `company_id` (Many2one, required)
- `currency_id` (Many2one, required)
- `journal_id` (Many2one account.journal, required, domain=[('type','=','bank')], tracking)
- `bank_id` (Many2one res.bank, tracking)
- `account_number` (Char, tracking)
- `iban` (Char, tracking)
- `bic` (Char, tracking)
- `bank_name` (Char, related=bank_id.name, store=True)
- `branch` (Char, tracking) - Agence
- `responsible_id` (Many2one res.users, default=current, tracking)
- `user_ids` (Many2many res.users)
- `current_balance` (Monetary, computed, stored) - Base sur dates d'operation
- `available_balance` (Monetary, computed, stored) - Base sur dates de valeur (<=today)
- `last_closing_date`, `last_closing_balance` (readonly)
- `last_statement_date`, `last_statement_balance` (tracking)
- `opening_balance` (Monetary, tracking)
- `opening_date` (Date, default=today, tracking)
- `overdraft_limit` (Monetary, default=0, tracking, >=0)
- `state` (Selection: active/suspended/closed, tracking)
- `operation_ids` (One2many treasury.bank.operation)
- `closing_ids` (One2many treasury.bank.closing)
- `transfer_in_ids`, `transfer_out_ids` (One2many treasury.transfer)
- `operation_count`, `closing_count`, `transfer_count` (Integer, computed)

Logique de calcul du solde :
- `_compute_current_balance()` : dernier rapprochement valide + operations posterieures (par date d'operation)
- `_compute_available_balance()` : idem mais par date de valeur (value_date <= today)

Contraintes SQL : code+company unique, journal+company unique, overdraft_limit >= 0
Contrainte : journal doit etre de type 'bank'

name_get() : "[CODE] NAME (account_number)"

#### 2. treasury.bank.operation (Operation bancaire)
Champs :
- `name` (Char, readonly, sequence: OPB/YYYY/00001)
- `bank_id` (Many2one treasury.bank, required, tracking)
- `operation_type` (Selection: in/out, required, tracking)
- `category_id` (Many2one treasury.operation.category, required, tracking)
- `payment_method` (Selection: transfer/check/cash/card/direct_debit/bank_fees/interest/other, default='other')
- `amount` (Monetary, required, >0, tracking)
- `date` (Datetime, required, default=now, tracking)
- `value_date` (Date, required, default=today, tracking) - Date de valeur bancaire
- `bank_reference` (Char) - Reference bancaire
- `check_number` (Char) - Numero de cheque
- `partner_id` (Many2one res.partner, tracking)
- `description` (Text)
- `state` (Selection: draft/posted/reconciled/cancel, tracking)
- `is_reconciled` (Boolean) - Flag rapprochement
- `reconciliation_date` (Date, readonly)
- `closing_id` (Many2one treasury.bank.closing, ondelete=set null)
- `payment_id` (Many2one account.payment, ondelete=set null)
- `transfer_id` (Many2one treasury.transfer, ondelete=cascade)
- `is_manual` (Boolean, default=True)
- `is_opening` (Boolean, default=False)
- `user_id` (Many2one, readonly)

Methodes :
- `action_post()` : comptabilise, verifie decouvert
- `action_cancel()` : annule (verifie rapprochement et cloture)
- `action_draft()` : retour brouillon
- `action_reconcile()` : marque comme rapproche avec date
- `action_unreconcile()` : retire le rapprochement

Verification decouvert : new_balance >= -overdraft_limit

#### 3. treasury.bank.closing (Rapprochement bancaire)
Champs :
- `name` (Char, readonly, sequence: RAP/YYYY/00001)
- `bank_id` (Many2one, required, tracking)
- `closing_date` (Date, required, tracking)
- `period_start` (Date, required, tracking) - Auto-calcule depuis dernier rapprochement
- `period_end` (Date, computed, stored)
- `balance_start` (Monetary, required, tracking) - Auto depuis dernier rapprochement
- `balance_end_theoretical` (Monetary, computed, stored)
- `balance_end_bank` (Monetary, tracking) - Solde du releve bancaire
- `difference` (Monetary, computed, stored) - balance_end_bank - theoretical
- `balance_end_bank_manual` (Boolean) - Modification manuelle du solde
- `total_in`, `total_out` (Monetary, computed, stored)
- `operation_ids` (One2many)
- `line_ids` (One2many treasury.bank.closing.line)
- `reconciled_operation_ids`, `unreconciled_operation_ids` (One2many, computed)
- `reconciled_count`, `unreconciled_count` (Integer, computed)
- `reconciliation_rate` (Float, computed) - Pourcentage rapproche
- `adjustment_operation_id` (Many2one, readonly)
- `state` (Selection: draft/confirmed/validated/cancel, tracking)
- `validated_by` (Many2one, readonly)
- `validated_date` (Datetime, readonly)

Methodes :
- `create()` : sequence, calcul period_start (depuis dernier rapprochement ou debut de mois), calcul balance_start, verification pas de draft/confirmed existant, auto-chargement operations
- `action_load_operations()` : charge operations + synchronise les paiements Odoo non encore importes
- `_sync_payments_to_operations()` : cree des treasury.bank.operation depuis account.payment non lies
- `_compute_closing_lines()` : genere les lignes de detail avec solde cumulatif
- `action_confirm()` : verifie donnees
- `action_validate()` : verifie operations non rapprochees, cree ajustement si ecart, met a jour bank
- `action_validate_force()` : valide malgre operations non rapprochees
- `action_back_to_draft()` : verifie pas de rapprochement posterieur, supprime ajustement
- `action_cancel()` : detache operations
- `action_print_report()` : impression

#### 4. treasury.bank.closing.line
Meme structure que treasury.cash.closing.line + champ `is_reconciled` (Boolean)

#### 5. treasury.transfer (Extension pour la banque)
Champs ajoutes :
- `transfer_type` selection_add : cash_to_bank, bank_to_cash, safe_to_bank, bank_to_safe, bank_to_bank
- `bank_from_id`, `bank_to_id` (Many2one treasury.bank, tracking)
- `bank_operation_out_id`, `bank_operation_in_id` (Many2one treasury.bank.operation, readonly)
- `bank_from_balance_before/after`, `bank_to_balance_before/after` (Monetary, readonly)
- `bank_from_balance_current`, `bank_to_balance_current` (Monetary, computed)
- `payment_method` (Selection: transfer/check/cash/card/other, default='transfer')
- `bank_reference` (Char)

Logique transferts bancaires :
- cash_to_bank : cree operation entrante banque
- bank_to_cash : cree operation sortante banque
- bank_to_bank : cree sortie source + entree destination
- safe_to_bank, bank_to_safe : idem avec coffres
- action_cancel() : supprime les operations bancaires associees

#### 6. account.payment (Extension bancaire)
Champs ajoutes :
- `treasury_bank_operation_id` (Many2one treasury.bank.operation, readonly)
- `bank_id` (Many2one treasury.bank, computed, stored)
- `mode_payment` (Selection: check/bank_transfer/bank_deposit, default='check')
- `check_number` (Char) - Numero de cheque
- `transfer_number` (Char) - Numero de virement
- `deposit_number` (Char) - Numero de versement

Surcharges :
- `action_post()` : cree automatiquement treasury.bank.operation si journal bancaire
- `action_cancel()` : verifie et annule l'operation bancaire (refuse si rapprochee ou dans cloture validee)
- `action_draft()` : supprime l'operation bancaire

Onchanges :
- `_onchange_check_number()` : met a jour ref = "CH N: " + check_number
- `_onchange_transfer_number()` : ref = "Virement N: " + transfer_number
- `_onchange_deposit_number()` : ref = "Versement N: " + deposit_number

Contrainte : unicite des numeros de cheque/virement/versement par journal

### Donnees initiales :
Sequences : OPB/YYYY/ (padding 5), RAP/YYYY/ (padding 5)
Categories d'operations bancaires (16 categories) :
- Entrees : BANK_CUSTOMER_IN, BANK_TRANSFER_IN, BANK_INTEREST_IN, BANK_REFUND_SUPPLIER, BANK_DEPOSIT
- Sorties : BANK_SUPPLIER_OUT, BANK_TRANSFER_OUT, BANK_CHECK_OUT, BANK_FEES, BANK_INTEREST_OUT, BANK_DIRECT_DEBIT, BANK_WITHDRAWAL, BANK_REFUND_CUSTOMER
- Mixtes : BANK_AJUST, BANK_CARD, BANK_OTHER

### Securite :
Groupes : `group_treasury_bank_user`, `group_treasury_bank_manager`
Regles : users voient uniquement banques ou ils sont dans user_ids/responsible_id/create_uid

### Menu :
Sous "Tresorerie" > "Banques" (sequence 5) :
- Comptes Bancaires, Operations Bancaires, Rapprochements Bancaires

### Vues :
- Banques : kanban avec couleurs par etat, tree, form avec boutons smart
- Operations : form avec methode de paiement conditionnelle (numero cheque visible si payment_method=check)
- Rapprochements : form avec 4 onglets (Lignes detail, Operations, Non rapprochees), statistiques rapprochement
- Transferts : extension du formulaire pour les champs bancaires

---

## PROMPT 3 — Module Comptage : `adi_treasury_cashcount`

Creer un module Odoo 19 `adi_treasury_cashcount` (version 19.0.1.0.0) de comptage de caisse.
Categorie: Accounting/Treasury. Dependances: adi_treasury.

### Modeles a creer :

#### 1. cash.denomination (Denomination)
Champs :
- `name` (Char, required) - Ex: "Billet de 2000 DA"
- `value` (Monetary, required, >0) - Valeur faciale
- `currency_id` (Many2one res.currency, required)
- `type` (Selection: bill/coin, required, default='bill')
- `active` (Boolean, default=True)
- `sequence` (Integer, default=10) - Ordre d'affichage
- `company_id` (Many2one res.company)

name_get() : icone + nom (billet ou piece)

#### 2. treasury.cash.closing.count (Ligne de comptage final)
Champs :
- `closing_id` (Many2one treasury.cash.closing, required, ondelete=cascade)
- `denomination_id` (Many2one cash.denomination, required)
- `quantity` (Integer, default=0, >=0)
- `subtotal` (Monetary, computed, stored) = quantity x denomination.value
- `currency_id` (Many2one, related=closing_id.currency_id)
- `denomination_value` (Monetary, related=denomination_id.value)
- `denomination_type` (Selection, related=denomination_id.type)

#### 3. treasury.cash.closing.initial.count (Ligne de comptage initial)
Meme structure que treasury.cash.closing.count mais pour le comptage initial
Ordonne par : denomination_type asc, denomination_value desc (billets d'abord, par valeur decroissante)

#### 4. treasury.cash.closing (Extension)
Champs ajoutes :
- `count_line_ids` (One2many treasury.cash.closing.count)
- `counted_total` (Monetary, computed, stored) = sum(count_line_ids.subtotal)
- `use_cash_count` (Boolean, default=True)
- `cash_count_done` (Boolean, default=False)
- `force_cash_count` (Boolean, computed) - Depuis config globale OU par caisse
- `show_count_in_report` (Boolean, computed)
- `initial_count_line_ids` (One2many treasury.cash.closing.initial.count)
- `initial_counted_total` (Monetary, computed, stored)
- `initial_count_done` (Boolean, default=False)
- `use_initial_count` (Boolean, computed) - Depuis config globale OU par caisse
- `force_initial_count` (Boolean, computed)
- `initial_difference` (Monetary, computed, stored) = initial_counted_total - balance_start
- `balance_start_adjusted` (Monetary, computed, stored) - CRITIQUE : Approche B

LOGIQUE CRITIQUE - Approche B pour le solde ajuste :
```
Si initial_count_done:
    balance_start_adjusted = initial_counted_total
Sinon:
    balance_start_adjusted = balance_start
```

SURCHARGE du calcul theorique :
```
balance_end_theoretical = balance_start_adjusted + total_in - total_out
```
(au lieu de balance_start + total_in - total_out)

Surcharge action_confirm() :
- Si force_cash_count ET NOT cash_count_done → ValidationError
- Si force_initial_count ET use_initial_count ET NOT initial_count_done → ValidationError

#### 5. treasury.cash (Extension)
Champs ajoutes :
- `force_cash_count` (Boolean, default=False) - Forcer comptage final par caisse
- `show_count_in_report` (Boolean, default=True)
- `enable_initial_count` (Boolean, default=False) - Activer comptage initial
- `force_initial_count` (Boolean, default=False) - Forcer comptage initial

#### 6. res.config.settings (Extension)
Parametres de configuration :
- `force_cash_count_global` (Boolean, config_parameter)
- `hide_count_in_report_global` (Boolean, config_parameter)
- `enable_initial_count_global` (Boolean, config_parameter)
- `force_initial_count_global` (Boolean, config_parameter)

### Wizards (TransientModel) :

#### cash.count.wizard (Comptage final)
Champs :
- `closing_id` (Many2one, required, readonly)
- `line_ids` (One2many cash.count.wizard.line)
- `total_bills`, `total_coins`, `total_counted` (Monetary, computed)
- `balance_end_theoretical` (Monetary, related)
- `difference` (Monetary, computed) = total_counted - balance_end_theoretical
- `filled_lines_count` (Integer, computed)

Methodes :
- `_prepare_wizard_lines()` : prepare les lignes depuis les denominations actives, recupere quantites existantes
- `action_confirm()` : supprime anciennes lignes, cree nouvelles, met a jour balance_end_real et cash_count_done
- `action_reset()` : remet toutes les quantites a 0

#### cash.count.wizard.line
Champs : wizard_id, denomination_id, denomination_value, denomination_type, denomination_name, quantity(>=0), subtotal(computed)
Ordonne par : denomination_type asc, denomination_value desc

#### initial.cash.count.wizard (Comptage initial)
Structure identique a cash.count.wizard mais :
- Reference = balance_start (au lieu de balance_end_theoretical)
- action_confirm() met a jour initial_count_line_ids et initial_count_done (pas balance_end_real)

#### initial.cash.count.wizard.line
Meme structure que cash.count.wizard.line

### Donnees initiales :
Denominations DZD (Dinar Algerien) pre-chargees :
- Billets : 2000 DA (seq 10), 1000 DA (seq 20), 500 DA (seq 30), 200 DA (seq 40)
- Pieces : 200 DA (seq 50), 100 DA (seq 60), 50 DA (seq 70), 20 DA (seq 80), 10 DA (seq 90), 5 DA (seq 100)

### Vues :
- Denominations : tree et form dans Configuration
- Cloture form : bouton "Comptage de caisse" ouvrant le wizard modal, onglet "Comptage" (readonly apres confirmation)
- Onglet "Comptage Initial" visible si use_initial_count=True
- Badge "Comptage obligatoire" si force_cash_count=True
- Section "Impact sur le calcul" montrant le solde ajuste
- Wizard : 3 onglets (Billets, Pieces, Tous) avec calcul temps reel, affichage ecart
- Configuration dans Settings: 4 options booleennes

### Rapport :
Integration des details de comptage dans le rapport de cloture (si show_count_in_report=True)

---

## PROMPT 4 — Module Dashboard : `adi_treasury_dashboard`

Creer un module Odoo 19 `adi_treasury_dashboard` (version 19.0.1.0.0) de tableau de bord tresorerie.
Categorie: Accounting/Treasury. Dependances: adi_treasury, adi_treasury_bank.

### Modele principal :

#### treasury.dashboard (Vue SQL virtuelle)
Type: Model avec `_auto = False` (pas de table physique, vue SQL)
Ordonne par : sequence, type

Champs :
- `name` (Char) - Nom de l'entite
- `code` (Char) - Code identifiant
- `balance` (Monetary) - Solde actuel
- `currency_id` (Many2one res.currency)
- `type` (Selection) - Valeurs :
  - cash, bank, safe (entites individuelles)
  - total_cash, total_bank, total_safe (totaux par categorie)
  - grand_total (total general)
  - total_bank_reconciled, total_bank_unreconciled (totaux rapprochement)
  - grand_total_reconciled, grand_total_unreconciled
- `color` (Integer) - Code couleur : 1=negatif/rouge, 10=cash/vert, 4=bank/bleu, 8=safe/violet, 5=warning/orange
- `sequence` (Integer) - Ordre d'affichage
- `state` (Selection: open/active/closed)
- `icon` (Char) - Classe Font Awesome (fa-money, fa-university, fa-lock, fa-balance-scale, fa-check-circle, fa-clock-o)
- `res_id` (Integer) - ID de l'enregistrement source
- `res_model` (Char) - Modele source
- `has_pending_closing` (Boolean) - Cloture en cours
- `is_balance_final` (Boolean) - Solde finalise (pas de cloture en attente)
- `reconciled_balance` (Monetary) - Solde rapproche
- `unreconciled_balance` (Monetary) - Solde non rapproche

Vue SQL (init()) avec UNION ALL :
1. Caisses individuelles (ID direct, type='cash', seq=1, color=10/vert)
2. Banques individuelles (ID=1000000+id, type='bank', seq=2, color=4/bleu)
3. Coffres individuels (ID=3000000+id, type='safe', seq=3, color=8/violet)
4. Total Caisses (ID=2000001, type='total_cash', seq=4)
5. Total Banques (ID=2000002, type='total_bank', seq=5)
6. Total Coffres (ID=2000004, type='total_safe', seq=6)
7. Total General (ID=2000003, type='grand_total', seq=7, = caisses + banques + coffres)
8. Total Banques Rapproche (ID=2000012, seq=12)
9. Total Banques Non Rapproche (ID=2000013, seq=13)
10. Total General Rapproche (ID=2000023, seq=21, = caisses + coffres + banques rapprochees)
11. Total General Non Rapproche (ID=2000024, seq=22)

Logique couleur :
- Negatif → 1 (rouge)
- Cash positif → 10 (vert)
- Bank positif → 4 (bleu)
- Safe positif → 8 (violet)
- Grand total positif → 5 (orange)
- Zero → 0 (gris)

Detection clotures en attente :
```sql
has_pending_closing = EXISTS(SELECT 1 FROM treasury_cash_closing WHERE cash_id=c.id AND state IN ('draft','confirmed'))
is_balance_final = NOT EXISTS(...)
```

Methodes :
- `get_dashboard_data()` : API Python retournant dict structure {cashes, banks, safes, totaux, currency}
- `action_open_record()` : ouvre l'enregistrement source

### Extension treasury.bank (Soldes rapproches)
Champs ajoutes :
- `reconciled_balance` (Monetary, computed, stored) - Operations rapprochees
- `unreconciled_balance` (Monetary, computed, stored) - Operations non rapprochees

Logique :
```
reconciled_balance = base_closing_balance + sum(operations rapprochees ou state='reconciled')
unreconciled_balance = sum(operations state='posted' et non rapprochees)
Verification : current_balance = reconciled_balance + unreconciled_balance
```

Surcharge `_compute_current_balance()` :
- CORRECTION : inclut les operations avec state 'posted' ET 'reconciled'
- CORRECTION : inclut les "operations orphelines" (avant cloture mais sans closing_id)

### Configuration :
- `treasury.config.reconciliation` (Singleton) avec show_reconciliation_details (Boolean)
- Extension res.config.settings avec `treasury_show_reconciliation_details`

### Vues :

#### Kanban Dashboard (Vue principale)
Classe CSS: o_kanban_dashboard o_treasury_dashboard
Desactiver : create, edit, delete, group
Template conditionnel par type :

- **total_cash** : carte verte, bordure success 3px, icone fa-calculator
- **total_bank** : carte bleue, bordure primary 3px, icone fa-calculator
- **total_safe** : carte sombre, bordure dark 3px, icone fa-lock
- **grand_total** : carte orange, bordure warning 3px, icone fa-balance-scale
- **cash** (individuel) : bordure verte si positif/rouge si negatif, footer avec badge etat + indicateur finalisation
- **bank** (individuel) : bordure bleue, affiche 3 soldes (courant + rapproche + non-rapproche)
- **safe** (individuel) : bordure sombre
- **total_bank_reconciled** : carte verte, fa-check-circle
- **total_bank_unreconciled** : carte orange, fa-clock-o
- **grand_total_reconciled/unreconciled** : idem

#### Autres vues : tree, pivot (par type), graph (barres par nom)

#### Vues Banques etendues :
- Kanban banque : carte avec 3 soldes (courant, rapproche, non-rapproche) + infos bancaires
- Tree banque : colonnes avec soldes et avatar responsable
- Pivot et Graph banque

### CSS/SCSS :
```scss
.o_treasury_dashboard {
    background-color: #f8f9fa;
    padding: 20px;
    .o_kanban_record {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        &:hover { transform: translateY(-2px); box-shadow: 0 8px 15px rgba(0,0,0,0.15); }
    }
}
// Gradients : Cash=#11998e→#38ef7d, Bank=#2193b0→#6dd5ed, Total=#667eea→#764ba2
// Responsive : polices reduites sur mobile
```

IMPORTANT pour Odoo 19 : utiliser le framework OWL 2.x pour les composants JavaScript du dashboard au lieu de jQuery/Widget legacy. Declarer les assets dans __manifest__.py via le dict 'assets'.

### Menu :
Sous "Tresorerie" :
- Tableau de Bord (priority 10, group treasury_manager)
- Caisses (priority 2, raccourci)
- Banques (priority 3, raccourci)
- Coffres (priority 4, raccourci)

---

## PROMPT 5 — Module Controle : `adi_treasury_control`

Creer un module Odoo 19 `adi_treasury_control` (version 19.0.1.0.0) de controle et securite.
Categorie: Accounting/Treasury. Dependances: adi_treasury, adi_treasury_bank.

Ce module consolide 4 modules Odoo 15 : transfer_control, access, payment_partner_restrict, transfert_control.

### Partie A : Controle des Transferts

#### treasury.transfer (Extension)
Champs ajoutes :
- `control_checked` (Boolean) - Controle effectue
- `control_date` (Datetime)
- `control_user_id` (Many2one res.users)
- `source_balance_before`, `source_balance_after` (Monetary)
- `dest_balance_before`, `dest_balance_after` (Monetary)
- `control_warning` (Text, computed) - Messages d'avertissement
- `force_transfer` (Boolean) - Forcage par les managers uniquement

Methode principale `_check_balance_before_transfer()` (appelee dans action_confirm) :
1. Recupere le solde de la source
2. Pour les **banques** : verifie si balance - amount < -overdraft_limit
3. Pour les **caisses/coffres** : si allow_negative_balance=False, verifie si balance >= amount
4. Verifie capacite de la destination (max_amount/max_capacity)
5. Si force_transfer=True (manager), log et autorise
6. Messages d'erreur formates avec montants et limites

#### treasury.cash (Extension controle)
Champs ajoutes :
- `allow_negative_balance` (Boolean, default=False)
- `min_balance` (Monetary, default=0)
- `control_level` (Selection: none/warning/blocking, default='blocking')
- `transfer_out_count`, `transfer_in_count` (Integer, computed)
- `pending_transfer_amount` (Monetary, computed)
- `available_balance` (Monetary, computed) = current_balance - pending_transfers

#### treasury.safe (Extension controle) : memes champs que cash

#### treasury.bank (Extension controle)
Champs ajoutes : idem +
- `allow_negative_balance` (Boolean, default=True) - Banques autorisent le decouvert par defaut
- `effective_available_balance` (Monetary, computed)
- `overdraft_remaining` (Monetary, computed) - Capacite de decouvert restante

#### treasury.bank.operation, treasury.safe.operation (Extensions)
Contraintes ajoutees :
- `_check_amount_positive()` : amount > 0
- `_check_bank_balance_on_out()` / `_check_safe_balance_on_out()` : verification solde avant sortie

#### res.config.settings (Extension)
8 parametres de configuration :
- `transfer_control_enabled` - Activation globale
- `transfer_require_check` - Verification manuelle requise
- `transfer_auto_check` - Verification auto a la confirmation
- `transfer_block_insufficient` - Bloquer si solde insuffisant
- `transfer_block_overdraft` - Bloquer si decouvert depasse
- `transfer_block_capacity` - Bloquer si capacite destination depassee
- `transfer_allow_manager_force` - Managers peuvent forcer
- `transfer_log_controls` - Logger les controles dans le chatter

### Partie B : Controle d'Acces

#### res.users (Extension)
Champs computed :
- `treasury_cash_ids` (Many2many, computed) - Caisses accessibles
- `treasury_safe_ids` (Many2many, computed) - Coffres accessibles
- `treasury_bank_ids` (Many2many, computed) - Banques accessibles
- `has_treasury_cash/safe/bank` (Boolean, computed)

Logique :
- Managers : voient TOUT
- Users : voient uniquement ou ils sont dans user_ids, responsible_id(s), create_uid

#### Protection des champs sensibles
- treasury.cash : user_ids et responsible_id modifiables uniquement par managers
- treasury.safe : responsible_ids modifiable uniquement par managers
- treasury.bank : user_ids et responsible_id modifiables uniquement par managers
Raises AccessError si non-manager tente de modifier

#### treasury.cash.operation (Protection suppression)
- Interdiction supprimer si dans cloture validee → UserError
- Interdiction supprimer si state=posted → UserError
- Interdiction supprimer si lie a un transfert → UserError
- Interdiction supprimer si lie a un paiement → UserError
- `can_reset_to_draft` (Boolean, computed)
- `action_reset_to_draft()` : remet en brouillon (avec verifications), retire de la cloture, log au chatter

### Partie C : Restriction Partenaires

Modifications de vues uniquement (pas de modeles) :
- Tous les champs partner_id dans les formulaires de paiement et operations de tresorerie :
  options={'no_create': True, 'no_create_edit': True, 'no_quick_create': True}
- Applique a : account.payment (form, tree, kanban), treasury.cash.operation (form, tree), treasury.bank.operation (form, tree)

### Partie D : Controle des Transferts Journaux

#### account.payment (Extension)
Champs computed :
- `source_journal_balance` (Monetary, computed) - Solde du journal source
- `destination_journal_balance` (Monetary, computed) - Solde du journal destination
- `is_amount_exceeds_balance` (Boolean, computed) - True si montant > solde source (en brouillon)
- `source_journal_name`, `destination_journal_name` (Char, computed)

Methode `_get_journal_balance(journal)` :
- Requete SQL directe sur account_move_line
- Uniquement moves en etat 'posted'
- Exclut les lignes du paiement courant
- Retourne debit - credit

Surcharge action_post() :
- PRE-VALIDATION : verifie solde AVANT comptabilisation
- Si balance < amount → ValidationError avec details

#### account.move (Extension)
Surcharge _check_balanced() :
- Pour les ecritures de type 'entry' avec journaux cash/bank, valide les transferts manuels

### Securite :

Groupes :
- `group_transfer_control_user` (implique treasury_user)
- `group_transfer_control_manager` (implique user + treasury_manager)

Regles d'acces comprehensives :
- Caisses : users voient uniquement ou autorises, pas de create/delete
- Coffres : idem
- Banques : users R/W, managers full
- Operations (cash, safe, bank) : users voient/creent pour entites autorisees, pas de delete
- Clotures : filtrees par entite autorisee
- Transferts : filtre complexe avec 11 conditions OR sur toutes les entites liees

Actions filtrees :
- action_treasury_cash_filtered, action_treasury_safe_filtered, etc.
- Les menus pointent vers ces actions filtrees

### Vues :
- Formulaire transfert : onglet "Controle du transfert" avec soldes avant/apres, checkbox force (managers), alertes
- Formulaires cash/safe/bank : onglet "Controle des transferts" avec control_level, allow_negative, min_balance, soldes
- Formulaire operation : bouton "Remettre en brouillon" (visible si can_reset_to_draft)
- account.payment : section "Informations sur les Soldes" avec alertes visuelles rouges si depassement
- Vues role-based : readonly pour users, editable pour managers (via priority 100/200)
- Settings : panneau de configuration avec 8 parametres

---

## PROMPT 6 — Module Ameliorations : `adi_treasury_enhanced`

Creer un module Odoo 19 `adi_treasury_enhanced` (version 19.0.1.0.0).
Categorie: Accounting/Treasury. Dependances: adi_treasury, adi_treasury_control.

### treasury.cash.closing (Extension)

Champs computed :
- `pending_manual_operation_ids` (One2many, computed) - Operations manuelles en brouillon pour la periode
- `pending_manual_operation_count` (Integer, computed)
- `all_pending_manual_operation_ids` (One2many, computed) - Toutes operations manuelles en attente (draft + posted, non dans cloture validee)
- `all_pending_manual_operation_count` (Integer, computed)

Methodes :

`action_view_pending_manual_operations()` - Bouton smart "A valider"
- Affiche les operations manuelles en brouillon de la periode
- Action fenetre avec domaine filtre

`action_view_all_pending_operations()` - Bouton smart "En attente"
- Affiche toutes les operations en attente (draft + posted non validees)

`action_validate_all_pending_operations()` - Action batch
- Valide toutes les operations draft de la periode en lot
- Appelle action_post() sur chaque operation
- Trace les succes et erreurs
- Recharge les operations si cloture en brouillon
- Notification de succes avec compteur

`action_add_pending_operations_to_closing()` - Helper
- Ajoute les operations posted non liees a la cloture
- Met a jour les totaux et lignes

`action_open_manual_operation_wizard()` - Gestion
- Ouvre une vue tree speciale pour gerer les operations manuelles
- Autorise creation/suppression dans la vue

### Actions serveur (binding sur liste treasury.cash.operation) :
- `action_validate_selected_operations` : valide les operations selectionnees en lot
- `action_delete_selected_draft_operations` : supprime les operations draft selectionnees en lot

### Vues :

Vue tree speciale `view_treasury_cash_operation_pending_tree` (priority 100) :
- Decorations : warning=draft, success=posted, muted=cancel
- Colonnes : name, date, type, categorie, partenaire, description, montant(sum), etat
- Boutons inline : "Voir" (toujours), "Valider" (si draft), "Brouillon" (si can_reset_to_draft)

Vue search `view_treasury_cash_operation_pending_search` :
- Filtres : draft, posted, entrees, sorties
- Groupes : etat, type, categorie

Extension formulaire cloture (priority 50) :
- 2 boutons smart dans button_box :
  - "A valider" (warning, fa-exclamation-triangle) si count > 0
  - "En attente" (info, fa-list-alt) si count > 0
- Boutons header : "Valider les operations", "Gerer les operations"
- Nouvel onglet "Operations manuelles" avec :
  - Alerte si operations draft existent
  - Tree readonly des operations en attente avec decorations

---

## PROMPT 7 — Module Depenses : `adi_cash_expense`

Creer un module Odoo 19 `adi_cash_expense` (version 19.0.1.0.0) de gestion des depenses de caisse.
Categorie: Accounting/Treasury. Dependances: base, account, hr, adi_treasury.

### Modeles a creer :

#### 1. cash.expense (Depense de caisse)
Herite de : mail.thread, mail.activity.mixin
Ordonne par : date desc, id desc

Champs :
- `name` (Char, readonly, sequence auto: DEP/YYYY/00001)
- `date` (Date, required, default=today, tracking)
- `company_id` (Many2one, required)
- `user_id` (Many2one res.users, readonly, default=current)
- `expense_type` (Selection: reimbursement/advance, required, default='reimbursement', tracking)
  - reimbursement : l'employe a paye et demande remboursement
  - advance : avance de caisse versee a l'employe
- `employee_id` (Many2one hr.employee, required, tracking)
- `partner_id` (Many2one res.partner, computed depuis employee.address_home_id, stored)
- `department_id` (Many2one hr.department, tracking)
- `amount` (Monetary, computed depuis lines OU manuel pour avances, stored)
- `amount_spent` (Monetary) - Montant effectivement depense (pour avances)
- `amount_remaining` (Monetary, computed, stored) = amount - amount_spent (pour avances)
- `currency_id` (Many2one, required)
- `description` (Text, required)
- `notes` (Text)
- `attachment_ids` (Many2many ir.attachment) - Justificatifs
- `attachment_count` (Integer, computed)
- `cash_id` (Many2one treasury.cash, required, domain=[('state','=','open')], tracking)
- `personal_account_id` (Many2one personal.cash.account, computed, stored) - Auto-cree si inexistant
- `approved_by` (Many2one, readonly, tracking)
- `approved_date` (Datetime, readonly)
- `paid_by` (Many2one, readonly, tracking)
- `paid_date` (Datetime, readonly)
- `settled_by` (Many2one, readonly, tracking)
- `settled_date` (Datetime, readonly)
- `state` (Selection: draft/submitted/approved/paid/settled/cancel, tracking)
- `line_ids` (One2many cash.expense.line)

Workflow :
1. **draft** → action_submit() : valide que remboursements ont des lignes, avances ont amount > 0
2. **submitted** → action_approve() : pour avances, verifie plafond d'avance (advance_limit vs current_balance + amount)
3. **approved** → action_pay() :
   - Cree treasury.cash.operation (type='out')
   - Categorie : REMB (remboursement) ou AVANC (avance)
   - Appelle action_post() sur l'operation
   - Remboursements → state='settled' (final)
   - Avances → state='paid' (en attente de regularisation)
4. **paid** (avance) → action_settle() : ouvre le wizard de regularisation
5. **cancel** → action_draft() : retour brouillon possible

Contraintes :
- amount > 0
- Remboursements en submitted/approved/paid doivent avoir des justificatifs

#### 2. cash.expense.line (Ligne de depense)
Ordonne par : expense_id, sequence, id

Champs :
- `sequence` (Integer, default=10)
- `expense_id` (Many2one cash.expense, required, ondelete=cascade)
- `name` (Char, required) - Description
- `product_id` (Many2one product.product, optional)
- `quantity` (Float, default=1.0)
- `unit_price` (Monetary, required)
- `total_amount` (Monetary, computed, stored) = quantity x unit_price
- `currency_id` (Many2one, related)
- `notes` (Text)
- `attachment_ids` (Many2many ir.attachment)

Contraintes : quantity > 0, unit_price >= 0
Onchange product_id : auto-remplit name et unit_price depuis le produit

#### 3. personal.cash.account (Compte personnel)
Herite de : mail.thread, mail.activity.mixin

Champs :
- `employee_id` (Many2one hr.employee, required, ondelete=restrict, tracking)
- `partner_id` (Many2one, related employee.address_home_id, stored)
- `active` (Boolean, default=True)
- `currency_id` (Many2one, required)
- `company_id` (Many2one, required)
- `notes` (Text)
- `current_balance` (Monetary, computed, stored) = sum(avances paid non regularisees .amount_remaining)
  Represente le montant que l'employe doit encore a l'entreprise
- `advance_limit` (Monetary, default=0, tracking) - 0 = illimite
- `total_expenses` (Monetary, computed)
- `total_advances` (Monetary, computed)
- `total_reimbursements` (Monetary, computed)
- `expense_count` (Integer, computed)
- `active_advance_count` (Integer, computed, stored)
- `expense_ids` (One2many cash.expense)
- `advance_ids` (One2many cash.expense, domain=[('expense_type','=','advance')])

Contraintes :
- Un seul compte par employe par company
- advance_limit >= 0

Methodes :
- action_view_expenses(), action_view_advances()
- name_get() : "Compte de {employe} (Solde: {balance} {devise})"

### Wizard : cash.expense.settlement.wizard (Regularisation d'avance)
Champs :
- `expense_id` (Many2one, required, readonly) - L'avance a regulariser
- `employee_id`, `cash_id`, `currency_id` (related, readonly)
- `amount_advanced` (Monetary, readonly) - Montant avance
- `use_lines` (Boolean, default=False) - Mode saisie detaillee
- `amount_spent` (Monetary) - Total depense
- `line_ids` (One2many cash.expense.settlement.line)
- `amount_from_lines` (Monetary, computed)
- `amount_to_return` (Monetary, computed) = max(0, amount_advanced - amount_spent)
- `amount_to_pay` (Monetary, computed) = max(0, amount_spent - amount_advanced)
- `settlement_type` (Selection: return/exact/additional, computed)
- `attachment_ids` (Many2many ir.attachment)
- `notes` (Text)

action_settle() :
- Valide justificatifs et montant
- Si use_lines : synchronise amount_spent, cree cash.expense.line
- Met a jour expense : amount_spent, state='settled', settled_by/date
- Cree operation tresorerie si necessaire :
  - amount_to_return > 0 → operation 'in' (RETAV) : l'employe rend l'excedent
  - amount_to_pay > 0 → operation 'out' (SUPPL) : l'entreprise paie le complement
  - exact → pas d'operation supplementaire

#### cash.expense.settlement.line
Champs : wizard_id, name(required), description, date(default=today), amount(required), attachment_ids, currency_id

### Donnees initiales :
Sequence : DEP/YYYY/ (padding 5)
Categories d'operations :
- REMB (out, seq 20) : Remboursement employe
- AVANC (out, seq 30) : Avance employe
- RETAV (in, seq 40) : Retour d'avance
- SUPPL (out, seq 50) : Paiement supplementaire

### Securite :
Categorie module : `module_category_cash_expense`

Groupes et roles :
1. `group_cash_expense_user` (implique base.group_user) - Cree et soumet ses propres depenses
2. `group_cash_expense_manager` (implique user) - Approuve les depenses
3. `group_cash_expense_cashier` (implique user) - Paie et regularise

Regles d'acces :
- Users : voient uniquement leurs depenses (user_id=current)
- Managers : voient tout, CRUD complet
- Cashiers : voient uniquement approved/paid/settled, R/W sans create/delete
- Comptes personnels : users voient uniquement leur propre compte (readonly)

### Menu :
Sous "Tresorerie" > "Depense Caisse" (sequence 40) :
- Operations > Toutes les depenses, Remboursements, Avances
- Comptes > Comptes personnels
- Configuration (group system)

### Vues :
- Depense form : radio expense_type, boutons smart (Justificatifs, Operations, Compte personnel), notebook avec lignes/description/justificatifs/infos, workflow buttons dans header
- Depense tree : decorations par etat, badges colores
- Depense kanban : groupable par etat
- Compte personnel form : boutons smart, soldes, onglets Depenses et Avances en cours
- Wizard regularisation : toggle lignes/montant direct, alertes visuelles (retour, supplement, exact)

### Rapport :
- Rapport QWeb PDF "Bon de depense"
- Contenu : type, reference, beneficiaire, departement, date, lignes, total, section avance si applicable, bloc signatures

---

## NOTES TECHNIQUES GENERALES POUR ODOO 19

### Differences majeures Odoo 15 → Odoo 19 :

1. **Framework JS** : OWL 2.x natif au lieu de jQuery/Widget. Utiliser les composants OWL pour le dashboard et les wizards.

2. **Manifest** :
   - `'version': '19.0.1.0.0'`
   - Assets declares via dict `'assets'` dans __manifest__.py :
     ```python
     'assets': {
         'web.assets_backend': [
             'module_name/static/src/js/*.js',
             'module_name/static/src/scss/*.scss',
             'module_name/static/src/xml/*.xml',
         ],
     }
     ```

3. **Champs** :
   - Utiliser `Command` (from odoo.fields) au lieu de tuples `(0, 0, vals)` pour les One2many/Many2many
   - `fields.Json` si disponible pour stocker des donnees structurees

4. **API** :
   - Verifier les changements sur `account.move`, `account.payment` entre v15 et v19
   - `payment_method_id` peut avoir change en `payment_method_line_id`

5. **Vues** :
   - Verifier la syntaxe XML des vues (certains attributs peuvent avoir change)
   - Utiliser les nouveaux widgets disponibles

6. **Securite** :
   - Utiliser les record rules modernes et les groupes XML
   - `ir.model.access.csv` reste le meme format

7. **Tests** :
   - Ajouter des tests unitaires avec `TransactionCase` et `HttpCase`
   - Tester les workflows complets, les contraintes, et les calculs

8. **Multi-societe** :
   - Supporter le multi-company natif avec `company_id` et regles d'acces company-dependentes

9. **Localisation** :
   - Les denominations de billets/pieces doivent etre configurables par devise/pays
   - Les montants en lettres doivent supporter le francais

10. **Performance** :
    - Utiliser des champs computed stored pour eviter les recalculs
    - Utiliser des index SQL sur les champs frequemment recherches
    - Optimiser les requetes SQL dans les vues dashboard
