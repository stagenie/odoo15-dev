# Modules Odoo 15 Développés pour AB Energie

## Description Générale du Projet

Développement d'une suite complète de modules Odoo 15 sur mesure pour **AB Energie**, couvrant l'ensemble des processus métier : gestion commerciale, trésorerie, stock, facturation, rapports et localisation algérienne. Ces modules apportent une **valeur ajoutée significative** en automatisant les processus critiques, en renforçant les contrôles internes et en offrant une visibilité en temps réel sur l'activité de l'entreprise.

---

## 1. Gestion de Trésorerie (Suite Complète)

> **Valeur ajoutée** : Gestion centralisée et sécurisée de l'ensemble de la trésorerie (caisses, coffres, banques) avec traçabilité complète, comptage physique obligatoire et tableau de bord en temps réel.

| Module | Description |
|--------|-------------|
| `adi_treasury` | Gestion complète de la trésorerie avec caisses, coffres et transferts inter-journaux |
| `adi_treasury_bank` | Gestion des comptes bancaires et opérations bancaires (chèques, virements) |
| `adi_treasury_cashcount` | Comptage détaillé des billets et pièces lors de la clôture de caisse |
| `adi_treasury_cashcount_extended` | Extension du comptage avec wizard et option de forçage pour cas exceptionnels |
| `adi_treasury_cashcount_init` | Comptage initial pour vérifier le solde de départ des clôtures |
| `adi_treasury_dashboard` | Tableau de bord pour visualiser les soldes des caisses et banques |
| `adi_treasury_dashboard_extended` | Extension avec affichage des coffres et totaux avancés |
| `adi_treasury_enhanced` | Améliorations des clôtures de caisse (validation, sécurité) |
| `adi_treasury_access` | Gestion des accès, visibilité et protection des opérations de trésorerie par utilisateur |
| `adi_treasury_balance_display` | Affichage des soldes rapprochés et non rapprochés des banques |
| `adi_treasury_transfer_control` | Contrôle avancé des transferts entre caisses, coffres et banques |
| `adi_cash_expense` | Gestion des dépenses de caisse avec remboursements et avances |
| `adi_transfert_control` | Contrôle des transferts entre caisses et banques avec affichage des soldes |

---

## 2. Gestion des Transferts et du Stock

> **Valeur ajoutée** : Maîtrise complète des flux de stock inter-dépôts avec validation à deux niveaux, contrôle des disponibilités, gestion des envois partiels et traçabilité des mouvements.

| Module | Description |
|--------|-------------|
| `adi_stock_transfer` | Gestion des transferts inter-dépôts avec validation à deux niveaux (demandeur/récepteur) |
| `adi_stock_transfer_enhanced` | Réservation multi-emplacement, restriction par équipe et gestion des reliquats |
| `adi_stock_transfer_suite` | Gestion des envois partiels avec option de renvoi du reste |
| `adi_stock_transfer_fix` | Outil de correction des transferts et pickings bloqués |
| `adi_stock_transfer_report` | Bon de transfert légal avec en-têtes par équipe commerciale |
| `adi_stock_transfer_control_fix` | Contrôle des transferts avec affichage de la quantité disponible, blocage si stock insuffisant |
| `adi_inventory_tracking` | Suivi des articles inventoriés avec filtrage par date d'inventaire |
| `adi_inventory_tracking_init` | Initialisation du suivi d'inventaire (rétro-remplissage depuis l'historique) |
| `adi_stock_print` | Impression de l'état du stock avec différentes options de filtrage |
| `product_inventory_report` | Rapport d'inventaire détaillé avec quantités par emplacement et nom du partenaire |
| `adi_transfert_stock` | Affichage des emplacements source/destination en haut du formulaire de transfert |
| `adi_global_stock_qty` | Affichage de la quantité totale en stock pour tous les utilisateurs (sans révéler les emplacements) |
| `adi_stock_manager_access` | Gestion des droits Stock Manager (entrepôts, emplacements, valeur inventaire) |
| `adi_stock_moves_report` | Rapport des mouvements de produits et palettes |
| `adi_global_delivery` | Regroupement des bons de livraison |

---

## 3. Rapports de Vente et Facturation Personnalisés

> **Valeur ajoutée** : Rapports commerciaux entièrement personnalisés (Devis, Proforma, Bon de commande, Facture, BL valorisé) avec impression conditionnelle selon le type de journal, formatage intelligent des quantités et affichage adapté TTC/HT.

