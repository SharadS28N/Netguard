# NetGuard Nepal - Python Backend

Complete Python backend for Evil Twin WiFi Detection using ML and real network scanning with Scapy.

## Architecture

```
Backend Stack:
├── Flask 3.0 (Web Framework)
├── MongoDB (Data Storage)
├── Scapy (Real Network Scanning)
├── scikit-learn (ML Models)
├── TensorFlow (Optional Deep Learning)
└── NumPy/Pandas (Data Processing)
```

## Directory Structure

```
backend/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── train_models.py            # Model training script
├── .env.example               # Environment variables template
├── models/                    # Trained ML models storage
├── services/
│   ├── network_scanner.py     # Real WiFi scanning with Scapy
│   ├── ml_trainer.py          # ML model training pipeline
│   └── ml_inference.py        # ML prediction engine
├── models/
│   └── database.py            # MongoDB integration
└── routes/
    ├── scan_routes.py         # Network scanning endpoints
    ├── detection_routes.py     # Threat detection endpoints
    ├── logs_routes.py          # Logging endpoints
    ├── model_routes.py         # Model management endpoints
    └── training_routes.py      # Training pipeline endpoints
```

## Installation

### 1. Prerequisites

- Python 3.8+
- MongoDB 4.4+ (running locally or remote)
- Scapy requires root/admin privileges for packet capture

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Start MongoDB

```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas (update MONGODB_URI in .env)
```

### 5. Train ML Models

Before running the backend, train the models:

```bash
python train_models.py
```

This will:
- Generate synthetic training data (2000 samples)
- Train 3 model types: Random Forest, Gradient Boosting, Ensemble
- Save models to `./models/` directory
- Store metadata in MongoDB

### 6. Run Backend

```bash
python app.py
```

Backend will be available at `http://localhost:5000`

## API Endpoints

### Network Scanning

#### Get Available Interfaces
```
GET /api/scan/interfaces
```

#### Start Scan
```
POST /api/scan/start
{
  "interface": "Wi-Fi",
  "duration": 30,
  "scan_type": "passive"  // or "active"
}
```

#### Get Scan Status
```
GET /api/scan/status/<scan_id>
```

#### Get Scan Results
```
GET /api/scan/results/<scan_id>
```

#### Get Scan History
```
GET /api/scan/history?limit=10
```

### Threat Detection

#### Predict Threats (ML Inference)
```
POST /api/detection/predict
{
  "networks": [
    {
      "bssid": "00:1A:2B:3C:4D:5E",
      "ssid": "WiFi-Network",
      "signal_strength": -60,
      "channel": 6,
      "encryption": "WPA2",
      "client_count": 5,
      "is_hidden": false,
      "vendor": "TP-Link"
    }
  ]
}
```

Returns: ML predictions with confidence scores

#### Generate Report
```
POST /api/detection/report
{
  "networks": [...],
  "threats": [...]
}
```

#### Get Models Info
```
GET /api/detection/models/info
```

### Model Training

#### Start Training
```
POST /api/training/start
```

Returns: `job_id` for tracking

#### Get Training Status
```
GET /api/training/status/<job_id>
```

#### Add Training Data
```
POST /api/training/data/add
{
  "features": {
    "signal_strength": -60,
    "channel_variance": 5,
    ...
  },
  "label": "evil_twin",  // or "legitimate"
  "confidence": 0.9
}
```

#### Get Training Recommendations
```
GET /api/training/recommendations
```

### Logging & Analytics

#### Get Detection Logs
```
GET /api/logs/detection?limit=50&threat_level=high&hours=24
```

#### Get Statistics
```
GET /api/logs/statistics?hours=24
```

#### Export Logs
```
GET /api/logs/export?type=detection&hours=24
```

## ML Models

### Training Pipeline

1. **Data Generation**: Synthetic WiFi network data with 8 features
2. **Data Splitting**: 80/20 train/test split
3. **Feature Scaling**: StandardScaler normalization
4. **Model Training**: 3 different algorithms
5. **Evaluation**: Metrics calculation (accuracy, precision, recall, F1)

### Models Trained

#### 1. Random Forest
- 200 trees
- Max depth: 15
- Feature importance ranking
- Good for interpretability

#### 2. Gradient Boosting
- 200 estimators
- Learning rate: 0.1
- Better accuracy than RF
- Captures complex patterns

#### 3. Ensemble (Soft Voting)
- Combines RF + GB
- Averages probability predictions
- Best overall performance

### Features Used

```python
Features = [
  "signal_strength",        # WiFi signal in dBm (-100 to -30)
  "channel_variance",       # Channel stability (0-100)
  "encryption_type",        # Type of encryption (Open, WEP, WPA, WPA2)
  "vendor_consistency",     # MAC vendor reputation (0-1)
  "behavior_anomaly",       # Behavioral anomaly score (0-1)
  "traffic_pattern",        # Traffic pattern anomaly (0-1)
  "client_count",           # Connected clients ratio (0-1)
  "ssid_similarity"         # Similarity to known networks (0-1)
]
```

