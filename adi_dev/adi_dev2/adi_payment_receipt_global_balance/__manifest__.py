{
    'name': 'Reçu de Paiement - Solde Global',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Corrige le calcul du solde dans le reçu de paiement pour les partenaires client/fournisseur',
    'description': """
        Corrige le module adi_payment_receipt_balance pour afficher le solde global
        (créances - dettes) au lieu du solde uniquement client ou uniquement fournisseur.
        Utile pour les partenaires qui sont à la fois clients et fournisseurs.
    """,
    'depends': ['adi_payment_receipt_balance'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
