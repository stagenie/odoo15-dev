# Module de Gestion des Dépenses de Caisse

## Description

Module Odoo 15 de gestion complète des dépenses de caisse, permettant de gérer les remboursements et les avances des employés avec intégration au module de trésorerie `adi_treasury`.

## Fonctionnalités

### 1. Gestion des Remboursements
- L'employé achète avec ses propres fonds
- Soumission de la dépense avec justificatifs obligatoires
- Workflow d'approbation par un responsable
- Paiement par le caissier
- Création automatique d'une opération de caisse

### 2. Gestion des Avances
- Attribution d'une avance de caisse à l'employé
- Suivi du solde restant
- Règlement de l'avance avec justificatifs des dépenses réelles
- Gestion automatique :
  - Retour d'argent si l'employé n'a pas tout dépensé
  - Paiement supplémentaire si les dépenses dépassent l'avance
  - Aucune opération si le montant exact a été dépensé

### 3. Comptes Personnels
- Création automatique d'un compte par employé
- Suivi du solde actuel (avances en cours)
- Configuration de limites d'avance par employé
- Historique complet des dépenses
- Statistiques : total des dépenses, avances, remboursements

### 4. Lignes de Dépenses Détaillées
- Ajout de plusieurs lignes par dépense
- Référence optionnelle à des articles (products)
- Quantité, prix unitaire, total automatique
- Justificatifs attachables par ligne

### 5. Sécurité et Droits d'Accès
- **Utilisateur** : Créer et soumettre ses propres dépenses
- **Responsable** : Approuver toutes les dépenses
- **Caissier** : Payer et régler les dépenses approuvées

## Dépendances

- `base`
- `account`
- `hr` (Ressources Humaines)
- `adi_treasury` (Module de trésorerie ADICOPS)

## Installation

1. Assurez-vous que le module `adi_treasury` est installé
2. Copiez le module `adi_cash_expense` dans votre répertoire addons
3. Mettez à jour la liste des applications
4. Installez le module `adi_cash_expense`

## Configuration

### Droits d'accès
1. Allez dans Paramètres > Utilisateurs & Sociétés > Utilisateurs
2. Assignez les groupes appropriés :
   - **Dépenses Caisse / Utilisateur** : Pour les employés
   - **Dépenses Caisse / Responsable** : Pour les gestionnaires
   - **Dépenses Caisse / Caissier** : Pour les caissiers

### Limites d'avance
1. Allez dans Dépenses Caisse > Comptes > Comptes personnels
2. Sélectionnez un compte d'employé
3. Définissez la "Limite d'avance" (0 = pas de limite)

## Utilisation

### Créer un remboursement

1. Menu : **Dépenses Caisse > Opérations > Remboursements**
2. Cliquez sur "Créer"
3. Sélectionnez :
   - Type : Remboursement
   - Employé bénéficiaire
   - Département (optionnel)
   - Caisse
4. Ajoutez les lignes de dépenses
5. Joignez les justificatifs
6. Cliquez sur "Soumettre"
7. Le responsable approuve
8. Le caissier paie

### Créer une avance

1. Menu : **Dépenses Caisse > Opérations > Avances**
2. Cliquez sur "Créer"
3. Sélectionnez :
   - Type : Avance
   - Employé bénéficiaire
   - Montant
   - Caisse
4. Décrivez l'objectif de l'avance
5. Cliquez sur "Soumettre"
6. Le responsable approuve
7. Le caissier paie (l'argent est donné à l'employé)
8. Plus tard, cliquez sur "Régler" pour finaliser
9. Indiquez le montant réellement dépensé
10. Joignez les justificatifs
11. Le système calcule automatiquement le solde

### Consulter un compte personnel

1. Menu : **Dépenses Caisse > Comptes > Comptes personnels**
2. Sélectionnez un employé
3. Consultez :
   - Solde actuel
   - Limite d'avance
   - Total des dépenses
   - Avances en cours
   - Historique complet

## Workflow des États

### Remboursement
```
Brouillon → Soumis → Approuvé → Réglé
```

### Avance
```
Brouillon → Soumis → Approuvé → Payé → Réglé
```

À tout moment (sauf Payé/Réglé) : → Annulé

## Intégrations avec adi_treasury

Le module crée automatiquement des opérations de trésorerie :

- **Remboursement** : Sortie de caisse (catégorie "Remboursement employé")
- **Avance** : Sortie de caisse (catégorie "Avance employé")
- **Retour d'avance** : Entrée de caisse (catégorie "Retour d'avance")
- **Paiement supplémentaire** : Sortie de caisse (catégorie "Paiement supplémentaire")

Toutes les opérations sont automatiquement liées aux clôtures de caisse.

## Rapports

Le module génère automatiquement :
- **Bon de dépense** : Document imprimable pour chaque dépense
- Contient toutes les informations et signatures nécessaires
- Différent selon le type (remboursement ou avance)

## Support

Pour toute question ou assistance :
- Email : info@adicops.com
- Web : https://adicops-dz.com

## Auteur

**ADICOPS**
Solutions ERP pour l'Algérie

## License

LGPL-3

## Version

15.0.1.0.0 (Odoo 15)
