# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import ValidationError


class AttendanceDaily(models.Model):
    """Modèle principal pour la gestion quotidienne des pointages"""
    _name = 'attendance.daily'
    _description = 'Pointage Quotidien'
    _order = 'date desc'
    _rec_name = 'date'

    # Champs principaux
    date = fields.Date(
        string='Date du pointage',
        required=True,
        default=fields.Date.today
    )

    # Sélection des employés
    selection_type = fields.Selection([
        ('all', 'Tous les employés'),
        ('department', 'Par département')
    ], string='Type de sélection', default='all', required=True)

    department_ids = fields.Many2many(
        'hr.department',
        string='Départements'
    )

    attendance_line_ids = fields.One2many(
        'attendance.daily.line',
        'attendance_id',
        string='Lignes de pointage'
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('processed', 'Traité')
    ], string='État', default='draft')

    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )

    @api.onchange('selection_type', 'department_ids')
    def _onchange_selection(self):
        """Génère automatiquement les lignes selon la sélection"""
        if not self.date:
            return

        # Récupérer les employés déjà présents pour éviter les doublons
        existing_employee_ids = self.attendance_line_ids.mapped('employee_id.id')

        # Récupérer les employés selon la sélection
        domain = [('contract_ids.state', '=', 'open')]
        if self.selection_type == 'department' and self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        employees = self.env['hr.employee'].search(domain)

        # Préparer les commandes pour mettre à jour les lignes
        commands = []

        # Garder les lignes existantes
        for line in self.attendance_line_ids:
            commands.append((4, line.id, 0))

        # Ajouter les nouvelles lignes pour les employés non présents
        for employee in employees:
            if employee.id not in existing_employee_ids:
                commands.append((0, 0, {
                    'employee_id': employee.id,
                    'is_present': True,
                    'standard_hours': 8.0,
                }))

        # Appliquer toutes les commandes
        if commands:
            self.attendance_line_ids = commands

    def action_print_sheet(self):
        """Imprime la feuille de présence"""
        self.ensure_one()
        return self.env.ref('adi_simple_attendance.action_report_attendance_sheet').report_action(self)

    def action_generate_lines(self):
        """Bouton pour régénérer toutes les lignes"""
        self.ensure_one()

        # Supprimer toutes les lignes existantes
        self.attendance_line_ids.unlink()

        # Récupérer les employés selon la sélection
        domain = [('contract_ids.state', '=', 'open')]
        if self.selection_type == 'department' and self.department_ids:
            domain.append(('department_id', 'in', self.department_ids.ids))

        employees = self.env['hr.employee'].search(domain)

        # Créer une ligne pour chaque employé
        for employee in employees:
            self.env['attendance.daily.line'].create({
                'attendance_id': self.id,
                'employee_id': employee.id,
                'is_present': True,
                'standard_hours': 8.0,
            })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Succès',
                'message': f'{len(employees)} lignes créées',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_confirm(self):
        """Confirme le pointage du jour"""
        self.ensure_one()
        if not self.attendance_line_ids:
            raise ValidationError("Aucune ligne de pointage à confirmer!")
        self.state = 'confirmed'

    def action_process(self):
        """Marque le pointage comme traité (utilisé dans la paie)"""
        self.ensure_one()
        self.state = 'processed'
        # Marquer toutes les lignes comme traitées
        self.attendance_line_ids.write({'is_processed': True})

    def unlink(self):
        """Empêche la suppression des pointages confirmés"""
        for record in self:
            if record.state != 'draft':
                raise ValidationError("Impossible de supprimer un pointage confirmé!")
        return super(AttendanceDaily, self).unlink()


class AttendanceDailyLine(models.Model):
    """Lignes de détail pour chaque employé"""
    _name = 'attendance.daily.line'
    _description = 'Ligne de pointage'
    _rec_name = 'employee_id'

    attendance_id = fields.Many2one(
        'attendance.daily',
        string='Pointage',
        required=True,
        ondelete='cascade'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True
    )

    # Informations employé (champs liés pour affichage)
    employee_name = fields.Char(
        related='employee_id.name',
        string='Nom et Prénom',
        readonly=True,
        store=True  # Stocker pour améliorer les performances
    )

    job_id = fields.Many2one(
        related='employee_id.job_id',
        string='Poste',
        readonly=True,
        store=True
    )

    department_id = fields.Many2one(
        related='employee_id.department_id',
        string='Département',
        readonly=True,
        store=True
    )

    # Statut de présence
    is_present = fields.Boolean(
        string='Présent',
        default=True
    )

    is_absent = fields.Boolean(
        string='Absent',
        default=False
    )

    # Heures
    standard_hours = fields.Float(
        string='Heures standard',
        default=8.0,
        help="Heures de présence normale (par défaut 8h)"
    )

    actual_hours = fields.Float(
        string='Heures de présence',
        help="Heures réelles en cas de présence partielle"
    )

    overtime_hours = fields.Float(
        string='Heures supplémentaires',
        default=0.0
    )

    # État
    is_processed = fields.Boolean(
        string='Traité',
        default=False,
        help="Indique si cette ligne a été utilisée dans une paie"
    )

    company_id = fields.Many2one(
        related='attendance_id.company_id',
        store=True
    )

    @api.onchange('is_present')
    def _onchange_is_present(self):
        """Gère la logique présent/absent"""
        if self.is_present:
            self.is_absent = False
            if not self.standard_hours:
                self.standard_hours = 8.0
        else:
            self.actual_hours = 0.0
            self.overtime_hours = 0.0

    @api.onchange('is_absent')
    def _onchange_is_absent(self):
        """Gère la logique absent/présent"""
        if self.is_absent:
            self.is_present = False
            self.standard_hours = 0.0
            self.actual_hours = 0.0
            self.overtime_hours = 0.0

    @api.constrains('employee_id', 'attendance_id')
    def _check_unique_employee(self):
        """Vérifie qu'un employé n'apparaît qu'une fois par pointage"""
        for record in self:
            if not record.employee_id:
                continue
            duplicate = self.search([
                ('attendance_id', '=', record.attendance_id.id),
                ('employee_id', '=', record.employee_id.id),
                ('id', '!=', record.id)
            ])
            if duplicate:
                raise ValidationError(
                    f"L'employé {record.employee_name} est déjà dans la liste!"
                )

    def get_total_hours(self):
        """Calcule le total des heures pour la ligne"""
        self.ensure_one()
        if self.is_absent:
            return 0.0
        elif self.actual_hours > 0:
            return self.actual_hours + self.overtime_hours
        else:
            return self.standard_hours + self.overtime_hours
