# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ItTicketStage(models.Model):
    """Replaces the old fixed 'Status' selection. Admin can add, rename,
    reorder (drag & drop) and delete stages from Configuration, or directly
    in the Kanban board - exactly like Project Task Stages."""

    _name = "it.ticket.stage"
    _description = "IT Ticket Stage"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    fold = fields.Boolean(
        string="Folded in Kanban",
        help="This stage is folded (collapsed) by default in the Kanban board.",
    )
    is_closed = fields.Boolean(
        string="Closing Stage",
        help="Tickets reaching this stage are considered closed: a Date Closed is "
        "required and the ticket counts as resolved in reports.",
    )
    color = fields.Integer(string="Color", default=0)

    _sql_constraints = [
        ("name_unique", "unique(name)", "A stage with this name already exists."),
    ]


class ItTicketType(models.Model):
    """Replaces the old fixed 'Type' selection (Incident / Demande)."""

    _name = "it.ticket.type"
    _description = "IT Ticket Type"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string="Color", default=1)

    _sql_constraints = [
        ("name_unique", "unique(name)", "A ticket type with this name already exists."),
    ]


class ItTicketCategory(models.Model):
    """Replaces the old fixed 'Category' selection (Network / Server / ...)."""

    _name = "it.ticket.category"
    _description = "IT Ticket Category"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string="Color", default=4)

    _sql_constraints = [
        ("name_unique", "unique(name)", "A category with this name already exists."),
    ]


class ItTicketPriority(models.Model):
    """Replaces the old fixed 'Priority' selection (Critical/High/Medium/Low).
    'sequence' controls display/sort order, 'color' controls the Kanban card
    color band (standard Odoo 0-11 palette index)."""

    _name = "it.ticket.priority"
    _description = "IT Ticket Priority"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    color = fields.Integer(string="Color", default=1)

    _sql_constraints = [
        ("name_unique", "unique(name)", "A priority with this name already exists."),
    ]


class ItTicketReporter(models.Model):
    """Directory of 'Reported By' people/teams, local to this module only -
    deliberately NOT hr.employee or res.partner, so it never touches HR/CRM
    data. Any ticket user can quick-create a new entry by typing a name that
    doesn't exist yet; it is then remembered for future tickets. Only Admin
    can rename or delete existing entries (Configuration menu)."""

    _name = "it.ticket.reporter"
    _description = "IT Ticket Reporter/Requester"
    _order = "name"

    name = fields.Char(required=True)

    _sql_constraints = [
        ("name_unique", "unique(name)", "This reporter/requester name is already in the list."),
    ]

    @api.model
    def action_import_users(self):
        """Fast-integration helper: copy every active internal Odoo User's
        name into this directory in one click, so 'Reported By' can be
        picked exactly like 'Assigned To' from day one. One-time bulk copy
        only - it does not keep syncing afterwards, and it never touches
        hr.employee or res.partner."""
        existing_names = set(self.search([]).mapped("name"))
        users = self.env["res.users"].sudo().search([("share", "=", False), ("active", "=", True)])
        to_create = []
        for user in users:
            if user.name and user.name not in existing_names:
                to_create.append({"name": user.name})
                existing_names.add(user.name)
        created = self.create(to_create) if to_create else self.browse()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Reporters imported",
                "message": "%s user(s) added to the Reported By list." % len(created)
                if created else "Every active user is already in the list.",
                "type": "success",
                "sticky": False,
            },
        }
