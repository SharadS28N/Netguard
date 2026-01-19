# NetGuard Nepal - API Documentation

Complete API reference for the Evil Twin Detection Platform backend.

## Base URL

```
http://localhost:3000/api
```

## Authentication

Currently, the API does not require authentication. For production deployments, add:
- API Key validation
- Bearer token authentication
- Rate limiting per user

## Response Format

All responses return JSON with the following structure:

### Success Response (2xx)

```json
{
  "data": {},
  "status": "success",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### Error Response (4xx, 5xx)

```json
{
  "error": "Error message",
  "details": "Additional error information",
  "status": "error",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## Endpoints

### 1. Network Detection

Analyze networks for evil twin threats using multi-layer AI/ML detection.

**Endpoint**: `POST /api/detect`

**Description**: Scans provided networks and returns threat assessment with multi-layer analysis.

#### Request Headers

```
Content-Type: application/json
```

#### Request Body

```json
{
  "networks": [
    {
      "ssid": "Free WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF",
      "signal_strength": -45,
      "channel": 6,
      "encryption": "Open",
      "beacon_interval": 100,
      "supported_rates": [1, 2, 5.5, 11, 6, 12, 24],
      "wps_enabled": true,
      "last_seen": 1704067200000
    },
    {
      "ssid": "Corporate_Network",
      "bssid": "11:22:33:44:55:66",
      "signal_strength": -65,
      "channel": 36,
      "encryption": "WPA3",
      "beacon_interval": 100,
      "supported_rates": [6, 12, 24, 48],
      "wps_enabled": false,
      "last_seen": 1704067200000
    }
  ],
  "scan_type": "active",
  "duration": 30
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| networks | Array | Yes | Array of network scan data |
| scan_type | String | No | "active" or "passive" (default: "active") |
| duration | Number | No | Scan duration in seconds (default: 30) |

#### Network Object Parameters

| Parameter | Type | Description |
|---|---|---|
| ssid | String | Network name (SSID) |
| bssid | String | MAC address (format: AA:BB:CC:DD:EE:FF) |
| signal_strength | Number | Signal strength in dBm (-120 to 0) |
| channel | Number | WiFi channel (1-165) |
| encryption | String | Encryption type (Open, WEP, WPA, WPA2, WPA3) |
| beacon_interval | Number | Beacon interval in ms (typical: 100) |
| supported_rates | Array | Supported data rates in Mbps |
| wps_enabled | Boolean | WPS (WiFi Protected Setup) status |
| last_seen | Number | Timestamp of last beacon (ms since epoch) |

#### Response

```json
{
  "scan_id": "scan_1704067200000_abc123def",
  "timestamp": 1704067200000,
  "networks": [
    {
      "ssid": "Free WiFi",
      "bssid": "AA:BB:CC:DD:EE:FF",
      "threat_level": "danger",
      "confidence": 0.92,
      "details": {
        "signature_score": 0.8,
        "behavior_score": 0.85,
        "traffic_score": 0.75,
        "ensemble_decision": "Detected via multi-layer analysis + ensemble decision"
      },
      "recommendations": [
        "Disconnect immediately - Evil Twin detected",
        "Do not transmit sensitive data on this network",
        "Report this network to your security team"
      ]
    }
  ],
  "overall_threat": "danger"
}
```

#### Response Parameters

| Parameter | Type | Description |
|---|---|---|
| scan_id | String | Unique scan identifier |
| timestamp | Number | Unix timestamp of scan |
| networks | Array | Array of analyzed networks |
| overall_threat | String | Overall threat level (safe/suspicious/danger) |

#### Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Invalid request format |
| 500 | Server error |

#### Example cURL

```bash
curl -X POST http://localhost:3000/api/detect \
  -H "Content-Type: application/json" \
  -d '{
    "networks": [
      {
        "ssid": "Free WiFi",
        "bssid": "AA:BB:CC:DD:EE:FF",
        "signal_strength": -45,
        "channel": 6,
        "encryption": "Open",
        "beacon_interval": 100,
        "supported_rates": [1, 2, 5.5, 11],
        "wps_enabled": true,
        "last_seen": 1704067200000
      }
    ]
  }'
