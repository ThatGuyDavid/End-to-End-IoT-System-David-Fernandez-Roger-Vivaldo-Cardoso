# End-to-End-IoT-System-David-Fernandez-Roger-Vivaldo-Cardoso
This repository contains the implementation of an end-to-end IoT system developed as part of CECS 327 - Intro to Networking and Distributed Systems. The project integrates TCP client/server communication, a database, and IoT sensor data to process user queries efficiently.


Below is a step-by-step guide to run and use the provided TCPServer.py and TCPClient.py applications:

Prerequisites
Make sure you have Python 3 installed on your machine.
Ensure both TCPServer.py and TCPClient.py files are in the same directory or that you know their file paths.

Running the Server
Open a terminal or command prompt and navigate to the directory where TCPServer.py is located.

Start the server by running
python3 TCPServer.py

Server Menu Interaction:

After the server starts, it will present you with a menu of options.
Press 2 to select the option that allows you to provide a custom IP address and port.
For example, you might see something like this:

markdown
Copy code
1. local host settings
2. Manually enter IP and port
...
Your choice: _
Type 2 and hit Enter.

When prompted for the IP address, enter the IP address on which you want the server to listen.
For a local setup, you can often use 127.0.0.1 or localhost.
Then when prompted for the port, enter a port number (e.g., 5000).
For example:


Enter the desrired IP Address: 127.0.0.1
Enter the desired Port Number: 5000
After this, the server should start listening for incoming connections.

Verify the Server is Running:

There will be a message showing a connection to the server to verify its on.

Running the Client
Open another terminal or command prompt (keep the first one with the server running).

Start the client 
python3 TCPClient.py

Client Menu Interaction:

After starting the client, a similar menu might appear.
Press 2 to be prompted to enter the server’s IP and port you configured on the server.
For example:

How would you like to simulate connection?
Enter 1 for local host
Enter 2 for to manually enter IP and port
...
Your choice:
Type 2 and hit Enter.

Enter the Server IP and Port in the Client:

When prompted, enter the same IP and port you used when setting up the server.
For example:


Using the Client’s Query Menu:

After successfully connecting, the client should present you with a UI menu of available queries or actions.
Navigate through the client’s menu as instructed by the on-screen prompts. Each choice will send a request to the server, and you’ll see corresponding responses in the client console.

What is the average moisture of my fridge over the past three hours?
What is the average water consumption per cycle in my dishwasher?
Which device consumed more electricity among my three IoT devices?

Tips and Troubleshooting
Connection Issues:
If the client can’t connect to the server, make sure:

Both are running on the same machine (if using localhost or 127.0.0.1).
The port number is the same on both server and client.
The server is already up and listening before you run the client.
Firewall/Network Constraints:
If running on different machines on a network, ensure that:

The server’s machine firewall allows inbound connections on the chosen port.
The client has network access to the server’s IP and port.
Server or Client Crashes: If an error occurs, check the terminal output for Python exception messages, verify that the server has not exited, and ensure no other application is using the chosen port.

By following these instructions, you should be able to set custom IP and port settings for your server, connect to it from the client, and then navigate through the client’s UI to issue queries and receive responses.
