from odoo import http
from odoo.http import request
import base64

class RewardsController(http.Controller):

    @http.route('/get_rewards_by_service', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def get_rewards_by_service(self, **kwargs):
        service_id = kwargs.get("service_id")
        try:
            if not service_id:
                return {
                    'status': False,
                    'message': 'El ID del servicio es requerido.'
                }

            # Buscar recompensas asociadas al servicio especificado
            rewards = request.env['rewards'].sudo().search([
                ('service_id', '=', int(service_id)),  # Filtrar por el ID del servicio
                ('active', '=', True)  # Opcional: Solo recompensas activas
            ])

            if not rewards:
                return {
                    'status': False,
                    'message': 'No se encontraron recompensas para el servicio proporcionado.'
                }

            # Preparar la lista de recompensas junto con la información del usuario
            rewards_data = []
            for reward in rewards:
                # Buscar las relaciones en el modelo intermedio para esta recompensa
                reward_user_rels = request.env['reward.user.rel'].sudo().search([
                    ('reward_id', '=', reward.id)
                ], order='entregada ASC')

                # Agregar información de las relaciones al resultado
                for rel in reward_user_rels:
                    rewards_data.append({
                        'id': reward.id,
                        'name': reward.name,
                        'description': reward.description,
                        'points_required': reward.points_required,
                        'active': reward.active,
                        'image': base64.b64encode(reward.image).decode() if reward.image else False,
                        'entregada': rel.entregada,
                        'user': {
                            'id': rel.user_id.id,
                            'name': rel.user_id.name
                        }
                    })

            if not rewards_data:
                return {
                    'status': False,
                    'message': 'No se encontraron relaciones usuario-recompensa para este servicio.'
                }

            return {
                'status': True,
                'data': rewards_data
            }
        except Exception as e:
            return {
                'status': False,
                'message': f'Error al obtener las recompensas: {str(e)}'
            }

    @http.route('/validate_reward_delivery', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def validate_reward_delivery(self, **kwargs):
        reward_id = kwargs.get("reward_id")
        user_id = kwargs.get("user_id")

        try:
            # Verificar que ambos IDs hayan sido proporcionados
            if not reward_id or not user_id:
                return {
                    'status': False,
                    'message': 'El ID de la recompensa y el ID del usuario son requeridos.'
                }

            # Buscar la relación específica entre usuario y recompensa
            reward_user_rel = request.env['reward.user.rel'].sudo().search([
                ('reward_id', '=', int(reward_id)),
                ('user_id', '=', int(user_id))
            ], limit=1)

            if not reward_user_rel:
                return {
                    'status': False,
                    'message': 'El usuario especificado no tiene registrada esta recompensa.'
                }

            # Verificar si ya fue entregada
            if reward_user_rel.entregada:
                return {
                    'status': True,
                    'message': 'La recompensa ya ha sido entregada.',
                    'reward': {
                        'id': reward_user_rel.reward_id.id,
                        'name': reward_user_rel.reward_id.name,
                        'entregada': reward_user_rel.entregada,
                        'user': {
                            'id': reward_user_rel.user_id.id,
                            'name': reward_user_rel.user_id.name
                        }
                    }
                }

            # Marcar como entregada para este usuario específico
            reward_user_rel.sudo().write({'entregada': True})

            return {
                'status': True,
                'message': 'La recompensa ha sido marcada como entregada exitosamente.',
                'reward': {
                    'id': reward_user_rel.reward_id.id,
                    'name': reward_user_rel.reward_id.name,
                    'entregada': reward_user_rel.entregada,
                    'user': {
                        'id': reward_user_rel.user_id.id,
                        'name': reward_user_rel.user_id.name
                    }
                }
            }

        except Exception as e:
            return {
                'status': False,
                'message': f'Error al validar y actualizar la recompensa: {str(e)}'
            }