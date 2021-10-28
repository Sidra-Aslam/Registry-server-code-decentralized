import json
import server_proxy

# variable to store all sensor links return from server_proxy
links = []

#Obtain list of all senssors details
def get_sensor_list():
    global links

    # call sensor api from server_proxy.py file to display all links
    links = server_proxy.get_sensor_list()
    if(links is not None):
        # iterate links to print link and number
        for link in links:
            # print link number
            print('link number',links.index(link))
            # print link detail (sensorName, sensorType, href, type)
            print(json.dumps(link, indent=4))


# method to call get_link_data from server_proxy.py file
def get_link_data():
    # ask link number to get data
    link_number = ''
    while len(link_number) == 0:
        link_number = input("Enter link number to get data: ")
    
    link = links[int(link_number)]

    # print link detail (sensorName, sensorType, href, type)
    print('sending request for link',json.dumps(link, indent=4))
    
    # call get_link_data from server_proxy.py file to get data for provided link/href
    link_data = server_proxy.get_link_data(link['href'])
    # print link response/data
    print(json.dumps(link_data, indent=4))


if __name__ == '__main__':
    # get all sensors
    get_sensor_list()
    
    # iterate links and get data
    if links is not None and len(links)>0:
        # run infinite loop (so that user can query link data any number of times)
        while True:
            get_link_data()