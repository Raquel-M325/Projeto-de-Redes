# Projeto-de-Redes

PROJETO BIMESTRAL – REDES DE COMPUTADORES

## 1. Objetivo
Construir um sistema cliente/servidor para inventário e monitoramento de computadores em rede, com descoberta automática, coleta de métricas, consolidação de dados e ação remota por meio de comandos administrativos.

## 2. Funcionalidades

### 2.1 Coleta por Cliente
- [x] Quantidade de processadores / núcleos  
- [x] Memória RAM livre  
- [x] Espaço em disco livre  
- [x] IPs das interfaces de rede (status UP/DOWN e tipo)  
- [x] Identificação do sistema operacional  

### 2.2 Servidor / Consolidação
- [x] Dashboard em terminal com lista de clientes  
- [x] Identificação de clientes online e offline (timeout de hello)  
- [x] Detalhamento de cliente selecionado  
- [x] Exportação de relatórios em CSV ou JSON  

## 3. Requisitos Principais
- [x] Arquitetura Cliente/Servidor  
- [x] Descoberta automática de clientes na LAN  
- [x] Comunicação utilizando sockets TCP e UDP  
- [x] Código organizado seguindo o paradigma de Orientação a Objetos  

## 4. Segurança
- [ ] Comunicação segura com criptografia ponta a ponta  
- [ ] Mecanismos de integridade das mensagens  
- [ ] Autenticação com controle de acesso por perfil  
- [x] Auditoria no servidor (registro de ações com data e hora)  


## 5. Bônus
- [x] Controle remoto do mouse do cliente  
- [x] Controle remoto do teclado do cliente  

## Considerações Finais
O projeto atende aos requisitos funcionais e arquiteturais propostos, incluindo comunicação em rede, descoberta automática, coleta de métricas e ações remotas.  
Os requisitos de segurança encontram-se parcialmente atendidos, ficando como ponto de melhoria futura.
