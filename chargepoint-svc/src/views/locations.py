from flask_restplus import fields, Resource
from flask_restplus import reqparse

from . import api
from models import Location
from util import abort
from .stations import geo_location_model, charge_station_model, nearby_parser, region_parser

ns = api.namespace("Location",
                   path='/api/v1/locations',
                   description='location query')

location_model = api.model('LocationModel', {
    'id': fields.Integer(description="location id", example=207557),
    'address': fields.String(description="locatioin address", example="7450 Wisconsin Ave, Bethesda, MD 20814, USA"),
    'name': fields.String(description="location name", example="3 Bethesda Metro Center"),
    'description': fields.String(description="description", example="9 Greenlots chargers, all J1772, next to the Edison building # 6090, which is near the back of the complex."),
    'phone': fields.String(description="phone number", example="9165674300"),
    'poi_name': fields.String(description="Point of interest / location type name", example="Restaurant"),
    'parking_type_name': fields.String(description="The types of parking available. Customers Only, Free, Pay, Restricted, Unknown, '', or null", example="Pay"),
    'cost_description': fields.String(description="A description of fees for charging and parking at this location", example="Not free, No sign. Charged $.40 for Hour and a half of slow 4.61kW charging. "),
    'open247': fields.Boolean(description="open for 24/7", example=False),
    'amenities': fields.List(fields.String, description="amenities tags", example=["Dining", "EV Parking","Shopping"]),
    'stations': fields.Nested(charge_station_model, as_list=True),
    'hours': fields.String(description="description for opening hours", example="6:00 AM to 12:00 AM"),
    'score': fields.Float(description="user rating, 0 to 10", example=8.9),
    'photos': fields.List(fields.String, description="photos url"),
    'geoLocation': fields.Nested(geo_location_model)
})


def filter_locations(locs, args, count):
    res = []
    for loc in locs:
        if len(res) >= count:
            return res
        if loc['score'] < args.get('score', 0.0):
            continue
        if args.get('availability'):
            try:
                avail = list(map(int, args.get('availability').split(',')))
            except ValueError:
                abort(400, "invalid field: availability")
            loc['stations'] = list(filter(lambda x: x['available'] in avail, loc['stations']))
        if args.get('networks'):
            try:
                 networks = list(map(int, args.get('networks').split(',')))
            except ValueError:
                abort(400, "invalid field: networks")
            loc['stations'] = list(filter(lambda x: x['network']['id'] in networks, loc['stations']))
        if args.get('connectors'):
            try:
                connectors = list(map(int, args.get('connectors').split(',')))
            except ValueError:
                abort(400, "invalid field: connectors")
            loc['stations'] = list(filter(lambda x: any([chpt['connector']['id'] in connectors for chpt in x['chargePoints']]), loc['stations']))
        if not loc['stations']:
            continue

        res.append(loc)
    return res

@ns.route("/<int:id>")
@ns.response(404, 'location not found')
@ns.param('id', 'location id')
class LocationService(Resource):
    @ns.doc('get location by id')
    @ns.marshal_with(location_model)
    def get(self, id):
        loc = Location.objects(id=id).first()
        if not loc:
            abort(404, "location not found")
        return loc


@ns.route("/nearby")
class LocationNearbyService(Resource):
    @ns.doc('ge nearby locations')
    @ns.marshal_list_with(location_model)
    @ns.expect(nearby_parser, validate=True)
    def get(self):
        args = nearby_parser.parse_args()
        locs = Location.objects(geoLocation__near=[args['lng'], args['lat']],
                                geoLocation__max_distance=args['radius'])

        return filter_locations(locs, args, args.get('count'))


@ns.route("/region")
class LocationRegionService(Resource):
    @ns.doc('ge locations within a region')
    @ns.marshal_list_with(location_model)
    @ns.expect(region_parser, validate=True)
    def get(self):
        args = region_parser.parse_args()
        lat_lu = args['latitude'] + args['latitudeDelta']/2.0
        lng_lu = args['longitude'] - args['longitudeDelta']/2.0
        lat_rb = args['latitude'] - args['latitudeDelta']/2.0
        lng_rb = args['longitude'] + args['longitudeDelta'] / 2.0

        if not all([ -180.0 < x < 180.0 for x in [lng_lu, lng_rb]]):
            abort(400, "invalid longitude")
        if not all([ -90.0 < x < 90.0 for x in [lat_lu, lat_rb]]):
            abort(400, "invalid latitude")

        locs = Location.objects(geoLocation__geo_within_box=[(lng_lu, lat_lu), (lng_rb, lat_rb)])

        return filter_locations(locs, args, args.get('count'))
