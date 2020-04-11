from flask_restplus import fields, Resource

from . import api
from models import ChargePoint
from util import abort

ns = api.namespace("ChargePoint",
                   path='/api/v1/chargepoint',
                   description='charge_point query')

connector_model = api.model('ConnectorModel', {
    'id': fields.Integer(description="connector id", example=2),
    'name': fields.String(description="connector name", example="J-1772"),
    'image': fields.String(description='image url', example="https://assets.plugshare.com/assets/outlets/image08.png")
})


charge_point_model = api.model('ChargePointModel', {
    'id': fields.Integer(description="charge point id", example=330854),
    'networkId': fields.Integer(description="network id", example=35),
    'stationId': fields.Integer(description="station id", example=132477),
    'available': fields.Integer(description="available info: \n"
                                            "0 = Unknown\n"
                                            "1 = Available\n"
                                            "2 = InUse\n"
                                            "3 = Offline\n"
                                            "4 = Under Repair",
                                example=1),
    'connector': fields.Nested(connector_model),
    'kilowatts': fields.Integer(description="charge power in kilowatts", example=16),
})


@ns.route("/<int:id>")
@ns.response(404, 'charge point not found')
@ns.param('id', 'charge point id')
class ChargePointService(Resource):
    @ns.doc('get chargepoint by id')
    @ns.marshal_with(charge_point_model)
    def get(self, id):
        chpt = ChargePoint.objects(id=id).first()
        if not chpt:
            abort(404, "charge point not found")
        return chpt


