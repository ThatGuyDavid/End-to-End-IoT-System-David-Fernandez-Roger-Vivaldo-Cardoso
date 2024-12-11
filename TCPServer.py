from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import socket
import sys
import math

# Load the .env
load_dotenv()

# Envirtoment Variables
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

# Global Variables (MongoDb)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]


# Function used to gather data from the database and calculate the current or relatively current - Relative Humidity (Fridge in Kitchen)


def calculate_query_1():
    # The collection with regards to metadata
    metadata_collection = next(
        (name for name in db.list_collection_names() if "metadata" in name), None)
    # The collection with regards to virtualized data from the devices and sensors
    virtual = db[next(
        (name for name in db.list_collection_names() if "virtual" in name), None)]
    # Calculate the timestamp for 3 hours ago
    current_time = datetime.now(tz=timezone.utc)
    three_hours_ago = current_time - timedelta(hours=3)

    # Convert the datetime to a Unix timestamp
    three_hours_ago_unix = int(three_hours_ago.timestamp())

    if metadata_collection is None or virtual is None:
        print("No MetaData and/or Virtual Data collection found")
        return 0
    metadata = db[metadata_collection]
    # Parameter for the search located in Metadata
    location: str = "Kitchen"
    # Parameters of event type for the search located in Metadata
    event_types = ["Moisture Monitoring"]
    # Database query on the metadata collection for devices that fit the {Location:Kitchen, Eventypes: Moisture, Temperature}
    device = metadata.find_one({
        "eventTypes": {"$in": event_types},
        "customAttributes.additionalMetadata.Location": location,
    })
    if device is None:
        return "{Error no device found}"
    device_id: str = device["assetUid"]
    if metadata_collection is None or virtual is None:
        print("No MetaData and/or Virtual Data collection found")
        return 0
    # Gather every data input of the specified Device that contains a moisture reading and also is within the last 3 hours
    results = virtual.find({
        "$expr": {
            # Convert to integer for comparison
            "$gte": [{"$toLong": "$payload.timestamp"}, three_hours_ago_unix]
        },
        "payload.parent_asset_uid": device_id,
        "payload.Moisture Meter - Fridge": {"$exists": True}})
    # Aggregate the values read from the moisture meter for the data points into a singular list
    humidities = [float(result["payload"].get(
        "Moisture Meter - Fridge")) for result in results]
    # Calculate the relative humidity of the Fridge given the data points of the last 3 hours
    if len(humidities) == 0:
        return "{Error no readings}"
    relative_humidity = sum(humidities) / len(humidities)
    print(relative_humidity)

    return round(relative_humidity, 2)


def calculate_query_2():
    # The collection with regards to metadata
    metadata_name = next(
        (name for name in db.list_collection_names() if "metadata" in name), None)

    # The collection with regards to virtualized data from the devices and sensors
    virtual = db[next(
        (name for name in db.list_collection_names() if "virtual" in name), None)]

    # If metadata collection exists
    if metadata_name is None or virtual is None:
        print("No MetaData and/or Virtual Data collection found")
        return 0

    metadata = db[metadata_name]
    event_types = ["Water Consumption Monitoring"]
    # Executes the query
    device = metadata.find_one({
        "eventTypes": {"$in": event_types},
    })

    device_id: str = device["assetUid"]

    documents = virtual.find({"payload.parent_asset_uid": device_id,
                              "payload.Water_consumption_sensor_DW": {"$exists": True}})
    values = 0
    count = 0

    # Loops through each document from the query
    for doc in documents:
        # Accesses the nested field in 'payload'. In case 'payload' does not exist,
        # returns '{}'.
        value = doc.get("payload", {}).get("Water_consumption_sensor_DW") or doc.get(
            "payload", {}).get("Water Consumption Sensor - Dishwasher")

        # If value is not 'NULL', adds itself to values and increments count.
        # Will be used later to find the average
        if value is not None:
            try:
                values += float(value)
                count += 1

            except ValueError:
                print("Problem when attempting to covert a value.")

    # Error handling in case count is 0
    if count > 0:
        average = round(values / math.ceil(count / 60), 2)
        return average
    else:
        print("No MetaData and/or Virtual Data collection found")
        return 0


