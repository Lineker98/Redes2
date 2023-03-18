import socket
import os
from typing import List

class UDPServer(object):

   def __init__(self, host: str, port: int, window_size: int, file_name: str) -> None:
      self.host = host
      self.port = port
      self.window_size = window_size
      self.file_name = file_name
      self.file_size = os.stat(file_name).st_size
      self.server = None

   def read_file(self, file_name) -> List:
      """
      Method to read the file requested by the client.

      Returns:
         List: A list with the chunks of 1024 size.
      """
      file_chunks = []
      file_size = os.stat(file_name).st_size

      with open(file_name, "rb") as file:
         while True:
               chunk = file.read(1024)
               if not chunk:
                  break
               file_chunks.append(chunk)

      print(f"File '{file_name}' of size {file_size} bytes loaded into memory in {len(file_chunks)} chunks")
      return file_chunks
   
   def init_server(self) -> None:
      """
      Method to init the UDP server and bind in the port and host
      """
      self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      self.server.bind((self.host, self.port))
      print(f"Server started on {self.host}:{self.port}")
   

   def process_requisition(self):
      """
      Main method to send the file chunks to the client.
      """

      while True:
         data, addr = self.server.recvfrom(1024)
         if "REQUEST" in data.decode():
               file_name = 'files/' + data.decode().split(':')[-1]
               chunks = self.read_file(file_name)
   
               for i in range(0, len(chunks), self.window_size):
                  chunk_window = chunks[i:i+self.window_size]
                  for chunk in chunk_window:
                     self.server.sendto(chunk, addr)

                  if i+self.window_size >= len(chunks):
                     self.server.sendto("EOF".encode(), addr)
                     print("File transferred")
                     break
         elif data.decode() == "LIST":
            self.list_files(addr)
   
   def list_files(self, addr):
      files = os.listdir('files')
      message = '\n'.join(files)
      self.server.sendto(message.encode(), addr)
      self.wait_ack()
      print("List transferred")
   
   def wait_ack(self):
      data = ''.encode()
      while data.decode() != 'ACK':
         data, addr = self.server.recvfrom(1024)
      self.server.sendto(data, addr)
            
if __name__ == "__main__":
    udp_server = UDPServer("127.0.0.1", 8080, window_size=16, file_name="teste.txt")
    udp_server.init_server()
    udp_server.process_requisition()