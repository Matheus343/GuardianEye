"""
EPI Guardian — Script de Detecção em Tempo Real
Raspberry Pi 4 · YOLOv8n ONNX · Picamera2

Fluxo:
  1. Captura frame via Picamera2 (640×480)
  2. Pré-processa para entrada do modelo (640×640, float32)
  3. Inferência com ONNX Runtime (4 threads, modo sequencial)
  4. NMS com limiar de confiança 0.45
  5. Lógica de inspeção condicionada à detecção de 'person'
  6. Envia resultado ao IoT Agent via HTTP POST (Ultralight 2.0) a cada 3s
  7. Ao encerrar, salva metricas.txt com confiança média por classe
"""

import cv2
import numpy as np
import onnxruntime as ort
import requests
import time
import os
from picamera2 import Picamera2

# ── Configurações ──────────────────────────────────────────────────────────────
MODEL_PATH        = "/home/cefsa1/yolo_scripts/best.onnx"
IOT_AGENT_URL     = "http://107.23.134.32:7896/iot/d"
APIKEY            = "tcc2026"
DEVICE_ID         = "raspi01"          # altere para "raspi02" no segundo dispositivo
CONF_THRESHOLD    = 0.45
NMS_THRESHOLD     = 0.4
IMG_SIZE          = 640
ENVIO_INTERVALO   = 3                  # segundos entre cada envio ao servidor
DISPLAY_AVAILABLE = os.environ.get("DISPLAY") is not None

# Classes do modelo treinado (Construction-PPE filtrado)
CLASS_NAMES = {
    0: "capacete",
    1: "oculos",
    2: "colete",
    3: "person"
}

COLORS = {
    0: (0, 255, 0),     # capacete  — verde
    1: (0, 200, 255),   # oculos    — azul claro
    2: (0, 255, 255),   # colete    — amarelo
    3: (255, 255, 255)  # person    — branco
}

# ── ONNX Runtime otimizado para Raspberry Pi 4 (ARM64, 4 cores) ───────────────
opts = ort.SessionOptions()
opts.intra_op_num_threads     = 4
opts.inter_op_num_threads     = 1
opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
opts.execution_mode           = ort.ExecutionMode.ORT_SEQUENTIAL

print("[INIT] Carregando modelo ONNX...")
session    = ort.InferenceSession(MODEL_PATH, sess_options=opts)
input_name = session.get_inputs()[0].name
print(f"[INIT] Modelo carregado! Classes: {CLASS_NAMES}")

# ── Câmera ─────────────────────────────────────────────────────────────────────
print("[INIT] Iniciando câmera...")
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
))
picam2.start()
time.sleep(2)
print(f"[INIT] Câmera pronta! Dispositivo: {DEVICE_ID}\n")


# ── Funções de inferência ──────────────────────────────────────────────────────

def preprocessar(frame: np.ndarray) -> np.ndarray:
    """Redimensiona e normaliza o frame para entrada do modelo."""
    img = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))        # HWC → CHW
    return np.expand_dims(img, axis=0)         # → (1, 3, 640, 640)


def detectar(frame: np.ndarray):
    """Executa inferência e aplica NMS. Retorna class_ids e confidences."""
    blob    = preprocessar(frame)
    outputs = session.run(None, {input_name: blob})[0]  # (1, num_det, 8)

    boxes, confidences, class_ids = [], [], []

    for det in outputs[0]:
        cx, cy, w, h = det[0], det[1], det[2], det[3]
        scores       = det[4:]
        class_id     = int(np.argmax(scores))
        confidence   = float(scores[class_id])

        if confidence < CONF_THRESHOLD:
            continue
        if class_id not in CLASS_NAMES:
            continue

        x1 = int((cx - w / 2))
        y1 = int((cy - h / 2))
        boxes.append([x1, y1, int(w), int(h)])
        confidences.append(confidence)
        class_ids.append(class_id)

    # Non-Maximum Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)

    if len(indices) == 0:
        return [], []

    idx = indices.flatten()
    return [class_ids[i] for i in idx], [confidences[i] for i in idx]


