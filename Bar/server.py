import socket
import select
from API import Api
import pickle
from threading import Thread


IP = socket.gethostbyname(socket.gethostname())
global CONNECTED
CONNECTED = False
def start_server(incoming_message_callback, error_callback):
    Thread(target=launch, args=(incoming_message_callback, error_callback), daemon=True).start()

def launch(incoming_message_callback, *_):# will receive incoming callback and error handle call back
    api = Api()
    print("#"*100)
    print(CONNECTED)
    HEADER_LENGTH = 10

    IP = ""
    PORT = 1234
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()

    sockets_list = [server_socket]

    clients = {}

    print(f'Listening for connections on {IP}:{PORT}...')

    def receive_message(client_socket, connection):
        try:
            message_header = client_socket.recv(HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            if connection:
                global CONNECTED
                data = client_socket.recv(message_length).decode('utf-8')
                CONNECTED = True
                print(CONNECTED)
            else:
                data = pickle.loads(client_socket.recv(message_length))
            return {'header': message_header, 'data': data}
        except:
            # If client close connection violently by crushing app or shut down the connection without closing it before.
            return False


    def build_request(data):
        if data['method'] in dir(Api):
            data['data'] = getattr(api, data['method'])(*data['attributes'])  # to execute the method with the given attributes
            return data

    def send_data(socket, data):
        data = pickle.dumps(data)
        message_header = f"{len(data):<{HEADER_LENGTH}}".encode('utf-8')
        socket.send(message_header+data)
        print('posted: ', data)

    while True:

        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket, True)
                if user is False:
                    continue

                sockets_list.append(client_socket)
                clients[client_socket] = user
                print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data']))
            else:
                message = receive_message(notified_socket, False)
                if message is False:
                    print('Closed connection from: {}'.format(clients[notified_socket]['data']))
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                user = clients[notified_socket]
                print(f'Received message from {user["data"]}: {message["data"]}')
                data_to_post = build_request(message['data'])
                send_data(notified_socket,data_to_post)
        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
