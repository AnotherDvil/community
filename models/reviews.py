# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
    
    #Al momento de crear un registro se llenará el campo written_by con el nombre del usuario actual
    @api.model
    def create(self, vals):
        # Obtener el usuario actual
        user = self.env.user
        # Obtener el empleado correspondiente al usuario actual
        employee = self.env['res.partner'].search([('user_id', '=', user.id)], limit=1)
        # Establecer el campo written_by con el empleado correspondiente
        vals['written_by'] = employee.id if employee else False
        return super(reviews, self).create(vals)