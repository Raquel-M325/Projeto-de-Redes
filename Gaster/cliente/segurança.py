import secrets
import time

class Seguranca:
    def __init__(self):
        self.tokens = {} #dicionario

    def criar_token(self, id_cliente):
        token = secrets.token_hex(16)

        self.tokens[id_cliente] = { #para cada cliente, terá seu token e tempo criado
            "token": token,
            "criado_em": time.time()
        }

        return token
