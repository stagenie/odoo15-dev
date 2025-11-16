from odoo import http
from odoo.http import request
import json

class SimpleAPI(http.Controller):

    @http.route('/api/simple', auth='public', methods=['GET'], csrf=False)
    def simple_api(self, **kw):
        response = {
            'message': 'Hello, this is a simple API in Odoo!',
        }
        return request.make_response(json.dumps(response), headers=[('Content-Type', 'application/json')])