from odoo import models, fields, api

class Notifications(models.Model):
    _name = 'notifications'

    name = fields.Many2one('res.partner', string="Usuario", required=True)
    message = fields.Text(string="Mensaje", required=True)
    is_read = fields.Boolean(string="Leída", default=False)
    create_date = fields.Datetime(string="Fecha de creación", default=fields.Datetime.now)