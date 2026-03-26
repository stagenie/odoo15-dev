{
    'name': 'Reçu de Paiement avec Solde',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Reçu de paiement avec ancien solde, montant versé et solde final',
    'description': """
        Ajoute un rapport PDF "Reçu de Paiement avec Solde" sur les paiements
        affichant l'ancien solde, le montant versé et le solde final du partenaire.
    """,
    'depends': ['account'],
    'data': [
        'report/report_action.xml',
        'report/report_payment_receipt_balance.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
