# -*- coding: utf-8 -*-
import secrets
import json
from odoo import http
from odoo.http import request, Response

class Reviews(http.Controller):

    @http.route('/reviews/<int:id_service>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_reviews(self, id_service, **kwargs):
        # Solicitudes BDD
        reviews = request.env['reviews'].sudo().search([('service_id', '=', id_service)], order="create_date desc")
        
        review_list = []  # Declaramos la lista fuera del bucle

        if reviews.exists():
            for review in reviews:
                review_list.append({
                    'id': review.id,
                    'create_date': review.create_date.strftime('%Y-%m-%d') if review.create_date else None,  # Convertir la fecha a cadena
                    'name': review.name,
                    'description': review.description,
                    'rating': review.rating,
                    'written_by': review.written_by.name 
                })
        else:
            review_list.append({
                'message': 'No se encontraron reseñas de tal servicio.'
            })
        # Devolver la respuesta en formato JSON
        return json.dumps(review_list)

    @http.route('/reviews/create', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def create_reviews(self, **kwargs):
        token = kwargs.get('written_by')
        busqueda = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        if not busqueda:
            return {
                'success': False,
                'Message': 'El usuario no fue encontrado con el token proporcionado',
            }

        description = kwargs.get('description', '')
        name = kwargs.get('name', '')

        reviews_model = request.env['reviews']
        description_censored = reviews_model.censor_bad_words(description)
        name_censored = reviews_model.censor_bad_words(name)

        new_review = {
            'name': name_censored,
            'description': description_censored,
            'rating': kwargs.get('rating'),
            'written_by': busqueda.id,
            'service_id': kwargs.get('service_id')
        }
        
        request_review = request.env['reviews'].sudo().create(new_review)
        if request_review:
            # Actualiza la calificación promedio
            service = request.env['services'].sudo().browse(new_review['service_id'])
            service.get_average()

            # Enviar una notificación al dueño del negocio
            if service.owner:
                notification_data = {
                    'name': service.owner.id,
                    'message': f"{busqueda.name} ha creado una nueva reseña en tu negocio con una calificación de {new_review['rating']}.",
                    'is_read': False
                }
                request.env['notifications'].sudo().create(notification_data)

            response = {
                'success': True,
                'Message': 'La reseña se creó con éxito',
                'id': request_review.id
            }
        else:
            response = {
                'success': True,
                'Message': 'La reseña NO se creó con exito',
            }
        return response

    #falta un metodo para borrar
    @http.route('/reviews/delete/<int:id_review>', type="json", auth="none", methods=['DELETE'], csrf=False, cors='*')
    def delete_reviews(self, id_review, **kwargs):
        reviews = request.env['reviews'].sudo().browse(id_review)
        if not reviews.exists():
            response = {
                'success': False,
                'message': 'No existe la reseña'
            }
        else:
            reviews.unlink()
            response = {
                'success': True,
                'message': 'Se borró la reseña'
            }
        json_response = json.dumps(response)
        return json_response