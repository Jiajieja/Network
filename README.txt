##Runing servers and clients
To run the servers, navigate to the source code directory of the server.py and run the command in the terminal: 
Python server.py [port number]
Python client.py [username] [IP address] [port number]

##Command 
//The chat system is in broadcast mode by default (i.e., messages are sent to all online users).
//send to [username] [message] -- Private messages can be sent to specific users
//get file list -- list all files in the server download folder
//download [filename] -- Download the file you want in the server download folder, and the file will be saved in the folder user_name download
//exitchat -- Exit the chat system and disconnect from the server.

##File structre 
server.py
client.py 
server.log
