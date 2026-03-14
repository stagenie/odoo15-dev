# Modules de Tresorerie Odoo 15 → Odoo 19
# Liste des fonctionnalites et prompts de creation

## Analyse des modules Odoo 15 identifies

| # | Module technique (Odoo 15) | Categorie | Description |
|---|---|---|---|
| 1 | `adi_treasury` | Core | Gestion des caisses, coffres et transferts |
| 2 | `adi_treasury_bank` | Core | Gestion bancaire et operations bancaires |
| 3 | `adi_treasury_cashcount` | Comptage | Comptage detaille billets/pieces |
| 4 | `adi_treasury_cashcount_extended` | Comptage | Comptage etendu avec wizard et forcage |
| 5 | `adi_treasury_cashcount_init` | Comptage | Comptage initial a l'ouverture |
| 6 | `adi_treasury_dashboard` | Dashboard | Tableau de bord tresorerie |
| 7 | `adi_treasury_dashboard_extended` | Dashboard | Dashboard etendu avec coffres |
| 8 | `adi_treasury_balance_display` | Dashboard | Soldes rapproches/non-rapproches |
| 9 | `adi_treasury_transfer_control` | Controle | Controle avance des transferts |
| 10 | `adi_treasury_access` | Securite | Controle d'acces et protection |
| 11 | `adi_treasury_enhanced` | Ameliorations | Ameliorations clotures de caisse |
| 12 | `adi_cash_expense` | Depenses | Depenses, remboursements, avances |
| 13 | `adi_payment_partner_restrict` | Controle | Restriction creation partenaires |
| 14 | `adi_transfert_control` | Controle | Controle transferts avec soldes |
| 15 | `adi_bank_payment_mode` | Bancaire | Modes de paiement bancaires |

---

## Plan de consolidation : 15 modules Odoo 15 → 7 modules Odoo 19

| Module Odoo 19 (nouveau) | Modules Odoo 15 fusionnes |
|---|---|
| `adi_treasury` | `adi_treasury` |
| `adi_treasury_bank` | `adi_treasury_bank` + `adi_bank_payment_mode` |
| `adi_treasury_cashcount` | `adi_treasury_cashcount` + `adi_treasury_cashcount_extended` + `adi_treasury_cashcount_init` |
| `adi_treasury_dashboard` | `adi_treasury_dashboard` + `adi_treasury_dashboard_extended` + `adi_treasury_balance_display` |
| `adi_treasury_control` | `adi_treasury_transfer_control` + `adi_treasury_access` + `adi_payment_partner_restrict` + `adi_transfert_control` |
| `adi_treasury_enhanced` | `adi_treasury_enhanced` |
| `adi_cash_expense` | `adi_cash_expense` |

---

## PROMPTS DE CREATION POUR ODOO 19

---

### PROMPT 1 — Module Core : `adi_treasury` (Caisses & Coffres)

Creer un module Odoo 19 `adi_treasury` de gestion de tresorerie comprenant :

- **Gestion des caisses (treasury.cash)** : creation de caisses liees a des journaux de type "cash", suivi du solde en temps reel, statuts (brouillon/ouvert/cloture)
- **Operations de caisse (treasury.cash.operation)** : encaissements et decaissements avec categorie d'operation, partenaire, reference, montant, generation automatique d'ecritures comptables (account.move)
- **Cloture de caisse (treasury.cash.closing)** : cloture journaliere avec solde d'ouverture automatique (base sur la cloture precedente), calcul du solde theorique, workflow brouillon -> valide -> finalise
- **Gestion des coffres-forts (treasury.safe)** : entite de stockage de fonds avec operations d'entree/sortie et suivi de solde
- **Operations de coffre (treasury.safe.operation)** : depots et retraits avec tracabilite comptable
- **Transferts inter-entites (treasury.transfer)** : transferts caisse<->caisse, caisse<->coffre, coffre<->coffre avec generation d'ecritures comptables croisees
- **Categories d'operations (treasury.operation.category)** : categorisation des operations (vente, achat, salaire, etc.)
- **Menus et vues** : vues liste, formulaire et kanban pour chaque entite, menu principal "Tresorerie"

**Modeles a creer :**
- `treasury.cash` (name, journal_id, balance, state, company_id, user_id)
- `treasury.cash.operation` (cash_id, date, category_id, partner_id, amount, ref, move_id, state, operation_type[encaissement/decaissement])
- `treasury.cash.closing` (cash_id, date, opening_balance, closing_balance, theoretical_balance, state, line_ids)
- `treasury.cash.closing.line` (closing_id, operation_id, amount, description)
- `treasury.safe` (name, journal_id, balance, state, company_id)
- `treasury.safe.operation` (safe_id, date, category_id, partner_id, amount, ref, move_id, state, operation_type)
- `treasury.transfer` (source_type, source_id, dest_type, dest_id, amount, date, state, move_ids)
- `treasury.operation.category` (name, code, operation_type)

