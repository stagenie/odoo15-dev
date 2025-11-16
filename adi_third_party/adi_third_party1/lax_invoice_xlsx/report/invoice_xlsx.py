from odoo import models
import json


class InvoiceXlsx(models.AbstractModel):
    _name = 'report.lax_invoice_xlsx.report_invoice_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = "Invoice Xlsx report"

    def generate_xlsx_report(self, workbook, data, invoice):
        for obj in invoice:
            sheet = workbook.add_worksheet(obj.name)
            bold = workbook.add_format({'bold': True})
            date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
            align_center = workbook.add_format({'align': 'center'})
            row = 5
            col = 6
            sheet.write(row, col, 'Order Date', bold)
            col += 1
            sheet.write(row, col, obj.invoice_date, date_format)
            row += 1
            col -= 1
            sheet.write(row, col, 'Payment Terms', bold)
            col += 1
            sheet.write(row, col, obj.invoice_payment_term_id.name)
            row = 1
            col = 1
            sheet.merge_range(row, col, row, col + 6, 'Invoice', align_center)
            row += 2
            col = 1
            sheet.write(row, col, obj.name, bold)
            row += 2
            sheet.write(row, col, 'Customer', bold)
            col += 1
            sheet.write(row, col, obj.partner_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'Salesperson', bold)
            col += 1
            sheet.write(row, col, obj.invoice_user_id.name)
            row += 1
            col -= 1
            sheet.write(row, col, 'State', bold)
            col += 1
            sheet.write(row, col, obj.state)
            row += 2
            col = 1
            sheet.write(row, col, 'Product', bold)
            col += 1
            sheet.write(row, col, 'Description', bold)
            col += 1
            sheet.write(row, col, 'Quantity', bold)
            col += 1
            sheet.write(row, col, 'UoM', bold)
            col += 1
            sheet.write(row, col, 'Price', bold)
            col += 1
            sheet.write(row, col, 'Taxes', bold)
            col += 1
            sheet.write(row, col, 'Subtotal', bold)
            row += 1
            col = 1
            tx_list = []
            for record in obj.invoice_line_ids:
                for tx in record.tax_ids:
                    tx_list.append(tx.name)
                sheet.write(row, col, record.product_id.name)
                col += 1
                sheet.write(row, col, record.name)
                col += 1
                sheet.write(row, col, record.quantity)
                col += 1
                sheet.write(row, col, record.product_uom_id.name)
                col += 1
                sheet.write(row, col, record.price_unit)
                col += 1
                sheet.write(row, col, ', '.join(tx_list))
                col += 1
                sheet.write(row, col, record.price_subtotal)
                col = 1
                row += 1
                tx_list.clear()
            row += 1
            col = 6
            sheet.write(row, col, 'Untaxed Amount:', bold)
            col += 1
            sheet.write(row, col, json.loads(obj.tax_totals_json).get('amount_untaxed'))
            row += 1
            col = 6
            if json.loads(obj.tax_totals_json).get('groups_by_subtotal').get('Untaxed Amount'):
                for rec in json.loads(obj.tax_totals_json).get('groups_by_subtotal').get('Untaxed Amount'):
                    sheet.write(row, col, rec.get('tax_group_name'))
                    col += 1
                    sheet.write(row, col, rec.get('tax_group_amount'))
                    row += 1
                    col -= 1
            col = 6
            sheet.write(row, col, 'Total:')
            col += 1
            sheet.write(row, col, json.loads(obj.tax_totals_json).get('amount_total'))
