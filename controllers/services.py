# -*- coding: utf-8 -*-
import secrets
import json
from odoo import http
from odoo.http import request, Response

class Services(http.Controller):

    @http.route('/services', type="json", auth='none', methods=['GET'], csrf=False, cors='*')
    def get_services(self, **kwargs):
        services = request.env['services'].sudo().search([('name', '!=', False), ('archived', '=', False)])
        unidades = []
        for service in services:
            unidades.append({
                'id': service.id,
                'name': service.name,
                'image': service.image,
                'qualification': service.qualification,
                'description': service.description
            })
        json_object = json.dumps({"data": unidades})
        return json_object

    @http.route('/services/<int:id_service>', type="json", auth='none', methods=['GET'], csrf=False, cors='*')
    def get_service_especific(self, id_service, **kwargs):
        services = request.env['services'].sudo().search([('id', '=', id_service), ('name', '!=', False), ('archived', '=', False)])
        unidades = []  # Inicializar la lista vacía antes de la verificación
        if services.exists():
            for service in services:
                unidades.append({
                    'id': service.id,
                    'name': service.name,
                    'image': service.image,
                    'qualification': service.qualification,
                    'description': service.description
                })
        else:
            # Si no se encuentran servicios, se añade un mensaje a la lista `unidades`
            unidades.append({
                'message': 'No se encontraron servicios con el ID especificado.'
            })
        # Convertir el resultado a JSON
        json_object = json.dumps({"data": unidades})
        # Retornar la respuesta como JSON con el código de estado 200
        return json_object

    @http.route('/services/create', type="json", auth='public', methods=['POST'], csrf=False, cors='*')
    def create_services(self, **kwargs):
        new_services = {
            'name': kwargs.get('name'),
            'direction': kwargs.get('direction')
        }
        new_service = request.env['services'].sudo().create(new_services)
        if new_services:
            response = {
                'succes': True,
                'message': 'El servicio se creo con exito',
                'id': new_service.id
            }
        else:
            response = {
                'succes': False,
                'message': 'No se pudo crear el servicio'
            }
        json_response = json.dumps(response)
        return json_response

    @http.route('/services/delete/<int:id_service>', type="http", auth='public', methods=['DELETE'], csrf=False, cors='*')
    def delete_service(self, id_service, **kwargs):
        service = request.env['services'].sudo().browse(id_service)
        if not service.exists():
            response = {
                'success': False,
                'message': 'No existe el servicio'
            }
        else:
            service.archived = True
            response = {
                'success': True,
                'message': 'Exito al borrar el servicio'
            }
        json_response = json.dumps(response)
        return json_response

    @http.route('/services/update/<int:id_service>', type="json", auth="public", methods=['PUT'], csrf=False, cors='*')
    def update_service(self, id_service, **kwargs):
        service = request.env['services'].sudo().browse(id_service)
        if not service.exists():
            response = {
                'success': False,
                'message': 'El servicio no existe'
            }
        else:
            new_data = {
                'name': kwargs.get('name', service.name)
            }
            service.write(new_data)
            response = {
                'success': True,
                'message': 'El servicio se ha actualizado'
            }
        json_response = json.dumps(response)
        return json_response