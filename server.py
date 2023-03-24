from modulo.comunication import UDPServer
import os

if __name__ == "__main__":
    udp_server = UDPServer("127.0.0.1", 8080, window_size=2)
    udp_server.init_server(True)

    while True:
      data, addr = udp_server.server.recvfrom(1024)

      if "REQUEST" in data.decode():
         file_name = os.path.join("files", data.decode().split(':')[-1])
         udp_server.send_file(file_name,addr)
      
      elif data.decode() == "LIST":
         udp_server.list_files(addr)
      
      elif 'STORE' in data.decode():
         file_list = data.decode().split('*')
         password = file_list[-1]
         file_path = 'files/' + file_list[0].split(':')[-1]

         data.decode().split('*')[-1]
         if udp_server.password == password:
            udp_server.send_packet("ACK".encode(), addr)
            udp_server.store_file(file_path, addr)
         else:
            udp_server.send_packet("ERROR".encode(), addr)