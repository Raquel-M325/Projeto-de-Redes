import socket
import threading
import time
from pynput import keyboard, mouse
from seguranca import Seguranca

BROADCAST_PORT = 50000

class ClientInfo:
    def __init__(self, ip, tcp_port):
        self.ip = ip
        self.tcp_port = tcp_port
        self.last_seen = time.time()
        self.last_msg = ""
        self.mac = None

    def update(self, msg):
        self.last_msg = msg
        self.last_seen = time.time()

    def __repr__(self):
        age = round(time.time() - self.last_seen, 1)
        return f"{self.ip}:{self.tcp_port} | MAC={self.mac} | UltimaMsg='{self.last_msg}' | {age}s atrás"

class DiscoveryServer:
    def __init__(self):
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", BROADCAST_PORT))
        self.seguranca = Seguranca()  # Auditoria do servidor

    # ----------------------------------------------------------------
    # ESCUTA BROADCASTS
    # ----------------------------------------------------------------
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
                    self.seguranca.auditar("NOVO_CLIENTE", f"{ip}:{tcp_port}")

                self.clients[key].update(msg)
                self.sock.sendto("DISCOVER_RESPONSE".encode(), addr)

    # ----------------------------------------------------------------
    # SOLICITA MAC via TCP
    # ----------------------------------------------------------------
    def ask_mac_tcp(self, key):
        if key not in self.clients:
            print("Cliente não encontrado!")
            return

        ip, port = key
        print(f"[Servidor] Conectando via TCP em {ip}:{port} ...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(b"GET_MAC\n")
            response = sock.recv(1024).decode().strip()
            sock.close()

            if response.startswith("MAC_ADDRESS;"):
                mac = response.split(";")[1]
                self.clients[key].mac = mac
                self.seguranca.auditar("MAC_RECEBIDO", f"{ip}:{port}", mac)

        except Exception as e:
            print(f"Erro ao conectar via TCP: {e}")

    # ----------------------------------------------------------------
    # CONTROLE REMOTO DE TECLADO
    # ----------------------------------------------------------------
    def control_keyboard(self, key):
        if key not in self.clients:
            print("Cliente não encontrado!")
            return

        ip, port = key
        print(f"[Servidor] Conectando ao cliente {ip}:{port} para controle de teclado")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(b"KEYBOARD_START\n")
            self.seguranca.auditar("TECLADO_INICIADO", f"{ip}:{port}")

            def on_press(k):
                try:
                    msg = f"KEY;DOWN;{k.char}\n"
                except AttributeError:
                    msg = f"KEY;DOWN;{k}\n"
                sock.send(msg.encode())

            def on_release(k):
                try:
                    msg = f"KEY;UP;{k.char}\n"
                except AttributeError:
                    msg = f"KEY;UP;{k}\n"
                sock.send(msg.encode())

                if k == keyboard.Key.esc:
                    sock.send(b"KEYBOARD_STOP\n")
                    sock.send(b"SESSION_END\n")
                    self.seguranca.auditar("TECLADO_FINALIZADO", f"{ip}:{port}")
                    return False

            print(">>> Controle de teclado ativo (ESC para sair)")
            listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            listener.start()
            listener.join()

            sock.close()
            print("[Servidor] Sessão de teclado encerrada")

        except Exception as e:
            print(f"Erro no controle de teclado: {e}")

    # ----------------------------------------------------------------
    # CONTROLE REMOTO DE MOUSE
    # ----------------------------------------------------------------
    def control_mousepad(self, key):
        if key not in self.clients:
            print("Cliente não encontrado!")
            return

        ip, port = key
        print(f"[Servidor] Conectando ao cliente {ip}:{port} para controle de mouse")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(b"MOUSE_START\n")
            self.seguranca.auditar("MOUSE_INICIADO", f"{ip}:{port}")

            last_pos = None

            def on_move(x, y):
                nonlocal last_pos
                if last_pos is None:
                    last_pos = (x, y)
                    return
                dx = x - last_pos[0]
                dy = y - last_pos[1]
                last_pos = (x, y)
                sock.send(f"MOUSE;MOVE;{dx};{dy}\n".encode())

            def on_click(x, y, button, pressed):
                if button == mouse.Button.middle and pressed:
                    sock.send(b"MOUSE_STOP\n")
                    sock.send(b"SESSION_END\n")
                    self.seguranca.auditar("MOUSE_FINALIZADO", f"{ip}:{port}")
                    return False
                action = "DOWN" if pressed else "UP"
                sock.send(f"MOUSE;CLICK;{button.name};{action}\n".encode())

            def on_scroll(x, y, dx, dy):
                sock.send(f"MOUSE;SCROLL;{dx};{dy}\n".encode())

            print(">>> Controle de mouse ativo (BOTÃO DO MEIO para sair)")
            with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
                listener.join()

            sock.close()
            print("[Servidor] Sessão de mouse encerrada")

        except Exception as e:
            print(f"Erro no controle de mouse: {e}")

    # ----------------------------------------------------------------
    # MENU INTERATIVO
    # ----------------------------------------------------------------
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

                case "5":
                    ip = input("Digite o IP do cliente: ")
                    port = int(input("Digite a porta TCP do cliente: "))
                    self.control_mousepad((ip, port))

                case "0":
                    print("Saindo...")
                    exit()

                case _:
                    print("Opção inválida!")

    # ----------------------------------------------------------------
    # START
    # ----------------------------------------------------------------
    def start(self):
        threading.Thread(target=self.listen_broadcasts, daemon=True).start()
        self.menu()


if __name__ == "__main__":
    DiscoveryServer().start()
