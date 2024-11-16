# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response

class News(http.Controller):
    @http.route('/news/create/<int:id_service>', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def create_news(self, id_service, **kwargs): 
        new_news = {
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'service_id': id_service
        }
        request_new = request.env['news'].sudo().create(new_news)
        if request_new:
            
            response = {
                'success': True,
                'Message': 'La novedad se creó con éxito',
                'id': request_new.id
            }
        else:
            response = {
                'success': True,
                'Message': 'La novedad NO se creó con exito',
            }
        return response

    @http.route('/news/delete/<int:id_new>', type="json", auth="none", methods=['DELETE'], csrf=False, cors='*')
    def delete_news(self, id_new, **kwargs):
        news = request.env['news'].sudo().browse(id_new)
        if not news.exists():
            response = {
                'success': False,
                'message': 'No existe la novedad'
            }
        else:
            news.unlink()
            response = {
                'success': True,
                'message': 'Exito al borrar la novedad'
            }
        json_response = json.dumps(response)
        return json_response