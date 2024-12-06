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
    entregada = fields.Boolean(string="Entregada (Global)", default=False)  # Opcional
    reward_user_rel_ids = fields.One2many('reward.user.rel', 'reward_id', string='Usuarios Asociados')
    
    service_id = fields.Many2one('services', 'Servicios')

class RewardUserRel(models.Model):
    _name = 'reward.user.rel'
    _description = 'Relación entre Recompensa y Usuario'

    reward_id = fields.Many2one('rewards', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
    entregada = fields.Boolean(string='Entregada', default=False)