# Module Comptage des Billets et Pièces

## Description

Extension du module `adi_treasury` permettant le comptage détaillé des billets et pièces lors de la clôture de caisse.

## Fonctionnalités

### 1. Gestion des Dénominations
- Configuration des dénominations de billets et pièces
- Support multi-devises
- Dénominations pré-configurées pour le Dinar Algérien (DZD) :
  - **Billets** : 2000 DA, 1000 DA, 500 DA, 200 DA
  - **Pièces** : 200 DA, 100 DA, 50 DA, 20 DA, 10 DA, 5 DA

### 2. Comptage lors de la Clôture
- Interface de comptage intuitive dans la clôture de caisse
- Saisie du nombre de billets/pièces par dénomination
- Calcul automatique du total compté
- Mise à jour automatique du solde réel

### 3. Exemple d'utilisation

Lors de la clôture, saisissez :
- 20 × Billet de 2000 DA = 40 000 DA
- 10 × Billet de 1000 DA = 10 000 DA
- 10 × Billet de 500 DA = 5 000 DA
- 20 × Pièce de 200 DA = 4 000 DA
- **Total compté** = 59 000 DA

Le solde réel est automatiquement mis à jour avec ce montant.

## Installation

1. Le module dépend de `adi_treasury`
2. Installer le module depuis le menu Applications
3. Les dénominations DZD sont créées automatiquement

## Configuration

### Ajouter de nouvelles dénominations

Menu : **Trésorerie > Configuration > Dénominations**

1. Cliquer sur "Créer"
2. Renseigner :
   - Nom (ex: "Billet de 500 EUR")
   - Valeur (ex: 500)
   - Devise (ex: EUR)
   - Type (Billet ou Pièce)
3. Enregistrer

## Utilisation

### Comptage lors de la clôture

1. Ouvrir une clôture de caisse en mode brouillon
2. Activer l'option **"Utiliser le comptage"**
3. Cliquer sur **"Initialiser le comptage"**
4. Saisir le nombre de billets/pièces pour chaque dénomination
5. Le **Total compté** et le **Solde réel** sont calculés automatiquement
6. Comparer avec le **Solde théorique** pour détecter les écarts
7. Valider la clôture

### Boutons disponibles

- **Initialiser le comptage** : Crée automatiquement une ligne pour chaque dénomination active
- **Réinitialiser le comptage** : Remet toutes les quantités à 0

## Modèles de données

### cash.denomination
- Dénominations des billets et pièces
- Champs : name, value, currency_id, type (bill/coin)

### treasury.cash.closing.count
- Lignes de comptage pour chaque clôture
- Champs : closing_id, denomination_id, quantity, subtotal

### treasury.cash.closing (héritage)
- Nouveaux champs :
  - `count_line_ids` : Lignes de comptage
  - `counted_total` : Total calculé
  - `use_cash_count` : Activer/désactiver le comptage

## Sécurité

- Les utilisateurs de trésorerie peuvent lire et créer des comptages
- Les managers peuvent tout faire, y compris gérer les dénominations

## Compatibilité

- Odoo 15.0
- Module parent : adi_treasury 15.0.1.0.0

## Auteur

ADICOPS - https://adicops-dz.com
