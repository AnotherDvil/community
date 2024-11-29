# -*- coding: utf-8 -*-
import logging
import re
import random
import string
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class services(models.Model):
    _name = 'services'
    _description = 'Modelo desarrollado para los servicios que habrá en la app'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Heredamos estos módulos para tener una tabla de seguimiento
    
    name = fields.Char('Nombre del negocio')
    owner = fields.Many2one('res.partner', 'Dueño')
    image = fields.Image('Perfil', attachment=True, max_width=1024, max_height=1024, store=True)
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

    empleados = fields.Many2many(
        'res.partner',                # Modelo relacionado
        'service_employee_rel',       # Nombre de la tabla de relación para "employees"
        'service_id',                 # Columna que hace referencia a este modelo (`services`)
        'partner_id',                 # Columna que hace referencia a `res.partner`
        string="Empleados"            # Etiqueta del campo
    )
    
    reviews = fields.One2many('reviews', 'service_id', string='Reseñas')
    proposals = fields.One2many('proposals', 'service_id', string="Propuestas")

    # Lista de malas palabras a censurar
    BAD_WORDS = [
        "pendejo", "pendeja", "cabron", "cabrona", "chingón", "chingona", "chingar", "chingada", 
        "chingado", "puto", "puta", "joto", "marica", "maricón", "mamón", "mamona", "culero", 
        "culera", "pinche", "guey", "wey", "zorra", "perra", "baboso", "babosa", "pito", "verga", 
        "menso", "culito", "madrazo", "chingadera", "chingadazo", "chingas", "chingaste", 
        "hijo de la chingada", "chingón", "chingona", "tarado", "estúpido", "idiota", "mugroso", 
        "mugrosa", "güey", "huevón", "guevón", "jodido", "mierda", "cacas", "nalga", "nalgotas", 
        "nalguitas", "prieto", "prieta", "nalgón", "gorda", "huevudo", "zorrón", "lagartona", "burra",
        "burro", "cochina", "metiche", "manchado", "chafa", "corriente", "piruja", "pirujita", "argüendero", 
        "chismoso", "chismosa", "vago", "rata", "mamonazo", "pelón", "menso", "mensote", "apestoso", "pata rajada", 
        "marrano", "zoquete", "imbécil", "ocicón", "mamilas", "chango", "meco", "no mames", "a huevo", "qué pedo",
        "pinche güey", "pinche vieja", "chingas a tu madre", "hijo de puta", "baboso", "pinche pendejo", "chingado güey", 
        "culero", "culera", "chingaquedito", "chale", "vato", "pinche vato", "pinche cabrón", "pinche joto"
    ]

    @api.model
    def create(self, vals):
        if 'description' in vals:
            vals['description'] = self.censor_bad_words(vals['description'])
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
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

    def write(self, vals):
        if 'description' in vals:
            vals['description'] = self.censor_bad_words(vals['description'])
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(services, self).write(vals)

    def censor_bad_words(self, text):
        for bad_word in self.BAD_WORDS:
            regex = re.compile(re.escape(bad_word), re.IGNORECASE)
            replacement = bad_word[0] + '*' * (len(bad_word) - 2) + bad_word[-1]
            text = regex.sub(replacement, text)
        return text

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