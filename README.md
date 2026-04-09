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

### 3. TMDb API Anahtarı
1. [TMDb](https://www.themoviedb.org/) hesabı oluşturun
2. Account Settings > API > Request an API Key
3. `config/.env` dosyasında `your_tmdb_api_key_here` kısmına kendi API anahtarınızı yapıştırın

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