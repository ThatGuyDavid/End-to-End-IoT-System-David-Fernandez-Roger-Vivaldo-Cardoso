import socket
import sys

# Used to handle user input that does not result in an integer.
def validate():
    while True:
        try:
            userInput = int(input())
            return userInput
        except ValueError:
            print("The number entered is not an integer.")

# This portion stimulates how the server is set up
print("How do you want to set up the server?")
print("Enter 1 for local host")
print("Enter 2 for manual set up")
user = validate()

while (user != 1) and (user != 2):
    print("Enter 1 for local host")
    print("Enter 2 for to manually enter IP and port")
    user = validate()

if user == 1:
    serverIP = 'localhost'
    serverPort = 1024

else:
    serverIP = input("Enter the desired address for this server: ")
    print("Enter the desired port number for this server: ")
    serverPort = validate()

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

while True:
    # Receives client message (up to 2048 bytes), and decodes the data into a string.
    myData = int(incomingSocket.recv(2048).decode('utf-8'))
    print("Performing query for option", myData)

    

    # Send a response back to client, encoding it in bytes.
    # incomingSocket.send(bytes(str("Message received! Modified message: " + myData.upper()), encoding='utf-8'))
    # incomingSocket.send(bytes(str(myData.upper()), encoding='utf-8'))

# Closes socket connection
incomingSocket.close()


