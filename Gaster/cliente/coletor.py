import os
import platform
import socket

class Coletor:
    def pegou_cpu(self):
        try:
            return os.cpu_count()
        except: 
            return None

    def pegou_disco(self):
        try:
            if platform.system() == "Windows":

            else: #caso for Linux

        except: #não achar nenhum
            return None
        
    def pegou_memoria(self):
        try:

        except: 
            return None

    def pegou_sistema(self):
        try:

        except: 
            return "Desconhecido, não foi encontrado"
                

    def pegou_rede(self):
        try:

        except: 


    def coletou_tudo(self):
        return {
            "CPU": self.pegou_cpu(),
            "Disco": self.pegou_disco(),
            "Memória": self.pegou_memoria(),
            "Rede": self.pegou_rede(),
            "Sistema": self.pegou_sistema()
        }
        