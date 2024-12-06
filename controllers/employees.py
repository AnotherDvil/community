# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import request, Response

class Employees(http.Controller):
    @http.route('/employees/<int:id_service>', type="http", auth="none", methods=['GET'], cors='*', csrf=False)
    def get_employees(self, id_service, **kwargs):
        employees = request.env['services'].sudo().search([('id', '=', id_service)])

        employees_list = []

        if employees.exists():
            for employee in employees.empleados:
                employees_list.append({
                    'id': employee.id,
                    'name': employee.name,
                    'email': employee.email
                })
        else:
            employees_list.append({
                'success': False,
                'message': 'No hay empleados de este servicio'
            })
        return json.dumps(employees_list)
    
    @http.route('/employees/unlink/<int:id_service>', type="json", auth="none", methods=['POST'], csrf=False, cors='*')
    def unlink_employees(self, id_service, **kwargs):
        id_employee = kwargs.get('id_employee')
        employee = request.env['services'].sudo().search([('id', '=', id_service)], limit=1)
        if employee:
            employee_to_unlink = request.env['res.partner'].sudo().search([('id', '=', id_employee)])
            employee.empleados = [(3, employee_to_unlink.id)]
            employee_to_unlink.job = 'user'
            employee_to_unlink.service_id_e = False

            response = {
                'success': True,
                'message': 'Empleado eliminado correctamente'
            }
        else:
            response = {
                'success': False,
                'message': 'El empleado no existe'
            }
        return response