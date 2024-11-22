# -*- coding: utf-8 -*-
import secrets
import json
import base64
from odoo import http
from odoo.http import request, Response

class Services(http.Controller):
    @http.route('/services', type="http", auth='none', methods=['GET'], csrf=False, cors='*')
    def get_services(self, **kwargs):
        services = request.env['services'].sudo().search([('name', '!=', False), ('archived', '=', False)], order="create_date desc")
        unidades = []
        for service in services:
            unidades.append({
                'id': service.id,
                'name': service.name,
                'image': base64.b64encode(service.image).decode() if service.image else False,
                'qualification': service.qualification,
                'description': service.description
            })
        json_object = json.dumps(unidades)
        return json_object

    @http.route('/search_service', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def search_service(self, **kwargs):
        access_code = kwargs.get('access_code')
        token = kwargs.get('token')
        # Busca el servicio por el código de acceso
        service = request.env['services'].sudo().search([('access_code', '=', access_code)], limit=1)
        if service:
            # Busca el usuario por su ID
            user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
            if user:
                # Asocia el usuario con el servicio (empleado)
                user.sudo().write({'service_id_e': service.id, 'job': 'employee', 'service_id_e': service.id})
                response = {
                    'status': True,
                    'message': 'El usuario fue agregado al servicio como empleado.'
                }
            else:
                response = {
                    'status': False,
                    'message': 'El usuario no fue encontrado.'
                }
        else:
            response = {
                'status': False,
                'message': 'El código de acceso no se encontró.'
            }
        return json.dumps(response)

    @http.route('/services/<int:id_service>', type="http", auth='none', methods=['GET'], csrf=False, cors='*')
    def get_service_especific(self, id_service, **kwargs):
        # Solicitudes BDD
        services = request.env['services'].sudo().search([('id', '=', id_service), ('name', '!=', False), ('archived', '=', False)])
        novedades = request.env['news'].sudo().search([('service_id', '=', id_service), ('name', '!=', False)], order="create_date desc")
        unidades = []  # Inicializar la lista vacía antes de la verificación
        
        if services.exists():
            for service in services:
                novedades_list = [] # Crea una lista para almacenar las novedades
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
                    'novedades': novedades_list
                })
        else:
            unidades.append({ # Si no se encuentran servicios, se añade un mensaje a la lista `unidades`
                'message': 'No se encontraron servicios con el ID especificado.'
            })
        json_object = json.dumps(unidades) # Convierte el resultado a JSON
        return json_object

    @http.route('/services/create', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def create_services(self, **kwargs):
        new_services = {
            'name': kwargs.get('name'),
            'direction': kwargs.get('direction'),
            'number_phone': kwargs.get('number_phone'),
            'email': kwargs.get('email'),
            'owner': kwargs.get('owner'),
            'description': kwargs.get('description')
        }

        image_data = kwargs.get('image')  # Obtener la imagen en formato base64

        if image_data and image_data.startswith('data:image/'):
            try:
                # Elimina el prefijo 'data:image/png;base64,'
                header, base64_image = image_data.split(',', 1)
                new_services['image'] = base64_image
                print(new_services['image'])
            except Exception as e:
                print(f"Error al procesar la imagen: {str(e)}")
                new_services['image'] = None

        update_user = request.env['res.partner'].sudo().search([('id', '=', int(new_services['owner']))], limit=1)
        if new_services and update_user:
            new_service = request.env['services'].sudo().create(new_services)
            update_user.write({'job': 'owner'})
            response = {
                'success': True,
                'message': 'El servicio se creo con exito',
                'id': new_service.id
            }
        else:
            response = {
                'success': False,
                'message': 'No se pudo crear el servicio'
            }
        json_response = json.dumps(response)
        return response

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
                'name': kwargs.get('name', service.name),
                'direction': kwargs.get('direction', service.direction),
                'image': kwargs.get('image', service.image),
                'number_phone': kwargs.get('number_phone', service.number_phone),
                'email': kwargs.get('email', service.email),
                'owner': kwargs.get('owner', service.owner)
            }
            service.write(new_data)
            response = {
                'success': True,
                'message': 'El servicio se ha actualizado'
            }
        json_response = json.dumps(response)
        return json_response

    @http.route('/searcher', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def searcher(self, **kwargs):
        content_input = kwargs.get('content_input')

        # Convierte la entrada a minúsculas para evitar problemas de mayúsculas/minúsculas
        search_term = content_input.strip().lower()
        
        # Busca servicios basados en múltiples campos
        services = request.env['services'].sudo().search([
            '|', '|', '|',
            ('name', 'ilike', search_term),
            ('owner.name', 'ilike', search_term),
            ('direction', 'ilike', search_term),
            ('access_code', 'ilike', search_term)
        ])
        
        # Formatea los resultados
        results = []
        for service in services:
            results.append({
                'id': service.id,
                'name': service.name,
                'image': base64.b64encode(service.image).decode() if service.image else False,
                'qualification': service.qualification,
                'description': service.description
            })
        
        if results:
            return {
                'success': True,
                'message': f'Se encontraron {len(results)} servicios.',
                'results': results
            }
        else:
            return {
                'success': False,
                'message': 'No se encontraron servicios que coincidan con el término de búsqueda.'
            }