import socket
import threading
import random
import time
import uuid
from pynput.keyboard import Controller, Key

BROADCAST_PORT = 50000
BROADCAST_ADDR = "<broadcast>"
BROADCAST_DELAY = 5


class Client:
    def __init__(self):
        self.tcp_port = random.randint(20000, 40000)
        self.running = True
        self.mac = self.get_local_mac()

    def get_local_mac(self):
        mac_int = uuid.getnode()
        return ":".join(f"{(mac_int >> 8*i) & 0xff:02x}" for i in reversed(range(6)))

    # -----------------------------------------------------------
    # UDP: broadcast de descoberta
    # -----------------------------------------------------------
    def send_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        while self.running:
            msg = f"DISCOVER_REQUEST;PORT={self.tcp_port}"
            sock.sendto(msg.encode(), (BROADCAST_ADDR, BROADCAST_PORT))
            time.sleep(BROADCAST_DELAY)

    # -----------------------------------------------------------
    # TCP: servidor interno para responder comandos
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

    # --------------------------------------------------------
    # Handle do TCP
    # --------------------------------------------------------
    def handle_tcp_connection(self, conn, addr):
        keyboard_ctl = Controller()
        keyboard_active = False
        buffer = ""
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    break
                buffer += data.decode()
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    # ---------- MAC ----------
                    if line == "GET_MAC":
                        conn.send(f"MAC_ADDRESS;{self.mac}\n".encode())
                        continue

                    # ---------- TECLADO ----------
                    if line == "KEYBOARD_START":
                        keyboard_active = True
                        continue
                    if line == "KEYBOARD_STOP":
                        keyboard_active = False
                        continue
                    if line == "SESSION_END":
                        keyboard_active = False
                        conn.close()
                        return

                    if keyboard_active and line.startswith("KEY;"):
                        try:
                            _, action, key = line.split(";", 2)
                            if key.startswith("Key."):
                                try:
                                    k = getattr(Key, key.replace("Key.", ""))
                                except AttributeError:
                                    continue  # tecla especial desconhecida
                            else:
                                k = key

                            if action == "DOWN":
                                keyboard_ctl.press(k)
                            elif action == "UP":
                                keyboard_ctl.release(k)
                        except Exception as e:
                            print("Erro ao processar tecla:", e)

            except Exception as e:
                print(f"[TCP] Erro na conexão {addr}: {e}")
                break

        conn.close()
        print(f"[TCP] Conexão encerrada {addr}")

    # --------------------------------------------------------
    # Main
    # --------------------------------------------------------
    def start(self):
        threading.Thread(target=self.send_broadcast, daemon=True).start()
        threading.Thread(target=self.tcp_server, daemon=True).start()
        print(f"[Cliente] TCP_PORT={self.tcp_port} | MAC={self.mac}")
        while self.running:
            time.sleep(5)


if __name__ == "__main__":
    Client().start()
