import socket
import os
from typing import List
import zlib
from typing import Tuple
import random
import string

class UDPServer(object):

   def __init__(self, host: str, port: int, window_size: int) -> None:
      self.host = host
      self.port = port
      self.window_size = window_size
      self.max_payload_size = 1024

      self.password = ''
      self.server = None

   def init_server(self, bind = False) -> None:
      """
      Method to init the UDP server and bind in the port and host
      """
      self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      if bind:
         self.server.bind((self.host, self.port))
         letters = string.ascii_lowercase
         self.password = ''.join(random.choice(letters) for i in range(8))
         print(self.password)

      print(f"Server started on {self.host}:{self.port}")
   
   def read_file(self, file_name) -> List:
      """
      Method to read the file requested by the client.

      Returns:
         List: A list with the chunks of 1024 size.
      """
      file_chunks = []

      with open(file_name, "rb") as file:
         while True:
               chunk = file.read(self.max_payload_size)
               if not chunk:
                  break
               file_chunks.append(chunk)
      return file_chunks
   
   def checksum_calculator(self, data: bytes) -> int:
      """
      Método para realzação do cáculo do checksum.

      Args:
          data (bytes): Dados, ou payload, sob os quais o checksum será calculado.

      Returns:
          int: checksum.
      """
      checksum = zlib.crc32(data)
      return checksum
   
   def make_header(self, num_seq: int, checksum: int) -> bytes:
      """
      Método para estruturação do cabeçalho utilizado. Será construído de 
      forma que os 4 primeiros bytes são para o número de sequência
      e os 4 bytes porteriores são para o checksum.

      Args:
          num_seq (int): Número de sequência do pacote que será enviado.
          checksum (int): Valor do checksum

      Returns:
          bytes: Bytes com os valores do numéro de sequência, seguido pelo checksum
      """
      if type(num_seq) is not bytes:
         num_seq = num_seq.to_bytes(4, byteorder='big')
      if type(checksum) is not bytes:
         checksum = checksum.to_bytes(4, byteorder='big')
      
      return num_seq + checksum
   
   def unpack_packet(self, packet: bytes) -> Tuple[int, int, bytes]:
      """
      Método para desempacotamento do pacote de dados.

      Args:
          packet (bytes): Pacote de dados recebido da janela deslizante.

      Returns:
          Tuple[int, int, bytes]: Tupla com os valores de número de sequência, checksum
          e o payload 
      """
      num_seq = int.from_bytes(packet[:4], byteorder='big')
      checksum = int.from_bytes(packet[4:8], byteorder='big')
      data = packet[8:]
      return (num_seq, checksum, data)

   
   def send_packet(self, packet, address):
      self.server.sendto(packet, address)

   def receive_packet(self):
      packet, address = self.server.recvfrom(self.max_payload_size)
      return packet, address

   def send_file(self, file_path: str, addr):
      """
      Método genérico para envio de arquivos, este método pode ser utilizando tanto pelo
      lado do servidor, quanto pelo lado do cliente.

      Args:
          file_path (str): Caminho de dstino para leitura do arquivo que será enviado.
          addr (_type_): _description_
      """
      data_packets = self.read_file(file_path)
      BASE = 0
      
      while BASE < len(data_packets) -1: 
            
         chunk_window = data_packets[BASE:BASE+self.window_size]
         
         for i, data in enumerate(chunk_window):
            num_seq = (BASE + i)
            checksum = self.checksum_calculator(data)
            header = self.make_header(num_seq, checksum)
            packet = header + data
            self.send_packet(packet, addr)

         packet, address = self.receive_packet()
         num_seq, checksum, data = self.unpack_packet(packet)
         BASE = num_seq

      data = "EOF".encode()
      checksum = self.checksum_calculator(data)
      header = self.make_header(0, checksum)
      packet = header + data

      self.server.sendto(packet, addr)
      print("File Sent !!")

   def store_file(self, file_path: str, addr):   
      """
      Método genérico para recebimento de arquivos, tanto pelo lado do servidor,
      quanto do lado do cliente.

      Args:
          file_path (str): Caminho para onde será salvo o arquivo
          addr (_type_): _description_
      """
      BASE = 0
      buffer = {}
      
      while True:
         packet, address = self.receive_packet()
         num_seq, true_checksum, data = self.unpack_packet(packet)

         if data.decode() == "EOF":
            print("File received!")
            break

         if num_seq == BASE:
            buffer[num_seq] = data
            checksum = self.checksum_calculator(data)
            ack_packet = BASE.to_bytes(4, byteorder='big')
            self.send_packet(ack_packet, address)
            BASE += 1   
            
         elif BASE > 0:
            ack_packet = (BASE-1).to_bytes(4, byteorder='big')
            self.send_packet(ack_packet, address)
                  
      with open(file_path, "wb") as f:
         buffer = dict(sorted(buffer.items()))
         buffer = list(buffer.values())
         f.writelines(buffer)

   def list_files(self, addr):
      """
      Método para listagem de todos os arquivos txt.

      Args:
          addr (_type_): _description_
      """
      files = os.listdir('files')
      message = '\n'.join(files)
      self.server.sendto(message.encode(), addr)
      print("List transferred")
            
if __name__ == "__main__":
    udp_server = UDPServer("127.0.0.1", 8080, window_size=2)
    udp_server.init_server(True)
    udp_server.process_requisition()