# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response

class Coins(http.Controller):

    @http.route('/coins', type="json", auth="none", methods=['POST'], cors='*', csrf=False)
    def update_coins(self, **kwargs):
        token = kwargs.get('token')
        user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        if user.exists():
            limit = 5
            if user.last_processed_moneda >= 5:
                response = {
                    'success': False,
                    'message': 'Ya haz llegado al limite de canjeo de hoy, por favor, espera hasta mañana'
                }
            else:
                user.moneda += 1
                user.last_processed_moneda += 1
                response = {
                    'success': True,
                    'message': 'Se canjeó correctamente, la moneda incrementó'
                }
            return response


