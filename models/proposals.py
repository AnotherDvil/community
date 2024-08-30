# -*- coding: utf-8 -*-

from odoo import models, fields, api

class proposals(models.Model):
    _name = 'proposals'
    _description = 'Propuestas'
    
    name = fields.Char('Nombre propuesta')
    description = fields.Char('Detalles')
    written_by = fields.Many2one('res.partner', string="Creado por", readonly=True)
    status = fields.Selection([
            ('draft', 'Borrador'), 
            ('complete', 'Completo'), 
            ('process', 'En proceso'), 
            ('cerrado', 'Cerrado')
        ], default='draft', string="Estado")
    close_date = fields.Datetime('Fecha de cierre')
    phase = fields.Selection([
        ('1', 'Uno'),
        ('2', 'Dos'),
        ('3', 'Tres')
    ], string="Fase")

    #Conexión con otros servidores
    service_id = fields.Many2one('services', 'Servicios')
    comments = fields.One2many('comments', 'proposals_id', string="Comentarios")
    
    #Metodos para cambiar el estado del registro
    def complete_status(self):
        self.status = 'complete'
    def draft_status(self):
        self.status = 'draft'
        
    #Al momento de crear un registro se llenará el campo written_by con el nombre del usuario actual
    @api.model
    def create(self, vals):
        # Obtener el usuario actual
        user = self.env.user
        # Obtener el empleado correspondiente al usuario actual
        employee = self.env['res.partner'].search([('user_id', '=', user.id)], limit=1)
        # Establecer el campo written_by con el empleado correspondiente
        vals['written_by'] = employee.id if employee else False
        return super(proposals, self).create(vals)

class comments(models.Model):
    _name = 'comments'
    _description = 'Comentarios de una propuesta'

    name = fields.Char(string="Comentario")
    approval = fields.Selection([
        ('yes', 'Lo apruebo'),
        ('no', 'NO lo apruebo'),
        ('meh', 'Me da igual')
    ], string="Aprobación")
    proposals_id = fields.Many2one('proposals', string="Propuestas")