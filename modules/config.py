"""
TMDb API Configuration
TMDb API anahtarı yapılandırma dosyası
"""

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))

TMDB_API_KEY = os.getenv('TMDB_API_KEY')
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'

def get_tmdb_config():
    """
    TMDb API yapılandırma bilgilerini döndürür
    """
    if not TMDB_API_KEY:
        raise ValueError(
            "TMDb API anahtarı bulunamadı!\n"
            "Lütfen aşağıdaki adımları izleyin:\n"
            "1. https://www.themoviedb.org/ adresine gidin\n"
            "2. Hesap oluşturun veya giriş yapın\n"
            "3. Account Settings > API > Request an API Key\n"
            "4. Developer olarak kabul edin\n"
            "5. API anahtarınızı config/.env dosyasına ekleyin:\n"
            "   TMDB_API_KEY=sizin_api_anahtariniz"
        )
    
    return {
        'api_key': TMDB_API_KEY,
        'base_url': TMDB_BASE_URL,
        'image_base_url': TMDB_IMAGE_BASE_URL
    }

if __name__ == "__main__":
    try:
        config = get_tmdb_config()
        print(f"API Key configured: {config['api_key'][:10]}...")
    except ValueError as e:
        print(f"Configuration error: {e}")