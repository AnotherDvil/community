# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import re

_logger = logging.getLogger(__name__)

class reviews(models.Model):
    _name = 'reviews'
    _description = 'Modelo desarrollado para las reseñas que tendrá cáda negocio'
    
    name = fields.Char("Titulo")
    description = fields.Char("Descripción")
    rating = fields.Float("Calificación")
    """ rating = fields.Selection([
        ('0', '0 Stars'),
        ('1', '1 Star'),
        ('2', '2 Stars'),
        ('3', '3 Stars')
    ], string="Calificación") """
    written_by = fields.Many2one('res.partner', string="Redactado por")
    service_id = fields.Many2one('services', 'Servicios')

    """ @api.model
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
        
        return super(reviews, self).create(vals) """

        # Lista de malas palabras a censurar
    BAD_WORDS = ["tetas", "culo", "pito"]

    def censor_bad_words(self, text):
        for bad_word in self.BAD_WORDS:
            # Usar regex para reemplazar cada mala palabra con asteriscos
            regex = re.compile(re.escape(bad_word), re.IGNORECASE)
            replacement = bad_word[0] + '*' * (len(bad_word) - 2) + bad_word[-1]
            text = regex.sub(replacement, text)
        return text

    @api.model
    def create(self, vals):
        if 'description' in vals:
            vals['description'] = self.censor_bad_words(vals['description'])
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(reviews, self).create(vals)

    def write(self, vals):
        if 'description' in vals:
            vals['description'] = self.censor_bad_words(vals['description'])
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(reviews, self).write(vals)