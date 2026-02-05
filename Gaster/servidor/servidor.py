import socket
import json

class Servidor: #não está totalmente completo para responder varios clientes
    def __init__(self, porta, ip):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.porta_servidor = porta
        self.ip_servidor = ip

    def ouvir(self):
        self.socket.bind((self.ip_servidor, self.porta_servidor))
        self.socket.listen()
        print("Ouvindo. . .")

    def responder(self):
        conexao, endereco = self.socket.accept()
        print(f"Peguei o cliente: {endereco}")

        dados = conexao.recv(4096) #quantidade de letras para receber 
        mensagem = json.loads(dados.decode()) #novamente converte byte em texto

        print("Mensagem recebida:")
        print(mensagem)


#---------------------------------------RASCUNHO------------------------------------------------------

    def UDP_envia_broadcast(self):
        self.permissão = sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) #ele permite que a pessoa possa  ter o envio broadcast

        while True:
            

