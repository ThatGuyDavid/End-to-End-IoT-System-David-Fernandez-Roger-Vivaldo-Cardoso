from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import socket
import sys

#Load the .env
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
    metadata = db["IoT_metadata"]
    # The collection with regards to virtualized data from the devices and sensors
    virtual = db["IoT_virtual"]
    # Parameter for the search located in Metadata
    location: str = "Kitchen"
    # Parameters of event type for the search located in Metadata
    event_types = ["Moisture Monitoring", "Temperature Monitoring"]
    # Database query on the metadata collection for devices that fit the {Location:Kitchen, Eventypes: Moisture, Temperature}
    device = metadata.find_one({
        "eventTypes": {"$in": event_types},
        "customAttributes.additionalMetadata.Location": location,
    })

    # Get the Devices_Id to query over the vrtualized data
    device_id: str = device["assetUid"]

    # Calculate the timestamp for 3 hours ago
    current_time = datetime.now(tz=timezone.utc)
    three_hours_ago = current_time - timedelta(hours=3)

    # Convert the datetime to a Unix timestamp
    three_hours_ago_unix = int(three_hours_ago.timestamp())

    # Gather every data input of the specified Device that contains a moisture reading and also is within the last 3 hours
    results = virtual.find({
    "$expr": {
        "$gte": [{"$toLong": "$payload.timestamp"}, three_hours_ago_unix]  # Convert to integer for comparison
    },
    "payload.parent_asset_uid": device_id,
    "payload.Moisture Meter - Fridge 1": {"$exists": True}})
    
    # Aggregate the values read from the moisture meter for the data points into a singlular list
    humidities = [float(result["payload"].get("Moisture Meter - Fridge 1")) for result in results]
    # Calculate the relative humidity of the Fridge given the data points of the last 3 hours
    relative_humidity = sum(humidities) / len(humidities)

    # Return a message of the resulatant of the calculations from the queries for the user
    message = f"\nThe average moisture in the kitchen fridge over 3 hours is {relative_humidity:.2f}% (RH%)\n\n"
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
    # Set the serverIp and serverPort tto the arguements
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
            # Calculate the average water consumption per cycle in my smart dishwasher
            continue
        else:
            # Calculate who has consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)
            continue
        

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
            tcp_server(serverIP,serverPort)
            break

        else:
            serverIP: str = input("Enter the desired address for this server: ")
            print("Enter the desired port number for this server: ")
            serverPort: int = validate()
            tcp_server(serverIP,serverPort)
            break