```

---

### 2. ML Model Inference

Run machine learning model inference on feature vectors.

**Endpoint**: `POST /api/model`

**Description**: Executes ML models (signature, behavior, traffic, or ensemble) on provided features.

#### Request Body

```json
{
  "features": [0.3, 0.25, 0.15, 0.2, 0.1, 0.2, 0.15, 0.05],
  "model_type": "ensemble"
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| features | Array | Yes | Array of numeric feature values (0-1 range) |
| model_type | String | No | Model type: "signature", "behavior", "traffic", "ensemble" (default: "ensemble") |

#### Response

```json
{
  "prediction": "evil_twin_detected",
  "confidence": 0.87,
  "model_used": "Ensemble Meta-Model (Signature + Behavior + Traffic)",
  "processing_time_ms": 15
}
```

#### Model Types

##### Signature Model
- Detects known threat patterns
- Features: [beacon_anomaly, encryption_weakness, ssid_similarity, channel_anomaly]
- Best for: Known attacks, signature-based threats

##### Behavior Model
- Analyzes network behavior patterns
- Features: [wps_enabled, rate_anomaly, power_anomaly, frequency_deviation]
- Best for: Anomalous network behavior

##### Traffic Model
- Analyzes traffic patterns
- Features: [beacon_frequency, association_rate, data_rate, client_count]
- Best for: Real-time threat detection

##### Ensemble Model (Recommended)
- Combines all three models with weighted voting
- Weights: 40% signature, 35% behavior, 25% traffic
- Best for: Comprehensive threat assessment

#### Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Invalid features or model type |
| 500 | Model inference error |

#### Example cURL

```bash
curl -X POST http://localhost:3000/api/model \
  -H "Content-Type: application/json" \
  -d '{
    "features": [0.3, 0.25, 0.15, 0.2],
    "model_type": "ensemble"
  }'
```

---

### 3. Detection Logs

Manage detection history and analytics.

**Endpoint**: `GET /api/logs`

**Description**: Retrieve detection logs with filtering and pagination.

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| limit | Number | 50 | Maximum logs to return |
| offset | Number | 0 | Pagination offset |
| threat_level | String | all | Filter: "danger", "suspicious", "safe", or "all" |

#### Response

```json
{
  "logs": [
    {
      "id": "log_1704067200000",
      "timestamp": 1704067200000,
      "detection_result": {...},
      "user_action": "scan_completed",
      "created_at": "2024-01-01T12:00:00.000Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### Example cURL

```bash
# Get latest 20 logs
curl http://localhost:3000/api/logs?limit=20

# Get danger threats with pagination
curl http://localhost:3000/api/logs?limit=10&offset=0&threat_level=danger

# Get suspicious networks
curl http://localhost:3000/api/logs?threat_level=suspicious
```

---

**Endpoint**: `POST /api/logs`

**Description**: Create a new detection log entry.

#### Request Body

```json
{
  "detection_result": {
    "scan_id": "scan_123",
    "networks": [...],
    "overall_threat": "danger"
  },
  "user_action": "scan_completed"
}
```

#### Response

```json
{
  "id": "log_1704067200000",
  "timestamp": 1704067200000,
  "detection_result": {...},
  "user_action": "scan_completed",
  "created_at": "2024-01-01T12:00:00.000Z"
}
```

#### Example cURL

```bash
curl -X POST http://localhost:3000/api/logs \
  -H "Content-Type: application/json" \
  -d '{
    "detection_result": {
      "scan_id": "scan_123",
      "networks": [],
      "overall_threat": "safe"
    },
    "user_action": "manual_log"
  }'
```

---

**Endpoint**: `DELETE /api/logs`

**Description**: Delete old logs older than specified days.

#### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| older_than_days | Number | 30 | Delete logs older than this many days |

#### Response

```json
{
  "message": "Deleted 45 old logs",
  "remaining": 155
}
```

#### Example cURL

```bash
# Delete logs older than 60 days
curl -X DELETE http://localhost:3000/api/logs?older_than_days=60
```

---

## Rate Limiting

Currently not implemented. For production:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704070800
```

## Error Handling

### Common Errors

#### 400 - Bad Request

```json
{
  "error": "Invalid networks data",
  "details": "networks parameter must be an array"
}
```

#### 500 - Server Error

```json
{
  "error": "Detection failed",
  "details": "Internal server error message"
}
```

## Pagination

All list endpoints support pagination:

```
GET /api/logs?limit=20&offset=0
```

- **limit**: Items per page (1-100)
- **offset**: Starting position

## Data Types

### Threat Levels

- **danger**: High confidence evil twin (>0.7 ensemble score)
- **suspicious**: Suspicious behavior (0.4-0.7 ensemble score)
- **safe**: Legitimate network (<0.4 ensemble score)

### Encryption Types

- **Open**: No encryption
- **WEP**: Deprecated encryption
- **WPA**: WiFi Protected Access (deprecated)
- **WPA2**: WiFi Protected Access II (current standard)
- **WPA3**: WiFi Protected Access III (next-gen)

---

## Integration Examples

### JavaScript/TypeScript

```typescript
// Perform network detection
async function detectEvilTwins(networks) {
  const response = await fetch('/api/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ networks })
  })
  return response.json()
}

// Get detection history
async function getLogs(threat_level = 'all') {
  const response = await fetch(`/api/logs?threat_level=${threat_level}`)
  return response.json()
}
```

### Python

```python
import requests
import json

def detect_evil_twins(networks):
    response = requests.post(
        'http://localhost:3000/api/detect',
        json={'networks': networks}
    )
    return response.json()

def get_logs(threat_level='all'):
    response = requests.get(
        f'http://localhost:3000/api/logs?threat_level={threat_level}'
    )
    return response.json()
```

### cURL

```bash
#!/bin/bash

# Detect networks
curl -X POST http://localhost:3000/api/detect \
  -H "Content-Type: application/json" \
  -d @networks.json

# Get logs
curl http://localhost:3000/api/logs?limit=50

# Run ML model
curl -X POST http://localhost:3000/api/model \
  -H "Content-Type: application/json" \
  -d '{"features": [0.3, 0.25, 0.15, 0.2], "model_type": "ensemble"}'
```

---

## Webhook Support (Future)

Future versions will support webhooks for real-time threat alerts:

```json
POST /webhooks/threat-detected
{
  "event": "threat_detected",
  "scan_id": "scan_123",
  "threat_level": "danger",
  "networks_affected": 3,
  "timestamp": 1704067200000
}
```

---

## Version History

| Version | Date | Changes |
|---|---|---|
| 1.0.0 | 2024-01-01 | Initial release |

---

## Support

For API issues or questions:
1. Check error responses for detailed information
2. Review example requests above
3. Enable debug logging in application
4. Submit issue with request/response logs
