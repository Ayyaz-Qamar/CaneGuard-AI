# 🌿 CaneGuard AI — Automated Sugarcane Disease Detection System
**AI-powered web app that detects sugarcane leaf diseases from images with 92.57% accuracy using MobileNetV2, Flask, and TensorFlow.**
<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.x-black?style=for-the-badge&logo=flask)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange?style=for-the-badge&logo=tensorflow)
![MobileNetV2](https://img.shields.io/badge/Model-MobileNetV2-green?style=for-the-badge)
![Accuracy](https://img.shields.io/badge/Accuracy-92.57%25-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)



</div>

---

## 📌 Table of Contents
- [About](#-about-the-project)
- [Features](#-features)
- [Disease Classes](#-disease-classes)
- [Tech Stack](#-tech-stack)
- [Model Training](#-model-training)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Results](#-results)

---

## 🧠 About the Project

CaneGuard AI is a Flask-based web application that uses **MobileNetV2 deep learning** to detect sugarcane leaf diseases from uploaded photos. A farmer uploads a leaf image and receives an instant diagnosis with treatment recommendations, weather risk assessment, and a downloadable PDF report in English or Urdu.

> **Problem:** Farmers lose up to 30% of crop annually due to undetected diseases with no affordable local-language tool available.
>
> **Solution:** Upload a photo → get full diagnosis in seconds.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Detection | Instant disease detection from leaf image |
| 📊 Confidence Score | Prediction confidence + damage percentage |
| 💊 Treatment Guide | Fungicide, fertilizer & precautions per disease |
| 🌦️ Weather Forecast | 7-day disease risk assessment by city |
| 📄 PDF Report | Downloadable diagnostic report per scan |
| 📜 Scan History | Complete scan records with analytics dashboard |
| 🌐 Bilingual UI | Full English and Urdu language support |
| 🌙 Theme Toggle | Dark and Light mode support |

---

## 🦠 Disease Classes

| # | Disease | Risk Level |
|---|---|---|
| 1 | ✅ Healthy | Low |
| 2 | 🔴 Red Rot | High |
| 3 | 🟠 Mosaic Virus | High |
| 4 | 🟡 Yellow Leaf Disease | Medium |
| 5 | 🟤 Rust | Medium |
| 6 | 🟣 Bacterial Blights | High |

---

## 🛠️ Tech Stack

```
Backend       →  Python 3.11, Flask, Flask-Login
Deep Learning →  TensorFlow, Keras, MobileNetV2
Image Process →  Pillow (PIL), NumPy
Database      →  SQLite
Weather API   →  OpenWeatherMap
PDF           →  ReportLab
Training      →  Google Colab (GPU)
```

---

## 🔬 Model Training

| Phase | Layers Trained | Val Accuracy |
|---|---|---|
| Phase 1 | Top classifier only | 82.20% |
| Phase 2 ⭐ | Top 30 MobileNetV2 layers | **92.57%** |
| Phase 3 | Full fine-tune | Planned |

- **Architecture:** MobileNetV2 + GlobalAvgPool + Dense(512) + Dense(256) + Softmax(6)
- **Dataset:** 20,000+ images — 75% Train / 15% Val / 10% Test
- **Best model:** `model/caneguard_v2_best.keras`

---

## 📁 Project Structure

```
CaneGuard-AI/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── routes.py
│   ├── models.py
│   └── templates/
├── modules/
│   ├── disease_detector.py
│   ├── treatment_engine.py
│   ├── damage_calculator.py
│   ├── weather_module.py
│   └── pdf_generator.py
├── model/
│   └── caneguard_v2_best.keras
├── static/
├── uploads/
├── reports/
├── run.py
└── requirements.txt
```

---

## ⚙️ Installation

```bash
# 1. Clone repo
git clone https://github.com/YOUR_USERNAME/caneguard-ai.git
cd caneguard-ai

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place trained model in model/ folder

# 5. Run
python run.py
```

Open browser: `http://localhost:5000`

---

## 📈 Results

| Test Type | Result |
|---|---|
| Dataset images | 98 — 100% confidence |
| Real-world images | ~63% confidence |
| Validation accuracy | **92.57%** |

---

## 👨‍💻 Developer

**Ayyaz Qamar**

---

## 📄 License

MIT License

---

<div align="center">
Made with ❤️ for farmers of Pakistan 🌾
</div>
