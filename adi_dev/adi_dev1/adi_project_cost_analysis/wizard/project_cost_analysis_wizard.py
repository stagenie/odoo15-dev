from odoo import api, fields, models


class ProjectCostAnalysisWizard(models.TransientModel):
    _name = 'project.cost.analysis.wizard'
    _description = 'Analyse des Coûts Projets'

    project_ids = fields.Many2many('project.project', string='Projets',
        help="Laisser vide pour inclure tous les projets")
    date_from = fields.Date('Date du')
    date_to = fields.Date('Date fin')
    product_ids = fields.Many2many('product.product', string='Articles',
        help="Laisser vide pour inclure tous les articles")

    def get_report_data(self):
        domain = [
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
            ('move_id.state', '=', 'posted'),
            ('analytic_account_id', '!=', False),
            ('display_type', '=', False),
        ]

        if self.project_ids:
            analytic_ids = self.project_ids.filtered('analytic_account_id').mapped('analytic_account_id').ids
            if not analytic_ids:
                return []
            domain.append(('analytic_account_id', 'in', analytic_ids))

        if self.date_from:
            domain.append(('move_id.invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('move_id.invoice_date', '<=', self.date_to))

        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))

        lines = self.env['account.move.line'].search(domain)
        if not lines:
            return []

        line_analytic_ids = lines.mapped('analytic_account_id').ids

        if self.project_ids:
            projects_to_check = self.project_ids.filtered('analytic_account_id')
        else:
            projects_to_check = self.env['project.project'].search([
                ('analytic_account_id', 'in', line_analytic_ids)
            ])

        analytic_to_project = {
            p.analytic_account_id.id: p
            for p in projects_to_check
            if p.analytic_account_id
        }

        result = {}
        for line in lines:
            if not line.product_id:
                continue
            project = analytic_to_project.get(line.analytic_account_id.id)
            if not project:
                continue

            proj_key = project.id
            if proj_key not in result:
                result[proj_key] = {
                    'project': project,
                    'products': {},
                    'total': 0.0,
                }

            prod_key = line.product_id.id
            if prod_key not in result[proj_key]['products']:
                result[proj_key]['products'][prod_key] = {
                    'product': line.product_id,
                    'qty': 0.0,
                    'amount': 0.0,
                }

            sign = -1 if line.move_id.move_type == 'in_refund' else 1
            result[proj_key]['products'][prod_key]['qty'] += line.quantity * sign
            result[proj_key]['products'][prod_key]['amount'] += line.price_subtotal * sign
            result[proj_key]['total'] += line.price_subtotal * sign

        final = []
        for proj_data in sorted(result.values(), key=lambda x: x['project'].name):
            product_lines = []
            for p in sorted(proj_data['products'].values(), key=lambda x: x['product'].name):
                qty = p['qty']
                amount = p['amount']
                p['price_unit'] = (amount / qty) if qty else 0.0
                product_lines.append(p)
            final.append({
                'project': proj_data['project'],
                'lines': product_lines,
                'total': proj_data['total'],
            })

        return final

    def get_currency(self):
        return self.env.company.currency_id

    def action_preview(self):
        action = self.env.ref(
            'adi_project_cost_analysis.action_report_project_cost_analysis'
        ).report_action(self)
        action['report_type'] = 'qweb-html'
        return action

    def action_print(self):
        return self.env.ref(
            'adi_project_cost_analysis.action_report_project_cost_analysis'
        ).report_action(self)
