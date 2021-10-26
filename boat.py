from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('', methods=['POST','GET'])
def boats_get_post():
    content = request.get_json()
    if request.method == 'POST':
        if "name" in content and "type" in content and "length" in content:
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(new_boat)
            return str(new_boat.key.id)
        elif request.method == 'GET':
            query = client.query(kind=constants.boats)
            q_limit = int(request.args.get('limit', '2'))
            q_offset = int(request.args.get('offset', '0'))
            l_iterator = query.fetch(limit= q_limit, offset=q_offset)
            pages = l_iterator.pages
            results = list(next(pages))
            if l_iterator.next_page_token:
                next_offset = q_offset + q_limit
                next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
            else:
                next_url = None
            for e in results:
                e["id"] = e.key.id
            output = {"boats": results}
            if next_url:
                output["next"] = next_url
            return json.dumps(output)
        else:
            return 'Method not recogonized'

@bp.route('/<id>', methods=['PUT','DELETE'])
def boats_put_delete(id):
    if request.method == 'PUT':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        boat.update({"name": content["name"], "description": content["description"],
          "price": content["price"]})
        client.put(boat)
        return ('',200)
    elif request.method == 'DELETE':
        key = client.key(constants.boats, int(id))
        client.delete(key)
        return ('',200)
    else:
        return 'Method not recogonized'

@bp.route('/<lid>/guests/<gid>', methods=['PUT','DELETE'])
def add_delete_reservation(lid,gid):
    if request.method == 'PUT':
        boat_key = client.key(constants.boats, int(lid))
        boat = client.get(key=boat_key)
        guest_key = client.key(constants.guests, int(gid))
        guest = client.get(key=guest_key)
        if 'guests' in boat.keys():
            boat['guests'].append(guest.id)
        else:
            boat['guests'] = [guest.id]
        client.put(boat)
        return('',200)
    if request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(lid))
        boat = client.get(key=boat_key)
        if 'guests' in boat.keys():
            boat['guests'].remove(int(gid))
            client.put(boat)
        return('',200)

@bp.route('/<id>/guests', methods=['GET'])
def get_reservations(id):
    boat_key = client.key(constants.boats, int(id))
    boat = client.get(key=boat_key)
    guest_list  = []
    if 'guests' in boat.keys():
        for gid in boat['guests']:
            guest_key = client.key(constants.guests, int(gid))
            guest_list.append(guest_key)
        return json.dumps(client.get_multi(guest_list))
    else:
        return json.dumps([])
