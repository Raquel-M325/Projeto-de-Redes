class Painel:
    def mostrar_cliente(self, id_cliente, armazenamento):
        for id_cliente, cliente in armazenamento: #tá incompleto
            print(f"ID: {id_cliente}")
            print(f"Memória: {id_cliente}") #precisa chamar os outros depois, só é a base da ideia
            print(f"CPU: {id_cliente}")
            print(f"Disco: {id_cliente}")
            print(f"Rede: {id_cliente}")
            print(f"Sistema: {id_cliente}")
