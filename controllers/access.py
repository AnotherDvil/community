# -*- coding: utf-8 -*-
import secrets
import json
from odoo import http
from odoo.http import request, Response

class CommunityLogin(http.Controller):
    @http.route('/login', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def login(self, **kwargs):
        email = kwargs.get('email')
        password = kwargs.get('password')
        # Buscar contacto por correo electrónico y contraseña
        partner = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if partner:
            #token = secrets.token_urlsafe(20)
            partner.sudo().write({'token': token})
            response = {
                'status': True,
                'id': partner.id,
                'name': partner.name,
                'email': partner.email,
                'token': partner.token
            }
        else:
            response = {
                'status': False,
                'message': 'Credenciales invalidas'
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
                    'token': token  # Guardar el token generado
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

    """ @http.route('/signup', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
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
            
            if user_type == 'user':  # Si el tipo de usuario es 'usuario'
                usuario = request.env['res.partner'].sudo().create({
                    'name': name,
                    'email': email,
                    'password': password,
                    'job': user_type,
                    'token': token  # Guardar el token generado
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

            elif user_type == 'employee':  # Si el tipo de usuario es 'empleado'
                access_code = kwargs.get('access_code')
                service = request.env['services'].sudo().search([('access_code', '=', access_code)], limit=1)

                if service:
                    usuario = request.env['res.partner'].sudo().create({
                        'name': name,
                        'email': email,
                        'password': password,
                        'job': user_type,
                        'service_id_e': service.id,
                        'token': token  # Guardar el token generado
                    })

                    if usuario:
                        response = {
                            'status': True,
                            'id': usuario.id,
                            'name': usuario.name,
                            'email': usuario.email,
                            'service': service.name,
                            'token': token  # Devolver el token en la respuesta
                        }
                    else:
                        response = {
                            'status': False,
                            'message': 'Hubo un error al crear al empleado'
                        }
                else:
                    response = {
                        'status': False,
                        'message': 'Código de acceso incorrecto o servicio no encontrado'
                    }

                return response

            elif user_type == 'dueño':  # Si el tipo de usuario es 'dueño'
                picture_service = kwargs.get('image_service')
                service_name = kwargs.get('service_name')
                street = kwargs.get('street')
                phone_service = kwargs.get('phone_service')
                service_email = kwargs.get('service_email')
                description = kwargs.get('description')

                # Búsqueda en la base de datos para el servicio
                service = request.env['services'].sudo().search([('email', '=', service_email)], limit=1)

                if service:
                    response = {
                        'status': False,
                        'message': 'Ya existe un servicio registrado con este correo electrónico'
                    }
                else:
                    # Crear usuario
                    usuario = request.env['res.partner'].sudo().create({
                        'name': name,
                        'email': email,
                        'password': password,
                        'job': user_type,
                        'token': token  # Guardar el token generado
                    })

                    if usuario:
                        # Crear servicio
                        servicio = request.env['services'].sudo().create({
                            'name': service_name,
                            'owner': usuario.id,
                            'image': picture_service,
                            'direction': street,
                            'number_phone': phone_service,
                            'email': service_email,
                            'description': description
                        })

                        if servicio:
                            response = {
                                'status': True,
                                'user_id': usuario.id,
                                'service_id': servicio.id,
                                'name': usuario.name,
                                'email': usuario.email,
                                'service_name': servicio.name,
                                'token': token  # Devolver el token en la respuesta
                            }
                        else:
                            response = {
                                'status': False,
                                'message': 'Hubo un error al crear el servicio'
                            }
                    else:
                        response = {
                            'status': False,
                            'message': 'Hubo un error al crear al dueño'
                        }

                return response """

    """@http.route('/signup', type="http", auth="none", methods=['POST'], csrf=False, cors='*')
    def signup(self, **kwargs):
        # Asignamos valores del usuario
        name = kwargs.get('name')
        email = kwargs.get('email')
        password = kwargs.get('password')
        user_type = kwargs.get('user_type')

        # Búsqueda en la base de datos
        user = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        
        if user:  # Si existe un usuario con el correo proporcionado
            return {
                'status': False,
                'message': 'El correo ya está registrado'
            }

        # Base de creación del usuario
        usuario_vals = {
            'name': name,
            'email': email,
            'password': password,
            'job': user_type
        }

        # Crear usuario según el tipo
        if user_type == 'employee':
            access_code = kwargs.get('access_code')
            service = request.env['services'].sudo().search([('access_code', '=', access_code)], limit=1)

            if not service:
                return {
                    'status': False,
                    'message': 'Código de acceso incorrecto o servicio no encontrado'
                }
            usuario_vals['service_id_e'] = service.id

        elif user_type == 'dueño':
            service_email = kwargs.get('service_email')
            service_exists = request.env['services'].sudo().search([('email', '=', service_email)], limit=1)

            if service_exists:
                return {
                    'status': False,
                    'message': 'Ya existe un servicio registrado con este correo electrónico'
                }
            
        usuario = request.env['res.partner'].sudo().create(usuario_vals)

        if user_type == 'dueño' and usuario:
            # Crear servicio si es dueño
            service_vals = {
                'name': kwargs.get('service_name'),
                'owner': usuario.id,
                'image': kwargs.get('image_service'),
                'direction': kwargs.get('street'),
                'number_phone': kwargs.get('phone_service'),
                'email': kwargs.get('service_email'),
                'description': kwargs.get('description')
            }
            servicio = request.env['services'].sudo().create(service_vals)

            if not servicio:
                return {
                    'status': False,
                    'message': 'Hubo un error al crear el servicio'
                }
            return {
                'status': True,
                'user_id': usuario.id,
                'service_id': servicio.id,
                'name': usuario.name,
                'email': usuario.email,
                'service_name': servicio.name
            }

        if usuario:
            return {
                'status': True,
                'id': usuario.id,
                'name': usuario.name,
                'email': usuario.email
            }
        else:
            return {
                'status': False,
                'message': 'Hubo un error al crear al usuario'
            }"""