| Module | Description |
|--------|-------------|
| `adi_ab_sale_reports` | Personnalisation complète des rapports de vente (Devis sans TVA en TTC, Proforma, Bon de commande avec délai de livraison et modalités de paiement) |
| `adi_ab_invoice_reports` | Personnalisation des rapports de factures (Facture, Facture sans paiement, BL valorisé) avec mode de règlement en bas |
| `adi_total_discount` | Calcul et affichage du total de remise dans les documents commerciaux |
| `adi_journal_report_type` | Impression conditionnelle selon le type de journal (Facture / Vente) |
| `adi_report_qty_format` | Suppression des décimales inutiles dans les quantités des rapports |
| `adi_report_template_config` | Configuration avancée des templates de rapports avec styles personnalisables |
| `adi_team_header` | En-tête personnalisée par équipe commerciale dans les rapports |
| `adi_team_header_enhanced` | Amélioration de l'affichage de l'en-tête avec coordonnées fiscales |
| `adi_number_in_reports` | Numérotation dans les rapports |

---

## 4. Gestion Commerciale et Contrôles de Vente

> **Valeur ajoutée** : Sécurisation du processus de vente avec contrôle de limite de crédit, alerte articles en double, préservation des prix, sauvegarde automatique et gestion avancée des équipes commerciales.

