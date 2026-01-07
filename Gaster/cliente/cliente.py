import socker

class Cliente:
    def __init__(self, id_cliente, porta):
        self.id_cliente = id_cliente
        self.socker = socker.socker(socker.AF_INET, socket.SOCK_STREAM)
        self.porta_servidor = porta

    def 