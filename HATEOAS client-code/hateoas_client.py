import json
import requests

secret = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiU1lTVEVNX1JFQURFUiIsImV4cCI6MTY1MDAwNzkxNSwic3ViIjoibWljaGFlbC5tcmlzc2FAaW5ub3JlbmV3LmV1In0.SjUiT_WJU_iT-RLsJs4lwtobSuaeXjIc-5zgZlIe1pA'

# variable to store all sensor links return from server_proxy
links = []

proxy_server_endpoint = 'http://127.0.0.1:8888'

#Obtain list of all senssors details
def get_sensor_list():
    global links

    # call proxy server using endpoint to get all sensors from actual server and return links
    resp = requests.get(proxy_server_endpoint+'/sensor_list?secret='+secret)
    if resp.ok:
        links = resp.json()
        # iterate links to print link and number
        for link in links:
            # print link number
            print('link number',links.index(link))
            # print link detail (sensorName, sensorType, href, type)
            print(json.dumps(link, indent=4))
    else:
        # proxy server failed to get sensor list
        print(resp.text)

# method to call get_link_data from server_proxy.py file
def get_link_data():
    # ask link number to get data
    link_number = ''
    while len(link_number) == 0 or int(link_number) >= len(links):
        link_number = input("Enter link number to get data: ")
    
    link = links[int(link_number)]

    # print link detail (sensorName, sensorType, href, type)
    print('sending request for link',json.dumps(link, indent=4))
    
    # call proxy server's '/sensor_data' endpoint to get sensor data for provided link/href
    resp = requests.get(proxy_server_endpoint+link['href']+'&secret='+secret)
    
    if resp.ok:
        link_data = resp.json()
        print('Sensor data returned: ')
        # print link response/data
        print(json.dumps(link_data, indent=4))
    else:
        # proxy server failed to get data so display error message
        print(resp.text)

if __name__ == '__main__':
    # get all sensors
    get_sensor_list()
    
    # iterate links and get data
    if links is not None and len(links)>0:
        # run infinite loop (so that user can query link data any number of times)
        while True:
            get_link_data()