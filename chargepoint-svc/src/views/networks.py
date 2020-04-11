from flask_restplus import fields, Resource

from . import api
from models import Network
from util import abort

ns = api.namespace("Networks",
                   path='/api/v1/networks',
                   description='get all networks')


network_model = api.model('NetworkModel', {
    'id': fields.Integer(description="network id", example=1),
    'name': fields.String(description="network name", example="ChargePoint"),
    'phone': fields.String,
    'url': fields.String,
    'image': fields.String
})



@ns.route("/")
class NetworkService(Resource):
    @ns.doc('get all networks')
    @ns.marshal_list_with(network_model)
    def get(self):
        networks = list(Network.objects())
        if not networks:
            abort(404, "networks not found")
        return networks
