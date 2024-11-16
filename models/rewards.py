# -*- coding: utf-8 -*-

from odoo import models, fields, api

class rewards(models.Model):
    _name = 'rewards'
    _description = 'Recompensas de algún negocio'
    
    name = fields.Char('Nombre')
    description = fields.Char('Descripción de la recompensa')
    points_required = fields.Integer('Puntos requeridos')
    active = fields.Boolean('Está activo?')
    image = fields.Binary('Imagen recompensa', readonly=False)
    
    service_id = fields.Many2one('services', 'Servicios')