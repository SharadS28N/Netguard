# NetGuard Nepal - Python Backend Fixes

This document summarizes the changes made to getting the backend running successfully.

## 1. Configuration Fixes

- **Issue**: `.env` file was missing (only `.env.example` existed).
- **Fix**: Created `.env` with default configuration:
  ```env
  MONGODB_URI=mongodb://localhost:27017
  MONGODB_DB=netguard
  FLASK_HOST=0.0.0.0
  FLASK_PORT=5000
  FLASK_DEBUG=True
  ```

## 2. Dependency Fixes

- **Issue**: `numpy` and other packages failed to install due to strict version pinning incompatible with Python 3.14.
- **Fix**: Removed version constraints in `requirements.txt` to allow installing the latest compatible versions.
- **Issue**: `tensorflow` installation failed (no matching distribution for Python 3.14).
- **Fix**: Removed `tensorflow` from `requirements.txt` as it is an optional dependency for this project.

## 3. Code Fixes

- **Issue**: `train_models.py` failed with an `IndexError` during training. This was caused by synthetic data generation producing imbalanced classes (sometimes 0 samples of a specific class), which caused `sklearn`'s stratification to fail.
- **Fix**: Modified `services/ml_trainer.py` to explicitly force the inclusion of at least 5 samples of both "Legitimate" and "Evil Twin" classes in the synthetic dataset.

## Current Status

- Dependencies installed successfully.
- Models trained successfully.
- Backend server is running on `http://localhost:5000`.
