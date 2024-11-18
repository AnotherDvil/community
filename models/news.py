# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import re

_logger = logging.getLogger(__name__)

class news(models.Model):
    _name = 'news'
    _description = 'Novedades del negocio'
    
    name = fields.Char('Nombre')
    description = fields.Char('Descripción')
    service_id = fields.Many2one('services', string="Servicio")

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

    def censor_bad_words(self, text):
        for bad_word in self.BAD_WORDS:
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
        return super(news, self).create(vals)

    def write(self, vals):
        if 'description' in vals:
            vals['description'] = self.censor_bad_words(vals['description'])
        if 'name' in vals:
            vals['name'] = self.censor_bad_words(vals['name'])
        return super(news, self).write(vals)