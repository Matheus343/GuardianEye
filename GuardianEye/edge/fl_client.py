"""
Guardian Eye — Cliente Flower (Aprendizado Federado)
Raspberry Pi 4 · Flower 1.7.0 · FedAvg

Fluxo por round:
  1. Conecta ao servidor Flower na EC2 (porta 8080)
  2. Recebe pesos globais do servidor
  3. Aplica os pesos no modelo ONNX local
  4. Executa ajuste local simulado sobre o dataset da sessão
  5. Envia pesos atualizados ao servidor para agregação FedAvg
  6. Ao final, substitui o best.onnx com validação obrigatória
"""

import argparse
import logging
import time
import os
import numpy as np
import flwr as fl
import onnxruntime as ort
from typing import Dict, List, Tuple
from flwr.common import NDArrays, Scalar

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FL-CLIENT] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Configurações padrão ──────────────────────────────────────────────────────
MODEL_PATH  = "/home/cefsa1/yolo_scripts/best.onnx"
DEVICE_ID   = os.environ.get("DEVICE_ID", "raspi01")


# ── Helpers para extração e injeção de pesos ONNX ────────────────────────────

def get_onnx_weights(model_path: str) -> List[np.ndarray]:
    """Extrai os inicializadores (pesos) de um modelo ONNX como lista de arrays."""
    import onnx
    model = onnx.load(model_path)
    return [np.array(init.float_data).reshape(
                [d for d in init.dims]) if len(init.float_data) > 0
            else np.frombuffer(init.raw_data, dtype=np.float32).reshape(
                [d for d in init.dims])
            for init in model.graph.initializer]


def set_onnx_weights(model_path: str, weights: List[np.ndarray], output_path: str):
    """Injeta pesos recebidos do servidor em um modelo ONNX e salva."""
    import onnx
    model = onnx.load(model_path)
    for init, w in zip(model.graph.initializer, weights):
        init.ClearField("float_data")
        init.ClearField("raw_data")
        init.raw_data = w.astype(np.float32).tobytes()
    onnx.save(model, output_path)


def validar_onnx(model_path: str) -> bool:
    """Valida se o modelo ONNX carrega corretamente com ONNX Runtime."""
    try:
        sess = ort.InferenceSession(model_path)
        _ = sess.get_inputs()[0].shape
        return True
    except Exception as e:
        log.error(f"Falha na validação do modelo: {e}")
        return False


# ── Cliente Flower ─────────────────────────────────────────────────────────────

class EPIGuardianClient(fl.client.NumPyClient):

    def __init__(self, model_path: str, device_id: str):
        self.model_path = model_path
        self.device_id  = device_id
        self.round      = 0
        log.info(f"Cliente iniciado — dispositivo: {device_id} | modelo: {model_path}")

    def get_parameters(self, config: Dict) -> NDArrays:
        log.info("Enviando pesos ao servidor...")
        return get_onnx_weights(self.model_path)

    def fit(
        self,
        parameters: NDArrays,
        config: Dict,
    ) -> Tuple[NDArrays, int, Dict[str, Scalar]]:
        self.round = config.get("server_round", self.round + 1)
        log.info(f"Round {self.round} — recebendo pesos globais do servidor...")

        # Aplica pesos globais em arquivo temporário
        tmp_path = self.model_path.replace(".onnx", "_global_tmp.onnx")
        set_onnx_weights(self.model_path, parameters, tmp_path)

        # Simula ajuste local (fine-tuning leve sobre dados da sessão)
        log.info(f"Round {self.round} — executando ajuste local...")
        time.sleep(2)   # representa o tempo de treino local na Pi

        # Retorna pesos do modelo ajustado
        updated_weights = get_onnx_weights(tmp_path)
        num_samples = 50  # número representativo de amostras locais

        log.info(f"Round {self.round} — pesos locais prontos para envio.")
        return updated_weights, num_samples, {"device": self.device_id, "round": self.round}

    def evaluate(
        self,
        parameters: NDArrays,
        config: Dict,
    ) -> Tuple[float, int, Dict[str, Scalar]]:
        log.info(f"Round {self.round} — avaliando modelo global...")

        # Aplica pesos recebidos e valida o modelo
        eval_path = self.model_path.replace(".onnx", "_eval.onnx")
        set_onnx_weights(self.model_path, parameters, eval_path)

        if not validar_onnx(eval_path):
            return 1.0, 0, {"error": "modelo inválido"}

        # Substitui best.onnx somente se a validação passar
        backup_path = self.model_path.replace(".onnx", "_backup.onnx")
        os.rename(self.model_path, backup_path)
        os.rename(eval_path, self.model_path)
        log.info(f"Modelo global aceito e substituído (backup em {backup_path})")

        loss = 0.5   # placeholder — em produção: calcular sobre dataset local
        return loss, 50, {"device": self.device_id}


# ── Ponto de entrada ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="EPI Guardian — Cliente Flower")
    parser.add_argument("--server",    default="107.23.134.32:8080", help="Endereço do servidor Flower")
    parser.add_argument("--model",     default=MODEL_PATH,            help="Caminho do modelo ONNX")
    parser.add_argument("--device-id", default=DEVICE_ID,             help="ID do dispositivo (raspi01/raspi02)")
    args = parser.parse_args()

    log.info(f"Conectando ao servidor: {args.server}")
    log.info(f"Modelo: {args.model} | Dispositivo: {args.device_id}")

    client = EPIGuardianClient(
        model_path=args.model,
        device_id=args.device_id
    )

    fl.client.start_numpy_client(
        server_address=args.server,
        client=client,
    )


if __name__ == "__main__":
    main()
