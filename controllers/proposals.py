# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response

class Proposals(http.Controller):
    # Controlador para obtener las propuestas del proyecto
    @http.route('/proposals/<int:id_service>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_proposals(self, id_service, **kwargs):
        # Solicitamos a la BDD
        proposals = request.env['proposals'].sudo().search([('service_id', '=', id_service)])

        proposals_list = []

        if proposals.exists():
            for prop in proposals:
                # Diccionario para mapear las claves a sus etiquetas amigables
                status_dict = dict(prop._fields['status'].selection)
                
                proposals_list.append({
                    'id': prop.id,
                    'create_date': prop.create_date.strftime('%Y-%m-%d') if prop.create_date else None,
                    'name': prop.name,
                    'written_by': prop.written_by.name,
                    'status': status_dict.get(prop.status, prop.status),  # Convertir la clave al valor amigable
                    'description': prop.description,
                    'close_date': prop.close_date.strftime('%Y-%m-%d') if prop.close_date else None
                })
        else:
            proposals_list.append({
                'message': 'No existen propuestas en este servicio'
            })
        
        return json.dumps(proposals_list)


    # Controlador para obtener las propuestas del proyecto
    @http.route('/proposalsDetail/<int:id_proposal>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_proposalsDetail(self, id_proposal, **kwargs):
        # Solicitudes a la base de datos
        proposals = request.env['proposals'].sudo().search([('id', '=', id_proposal), ('name', '!=', False)])
        comments = request.env['comments'].sudo().search([('proposals_id', '=', id_proposal), ('name', '!=', False)])
        votes = request.env['vote'].sudo().search([('proposals_id', '=', id_proposal), ('name', '!=', False)])

        unidades = []

        if proposals.exists():
            for prop in proposals:
                status_dict = dict(prop._fields['status'].selection)
                result_dict = dict(prop._fields['result'].selection)

                # Obtener la lista de comentarios
                comments_list = []
                if comments.exists():
                    for com in comments:
                        comments_list.append({
                            'written_by': com.written_by.name,
                            'message': com.name
                        })

                # Obtener la lista de votos
                votes_list = []
                if votes.exists():
                    for vote in votes:
                        vote_selection_dict = dict(vote._fields['name'].selection)
                        votes_list.append({
                            'postura': vote_selection_dict.get(vote.name, vote.name),
                            'written_by': vote.written_by.name
                        })

                proposal_data = {
                    'id': prop.id,
                    'create_date': prop.create_date.strftime('%Y-%m-%d') if prop.create_date else None,
                    'name': prop.name,
                    'written_by': prop.written_by.name,
                    'status': status_dict.get(prop.status, prop.status),
                    'description': prop.description,
                    'close_date': prop.close_date.strftime('%Y-%m-%d') if prop.close_date else None,
                    'result': result_dict.get(prop.result, prop.result),
                    'service_related': prop.service_id.id
                }

                # Condiciones según el estado de la propuesta
                # Añadir datos específicos según el estado
                if prop.status == 'debate':
                    proposal_data['comments'] = comments_list
                elif prop.status == 'deliver':
                    proposal_data['votes'] = votes_list
                elif prop.status == 'complete':
                    proposal_data['votes'] = votes_list
                    proposal_data['comments'] = comments_list

                # Agregar la propuesta a la lista final
                unidades.append(proposal_data)

        else:
            unidades.append({
                'message': 'No se encontró esta propuesta :c'
            })

        return json.dumps(unidades)