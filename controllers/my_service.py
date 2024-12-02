# -*- coding: utf-8 -*-
import secrets
import json
import base64
from odoo import http
from odoo.http import request, Response

class MyService(http.Controller):

    @http.route('/myService/<int:id_service>', type="http", auth='none', methods=['GET'], csrf=False, cors='*')
    def get_my_service(self, id_service, **kwargs):
        service = request.env['services'].sudo().search([('id', '=', id_service), ('name', '!=', False)])
        novedades = request.env['news'].sudo().search([('service_id', '=', id_service), ('name', '!=', False)], order="create_date desc")

        unidades = []

        if service.exists():
            for service in service:
                novedades_list = [] # Lista para almacenar las novedades
                if novedades.exists():
                    for novedad in novedades:
                        novedades_list.append({
                            'id': novedad.id,
                            'name': novedad.name,
                            'description': novedad.description
                        })

                unidades.append({
                    'id': service.id,
                    'name': service.name,
                    'image': base64.b64encode(service.image).decode() if service.image else False,
                    'qualification': service.qualification,
                    'description': service.description,
                    'novedades': novedades_list,
                    'access_code': service.access_code
                })
        else:
            unidades.append({ # Si no se encuentran servicios, se añade un mensaje a la lista `unidades`
                'message': 'No se encontraron servicios con el ID especificado.'
            })
        json_object = json.dumps(unidades) # Convierte el resultado a JSON
        return json_object