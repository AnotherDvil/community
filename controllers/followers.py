# Seguidores del servicio
# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response

class Followers(http.Controller):
    # Controlador para obtener los seguidores del servicio
    @http.route('/services/<int:id_service>/followers', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_followers(self, id_service, **kwargs):
        # Solicitud a la BDD
        followers = request.env['services'].sudo().search([('id', '=', id_service)])

        followers_list = []

        if followers.exists():
            for person in followers.followers:
                followers_list.append({
                    'id': person.id,
                    'name': person.name,
                    'email': person.email
                })
        else:
            followers_list.append({
                'message': 'No tienes seguidores!'
            })

        json_object = json.dumps(followers_list)
        return json_object

    #Controlador para obtener a los servicios seguidos
    @http.route('/followed', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def get_following_user(self, **kwargs):
        token = kwargs.get('token')
        followed = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        followed_list = []

        if followed.exists():
            for service in followed.followed_services:
                followed_list.append({
                    'id': service.id,
                    'name': service.name,
                    'direction': service.direction
                })
        else:
            followed_list.append({
                'message': 'No sigues a nadie'
            })

        json_object = json.dumps(followed_list)
        return followed_list

    @http.route('/followed/unlink/<int:id_service>', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def unlink_services_followed(self, id_service, **kwargs):
        token = kwargs.get('token')
        followed = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        if followed:
            # Buscar el servicio en base a `id_service`
            service_to_unlink = request.env['services'].sudo().browse(id_service)
            
            # Quitar el servicio de la relación Many2many
            followed.followed_services = [(3, service_to_unlink.id)]
            
            # Responder confirmando la desvinculación
            response = {
                'success': True,
                'message': f'El servicio con ID {id_service} ha sido desvinculado correctamente del usuario {followed.id}.'
            }
        else:
            # Responder en caso de no encontrar el usuario
            response = {
                'success': False,
                'message': 'Usuario no encontrado o token inválido.'
            }

        return response

        