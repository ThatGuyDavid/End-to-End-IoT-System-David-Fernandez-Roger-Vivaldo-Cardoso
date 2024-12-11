import socket
import sys
from wsgiref.simple_server import server_version


# Used to handle user input that does not result in an integer.
def validate():
    while True:
        try:
            userInput = int(input())
            return userInput
        except ValueError:
            print("The number entered is not an integer.")

# This portion allows user to decide how they want to simulate the connection.
print("How would you like to simulate connection?")
print("Enter 1 for local host")
print("Enter 2 for to manually enter IP and port")
user = validate()

while (user != 1) and (user != 2):
    print("Enter 1 for local host")
    print("Enter 2 for to manually enter IP and port")
    user = validate()

if user == 1:
    serverIP = 'localhost'
    serverPort = 1024

else:
    serverIP = input("Enter the server IP address: ")
    print("Enter the server port number: ")
    serverPort = validate()

# Creates a TCP socket!
# socket.AF_INET is used to work with IPv4 addresses
# socket.SOCK_STREAM is used to create a TCP type connection
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Ensures that the user only inputs the correct IP and port number
try:
    # Connects to the server with its IP address and port number
    myTCPSocket.connect((serverIP, serverPort))
except:
    print("Could not connect to server, terminating.")
    sys.exit()



while True:

    # Doesn't allow empty messages to be sent to server
    print("Enter 1,2 or 3 to choose one of the following options:")
    while True:
        # User chooses and option to send to the server.
        print("1) What is the average moisture of my fridge over the past three hours?")
        print("2) What is the average water consumption per cycle in my dishwasher?")
        print("3) Which device consumed more electricity among my three IoT devices?")
        choice = validate()

        if (choice == 1) or (choice == 2) or (choice == 3):
            break

        print("Can not process query at this time, enter 1,2, or 3 to select one of the following:")

    # The choice is encoded into bytes and then sent to the server.
    myTCPSocket.send(bytes(str(choice), encoding='utf-8'))

    # The client receives the servers responses (up to 2048 bytes) and decodes it into a string.
    serverResponse = myTCPSocket.recv(2048).decode('utf-8')
    
    if choice == 1:
        print(f"\nThe average moisture in the kitchen fridge over 3 hours is {serverResponse}% (RH%)\n\n")

    if choice == 2:
        print(f"\nAverage water consumption is about {serverResponse} gallons per cycle.\n\n")

    if choice == 3:
        print(f"\nThe device with the highest total consumption is {serverResponse} units.\n\n")


    print("Do you wish to continue sending messages to this server?")
    print("Enter 1 to continue")
    print("Enter 2 to terminate")
    user2 = validate()

    while (user2 != 1) and (user2 != 2):
        print("Enter 1 to continue")
        print("Enter 2 to terminate")
        user2 = validate()

    if user2 == 2:
        break

# Closes socket once finish.
myTCPSocket.close()
