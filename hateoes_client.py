import requests
import json

# authentication token/secret key
secret = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiU1lTVEVNX1JFQURFUiIsImV4cCI6MTY1MDAwNzkxNSwic3ViIjoibWljaGFlbC5tcmlzc2FAaW5ub3JlbmV3LmV1In0.SjUiT_WJU_iT-RLsJs4lwtobSuaeXjIc-5zgZlIe1pA'
# auth token header
headers = {'X-Auth-Token': secret}
    
#Obtain list of all senssors details
def sensors_api():
    # call sensor api to display all sensors
    resp = requests.get('http://129.192.68.219:80/api-gateway/v2/api/sensors/', headers=headers)
    if resp.ok:
        print("Sensors api response")
        sensors = resp.json()
        print(json.dumps(sensors, indent=4))
    else:
        # print error details
        print("HTTP %i - %s, Message %s" % (resp.status_code, resp.reason, resp.text))

# To obtain sensor data and ask sensor id from user to get data from API/sensor
def read_sensor_data():
    sensor_id = ''
    while len(sensor_id) == 0:
        sensor_id = input("Enter sensor ID to read data: ")

    # call sensor api with sensor id to read data from spacific sensor
    resp = requests.get('http://129.192.68.219:80/api-gateway/v2/api/sensors/'+sensor_id, headers=headers)
    if resp.ok:
        print(20 * "-")
        print("Response from sensor id ",sensor_id)
        sensors = resp.json()
        # print sensor data
        print(json.dumps(sensors, indent=4))
        
    else:
        # print error details
        print("HTTP %i - %s, Message %s" % (resp.status_code, resp.reason, resp.text))


# call sensors api to display all sensors
sensors_api()

# read data from sensor by sensor id
read_sensor_data()