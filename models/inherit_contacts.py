# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from datetime import datetime, date, time
from odoo.exceptions import UserError
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
    moneda = fields.Integer('Puntos Community', default=0)
    last_processed_moneda = fields.Integer('Ultima act. Moneda', help="Veces que se ha actualizado el campo moneda", default=0)
    #Empleado
    service_id_e = fields.Many2one('services', string='Servicio empleado')
    service_id_f = fields.Many2one('services', string='Servicio inscrito')
    #Seguidores
    followed_services = fields.Many2many('services','service_partner_rel','partner_id','service_id',string="Servicios Seguidos")
    #Propietario del servicio
    service_owner = fields.Many2one('services', string='Servicio del dueño', compute='get_owner')
    # Recompensas canjeadas
    redeemed_rewards = fields.Many2many('rewards', 'reward_partner_rel', 'partner_id', 'reward_id', string="Recompensas Canjeadas")
    followed_rewards = fields.One2many('rewards', compute='_compute_followed_rewards', string="Recompensas de Servicios Seguidos")
    #Notificaciones
    notifications = fields.One2many('notifications', 'name', string="Notificaciones")

    @api.depends('last_processed_moneda')
    def _cron_reset_moneda(self):
        today = datetime.today()
        contacts = self.env['res.partner'].search([('name', '!=', False)])
        for record in contacts:
            if record.last_processed_moneda:
                record.last_processed_moneda = 0

    @api.depends('followed_services', 'redeemed_rewards')
    def _compute_followed_rewards(self):
        for record in self:
            # Obtener todas las recompensas de los servicios seguidos
            all_rewards = record.followed_services.mapped('rewards')
            # Filtrar recompensas que no están en las canjeadas
            available_rewards = all_rewards - record.redeemed_rewards
            record.followed_rewards = available_rewards
            self.register_existing_rewards()

    def redeem_reward(self, reward_id):
        # Obtenemos el usuario y la recompensa que desea canjear
        reward = self.env['rewards'].browse(reward_id)

        # Validamos si el usuario ya ha canjeado esta recompensa específica
        if reward in self.redeemed_rewards:
            raise UserError("Esta recompensa ya ha sido canjeada.")

        # Validamos que el usuario tenga suficientes monedas para canjear la recompensa
        if self.moneda < reward.points_required:
            raise UserError("No tienes suficientes puntos para canjear esta recompensa.")

        # Descontamos las monedas requeridas
        self.moneda -= reward.points_required

        # Agregamos la recompensa a la lista de recompensas canjeadas
        self.write({'redeemed_rewards': [(4, reward.id)]})
        self.register_existing_rewards()

    def register_existing_rewards(self):
        # Obtener todas las recompensas ya canjeadas por este usuario
        for partner in self:
            for reward in partner.redeemed_rewards:
                # Crear una relación entre el usuario y la recompensa si no existe
                existing_rel = self.env['reward.user.rel'].search([
                    ('user_id', '=', partner.id),
                    ('reward_id', '=', reward.id)
                ])
                if not existing_rel:
                    self.env['reward.user.rel'].create({
                        'reward_id': reward.id,
                        'user_id': partner.id
                    })

    def redeem_reward_action(self):
        self.ensure_one()

        # Filtra solo las recompensas que el usuario aún no ha canjeado
        available_rewards = self.followed_services.mapped('rewards').filtered(
            lambda r: r not in self.redeemed_rewards
        )
        
        if not available_rewards:
            raise UserError("No hay recompensas disponibles para canjear.")

        # Usar el primer reward_id en available_rewards que aún no haya sido canjeado
        reward_id = available_rewards[0].id
        result = self.redeem_reward(reward_id)
        self.register_existing_rewards()

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
                    record.service_owner = False
                """ else:
                    # Si no se encuentra un servicio, asigna False
                    record.service_owner = ''
                    record.job = 'user'  # Restablece el tipo de usuario a 'Usuario' """
            except Exception as e:
                # Manejo de errores para evitar que el sistema falle
                _logger.error(f"Error al calcular el servicio del dueño para el contacto {record.id}: {str(e)}")
                record.service_owner = ''  # Asigna False si ocurre un error