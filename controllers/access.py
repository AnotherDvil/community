# -*- coding: utf-8 -*-
import requests
import secrets
import json
from odoo import http
from odoo.http import request, Response
from PIL import Image
from io import BytesIO

class CommunityLogin(http.Controller):
    @http.route('/login', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def login(self, **kwargs):
        email = kwargs.get('email')
        # password = kwargs.get('password')
        # Buscar contacto por correo electrónico y contraseña
        partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if partner:
            if partner.token == False:
                token = secrets.token_urlsafe(20)
                partner.sudo().write({'token': token})
            else:
                token = partner.token

            response = {
                'status': True,
                'id': partner.id,
                'name': partner.name,
                'email': partner.email,
                'token': token,
                'rol': partner.job
            }

            if partner.job == 'owner':
                service_id = partner.service_owner.id
                response['owner_service'] = service_id
        else:
            response = {
                'status': False,
                'message': 'Credenciales invalidas'
            }
        return response
 
    @http.route('/validate_email', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def validate_email(self, **kwargs):
        email = kwargs.get('email')
        user = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if user:
            response = {
                'status': True,
                'message': 'Existe un usuario registrado con ese correo'
            }
        else:
            response = {
                'status': False,
                'message': 'No hay un usuario que coincida'
            }
        return response

    @http.route('/logout', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def logout(self, **kwargs):
        # Asegurémonos de recibir el token correctamente
        token = kwargs.get('token')
        # Buscar empleado por token
        partner = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        if partner:
            # Invalidar el token
            partner.sudo().write({'token': False})
            response = {
                'status': True,
                'message': 'Cierre de sesión exitoso'
            }
        else:
            response = {
                'status': False,
                'message': 'Token invalido'
            }
        return response

    @http.route('/signup', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def signup(self, **kwargs):
        # Asignar valores del usuario
        name = kwargs.get('name')
        email = kwargs.get('email')
        password = kwargs.get('password')
        user_type = kwargs.get('user_type')

        # Búsqueda de usuario por email
        user = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if user:  # Si existe un usuario, responder negativamente
            response = {
                'status': False,
                'message': 'El correo ya está registrado'
            }
            return response
        else:
            # Generar un token único para el usuario
            token = secrets.token_urlsafe(20)

            if user_type:  # Si el tipo de usuario es 'usuario'
                usuario = request.env['res.partner'].sudo().create({
                    'name': name,
                    'email': email,
                    'password': password,
                    'job': user_type,
                    'token': token  # Guarda el token generado
                })

                if usuario:
                    response = {
                        'status': True,
                        'id': usuario.id,
                        'name': usuario.name,
                        'email': usuario.email,
                        'token': token  # Devolver el token en la respuesta
                    }
                else:
                    response = {
                        'status': False,
                        'message': 'Hubo un error al crear al usuario'
                    }

                return response