def analisar_epi(class_ids, confidences):
    """
    Determina presença de EPIs somente se 'person' for detectada.
    Retorna: (capacete, oculos, colete, confianca_media)
    """
    if 3 not in class_ids:          # sem person → não avalia EPIs
        return None, None, None, 0.0

    capacete = False
    oculos   = False
    colete   = False
    confs    = []

    for cls, conf in zip(class_ids, confidences):
        if cls == 0:
            capacete = True
            confs.append(conf)
        elif cls == 1:
            oculos = True
            confs.append(conf)
        elif cls == 2:
            colete = True
            confs.append(conf)

    confianca = round(float(np.mean(confs)), 4) if confs else 0.0
    return capacete, oculos, colete, confianca


def enviar_dados(capacete, oculos, colete, confianca):
    """Envia resultado ao IoT Agent no formato Ultralight 2.0 via HTTP POST."""
    payload = (
        f"h|{capacete}|"
        f"g|{oculos}|"
        f"v|{colete}|"
        f"c|{confianca}|"
        f"w|{DEVICE_ID}|"
        f"t|{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}"
    )
    try:
        response = requests.post(
            IOT_AGENT_URL,
            params={"k": APIKEY, "i": DEVICE_ID},
            data=payload,
            headers={
                "Content-Type": "text/plain",
                "fiware-service": "tcc",
                "fiware-servicepath": "/"
            },
            timeout=5
        )
        print(f"[HTTP] {response.status_code} | {payload}")
    except Exception as e:
        print(f"[HTTP] Erro ao enviar: {e}")


# ── Acumuladores para métricas da sessão ──────────────────────────────────────
historico_confs = {0: [], 1: [], 2: []}


# ── Loop principal ─────────────────────────────────────────────────────────────
print(f"[RUN] Iniciando detecção — Dispositivo: {DEVICE_ID}")
print("Pressione CTRL+C para parar.\n")

frame_count  = 0
ultimo_envio = 0

try:
    while True:
        frame_count += 1
        frame = picam2.capture_array()

        class_ids, confidences = detectar(frame)
        capacete, oculos, colete, confianca = analisar_epi(class_ids, confidences)

        # Acumula confiança por classe para métricas finais
        for cls, conf in zip(class_ids, confidences):
            if cls in historico_confs:
                historico_confs[cls].append(conf)

        # Apenas exibe / envia quando há person no frame
        if capacete is not None:
            status = "OK" if (capacete and oculos and colete) else "NOK"
            print(
                f"[Frame {frame_count}] "
                f"Capacete:{capacete} Oculos:{oculos} Colete:{colete} "
                f"Conf:{confianca:.4f} | {status}"
            )

            agora = time.time()
            if agora - ultimo_envio >= ENVIO_INTERVALO:
                enviar_dados(capacete, oculos, colete, confianca)
                ultimo_envio = agora

        # Exibição ao vivo (somente quando DISPLAY disponível)
        if DISPLAY_AVAILABLE:
            for cls, conf in zip(class_ids, confidences):
                color = COLORS.get(cls, (200, 200, 200))
                label = f"{CLASS_NAMES.get(cls, str(cls))} {conf:.2f}"
                cv2.putText(frame, label, (10, 30 + cls * 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.imshow("EPI Guardian", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

except KeyboardInterrupt:
    print("\n[STOP] Detecção encerrada pelo usuário.")

finally:
    picam2.stop()
    if DISPLAY_AVAILABLE:
        cv2.destroyAllWindows()

    # ── Salva métricas da sessão ──────────────────────────────────────────────
    with open("metricas.txt", "w") as f:
        f.write(f"Sessão: {DEVICE_ID}\n")
        f.write(f"Frames processados: {frame_count}\n\n")
        nomes = {0: "capacete", 1: "oculos", 2: "colete"}
        for cls_id, nome in nomes.items():
            vals = historico_confs[cls_id]
            media = round(float(np.mean(vals)) * 100, 2) if vals else 0.0
            f.write(f"{nome}: {media}% (n={len(vals)})\n")

    print("[SAVE] metricas.txt salvo.")
