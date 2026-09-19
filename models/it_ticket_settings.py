# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ItTicketSettings(models.Model):
    """A single-record settings model, deliberately NOT res.config.settings,
    so access is governed purely by our own group_ticket_admin and doesn't
    require Odoo's base 'Settings/Administration' system group."""

    _name = "it.ticket.settings"
    _description = "IT Ticket Tracker Settings"

    auto_generate_id = fields.Boolean(
        string="Auto-generate Ticket ID",
        help="When enabled, leaving the Ticket ID blank on a new ticket generates one "
        "automatically (e.g. TCK-000123). When disabled (default, matches the normal process), "
        "the Ticket ID must be pasted in manually from the external ticketing tool.",
    )
    id_prefix = fields.Char(string="Ticket ID Prefix", default="TCK-")

    @api.model
    def get_singleton(self):
        record = self.search([], limit=1)
        if not record:
            record = self.create({})
        return record
