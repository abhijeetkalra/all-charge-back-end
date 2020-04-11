from flask_restplus import fields, Resource

from . import api
from models import Connector
from util import abort

ns = api.namespace("connectors",
                   path='/api/v1/connectors',
                   description='get all connectors')


connector_model = api.model('ConnectorModel', {
    'id': fields.Integer(description="connector id", example=2),
    'name': fields.String(description="connector name", example="J-1922"),
    'image': fields.String(description="url for connector image")
})



@ns.route("/")
class ConnectorService(Resource):
    @ns.doc('get all connectors')
    @ns.marshal_list_with(connector_model)
    def get(self):
        connectors = list(Connector.objects())
        if not connectors:
            abort(404, "networks not found")
        return connectors
