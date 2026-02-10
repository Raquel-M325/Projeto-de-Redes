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


### 🧩 Organização do Código – Cliente (`cliente.py`)

O arquivo `cliente.py` concentra toda a lógica executada em cada máquina cliente do sistema.

---

#### 🧑‍💻 Classe `Client`
A classe `Client` representa o cliente da aplicação e é responsável por:

- Inicializar o cliente e definir sua porta TCP
- Gerenciar a execução contínua do programa
- Centralizar comunicação, coleta de dados e execução de comandos

---

#### 🔧 Método `__init__`
Inicializa o cliente definindo:
- Porta TCP aleatória para comunicação
- Estado de execução do cliente
- Endereço MAC da máquina

Essas informações são usadas para identificação pelo servidor.

---

#### 📡 Método `send_broadcast`
Responsável pela **descoberta automática** do cliente na rede.

- Envia mensagens periódicas via **UDP broadcast**
- Informa ao servidor a porta TCP disponível
- Permite que o servidor detecte clientes sem configuração manual

---

#### 🔗 Método `tcp_server`
Cria um **servidor TCP interno** no cliente.

- Fica escutando conexões do servidor
- Aceita múltiplas conexões simultâneas usando threads
- Encaminha cada conexão para tratamento específico

---

#### 🔄 Método `handle_tcp_connection`
Gerencia toda a comunicação TCP com o servidor.

Esse método:
- Interpreta comandos recebidos
- Controla o início e fim do controle de teclado e mouse
- Responde solicitações como envio do MAC e inventário
- Mantém a sessão ativa até o encerramento

---

#### ⌨️ Controle de Teclado
Dentro de `handle_tcp_connection`, o cliente:
- Recebe eventos de teclado
- Executa pressionamento e liberação de teclas
- Ativa ou desativa o controle conforme comandos recebidos

---

#### 🖱️ Controle de Mouse
Também em `handle_tcp_connection`, o cliente:
- Executa comandos de movimento, clique e rolagem do mouse
- Responde dinamicamente aos comandos do servidor
- Encerra a sessão conforme solicitado

---

#### 📊 Método `coletar_dados`
Responsável pela **coleta de inventário** do sistema.

Retorna informações como:
- Número de núcleos de CPU
- Memória RAM disponível
- Espaço livre em disco
- Interfaces de rede com IP, status e tipo
- Sistema operacional

Os dados são enviados ao servidor em formato estruturado.

---

#### 🌐 Método `identificar_tipo`
Classifica cada interface de rede como:
- Loopback
- Wi-Fi
- Ethernet

Essa classificação auxilia na organização das informações coletadas.

---

#### ▶️ Método `start`
Inicia a execução do cliente.

- Dispara as threads de broadcast UDP e servidor TCP
- Mantém o cliente ativo em execução contínua

---

📌 *Essa estrutura garante organização clara, modularidade e fácil manutenção do código do cliente.*

### 🧩 Organização do Código – Servidor (`servidor.py`)

O arquivo `servidor.py` representa o núcleo central do sistema.  
Ele é responsável por **descobrir clientes na rede**, **gerenciar conexões**, **solicitar dados**, **consolidar informações** e **executar ações remotas**.

---

#### 🗂️ Classe `ClientInfo`
A classe `ClientInfo` representa um cliente conhecido pelo servidor.

Ela armazena:
- Endereço IP do cliente
- Porta TCP utilizada
- Última vez que o cliente foi visto
- Última mensagem recebida
- Endereço MAC
- Dados de inventário do cliente

Essa classe facilita o gerenciamento e a visualização dos clientes conectados.

---

#### 🖥️ Classe `DiscoveryServer`
A classe `DiscoveryServer` centraliza todas as funcionalidades do servidor.

Ela é responsável por:
- Detectar clientes automaticamente
- Manter a lista de clientes ativos
- Solicitar informações dos clientes
- Executar controle remoto
- Consolidar e exportar dados

---

#### 📡 Método `listen_broadcasts`
Responsável pela **descoberta automática de clientes**.

- Escuta mensagens UDP na porta de broadcast
- Identifica novos clientes a partir das mensagens recebidas
- Atualiza o tempo de atividade dos clientes já conhecidos
- Registra automaticamente clientes recém-descobertos

---

#### 🔗 Método `ask_mac_tcp`
Solicita o **endereço MAC** de um cliente específico.

- Abre uma conexão TCP com o cliente
- Envia o comando de solicitação
- Armazena o MAC recebido na estrutura do cliente

---

#### ⌨️ Método `control_keyboard`
Implementa o **controle remoto de teclado**.

- Captura eventos do teclado local do servidor
- Envia esses eventos via TCP para o cliente selecionado
- Permite encerrar a sessão pressionando a tecla ESC

---

#### 🖱️ Método `control_mousepad`
Implementa o **controle remoto de mouse**.

- Captura movimentos, cliques e rolagem do mouse
- Envia os comandos em tempo real ao cliente
- Encerra a sessão ao pressionar o botão do meio do mouse

---

#### 📊 Método `ask_inventory_tcp`
Responsável por solicitar o **inventário do sistema** de um cliente.

- Envia o comando de coleta
- Recebe os dados em formato JSON
- Armazena as informações no objeto `ClientInfo`

---

#### 📈 Método `consolidado`
Realiza a **consolidação dos dados coletados**.

- Calcula médias de CPU, memória RAM e disco
- Considera apenas clientes que responderam à coleta
- Exibe os resultados diretamente no terminal

---

#### 📁 Método `export_csv`
Responsável pela **exportação dos dados**.

- Gera um arquivo `relatorio.csv`
- Inclui dados principais de cada cliente
- Permite análise externa dos resultados coletados

---

#### 📋 Método `menu`
Implementa o **menu interativo do servidor**.

Por meio dele é possível:
- Listar clientes conectados
- Solicitar MAC
- Controlar teclado e mouse
- Coletar inventário
- Visualizar médias consolidadas
- Exportar relatórios

---

#### ▶️ Método `start`
Inicializa o servidor.

- Inicia a escuta de broadcasts em uma thread separada
- Ativa o menu interativo principal
- Mantém o servidor em execução contínua

---

📌 *Essa estrutura garante centralização do controle, organização clara e facilidade de expansão do servidor.*



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
