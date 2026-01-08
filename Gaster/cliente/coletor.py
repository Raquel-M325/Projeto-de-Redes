import os
import platform
import socket
import psutil

class Coletor:
    def pegou_cpu(self):
        try:
            return os.cpu_count()
        except: 
            return None

    def pegou_disco(self):
        try:
            disco = psutil.disk_usage("/")
            return round(disco.free / (1024 ** 3), 2) #quero em GB

        except: #não achar nenhum
            return None
        
    def pegou_memoria(self):
        try:
            memoria = psutil.virtual_memory()
            return round(memoria.available / (1024 ** 2), 2) #quero em MB
        except: 
            return None

    def pegou_sistema(self):
        try:
            
        
        except: 
            return "Desconhecido, não foi encontrado"
                

    def pegou_rede(self):
        rede = []
        nome_rede = socket.gethostname()

        


    def coletou_tudo(self):
        return {
            "CPU": self.pegou_cpu(),
            "Disco": self.pegou_disco(),
            "Memória": self.pegou_memoria(),
            "Rede": self.pegou_rede(),
            "Sistema": self.pegou_sistema()
        }
        