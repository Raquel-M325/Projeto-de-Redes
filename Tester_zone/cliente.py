import socket
import threading
import random
import time
import uuid
from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController, Button
import struct
from seguranca import Seguranca

BROADCAST_PORT = 50000
BROADCAST_ADDR = "<broadcast>"
BROADCAST_DELAY = 5

class Client:
    def __init__(self):
        self.tcp_port = random.randint(20000, 40000)
        self.running = True
        self.mac = self.get_local_mac()
        self.seguranca = Seguranca()

    def get_local_mac(self):
        mac_int = uuid.getnode()
        return ":".join(f"{(mac_int >> 8*i) & 0xff:02x}" for i in reversed(range(6)))

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
    # UDP broadcast de descoberta
    # -----------------------------------------------------------
    def send_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            msg = f"DISCOVER_REQUEST;PORT={self.tcp_port}"
            sock.sendto(msg.encode(), (BROADCAST_ADDR, BROADCAST_PORT))
            time.sleep(BROADCAST_DELAY)

    # -----------------------------------------------------------
    # TCP: servidor interno para comandos
    # -----------------------------------------------------------
    def tcp_server(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", self.tcp_port))
        sock.listen(5)
        print(f"[Cliente] Servidor TCP escutando na porta {self.tcp_port}...")

        while self.running:
            conn, addr = sock.accept()
            threading.Thread(
                target=self.handle_tcp_connection,
                args=(conn, addr),
                daemon=True
            ).start()

    # -----------------------------------------------------------
    # Handle do TCP
    # -----------------------------------------------------------
    def handle_tcp_connection(self, conn, addr):
        keyboard_ctl = Controller()
        keyboard_active = False

        mouse_ctl = MouseController()
        mouse_active = False

        try:
            # Autenticação
            self.send_encrypted(conn, "LOGIN_REQUEST")
            login_data = self.recv_encrypted(conn)
            usuario, senha = login_data.split(";", 1)
            if not self.seguranca.autenticar(usuario, senha):
                self.send_encrypted(conn, "LOGIN_FAILED")
                conn.close()
                return
            self.send_encrypted(conn, "LOGIN_SUCCESS")

            while True:
                line = self.recv_encrypted(conn).strip()

                # ---------- MAC ----------
                if line == "GET_MAC":
                    self.send_encrypted(conn, f"MAC_ADDRESS;{self.mac}")
                    continue

                # ---------- Teclado ----------
                if line == "KEYBOARD_START":
                    keyboard_active = True
                    continue
                if line == "KEYBOARD_STOP":
                    keyboard_active = False
                    continue

                # ---------- Mouse ----------
                if line == "MOUSE_START":
                    mouse_active = True
                    continue
                if line == "MOUSE_STOP":
                    mouse_active = False
                    continue

                if line == "SESSION_END":
                    keyboard_active = False
                    mouse_active = False
                    conn.close()
                    return

                # Processa teclado
                if keyboard_active and line.startswith("KEY;"):
                    try:
                        _, action, key = line.split(";", 2)
                        if key.startswith("Key."):
                            k = getattr(Key, key.replace("Key.", ""), None)
                            if not k:
                                continue
                        else:
                            k = key
                        if action == "DOWN":
                            keyboard_ctl.press(k)
                        elif action == "UP":
                            keyboard_ctl.release(k)
                    except Exception:
                        continue

                # Processa mouse
                if mouse_active and line.startswith("MOUSE;"):
                    try:
                        parts = line.split(";")
                        if parts[1] == "MOVE":
                            dx = int(parts[2])
                            dy = int(parts[3])
                            mouse_ctl.move(dx, dy)
                        elif parts[1] == "CLICK":
                            btn = Button.left if parts[2] == "left" else Button.right
                            if parts[3] == "DOWN":
                                mouse_ctl.press(btn)
                            else:
                                mouse_ctl.release(btn)
                        elif parts[1] == "SCROLL":
                            dx = int(parts[2])
                            dy = int(parts[3])
                            mouse_ctl.scroll(dx, dy)
                    except Exception:
                        continue

        except Exception as e:
            print(f"[TCP] Erro na conexão {addr}: {e}")
        finally:
            conn.close()
            print(f"[TCP] Conexão encerrada {addr}")

    # -----------------------------------------------------------
    # Main
    # -----------------------------------------------------------
    def start(self):
        threading.Thread(target=self.send_broadcast, daemon=True).start()
        threading.Thread(target=self.tcp_server, daemon=True).start()
        print(f"[Cliente] TCP_PORT={self.tcp_port} | MAC={self.mac}")
        while self.running:
            time.sleep(5)


if __name__ == "__main__":
    Client().start()