| Module | Description |
|--------|-------------|
| `adi_auto_save` | Sauvegarde automatique des devis/commandes clients et fournisseurs |
| `adi_duplicate_article_alert` | Alerte lors de la saisie en double d'un article dans les bons (vente, achat, livraison) |
| `adi_partner_credit_limit` | Affichage du solde client et solde maximum dans les bons de commande |
| `adi_partner_credit_limit_delivery` | Option de blocage de la limite de crédit au niveau de la livraison (pas seulement la commande) |
| `adi_sale_price_preserve` | Préservation du prix unitaire saisi manuellement lors de modification des lignes de devis |
| `adi_sale_team_security` | Sécurité par équipe commerciale (restriction de visibilité) |
| `adi_picking_team_control` | Contrôle des BL par équipe commerciale (restriction validation et modification entrepôt) |
| `adi_opp_number` | Champ OPP Number sur les devis/commandes |
| `adi_sale_product_history` | Historique des prix de vente par produit |
| `adi_sale_product_history_contact` | Filtre par contact dans l'historique des prix de vente |
| `adi_total_solde_customer` | Affichage du solde total dû par client |
| `adi_delivery_synch` | Synchronisation du statut de livraison |
| `adi_sale_project_costing` | Calcul de prix de vente à partir du coût avec marges (équipement + main d'oeuvre) |

---

## 5. Facturation et Comptabilité

> **Valeur ajoutée** : Contrôles renforcés sur la facturation (séquence/date, paiements bancaires, exclusion de solde), automatisation des processus de paiement et nettoyage comptable.

| Module | Description |
|--------|-------------|
| `adi_bank_payment_mode` | Extension des modes de paiement bancaires avec contrôle de non-duplication des N° de chèque/virement |
| `adi_partner_ledger_exclude` | Option "Ne pas inclure dans le calcul de solde" sur les factures avec filtre approprié |
| `adi_invoice_date_sequence_control` | Contrôle de cohérence entre dates et numéros séquentiels des factures |
| `adi_invoice_line_sync` | Ajout de lignes de facture depuis d'autres factures validées (sélection multiple) |
| `adi_invoice_payment_button` | Smart Button pour afficher les paiements liés à une facture |
| `adi_invoice_observation` | Champ observation sur les factures |
| `adi_payment_shortcuts` | Raccourcis rapides pour les paiements clients et fournisseurs |
| `adi_payment_partner_restrict` | Désactivation de la création de partenaires depuis les paiements et opérations de trésorerie |
| `adi_journal_visibility` | Masquage de journaux sans archivage |
| `adi_service_journal` | Journaux d'achat dédiés aux services |
| `adi_service_supplier` | Gestion des fournisseurs de service avec journal dédié |
| `adi_account_cleanup` | Détection et correction des écritures orphelines, suppression des documents annulés |
| `adi_journal_restricted_extended` | Extension de restriction des journaux par utilisateur |

---

## 6. Gestion des Retours Clients et Fournisseurs

> **Valeur ajoutée** : Processus complet de retour avec création automatique d'avoirs, traçabilité et gestion des retours tant côté client que fournisseur.

| Module | Description |
|--------|-------------|
| `adi_return_management` | Gestion complète des retours clients avec création automatique d'avoirs et wizard d'analyse |
| `adi_supplier_return_management` | Gestion complète des retours fournisseurs avec création automatique d'avoirs |

---

## 7. Localisation Algérienne

> **Valeur ajoutée** : Conformité totale avec la réglementation algérienne (plan comptable SCF, droit de timbre, informations fiscales, rapports normalisés).

| Module | Description |
|--------|-------------|
| `dns_l10n_dz_scf` | Plan comptable normalisé - Système Comptable Financier Algérien |
| `l10n_dz_droit_timbre` | Gestion du droit de timbre (timbre de quittances) avec colonne timbre dans les factures |
| `l10n_dz_information_fiscale` | Informations fiscales algériennes (RC, AI, NIF, NIS) avec contrôle d'impression |
| `l10n_dz_reports` | Rapports selon les normes algériennes |
| `l10n_dz_collectivite_territoriale` | Collectivités territoriales algériennes (wilayas, communes) |
| `dns_amount_to_text_dz` | Conversion des montants en lettres (Dinars Algériens) |

---

## 8. Ressources Humaines

> **Valeur ajoutée** : Gestion simplifiée de la paie avec intégration pointage, avances et prêts employés.

| Module | Description |
|--------|-------------|
| `adi_simple_attendance` | Module simplifié de gestion des pointages quotidiens |
| `adi_simple_payroll` | Module de paie simplifié avec intégration pointage, avances et prêts |
| `adi_employee_advance` | Gestion des avances sur salaire avec factures fournisseur automatiques |
| `adi_employee_loans` | Gestion des prêts employés avec échéancier de remboursement |

---

## 9. Outils et Productivité

> **Valeur ajoutée** : Fonctionnalités transversales améliorant l'expérience utilisateur et la productivité quotidienne.

| Module | Description |
|--------|-------------|
| `adi_whatsapp_send` | Envoi de documents commerciaux via WhatsApp |
| `adi_disable_quick_create` | Désactivation de la création rapide pour produits et partenaires (évite les erreurs) |
| `adi_hide_cost_margin` | Masquage des coûts et marges pour les utilisateurs non autorisés |
| `adi_hide_rainbow` | Masquage global du Rainbow Man |
| `adi_partner_custom_fields` | Champs personnalisés sur les partenaires (dimensions sur lignes commande/facture) |
| `adi_pack_product_bom` | Gestion des packs de produits avec nomenclatures de type kit |
| `adi_quantity_invoiced` | Affichage des quantités facturées |
| `adi_track_products_invoiced` | Suivi des produits facturés |
| `adi_stock_default` | Configuration produit stockable par défaut |
| `adi_dz_blv_faroute` | Facture de route / BL valorisé |
| `adi_expenses` | Gestion des dépenses de l'entreprise |
| `adi_phy_inv_restriction` | Restriction d'accès aux inventaires physiques par utilisateur |

---

## 10. Module Spécialisé - MAGIMED

> **Valeur ajoutée** : Conformité ISO pour la gestion pharmaceutique avec traçabilité complète.

| Module | Description |
|--------|-------------|
| `adi_magimed` | Gestion de traçabilité complète pour conformité ISO - MAGIMED (gestion pharmaceutique interne) |

---

## Synthèse

| Domaine | Nombre de modules |
|---------|:-----------------:|
| Gestion de Trésorerie | 13 |
| Gestion des Transferts et du Stock | 15 |
| Rapports de Vente et Facturation | 9 |
| Gestion Commerciale et Contrôles | 13 |
| Facturation et Comptabilité | 13 |
| Retours Clients / Fournisseurs | 2 |
| Localisation Algérienne | 6 |
| Ressources Humaines | 4 |
| Outils et Productivité | 12 |
| Module Spécialisé (MAGIMED) | 1 |
| **TOTAL** | **88** |

---

## Points Forts de la Solution

1. **Couverture fonctionnelle complète** : De la vente à la trésorerie en passant par le stock et la comptabilité
2. **Sécurité et contrôles** : Validation multi-niveaux, restrictions par équipe, contrôle des limites de crédit
3. **Conformité algérienne** : Plan comptable SCF, droit de timbre, informations fiscales
4. **Traçabilité** : Suivi complet des mouvements de stock, des paiements et des retours
5. **Productivité** : Sauvegarde automatique, raccourcis paiement, WhatsApp, rapports personnalisés
6. **Tableau de bord temps réel** : Visibilité instantanée sur les soldes caisses, coffres et banques
