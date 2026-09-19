from . import models


def post_init_hook(env):
    """One-time, at install: copy every active internal User's name into the
    'Reported By' directory, so it works like 'Assigned To' from day one
    ("fast integration"). Never touches hr.employee/res.partner, and does
    not keep re-syncing afterwards - Admin can re-run this any time from
    Configuration > Reporters / Requesters > Import current Users."""
    env["it.ticket.reporter"].action_import_users()
