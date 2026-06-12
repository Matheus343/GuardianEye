<div align="center">

# 🦺 EPI Guardian

**Sistema de Monitoramento de EPIs com Aprendizado Federado em Ambiente Industrial**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-FF6B35?style=flat-square)](https://ultralytics.com)
[![Flower](https://img.shields.io/badge/Flower-FedAvg-499848?style=flat-square)](https://flower.ai)
[![FIWARE](https://img.shields.io/badge/FIWARE-Orion%203.10-5DC0CF?style=flat-square)](https://fiware.org)
[![ASP.NET](https://img.shields.io/badge/ASP.NET-MVC%208.0-512BD4?style=flat-square&logo=dotnet&logoColor=white)](https://dotnet.microsoft.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![AWS](https://img.shields.io/badge/AWS-EC2-FF9900?style=flat-square&logo=amazonwebservices&logoColor=white)](https://aws.amazon.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

<br/>

> Trabalho de Conclusão de Curso — Engenharia de Computação · CEFSA · 2026  
> Orientador: Prof. Dr. Fábio Henrique Cabrini

</div>

---

## 📋 Sobre o Projeto

O **EPI Guardian** é um sistema distribuído de monitoramento de Equipamentos de Proteção Individual (EPIs) em tempo real, desenvolvido para ambientes industriais. O sistema utiliza dispositivos **Raspberry Pi 4** como unidades de borda para capturar e processar imagens, detectar a presença ou ausência de EPIs com o modelo **YOLOv8n** e transmitir os dados para uma plataforma centralizada na nuvem (**AWS EC2**) por meio da stack de IoT **FIWARE**.

O diferencial do projeto está na adoção do **Aprendizado Federado** com o framework **Flower (FedAvg)**: os dispositivos de borda refinam colaborativamente o modelo de detecção sem que as imagens dos trabalhadores sejam transmitidas para o servidor central, preservando a privacidade dos dados em conformidade com a **LGPD**. Os resultados de conformidade são exibidos em um **dashboard web** desenvolvido em ASP.NET MVC 8.0.

### Funcionalidades

- Detecção em tempo real de capacete, óculos de proteção e colete de segurança
- Inferência local no dispositivo de borda via ONNX Runtime (sem GPU)
- Refinamento colaborativo do modelo via Aprendizado Federado (FedAvg)
- Transmissão de dados via MQTT/HTTP no formato Ultralight 2.0
- Persistência histórica de detecções no MongoDB via FIWARE Cygnus
- Dashboard web com gráficos de conformidade, alertas e relatórios por e-mail

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AWS EC2  (t3.medium)                        │
│                                                                      │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │  Orion   │  │  IoT Agent   │  │  Cygnus  │  │  Flower       │  │
│  │ Context  │◄─│  MQTT (UL2)  │  │(MongoDB  │  │  Server       │  │
│  │ Broker   │  │  Port 4041   │  │ Sink)    │  │  FedAvg       │  │
│  └────┬─────┘  └──────┬───────┘  └────┬─────┘  └──────┬────────┘  │
│       │               │               │                │            │
│  ┌────▼───────────────▼───────────────▼────┐   ┌──────▼────────┐  │
│  │              MongoDB 4.4                 │   │  WebApp       │  │
│  │         (estado atual + histórico)       │   │  ASP.NET MVC  │  │
│  └──────────────────────────────────────────┘   └───────────────┘  │
│                         ▲                                           │
│               ┌──────────┴──────────┐                              │
│               │   Mosquitto MQTT    │                               │
│               │     Port 1883       │                               │
│               └──────────┬──────────┘                              │
└──────────────────────────┼──────────────────────────────────────────┘
                           │ MQTT / HTTP
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐  ┌──────▼──────┐        ·
   │  Raspberry  │  │  Raspberry  │   (N dispositivos)
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
| **Inferência** | ONNX Runtime | 1.18+ | Execução do modelo na Raspberry Pi |
| **Federated Learning** | Flower (FedAvg) | 1.x | Agregação federada de pesos |
| **IoT Middleware** | FIWARE Orion CB | 3.10.1 | Estado atual dos dispositivos (NGSI v2) |
| **Protocolo IoT** | IoT Agent MQTT (UL2) | latest | Tradução Ultralight → NGSI |
| **Broker MQTT** | Eclipse Mosquitto | 2.0 | Comunicação MQTT entre Pi e EC2 |
| **Persistência** | FIWARE Cygnus + MongoDB | 4.4 | Histórico de detecções |
| **Dashboard** | ASP.NET MVC | 8.0 | Interface web de monitoramento |
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
│   ├── requirements.txt               # Dependências Python para a Raspberry Pi
│   └── models/
│       └── .gitkeep                   # Coloque o best.onnx aqui (não versionado)
│
├── 📂 federated/                      # Aprendizado Federado
│   ├── server.py                      # Servidor Flower com estratégia FedAvg
│   ├── simulation.py                  # Simulação local de rounds federados
│   ├── Dockerfile                     # Container do servidor Flower
│   └── requirements.txt
│
├── 📂 dashboard/                      # WebApp ASP.NET MVC 8.0
│   └── EpiGuardian.Web/
│       ├── Controllers/               # HomeController, DashboardController, AuthController
│       ├── Models/                    # DetectionRecord, DeviceStatus, ReportModel
│       ├── Views/                     # Razor views (Index, Dashboard, Graficos, Login)
│       ├── Services/                  # MongoDbService, EmailService
│       ├── wwwroot/                   # Chart.js, CSS, assets estáticos
│       ├── appsettings.json
│       └── EpiGuardian.Web.csproj
│
├── 📂 training/                       # Notebooks Google Colab
│   ├── 01_dataset_preparation.ipynb   # Filtragem, remapeamento e balanceamento do dataset
│   └── 02_train_baseline.ipynb        # Treinamento YOLOv8n (100 épocas, 640px)
│
└── 📂 docs/                           # Documentação complementar
    ├── provisioning.md                # Provisionamento dos dispositivos no IoT Agent
    ├── fiware_setup.md                # Configuração das subscriptions FIWARE
    └── images/
        └── architecture.png
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
- Raspberry Pi OS (64-bit, Bookworm)
- Módulo de câmera oficial ou USB
- Python 3.10+
- Rede com acesso ao IP público da EC2

### Treinamento (Google Colab)
- Conta Google com acesso ao Colab
- Runtime com GPU (**T4** recomendado)

---

## 🚀 Instalação e Configuração

### 1. Infraestrutura — AWS EC2

```bash
# Clone o repositório na EC2
git clone https://github.com/seu-usuario/epi-guardian.git
cd epi-guardian/infra

# Configure as variáveis de ambiente
cp .env.example .env
nano .env   # preencha APIKEY, MONGO_URI, EMAIL_*, etc.

# Instale Docker (se necessário)
chmod +x setup_ec2.sh && sudo ./setup_ec2.sh

# Suba a stack completa
docker compose up -d

# Verifique os containers
docker compose ps
```

Aguarde todos os serviços ficarem `healthy` e então provisione os dispositivos:

```bash
# Registrar serviço de EPI no IoT Agent
curl -X POST http://localhost:4041/iot/services \
  -H "Content-Type: application/json" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" \
  -d @docs/provisioning_service.json

# Registrar dispositivo raspi01
curl -X POST http://localhost:4041/iot/devices \
  -H "Content-Type: application/json" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" \
  -d @docs/provisioning_raspi01.json
```

> Consulte [`docs/provisioning.md`](docs/provisioning.md) para o payload completo e instruções de registro do raspi02.

---

### 2. Dispositivos de Borda — Raspberry Pi 4

```bash
# Instale as dependências
pip3 install -r edge/requirements.txt --break-system-packages

# Instale o picamera2 (se necessário)
sudo apt install python3-picamera2 -y

# Copie o modelo ONNX para a pasta models/
# (gerado pelo notebook 02_train_baseline.ipynb)
cp best.onnx edge/models/

# Execute o script de detecção
cd edge
python3 detection.py
```

Para que o script inicie automaticamente no boot:

```bash
# Crie o serviço systemd
sudo nano /etc/systemd/system/epi-detection.service
# (conteúdo disponível em docs/systemd_service.md)

sudo systemctl enable epi-detection
sudo systemctl start epi-detection
```

---

### 3. Aprendizado Federado

O servidor Flower já sobe automaticamente via `docker compose`. Para iniciar uma sessão de treinamento federado, execute o cliente em cada Raspberry Pi:

```bash
cd edge
python3 fl_client.py --server <IP_EC2>:8080 --device-id raspi01
```

O servidor aguarda o número mínimo de clientes conectados antes de iniciar o primeiro round. Após a conclusão dos rounds configurados, o modelo global atualizado é exportado automaticamente para ONNX e distribuído aos dispositivos.

---

### 4. Dashboard Web

O dashboard sobe automaticamente via `docker compose` na porta `5000`. Acesse:

```
http://<IP_EC2>:5000
```

Para desenvolvimento local:

```bash
cd dashboard/EpiGuardian.Web
dotnet restore
dotnet run
```

---

## 🔬 Treinamento do Modelo

Os notebooks em `training/` reproduzem todo o pipeline de preparação de dados e treinamento. Execute na ordem:

| Notebook | Descrição |
|----------|-----------|
| `01_dataset_preparation.ipynb` | Download do *Construction-PPE*, filtragem para 4 classes, balanceamento de óculos de proteção (duplicação + augmentação), divisão 70/30 |
| `02_train_baseline.ipynb` | Treinamento YOLOv8n — 100 épocas, imgsz 640, batch 16, GPU T4 — exportação para ONNX opset 12 |

---

## 📊 Resultados

### Modelo Baseline (sem Aprendizado Federado)

Treinamento: 100 épocas · GPU Tesla T4 · ~1h03min · 3.006.233 parâmetros · 8,1 GFLOPs

| Classe | Precisão | Recall | mAP50 | mAP50-95 |
|--------|----------|--------|-------|----------|
| Capacete | 86,6% | 77,0% | 80,1% | 41,9% |
| Óculos de proteção | 85,1% | 78,7% | 81,4% | 37,3% |
| Colete de segurança | 87,9% | 76,6% | 83,7% | 50,5% |
| **Média geral** | **86,5%** | **77,4%** | **81,8%** | **43,2%** |

### Confiança Média em Cenário Controlado (Baseline sem FL)

Câmera a 1.540 mm de altura · 560 mm do sujeito · 54 lux de iluminação

| Classe | Confiança média |
|--------|----------------|
| Capacete | 61,69% |
| Óculos de proteção | 68,68% |
| Colete de segurança | 51,75% |

> Os incrementos promovidos pelas rodadas de Aprendizado Federado sobre esses valores estão detalhados no artigo do TCC.

---

## 🗂️ Variáveis de Ambiente

Copie `infra/.env.example` para `infra/.env` e preencha:

```env
# FIWARE
FIWARE_SERVICE=tcc
APIKEY=tcc2026

# MongoDB
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_DB=epi_guardian

# Flower
FL_SERVER_PORT=8080
FL_MIN_CLIENTS=2
FL_NUM_ROUNDS=50

# Dashboard / E-mail
WEBAPP_PORT=5000
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=seu@email.com
EMAIL_PASS=sua_senha_app
```

> ⚠️ **Nunca versione o arquivo `.env`** com credenciais reais. O `.gitignore` já o exclui por padrão.

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
