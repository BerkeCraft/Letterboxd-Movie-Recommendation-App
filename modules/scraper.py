"""
Letterboxd Profile Scraper (RSS-based)
Kullanıcının Letterboxd profilinden izlenilen ve puanlanan filmleri RSS üzerinden çeker
"""

import requests
import xml.etree.ElementTree as ET
import re
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from datetime import datetime

class LetterboxdScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        self.session.headers.update(self.headers)
    
    def validate_letterboxd_url(self, url):
        """
        URL'nin geçerli bir Letterboxd profil URL'si olup olmadığını kontrol eder
        """
        parsed = urlparse(url)
        valid_domains = ['letterboxd.com', 'www.letterboxd.com']
        
        if parsed.netloc not in valid_domains:
            return False
        
        # Profil URL'si formatı: letterboxd.com/username/
        path_parts = parsed.path.strip('/').split('/')
        return len(path_parts) == 1 and path_parts[0] != ''
    
    def get_username_from_url(self, url):
        """
        URL'den kullanıcı adını çıkarır
        """
        parsed = urlparse(url)
        return parsed.path.strip('/').split('/')[0]
    
    def extract_rating_from_title(self, title):
        """
        Başlıktan puanı çıkarır (örn: "Film Adı, 2020 - ★★★★")
        """
        # Star rating pattern
        star_pattern = r'[-—]\s*([★½]+)\s*$'
        star_match = re.search(star_pattern, title)
        
        if star_match:
            stars = star_match.group(1)
            # Yıldızları sayıya çevir
            full_stars = stars.count('★')
            half_star = stars.count('½')
            return full_stars + half_star * 0.5
        
        return None
    
    def extract_film_info_from_title(self, title):
        """
        Başlıktan film adı ve yılı çıkarır
        """
        # Pattern: "Film Adı, YYYY - Rating"
        main_pattern = r'^(.+?),\s*(\d{4})\s*[-—]'
        match = re.match(main_pattern, title)
        
        if match:
            film_title = match.group(1).strip()
            year = int(match.group(2))
            return film_title, year
        
        return None, None
    
    def scrape_rss_feed(self, username, max_pages=5):
        """
        RSS feed'den film verilerini çeker (çoklu sayfa desteği)
        """
        rss_url = f"https://letterboxd.com/{username}/rss/"
        
        try:
            response = self.session.get(rss_url, timeout=15)
            response.raise_for_status()
            
            # XML parse et
            root = ET.fromstring(response.content)
            
            # Namespace handling
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'letterboxd': 'https://letterboxd.com',
                'tmdb': 'https://themoviedb.org'
            }
            
            films = []
            items = root.findall('.//item')
            
            for item in items:
                try:
                    film_data = self.parse_rss_item(item, namespaces)
                    if film_data and film_data.get('rating'):
                        films.append(film_data)
                except Exception as e:
                    print(f"RSS item parse hatası: {e}")
                    continue
            
            print(f"RSS'ten {len(films)} film bulundu")
            return films
            
        except requests.RequestException as e:
            raise Exception(f"RSS feed çekilemedi: {e}")
        except ET.ParseError as e:
            raise Exception(f"RSS XML parse hatası: {e}")
        except Exception as e:
            raise Exception(f"RSS işlenirken hata: {e}")
    
    def scrape_additional_pages(self, username, start_count=0):
        """
        Ek sayfalardan film çekmek için (RSS'in yetersiz olduğu durumlarda)
        """
        additional_films = []
        
        # Farklı sayfalardan dene
        for page in range(1, 6):  # Max 5 ek sayfa
            try:
                time.sleep(1)  # Rate limiting
                
                page_url = f"https://letterboxd.com/{username}/films/page/{page}/"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (compatible; FilmRecommender/1.0)',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'no-cache'
                }
                
                response = self.session.get(page_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Film elementlerini bul
                    film_elements = soup.find_all('li', class_='poster-container')
                    
                    for film_element in film_elements:
                        try:
                            film_data = self.extract_film_data_from_page(film_element)
                            if film_data:
                                additional_films.append(film_data)
                        except Exception:
                            continue
                    
                    print(f"Sayfa {page} üzerinden {len(film_elements)} film bulundu")
                    
                elif response.status_code == 429:  # Rate limit
                    print(f"Rate limit, sayfa {page} atlanıyor")
                    break
                    
            except Exception as e:
                print(f"Sayfa {page} çekilemedi: {e}")
                continue
        
        # Yeni filmleri mevcut listeye ekle
        return additional_films
    
    def extract_film_data_from_page(self, film_element):
        """
        HTML sayfasından film verisi çıkarır
        """
        try:
            film_data = {}
            
            # Film linki
            link_elem = film_element.find('a')
            if link_elem:
                href = link_elem.get('href', '')
                film_data['url'] = urljoin('https://letterboxd.com', href)
            
            # Film adı
            img_elem = film_element.find('img')
            if img_elem:
                title = img_elem.get('alt', '').strip()
                film_data['title'] = title
            
            # Puanı bul
            rating_elem = film_element.find(['span'], class_='rating')
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                # Puanı sayıya çevir
                rating = self.extract_rating_from_text(rating_text)
                if rating:
                    film_data['rating'] = rating
            
            # Yıl bilgisini bul
            year_elem = film_element.find(['span', 'small'], string=re.compile(r'\b(19|20)\d{2}\b'))
            if year_elem:
                year_text = year_elem.get_text(strip=True)
                year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
                if year_match:
                    film_data['year'] = int(year_match.group())
            
            return film_data if film_data.get('title') and film_data.get('rating') else None
            
        except Exception:
            return None
    
    def extract_rating_from_text(self, text):
        """
        Metinden puan çıkarır
        """
        # Star pattern
        if '★' in text:
            star_count = text.count('★')
            half_star = text.count('½')
            return star_count + half_star * 0.5
        
        # Number pattern
        number_match = re.search(r'(\d+\.?\d*)', text)
        if number_match:
            try:
                return float(number_match.group(1))
            except:
                pass
        
        # Text patterns
        if any(word in text.lower() for word in ['half', '½']):
            return 0.5
        elif any(word in text.lower() for word in ['one', '1', 'bir']):
            return 1.0
        elif any(word in text.lower() for word in ['two', '2', 'iki']):
            return 2.0
        elif any(word in text.lower() for word in ['three', '3', 'üç']):
            return 3.0
        elif any(word in text.lower() for word in ['four', '4', 'dört']):
            return 4.0
        elif any(word in text.lower() for word in ['five', '5', 'beş']):
            return 5.0
        
        return None
    
    def parse_rss_item(self, item, namespaces):
        """
        RSS item'ından film verilerini çıkarır
        """
        # Title elementinden bilgileri çıkar
        title_elem = item.find('title')
        if title_elem is None:
            return None
        
        title_text = title_elem.text or ""
        
        # Puanı çıkar
        rating = self.extract_rating_from_title(title_text)
        if not rating:
            return None  # Sadece puanlanmış filmleri işle
        
        # Film adı ve yıl
        film_title, year = self.extract_film_info_from_title(title_text)
        if not film_title:
            return None
        
        # TMDb ID'yi daha doğru şekilde al
        tmdb_id_elem = item.find('.//tmdb:movieId', namespaces)
        tmdb_id = tmdb_id_elem.text if tmdb_id_elem is not None else None
        
        # Watched date
        watched_date_elem = item.find('.//letterboxd:watchedDate', namespaces)
        watched_date = watched_date_elem.text if watched_date_elem is not None else None
        
        # Rewatch flag
        rewatch_elem = item.find('.//letterboxd:rewatch', namespaces)
        is_rewatch = rewatch_elem.text == 'Yes' if rewatch_elem is not None else False
        
        film_data = {
            'title': film_title,
            'year': year,
            'rating': rating,
            'url': self.get_element_text(item, 'link'),
            'review_id': self.get_element_text(item, 'guid'),
            'watched_date': watched_date,
            'is_rewatch': is_rewatch,
            'tmdb_id': int(tmdb_id) if tmdb_id and tmdb_id.isdigit() else None
        }
        
        # Description'dan poster URL'ini çıkar (varsa)
        description = self.get_element_text(item, 'description')
        if description:
            poster_match = re.search(r'<img src="([^"]+)"', description)
            if poster_match:
                film_data['poster_url'] = poster_match.group(1)
        
        return film_data
    
    def get_element_text(self, element, tag, namespaces=None):
        """
        XML elementinin metin içeriğini güvenli şekilde alır
        """
        try:
            if namespaces:
                found = element.find(f'.//{{{namespaces.get(tag.split(":")[0], "")}}}{tag}')
            else:
                found = element.find(tag)
            
            return found.text if found is not None else None
        except Exception:
            return None
    
    def get_all_rated_films(self, username):
        """
        Kullanıcının tüm puanladığı filmleri RSS + ek sayfalardan çeker
        """
        try:
            print(f"RSS feed taranıyor: {username}")
            films = self.scrape_rss_feed(username)
            
            # RSS'ten az film geldiyse ek sayfalardan dene
            if len(films) < 20:  # Eğer 20'den az film geldiyse
                print("RSS filmleri yetersiz, ek sayfalardan deneniyor...")
                additional_films = self.scrape_additional_pages(username, len(films))
                
                # Yeni filmleri ekle, duplicate'ları temizle
                existing_titles = {f.get('title', '') + str(f.get('year', '')) for f in films}
                
                for new_film in additional_films:
                    film_key = new_film.get('title', '') + str(new_film.get('year', ''))
                    if film_key not in existing_titles and new_film.get('rating'):
                        films.append(new_film)
                        existing_titles.add(film_key)
                
                print(f"Toplam {len(films)} film bulundu (RSS + ek sayfalar)")
            else:
                print(f"Toplam {len(films)} film bulundu (sadece RSS)")
            
            # Puanlara göre sırala (en yüksekten en düşüğe)
            films.sort(key=lambda x: x.get('rating', 0), reverse=True)
            
            return films
            
        except Exception as e:
            raise Exception(f"Film verisi alınırken hata: {e}")
    
    def scrape_profile(self, url):
        """
        Letterboxd profil URL'sinden tüm puanlanmış filmleri çeker
        """
        if not self.validate_letterboxd_url(url):
            raise ValueError("Geçersiz Letterboxd profil URL'si")
        
        username = self.get_username_from_url(url)
        
        try:
            all_films = self.get_all_rated_films(username)
            
            # 3+ puanlı filmleri filtrele
            high_rated_films = [
                film for film in all_films 
                if film.get('rating', 0) >= 3.0
            ]
            
            return {
                'username': username,
                'all_films': all_films,
                'high_rated_films': high_rated_films,
                'total_films': len(all_films),
                'high_rated_count': len(high_rated_films)
            }
            
        except Exception as e:
            raise Exception(f"Profil taranırken hata: {e}")

if __name__ == "__main__":
    # Test
    scraper = LetterboxdScraper()
    
    test_url = "https://letterboxd.com/berkecraft/"
    
    try:
        result = scraper.scrape_profile(test_url)
        print(f"Kullanıcı: {result['username']}")
        print(f"Toplam film: {result['total_films']}")
        print(f"3+ puanlı film: {result['high_rated_count']}")
        
        print("\n3+ puanlı filmler:")
        for film in result['high_rated_films']:
            print(f"- {film['title']} ({film.get('year', 'N/A')}) - Puan: {film['rating']} - TMDb ID: {film.get('tmdb_id', 'N/A')}")
            
    except Exception as e:
        print(f"Hata: {e}")