from odoo import fields, models


class ProjectCostAnalysisWizard(models.TransientModel):
    _inherit = 'project.cost.analysis.wizard'

    show_detail = fields.Boolean('Détailler par facture',
        help="Affiche le détail de chaque facture fournisseur pour chaque article")

    def get_report_data(self):
        data = super().get_report_data()
        if not self.show_detail or not data:
            return data

        # Rebuild same domain as parent to fetch individual lines
        domain = [
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
            ('move_id.state', '=', 'posted'),
            ('analytic_account_id', '!=', False),
            ('display_type', '=', False),
        ]
        if self.project_ids:
            analytic_ids = self.project_ids.filtered('analytic_account_id').mapped('analytic_account_id').ids
            if analytic_ids:
                domain.append(('analytic_account_id', 'in', analytic_ids))
        if self.date_from:
            domain.append(('move_id.invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('move_id.invoice_date', '<=', self.date_to))
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))

        lines = self.env['account.move.line'].search(domain)

        # Build analytic_id → project_id map from the already-computed data
        project_ids = [p['project'].id for p in data]
        projects = self.env['project.project'].browse(project_ids)
        analytic_to_project_id = {
            p.analytic_account_id.id: p.id
            for p in projects if p.analytic_account_id
        }

        # (project_id, product_id) → list of detail lines
        detail_map = {}
        for line in lines:
            if not line.product_id:
                continue
            proj_id = analytic_to_project_id.get(line.analytic_account_id.id)
            if not proj_id:
                continue
            key = (proj_id, line.product_id.id)
            if key not in detail_map:
                detail_map[key] = []
            sign = -1 if line.move_id.move_type == 'in_refund' else 1
            detail_map[key].append({
                'invoice_name': line.move_id.name or line.move_id.ref or '—',
                'partner_name': line.move_id.partner_id.name or '',
                'date': line.move_id.invoice_date,
                'qty': line.quantity * sign,
                'price_unit': line.price_unit,
                'amount': line.price_subtotal * sign,
            })

        # Sort detail lines by date then invoice name
        for dlines in detail_map.values():
            dlines.sort(key=lambda x: (x['date'] or '', x['invoice_name'] or ''))

        for proj_data in data:
            for product_line in proj_data['lines']:
                key = (proj_data['project'].id, product_line['product'].id)
                product_line['detail_lines'] = detail_map.get(key, [])

        return data

    def action_preview(self):
        if self.show_detail:
            action = self.env.ref(
                'adi_project_cost_analysis_detail.action_report_project_cost_analysis_detail'
            ).report_action(self)
            action['report_type'] = 'qweb-html'
            return action
        return super().action_preview()

    def action_print(self):
        if self.show_detail:
            return self.env.ref(
                'adi_project_cost_analysis_detail.action_report_project_cost_analysis_detail'
            ).report_action(self)
        return super().action_print()
