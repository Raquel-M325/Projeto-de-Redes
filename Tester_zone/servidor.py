import socket
import threading
import time
from pynput import keyboard, mouse
import struct
from seguranca import Seguranca

BROADCAST_PORT = 50000

class ClientInfo:
    def __init__(self, ip, tcp_port):
        self.ip = ip
        self.tcp_port = tcp_port
        self.last_seen = time.time()
        self.last_msg = ""
        self.mac = None
        self.usuario = None

    def update(self, msg):
        self.last_msg = msg
        self.last_seen = time.time()

    def __repr__(self):
        age = round(time.time() - self.last_seen, 1)
        return f"{self.ip}:{self.tcp_port} | MAC={self.mac} | Usuario={self.usuario} | UltimaMsg='{self.last_msg}' | {age}s atrás"

class DiscoveryServer:
    def __init__(self):
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", BROADCAST_PORT))
        self.seguranca = Seguranca()

    # -----------------------------------------------------------
    # Funções de envio/recebimento seguro
    # -----------------------------------------------------------
    def send_encrypted(self, sock, mensagem: str):
        dados = self.seguranca.encriptar(mensagem)
        sock.sendall(struct.pack(">I", len(dados)) + dados)

    def recv_encrypted(self, sock) -> str:
        raw_len = sock.recv(4)
        if len(raw_len) < 4:
            raise ConnectionError("Conexão encerrada ou dados incompletos")
        msg_len = struct.unpack(">I", raw_len)[0]
        dados = b""
        while len(dados) < msg_len:
            chunk = sock.recv(msg_len - len(dados))
            if not chunk:
                raise ConnectionError("Conexão encerrada antes de receber todos os bytes")
            dados += chunk
        return self.seguranca.descriptar(dados)

    # -----------------------------------------------------------
    # Escuta broadcasts UDP
    # -----------------------------------------------------------
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
                self.clients[key].update(msg)
                self.sock.sendto("DISCOVER_RESPONSE".encode(), addr)

    # -----------------------------------------------------------
    # Conecta TCP e autentica
    # -----------------------------------------------------------
    def connect_and_auth(self, key):
        if key not in self.clients:
            print("Cliente não encontrado!")
            return None
        ip, port = key
        client = self.clients[key]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            # Recebe LOGIN_REQUEST
            if self.recv_encrypted(sock) != "LOGIN_REQUEST":
                sock.close()
                return None
            usuario = input(f"Digite usuário para {ip}:{port}: ")
            senha = input(f"Digite senha para {usuario}: ")
            self.send_encrypted(sock, f"{usuario};{senha}")
            status = self.recv_encrypted(sock)
            if status != "LOGIN_SUCCESS":
                print("Autenticação falhou")
                sock.close()
                return None
            client.usuario = usuario
            self.seguranca.auditar("LOGIN", usuario, f"Cliente {ip}:{port}")
            return sock
        except Exception as e:
            print(f"Erro ao conectar e autenticar: {e}")
            return None

    # -----------------------------------------------------------
    # Solicitar MAC
    # -----------------------------------------------------------
    def ask_mac_tcp(self, key):
        sock = self.connect_and_auth(key)
        if not sock:
            return
        try:
            self.send_encrypted(sock, "GET_MAC")
            resp = self.recv_encrypted(sock)
            if resp.startswith("MAC_ADDRESS;"):
                mac = resp.split(";")[1]
                self.clients[key].mac = mac
                self.seguranca.auditar("GET_MAC", self.clients[key].usuario, f"MAC: {mac}")
                print(f"[MAC recebido] {key} => {mac}")
        finally:
            sock.close()

    # -----------------------------------------------------------
    # Controle teclado
    # -----------------------------------------------------------
    def control_keyboard(self, key):
        sock = self.connect_and_auth(key)
        if not sock:
            return
        print(f"[Servidor] Controle de teclado para {key}")
        self.send_encrypted(sock, "KEYBOARD_START")

        def on_press(k):
            try:
                msg = f"KEY;DOWN;{k.char}"
            except AttributeError:
                msg = f"KEY;DOWN;{k}"
            self.send_encrypted(sock, msg)

        def on_release(k):
            try:
                msg = f"KEY;UP;{k.char}"
            except AttributeError:
                msg = f"KEY;UP;{k}"
            self.send_encrypted(sock, msg)
            if k == keyboard.Key.esc:
                self.send_encrypted(sock, "KEYBOARD_STOP")
                self.send_encrypted(sock, "SESSION_END")
                return False

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()
        sock.close()
        print("[Servidor] Sessão de teclado encerrada")

    # -----------------------------------------------------------
    # Controle mouse
    # -----------------------------------------------------------
    def control_mousepad(self, key):
        sock = self.connect_and_auth(key)
        if not sock:
            return
        print(f"[Servidor] Controle de mouse para {key}")
        self.send_encrypted(sock, "MOUSE_START")
        last_pos = None

        def on_move(x, y):
            nonlocal last_pos
            if last_pos is None:
                last_pos = (x, y)
                return
            dx = x - last_pos[0]
            dy = y - last_pos[1]
            last_pos = (x, y)
            self.send_encrypted(sock, f"MOUSE;MOVE;{dx};{dy}")

        def on_click(x, y, button, pressed):
            if button == mouse.Button.middle and pressed:
                self.send_encrypted(sock, "MOUSE_STOP")
                self.send_encrypted(sock, "SESSION_END")
                return False
            action = "DOWN" if pressed else "UP"
            self.send_encrypted(sock, f"MOUSE;CLICK;{button.name};{action}")

        def on_scroll(x, y, dx, dy):
            self.send_encrypted(sock, f"MOUSE;SCROLL;{dx};{dy}")

        with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()

        sock.close()
        print("[Servidor] Sessão de mouse encerrada")

    # -----------------------------------------------------------
    # Menu
    # -----------------------------------------------------------
    def menu(self):
        while True:
            print("\n=== MENU SERVIDOR ===")
            print("1 - Listar clientes")
            print("2 - Solicitar MAC de um cliente")
            print("3 - Solicitar MAC de todos os clientes")
            print("4 - Controlar teclado de um cliente")
            print("5 - Controlar mouse de um cliente")
            print("0 - Sair")
            op = input("> ")

            match op:
                case "1":
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
                case "5":
                    ip = input("Digite o IP do cliente: ")
                    port = int(input("Digite a porta TCP do cliente: "))
                    self.control_mousepad((ip, port))
                case "0":
                    exit()
                case _:
                    print("Opção inválida!")

    # -----------------------------------------------------------
    # Start
    # -----------------------------------------------------------
    def start(self):
        threading.Thread(target=self.listen_broadcasts, daemon=True).start()
        self.menu()


if __name__ == "__main__":
    DiscoveryServer().start()
