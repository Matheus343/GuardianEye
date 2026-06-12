# Provisionamento dos Dispositivos no IoT Agent

Execute os comandos abaixo na EC2 após a stack estar de pé (`docker compose up -d`).

---

## 1. Registrar o Service Group

```bash
curl -s -X POST "http://localhost:4041/iot/services" \
  -H "Content-Type: application/json" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" \
  -d '{
    "services": [{
      "apikey":        "tcc2026",
      "cbroker":       "http://orion:1026",
      "entity_type":   "Device",
      "resource":      "/iot/d"
    }]
  }'
```

Resposta esperada: `{"count":0,"services":[]}`

---

## 2. Registrar raspi01

```bash
curl -s -X POST "http://localhost:4041/iot/devices" \
  -H "Content-Type: application/json" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" \
  -d '{
    "devices": [{
      "device_id":   "raspi01",
      "entity_name": "urn:ngsi-ld:Device:raspi01",
      "entity_type": "Device",
      "transport":   "HTTP",
      "attributes": [
        { "object_id": "h", "name": "h", "type": "Text" },
        { "object_id": "g", "name": "g", "type": "Text" },
        { "object_id": "v", "name": "v", "type": "Text" },
        { "object_id": "c", "name": "c", "type": "Text" },
        { "object_id": "w", "name": "w", "type": "Text" },
        { "object_id": "t", "name": "t", "type": "Text" }
      ]
    }]
  }'
```

---

## 3. Registrar raspi02

```bash
curl -s -X POST "http://localhost:4041/iot/devices" \
  -H "Content-Type: application/json" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" \
  -d '{
    "devices": [{
      "device_id":   "raspi02",
      "entity_name": "urn:ngsi-ld:Device:raspi02",
      "entity_type": "Device",
      "transport":   "HTTP",
      "attributes": [
        { "object_id": "h", "name": "h", "type": "Text" },
        { "object_id": "g", "name": "g", "type": "Text" },
        { "object_id": "v", "name": "v", "type": "Text" },
        { "object_id": "c", "name": "c", "type": "Text" },
        { "object_id": "w", "name": "w", "type": "Text" },
        { "object_id": "t", "name": "t", "type": "Text" }
      ]
    }]
  }'
```

---

## 4. Criar subscription Orion → Cygnus (persistência histórica)

```bash
curl -s -X POST "http://localhost:1026/v2/subscriptions" \
  -H "Content-Type: application/json" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" \
  -d '{
    "description": "Persiste detecções no MongoDB via Cygnus",
    "subject": {
      "entities": [{ "idPattern": ".*", "type": "Device" }],
      "condition": {
        "attrs": ["h", "g", "v", "c", "w", "t"]
      }
    },
    "notification": {
      "http": { "url": "http://cygnus:5051/notify" },
      "attrs": ["h", "g", "v", "c", "w", "t"]
    },
    "throttling": 1
  }'
```

---

## Mapeamento de atributos Ultralight 2.0

| Chave UL | Nome NGSI | Conteúdo |
|----------|-----------|----------|
| `h` | `h` | `True` / `False` — capacete detectado |
| `g` | `g` | `True` / `False` — óculos detectado |
| `v` | `v` | `True` / `False` — colete detectado |
| `c` | `c` | Float — confiança média da detecção |
| `w` | `w` | String — ID do dispositivo (`raspi01`, `raspi02`) |
| `t` | `t` | ISO 8601 UTC — timestamp da detecção |

---

## Verificar dispositivos provisionados

```bash
curl -s "http://localhost:4041/iot/devices" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" | python3 -m json.tool
```

## Verificar estado atual no Orion

```bash
curl -s "http://localhost:1026/v2/entities" \
  -H "fiware-service: tcc" \
  -H "fiware-servicepath: /" | python3 -m json.tool
```
