import socket
import os
from typing import List
import zlib
import struct

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
   
   def send_packet(self, packet, address):
      self.server.sendto(packet, address)

   def receive_packet(self):
      packet, address = self.server.recvfrom(self.max_payload_size)
      return packet, address

   def send_file(self, file_path, addr):
      data_packets = self.read_file(file_path)
      print(data_packets)
      BASE = 0
      
      while BASE < len(data_packets) -1: 
            
         chunk_window = data_packets[BASE:BASE+self.window_size]

         for i, data in enumerate(chunk_window):
            seq_num_bytes = (BASE + i).to_bytes(4, byteorder='big')
            packet = seq_num_bytes + data
            self.send_packet(packet, addr)

         packet, address = self.receive_packet()
         ack = int.from_bytes(packet[:4], byteorder='big')
         data = packet[4:]

         print(BASE)
         print(len(data_packets))
         BASE = ack
      
      seq_num_bytes = BASE.to_bytes(4, byteorder='big')
      end_of_file = "EOF"
      full_packet = seq_num_bytes + end_of_file.encode()

      self.server.sendto(full_packet, addr)

   def store_file(self, file_path, addr):   
      BASE = 0
      buffer = {}
      
      while True:
         packet, address = self.receive_packet()

         seq_num = int.from_bytes(packet[:4], byteorder='big')
         data = packet[4:]

         if data.decode() == "EOF":
            print("File received!")
            break

         buffer[seq_num] = data

         if seq_num == BASE:
            ack_packet = BASE.to_bytes(4, byteorder='big')
            self.send_packet(ack_packet, address)
            
            BASE += 1
         
         elif BASE > 0:
            ack_packet = (BASE-1).to_bytes(4, byteorder='big')
            self.send_packet(ack_packet, address)
         
         print(BASE)
         
         
      with open(file_path, "wb") as f:
         print(buffer)     
         buffer = dict(sorted(buffer.items()))
         buffer = list(buffer.values())
         f.writelines(buffer)

   def list_files(self, addr):
      files = os.listdir('files')
      message = '\n'.join(files)
      self.server.sendto(message.encode(), addr)
      print("List transferred")
            
if __name__ == "__main__":
    udp_server = UDPServer("127.0.0.1", 8080, window_size=2)
    udp_server.init_server(True)
    udp_server.process_requisition()