import socket
import threading
import random
import time
import uuid
from pynput import keyboard
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
            print(f"[Broadcast enviado] {msg}")
            time.sleep(BROADCAST_DELAY)

            # op = input("> ")
            # match op:

            #     case "0":
            #         exit()

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
            print(f"[TCP] Conexão recebida de {addr}")

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
        print(f"[TCP] Handler ativo para {addr}")

        while True:
            data = conn.recv(1024).decode()
            if not data:
                break

            for line in data.strip().split("\n"):

                if line == "KEYBOARD_START":
                    print("[Teclado remoto ativado]")
                    keyboard_active = True
                    continue

                if line == "KEYBOARD_STOP":
                    print("[Teclado remoto desativado]")
                    keyboard_active = False
                    continue

                if keyboard_active and line.startswith("KEY;"):
                    try:
                        _, action, key = line.split(";", 2)

                        if key.startswith("Key."):
                            k = Key[key.replace("Key.", "")]
                        else:
                            k = key

                        if action == "DOWN":
                            keyboard_ctl.press(k)
                        elif action == "UP":
                            keyboard_ctl.release(k)

                    except Exception as e:
                        print("Erro ao processar tecla:", e)

        conn.close()
        print(f"[TCP] Conexão encerrada {addr}")

    def main_logic(self):
        while self.running:
            time.sleep(5)

    def start(self):
        print(f"[Cliente] TCP_PORT={self.tcp_port}  |  MAC={self.mac}")

        threading.Thread(target=self.send_broadcast, daemon=True).start()
        threading.Thread(target=self.tcp_server, daemon=True).start()

        self.main_logic()


if __name__ == "__main__":
    Client().start()