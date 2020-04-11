import json
from flask_restplus import fields, Resource, reqparse
from geopy.distance import geodesic

from . import api
from models import ChargeStation, Location
from util import abort
from .charge_point import charge_point_model
from .networks import network_model

ns = api.namespace("ChargeStation",
                   path='/api/v1/stations',
                   description='charge station query')
geo_location_model = api.model('GeoLocationModel', {
    'type': fields.String(description="always be Point", example="Point"),
    'coordinates': fields.List(fields.Float, description="GPS coordinates in [longitude, latitude]", example=[-90.3, 40.4]),
})


charge_station_model = api.model('ChargeStationModel', {
    'id': fields.Integer(description="charge statioin id", example=443266),
    'name': fields.String(description='station name', example='chargepoint - airport'),
    'network': fields.Nested(network_model),
    'locationId': fields.Integer(description="location id", example=207557),
    'cost': fields.Integer(description="cost type:\n0 = Unknown\n1 = Free\n2 = Fee", example=2),
    'cost_description': fields.String(description="cost descriptioin", example="$0.00/Hr for first 4 hours, $10.00/Hr afterwards"),
    'available': fields.Integer(description="available info: \n"
                                            "0 = Unknown\n"
                                            "1 = Available\n"
                                            "2 = InUse\n"
                                            "3 = Offline\n"
                                            "4 = Under Repair",
                                example=1),
    'hours': fields.String(description="description for opening hours", example="6:00 AM to 12:00 AM"),
    'score': fields.Float(description="user rating, 0 to 10", example=8.9),
    'images': fields.List(fields.String, description="image url"),
    'chargePoints': fields.Nested(charge_point_model),
    'geoLocation': fields.Nested(geo_location_model),
    'address': fields.String(description="address"),
    'distance': fields.Float(description="distance of station and given location in miles")
})

geo_location_base_parser = reqparse.RequestParser()
geo_location_base_parser.add_argument('count', type=int, default=200, help="result count limit, [0,500]")
geo_location_base_parser.add_argument('connectors', type=str, default='', help='connector type id, separated by comma')
geo_location_base_parser.add_argument('available', help='filter on a comma separated list of availability values', type=str, default='')
geo_location_base_parser.add_argument('networks', help='filter on a comma separated list of network ids', type=str, default='')
geo_location_base_parser.add_argument('score', help='filter on a score', type=float, default=0.0)

nearby_parser = geo_location_base_parser.copy()
nearby_parser.add_argument('radius', help='Search radius in meters', type=int, default=5000)
nearby_parser.add_argument('latitude', help='latitude', type=float, required=True)
nearby_parser.add_argument('longitude', help='longitude', type=float, required=True)


region_parser = geo_location_base_parser.copy()
region_parser.add_argument('latitude', 'latitude', type=float, required=True)
region_parser.add_argument('longitude', 'longitude', type=float, required=True)
region_parser.add_argument('latitudeDelta', 'latitude span', type=float, required=True)
region_parser.add_argument('longitudeDelta', 'longitude span', type=float, required=True)


def filter_stations(stations, args, count):
    res = []
    for s in stations:
        if len(res) >= count:
            return res
        if s['score'] < args.get('score', 0.0):
            continue
        if args.get('available'):
            try:
                avail = list(map(int, args.get('available').split(',')))
            except ValueError:
                abort(400, "invalid field: available")
            if s['available'] not in avail:
                continue
        if args.get('networks'):
            try:
                 networks = list(map(int, args.get('networks').split(',')))
            except ValueError:
                abort(400, "invalid field: networks")
            if s['network']['id'] not in networks:
                continue
        if args.get('connectors'):
            try:
                connectors = list(map(int, args.get('connectors').split(',')))
            except ValueError:
                abort(400, "invalid field: connectors")
            if not any([chpt['connector']['id'] in connectors for chpt in s['chargePoints']]):
                continue
        s.distance = geodesic(reversed(s['geoLocation']['coordinates']), [args['latitude'], args['longitude']]).miles
        if res and res[-1]['network']['id'] == s['network']['id'] and abs(res[-1].distance-s.distance) <= 0.001:
            continue
        res.append(s)
    return res


@ns.route("/<int:id>")
@ns.response(404, 'station not found')
@ns.param('id', 'station id')
class ChargeStationService(Resource):
    @ns.doc('get station by id')
    @ns.marshal_with(charge_station_model)
    def get(self, id):
        station = ChargeStation.objects(id=id).first()
        if not station:
            abort(404, "charge station not found")
        return station

@ns.route("/nearby")
class StationNearbyService(Resource):
    @ns.doc('ge nearby locations')
    @ns.marshal_list_with(charge_station_model)
    @ns.expect(nearby_parser, validate=True)
    def get(self):
        args = nearby_parser.parse_args()
        stations = ChargeStation.objects(geoLocation__near=[args['longitude'], args['latitude']],
                                geoLocation__max_distance=args['radius'])

        return filter_stations(stations, args, args.get('count'))


@ns.route("/region")
class StationRegionService(Resource):
    @ns.doc('ge locations within a region')
    @ns.marshal_list_with(charge_station_model)
    @ns.expect(region_parser, validate=True)
    def get(self):
        args = region_parser.parse_args()

        lat_lu = args['latitude'] + args['latitudeDelta']/2.0
        lng_lu = args['longitude'] - args['longitudeDelta']/2.0
        lat_rb = args['latitude'] - args['latitudeDelta']/2.0
        lng_rb = args['longitude'] + args['longitudeDelta'] / 2.0
        #lng_lu, lat_lu = args['lng_left_up'], args['lat_left_up']
        #lng_rb, lat_rb = args['lng_right_bottom'], args['lat_right_bottom']

        if not all([ -180.0 < x < 180.0 for x in [lng_lu, lng_rb]]):
            abort(400, "invalid longitude")
        if not all([ -90.0 < x < 90.0 for x in [lat_lu, lat_rb]]):
            abort(400, "invalid latitude")

        locs = ChargeStation.objects(geoLocation__geo_within_box=[(lng_lu, lat_lu), (lng_rb, lat_rb)])

        return filter_stations(locs, args, args.get('count'))