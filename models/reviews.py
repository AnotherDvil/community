# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class reviews(models.Model):
    _name = 'reviews'
    _description = 'Modelo desarrollado para las reseñas que tendrá cáda negocio'
    
    name = fields.Char("Titulo")
    description = fields.Char("Descripción")
    rating = fields.Selection([
        ('0', '0 Stars'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars')
    ], string="Calificación")
    written_by = fields.Many2one('res.partner', string="Redactado por", readonly=True)
    service_id = fields.Many2one('services', 'Servicios')
    
    @api.model
    def create(self, vals):
        # Obtener el usuario actual
        user = self.env.user
        _logger.info(f"Usuario actual: {user.name} (ID: {user.id})")
        
        # Obtener el empleado correspondiente al usuario actual
        employee = self.env['res.partner'].search([('user_id', '=', user.id)], limit=1)
        _logger.info(f"Empleado encontrado: {employee.name if employee else 'No encontrado'} (ID: {employee.id if employee else 'N/A'})")
        
        # Establecer el campo written_by con el empleado correspondiente
        if employee:
            vals['written_by'] = employee.id
        else:
            _logger.warning(f"No se encontró un res.partner para el usuario {user.name} (ID: {user.id})")
        
        return super(reviews, self).create(vals)