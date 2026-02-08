from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import datetime

class Seguranca:
    def __init__(self):
        self.chave = get_random_bytes(16)  
        self.arquivo_auditoria = "auditoria.txt"
        self.usuarios = {
            "admin": "1234",
            "user": "abcd"
        }

    def autenticar(self, usuario, senha):
        if self.usuarios.get(usuario) == senha:
            self.auditar("LOGIN", usuario)
            return True
        else:
            self.auditar("FALHA_LOGIN", usuario)
            return False

    def encriptar(self, mensagem):
        iv = get_random_bytes(16)  # vetor de inicialização
        cipher = AES.new(self.chave, AES.MODE_CFB, iv)
        return iv + cipher.encrypt(mensagem.encode())  # envia IV junto com a mensagem

    def descriptar(self, dados):
        iv = dados[:16]
        cipher = AES.new(self.chave, AES.MODE_CFB, iv)
        return cipher.decrypt(dados[16:]).decode()

    def auditar(self, acao, usuario):
        with open(self.arquivo_auditoria, "a") as f:
            f.write(f"{datetime.datetime.now()} | {usuario} | {acao}\n")
