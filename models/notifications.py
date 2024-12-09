from odoo import models, fields, api

class Notifications(models.Model):
    _name = 'notifications'

    name = fields.Many2one('res.partner', string="Usuario", required=True)
    message = fields.Text(string="Mensaje", required=True)
    is_read = fields.Boolean(string="Leída", default=False)
    create_date = fields.Datetime(string="Fecha de creación", default=fields.Datetime.now)
    route = fields.Char(string="Ruta")
    tipo = fields.Char(string="Tipo de notificación")
    service = fields.Char(string="Servicio relacionado")
    usuario_mencionado = fields.Char(string="Usuario mencionado")
    objeto_solicitado = fields.Char(string="Recompensa/Propuesta/Novedad")
    servicio_mencionado = fields.Char(string="Servicio mencionado")