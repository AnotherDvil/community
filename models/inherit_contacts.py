# -*- coding: utf-8 -*-
from odoo import models, fields, api
import secrets
import logging
_logger = logging.getLogger(__name__)

class Contacts(models.Model):
    _inherit = 'res.partner'

    password = fields.Char(string='Contraseña')
    token = fields.Char(string='Token de seguridad')
    archived = fields.Boolean('¿Se dió de baja?', tracking=True)
    job = fields.Selection([
        ('user', 'Usuario'),
        ('employee', 'Empleado'),
        ('owner', 'Dueño')
    ], string='Tipo de usuario', default="user")

    #Empleado
    service_id_e = fields.Many2one('services', string='Servicio empleado')
    service_id_f = fields.Many2one('services', string='Servicio inscrito')


    #Seguidores
    followed_services = fields.Many2many(
        'services',
        'service_partner_rel',
        'partner_id',
        'service_id',
        string="Servicios Seguidos"
    )

    #Propietario del servicio
    service_owner = fields.Many2one('services', string='Servicio del dueño', compute='get_owner')

    @api.model
    def create(self, vals):
        record = super(Contacts, self).create(vals)

        token = secrets.token_urlsafe(20)
        record.token = token

        return record

    def get_owner(self):
        for record in self:
            try:
                # Buscar el servicio en base al dueño
                services = self.env['services'].search([('owner', '=', record.id)], limit=1)

                if services:
                    record.service_owner = services.id  # Asigna el servicio al campo 'service_owner'
                    record.job = 'owner'  # Cambia el tipo de usuario a 'Dueño'
                else:
                    # Si no se encuentra un servicio, asigna False
                    record.service_owner = ''
                    record.job = 'user'  # Restablece el tipo de usuario a 'Usuario'
            except Exception as e:
                # Manejo de errores para evitar que el sistema falle
                _logger.error(f"Error al calcular el servicio del dueño para el contacto {record.id}: {str(e)}")
                record.service_owner = ''  # Asigna False si ocurre un error