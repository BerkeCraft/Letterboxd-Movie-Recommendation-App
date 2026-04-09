# Letterboxd Film Öneri Uygulaması

## 🎬 Açıklama
Letterboxd profilinizi analiz ederek kişiselleştirilmiş film önerileri sunan Python/Tkinter tabanlı masaüstü uygulaması.

## 📋 Özellikler
- Letterboxd profilinden izlenilen ve puanlanan filmleri çekme
- TMDb API ile film verilerini zenginleştirme
- 3+ puanlı filmlere dayalı akıllı öneri algoritması
- Modern Tkinter arayüzü
- Max 10 film önerisi

## 🚀 Kurulum

### 1. Python Sanal Ortamı
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# veya
venv\Scripts\activate     # Windows
```

### 2. Gerekli Kütüphaneler
```bash
pip install -r requirements.txt
```

## 🎯 Kullanım
```bash
python main.py
```

## 📁 Proje Yapısı
```
├── modules/
│   ├── scraper.py     # Letterboxd web scraping
│   ├── tmdb_api.py    # TMDb entegrasyonu
│   ├── recommender.py # Öneri algoritması
│   └── ui.py          # Tkinter arayüzü
├── config/.env        # API anahtarı
├── main.py            # Ana uygulama
└── requirements.txt   # Gerekli paketler
```

Letterboxd Movie Recommendation App

🎬 Description
A Python/Tkinter-based desktop application that analyzes your Letterboxd profile and provides personalized movie recommendations.

📋 Features

Fetches watched and rated films from your Letterboxd profile
Enriches movie data using the TMDb API
Smart recommendation algorithm based on films rated 3+
Modern Tkinter user interface
Up to 10 movie recommendations

🚀 Installation

Python Virtual Environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate     # Windows
Required Libraries
pip install -r requirements.txt
TMDb API Key
Create a TMDb account
Go to Account Settings > API > Request an API Key
Paste your API key into config/.env in place of your_tmdb_api_key_here

🎯 Usage

python main.py

📁 Project Structure

├── modules/
│   ├── scraper.py     # Letterboxd web scraping
│   ├── tmdb_api.py    # TMDb integration
│   ├── recommender.py # Recommendation algorithm
│   └── ui.py          # Tkinter interface
├── config/.env        # API key
├── main.py            # Main application
└── requirements.txt   # Required packages
```
