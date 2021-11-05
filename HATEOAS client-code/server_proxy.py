import requests
import json
from flask import Flask, request, jsonify

# create flask app object
app = Flask(__name__)

# Obtain list of all senssors details
# endpoint to return sensor list from actual server
@app.route('/sensor_list', methods=['GET'])
def get_sensor_list():
    # return error if secret is not available in url
    if 'secret' not in request.args:
        return 'Secret key not found', 400

    # get secret value from url arguments
    secret = request.args['secret']

    # auth token header
    headers = {'X-Auth-Token': secret}

    # call actual sensor api to display all sensors
    resp = requests.get('http://129.192.68.219:80/api-gateway/v2/api/sensors/', headers=headers)
    if resp.ok:
        print("Sensors api response")
        sensors = resp.json()
        # links object
        links = []
        # iterate all sensors and create link
        for sensor in sensors:
            link = {
                'sensorName': sensor['name'],
                'sensorType': sensor['sensorType'],
                'href': '/sensor_data?id='+sensor['id'],
                'type': 'get'
            }
            links.append(link)

        # return links
        return jsonify(links)
    else:
        # actual server failed so return error text and code
        return resp.text, resp.status_code


# To obtain sensor data based on link (link is a sensor's id)
# endpoint to return sensor data from actual server
@app.route('/sensor_data', methods=['GET'])
def get_link_data():

    # return error if secret or sensor id is not available in url
    if 'secret' not in request.args:
        return 'Secret key not found', 400
    elif 'id' not in request.args:
        return 'Sensor id not found', 400
    
    # get secret key and id from url arguments
    secret = request.args['secret']
    id = request.args['id']

    # auth token header
    headers = {'X-Auth-Token': secret}

    # call api based on provided link
    resp = requests.get(
        'http://129.192.68.219:80/api-gateway/v2/api/sensors/'+id, headers=headers)
    if resp.ok:
        sensor_data = resp.json()
        # return sensor data to client file
        return jsonify(sensor_data)
    else:
        # actual server failed so return error text and code
        return resp.text, resp.status_code


if __name__ == '__main__':
    app.run(debug=False, port=8888, host='127.0.0.1')
