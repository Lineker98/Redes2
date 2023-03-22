import socket

# Configuração do socket
host = 'localhost'
port = 8888
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Definição da janela de envio e recebimento
WINDOW_SIZE = 4
BASE = 0
NEXT_SEQ_NUM = 0

# Definição do tamanho máximo de dados a serem enviados em cada pacote
MAX_DATA_SIZE = 1024

# Função para enviar pacotes
def send_packet(packet):
   client.sendto(packet, (host, port))

# Função para receber ACKs
def receive_ack():
   ack_packet, address = client.recvfrom(MAX_DATA_SIZE)
   ack = int.from_bytes(ack_packet, byteorder='big')
   return ack

while True:
   message = input('Enter message to send: ')

   data_packets = [message[i:i+MAX_DATA_SIZE] for i in range(0, len(message), MAX_DATA_SIZE)]

   for i, data in enumerate(data_packets):
      seq_num_bytes = NEXT_SEQ_NUM.to_bytes(4, byteorder='big')
      packet = seq_num_bytes + data.encode()

      send_packet(packet)

      ack_received = False
      while not ack_received:
         ack = receive_ack()

         if ack == NEXT_SEQ_NUM:
            BASE = NEXT_SEQ_NUM
            NEXT_SEQ_NUM += 1

            if NEXT_SEQ_NUM - BASE == WINDOW_SIZE:
               BASE = NEXT_SEQ_NUM - WINDOW_SIZE

            ack_received = True
         else:
            send_packet(packet)

   print('Message sent successfully!')