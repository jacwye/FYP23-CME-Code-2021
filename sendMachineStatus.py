from python_graphql_client import GraphqlClient

client = GraphqlClient(endpoint='http://localhost:5001/cms-uoa/us-central1/graph')

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

online_devices = []
## Change the path of the devicelist file accordingly
device_list_file = open("Engine/devicelist.txt", "r")
lines = device_list_file.readlines()
for line in lines:
    online_devices.append(line.strip("\n"))
print("ONLINE DEVICES")
print(online_devices)

data = client.execute(query=get_machines_query)
print('DATA')
print(data['data'])
print('MACHINES')
machines = data['data']['machines']
for machine in machines:
    print(machine['name'])
    if machine['name'] in online_devices:
        mutation_response = client.execute(query=update_machine_mutation, variables={"id": machine["id"], "input": {
            "operatingStatus": "Online"
        }})
        print(mutation_response)
    else:
        mutation_response = client.execute(query=update_machine_mutation, variables={"id": machine["id"], "input": {
            "operatingStatus": "Offline"
        }})
        print(mutation_response)


