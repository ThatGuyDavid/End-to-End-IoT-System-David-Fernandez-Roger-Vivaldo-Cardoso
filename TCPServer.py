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
