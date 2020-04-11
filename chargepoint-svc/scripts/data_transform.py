import json
import datetime
import random
from mongoengine import connect
from pymongo import MongoClient

from src.models import *

#connect(db='chargepoint', username='chargepoint', password='Sapvora123')
#src = MongoClient('mongodb://crawler:Sapvora123@127.0.0.1/crawler')['crawler']['location']

connect('chargepoint')
src = MongoClient()['crawler']['location']


amenity_type = {
    1: "Lodging",
    2: "Dining",
    3: "Restrooms",
    4: "EV Parking",
    5: "Valet Parking",
    6: "Park",
    7: "WiFi",
    8: "Shopping",
    9: "Grocery"
}

connector_types = [
    # id, name, image_url
    (1, "US Wall Outlet", "https://assets.plugshare.com/assets/outlets/image03.png"),
    (2, "J-1772", "https://assets.plugshare.com/assets/outlets/image08.png"),
    (3, "CHAdeMO", "https://assets.plugshare.com/assets/outlets/image04.png"),
    (4, "Tesla Roadster", "https://assets.plugshare.com/assets/outlets/image00.png"),
    (5, "NEMA 14-50", "https://assets.plugshare.com/assets/outlets/image10.png"),
    (6, "Tesla", "https://assets.plugshare.com/assets/outlets/image05.png"),
    (7, "Type 2 (Mennekes)", "https://assets.plugshare.com/assets/outlets/image06.png"),
    (8, "Type 3", "https://assets.plugshare.com/assets/outlets/image16.png"),
    (9, "BS1363", "https://assets.plugshare.com/assets/outlets/image09.png"),
    (10, "Europlug", "https://assets.plugshare.com/assets/outlets/image13.png"),
    (11, "UK Commando", "https://assets.plugshare.com/assets/outlets/image12.png"),
    (12, "AS3112", "https://assets.plugshare.com/assets/outlets/image01.png"),
    (13, "SAE Combo DC CCS", "https://assets.plugshare.com/assets/outlets/image02.png"),
    (14, "Three Phase (AU)", "https://assets.plugshare.com/assets/outlets/image14.png"),
    (15, "Caravan Mains Socket", "https://assets.plugshare.com/assets/outlets/image15.png"),
    (16, "China GB/T", "https://assets.plugshare.com/assets/outlets/image06.png"),
    (17, "China GB/T 2", "https://assets.plugshare.com/assets/outlets/image17.png"),

]

TYPE_KWS = [(1, 2), (2, 10), (3, 40), (13, 50)]

def load_raw_locations():
    cnt = 0
    for l in src.find():
        print("[%d]\tInserting location: %d\t  ...  " % (cnt, l['id']), end="")
        if not l.get('address', None):
            continue
        loc = Location(
            id=l['id'],
            address=l['address'],
            amenities=[amenity_type[x['type']] for x in l['amenities']],
            name=l['name'],
            description=l['description'],
            phone=l['phone'],
            poi_name=l['poi_name'],
            parking_type_name=l['parking_type_name'],
            cost_description=l['cost_description'],
            open247=l['open247'],
            hours=l['hours'],
            score=l.get('score', random.randint(4,10)),
            photos=[x['url'] for x in l['photos']],
            geoLocation=(l['longitude'], l['latitude']),
            created_at=datetime.datetime.utcnow()
        )
        stations = []
        for s in l['stations']:
            if not s['network_id'] or not s['name']:
                continue

            if s['network_id'] and not Network.objects(id=s['network_id']).first():
                n = s['network']
                network = Network(
                    id=n['id'],
                    name=n['name'],
                    url=n.get('url', None),
                    image=n.get('image', None),
                    phone=n.get('phone', None),
                    created_at=datetime.datetime.utcnow()
                )
                network.save()

            station = ChargeStation(
                id=s['id'],
                network=Network.objects(id=s['network_id']).first(),
                locationId=s['location_id'],
                name=s['name'],
                cost=s['cost'],
                cost_description=s['cost_description'],
                available=1,
                hours=s['hours'],
                geoLocation=(l['longitude'], l['latitude']),
                score=random.randrange(4, 10),
                address=l['address'],
                images=[random.choice(loc.photos)] if loc.photos else None,
                created_at=datetime.datetime.utcnow(),
            )

            if not station['name']:
                station['name'] = "-".join([station['network']['name'], l['name']])


            chpts = []
            for c in s['outlets']:
                chpt = ChargePoint(
                    id=c['id'],
                    networkId=s['network_id'],
                    stationId=station.id,
                    available=c.get('available', 1) or 1,
                    connector=c['connector'],
                    kilowatts=int(c['kilowatts']) if c['kilowatts'] else None,
                    created_at=datetime.datetime.utcnow()
                )
                chpt.save()
                chpts.append(chpt)
            for i in range(random.randint(3, 10)):
                type = random.choice(TYPE_KWS)
                chpt = ChargePoint(
                    id=int(str(station.id)+"000"+str(i)),
                    networkId=s['network_id'],
                    stationId=station.id,
                    available=random.choice([1,2]),
                    connector=type[0],
                    kilowatts=type[1],
                    created_at=datetime.datetime.utcnow()
                )
                chpt.save()
                chpts.append(chpt)

            station.chargePoints = chpts
            station.save()
            stations.append(station)
        loc.stations = stations
        loc.save()
        print("done")
        cnt += 1

def load_networks():
    raw = """1 ChargePoint 
15 Endesa 
36 ChargeNet 
54 Electrify Canada
2 Blink 
19 EVgo 
37 Recargo 
3 Semaconnect 
22 Lastestasjoner 
41 KSI 
4 GE WattStation 
23 EnelDrive 
45 POLAR 
5 Sun Country 
25 Volta 
46 EVConnect 
6 Circuit Electrique 
26 Greenlots 
47 Electrify America 
7 FLO 
29 OpConnect 
48 Chargefox 
8 Tesla Supercharger
30 Shorepower 
49 BC Hydro EV 
9 Webasto 
33 CarCharging 
50 Irvine Company 
13 Innogy 
34 JNSH 
51 Ionity 
14 Oplaadpalen 
35 Tesla Destination
52 Fastned"""
    for line in raw.split('\n'):
        id, *name = line.strip().split(' ')
        network = Network(id=int(id), name=" ".join(name), created_at=datetime.datetime.utcnow())
        network.save()
    print('done')


def load_connectors():
    for id, name, url in connector_types:
        c = Connector(id=id, name=name, image=url, created_at=datetime.datetime.utcnow())
        c.save()
    print('done with connectors')


if __name__ == '__main__':
    #load_networks()
    load_connectors()
    load_raw_locations()
