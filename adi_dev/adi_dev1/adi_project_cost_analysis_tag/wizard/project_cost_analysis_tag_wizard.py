from odoo import fields, models

UNTAGGED_LABEL = 'Sans étiquette'


class ProjectCostAnalysisTagWizard(models.TransientModel):
    _name = 'project.cost.analysis.tag.wizard'
    _description = 'Analyse des Coûts Projets par Dépense'

    project_ids = fields.Many2many('project.project', string='Projets',
        help="Laisser vide pour inclure tous les projets")
    date_from = fields.Date('Date du')
    date_to = fields.Date('Date fin')
    product_ids = fields.Many2many('product.product', string='Articles',
        help="Laisser vide pour inclure tous les articles")
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Dépenses (étiquettes)',
        help="Laisser vide pour inclure toutes les étiquettes")
    include_untagged = fields.Boolean('Inclure les dépenses sans étiquette', default=True,
        help="Ignoré si des étiquettes sont sélectionnées")
    show_products = fields.Boolean('Détail par article', default=True,
        help="Affiche les articles de chaque catégorie de dépense")

    def _get_line_domain(self):
        domain = [
            ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),
            ('move_id.state', '=', 'posted'),
            ('analytic_account_id', '!=', False),
            ('display_type', '=', False),
            ('product_id', '!=', False),
        ]
        if self.project_ids:
            analytic_ids = self.project_ids.filtered('analytic_account_id').mapped('analytic_account_id').ids
            domain.append(('analytic_account_id', 'in', analytic_ids))
        if self.date_from:
            domain.append(('move_id.invoice_date', '>=', self.date_from))
        if self.date_to:
            domain.append(('move_id.invoice_date', '<=', self.date_to))
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        return domain

    def _get_line_tags(self, line):
        # Tags set on the invoice line, or directly on its analytic entries
        return line.analytic_tag_ids | line.analytic_line_ids.mapped('tag_ids')

    def get_report_data(self):
        lines = self.env['account.move.line'].search(self._get_line_domain())
        if not lines:
            return []

        if self.project_ids:
            projects = self.project_ids.filtered('analytic_account_id')
        else:
            projects = self.env['project.project'].search([
                ('analytic_account_id', 'in', lines.mapped('analytic_account_id').ids)
            ])
        analytic_to_project = {p.analytic_account_id.id: p for p in projects}

        result = {}
        for line in lines:
            project = analytic_to_project.get(line.analytic_account_id.id)
            if not project:
                continue

            tags = self._get_line_tags(line)
            if self.analytic_tag_ids:
                if not (tags & self.analytic_tag_ids):
                    continue
            elif not tags and not self.include_untagged:
                continue

            tags = tags.sorted('name')
            tag_key = tuple(tags.ids)
            proj_data = result.setdefault(project.id, {
                'project': project,
                'categories': {},
                'total': 0.0,
            })
            cat = proj_data['categories'].setdefault(tag_key, {
                'name': ' + '.join(tags.mapped('name')) or UNTAGGED_LABEL,
                'untagged': not tags,
                'products': {},
                'total': 0.0,
            })
            prod = cat['products'].setdefault(line.product_id.id, {
                'product': line.product_id,
                'qty': 0.0,
                'amount': 0.0,
            })

            sign = -1 if line.move_id.move_type == 'in_refund' else 1
            amount = line.price_subtotal * sign
            prod['qty'] += line.quantity * sign
            prod['amount'] += amount
            cat['total'] += amount
            proj_data['total'] += amount

        final = []
        for proj_data in sorted(result.values(), key=lambda x: x['project'].name):
            categories = []
            # Tagged categories by name, untagged last
            for cat in sorted(proj_data['categories'].values(),
                              key=lambda c: (c['untagged'], c['name'])):
                product_lines = []
                for p in sorted(cat['products'].values(), key=lambda x: x['product'].name):
                    p['price_unit'] = (p['amount'] / p['qty']) if p['qty'] else 0.0
                    product_lines.append(p)
                cat['lines'] = product_lines
                cat['percent'] = (cat['total'] / proj_data['total'] * 100.0) if proj_data['total'] else 0.0
                categories.append(cat)
            final.append({
                'project': proj_data['project'],
                'categories': categories,
                'total': proj_data['total'],
            })

        return final

    def get_tag_summary(self, data):
        """Totals per category across all projects (for the general recap)."""
        summary = {}
        for proj in data:
            for cat in proj['categories']:
                entry = summary.setdefault(cat['name'], {
                    'name': cat['name'], 'untagged': cat['untagged'], 'total': 0.0,
                })
                entry['total'] += cat['total']
        grand_total = sum(p['total'] for p in data)
        res = sorted(summary.values(), key=lambda c: (c['untagged'], c['name']))
        for entry in res:
            entry['percent'] = (entry['total'] / grand_total * 100.0) if grand_total else 0.0
        return res

    def get_currency(self):
        return self.env.company.currency_id

    def action_preview(self):
        action = self.env.ref(
            'adi_project_cost_analysis_tag.action_report_project_cost_analysis_tag'
        ).report_action(self)
        action['report_type'] = 'qweb-html'
        return action

    def action_print(self):
        return self.env.ref(
            'adi_project_cost_analysis_tag.action_report_project_cost_analysis_tag'
        ).report_action(self)
