{
    'name': 'Fix Affichage Paiement à Terme',
    'version': '15.0.1.0.0',
    'category': 'Accounting',
    'summary': "Affiche 'Paiement à Terme' lorsque aucun paiement n'est enregistré et que le mode de paiement n'est pas défini",
    'description': """
        Module de correction pour les rapports de facture/vente AB.

        - Remplace "À définir" / "Date à terme" par "Paiement à Terme"
        - Masque le bloc "Mode de règlement" lorsqu'un paiement existe
          déjà (et que le mode de paiement n'est pas défini), car les
          détails de paiement sont déjà affichés ailleurs.

        Templates impactés :
        - l10n_dz_droit_timbre.adi_report_invoice (Facture)
        - l10n_dz_droit_timbre.adi_bl_report_invoice (Vente BL)
        - adi_ab_invoice_reports.ab_vente_ttc_report (Vente TTC)
    """,
    'depends': ['adi_ab_invoice_reports'],
    'data': [
        'views/report_payment_term_fix.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
