"""
TMDb API Integration
Film arama, detayları ve benzer filmler için TMDb API entegrasyonu
"""

import requests
from .config import get_tmdb_config
import time
from threading import Lock

class TMDBAPI:
    def __init__(self):
        self.config = get_tmdb_config()
        self.api_key = self.config['api_key']
        self.base_url = self.config['base_url']
        self.image_base_url = self.config['image_base_url']
        
        # API rate limiting için thread-safe implementation
        self._rate_limit_lock = Lock()
        self.last_request_time = 0
        self.min_request_interval = 0.25  # 250ms (4 requests per second to be safe)
    
    def _make_request(self, endpoint, params=None):
        """
        API request'i yapar, thread-safe rate limiting uygular
        """
        # Thread-safe rate limiting
        with self._rate_limit_lock:
            current_time = time.time()
            if current_time - self.last_request_time < self.min_request_interval:
                time.sleep(self.min_request_interval - (current_time - self.last_request_time))
            
            url = f"{self.base_url}/{endpoint}"
            
            default_params = {
                'api_key': self.api_key,
                'language': 'en-US'
            }
            
            if params:
                default_params.update(params)
            
            try:
                response = requests.get(url, params=default_params, timeout=10)
                response.raise_for_status()
                self.last_request_time = time.time()
                return response.json()
            except requests.RequestException as e:
                raise Exception(f"TMDb API request failed: {e}")
    
    def search_movie(self, title, year=None):
        """
        Film başlığına göre film arar
        """
        params = {
            'query': title,
            'page': 1
        }
        
        if year:
            params['year'] = year
        
        try:
            data = self._make_request('search/movie', params)
            
            if data.get('results') and len(data['results']) > 0:
                # İlk sonucu al ve detaylı bilgileri çek
                result = data['results'][0]
                movie_id = result.get('id')
                
                if movie_id:
                    # Detaylı bilgileri çek (genre'ler için)
                    detailed_data = self._make_request(f'movie/{movie_id}')
                    if detailed_data:
                        result.update(detailed_data)
                
                return self._format_movie_data(result)
            
            return None
            
        except Exception as e:
            print(f"Film arama hatası ({title}): {e}")
            return None
    
    def get_movie_details(self, movie_id):
        """
        Film ID'sine göre film detaylarını çeker
        """
        try:
            data = self._make_request(f'movie/{movie_id}')
            return self._format_movie_data(data)
        except Exception as e:
            print(f"Film detayları hatası ({movie_id}): {e}")
            return None
    
    def get_similar_movies(self, movie_id, max_results=10):
        """
        Benzer filmleri çeker
        """
        params = {'page': 1}
        
        try:
            data = self._make_request(f'movie/{movie_id}/similar', params)
            
            similar_movies = []
            for result in data.get('results', [])[:max_results]:
                movie_data = self._format_movie_data(result)
                if movie_data:
                    similar_movies.append(movie_data)
            
            return similar_movies
            
        except Exception as e:
            print(f"Benzer filmler hatası ({movie_id}): {e}")
            return []
    
    def _format_movie_data(self, raw_data):
        """
        TMDb API verisini standart formata dönüştürür
        """
        if not raw_data:
            return None
        
        return {
            'id': raw_data.get('id'),
            'title': raw_data.get('title', ''),
            'original_title': raw_data.get('original_title', ''),
            'overview': raw_data.get('overview', ''),
            'release_date': raw_data.get('release_date', ''),
            'year': self._extract_year(raw_data.get('release_date')),
            'vote_average': raw_data.get('vote_average', 0),
            'vote_count': raw_data.get('vote_count', 0),
            'popularity': raw_data.get('popularity', 0),
            'genres': [genre['name'] for genre in raw_data.get('genres', [])],
            'poster_path': raw_data.get('poster_path'),
            'backdrop_path': raw_data.get('backdrop_path'),
            'poster_url': self._get_image_url(raw_data.get('poster_path')),
            'tmdb_url': f"https://www.themoviedb.org/movie/{raw_data.get('id')}"
        }
    
    def _extract_year(self, release_date):
        """
        Release date'den yılı çıkarır
        """
        if release_date and len(release_date) >= 4:
            try:
                return int(release_date[:4])
            except ValueError:
                pass
        return None
    
    def _get_image_url(self, path, size='w500'):
        """
        Poster URL'ini oluşturur
        """
        if path:
            return f"https://image.tmdb.org/t/p/{size}{path}"
        return None
    
    def enrich_letterboxd_films(self, letterboxd_films):
        """
        Letterboxd film verilerini TMDb bilgileriyle zenginleştirir
        """
        enriched_films = []
        
        for film in letterboxd_films:
            title = film.get('title', '')
            year = film.get('year')
            
            if not title:
                continue
            
            print(f"TMDb'de aranyor: {title}")
            tmdb_data = self.search_movie(title, year)
            
            if tmdb_data:
                # Letterboxd verisi ile TMDb verisini birleştir
                enriched_film = {
                    **film,  # Letterboxd verileri
                    **tmdb_data  # TMDb verileri
                }
                enriched_films.append(enriched_film)
            else:
                # TMDb'de bulunamasa bile orijinal veriyi ekle
                enriched_films.append(film)
            
            time.sleep(0.1)  # Rate limiting
        
        return enriched_films
    
    def get_genre_recommendations(self, genre_names, min_vote_average=7.0, max_results=20):
        """
        Belirli türlerde yüksek puanlı filmler önerir
        """
        recommendations = []
        
        # Her genre için ayrı arama yap
        for genre in genre_names[:3]:  # Max 3 genre
            params = {
                'with_genres': genre,
                'vote_average.gte': min_vote_average,
                'sort_by': 'vote_average.desc',
                'page': 1
            }
            
            try:
                data = self._make_request('discover/movie', params)
                
                for result in data.get('results', []):
                    movie_data = self._format_movie_data(result)
                    if movie_data and movie_data not in recommendations:
                        recommendations.append(movie_data)
                        
                        if len(recommendations) >= max_results:
                            break
                            
            except Exception as e:
                print(f"Genre recommendation hatası ({genre}): {e}")
                continue
            
            if len(recommendations) >= max_results:
                break
        
        return recommendations[:max_results]

if __name__ == "__main__":
    # Test
    try:
        tmdb = TMDBAPI()
        
        # Film arama test
        movie = tmdb.search_movie("Inception", 2010)
        if movie:
            print(f"Film bulundu: {movie['title']} ({movie['year']})")
            print(f"Genre: {movie['genres']}")
            print(f"Puan: {movie['vote_average']}")
        
        # Benzer filmler test
        if movie:
            similar = tmdb.get_similar_movies(movie['id'])
            print(f"\nBenzer filmler:")
            for i, sim_movie in enumerate(similar[:3]):
                print(f"{i+1}. {sim_movie['title']} ({sim_movie['year']}) - Puan: {sim_movie['vote_average']}")
                
    except Exception as e:
        print(f"Test hatası: {e}")