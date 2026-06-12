<div align="center">

# 🦺 Guardian Eye

**Sistema de Monitoramento de EPIs com Aprendizado Federado em Ambiente Industrial**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=flat-square)](https://ultralytics.com)
[![Flower](https://img.shields.io/badge/Flower-FedAvg-499848?style=flat-square)](https://flower.ai)
[![FIWARE](https://img.shields.io/badge/FIWARE-Orion%203.10-5DC0CF?style=flat-square)](https://fiware.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=flat-square&logo=amazonwebservices&logoColor=white)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br/>

> Trabalho de Conclusão de Curso — Engenharia de Computação · CEFSA · 2026  
> Orientador: Prof. Dr. Fábio Henrique Cabrini

</div>

---

## 📋 Sobre o Projeto

O **Guardian Eye** é um sistema distribuído de monitoramento de Equipamentos de Proteção Individual (EPIs) em tempo real para ambientes industriais. Dispositivos **Raspberry Pi 4** atuam como unidades de borda: capturam frames via câmera, executam inferência local com o modelo **YOLOv8n** (ONNX Runtime, sem GPU) e transmitem os resultados para uma plataforma centralizada na nuvem (**AWS EC2**) por meio da stack de IoT **FIWARE**.

O diferencial do projeto é o **Aprendizado Federado** com o framework **Flower (FedAvg)**: os dispositivos refinam colaborativamente o modelo de detecção sem que nenhuma imagem dos trabalhadores seja transmitida ao servidor, preservando a privacidade dos dados em conformidade com a **LGPD**.

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────────────┐
│                        AWS EC2  (t3.medium)                      │
│                                                                   │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌─────────────┐ │
│  │  Orion   │  │  IoT Agent   │  │  Cygnus  │  │   Flower    │ │
│  │ Context  │◄─│  MQTT (UL2)  │  │(MongoDB  │  │   Server    │ │
│  │ Broker   │  │  Port 4041   │  │  Sink)   │  │   FedAvg    │ │
│  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └──────┬──────┘ │
│       │               │               │                │         │
│  ┌────▼───────────────▼───────────────▼────┐  ┌───────▼──────┐ │
│  │             MongoDB 4.4                  │  │   Aplicação  │ │
│  │        (estado atual + histórico)        │  │     Web      │ │
│  └──────────────────────────────────────────┘  └──────────────┘ │
│                        ▲                                          │
│              ┌──────────┴──────────┐                             │
│              │   Mosquitto MQTT    │                              │
│              │     Port 1883       │                              │
│              └──────────┬──────────┘                             │
└─────────────────────────┼──────────────────────────────────────-─┘
                          │ HTTP (Ultralight 2.0)
         ┌────────────────┼────────────────┐
         │                │                │
  ┌──────▼──────┐  ┌──────▼──────┐        ·
  │  Raspberry  │  │  Raspberry  │  (N dispositivos)
  │   Pi 4 #1   │  │   Pi 4 #2   │
  │             │  │             │
  │ ┌─────────┐ │  │ ┌─────────┐ │
  │ │YOLOv8n  │ │  │ │YOLOv8n  │ │
  │ │  ONNX   │ │  │ │  ONNX   │ │
  │ └─────────┘ │  │ └─────────┘ │
  │  detection  │  │  detection  │
  │  fl_client  │  │  fl_client  │
  └─────────────┘  └─────────────┘
       Camera            Camera
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Versão | Função |
|--------|-----------|--------|--------|
| **Detecção** | YOLOv8n (Ultralytics) | 8.4.x | Modelo de visão computacional |
| **Inferência** | ONNX Runtime | 1.18+ | Execução do modelo na Raspberry Pi sem GPU |
| **Federated Learning** | Flower (FedAvg) | 1.7.0 | Agregação federada de pesos |
| **IoT Middleware** | FIWARE Orion CB | 3.10.1 | Estado atual dos dispositivos (NGSI v2) |
| **Protocolo IoT** | IoT Agent MQTT (UL2) | latest | Tradução Ultralight 2.0 → NGSI |
| **Broker MQTT** | Eclipse Mosquitto | 2.0 | Comunicação entre Pi e EC2 |
| **Persistência** | FIWARE Cygnus + MongoDB | 4.4 | Histórico de detecções |
| **Infraestrutura** | Docker Compose + AWS EC2 | t3.medium | Orquestração e hospedagem |
| **Treinamento** | Google Colab (GPU T4) | — | Treinamento do modelo baseline |

---

## 📁 Estrutura do Repositório

```
epi-guardian/
│
├── 📄 README.md
├── 📄 LICENSE
├── 📄 .gitignore
│
├── 📂 infra/                          # Infraestrutura AWS EC2
│   ├── docker-compose.yml             # Stack completa (FIWARE + Flower + WebApp)
│   ├── .env.example                   # Variáveis de ambiente (copie para .env)
│   ├── setup_ec2.sh                   # Script de instalação do Docker na EC2
│   └── mosquitto/
│       └── mosquitto.conf             # Configuração do broker MQTT
│
├── 📂 edge/                           # Dispositivos Raspberry Pi 4
│   ├── detection.py                   # Script principal de detecção em tempo real
│   ├── fl_client.py                   # Cliente Flower (participa do treinamento federado)
│   └── requirements.txt               # Dependências Python para a Raspberry Pi
│
├── 📂 federated/                      # Aprendizado Federado
│   ├── server.py                      # Servidor Flower com estratégia FedAvg
│   ├── Dockerfile                     # Container do servidor Flower
│   └── requirements.txt
│
├── 📂 training/                       # Configuração do treinamento
│   └── ppe_custom.yaml                # Dataset config (4 classes, split 70/30)
│
└── 📂 docs/                           # Documentação complementar
    └── provisioning.md                # Provisionamento dos dispositivos no IoT Agent
```

---

## ⚙️ Pré-requisitos

### Servidor (AWS EC2)
- Instância **t3.medium** ou superior (Ubuntu 24.04 LTS)
- **Docker** 24+ e **Docker Compose** v2+
- Portas abertas no Security Group: `22`, `1026`, `1883`, `4041`, `7896`, `8080`, `8668`, `5000`
- IP elástico configurado

### Dispositivo de Borda (Raspberry Pi 4)
- Raspberry Pi 4 com **4 GB** de RAM (recomendado)
- Raspberry Pi OS 64-bit (Bookworm)
- Módulo de câmera CSI ou USB
- Python 3.10+
- Rede com acesso ao IP público da EC2

### Treinamento (Google Colab)
- Conta Google com acesso ao Colab
- Runtime com GPU (**T4** recomendado)

---

## 🚀 Instalação e Configuração

### 1. Infraestrutura — AWS EC2

```bash
git clone https://github.com/seu-usuario/epi-guardian.git
cd epi-guardian/infra

cp .env.example .env
nano .env   # preencha APIKEY, variáveis de e-mail, etc.

chmod +x setup_ec2.sh && sudo ./setup_ec2.sh

docker compose up -d
docker compose ps
```

Aguarde todos os serviços ficarem `healthy` e provisione os dispositivos conforme [`docs/provisioning.md`](docs/provisioning.md).

---

### 2. Dispositivos de Borda — Raspberry Pi 4

```bash
# Instale as dependências
pip3 install -r edge/requirements.txt --break-system-packages
sudo apt install python3-picamera2 -y

# Coloque o modelo ONNX na pasta correta
cp best.onnx /home/cefsa1/yolo_scripts/best.onnx

# Execute a detecção
python3 edge/detection.py
```

Para iniciar automaticamente no boot, configure um serviço `systemd` apontando para `detection.py`.

---

### 3. Aprendizado Federado

O servidor Flower sobe automaticamente via `docker compose`. Para iniciar uma sessão de treinamento federado, execute em cada Raspberry Pi:

```bash
python3 edge/fl_client.py --server <IP_EC2>:8080 --device-id raspi01
# Na segunda Pi:
python3 edge/fl_client.py --server <IP_EC2>:8080 --device-id raspi02
```

O servidor aguarda o número mínimo de clientes (`FL_MIN_CLIENTS`) antes de iniciar o Round 1. Ao final dos rounds, o modelo global é salvo em `federated/global_models/` e o `best.onnx` nos dispositivos é substituído após validação automática.

---

## 🔬 Treinamento do Modelo

O arquivo `training/ppe_custom.yaml` contém a configuração do dataset utilizado no treinamento do baseline:

- **Dataset:** Construction-PPE (Ultralytics) — ~3.000 imagens originais
- **Classes:** capacete (0), óculos de proteção (1), colete de segurança (2), person (3)
- **Divisão:** 70% treino (1.142 imagens) / 30% validação (284 imagens)
- **Treinamento:** YOLOv8n · 100 épocas · imgsz 640 · batch 16 · GPU Tesla T4 · ~1h03min
- **Exportação:** ONNX opset 12 · 6,3 MB

---

## 📊 Resultados

### Modelo Baseline (sem Aprendizado Federado)

| Classe | Precisão | Recall | mAP50 | mAP50-95 |
|--------|----------|--------|-------|----------|
| Capacete | 86,6% | 77,0% | 80,1% | 41,9% |
| Óculos de proteção | 85,1% | 78,7% | 81,4% | 37,3% |
| Colete de segurança | 87,9% | 76,6% | 83,7% | 50,5% |
| **Média geral** | **86,5%** | **77,4%** | **81,8%** | **43,2%** |

### Confiança em Cenário Controlado (Baseline sem FL)

Câmera a 1.540 mm · distância 560 mm · 54 lux

| Classe | Confiança média |
|--------|----------------|
| Capacete | 61,69% |
| Óculos de proteção | 68,68% |
| Colete de segurança | 51,75% |

> Os incrementos promovidos pelas rodadas de Aprendizado Federado estão detalhados no artigo do TCC.

---

## 🖥️ Aplicação Web

A arquitetura do Guardian Eye é agnóstica quanto à camada de visualização — qualquer aplicação capaz de consumir a API NGSI v2 do Orion Context Broker ou consultar diretamente o MongoDB pode ser utilizada como dashboard.

Para este projeto, foi desenvolvida uma aplicação web com a seguinte stack:

| Componente | Tecnologia |
|------------|-----------|
| Framework | ASP.NET Core MVC 8.0 (C#) |
| Frontend | Razor Views + CSS customizado |
| Gráficos | Chart.js (CDN) |
| Banco de dados | MongoDB.Driver 3.7.1 (NuGet) |
| Autenticação | Cookie Authentication (ASP.NET Identity) |
| E-mail | MailKit — relatório diário via Gmail SMTP |
| Container | Docker (Dockerfile multi-stage) |

A aplicação expõe as seguintes páginas: **Dashboard** (KPIs em tempo real com refresh a cada 5 minutos), **Histórico** (últimas 50 inspeções das 24h anteriores por dispositivo), **Gráficos** (taxa de conformidade OK/NOK, EPIs mais ausentes e confiança por dispositivo) e **Gestão de usuários** (CRUD — perfil admin).

---

## 🗂️ Variáveis de Ambiente

Copie `infra/.env.example` para `infra/.env` e preencha os valores:

```env
FIWARE_SERVICE=tcc
APIKEY=tcc2026

MONGO_HOST=mongodb
MONGO_PORT=27017

FL_SERVER_PORT=8080
FL_MIN_CLIENTS=2
FL_NUM_ROUNDS=50

WEBAPP_PORT=5000
EMAIL_USER=seu@email.com
EMAIL_PASS=sua_senha_app
```

> ⚠️ Nunca versione o arquivo `.env` com credenciais reais — o `.gitignore` já o exclui por padrão.

---

## 👥 Autores

| Nome | Função |
|------|--------|
| **Adriana Monteiro Martani** | Desenvolvimento e documentação |
| **Analuz Marin Ramos** | Desenvolvimento e documentação |
| **Matheus** | Desenvolvimento e documentação |
| **Yasmin Laisa Maciel** | Desenvolvimento e documentação |

**Orientador:** Prof. Dr. Fábio Henrique Cabrini  
**Instituição:** CEFSA — Faculdade Engenheiro Salvador Arena  
**Curso:** Engenharia de Computação · 2026

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

---

<div align="center">
Desenvolvido como Trabalho de Conclusão de Curso — CEFSA · 2026
</div>
