import _thread
import os

from socket import *
from os import listdir, path, makedirs
from sys import argv
from gpiozero import LED
from time import sleep

BUFFER_SIZE = 1024
STORAGE_PATH = './storage/'


class Socket:
	socket = None

	@staticmethod
	def get_socket(port):
		if Socket.socket is None:
			Socket.socket = socket(AF_INET, SOCK_STREAM)
			Socket.socket.bind(('', port))
			Socket.socket.listen(1)
		return Socket.socket


def run_presentation(obj):
	os.system('pkill evince')
	os.system('evince --presentation ' + obj)


class DataSocket:
	def __init__(self, address, port):
		self.address = address
		self.conn_socket, self.incoming_address = (None, None)
		self.socket = Socket.get_socket(port)

	def accept(self):
		self.conn_socket, self.incoming_address = self.socket.accept()
		return self.incoming_address[0] == self.address[0]

	def send_to_client(self, filename):
		file_obj = open(STORAGE_PATH + filename.decode('utf-8'), 'rb')
		self.conn_socket.sendfile(file_obj)
		file_obj.close()
		return True

	def get_from_client(self, filename):
		obj = STORAGE_PATH + filename.decode('utf-8')
		file_obj = open(obj, 'wb')
		while 1:
			data = self.conn_socket.recv(BUFFER_SIZE)
			if data == b'':
				break
			file_obj.write(data)
		file_obj.close()
		_thread.start_new_thread(run_presentation, (obj,))
		return True

	def close(self):
		self.conn_socket.close()


class Main:
	def __init__(self, port_a=1234, port_b=1235):
		self.port_a = int(port_a)
		self.port_b = int(port_b)
		self.socket = None
		self.lampu = 0

	def init_app(self):
		if not path.exists(STORAGE_PATH):
			makedirs(STORAGE_PATH)
		self.create_socket()
		print('The server is ready to receive')

		while 1:
			try:
				self.listen_to_client()
			except (KeyboardInterrupt, Exception) as e:
				self.socket.close()
				Socket.socket.close()
				raise e

	def create_socket(self):
		self.socket = socket(AF_INET, SOCK_STREAM)
		self.socket.bind(('', self.port_a))
		self.socket.listen(1)

	def uripno_lampu(self):
		led0 = LED(27)
		led1 = LED(9)
		led2 = LED(22)
		led3 = LED(10)
		led4 = LED(11)
		led5 = LED(24)
		led6 = LED(17)
		led7 = LED(23)
		counter = 0
		self.lampu = 1
		while self.lampu > 0:
			if counter == 0:
				led7.off()
				led0.on()
			if counter == 1:
				led1.on()
			if counter == 2:
				led2.on()
			if counter == 3:
				led0.off()
				led3.on()
			if counter == 4:
				led1.off()
				led4.on()
			if counter == 5:
				led2.off()
				led5.on()
			if counter == 6:
				led3.off()
				led6.on()
			if counter == 7:
				led4.off()
				led7.on()
			if counter == 8:
				led5.off()
			if counter == 9:
				led6.off()
			if counter == 10:
				led7.off()

			if counter == 10:
				counter = 0
			else:
				counter += 1
			sleep(0.25)

	def handle_client(self, connection, address):
		_thread.start_new_thread(self.uripno_lampu,())
		cmd = connection.recv(BUFFER_SIZE)
		args = cmd.split()
		cmd = args[0].upper() if len(args) > 0 else ""
		if cmd == b"LIST":
			self.get_list(connection)
		elif cmd == b"RETR":
			self.retrieve(connection, address, args[1])
		elif cmd == b"STOR":
			self.send(connection, address, args[1])
		connection.close()
		sleep(7)
		self.lampu = 0

	def listen_to_client(self):
		conn_socket, address = self.socket.accept()
		print("Incoming connection from address ", address[0], ":", address[1])
		_thread.start_new_thread(self.handle_client, (conn_socket, address))

	@staticmethod
	def get_list(conn_socket):
		result = ""
		for file in listdir(STORAGE_PATH):
			result = result + file + "\n"
		conn_socket.send(bytes(result, 'utf-8'))

	def retrieve(self, conn_socket, address, filename):
		try:
			data_socket = DataSocket(address, self.port_b)
			conn_socket.send(b'125 Data connection already open; transfer starting')
			if data_socket.accept():
				data_socket.send_to_client(filename)
			data_socket.close()
		except OSError as e:
			if e.errno == 98:
				conn_socket.send(b'425 Can\'t open data connection')
			else:
				conn_socket.send(bytes(e.errno))

	def send(self, conn_socket, address, filename):
		try:
			data_socket = DataSocket(address, self.port_b)
			conn_socket.send(b'125 Data connection already open; transfer starting')
			if data_socket.accept():
				data_socket.get_from_client(filename)
			data_socket.close()
		except OSError as e:
			if e.errno == 98:
				conn_socket.send(b'425 Can\'t open data connection')
			else:
				conn_socket.send(b'452 Error writing file')


if __name__ == "__main__":
	argv.pop(0)
	main = Main(*argv)
	main.init_app()
