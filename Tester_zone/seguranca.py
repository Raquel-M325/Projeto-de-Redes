from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import datetime

class Seguranca:
    def __init__(self):
        self.chave = get_random_bytes(16)  # chave AES aleatória
        self.arquivo_auditoria = "auditoria.txt"
        self.usuarios = {
            "admin": "1234",
            "user": "abcd"
        }

    # Autenticação simples
    def autenticar(self, usuario, senha):
        if self.usuarios.get(usuario) == senha:
            self.auditar("LOGIN", usuario)
            return True
        else:
            self.auditar("FALHA_LOGIN", usuario)
            return False

    # Encripta uma mensagem
    def encriptar(self, mensagem):
        iv = get_random_bytes(16)
        cipher = AES.new(self.chave, AES.MODE_CFB, iv)
        return iv + cipher.encrypt(mensagem.encode())

    # Descripta uma mensagem
    def descriptar(self, dados):
        iv = dados[:16]
        cipher = AES.new(self.chave, AES.MODE_CFB, iv)
        return cipher.decrypt(dados[16:]).decode()

    # Auditoria de ações
    def auditar(self, acao, usuario):
        with open(self.arquivo_auditoria, "a") as f:
            f.write(f"{datetime.datetime.now()} | {usuario} | {acao}\n")
