{
    'name': 'Beauty Spa Management',
    'version': '19.0.1.1.0',
    'category': 'Services/Spa',
    'summary': 'Appointments, therapists, packages & invoicing for beauty spas',
    'description': """
Beauty Spa Management
======================
Complete salon & spa management for Odoo 19:

- Appointment calendar (drag-and-drop, colour-coded by therapist)
- Services catalogue with categories and duration/price
- Therapist profiles with specialisations
- Treatment rooms management
- Packages (bundles of services at a special price)
- One-click invoice generation from any appointment
- PDF appointment confirmation & receipt
- Kanban board by appointment status
- Demo data included

Contact & Support:
------------------
- Email: abdzoro89@gmail.com / a.osman@bab.com.sa
- Phone: +966562984106 / +966553368212
    """,
    'author': 'Abdulkrim Osman (+966562984106, +966553368212)',
    'website': 'https://apps.odoo.com',
    'support': 'abdzoro89@gmail.com',
    'maintainer': 'a.osman@bab.com.sa',
    'depends': ['base', 'mail', 'account'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'data/cleanup.xml',
        'data/ir_sequence.xml',
        'views/spa_service_category_views.xml',
        'views/spa_service_views.xml',
        'views/spa_therapist_views.xml',
        'views/spa_room_views.xml',
        'views/spa_package_views.xml',
        'views/spa_appointment_views.xml',
        'report/spa_appointment_report.xml',
        'report/spa_appointment_template.xml',
        'views/menu_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'price': 0.0,
    'currency': 'EUR',
    'images': ['static/description/banner.svg', 'static/description/icon.png'],
}