---

### PROMPT 2 — Module Bancaire : `adi_treasury_bank` (Operations Bancaires)

Creer un module Odoo 19 `adi_treasury_bank` de gestion bancaire comprenant :

- **Comptes bancaires (treasury.bank)** : gestion des comptes bancaires lies aux journaux de type "bank", suivi du solde, gestion du decouvert autorise
- **Operations bancaires (treasury.bank.operation)** : operations par cheque, virement, carte bancaire, prelevement, avec date de valeur et date d'operation
- **Cloture bancaire (treasury.bank.closing)** : rapprochement periodique des comptes bancaires avec lignes de detail
- **Transferts etendus** : transferts banque<->caisse, banque<->coffre, banque<->banque avec ecritures comptables automatiques
- **Modes de paiement bancaires** : personnalisation des modes de paiement par journal bancaire, controle de doublons sur les numeros de cheques/virements
- **Integration avec les paiements Odoo** : liaison avec account.payment pour les encaissements et decaissements clients/fournisseurs
- **Releves bancaires** : generation et consultation des releves de compte

**Modeles a creer :**
- `treasury.bank` (name, journal_id, bank_account_id, balance, overdraft_limit, state, company_id)
- `treasury.bank.operation` (bank_id, date, value_date, payment_method[cheque/virement/carte/prelevement], partner_id, amount, ref, check_number, move_id, state, operation_type)
- `treasury.bank.closing` (bank_id, date, opening_balance, closing_balance, state, line_ids)
- `treasury.bank.closing.line` (closing_id, operation_id, amount, description)

**Dependances** : `adi_treasury`

---

### PROMPT 3 — Module Comptage : `adi_treasury_cashcount` (Comptage Billets & Pieces)

Creer un module Odoo 19 `adi_treasury_cashcount` de comptage de caisse comprenant :

- **Comptage detaille par coupure** : saisie du nombre de billets et pieces par denomination (ex: 2000 DA, 1000 DA, 500 DA, 200 DA, 100 DA, 50 DA, 20 DA, 10 DA, 5 DA)
- **Gestion des denominations** : modele configurable de denominations (billets et pieces) avec valeur faciale
- **Comptage final** : wizard de comptage avec onglets Billets/Pieces/Tous, calcul automatique du total en temps reel
- **Comptage initial** : verification du solde d'ouverture a la reprise d'une cloture, comptage initial avec detail par coupure
- **Ecarts** : affichage automatique de l'ecart entre le solde theorique et le comptage reel, alerte visuelle en cas de difference
- **Option de forcage** : possibilite de forcer la validation malgre un ecart (avec tracabilite), configurable par caisse ou globalement
- **Integration cloture** : les resultats de comptage (initial et final) apparaissent dans le formulaire de cloture avec detail des coupures

**Modeles a creer :**
- `treasury.denomination` (name, value, type[bill/coin], currency_id, active)
- `treasury.cashcount` (closing_id, count_type[initial/final], total, variance, date, forced, force_reason)
- `treasury.cashcount.line` (cashcount_id, denomination_id, quantity, subtotal)

**Dependances** : `adi_treasury`

---

### PROMPT 4 — Module Dashboard : `adi_treasury_dashboard` (Tableau de Bord)

Creer un module Odoo 19 `adi_treasury_dashboard` de tableau de bord tresorerie comprenant :

- **Vue d'ensemble des caisses** : affichage kanban de toutes les caisses avec leur solde actuel, couleurs selon le statut
- **Vue d'ensemble des banques** : affichage kanban des comptes bancaires avec soldes
- **Vue d'ensemble des coffres** : affichage des coffres-forts avec leurs soldes
- **Totaux calcules** : Total Caisses, Total Banques, Total Coffres, Total General (somme des trois)
- **Indicateurs de statut** : badges visuels "Finalise"/"En cours" pour chaque entite
- **Soldes bancaires detailles** :
  - Solde courant : toutes operations validees
  - Solde rapproche : operations rapprochees avec releve bancaire
  - Solde non rapproche : operations en attente de rapprochement
- **Raccourcis de navigation** : liens directs depuis les cartes du dashboard vers les formulaires detailles de chaque caisse/banque/coffre
- **Interface OWL** : utiliser le framework OWL d'Odoo 19 pour un dashboard reactif et moderne avec composants JavaScript

**Dependances** : `adi_treasury`, `adi_treasury_bank`

---

### PROMPT 5 — Module Controle : `adi_treasury_control` (Controle & Securite)

Creer un module Odoo 19 `adi_treasury_control` de controle et securite de tresorerie comprenant :

**Controle des transferts :**
- Verification du solde disponible avant tout transfert (toutes sources : caisse, banque, coffre)
- Verification du montant maximum a la destination
- Autorisation de solde negatif configurable par entite
- Controle du decouvert bancaire
- Messages d'avertissement detailles
- Historique des controles de transfert

