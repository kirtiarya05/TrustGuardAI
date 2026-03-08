---
description: How to run the TrustGuard AI Global Intelligence Platform
---

# Instructions

To get **TrustGuard AI v4.2.0** up and running with the new Global Forensic features.

## 1. Train the Global Mega-Model (Optional - Already Deployed)
The model is now trained on **120,000+ records** including WELFake and LIAR datasets.
```bash
cd backend
python train_extensive.py
```

## 2. Start the Deep-Scan Backend API
The backend now supports **Signature-based Scam Scanning** and **Linguistic Forensics (Sentiment Analysis)**.
```bash
cd backend
# Make sure textblob is installed
pip install textblob
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## 3. Start the Cyber-Intelligence Frontend UI
The UI features **CRT Scanlines**, **Neural Mapping animations**, and **Global Forensic metrics**.
```bash
cd frontend
npm run dev
```

Your web application will be live at:
- **Frontend / Forensic Dashboard**: [http://localhost:5173/](http://localhost:5173/)
- **Backend / Deep Scan API**: [http://localhost:8000](http://localhost:8000)

## 🔍 Protocol Status:
- [x] Global Dataset Merged (v4.2.0)
- [x] Forensic UI Deployed
- [x] Deep Scam Pattern Engine Active
