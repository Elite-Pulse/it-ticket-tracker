{
    "name": "IT Ticket Tracker",
    "version": "18.0.1.0.0",
    "category": "Services/Helpdesk",
    "summary": "Track, resolve and report on IT support tickets, with configurable stages, automated reporting and email delivery",
    "description": """
IT Ticket Tracker
=================

A lightweight IT ticket management application for Odoo 18 Community.

IT Ticket Tracker helps IT teams register, manage, track and report
incidents and service requests from a centralized interface.

Key Features
------------

* Configurable ticket stages
* Configurable ticket types and categories
* Configurable priorities
* Configurable reporters
* Kanban board with drag-and-drop workflow
* Priority and category tags
* Favorites for frequently accessed tickets
* Automatic resolution-time calculation
* ISO week number tracking
* Access control with three levels:
  - Own Tickets
  - All Tickets
  - Administrator
* PDF ticket reports
* Excel ticket reports
* Report filtering by date, status and employee
* Automatic scheduled report delivery by email
* Daily, weekly, bi-weekly, monthly and yearly schedules
* Complete report delivery history
* No external services required

Designed for IT departments and technical support teams
that need a simple and configurable ticket tracking solution.

Developed by Abdechakour Hrouchan.
""",
    "author": "Abdechakour Hrouchan",
    "website": "https://www.misterinfo.ma",
    "license": "LGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ticket_security.xml",
        "security/ir.model.access.csv",
        "data/it_ticket_sequence.xml",
        "data/it_ticket_master_data.xml",
        "data/it_ticket_mail_cron.xml",
        "views/it_ticket_views.xml",
        "views/it_ticket_config_views.xml",
        "views/it_ticket_report_wizard_views.xml",
        "views/it_ticket_mail_schedule_views.xml",
        "views/it_ticket_menus.xml",
        "views/report_it_ticket.xml",
    ],
    "application": True,
    "installable": True,
    "post_init_hook": "post_init_hook",
}
