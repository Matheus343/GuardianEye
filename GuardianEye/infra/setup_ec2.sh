#!/bin/bash
# setup_ec2.sh — Instala Docker e configura o ambiente na EC2 (Ubuntu 24.04)
# Uso: sudo ./setup_ec2.sh

set -e

echo "=========================================="
echo "  EPI Guardian — Setup EC2"
echo "=========================================="

# ── Atualiza o sistema ────────────────────────────────────────────────────────
echo "[1/5] Atualizando pacotes..."
apt-get update -y && apt-get upgrade -y

# ── Instala dependências ──────────────────────────────────────────────────────
echo "[2/5] Instalando dependências..."
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    nano

# ── Instala Docker ────────────────────────────────────────────────────────────
echo "[3/5] Instalando Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# ── Adiciona usuário ubuntu ao grupo docker ───────────────────────────────────
echo "[4/5] Configurando permissões..."
usermod -aG docker ubuntu

# ── Habilita Docker no boot ───────────────────────────────────────────────────
echo "[5/5] Habilitando serviço Docker..."
systemctl enable docker
systemctl start docker

echo ""
echo "=========================================="
echo "  Docker instalado com sucesso!"
echo "  Docker: $(docker --version)"
echo "  Compose: $(docker compose version)"
echo ""
echo "  PRÓXIMO PASSO:"
echo "  cd ~/epi-guardian/infra"
echo "  cp .env.example .env && nano .env"
echo "  docker compose up -d"
echo "=========================================="