def calculate_query_3():
    # The collection with regards to metadata
    metadata_name = next(
        (name for name in db.list_collection_names() if "metadata" in name), None)

    # The collection with regards to virtualized data from the devices and sensors
    virtual = db[next(
        (name for name in db.list_collection_names() if "virtual" in name), None)]

    if metadata_name is None or virtual is None:
        print("No MetaData and/or Virtual Data collection found")
        return 0

    metadata = db[metadata_name]
    event_types = ["Electricity Consumption"]
    devices = metadata.find({
        "eventTypes": {"$in": event_types},
    })
    # Store names of Ammeter
    ammeter_sensors = []

    # Total Consumption will be stored in the dictionary with the name and key being device_id
    electricity_data = {}

    for device in devices:
        device_id = device["assetUid"]
        device_name = device["customAttributes"].get(
            "name", f"Device {device_id}")

        # Extract all ammeter sensors for this device
        ammeter_sensors = [
            sensor["customAttributes"]["name"]
            for board in device["customAttributes"].get("children", [])
            for sensor in board.get("customAttributes", {}).get("children", [])
            if sensor.get("customAttributes", {}).get("type") == "SENSOR"
            and "Ammeter" in sensor.get("customAttributes", {}).get("name", "")
        ]

        # If no ammeters found, skip this device
        if not ammeter_sensors:
            continue

        # Sum total consumption across all ammeters for this device
        total_consumption = 0
        for ammeter in ammeter_sensors:
            documents = virtual.find({
                "payload.parent_asset_uid": device_id,
                f"payload.{ammeter}": {"$exists": True}
            })

            for doc in documents:
                try:
                    consumption = float(doc["payload"].get(ammeter, 0))
                    total_consumption += consumption
                except ValueError:
                    print(
                        f"Invalid consumption value for {device_name}: {doc}")

        # Store the total consumption data
        electricity_data[device_id] = {
            "name": device_name,
            "ammeter_names": ammeter_sensors,
            "total_consumption": total_consumption,
        }

    # Determine the device with the highest consumption
    if not electricity_data:
        return "{Error no electricity consumption data found}"

    # Calculate the device with the most total consumption
    max_device = max(electricity_data.items(),
                     key=lambda item: item[1]["total_consumption"])
    # Get the name and total consumption for highest consumption device
    device_name, total_consumption = max_device[1]["name"], max_device[1]["total_consumption"]

    # Set message to be returned to client (device name and total consumption)
    message = (f"{device_name} with {total_consumption:.2f}")

    return message


# Used to handle user input that does not result in an integer.


def validate():
    while True:
        try:
            userInput: int = int(input())
            return userInput
        except ValueError:
            print("The number entered is not an integer.")


# Set up TCP Server (host = ServerIP, port = ServerPort). Arguements passed are the serverIp and serverPort in which the server will be hosted on


def tcp_server(host, port):
    # Set the serverIp and serverPort to the arguements
    serverIP: str = host
    serverPort: int = port
    # Creates a TCP socket!
    # socket.AF_INET is used to work with IPv4 addresses
    # socket.SOCK_STREAM is used to create a TCP type connection
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Error handling if the inputted IP and port number is invalid
    try:
        # Binds the socket to an address and port number
        myTCPSocket.bind((serverIP, serverPort))
    except:
        print("Could not set up server with provided IP and port, terminating.")
        sys.exit()
    # Sever is now listening for connections! The number "5" represents the max # of queued connections
    myTCPSocket.listen(5)
    # Prevent further execution until a client connects
    # Stores the socket object, and the address of the connected client respectively
    incomingSocket, incomingAddress = myTCPSocket.accept()
    print(f"Client Connected Successfully  {incomingAddress}")
    # Test database
    # print(db.list_collection_names())
    while True:
        # Receives client message (up to 1024 bytes), and decodes the data into a string.
        query = int(incomingSocket.recv(1024).decode('utf-8'))
        print(f"Recieved query: {query}")
        if query == 1:
            # Calculate the relative humidity of the Fridge located in the kitchen
            message: str = calculate_query_1()
            incomingSocket.send(bytes(str(message), encoding='utf-8'))
        elif query == 2:
            water_consumption = calculate_query_2()
            incomingSocket.send(str(water_consumption).encode('utf-8'))
        else:
            selection = calculate_query_3()
            incomingSocket.send(str(selection).encode('utf-8'))
        # Send a response back to client, encoding it in bytes.
        # incomingSocket.send(bytes(str("Message received! Modified message: " + myData.upper()), encoding='utf-8'))
        # incomingSocket.send(bytes(str(myData.upper()), encoding='utf-8'))
    # Closes socket connection
    incomingSocket.close()


if __name__ == "__main__":
    # This portion stimulates how the server is set up
    while True:
        print("Enter 1 for local host")
        print("Enter 2 for to manually enter IP and port")
        user: int = validate()
        if user == 1:
            serverIP: str = 'localhost'
            serverPort: int = 1024
            tcp_server(serverIP, serverPort)
            break
        else:
            serverIP: str = input(
                "Enter the desired address for this server: ")
            print("Enter the desired port number for this server: ")
            serverPort: int = validate()
            tcp_server(serverIP, serverPort)
            break
