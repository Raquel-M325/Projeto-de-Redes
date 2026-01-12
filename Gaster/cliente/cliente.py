import socket
import json
import time
from coletor import Coletor

class Cliente:
    def __init__(self, id_cliente, porta, ip):
        self.id_cliente = id_cliente
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.porta_servidor = porta
        self.ip_servidor = ip
        self.coletor = Coletor()

    def conecta(self):
        self.socket.connect((self.ip_servidor, self.porta_servidor)) #endereço, é obrigatório ter (()) para dizer que é dupla

    def manda_mensagem(self):
        mensagem = {
            "Tipo" : "HELLO",
            "id_do_cliente" : self.id_cliente,
            "Informações" : self.coletor.coletou_tudo(),
            "Tempo" : time.time()

        }

        dados = json.dumps(mensagem).encode() #transformar o texto do dicionário em bytes - dados
        self.socket.send(dados)

