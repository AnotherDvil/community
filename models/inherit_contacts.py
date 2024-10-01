# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Contacts(models.Model):
    _inherit = 'res.partner'

    password = fields.Char(string='Contraseña')
    token = fields.Char(string='Token de seguridad')
    archived = fields.Boolean('¿Se dió de baja?', tracking=True)
    job = fields.Selection([
        ('user', 'Usuario'),
        ('employee', 'Empleado'),
        ('owner', 'Dueño')
    ], string='Tipo de usuario')
    
    
    service_id_e = fields.Many2one('services', string='Servicio inscrito')
    service_id_f = fields.Many2one('services', string="Servicio")