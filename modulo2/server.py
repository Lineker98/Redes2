import socket

# Configuração do socket
host = 'localhost'
port = 8888
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((host, port))


WINDOW_SIZE = 4
BASE = 0
NEXT_SEQ_NUM = 0
MAX_DATA_SIZE = 1024

def send_packet(packet, address):
   server.sendto(packet, address)

def receive_packet():
   packet, address = server.recvfrom(MAX_DATA_SIZE)
   return packet, address

while True:
   packet, address = receive_packet()

   seq_num = int.from_bytes(packet[:4], byteorder='big')
   data = packet[4:]

   if seq_num == NEXT_SEQ_NUM:
      ack_packet = NEXT_SEQ_NUM.to_bytes(4, byteorder='big')
      send_packet(ack_packet, address)

      BASE = NEXT_SEQ_NUM
      NEXT_SEQ_NUM += 1

      print(f'Received data: {data.decode()}')

      if NEXT_SEQ_NUM - BASE == WINDOW_SIZE:
         BASE = NEXT_SEQ_NUM - WINDOW_SIZE
   else:
      ack_packet = BASE.to_bytes(4, byteorder='big')
      send_packet(ack_packet, address)