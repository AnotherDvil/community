# -*- coding: utf-8 -*-
import secrets
import json
from odoo import http
from odoo.http import request, Response

class Reviews(http.Controller):

    @http.route('/reviews/<int:id_service>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_reviews(self, id_service, **kwargs):
        # Solicitudes BDD
        reviews = request.env['reviews'].sudo().search([('service_id', '=', id_service)])
        
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
        print("Token: ",token)
        busqueda = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        new_review = {
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'rating': kwargs.get('rating'),
            'written_by': busqueda.id,
            'service_id': kwargs.get('service_id')
        }
        print(new_review)
        request_review = request.env['reviews'].sudo().create(new_review)
        if request_review:
            response = {
                'success': True,
                'Message': 'La reseña se creó con exito',
                'id': request_review.id
            }
        else:
            response = {
                'success': True,
                'Message': 'La reseña NO se creó con exito',
            }
        return response