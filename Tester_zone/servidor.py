import socket
import threading
from pynput import keyboard, mouse
import time

BROADCAST_PORT = 50000

class ClientInfo:
    def __init__(self, ip, tcp_port):
        self.ip = ip
        self.tcp_port = tcp_port
        self.last_seen = time.time()
        self.mac = None

    def update(self):
        self.last_seen = time.time()

    def __repr__(self):
        return f"{self.ip}:{self.tcp_port} | MAC={self.mac}"

class DiscoveryServer:
    def __init__(self):
        self.clients = {}
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", BROADCAST_PORT))

    def listen_broadcasts(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode()
            ip = addr[0]
            if msg.startswith("DISCOVER_REQUEST"):
                tcp_port = int(msg.split("=")[1])
                key = (ip, tcp_port)
                if key not in self.clients:
                    self.clients[key] = ClientInfo(ip, tcp_port)
                self.clients[key].update()
                self.sock.sendto("DISCOVER_RESPONSE".encode(), addr)

    def autenticar_cliente(self, ip, port, usuario, senha):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(f"LOGIN;{usuario};{senha}\n".encode())
            resp = sock.recv(1024).decode().strip()
            sock.close()
            return resp == "LOGIN_OK"
        except:
            return False

    def ask_mac(self, ip, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, port))
            sock.send(b"GET_MAC\n")
            resp = sock.recv(1024).decode().strip()
            sock.close()
            if resp.startswith("MAC_ADDRESS;"):
                return resp.split(";")[1]
        except:
            return None

    def control_keyboard(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.send(b"KEYBOARD_START\n")

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
                return False

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
        listener.join()
        sock.close()

    def control_mouse(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.send(b"MOUSE_START\n")
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
            action = "DOWN" if pressed else "UP"
            sock.send(f"MOUSE;CLICK;{button.name};{action}\n".encode())
            if button == mouse.Button.middle and pressed:
                sock.send(b"MOUSE_STOP\n")
                sock.send(b"SESSION_END\n")
                return False

        def on_scroll(x, y, dx, dy):
            sock.send(f"MOUSE;SCROLL;{dx};{dy}\n".encode())

        with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            listener.join()
        sock.close()

    def menu(self):
        while True:
            print("\n=== MENU SERVIDOR ===")
            print("1 - Listar clientes")
            print("2 - Controlar teclado")
            print("3 - Controlar mouse")
            print("0 - Sair")
            op = input("> ")
            match op:
                case "1":
                    for k, c in self.clients.items():
                        print(f"{k} -> {c}")
                case "2":
                    ip = input("IP: ")
                    port = int(input("Porta: "))
                    self.control_keyboard(ip, port)
                case "3":
                    ip = input("IP: ")
                    port = int(input("Porta: "))
                    self.control_mouse(ip, port)
                case "0":
                    exit()

    def start(self):
        threading.Thread(target=self.listen_broadcasts, daemon=True).start()
        self.menu()

if __name__ == "__main__":
    DiscoveryServer().start()
