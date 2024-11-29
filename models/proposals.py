# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date, time, timedelta
import logging
import re

_logger = logging.getLogger(__name__)

# Lista de malas palabras a censurar
BAD_WORDS = [
    "pendejo", "pendeja", "cabron", "cabrona", "chingón", "chingona", "chingar", "chingada", 
    "chingado", "puto", "puta", "joto", "marica", "maricón", "mamón", "mamona", "culero", 
    "culera", "pinche", "guey", "wey", "zorra", "perra", "baboso", "babosa", "pito", "verga", 
    "menso", "culito", "madrazo", "chingadera", "chingadazo", "chingas", "chingaste", 
    "hijo de la chingada", "chingón", "chingona", "tarado", "estúpido", "idiota", "mugroso", 
    "mugrosa", "güey", "huevón", "guevón", "jodido", "mierda", "cacas", "nalga", "nalgotas", 
    "nalguitas", "prieto", "prieta", "nalgón", "gorda", "huevudo", "zorrón", "lagartona", "burra",
    "burro", "cochina", "metiche", "manchado", "chafa", "corriente", "piruja", "pirujita", "argüendero", 
    "chismoso", "chismosa", "vago", "rata", "mamonazo", "pelón", "menso", "mensote", "apestoso", "pata rajada", 
    "marrano", "zoquete", "imbécil", "ocicón", "mamilas", "chango", "meco", "no mames", "a huevo", "qué pedo",
    "pinche güey", "pinche vieja", "chingas a tu madre", "hijo de puta", "baboso", "pinche pendejo", "chingado güey", 
    "culero", "culera", "chingaquedito", "chale", "vato", "pinche vato", "pinche cabrón", "pinche joto"
]

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
    result = fields.Selection([
        ('denied', 'Denegado'),
        ('progress', 'En progreso'),
        ('accepted', 'Aceptado')
    ], default='progress', string="Resultado")

    close_date_debate = fields.Datetime('Fecha de cierre de la fase debate', tracking=True)
    close_date_deliver = fields.Datetime('Fecha de cierre de la fase deliberación', tracking=True)

    #Conexión con otros modelos
    service_id = fields.Many2one('services', 'Servicios')
    comments = fields.One2many('comments', 'proposals_id', string="Comentarios")
    vote = fields.One2many('vote', 'proposals_id', string="Votaciones")
    
    #Metodos para cambiar el estado del registro
    def complete_status(self):
        self.status = 'complete'
    def draft_status(self):
        self.status = 'draft'
        
    """ #Al momento de crear un registro se llenará el campo written_by con el nombre del usuario actual
    @api.model
    def create(self, vals):
        # Obtener el usuario actual
        user = self.env.user
        # Obtener el empleado correspondiente al usuario actual
        employee = self.env['res.partner'].search([('user_id', '=', user.id)], limit=1)
        # Establecer el campo written_by con el empleado correspondiente
        vals['written_by'] = employee.id if employee else False
        return super(proposals, self).create(vals) """

    def change_phase(self):
        today = datetime.today()
        print("Hoy es: ",today)
        for record in self:
            margin = timedelta(minutes=5)
            if record.close_date_debate:
                if abs(today - record.close_date_debate) <= margin:
                    record.status = 'deliver'
            elif record.close_date_debate and record.close_date_deliver:
                if abs(today - record.close_date_deliver) <= margin:
                    record.obtain_results()
                    record.status = 'complete'

    def _cron_change_phase(self):
        today = datetime.today()
        print("Hoy es: ",today)
        proposals = self.env['proposals'].search([('name', '!=', False)])
        for record in proposals:
            margin = timedelta(minutes=5)
            if record.close_date_debate:
                if abs(today - record.close_date_debate) <= margin:
                    record.status = 'deliver'
            elif record.close_date_debate and record.close_date_deliver:
                if abs(today - record.close_date_deliver) <= margin:
                    record.obtain_results()
                    record.status = 'complete'

    def obtain_results(self):
        today = datetime.today()
        print("Hoy es: ",today)
        for record in self:
            if record.close_date_debate and record.close_date_deliver:
                margin = timedelta(minutes=10) # Margen de tiempo, es decir, considera 30 mn antes o despues

                # Varificados que hoy está dentro del margen de la fecha de cierre
                if abs(today - record.close_date_deliver) <= margin:
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
            if record.close_date_debate:
                margin = timedelta(minutes=10) # Margen de tiempo, es decir, considera 30 mn antes o despues

                # Varificados que hoy está dentro del margen de la fecha de cierre
                if abs(today - record.close_date_debate) <= margin:
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
    
    def censor_bad_words(self, text):
        for bad_word in BAD_WORDS:
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
        return super(proposals, self).create(vals)

    def write(self, vals):
        if 'description' in vals:
            vals['description'] = self.censor_bad_words(vals['description'])
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(proposals, self).write(vals)

class comments(models.Model):
    _name = 'comments'
    _description = 'Comentarios de una propuesta'

    name = fields.Char(string="Comentario")

    written_by = fields.Many2one('res.partner', string="Creado por")
    proposals_id = fields.Many2one('proposals', string="Propuestas")

    def censor_bad_words(self, text):
        for bad_word in BAD_WORDS:
            regex = re.compile(re.escape(bad_word), re.IGNORECASE)
            replacement = bad_word[0] + '*' * (len(bad_word) - 2) + bad_word[-1]
            text = regex.sub(replacement, text)
        return text

    @api.model
    def create(self, vals):
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(comments, self).create(vals)

    def write(self, vals):
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(comments, self).write(vals)

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
    validation = fields.Boolean("Ya votó?")