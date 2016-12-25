from socket import *
from sys import argv

BYTE_SIZE = 1024

from http.server import BaseHTTPRequestHandler, HTTPServer

# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

  # GET
  def do_GET(self):
        # Send response status code
        self.send_response(200)

        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()

        # Send message back to client
        message = "opo iki Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return

def run():
  print('starting server...')

  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8081)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')
  httpd.serve_forever()


class DataSocket:

    def __init__(self, hostname, port):
        self.port = port
        self.hostname = hostname
        self.socket = None

    def connect(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.hostname, self.port))
        return True

    def send_to_server(self, filename):
        file_obj = open(filename, 'rb')
        self.socket.sendfile(file_obj)
        file_obj.close()
        return True

    def get_from_server(self, filename):
        file_obj = open(filename, 'wb')
        while 1:
            data = self.socket.recv(BYTE_SIZE)
            if data == b'':
                break
            file_obj.write(data)
        file_obj.close()
        return True

    def close(self):
        self.socket.close()


class Main:

    def __init__(self, hostname='localhost', port_a=1234, port_b=1235):
        self.hostname = hostname
        self.port = port_a
        self.data_socket = DataSocket(hostname, port_b)
        self.conn_socket = None

    def init_app(self):
        print('application is ready')

        while 1:
            try:
                self.process_input()
            except KeyboardInterrupt:
                self.conn_socket.close()
            except Exception:
                self.conn_socket.close()
                raise Exception
    
    def create_socket(self):
        self.conn_socket = socket(AF_INET, SOCK_STREAM)
        self.conn_socket.connect((self.hostname, self.port))

    def process_input(self):
        inp = input()
        args = inp.split()
        cmd = args[0].upper()
        self.create_socket()
        if cmd == "LIST":
            self.get_list()
        elif cmd == "RETR":
            self.retrieve(args[1])
        elif cmd == "STOR":
            self.send(args[1])
        self.conn_socket.close()

    def get_list(self):
        data = b''
        self.conn_socket.send(b'LIST')
        empty = True
        while 1:
            retrieve_data = self.conn_socket.recv(BYTE_SIZE)
            if retrieve_data == b'':
                break
            else:
                empty = False
            data += retrieve_data
        if empty:
            print("the server is empty")
        else:   
            print(data.decode('utf-8'))

    def retrieve(self, filename):
        self.conn_socket.send(bytes("RETR " + filename, 'utf-8'))
        resp = self.conn_socket.recv(BYTE_SIZE)
        try:
            print(resp)
            if resp.split()[0] != b'125':
                raise OSError(resp)
            print('transferring data...')
            if self.data_socket.connect():
                self.data_socket.get_from_server(filename)
            self.data_socket.close()
            print("data is successfully retrieved")
        except OSError as e:
            print("failed to retrieve "+filename+" from server, "+str(e))

    def send(self, filename):
        self.conn_socket.send(bytes("STOR " + filename, 'utf-8'))
        resp = self.conn_socket.recv(BYTE_SIZE)

        try:
            if resp.split()[0] != b'125':
                raise OSError
            if self.data_socket.connect():
                self.data_socket.send_to_server(filename)
            self.data_socket.close()
            print("data is successfully sent")
        except OSError:
            print("failed to store "+filename+" to server")

print("asyu")

if __name__ == "__main__":
    print("kwkw")
    argv.pop(0)
    print("HAHAHA")
    run()

    # main = Main(*argv)
    # main.init_app()
