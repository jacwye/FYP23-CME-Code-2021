from python_graphql_client import GraphqlClient
from datetime import datetime, timezone
import requests
import re

#client = GraphqlClient(endpoint='http://localhost:5001/cms-uoa/us-central1/graph')
client = GraphqlClient(endpoint='https://us-central1-cms-uoa.cloudfunctions.net/graph')


DEFAULT_IMAGE_LINK = "https://firebasestorage.googleapis.com/v0/b/cms-uoa.appspot.com/o/images%2FdefaultImage.png?alt=media&token=a194efe4-c99a-4ba8-a1e4-2afcd229ef48"
## Change the URL to production once ready
INGESTOR_URL = "https://us-central1-cms-uoa.cloudfunctions.net/ingestor"
#INGESTOR_URL = "http://localhost:5001/cms-uoa/us-central1/ingestor"

get_machines_query = """
    query getMachines {
        machines {
            id
            name
            subscribers
            operatingStatus
            notificationStatus
            healthStatus
            image
            sensors {
                id
                name
                healthStatus
            }
        }
    }
"""

create_machine_mutation = """
    mutation createMachine($name: String!, $image: String!) {
        createMachine(name: $name, image: $image) {
            machine {
                id
                name
                notificationStatus
                healthStatus
                operatingStatus
                image
            }
        }
    }
"""

update_machine_mutation = """
    mutation updateMachine($id: ID!, $input: MachineUpdateInput) {
        updateMachine(id: $id, input: $input) {
            machine {
                id
                name
                notificationStatus
                healthStatus
                operatingStatus
                subscribers
                image
            }
        }
    }
"""

create_sensor_mutation = """
    mutation createSensor($input: SensorInput) {
        createSensor(input: $input) {
            sensor {
                id
                name
                healthStatus
                threshold
            }
        }
    }
"""

get_sensor_query = """
    query getSensorById($machineId: ID!, $id: ID!) {
        sensor(machineId: $machineId, id: $id) {
            name
            healthStatus
            threshold
            sensorData {
                timestamp
                value
            }
            latestThresholdBreach
        }
    }
"""

update_sensor_mutation = """
    mutation updateSensor($id: ID!, $machineId: ID!, $input: SensorUpdateInput) {
        updateSensor(id: $id, machineId: $machineId, input: $input) {
            sensor {
                name
                healthStatus
                threshold
                sensorData {
                    timestamp
                    value
                }
                latestThresholdBreach
            }
        }
    }
"""

def check_machine_and_sensor(machine_name, sensor_name, sensor_threshold):
    machine_id = None
    sensor_id = None
    
    machine_found = False
    machine_data = (client.execute(query=get_machines_query))['data']['machines']
    
    for machine in machine_data:
        if machine['name'] == machine_name:
            machine_found = True
            machine_id = machine['id']
            print('MACHINE FOUND')
    
    if not machine_found:
        print('MACHINE NOT FOUND')
        response = client.execute(query=create_machine_mutation, variables={"name": machine_name, "image": DEFAULT_IMAGE_LINK})
        machine_id = response['data']['createMachine']['machine']['id']

    machine_data = (client.execute(query=get_machines_query))['data']['machines']

    for machine in machine_data:
        if machine['name'] == machine_name:
            sensors = machine['sensors']
            sensor_found = False
            for sensor in sensors:
                if sensor['name'] == sensor_name:
                    sensor_found = True
                    sensor_id = sensor['id']
                    check_sensor_threshold(machine_id, sensor_id, sensor_threshold)
                    print("SENSOR FOUND")
                    break
            if not sensor_found:
                print("SENSOR NOT FOUND")
                response = client.execute(query=create_sensor_mutation, variables={"input": {
                    "machineID": machine["id"],
                    "name": sensor_name,
                    "threshold": sensor_threshold
                }})
                sensor_id = response['data']['createSensor']['sensor']['id']
                break
    
    return ([machine_id, sensor_id])


def update_machine_operating_status(machine_id, operating_status):
    mutation_response = client.execute(query=update_machine_mutation, variables={"id": machine_id, "input": {
        "operatingStatus": operating_status
    }})
    print(mutation_response)

def check_sensor_threshold(machine_id, sensor_id, threshold_value):
    current_sensor_threshold = (client.execute(query=get_sensor_query, variables={"machineId": machine_id, "id": sensor_id}))['data']['sensor']['threshold']
    if (current_sensor_threshold != threshold_value):
        mutation_response = client.execute(query=update_sensor_mutation, variables={"id": sensor_id, "machineId": machine_id, "input": {
        "threshold": threshold_value
        }})
        print(mutation_response)

def update_sensor_latest_threshold_breach(machine_id, sensor_id, latestThresholdBreach):
    formattedLatestThresholdBreach = re.sub('[^A-Za-z0-9]+', '', latestThresholdBreach)
    mutation_response = client.execute(query=update_sensor_mutation, variables={"id": sensor_id, "machineId": machine_id, "input": {
        "latestThresholdBreach": formattedLatestThresholdBreach
    }})
    print(mutation_response)

def send_sensor_data(machine_id, sensor_id, rms_value, timestamp):
    data = {
        "timestamp": timestamp,
        "value": rms_value
    }
    url = INGESTOR_URL + "/machine/" + str(machine_id) + "/sensor/" + str(sensor_id)
    print(url)
    response = requests.post(url=url, json=data, headers={
        "content-type": "application/json"
    })
    print(response)

# Uncomment this to test the functions on their own
# if __name__ == '__main__':
    # latest_threshold_breach = re.sub('[^A-Za-z0-9]+', '', datetime.now().astimezone().replace(microsecond=0).isoformat())
    # print(type(latest_threshold_breach))
    # update_sensor_latest_threshold_breach("jq6ZBtUU3137gg07Jijz", "r8WLiEfSSS6ceYb8N6pN", latest_threshold_breach)