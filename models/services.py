# -*- coding: utf-8 -*-

import random
import string
from odoo import models, fields, api

class services(models.Model):
    _name = 'services'
    _description = 'Modelo desarrollado para los servicios que habrá en la app'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Heredamos estos módulos para tener una tabla de seguimiento
    
    name = fields.Char('Nombre del negocio')
    owner = fields.Many2one('res.partner', 'Dueño')
    image = fields.Binary('Perfil')
    direction = fields.Char('Dirección', tracking=True)
    number_phone = fields.Char('Teléfono', tracking=True)
    email = fields.Char('Correo electrónico', tracking=True)
    bank_account_id = fields.Many2one('res.partner.bank', 'Método de pago', tracking=True)
    archived = fields.Boolean('¿Se dió de baja?', tracking=True)
    qualification = fields.Float('Calificación', tracking=True)
    access_code = fields.Char('Código de acceso', tracking=True, readonly=True)
    description = fields.Char('Descripción', tracking=True)
    category = fields.Selection([
        ('art', 'Arte'),
        ('tech', 'Tecnología'),
        ('health', 'Salud'),
        ('education', 'Educación'),
        ('retail', 'Comercio minorista'),
        ('hospitality', 'Hostelería y Turismo'),
        ('finance', 'Finanzas y Seguros'),
        ('construction', 'Construcción e Ingeniería'),
        ('entertainment', 'Medios y Entretenimiento'),
        ('logistics', 'Logística y Transporte'),
        ('food', 'Comida'),
        ('mode', 'Moda'),
        ('personal_services', 'Servicios personales'),
        ('creative_services', 'Servicios creativos'),
        ('maintenance', 'Servicios de mantenimiento'),
    ], string='Categoría', tracking=True)
    
    #Conexión con otros modelos
    novedades = fields.One2many('news', 'service_id', string="Novedades")
    rewards = fields.One2many('rewards', 'service_id', string="Recompensas")

    followers = fields.Many2many(
        'res.partner',                # Modelo relacionado
        'service_partner_rel',         # Nombre de la tabla de relación
        'service_id',                  # Columna que hace referencia a este modelo (`services`)
        'partner_id',                  # Columna que hace referencia a `res.partner`
        string="Seguidores"            # Etiqueta del campo
    )

    empleados = fields.One2many(
        'res.partner',
        'service_id_e',
        string="Empleados"
    )
    
    reviews = fields.One2many('reviews', 'service_id', string='Reseñas')
    proposals = fields.One2many('proposals', 'service_id', string="Propuestas")

    @api.model
    def create(self, vals):
        # Generar access_code automáticamente si no se ha proporcionado
        if 'access_code' not in vals or not vals['access_code']:
            vals['access_code'] = self.generate_access_code()
        # Crear el servicio utilizando el método original con los valores actualizados
        record = super(services, self).create(vals)
        # Actualizar el campo 'service_owner' en el modelo 'res.partner' si hay un dueño
        if record.owner:
            partner = self.env['res.partner'].browse(record.owner.id)
            partner.get_owner()  # Llama a la función get_owner para actualizar el campo 'service_owner'
        return record

    def generate_access_code(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(6))

    @api.model
    def _cron_scheduled_generate_access_code(self):
        services = self.search([])
        for service in services:
            service.access_code = self.generate_access_code()

    @api.depends('reviews.rating')
    @api.onchange('reviews')
    def get_average(self):
        for record in self:
            ratings = record.reviews.mapped('rating')
            if ratings:
                record.qualification = sum(ratings) / len(ratings)
            else:
                record.qualification = 0.0