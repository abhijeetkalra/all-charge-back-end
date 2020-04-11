import datetime
from mongoengine import Document, fields


class Network(Document):
    id = fields.IntField(required=True, primary_key=True)
    name = fields.StringField(required=True, max_length=200)
    phone = fields.StringField()
    url = fields.StringField()
    image = fields.StringField()
    created_at = fields.DateTimeField()
    modified_at = fields.DateTimeField(default=datetime.datetime.utcnow())


class Connector(Document):
    id = fields.IntField(required=True, primary_key=True)
    name = fields.StringField(required=True, max_length=200)
    image = fields.URLField(required=True)
    created_at = fields.DateTimeField()
    modified_at = fields.DateTimeField(default=datetime.datetime.utcnow())


class ChargePoint(Document):
    meta = {
        "indexes": [
            'stationId',
            'networkId'
        ]
    }
    id = fields.IntField(required=True, primary_key=True)
    # 0 = Unknown
    # 1 = Available
    # 2 = InUse
    # 3 = Offline
    # 4 = Under Repair
    networkId = fields.IntField(required=True)
    stationId = fields.IntField(required=True)
    available = fields.IntField(required=True)
    connector = fields.ReferenceField(Connector)
    kilowatts = fields.IntField()
    created_at = fields.DateTimeField()
    modified_at = fields.DateTimeField(default=datetime.datetime.utcnow())

class ChargeStation(Document):
    meta = {
        "indexes": [
            'network',
            'locationId',
        ]
    }
    id = fields.IntField(required=True, primary_key=True)
    network = fields.ReferenceField(Network)
    locationId = fields.IntField(required=True)
    name = fields.StringField(required=True, max_length=200)

    #0 = Unknown
    #1 = Free
    #2 = Fee
    cost = fields.IntField()
    cost_description = fields.StringField(max_length=1000)
    address = fields.StringField(max_length=300)
    available = fields.IntField(required=True)
    hours = fields.StringField(max_length=400)
    geoLocation = fields.PointField(auto_index=True)
    score = fields.FloatField(min_value=0, max_value=10.0, required=True)
    images = fields.ListField(fields.URLField())
    chargePoints = fields.ListField(fields.ReferenceField(ChargePoint))
    created_at = fields.DateTimeField()
    modified_at = fields.DateTimeField(default=datetime.datetime.utcnow())


class Location(Document):
    meta = {
        "indexes": [
        ]
    }

    id = fields.IntField(required=True, primary_key=True)
    address = fields.StringField(required=True, max_length=300)
    name = fields.StringField(required=True, max_length=200)
    description = fields.StringField(max_length=8192)
    phone = fields.StringField(max_length=20)
    poi_name = fields.StringField(max_length=30)
    parking_type_name = fields.StringField(max_length=20)
    cost_description = fields.StringField(max_length=1024)
    open247 = fields.BooleanField()
    amenities = fields.ListField(fields.StringField())
    stations = fields.ListField(fields.ReferenceField(ChargeStation))
    hours = fields.StringField(max_length=2048)
    score = fields.FloatField(min_value=0.0, max_value=10.0)
    photos = fields.ListField(fields.URLField())
    geoLocation = fields.PointField(auto_index=True)
    created_at = fields.DateTimeField()
    modified_at = fields.DateTimeField(default=datetime.datetime.utcnow())

