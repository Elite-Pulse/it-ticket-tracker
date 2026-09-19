# -*- coding: utf-8 -*-
import base64
import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ItTicketMailSchedule(models.Model):
    _name = "it.ticket.mail.schedule"
    _description = "IT Ticket Auto-Mailing Schedule"

    name = fields.Char(required=True, default="IT Ticket Report Mailing")
    active = fields.Boolean(default=True, string="Enabled")

    partner_ids = fields.Many2many(
        "res.partner", "it_ticket_mail_schedule_to_rel", "schedule_id", "partner_id",
        string="Send To", help="Pick existing contacts/users, or type an email address and choose 'Create ...'.",
    )
    partner_cc_ids = fields.Many2many(
        "res.partner", "it_ticket_mail_schedule_cc_rel", "schedule_id", "partner_id", string="CC",
    )
    subject = fields.Char(default="IT Ticket Report", required=True)

    # Admin can tick more than one - each fires on its own cycle.
    send_daily = fields.Boolean(string="Every day")
    send_weekly = fields.Boolean(string="Every week")
    send_biweekly = fields.Boolean(string="Every 2 weeks")
    send_monthly = fields.Boolean(string="Every month")
    send_yearly = fields.Boolean(string="Every year")

    stage_ids = fields.Many2many(
        "it.ticket.stage", string="Ticket Status",
        help="Leave empty for every status (Open, In Progress, Pending, Resolved, Closed).",
    )
    assigned_to_ids = fields.Many2many(
        "res.users", string="Employees",
        help="Leave empty to include every employee's tickets.",
    )

    last_run_daily = fields.Datetime(readonly=True)
    last_run_weekly = fields.Datetime(readonly=True)
    last_run_biweekly = fields.Datetime(readonly=True)
    last_run_monthly = fields.Datetime(readonly=True)
    last_run_yearly = fields.Datetime(readonly=True)

    log_ids = fields.One2many("it.ticket.mail.log", "schedule_id", string="History")
    log_count = fields.Integer(compute="_compute_log_count")

    def _compute_log_count(self):
        for rec in self:
            rec.log_count = len(rec.log_ids)

    def action_view_logs(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "History - %s" % self.name,
            "res_model": "it.ticket.mail.log",
            "view_mode": "list,form",
            "domain": [("schedule_id", "=", self.id)],
        }

    def _get_domain(self):
        self.ensure_one()
        domain = []
        if self.stage_ids:
            domain.append(("stage_id", "in", self.stage_ids.ids))
        if self.assigned_to_ids:
            domain.append(("assigned_to", "in", self.assigned_to_ids.ids))
        return domain

    def action_send_now(self):
        """Manual 'send now' button - runs the same code path as the cron,
        logged as 'manual' in the history."""
        for rec in self:
            rec._send_report("manual")
        return True

    def _send_report(self, frequency):
        self.ensure_one()
        Log = self.env["it.ticket.mail.log"].sudo()
        tickets = self.env["it.ticket"].sudo().search(self._get_domain())

        if not tickets:
            Log.create({
                "schedule_id": self.id, "run_date": fields.Datetime.now(),
                "frequency": frequency, "ticket_count": 0,
                "success": True, "note": "No matching tickets - nothing sent.",
            })
            return

        if not self.partner_ids:
            Log.create({
                "schedule_id": self.id, "run_date": fields.Datetime.now(),
                "frequency": frequency, "ticket_count": len(tickets),
                "success": False, "note": "No recipient configured (Send To is empty).",
            })
            return

        try:
            xlsx_name, xlsx_data = tickets._build_xlsx_file()
            pdf_content, _fmt = self.env["ir.actions.report"].sudo()._render_qweb_pdf(
                "it_ticket_tracker.action_report_it_ticket", tickets.ids
            )
            pdf_name = "IT_Ticket_Report_%s.pdf" % fields.Date.context_today(self)

            attachments = self.env["ir.attachment"].sudo().create([
                {
                    "name": xlsx_name, "type": "binary",
                    "datas": base64.b64encode(xlsx_data),
                    "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                },
                {
                    "name": pdf_name, "type": "binary",
                    "datas": base64.b64encode(pdf_content),
                    "mimetype": "application/pdf",
                },
            ])

            mail = self.env["mail.mail"].sudo().create({
                "subject": self.subject or "IT Ticket Report",
                "recipient_ids": [(6, 0, self.partner_ids.ids)],
                "email_cc": ",".join(self.partner_cc_ids.mapped("email")) if self.partner_cc_ids else False,
                "body_html": "<p>Please find attached the IT Ticket report (%s ticket(s)), in both PDF and Excel.</p>" % len(tickets),
                "attachment_ids": [(6, 0, attachments.ids)],
                "auto_delete": False,
            })
            mail.send()

            Log.create({
                "schedule_id": self.id, "run_date": fields.Datetime.now(),
                "frequency": frequency, "ticket_count": len(tickets),
                "success": True, "note": "Sent to %s recipient(s)." % len(self.partner_ids),
            })
        except Exception as exc:  # noqa: BLE001 - logged into history, never silently lost
            _logger.exception("IT Ticket auto-mailing failed for schedule %s", self.id)
            Log.create({
                "schedule_id": self.id, "run_date": fields.Datetime.now(),
                "frequency": frequency, "ticket_count": len(tickets),
                "success": False, "note": str(exc)[:500],
            })

    @api.model
    def _cron_send_scheduled_reports(self):
        now = fields.Datetime.now()
        for sched in self.search([("active", "=", True)]):
            if sched.send_daily and (not sched.last_run_daily or (now - sched.last_run_daily).total_seconds() >= 23 * 3600):
                sched._send_report("daily")
                sched.last_run_daily = now
            if sched.send_weekly and (not sched.last_run_weekly or (now - sched.last_run_weekly).days >= 7):
                sched._send_report("weekly")
                sched.last_run_weekly = now
            if sched.send_biweekly and (not sched.last_run_biweekly or (now - sched.last_run_biweekly).days >= 14):
                sched._send_report("biweekly")
                sched.last_run_biweekly = now
            if sched.send_monthly and (not sched.last_run_monthly or (now - sched.last_run_monthly).days >= 28):
                sched._send_report("monthly")
                sched.last_run_monthly = now
            if sched.send_yearly and (not sched.last_run_yearly or (now - sched.last_run_yearly).days >= 365):
                sched._send_report("yearly")
                sched.last_run_yearly = now


class ItTicketMailLog(models.Model):
    _name = "it.ticket.mail.log"
    _description = "IT Ticket Auto-Mailing History"
    _order = "run_date desc"

    schedule_id = fields.Many2one("it.ticket.mail.schedule", string="Schedule", ondelete="cascade")
    run_date = fields.Datetime(required=True)
    frequency = fields.Selection(
        [("daily", "Daily"), ("weekly", "Weekly"), ("biweekly", "Every 2 weeks"),
         ("monthly", "Monthly"), ("yearly", "Yearly"), ("manual", "Manual")],
    )
    ticket_count = fields.Integer(string="Tickets Included")
    success = fields.Boolean(string="Sent OK")
    note = fields.Char()
