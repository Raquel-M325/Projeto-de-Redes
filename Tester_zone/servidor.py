import socket
import threading
import time
from pynput import keyboard
from seguranca import Seguranca
import datetime

BROADCAST_PORT = 50000

# -------------------------
# CLIENTE
# -------------------------
class ClientInfo:
    def __init__(self, ip, tcp_port):
        self.ip = ip
        self.tcp_port = tcp_port
        self.last_seen = time.time()
        self.last_msg = ""
        self.mac = None
        self.seguranca = Seguranca()
        self.autenticado = False  # controle de login

    def update(self, msg):
        self.last_msg = msg
        self.last_seen = time.time()

    def __repr__(self):
        age = round(time.time() - self.last_seen, 1)
        return f"{self.ip}:{self.tcp_port} | MAC={self.mac} | ÚltimaMsg='{self.last_msg}' | {age}s atrás"


# -------------------------
# SERVIDOR
# -------------------------
class DiscoveryServer:
    def __init__(self):
        self.clients = {}  # chave: (ip, tcp_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", BROADCAST_PORT))
        self.log_file = "auditoria.log"

    # -------------------------
    # AUDITORIA
    # -------------------------
    def log_acao(self, acao, key):
        ip, port = key
        with open(self.log_file, "a") as f:
            f.write(f"{datetime.datetime.now()} | {acao} | Cliente: {ip}:{port}\n")

    # -------------------------
    # ESCUTA BROADCASTS
    # -------------------------
    def listen_broadcasts(self):
        print(f"[Servidor] Ouvindo broadcasts na porta {BROADCAST_PORT}...")
        while True:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode()
            ip = addr[0]

            print(f"[Broadcast de {ip}] {msg}")

            if msg.startswith("DISCOVER_REQUEST"):
                tcp_port = int(msg.split("=")[1])
                key = (ip, tcp_port)

                if key not in self.clients:
                    self.clients[key] = ClientInfo(ip, tcp_port)
                    print(f"[Novo cliente] {ip}:{tcp_port}")
                    self.log_acao("Cliente registrado", key)

                self.clients[key].update(msg)
                self.sock.sendto("DISCOVER_RESPONSE".encode(), addr)

    # -------------------------
    # SOLICITA MAC via TCP
    # -------------------------
    def ask_mac_tcp(self, key):
        if key not in self.clients:
            print("Cliente não encontrado!")
            return

        client = self.clients[key]

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((client.ip, client.tcp_port))

            # LOGIN
            sock.send(b"LOGIN;admin;1234\n")
            resp = sock.recv(1024)
            if client.seguranca.descriptar(resp) != "LOGIN_OK":
                print(f"[Servidor] Cliente {key} não autenticou")
                self.log_acao("Falha autenticação", key)
                sock.close()
                return
            client.autenticado = True
            self.log_acao("Cliente autenticado", key)

            # Solicita MAC
            sock.send(client.seguranca.encriptar("GET_MAC"))
            resp_mac = sock.recv(1024)
            mac = client.seguranca.descriptar(resp_mac)
            client.mac = mac
            print(f"[MAC recebido] {key} => {mac}")
            self.log_acao("Solicitou MAC", key)

            sock.close()
        except Exception as e:
            print(f"Erro ao conectar via TCP: {e}")
            self.log_acao(f"Erro conexão: {e}", key)

    # -------------------------
    # CONTROLE REMOTO DE TECLADO
    # -------------------------
    def control_keyboard(self, key):
        if key not in self.clients:
            print("Cliente não encontrado!")
            return

        client = self.clients[key]
        print(f"[Servidor] Conectando ao cliente {key} para controle de teclado")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((client.ip, client.tcp_port))

            # LOGIN
            sock.send(b"LOGIN;admin;1234\n")
            resp = sock.recv(1024)
            if client.seguranca.descriptar(resp) != "LOGIN_OK":
                print(f"[Servidor] Cliente {key} não autenticou")
                sock.close()
                return

            sock.send(client.seguranca.encriptar("KEYBOARD_START"))

            def on_press(k):
                try:
                    msg = f"KEY;DOWN;{k.char}\n"
                except AttributeError:
                    msg = f"KEY;DOWN;{k}\n"
                sock.send(client.seguranca.encriptar(msg))

            def on_release(k):
                try:
                    msg = f"KEY;UP;{k.char}\n"
                except AttributeError:
                    msg = f"KEY;UP;{k}\n"
                sock.send(client.seguranca.encriptar(msg))
                if k == keyboard.Key.esc:
                    sock.send(client.seguranca.encriptar("KEYBOARD_STOP"))
                    sock.send(client.seguranca.encriptar("SESSION_END"))
                    return False

            print(">>> Controle de teclado ativo (ESC para sair)")
            listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            listener.start()
            listener.join()

            sock.close()
            print("[Servidor] Sessão de teclado encerrada")
            self.log_acao("Controle de teclado encerrado", key)

        except Exception as e:
            print(f"Erro no controle de teclado: {e}")
            self.log_acao(f"Erro teclado: {e}", key)

    # -------------------------
    # MENU INTERATIVO
    # -------------------------
    def menu(self):
        while True:
            print("\n=== MENU SERVIDOR ===")
            print("1 - Listar clientes")
            print("2 - Solicitar MAC de um cliente")
            print("3 - Solicitar MAC de todos os clientes")
            print("4 - Controlar teclado de um cliente")
            print("0 - Sair")
            op = input("> ")

            match op:
                case "1":
                    print("\n--- CLIENTES ---")
                    for key, info in self.clients.items():
                        print(f"{key} -> {info}")
                case "2":
                    ip = input("Digite o IP: ")
                    port = int(input("Digite a porta TCP do cliente: "))
                    self.ask_mac_tcp((ip, port))
                case "3":
                    for key in self.clients:
                        self.ask_mac_tcp(key)
                case "4":
                    ip = input("Digite o IP do cliente: ")
                    port = int(input("Digite a porta TCP do cliente: "))
                    self.control_keyboard((ip, port))
                case "0":
                    print("Saindo...")
                    exit()
                case _:
                    print("Opção inválida!")

    # -------------------------
    # START
    # -------------------------
    def start(self):
        threading.Thread(target=self.listen_broadcasts, daemon=True).start()
        self.menu()


if __name__ == "__main__":
    DiscoveryServer().start()
