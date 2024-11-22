# -*- coding: utf-8 -*-
{
    'name': "community",
    'summary': "Desarrollo por el equipo Nexus Technologies",
    'description': """
        Community surge en respuesta a la necesidad de mejorar la experiencia del cliente y 
        fortalecer la relación entre las empresas y su comunidad de usuarios. En muchos casos, 
        la interacción entre clientes y negocio  se limita a transacciones comerciales, con una 
        falta de participación activa por parte de los clientes en la mejora de los servicios 
        ofrecidos. Para abordar esta brecha, se propone desarrollar una aplicación integral de 
        servicio al cliente que fomente una mayor participación e interacción entre ambas partes.
        Sin embargo, para lograr este objetivo, es crucial enfrentar una serie de desafíos. 
        Entre ellos se encuentran garantizar la accesibilidad de la aplicación para todos los 
        usuarios, establecer canales de comunicación efectivos entre clientes y empresas, y 
        promover una cultura de participación activa y retroalimentación constructiva por 
        parte de la comunidad de usuarios. Al superar estos desafíos, se espera crear una 
        plataforma que no solo mejore la calidad de los servicios ofrecidos, sino que también 
        fortalezca la relación entre las empresas y su comunidad, generando un mayor sentido 
        de pertenencia y compromiso por parte de los clientes.
    """,
    'author': "Nexus Technologies",
    'category': 'Services',
    'version': '1.6',
    'depends': [
        'base',
        'mail',
        'contacts'
    ],
    # always loaded
    'data': [
        'views/view_res_partner.xml',
        'views/menu_view.xml',
        'views/view_services.xml',
        'views/proposals_view.xml',
        'security/community_security.xml',
        'security/ir.model.access.csv',
        'data/obtain_results_prop.xml',
        'data/reset_moneda.xml',
        'data/change_phase.xml'
    ]
}