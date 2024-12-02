# -*- coding: utf-8 -*-
import secrets
import json
import base64
from odoo import http
from odoo.http import request, Response

class Rewards(http.Controller):

    @http.route('/myRewards', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def get_my_rewards(self, **kwargs):
        token = kwargs.get("token")
        rewards = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)
        reward_list = []

        if rewards.exists():

            for reward in rewards.followed_rewards:
                if reward.active == True:
                    reward_list.append({
                        'id': reward.id,
                        'name': reward.name,
                        'description': reward.description,
                        'points_required': reward.points_required,
                        'active': reward.active,
                        'image': base64.b64encode(reward.image).decode() if reward.image else False,
                        'service': reward.service_id.name
                    })
        else:
            reward_list,append({
                'message': 'No tienes recompensas activas, debes seguir a un negocio para obtener sus recompensas'
            })

        return {
            'community_points': rewards.moneda,
            'data': reward_list,
        }

    @http.route('/myRewards/redeem', type="json", auth='none', methods=['POST'], csrf=False, cors='*')
    def redeem_my_reward(self, **kwargs):
        token = kwargs.get("token")
        reward_id = kwargs.get("reward_id")

        contact = request.env['res.partner'].sudo().search([('token', '=', token)], limit=1)

        if not contact:
            return {'error': 'Usuario no encontrado o token inválido.'}

        reward_to_redeem = contact.followed_rewards.filtered(lambda r: r.id == reward_id and r.active)

        if not reward_to_redeem:
            return {'error': 'Recompensa no encontrada o ya ha sido canjeada.'}

        reward_to_redeem = reward_to_redeem[0]
        if contact.moneda < reward_to_redeem.points_required:
            return {'error': 'No tienes suficientes puntos para canjear esta recompensa.'}

        try:
            contact.moneda -= reward_to_redeem.points_required
            contact.redeemed_rewards = [(4, reward_to_redeem.id)]
            contact.followed_rewards = [(3, reward_to_redeem.id)]
            
            business_owner = reward_to_redeem.service_id.owner
            if business_owner:
                notification_message = (
                    f"{contact.name} ha canjeado la recompensa '{reward_to_redeem.name}' "
                    f"de tu servicio '{reward_to_redeem.service_id.name}'."
                )
                request.env['notifications'].sudo().create({
                    'name': business_owner.id,
                    'message': notification_message,
                    'route': False
                })

            return {
                'success': True,
                'message': 'Recompensa canjeada exitosamente.',
                'reward': {
                    'id': reward_to_redeem.id,
                    'name': reward_to_redeem.name,
                    'description': reward_to_redeem.description,
                    'points_required': reward_to_redeem.points_required,
                    'active': reward_to_redeem.active
                }
            }
        except Exception as e:
            _logger.error(f"Error al canjear recompensa: {str(e)}")
            return {'error': 'Ocurrió un error al intentar canjear la recompensa.'}

    # Controladores para el negocio, con estos podrá crear y borrar una recompensa
    @http.route('/rewards/get/<int:id_service>', type="http", auth="none", methods=['GET'], cors='*', csrf=False)
    def get_rewards(self, id_service, **kwargs):
        rewards = request.env['rewards'].sudo().search([('service_id', '=', id_service), ('active', '=', True)])
        rewards_list = []

        if rewards.exists():
            for reward in rewards:
                rewards_list.append({
                    'id': reward.id,
                    'name': reward.name,
                    'description': reward.description,
                    'points_required': reward.points_required,
                    'is_active': reward.active,
                    'image': base64.b64encode(reward.image).decode() if reward.image else False,
                    'service': reward.service_id.name
                })
        else:
            rewards_list.append({
                'message': 'No hay recompensas, crea una!'
            })
        return json.dumps(rewards_list)

    @http.route('/rewards/create', type="json", auth="none", methods=['POST'], cors='*', csrf=False)
    def create_reward(self, **kwargs):
        new_reward = {
            'name': kwargs.get('name'),
            'description': kwargs.get('description'),
            'points_required': kwargs.get('points_required'),
            'active': kwargs.get('active'),
            'service_id': kwargs.get('service_id')
        }

        if new_reward:
            new_rewards = request.env['rewards'].sudo().create(new_reward)

            service = request.env['services'].sudo().browse(kwargs.get('service_id'))
            if service.exists():
                # Identifica a los seguidores del servicio
                followers = service.followers

                # Crea notificaciones para cada seguidor
                notifications = []
                for follower in followers:
                    notifications.append({
                        'name': follower.id,
                        'message': f"¡Nueva recompensa disponible! {new_rewards.name}: {new_rewards.description}",
                        'route': f"/MyRewards"
                    })

                # Crea todas las notificaciones en un solo paso
                if notifications:
                    request.env['notifications'].sudo().create(notifications)

            response = {
                'success': True,
                'message': 'La recompensa se creó con exito',
                'id': new_rewards.id
            }
        else:
            response = {
                'success': False,
                'message': 'No se pudo crear la recompensa'
            }
        return response

    @http.route('/rewards/delete/<int:id_reward>', type="http", auth="none", methods=['DELETE'], cors='*', csrf=False)
    def delete_reward(self, id_reward, **kwargs):
        reward = request.env['rewards'].sudo().browse(id_reward)
        if not reward.exists():
            response = {
                'success': False,
                'message': 'No existe la recompensa'
            }
        else:
            reward.unlink()
            response = {
                'success': True,
                'message': 'Éxito al borrar la recompensa'
            }
        return json.dumps(response)