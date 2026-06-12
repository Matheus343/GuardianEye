"""
Guardian Eye — Servidor Flower FedAvg
AWS EC2 · Flower 1.7.0

Aguarda conexão dos dispositivos Raspberry Pi, coordena os rounds de
aprendizado federado com estratégia FedAvg e salva o modelo global
a cada round em global_models/.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import flwr as fl
import numpy as np
from flwr.common import FitRes, Parameters, Scalar, parameters_to_ndarrays
from flwr.server.client_proxy import ClientProxy

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [FL-SERVER] %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Configurações ──────────────────────────────────────────────────────────────
NUM_ROUNDS       = int(os.environ.get("FL_NUM_ROUNDS",   50))
MIN_CLIENTS      = int(os.environ.get("FL_MIN_CLIENTS",   2))
SERVER_PORT      = int(os.environ.get("FL_SERVER_PORT", 8080))
MODELS_DIR       = Path("global_models")
MODELS_DIR.mkdir(exist_ok=True)


# ── Estratégia customizada (FedAvg + salvamento de modelo) ────────────────────

class EpiGuardianFedAvg(fl.server.strategy.FedAvg):
    """
    FedAvg com salvamento automático do modelo global a cada round.
    O modelo é salvo como .npz em global_models/global_round_XXX.npz
    e também como global_latest.npz para uso imediato pelos dispositivos.
    """

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures,
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:

        # Agrega pesos via FedAvg padrão
        aggregated_params, metrics = super().aggregate_fit(
            server_round, results, failures
        )

        if aggregated_params is not None:
            # Converte para NumPy e salva
            weights = parameters_to_ndarrays(aggregated_params)
            self._salvar_modelo(weights, server_round)

            # Log do progresso
            num_clientes = len(results)
            total_amostras = sum(fit_res.num_examples for _, fit_res in results)
            log.info(
                f"Round {server_round}/{NUM_ROUNDS} concluído — "
                f"{num_clientes} cliente(s) · {total_amostras} amostras"
            )

        return aggregated_params, metrics

    def _salvar_modelo(self, weights: List[np.ndarray], round_num: int):
        """Salva os pesos agregados como arquivo .npz."""
        save_path = MODELS_DIR / f"global_round_{round_num:03d}.npz"
        latest_path = MODELS_DIR / "global_latest.npz"

        np.savez(save_path,    *weights)
        np.savez(latest_path,  *weights)

        log.info(f"Modelo global salvo: {save_path}")


# ── Ponto de entrada ──────────────────────────────────────────────────────────

def main():
    strategy = EpiGuardianFedAvg(
        fraction_fit=1.0,              # usa todos os clientes disponíveis
        fraction_evaluate=1.0,
        min_fit_clients=MIN_CLIENTS,
        min_evaluate_clients=MIN_CLIENTS,
        min_available_clients=MIN_CLIENTS,
        fit_metrics_aggregation_fn=_agregar_metricas,
    )

    log.info(f"Servidor iniciado na porta {SERVER_PORT}")
    log.info(f"Aguardando {MIN_CLIENTS} cliente(s) para iniciar os rounds...")
    log.info(f"Rounds configurados: {NUM_ROUNDS}")

    fl.server.start_server(
        server_address=f"0.0.0.0:{SERVER_PORT}",
        config=fl.server.ServerConfig(num_rounds=NUM_ROUNDS),
        strategy=strategy,
    )


def _agregar_metricas(metrics):
    """Agrega métricas de todos os clientes (média ponderada)."""
    total = sum(n for n, _ in metrics)
    return {
        "device_count": len(metrics),
        "total_samples": total,
    }


if __name__ == "__main__":
    main()
