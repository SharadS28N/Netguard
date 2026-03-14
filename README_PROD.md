# Netguard Production & Deployment Guide

This guide explains how to run Netguard in a production-grade environment, handle security, and manage the ML pipeline.

## 1. Security & Environment (GitHub Readiness)

To keep your credentials safe when pushing to a public repository:
- **.env file**: Never commit this. We've provided `.env.example`.
- **.gitignore**: We've configured this to exclude `.env`, all `.pkl` model files, and local data.
- **Secret Keys**: Always generate a fresh `SECRET_KEY` for production using:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

## 2. WiFi Scanning: The "Phone" Reality

**Important**: Web browsers (Chrome, Safari, etc.) on phones **cannot** scan nearby WiFi networks due to OS security restrictions.

### How it works now:
- The backend scans the WiFi networks visible to the **server** (e.g., your laptop).
- When you access the website from your phone, you are seeing the threat report for the **server's location**.

### How to scan from a different location:
To detect threats in a remote location (like a cafe while your server is at home), you need an **Agent**:
1. Run a small Python script (using our `WiFiScanner` class) on a device at the target location.
2. The script "POSTs" the scan results to your server's `/api/scan/remote` endpoint (to be implemented).

## 3. ML Model Hosting (Hugging Face)

Instead of keeping large `.pkl` files in your repo, host them on Hugging Face:

1. Create a "Model" repository on [huggingface.co](https://huggingface.co/).
2. Upload your `rf_model.pkl`, `gb_model.pkl`, and `scaler.pkl`.
3. In your `.env`, set:
   ```env
   HF_MODEL_ID=your_username/your_repo_name
   HF_TOKEN=your_huggingface_read_token
   ```
4. The backend will automatically download the models on startup if they are missing locally.

## 4. Database (MongoDB Atlas)

All data (scans, threats, model metadata) is stored in MongoDB Atlas.
1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com/).
2. Get your connection string (Python driver).
3. Set `MONGODB_URI` in your `.env`.

## 5. Running in Production

### Locally (Windows)
We use `waitress` as the production WSGI server:
```bash
cd backend
pip install -r requirements.txt
python wsgi.py
```

### Linux / Docker
We use `gunicorn` inside a Docker container:
```bash
docker-compose up --build
```

## 6. Order of Operations
To ensure everything works correctly, follow this order:
1. **Setup MongoDB**: Create your Atlas cluster and get the URI.
2. **Configure .env**: Copy `.env.example` to `.env` and fill in the URI and Secret Key.
3. **Train Models**: Run `python train_models.py` once to generate initial models (or upload them to HF).
4. **Start Backend**: Run `python wsgi.py`.
5. **Start Frontend**: Run `npm run dev` (or build and serve).
