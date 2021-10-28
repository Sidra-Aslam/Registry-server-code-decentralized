import requests
import json

# orinal server will be called from this will to get sensor ids
# authentication token/secret key
secret = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiU1lTVEVNX1JFQURFUiIsImV4cCI6MTY1MDAwNzkxNSwic3ViIjoibWljaGFlbC5tcmlzc2FAaW5ub3JlbmV3LmV1In0.SjUiT_WJU_iT-RLsJs4lwtobSuaeXjIc-5zgZlIe1pA'
# auth token header
headers = {'X-Auth-Token': secret}

# Obtain list of all senssors details


def get_sensor_list():
    # call sensor api to display all sensors
    resp = requests.get(
        'http://129.192.68.219:80/api-gateway/v2/api/sensors/', headers=headers)
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
                'href': 'sensors/'+sensor['id'],
                'type': 'get'
            }
            links.append(link)

        # return links
        return links
    else:
        # print error details
        print("HTTP %i - %s, Message %s" %
              (resp.status_code, resp.reason, resp.text))
        return None


# To obtain sensor data based on link (link is a sensor's id)
def get_link_data(link):
    # call api based on provided link
    resp = requests.get(
        'http://129.192.68.219:80/api-gateway/v2/api/'+link, headers=headers)
    if resp.ok:
        print(20 * "-")
        print("Response from link ", link)
        sensor_data = resp.json()
        
        return sensor_data
    else:
        # print error details
        print("HTTP %i - %s, Message %s" %
              (resp.status_code, resp.reason, resp.text))
        return None
