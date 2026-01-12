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
            return platform.system()
        
        except: 
            return "Desconhecido, não foi encontrado"
                

    def pegou_rede(self):
        informacoes = []
        se_tem_portas = psutil.net_if_addrs()
        esta_aberto_ou_nao = psutil.net_if_stats()

        for nome_da_porta, enderecos in se_tem_portas.items():
            info = {
                "interface" : nome_da_porta,
                "status" : "DOWN",
                "tipo" : "Desconhecido",
                "ips" : []
            }

            if nome_da_porta in esta_aberto_ou_nao and esta_aberto_ou_nao[nome_da_porta].isup: #se está aberto, ele muda o status
                info["status"] = "UP"

            nome = nome_da_porta.lower()
            if "lo" in nome:
                info["tipo"] = "loopback"

            elif "wi" in nome or "wlan" in nome:
                info["tipo"] = "wifi"

            else:
                info["tipo"] = "ethernet"

            for endereco in enderecos:
                if endereco.family == socket.AF_INET: #para cada endereço que encontro, guardo o ip se é Ipv4 ou Ipv6 familiar por exemplo 
                    info["ips"].append(endereco.address)

            informacoes.append(info)
        
        return informacoes


    def coletou_tudo(self):
        return {
            "CPU": self.pegou_cpu(),
            "Disco": self.pegou_disco(),
            "Memória": self.pegou_memoria(),
            "Rede": self.pegou_rede(),
            "Sistema": self.pegou_sistema()
        }
        