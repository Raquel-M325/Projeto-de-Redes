from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import datetime
import base64

class Seguranca:
    def __init__(self):
        self.chave = get_random_bytes(16)
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

    # Auditoria
    def auditar(self, acao, usuario, detalhes=""):
        linha = f"{datetime.datetime.now()} | {usuario} | {acao} | {detalhes}\n"
        linha_bytes = linha.encode("utf-8")
        with open(self.arquivo_auditoria, "ab") as f:
            f.write(base64.b64encode(linha_bytes) + b"\n")
        print(f"[AUDITORIA] {linha.strip()}")

    # Lê auditoria legível
    def ler_auditoria(self):
        try:
            with open(self.arquivo_auditoria, "rb") as f:
                print("\n=== LOGS DE AUDITORIA ===")
                for linha in f:
                    print(base64.b64decode(linha).decode("utf-8").strip())
        except FileNotFoundError:
            print("Arquivo de auditoria não encontrado.")