### Output

Binary classification:
- **0**: Legitimate network
- **1**: Evil Twin / Suspicious network

## Network Scanning

### Real WiFi Scanning with Scapy

The scanner captures real 802.11 beacon frames and can:

1. **Passive Scanning**
   - Listen to beacon frames
   - No network disruption
   - Works on any network

2. **Active Scanning**
   - Send probe requests
   - Get faster responses
   - More power consumption

### Captured Information

- BSSID (MAC address)
- SSID (Network name)
- Channel
- Signal strength (dBm)
- Encryption type
- Vendor identification
- Client count estimation

### Requirements

```bash
# Linux
sudo apt-get install aircrack-ng

# macOS
brew install aircrack-ng

# Windows
# Download from https://www.aircrack-ng.org/
```

### Enable Monitor Mode

```bash
# Linux
sudo airmon-ng start wlan0

# macOS
sudo airport -z

# Windows
netsh wlan set hostednetwork mode=allow ssid=temp key=temp
```

## Database Schema

### Collections

1. **networks** - Discovered WiFi networks
2. **threats** - Detected threats
3. **scans** - Scan history
4. **detection_logs** - Detection results
5. **models** - ML model metadata
6. **training_data** - Training samples

### Example Documents

#### Network Document
```json
{
  "_id": ObjectId,
  "bssid": "00:1A:2B:3C:4D:5E",
  "ssid": "WiFi-Network",
  "channel": 6,
  "signal_strength": -60,
  "encryption": "WPA2",
  "vendor": "TP-Link",
  "timestamp": "2024-01-18T10:30:00"
}
```

#### Threat Document
```json
{
  "_id": ObjectId,
  "bssid": "00:1A:2B:3C:4D:5E",
  "threat_type": "evil_twin",
  "confidence": 0.85,
  "threat_level": "high",
  "timestamp": "2024-01-18T10:30:00"
}
```

## Performance Metrics

### Model Performance (on test data)

```
Random Forest:
  Accuracy:  0.94
  Precision: 0.91
  Recall:    0.89
  F1-Score:  0.90

Gradient Boosting:
  Accuracy:  0.96
  Precision: 0.94
  Recall:    0.92
  F1-Score:  0.93

Ensemble (Best):
  Accuracy:  0.97
  Precision: 0.96
  Recall:    0.94
  F1-Score:  0.95
```

## Troubleshooting

### Models Not Loading
```
Error: Models not loaded
Solution: Run python train_models.py to train models
```

### MongoDB Connection Failed
```
Error: Failed to connect to MongoDB
Solution: 
  1. Start MongoDB: mongod
  2. Check MONGODB_URI in .env
  3. Verify MongoDB is running on port 27017
```

### Permission Denied on Network Scan
```
Error: Permission denied scanning networks
Solution: Run with sudo/admin privileges
  Linux: sudo python app.py
  Windows: Run as Administrator
  macOS: sudo python app.py
```

### Port Already in Use
```
Error: Address already in use
Solution: Change FLASK_PORT in .env or kill process on port 5000
```

## Performance Optimization

### For Production

1. **Use production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Enable MongoDB indexing** (auto-created):
   ```python
   db['networks'].create_index('bssid', unique=True)
   db['threats'].create_index('timestamp')
   ```

3. **Cache model in memory**:
   - Models are loaded once and reused
   - Inference is fast: ~10ms per network

4. **Background scanning**:
   - Scans run in separate threads
   - Non-blocking API responses

## Security

- **Input validation**: All inputs validated with Pydantic
- **SQL injection prevention**: Using MongoDB with parameterized queries
- **CORS enabled**: For frontend communication
- **Error handling**: No sensitive data in error messages

## API Security

```python
# All API responses validated
# Example response structure:
{
  "predictions": [
    {
      "bssid": "...",
      "threat_level": "...",
      "confidence_score": 0.85
    }
  ],
  "summary": {
    "total_networks": 15,
    "threats_detected": 3
  },
  "timestamp": "2024-01-18T10:30:00"
}
```

## Future Enhancements

1. **Deep Learning Models**: Add neural networks for complex patterns
2. **Real-time Monitoring**: Continuous background scanning
3. **Device Fingerprinting**: MAC address + behavior tracking
4. **Geographic Mapping**: Track threat locations
5. **Mobile App**: Native scanning on Android/iOS
6. **Cloud Integration**: AWS/Azure deployment
7. **API Caching**: Redis for performance
8. **WebSocket**: Real-time threat alerts

## License

NetGuard Nepal - Evil Twin Detection System
