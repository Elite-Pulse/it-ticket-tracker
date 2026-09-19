# -*- coding: utf-8 -*-
from datetime import datetime, time

from odoo import api, fields, models
from odoo.exceptions import UserError


class ItTicketReportWizard(models.TransientModel):
    _name = "it.ticket.report.wizard"
    _description = "IT Ticket Report Wizard"

    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    assigned_to_ids = fields.Many2many("res.users", string="Assigned To", help="Leave empty for everyone you can see.")
    stage_ids = fields.Many2many(
        "it.ticket.stage", string="Stage",
        help="Leave empty for All stages. Pick one or more (Open, In Progress, Pending, Resolved, Closed...).",
    )
    # Controls which button(s) this dialog shows - set via the menu action's context.
    report_mode = fields.Selection(
        [("pdf", "PDF"), ("excel", "Excel"), ("both", "Both")], default="both",
    )
    # "Own Tickets" users can only ever export their own data anyway (record
    # rules enforce that regardless of this filter) - hide the Assigned To
    # control for them so the dialog doesn't misleadingly suggest they can
    # pick someone else's tickets.
    can_filter_others = fields.Boolean(compute="_compute_can_filter_others")

    def _compute_can_filter_others(self):
        is_privileged = self.env.user.has_group("it_ticket_tracker.group_ticket_all") or \
            self.env.user.has_group("it_ticket_tracker.group_ticket_admin")
        for rec in self:
            rec.can_filter_others = is_privileged

    def _get_domain(self):
        domain = []
        if self.date_from:
            domain.append(("date_opened", ">=", datetime.combine(self.date_from, time.min)))
        if self.date_to:
            domain.append(("date_opened", "<=", datetime.combine(self.date_to, time.max)))
        if self.can_filter_others and self.assigned_to_ids:
            domain.append(("assigned_to", "in", self.assigned_to_ids.ids))
        if self.stage_ids:
            domain.append(("stage_id", "in", self.stage_ids.ids))
        return domain

    def _get_tickets(self):
        tickets = self.env["it.ticket"].search(self._get_domain())
        if not tickets:
            raise UserError("No tickets match these filters. Widen the date range or status.")
        return tickets

    def action_generate_pdf(self):
        tickets = self._get_tickets()
        return self.env.ref("it_ticket_tracker.action_report_it_ticket").report_action(tickets)

    def action_generate_excel(self):
        tickets = self._get_tickets()
        return tickets.action_export_xlsx()
