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
- [ ] Auditoria no servidor (registro de ações com data e hora)  


## 5. Bônus
- [x] Controle remoto do mouse do cliente  
- [x] Controle remoto do teclado do cliente  


## 🔧 Como o sistema foi desenvolvido?

### 🌐 Comunicação Cliente / Servidor
O sistema utiliza uma arquitetura cliente/servidor.  
Os clientes se comunicam com o servidor usando **UDP para descoberta automática** e **TCP para troca de comandos**, garantindo comunicação direta e contínua.


### 📡 Descoberta Automática na Rede
Cada cliente envia mensagens periódicas via **broadcast UDP**, informando sua porta TCP.  
O servidor escuta essas mensagens e registra automaticamente os clientes disponíveis na rede local.


### ⌨️ Controle Remoto de Teclado
O servidor captura os eventos do teclado local e envia para o cliente selecionado.  
O cliente recebe esses comandos e executa as ações em tempo real.

- Pressionar **ESC** encerra a sessão de controle


### 🖱️ Controle Remoto de Mouse
O servidor captura movimentos, cliques e rolagem do mouse.  
Esses eventos são transmitidos ao cliente, que executa as ações correspondentes.

- O **botão do meio do mouse** encerra a sessão


### 📝 Registro de Ações
O servidor mantém um arquivo de registro (`auditoria.txt`) contendo:

- 📅 Data e hora
- 💻 Identificação do cliente
- ⚙️ Ação executada

Esse registro permite acompanhar todas as interações realizadas durante o uso do sistema.


### 🧱 Organização do Código
O projeto foi desenvolvido seguindo o paradigma de **Orientação a Objetos**, com divisão clara de responsabilidades:

- 👤 Cliente: anuncia sua presença e executa comandos
- 🖥️ Servidor: gerencia conexões e envia comandos
- 📦 Módulos separados para cada funcionalidade


### 🔄 Fluxo de Funcionamento
1️⃣ Cliente inicia e anuncia presença na rede  
2️⃣ Servidor detecta automaticamente  
3️⃣ Operador seleciona o cliente pelo menu  
4️⃣ Comandos são enviados  
5️⃣ Cliente executa localmente  
6️⃣ Ações são registradas  

---

📌 *Este projeto demonstra comunicação em rede, controle remoto e organização modular de código.*


## Considerações Finais
O projeto atende aos requisitos funcionais e arquiteturais propostos, incluindo comunicação em rede, descoberta automática, coleta de métricas e ações remotas.  
Os requisitos de segurança encontram-se parcialmente atendidos, ficando como ponto de melhoria futura.
