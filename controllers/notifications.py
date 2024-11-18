# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response

class Notifications(http.Controller):
    @http.route('/notifications', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def get_notifications(self, **kwargs):
        token = kwargs.get('token')
        user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        noti_list = []
        
        if user.exists():
            # Ordena las notificaciones por fecha de creación en orden descendente
            notifications = user.notifications.filtered(lambda n: not n.is_read).sorted(key=lambda n: n.create_date, reverse=True)
            unread_count = len(user.notifications.filtered(lambda n: not n.is_read))

            for notis in notifications:
                if notis.is_read == False:
                    noti_list.append({
                        'id': notis.id,
                        'message': notis.message,
                        'route': notis.route,
                        'number': "10+" if unread_count > 10 else unread_count
                    })
        else:
            noti_list.append({
                'message': 'No tienes notificaciones'
            })
        
        return noti_list

    """ @http.route('/notifications/length', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def get_notifications_length(self, **kwargs):
        token = kwargs.get('token')
        user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        
        if user.exists():
            # Cuenta las notificaciones no leídas
            unread_count = len(user.notifications.filtered(lambda n: not n.is_read))
            
            # Si hay más de 10 notificaciones no leídas, muestra "10+"
            response = {
                'number': "10+" if unread_count > 10 else unread_count
            }
        else:
            response = {
                'number': 0
            }
        return response """

    @http.route('/notifications/read/<int:id_noti>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def read_notifications(self, id_noti, **kwargs):
        notification = request.env['notifications'].sudo().search([('id', '=', id_noti)], limit=1)
        if notification.exists():
            notification.sudo().write({'is_read': True})
            response = {
                'success': True,
                'message': 'la notificación cambió de estado'
            }
        else:
            response = {
                'success': False,
                'message': 'no se encontró la notificación'
            }
        return json.dumps(response)