**Controle d'acces :**
- Regles d'acces par utilisateur pour les caisses, coffres, banques, operations et transferts
- Menus dynamiques (visibles uniquement si l'utilisateur a acces)
- Filtres automatiques pour n'afficher que les entites autorisees
- Les managers ont un acces complet
- Groupes de securite : Utilisateur Tresorerie, Manager Tresorerie

**Protection des operations :**
- Interdiction de supprimer des operations dans des clotures validees
- Interdiction de supprimer des operations comptabilisees (posted)
- Bouton "Remettre en brouillon" pour contrepassation
- Protection des operations liees aux transferts et paiements

**Controle des paiements :**
- Affichage des soldes source et destination dans le formulaire de transfert
- Alerte visuelle rouge si le montant depasse le solde disponible
- Restriction de la creation de partenaires depuis les paiements et operations de tresorerie (forcer la selection de partenaires existants via widget many2one sans quick_create)

**Modeles a creer / etendre :**
- `treasury.access.rule` (user_id, entity_type[cash/safe/bank], entity_id, access_level)
- `treasury.transfer.control.log` (transfer_id, check_type, result, message, date)

**Fichiers de securite :**
- `security/treasury_security.xml` : groupes et regles d'acces
- `security/ir.model.access.csv` : droits CRUD par groupe

**Dependances** : `adi_treasury`, `adi_treasury_bank`

---

### PROMPT 6 — Module Ameliorations : `adi_treasury_enhanced` (Workflow Ameliore)

Creer un module Odoo 19 `adi_treasury_enhanced` d'ameliorations du workflow de tresorerie comprenant :

- **Affichage des operations manuelles** : visualisation claire des operations manuelles dans le formulaire de cloture, avec distinction entre operations automatiques et manuelles
- **Bouton intelligent "Operations a traiter"** : bouton smart avec compteur affichant le nombre d'operations en attente de traitement dans chaque cloture
- **Actions groupees sur les operations** : validation en lot et suppression en lot des operations via server actions
- **Workflow de cloture ameliore** : processus de cloture optimise avec etapes claires et validation par etapes
- **Visualisation des operations** : interface claire pour visualiser et traiter les operations en attente avec filtres et regroupements

**Dependances** : `adi_treasury`

---

### PROMPT 7 — Module Depenses : `adi_cash_expense` (Depenses & Avances)

Creer un module Odoo 19 `adi_cash_expense` de gestion des depenses de caisse comprenant :

- **Remboursement des employes** : workflow complet achat -> justification (piece jointe) -> validation -> remboursement depuis la caisse, avec suivi du statut
- **Avances de caisse** : gestion des avances aux employes (montant verse, suivi du solde restant, regularisation/apurement partiel ou total)
- **Comptes personnels** : suivi du solde par employe, plafond d'avance paramerable, historique complet des mouvements (avances et remboursements)
- **Integrations** :
  - Avec le module de tresorerie : generation automatique d'operations de caisse lors du remboursement ou de l'avance
  - Avec le module RH : liaison avec hr.employee pour identifier l'employe beneficiaire
  - Avec les pieces justificatives : gestion des attachments (factures, recus) lies aux depenses
- **Workflow de validation** : circuit d'approbation des depenses et avances (demande -> approbation manager -> paiement)

**Modeles a creer :**
- `cash.expense` (employee_id, date, amount, description, state[draft/submitted/approved/paid/refused], expense_type[reimbursement/advance], cash_id, operation_id, attachment_ids)
- `cash.expense.line` (expense_id, description, amount, account_id)
- `employee.cash.account` (employee_id, balance, advance_limit, line_ids)
- `employee.cash.account.line` (account_id, date, amount, type[advance/reimbursement/settlement], expense_id, ref)

**Dependances** : `adi_treasury`, `hr`

---

## NOTES TECHNIQUES POUR ODOO 19

### Differences majeures Odoo 15 → Odoo 19 a prendre en compte :

1. **Framework JS** : Utiliser OWL 2.x (natif Odoo 19) au lieu de jQuery/Widget legacy
2. **Manifest** : Utiliser `__manifest__.py` avec `'version': '19.0.1.0.0'`
3. **Assets** : Declarer les assets dans `__manifest__.py` via `'assets'` dict au lieu de `template` XML
4. **Vues** : Utiliser les nouvelles API de vues Odoo 19
5. **Champs** : Utiliser `fields.Json` si disponible, `Command` au lieu de tuples `(0, 0, vals)`
6. **API** : Verifier les changements d'API sur `account.move`, `account.payment` entre v15 et v19
7. **Securite** : Utiliser les record rules modernes et les groupes XML
8. **Tests** : Ajouter des tests unitaires avec `TransactionCase` et `HttpCase`
9. **Multi-societe** : Supporter le multi-company natif avec `company_id` et regles d'acces
10. **Localisation** : Les denominations de billets/pieces doivent etre configurables par devise/pays
