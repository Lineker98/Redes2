from modulo2.comunication import UDPServer
import os

if __name__ == "__main__":
   udp_server = UDPServer("127.0.0.1", 8080, window_size=2)
   udp_server.init_server()

   while True:
      print("Escolha uma das opções")
      print("1 - Listar os arquivos")
      print("2 - Receber os arquivos")
      print("3 - Enviar arquivo")
      choice = input()

      if choice == '1':
         message = 'LIST'
         udp_server.server.sendto(
            message.encode(),
            (udp_server.host, udp_server.port)
         )
         
         data, addr = udp_server.server.recvfrom(1024)
         print(data.decode())
         
      elif choice == '2':
         file_name = input("Entre com o nome do arquivo: ")
         addr = (udp_server.host, udp_server.port)

         udp_server.server.sendto(f"REQUEST:{file_name}".encode(), addr)
         udp_server.store_file(file_name, addr)

      elif choice == '3':
         file_name = input("Entre com o nome do arquivo: ")
         password = input("Entre com a senha do servidor: ")

         udp_server.server.sendto(
            f"STORE:{file_name}*{password}".encode(), 
            (udp_server.host, udp_server.port)
         )
         
         udp_server.send_file(file_name,(udp_server.host, udp_server.port))

      else:
         print("opção inválida, tente novamente")

      print("\n\nClique enter para continuar")
      input()
      os.system("clear")