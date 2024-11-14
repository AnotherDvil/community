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
                    'create_date': prop.create_date.strftime('%Y-%m-%d %H:%M:%S') if prop.create_date else None,  # Incluye la hora en el formato
                    'name': prop.name,
                    'written_by': prop.written_by.name,
                    'status': status_dict.get(prop.status, prop.status),  # Convertir la clave al valor amigable
                    'description': prop.description,
                    'close_date': prop.close_date.strftime('%Y-%m-%d %H:%M:%S') if prop.close_date else None
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
                    'create_date': prop.create_date.strftime('%Y-%m-%d %H:%M:%S') if prop.create_date else None,
                    'name': prop.name,
                    'written_by': prop.written_by.name,
                    'status': status_dict.get(prop.status, prop.status),
                    'description': prop.description,
                    'close_date': prop.close_date.strftime('%Y-%m-%d %H:%M:%S') if prop.close_date else None,
                    'close_date_debate': prop.close_date_debate.strftime('%Y-%m-%d %H:%M:%S') if prop.close_date_debate else None,
                    'close_date_deliver': prop.close_date_deliver.strftime('%Y-%m-%d %H:%M:%S') if prop.close_date_deliver else None,
                    'result': result_dict.get(prop.result, prop.result),
                    'service_related': prop.service_id.id
                }

                # Condiciones según el estado de la propuesta
                if prop.status == 'debate':
                    proposal_data['comments'] = comments_list

                elif prop.status == 'deliver':
                    proposal_data['votes'] = votes_list
                    proposal_data['comments'] = comments_list

                elif prop.status == 'complete':
                    proposal_data['votes'] = votes_list
                    proposal_data['comments'] = comments_list

                # Agrega la propuesta a la lista final
                unidades.append(proposal_data)

        else:
            unidades.append({
                'message': 'No se encontró esta propuesta :c'
            })

        return json.dumps(unidades)

    @http.route('/proposals/create', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def create_proposals(self, **kwargs):
        token = kwargs.get('token')
        update_user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        new_proposals = {
            'name': kwargs.get('name'),
            'status': 'debate',
            'description': kwargs.get('description'),
            'service_id': kwargs.get('service_id'),
            'written_by': update_user.id
        }

        if new_proposals and update_user:
            new_proposal = request.env['proposals'].sudo().create(new_proposals)
            response = {
                'success': True,
                'message': 'La propuesta se creo con exito',
                'id': new_proposal.id
            }
        else:
            response = {
                'success': False,
                'message': 'No se pudo crear la propuesta'
            }
        json_response = json.dumps(response)
        return response

    @http.route('/comment/<int:id_proposal>', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def create_comment(self, id_proposal, **kwargs):
        proposal = request.env['proposals'].sudo().search([('id', '=', id_proposal)], limit=1)

        if proposal.status == 'debate':
            token = kwargs.get('token')
            update_user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)

            new_comment = {
                'name': kwargs.get('name'),
                'written_by': update_user.id,
                'proposals_id': id_proposal
            }

            if update_user and new_comment:
                comment_up = request.env['comments'].sudo().create(new_comment)
                response = {
                    'success': True,
                    'message': 'El comentario se creó con exito',
                    'id': comment_up.id
                }
            else:
                response = {
                    'success': False,
                    'message': 'No se pudo crear el comentario'
                }
            return response
        else:
            response = {
                'success': False,
                'message': 'No se pudo crear el comentario'
            }

            return response

    @http.route('/vote/<int:id_proposal>', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def create_vote(self, id_proposal, **kwargs):
        proposal = request.env['proposals'].sudo().search([('id', '=', id_proposal)], limit=1)

        if proposal.status == 'deliver':
            token = kwargs.get('token')
            update_user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)

            new_vote = {
                'name': kwargs.get('name'),
                'written_by': update_user.id,
                'proposals_id': id_proposal
            }

            if update_user and new_vote:
                vote_up = request.env['vote'].sudo().create(new_vote)
                response = {
                    'success': True,
                    'message': 'El voto se creó con exito',
                    'id': vote_up.id
                }
            else:
                response = {
                    'success': False,
                    'message': 'No se pudo crear el voto'
                }
            return response
        else:
            response = {
                'success': False,
                'message': 'No se pudo crear el voto'
            }

            return response

    #borrar propuestas
    @http.route('/proposals/delete/<int:id_proposal>', type="json", auth="none", methods=['DELETE'], csrf=False, cors='*')
    def delete_proposals(self, id_proposal, **kwargs):
        proposals = request.env['proposals'].sudo().browse(id_new)
        if not proposals.exists():
            response = {
                'success': False,
                'message': 'No existe la propuesta'
            }
        else:
            proposals.unlink()
            response = {
                'success': True,
                'message': 'Exito al borrar la propuesta'
            }
        json_response = json.dumps(response)
        return json_response