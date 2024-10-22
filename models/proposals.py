# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date, time, timedelta

class proposals(models.Model):
    _name = 'proposals'
    _description = 'Propuestas'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Nombre propuesta')
    description = fields.Char('Detalles')
    written_by = fields.Many2one('res.partner', string="Creado por")
    status = fields.Selection([
            ('draft', 'Borrador'), 
            ('debate', 'Debate'),
            ('deliver', 'Deliberación'), 
            ('complete', 'Completo'),
        ], default='draft', string="Estado")
    close_date = fields.Datetime('Fecha de cierre', tracking=True)
    result = fields.Selection([
        ('denied', 'Denegado'),
        ('progress', 'En progreso'),
        ('accepted', 'Aceptado')
    ], default='progress', string="Resultado")

    #Conexión con otros modelos
    service_id = fields.Many2one('services', 'Servicios')
    comments = fields.One2many('comments', 'proposals_id', string="Comentarios")
    vote = fields.One2many('vote', 'proposals_id', string="Votaciones")
    
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

    def obtain_results(self):
        today = datetime.today()
        print("Hoy es: ",today)
        for record in self:
            if record.close_date:
                margin = timedelta(minutes=30) # Margen de tiempo, es decir, considera 30 mn antes o despues

                # Varificados que hoy está dentro del margen de la fecha de cierre
                if abs(today - record.close_date) <= margin:
                    count_yes = 0
                    count_no = 0
                    count_meh = 0
                    
                    for votes in record.vote:
                        if votes.name == 'yes':
                            count_yes += 1
                        elif votes.name == 'no':
                            count_no += 1
                        else:
                            count_meh += 1
                    
                    # Determina cuál es el voto con mayor cantidad
                    if count_yes >= count_no and count_yes >= count_meh:
                        majority_vote = 'yes'
                        record.result = 'accepted'
                    elif count_no >= count_yes and count_no >= count_meh:
                        majority_vote = 'no'
                        record.result = 'denied'
                    else:
                        majority_vote = 'meh'
                        record.result = 'progress'
                    
                    print(f"Resultados: Yes: {count_yes}, No: {count_no}, Meh: {count_meh}")
                    print(f"Mayoría: {majority_vote}")

                    record.status = 'complete'
                else:
                    print(f"La fecha y hora actual no están dentro del margen de la fecha de cierre para la propuesta: '{record.name}'.")
            else:
                print(f"La propuesta: '{record.name}' no tiene una fecha de cierre definida.")

    def _cron_obtain_results(self):
        today = datetime.today()
        print("Hoy es: ",today)

        proposals = self.env['proposals'].search([('name', '!=', False)])
        for record in proposals:
            if record.close_date:
                margin = timedelta(minutes=30) # Margen de tiempo, es decir, considera 30 mn antes o despues

                # Varificados que hoy está dentro del margen de la fecha de cierre
                if abs(today - record.close_date) <= margin:
                    count_yes = 0
                    count_no = 0
                    count_meh = 0
                    
                    for votes in record.vote:
                        if votes.name == 'yes':
                            count_yes += 1
                        elif votes.name == 'no':
                            count_no += 1
                        else:
                            count_meh += 1
                    
                    # Determina cuál es el voto con mayor cantidad
                    if count_yes >= count_no and count_yes >= count_meh:
                        majority_vote = 'yes'
                        record.result = 'accepted'
                    elif count_no >= count_yes and count_no >= count_meh:
                        majority_vote = 'no'
                        record.result = 'denied'
                    else:
                        majority_vote = 'meh'
                        record.result = 'progress'
                    
                    print(f"Resultados: Yes: {count_yes}, No: {count_no}, Meh: {count_meh}")
                    print(f"Mayoría: {majority_vote}")

                    record.status = 'complete'
                else:
                    print(f"La fecha y hora actual no están dentro del margen de la fecha de cierre para la propuesta: '{record.name}'.")
            else:
                print(f"La propuesta: '{record.name}' no tiene una fecha de cierre definida.")

class comments(models.Model):
    _name = 'comments'
    _description = 'Comentarios de una propuesta'

    name = fields.Char(string="Comentario")

    written_by = fields.Many2one('res.partner', string="Creado por")
    proposals_id = fields.Many2one('proposals', string="Propuestas")

class vote(models.Model):
    _name = 'vote'
    _description = 'Voto'

    name = fields.Selection([
        ('yes', 'Lo apruebo'),
        ('no', 'NO lo apruebo'),
        ('meh', 'Me da igual')
    ], string="Aprobación")

    written_by = fields.Many2one('res.partner', string="Creado por")
    proposals_id = fields.Many2one('proposals', string="Propuestas")