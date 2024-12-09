# -*- coding: utf-8 -*-
import pytz
import json
from odoo import http
from odoo import fields
from odoo.http import request, Response
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.fields import Datetime
from datetime import datetime
from pytz import timezone

class Proposals(http.Controller):
    # Controlador para obtener las propuestas del proyecto
    @http.route('/proposals/<int:id_service>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_proposals(self, id_service, **kwargs):
        local_timezone = timezone('America/Mexico_City')
        # Solicitamos a la BDD
        proposals = request.env['proposals'].sudo().search([('service_id', '=', id_service)], order="create_date desc")

        proposals_list = []

        if proposals.exists():
            for prop in proposals:
                # Diccionario para mapear las claves a sus etiquetas amigables
                status_dict = dict(prop._fields['status'].selection)

                # convierte las fechas al timezone local
                close_date_deliver_local = Datetime.context_timestamp(prop, prop.close_date_deliver) if prop.close_date_deliver else None

                if close_date_deliver_local:
                    close_date_deliver_local = close_date_deliver_local.astimezone(local_timezone)
                
                proposals_list.append({
                    'id': prop.id,
                    'create_date': prop.create_date.strftime('%Y-%m-%d %H:%M:%S') if prop.create_date else None,  # Incluye la hora en el formato
                    'name': prop.name,
                    'written_by': prop.written_by.name,
                    'status': status_dict.get(prop.status, prop.status),  # Convertir la clave al valor amigable
                    'description': prop.description,
                    'close_date': close_date_deliver_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if close_date_deliver_local else None,
                })
        else:
            proposals_list.append({
                'message': 'No existen propuestas en este servicio'
            })
        
        return json.dumps(proposals_list)

    # Controlador para obtener las propuestas del proyecto
    @http.route('/proposalsDetail/<int:id_proposal>', type="http", auth="none", methods=['GET'], csrf=False, cors='*')
    def get_proposalsDetail(self, id_proposal, **kwargs):
        local_timezone = timezone('America/Mexico_City')

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
                            'written_by': vote.written_by.name if vote.written_by else False
                        })

                # Convertir las fechas al timezone local
                close_date_debate_local = Datetime.context_timestamp(prop, prop.close_date_debate) if prop.close_date_debate else None
                close_date_deliver_local = Datetime.context_timestamp(prop, prop.close_date_deliver) if prop.close_date_deliver else None

                if close_date_debate_local:
                    close_date_debate_local = close_date_debate_local.astimezone(local_timezone)
                if close_date_deliver_local:
                    close_date_deliver_local = close_date_deliver_local.astimezone(local_timezone)

                proposal_data = {
                    'id': prop.id,
                    'create_date': prop.create_date.strftime('%Y-%m-%d %H:%M:%S') if prop.create_date else None,
                    'name': prop.name,
                    'written_by': prop.written_by.name,
                    'status': status_dict.get(prop.status, prop.status),
                    'description': prop.description,
                    'close_date_debate': close_date_debate_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if close_date_debate_local else None,
                    'close_date_deliver': close_date_deliver_local.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if close_date_deliver_local else None,
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
        token = kwargs.get('written_by')
        description = kwargs.get('description', '')
        name = kwargs.get('name', '')
        debateEndDate = kwargs.get('debateEndDate')
        deliberationEndDate = kwargs.get('deliberationEndDate')
        print("debateEndDate: ", debateEndDate)
        print("deliberationEndDate: ", deliberationEndDate)

        update_user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)

        # Convertir las fechas a UTC
        local_tz = pytz.timezone('America/Mexico_City')  # Cambia esto a la zona horaria correcta
        if debateEndDate:
            local_date = datetime.strptime(debateEndDate + ":00", '%Y-%m-%dT%H:%M:%S')
            debateEndDate = local_tz.localize(local_date).astimezone(pytz.utc)
        if deliberationEndDate:
            local_date = datetime.strptime(deliberationEndDate + ":00", '%Y-%m-%dT%H:%M:%S')
            deliberationEndDate = local_tz.localize(local_date).astimezone(pytz.utc)


        if not update_user:
            return {
                'success': False,
                'message': 'El usuario no fue encontrado con el token proporcionado'
            }

        proposals_model = request.env['reviews']
        description_censored = proposals_model.censor_bad_words(description)
        name_censored = proposals_model.censor_bad_words(name)

        # Crear la propuesta
        new_proposals = {
            'name': name_censored,
            'status': 'debate',
            'description': description_censored,
            'service_id': kwargs.get('service_id'),
            'written_by': update_user.id,
            'close_date_debate': fields.Datetime.to_string(debateEndDate) if debateEndDate else False,
            'close_date_deliver': fields.Datetime.to_string(deliberationEndDate) if deliberationEndDate else False,
        }

        if new_proposals:
            new_proposal = request.env['proposals'].sudo().create(new_proposals)

            # Obtiene el negocio relacionado
            service = request.env['services'].sudo().browse(new_proposals['service_id'])

            # Notifica a los seguidores y al dueño del negocio
            if service:
                followers = service.followers
                notifications = []

                for follower in followers:
                    if follower.id != update_user.id:
                        notifications.append({
                            'name': follower.id,
                            'message': f"Se ha creado una nueva propuesta en el negocio '{service.name}': {new_proposals['name']}.",
                            'is_read': False,
                            'route': f'/ProposalDetail/{service.id}/{new_proposal.id}',
                            'tipo': 'new_proposal_owner',
                            'servicio_mencionado': service.name,
                            'objeto_solicitado': new_proposals['name']
                        })

                # Agrega notificación para el dueño del negocio si aplica
                if service.owner and service.owner.id != update_user.id:
                    notifications.append({
                        'name': service.owner.id,
                        'message': f"Se ha creado una nueva propuesta en tu negocio '{service.name}': {new_proposals['name']}.",
                        'is_read': False,
                        'route': f'/ProposalDetail/{service.id}/{new_proposal.id}',
                        'tipo': 'new_proposal_owner',
                        'servicio_mencionado': service.name,
                        'objeto_solicitado': new_proposals['name']
                    })

                # Crea las notificaciones
                if notifications:
                    request.env['notifications'].sudo().create(notifications)

            response = {
                'success': True,
                'message': 'La propuesta se creó con éxito y se notificó a los seguidores y al dueño del negocio.',
                'id': new_proposal.id
            }
        else:
            response = {
                'success': False,
                'message': 'No se pudo crear la propuesta'
            }

        return response

    @http.route('/comment/<int:id_proposal>', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def create_comment(self, id_proposal, **kwargs):
        proposal = request.env['proposals'].sudo().search([('id', '=', id_proposal)], limit=1)

        if proposal.status == 'debate':
            token = kwargs.get('token')
            name = kwargs.get('name')

            update_user = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
            comment_model = request.env['comments']
            name_censored = comment_model.censor_bad_words(name)

            new_comment = {
                'name': name_censored,
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
            validate = request.env['vote'].sudo().search([
                ('written_by', '=', update_user.id),
                ('proposals_id', '=', id_proposal)
            ])

            if validate:
                response = {
                    'success': False,
                    'message': 'El usuario ya votó',
                    'validacion': False
                }

                return response
            else:

                new_vote = {
                    'name': kwargs.get('name'),
                    'written_by': update_user.id,
                    'proposals_id': id_proposal,
                    'validation': True
                }

                if update_user and new_vote:
                    vote_up = request.env['vote'].sudo().create(new_vote)
                    response = {
                        'success': True,
                        'message': 'El voto se creó con exito',
                        'id': vote_up.id,
                        'validacion': True
                    }
                else:
                    response = {
                        'success': False,
                        'message': 'No se pudo crear el voto',
                        'validacion': False
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