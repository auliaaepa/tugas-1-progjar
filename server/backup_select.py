import socket
import select
import sys
import os

# initialize socket object with AF_INET as address family and SOCK_STREAM as socket type
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# validating address passed to bind() must allow reuse of local address
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind to the given address
HOST = str(sys.argv[1])
PORT = int(sys.argv[2])
server_address = (HOST, PORT)
server_socket.bind(server_address)

# accept connections from 5 clients
server_socket.listen(5)

# list to store accepted client
input_socket = [server_socket]

try:
    while True:
        # get read, write, and exception list from select
        read_list, write_list, exception_list = select.select(input_socket, [], [])
        
        for sock in read_list:
            # accept client and add it to the accepted client list
            if sock == server_socket:
                client_socket, client_address = server_socket.accept()
                input_socket.append(client_socket)
                print("Accepted client:", client_address)
            # handle receiving message and sending file
            else:
                try:
                    message = sock.recv(1024).decode("utf-8")
                    splited_message = message.split()
                    command, filename = splited_message[0], splited_message[1]
                    splited_filename = filename.split(".")
                    name, ext = splited_filename[0], splited_filename[1]
                    
                    filepath = "dataset/" + filename
                    # print(message); print(command); print(filename); print(name); print(ext)
                    
                    if message:
                        if command == "unduh":
                            if os.path.exists(filepath): 
                                success_msg = "Start sending file..."
                                sock.send(success_msg.encode("utf-8"))
                                print("Send to client :", sock.getpeername(), success_msg.encode("utf-8"))
                                
                                sock.send(filename.encode("utf-8"))
                                sock.send(str(os.path.getsize(filepath)).encode("utf-8"))

                                if ext == "html" or ext == "txt": 
                                    with open(filepath, 'rb') as file:
                                        content = file.read()
                                        sock.sendall(content)
                                        print(filename, "sent")
                                        file.close()
                                elif ext in ["jpg", "jpeg", "png", "gif", "mp4", "mp3"]:
                                    with open(filepath, 'rb') as file:
                                        content = file.read()
                                        sock.sendall(content)
                                        print(filename, "sent")
                                        file.close()
                            else:
                                error_msg = "File not found\n"
                                sock.send(error_msg.encode("utf-8"))
                                print("Send to client :", sock.getpeername(), error_msg.encode("utf-8"))                           
                        else:
                            error_msg = "Unknown command\n"
                            sock.send(error_msg.encode("utf-8"))
                            print("Send to client :", sock.getpeername(), error_msg.encode("utf-8"))
                    else:                    
                        sock.close()
                        input_socket.remove(sock)
                
                except IndexError:
                    error_msg = "Unknown command\n"
                    sock.send(error_msg.encode("utf-8"))
                    print("Send to client :", sock.getpeername(), error_msg.encode("utf-8"))
                
                except FileNotFoundError:
                    error_msg = "File not found\n"
                    sock.send(error_msg.encode("utf-8"))
                    print("Send to client :", sock.getpeername(), error_msg.encode("utf-8"))

except KeyboardInterrupt:        
    server_socket.close()
    sys.exit(0)