"""
Film Recommender
Letterboxd verilerine dayalı film öneri algoritması
"""

from collections import Counter
from .tmdb_api import TMDBAPI

class MovieRecommender:
    def __init__(self):
        self.tmdb = TMDBAPI()
        
    def analyze_user_preferences(self, high_rated_films):
        """
        Kullanıcının film tercihlerini analiz eder
        """
        if not high_rated_films:
            return {
                'favorite_genres': [],
                'preferred_decades': [],
                'rating_distribution': {},
                'total_films': 0
            }
        
        # Genre analizi
        all_genres = []
        for film in high_rated_films:
            genres = film.get('genres', [])
            if genres:
                all_genres.extend(genres)
        
        genre_counter = Counter(all_genres)
        favorite_genres = [genre for genre, count in genre_counter.most_common(5)]
        
        # On yıl analizi
        decades = []
        for film in high_rated_films:
            year = film.get('year')
            if year:
                decade = (year // 10) * 10
                decades.append(decade)
        
        decade_counter = Counter(decades)
        preferred_decades = [decade for decade, count in decade_counter.most_common(3)]
        
        # Puan dağılımı
        rating_distribution = Counter()
        for film in high_rated_films:
            rating = film.get('rating', 0)
            rating_distribution[rating] += 1
        
        return {
            'favorite_genres': favorite_genres,
            'preferred_decades': preferred_decades,
            'rating_distribution': dict(rating_distribution),
            'total_films': len(high_rated_films)
        }
    
    def get_similar_movies_for_user(self, high_rated_films, max_recommendations=10):
        """
        Kullanıcı için benzer filmler önerir
        """
        if not high_rated_films:
            return []
        
        recommendations = []
        processed_movie_ids = set()
        
        # Kullanıcının izlediği film ID'lerini sakla
        user_movie_ids = set()
        for film in high_rated_films:
            if film.get('id'):
                user_movie_ids.add(film['id'])
        
        # En yüksek puanlı filmlerden başla (max 5 film)
        sorted_films = sorted(
            [f for f in high_rated_films if f.get('id')], 
            key=lambda x: x.get('rating', 0), 
            reverse=True
        )[:5]
        
        for film in sorted_films:
            if film.get('id'):
                similar_movies = self.tmdb.get_similar_movies(
                    film['id'], 
                    max_results=20
                )
                
                for similar_movie in similar_movies:
                    movie_id = similar_movie.get('id')
                    
                    # Kullanıcının izlediği filmleri ve tekrarları çıkar
                    if (movie_id not in user_movie_ids and 
                        movie_id not in processed_movie_ids and
                        similar_movie.get('vote_average', 0) >= 6.5):
                        
                        # Öneri skorunu hesapla
                        score = self.calculate_recommendation_score(
                            film, similar_movie, high_rated_films
                        )
                        
                        recommendation = {
                            **similar_movie,
                            'recommendation_score': score,
                            'based_on_movie': film['title'],
                            'based_on_rating': film['rating']
                        }
                        
                        recommendations.append(recommendation)
                        processed_movie_ids.add(movie_id)
                        
                        if len(recommendations) >= max_recommendations:
                            break
                
                if len(recommendations) >= max_recommendations:
                    break
        
        # Skora göre sırala ve limit
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        return recommendations[:max_recommendations]
    
    def calculate_recommendation_score(self, user_film, candidate_movie, user_films):
        """
        Öneri skorunu hesaplar (0-100 arası)
        """
        score = 0
        
        # Temel TMDb puanı (30%)
        tmdb_score = candidate_movie.get('vote_average', 0)
        score += min(tmdb_score * 6, 30)  # Max 30 puan
        
        # Popülerlik (10%)
        popularity = candidate_movie.get('popularity', 0)
        score += min(popularity / 10, 10)  # Max 10 puan
        
        # Genre uyumu (35%)
        user_genres = set()
        for film in user_films:
            user_genres.update(film.get('genres', []))
        
        candidate_genres = set(candidate_movie.get('genres', []))
        genre_overlap = len(user_genres.intersection(candidate_genres))
        
        if candidate_genres and user_genres:
            genre_score = (genre_overlap / len(candidate_genres)) * 35
            score += genre_score
        
        # Yayın yılı yakınlığı (15%)
        user_film_year = user_film.get('year')
        candidate_year = candidate_movie.get('year')
        
        if user_film_year and candidate_year:
            year_diff = abs(user_film_year - candidate_year)
            if year_diff <= 5:
                score += 15
            elif year_diff <= 10:
                score += 10
            elif year_diff <= 20:
                score += 5
        
        # Film sayısı bonusu (10%)
        if len(user_films) >= 10:
            score += 10
        elif len(user_films) >= 5:
            score += 5
        
        return min(score, 100)
    
    def get_genre_based_recommendations(self, user_films, max_recommendations=10):
        """
        Genre bazlı öneriler (benzer filmer yetersizse)
        """
        # Tüm genre'leri topla
        all_genres = []
        for film in user_films:
            all_genres.extend(film.get('genres', []))
        
        if not all_genres:
            return []
        
        # En popüler genre'leri bul
        genre_counter = Counter(all_genres)
        top_genres = [genre for genre, count in genre_counter.most_common(3)]
        
        # Her genre için öneriler al
        recommendations = []
        for genre in top_genres:
            genre_recs = self.tmdb.get_genre_recommendations(
                [genre], 
                min_vote_average=6.5,
                max_results=5
            )
            
            for movie in genre_recs:
                movie['recommendation_score'] = 50  # Varsayılan skor
                movie['recommendation_reason'] = f"Genre: {genre}"
                recommendations.append(movie)
        
        # Skora göre sırala ve limit
        recommendations.sort(key=lambda x: x.get('vote_average', 0), reverse=True)
        return recommendations[:max_recommendations]
    
    def get_recommendations(self, high_rated_films, max_recommendations=20):
        """
        Geliştirilmiş öneri sistemi - çeşitli kaynaklardan dengeli öneriler
        Tüm filmleri (düşük puanlılar dahil) kontrol ederek öneri yapar
        """
        if not high_rated_films:
            return []
        
        # Film sayısına göre öneri sayısını ayarla
        total_films = len(high_rated_films)
        
        if total_films < 5:
            rec_count = 8
        elif total_films < 10:
            rec_count = 12
        elif total_films < 20:
            rec_count = 15
        elif total_films < 50:
            rec_count = 18
        else:
            rec_count = max_recommendations
        
        print(f"Film sayısına göre {rec_count} öneri hazırlanıyor (toplam {total_films} film)")
        
        # Tercihleri analiz et
        preferences = self.analyze_user_preferences(high_rated_films)
        
        # Öneri kaynaklarından filmler topla
        all_recommendations = []
        
        # 1. Genre bazlı öneriler (%35 ağırlık)
        genre_count = max(3, rec_count // 4)
        genre_recs = self.get_diverse_genre_recommendations(
            high_rated_films, 
            preferences,
            genre_count
        )
        for movie in genre_recs:
            movie['source'] = 'genre'
            movie['recommendation_score'] = 55 + movie.get('vote_average', 0) * 4
        all_recommendations.extend(genre_recs)
        
        # 2. Benzer filmler (%30 ağırlık) - ama çeşitli filmlerden
        similar_count = max(3, rec_count // 4)
        similar_recs = self.get_diverse_similar_movies(
            high_rated_films,
            similar_count
        )
        for movie in similar_recs:
            movie['source'] = 'similar'
            movie['recommendation_score'] = 50 + movie.get('vote_average', 0) * 3
        all_recommendations.extend(similar_recs)
        
        # 3. Popüler ve yüksek puanlı filmler (%25 ağırlık)
        popular_count = max(2, rec_count // 5)
        popular_recs = self.get_popular_recommendations(
            preferences,
            popular_count
        )
        for movie in popular_recs:
            movie['source'] = 'popular'
            movie['recommendation_score'] = 45 + movie.get('vote_average', 0) * 5
        all_recommendations.extend(popular_recs)
        
        # 4. Keşfet - farklı türlerden filmler (%10 ağırlık)
        discovery_count = max(2, rec_count // 6)
        discovery_recs = self.get_discovery_recommendations(
            preferences,
            discovery_count
        )
        for movie in discovery_recs:
            movie['source'] = 'discovery'
            movie['recommendation_score'] = 40 + movie.get('vote_average', 0) * 2
        all_recommendations.extend(discovery_recs)
        
        # 5. Bonus - daha fazla film için çeşitlilik
        if len(all_recommendations) < rec_count and total_films >= 10:
            bonus_count = rec_count - len(all_recommendations)
            bonus_recs = self.get_bonus_recommendations(preferences, bonus_count)
            for movie in bonus_recs:
                movie['source'] = 'bonus'
                movie['recommendation_score'] = 35 + movie.get('vote_average', 0) * 3
            all_recommendations.extend(bonus_recs)
        
        # Tekrarları ve tüm kullanıcı filmlerini temizle
        unique_recommendations = self.remove_duplicates(all_recommendations, high_rated_films)
        
        # Skora göre sırala ve limit
        unique_recommendations.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
        return unique_recommendations[:rec_count]
    
    def get_bonus_recommendations(self, preferences, max_results):
        """
        Ek çeşitlilik için bonus öneriler
        """
        recommendations = []
        import random
        
        # Kullanıcı için unique seed
        random.seed(hash(str(preferences['favorite_genres']) + "bonus"))
        
        # Farklı kategoriler
        bonus_configs = [
            {
                'name': 'Kült Klasikleri',
                'params': {
                    'with_genres': '18',  # Drama
                    'sort_by': 'vote_average.desc',
                    'vote_average.gte': 7.0,
                    'primary_release_date.lte': '1980-12-31',
                    'page': random.randint(1, 2)
                }
            },
            {
                'name': 'Ödüllü Filmler',
                'params': {
                    'with_credits': 'crew.person.id=7624',  # Oscar kazananlar
                    'sort_by': 'vote_average.desc',
                    'vote_average.gte': 6.5,
                    'page': random.randint(1, 2)
                }
            },
            {
                'name': 'Belgesel Denemeleri',
                'params': {
                    'with_genres': '99',  # Documentary
                    'sort_by': 'vote_average.desc',
                    'vote_average.gte': 7.0,
                    'vote_count.gte': 100,
                    'page': random.randint(1, 2)
                }
            }
        ]
        
        random.shuffle(bonus_configs)
        
        for config in bonus_configs[:2]:  # Max 2 kategori
            if len(recommendations) >= max_results:
                break
                
            try:
                data = self.tmdb._make_request('discover/movie', config['params'])
                movies = data.get('results', [])
                
                random.shuffle(movies)
                
                for movie in movies[:2]:  # Her kategoriden 2 film
                    if len(recommendations) >= max_results:
                        break
                    
                    movie_data = self.tmdb._format_movie_data(movie)
                    if movie_data and movie_data.get('vote_average', 0) >= 6.5:
                        movie_data['bonus_category'] = config['name']
                        recommendations.append(movie_data)
                        
            except Exception:
                continue
        
        return recommendations[:max_results]
    
    def get_diverse_genre_recommendations(self, high_rated_films, preferences, max_results):
        """
        Çeşitli genre'lerden kişiselleştirilmiş öneriler
        """
        if not preferences['favorite_genres']:
            return self.get_popular_recommendations(preferences, max_results)
        
        recommendations = []
        processed_movies = set()
        
        # Her kullanıcı için unique random seed
        import random
        random.seed(hash(preferences['favorite_genres'][0] + str(len(high_rated_films))))
        
        # Tüm genre'leri kullan ama sevilenleri önceliklendir
        all_genres = preferences['favorite_genres']
        
        # Genre'leri rastgele karıştır ama sevilenleri başa al
        top_genres = all_genres[:2]  # En sevilen 2 genre
        other_genres = all_genres[2:]  # Diğerleri
        
        # Toplam 5 genre kullan
        additional_genres = ['Drama', 'Comedy', 'Action', 'Thriller', 'Animation', 'Romance', 'Horror']
        available_other_genres = [g for g in additional_genres if g not in top_genres]
        other_genres.extend(random.sample(available_other_genres, min(3, len(available_other_genres))))
        
        selected_genres = top_genres + other_genres
        random.shuffle(selected_genres)
        
        # Her genre için farklı yıllardan ve sıralamalardan filmler çek
        for genre in selected_genres[:5]:  # Max 5 genre
            if len(recommendations) >= max_results:
                break
            
            genre_id = self.get_genre_id(genre)
            if not genre_id:
                continue
            
            # Farklı parametreler için aramalar
            search_configs = [
                # En yüksek puanlılar
                {
                    'with_genres': genre_id,
                    'vote_average.gte': 7.5,
                    'vote_count.gte': 500,
                    'sort_by': 'vote_average.desc'
                },
                # Popüler yeni filmler
                {
                    'with_genres': genre_id,
                    'primary_release_date.gte': '2020-01-01',
                    'vote_average.gte': 6.5,
                    'vote_count.gte': 300,
                    'sort_by': 'popularity.desc'
                },
                # Klasikler
                {
                    'with_genres': genre_id,
                    'primary_release_date.lte': '2000-12-31',
                    'vote_average.gte': 7.0,
                    'vote_count.gte': 200,
                    'sort_by': 'vote_average.desc'
                },
                # Gizli mücevherler
                {
                    'with_genres': genre_id,
                    'vote_average.gte': 7.0,
                    'vote_count.gte': 50,
                    'vote_count.lte': 500,  # Çok popüler olmayanlar
                    'sort_by': 'vote_average.desc'
                }
            ]
            
            # Her genre için 2 farklı arama dene
            random.shuffle(search_configs)
            
            for config in search_configs[:2]:
                if len(recommendations) >= max_results:
                    break
                
                try:
                    # Rastgele page (1-3 arası)
                    config['page'] = random.randint(1, 3)
                    
                    data = self.tmdb._make_request('discover/movie', config)
                    movies = data.get('results', [])
                    
                    # Rastgele 2 film seç
                    random.shuffle(movies)
                    
                    for movie in movies[:2]:
                        if len(recommendations) >= max_results:
                            break
                        
                        movie_id = movie.get('id')
                        if movie_id and movie_id not in processed_movies:
                            
                            movie_data = self.tmdb._format_movie_data(movie)
                            if movie_data and movie_data.get('vote_average', 0) >= 6.0:
                                
                                # Movie'ı genre ile işaretle
                                movie_data['source_genre'] = genre
                                recommendations.append(movie_data)
                                processed_movies.add(movie_id)
                                
                except Exception:
                    continue
                
                if len(recommendations) >= max_results:
                    break
        
        # Sonuçları karıştır
        random.shuffle(recommendations)
        return recommendations[:max_results]
    
    def get_diverse_similar_movies(self, high_rated_films, max_results):
        """
        Çeşitli filmlerden benzer öneriler (tek filme odaklanmadan)
        """
        recommendations = []
        processed_ids = set()
        
        # Puanlara göre gruplandır
        high_rated = [f for f in high_rated_films if f.get('rating', 0) >= 4.0]
        medium_rated = [f for f in high_rated_films if 3.0 <= f.get('rating', 0) < 4.0]
        
        # Her gruptan farklı filmler seç
        selected_films = []
        
        # En yüksek puanlılardan 2 film
        selected_films.extend(high_rated[:2])
        
        # Orta puanlılardan 2 film  
        selected_films.extend(medium_rated[:2])
        
        for film in selected_films[:4]:  # Max 4 film
            if film.get('id') and film['id'] not in processed_ids:
                try:
                    similar_movies = self.tmdb.get_similar_movies(film['id'], max_results=5)
                    
                    for movie in similar_movies:
                        if (movie.get('id') not in processed_ids and 
                            len(recommendations) < max_results and
                            movie.get('vote_average', 0) >= 6.0):
                            
                            recommendations.append(movie)
                            processed_ids.add(movie.get('id'))
                            
                except Exception:
                    continue
        
        return recommendations
    
    def get_popular_recommendations(self, preferences, max_results):
        """
        Kişiselleştirilmiş popüler filmler
        """
        recommendations = []
        import random
        
        # Kullanıcı için unique seed
        user_seed = hash(str(preferences['favorite_genres']) + str(preferences['preferred_decades']))
        random.seed(user_seed)
        
        # Farklı popüler kategorileri
        pop_configs = [
            {
                'name': 'Bu Yıl Popülerleri',
                'params': {
                    'primary_release_date.gte': '2024-01-01',
                    'sort_by': 'popularity.desc',
                    'vote_average.gte': 6.5,
                    'vote_count.gte': 100
                }
            },
            {
                'name': 'Tüm Zamanların En İyileri',
                'params': {
                    'sort_by': 'vote_average.desc',
                    'vote_average.gte': 7.5,
                    'vote_count.gte': 500
                }
            },
            {
                'name': 'Eleştirmen Seçkileri',
                'params': {
                    'sort_by': 'vote_average.desc',
                    'vote_average.gte': 7.0,
                    'vote_count.gte': 50,
                    'vote_count.lte': 1000  # Sadece eleştirmenlerin sevdiği, çok popüler olmayan
                }
            }
        ]
        
        # Config'leri karıştır
        random.shuffle(pop_configs)
        
        for config in pop_configs:
            if len(recommendations) >= max_results:
                break
            
            try:
                # Kullanıcının tercih ettiği yılları dahil et
                if preferences['preferred_decades']:
                    # Tercih edilen on yılından film çek
                    preferred_decade = preferences['preferred_decades'][0]
                    decade_start = preferred_decade
                    decade_end = preferred_decade + 9
                    
                    params = config['params'].copy()
                    params.update({
                        'primary_release_date.gte': f"{decade_start}-01-01",
                        'primary_release_date.lte': f"{decade_end}-12-31",
                        'page': random.randint(1, 2)
                    })
                else:
                    params = config['params'].copy()
                    params['page'] = random.randint(1, 2)
                
                data = self.tmdb._make_request('discover/movie', params)
                movies = data.get('results', [])
                
                # Rastgele filmler seç
                random.shuffle(movies)
                
                for movie in movies[:2]:
                    if len(recommendations) >= max_results:
                        break
                    
                    movie_data = self.tmdb._format_movie_data(movie)
                    if movie_data and movie_data.get('vote_average', 0) >= 6.5:
                        movie_data['source_category'] = config['name']
                        recommendations.append(movie_data)
                        
            except Exception:
                continue
        
        return recommendations[:max_results]
    
    def get_discovery_recommendations(self, preferences, max_results):
        """
        Kişiselleştirilmiş keşif filmleri - her kullanıcı için farklı
        """
        recommendations = []
        import random
        
        # Kullanıcı için unique seed oluştur
        user_seed = hash(str(preferences['favorite_genres']) + "discovery")
        random.seed(user_seed)
        
        # Tüm mevcut genre'ler
        all_genres = [
            'Action', 'Adventure', 'Animation', 'Comedy', 'Crime',
            'Documentary', 'Drama', 'Family', 'Fantasy', 'Horror',
            'Music', 'Mystery', 'Romance', 'Science Fiction',
            'Thriller', 'War', 'Western', 'History'
        ]
        
        user_genres = set(preferences.get('favorite_genres', []))
        
        # Keşif için kullanılabilecek genre'ler
        available_genres = [g for g in all_genres if g not in user_genres]
        
        # Her kullanıcı için farklı discovery stratejileri
        discovery_strategies = [
            {
                'name': 'Klasik Gizli Mücevherler',
                'params': {
                    'vote_average.gte': 7.5,
                    'vote_count.gte': 100,
                    'vote_count.lte': 1000,  # Çok popüler olmayan
                    'primary_release_date.lte': '2000-12-31',
                    'sort_by': 'vote_average.desc'
                }
            },
            {
                'name': 'Yeni Keşifler',
                'params': {
                    'vote_average.gte': 6.5,
                    'vote_count.gte': 50,
                    'primary_release_date.gte': '2020-01-01',
                    'sort_by': 'popularity.desc'
                }
            },
            {
                'name': 'Eleştirmen Favorileri',
                'params': {
                    'vote_average.gte': 7.0,
                    'vote_count.gte': 200,
                    'vote_count.lte': 2000,
                    'sort_by': 'vote_average.desc'
                }
            },
            {
                'name': 'Uluslararası Klasikler',
                'params': {
                    'vote_average.gte': 7.0,
                    'vote_count.gte': 150,
                    'with_original_language': 'fr,de,it,es,ja',  # Hollywood dışı
                    'sort_by': 'vote_average.desc'
                }
            }
        ]
        
        # Rastgele strateji seç
        random.shuffle(discovery_strategies)
        selected_strategy = discovery_strategies[0]
        
        print(f"Keşif stratejisi: {selected_strategy['name']}")
        
        # Kullanıcının tercih etmediği 3 rastgele genre seç
        random.shuffle(available_genres)
        selected_genres = available_genres[:3]
        
        for genre in selected_genres:
            if len(recommendations) >= max_results:
                break
            
            genre_id = self.get_genre_id(genre)
            if not genre_id:
                continue
            
            # Seçili strateji ile genre'i birleştir
            params = selected_strategy['params'].copy()
            params['with_genres'] = genre_id
            params['page'] = random.randint(1, 2)
            
            try:
                data = self.tmdb._make_request('discover/movie', params)
                movies = data.get('results', [])
                
                # Rastgele karıştır ve 1-2 film seç
                random.shuffle(movies)
                
                for movie in movies[:2]:
                    if len(recommendations) >= max_results:
                        break
                    
                    movie_data = self.tmdb._format_movie_data(movie)
                    if movie_data and movie_data.get('vote_average', 0) >= 6.0:
                        movie_data['discovery_strategy'] = selected_strategy['name']
                        movie_data['discovery_genre'] = genre
                        recommendations.append(movie_data)
                        
            except Exception as e:
                print(f"Discovery genre {genre} hatası: {e}")
                continue
        
        # Sonuçları karıştır
        random.shuffle(recommendations)
        return recommendations[:max_results]
    
    def get_genre_id(self, genre_name):
        """
        Genre adını TMDb ID'sine çevirir (basit mapping)
        """
        genre_mapping = {
            'Action': 28,
            'Adventure': 12,
            'Animation': 16,
            'Comedy': 35,
            'Crime': 80,
            'Documentary': 99,
            'Drama': 18,
            'Family': 10751,
            'Fantasy': 14,
            'History': 36,
            'Horror': 27,
            'Music': 10402,
            'Mystery': 9648,
            'Romance': 10749,
            'Science Fiction': 878,
            'TV Movie': 10770,
            'Thriller': 53,
            'War': 10752,
            'Western': 37
        }
        return genre_mapping.get(genre_name)
    
    def remove_duplicates(self, recommendations, user_films):
        """
        Tekrarları ve TÜM kullanıcı filmlerini (düşük puanlılar dahil) temizler
        """
        # Tüm kullanıcı filmlerinin ID'lerini al (yüksek ve düşük puanlılar)
        user_movie_ids = set()
        for film in user_films:
            if film.get('id'):
                user_movie_ids.add(film['id'])
            # Eğer TMDb ID yoksa, title+year kombinasyonu kontrol et
            elif film.get('title') and film.get('year'):
                user_movie_ids.add(f"{film['title']}_{film['year']}")
        
        seen_ids = set()
        unique_recommendations = []
        
        for movie in recommendations:
            movie_id = movie.get('id')
            movie_key = None
            
            if movie_id:
                # TMDb ID varsa direkt kontrol et
                if movie_id not in user_movie_ids and movie_id not in seen_ids:
                    unique_recommendations.append(movie)
                    seen_ids.add(movie_id)
            else:
                # TMDb ID yoksa title+year kombinasyonu kullan
                if movie.get('title') and movie.get('year'):
                    movie_key = f"{movie['title']}_{movie['year']}"
                    if movie_key not in user_movie_ids and movie_key not in seen_ids:
                        movie['movie_key'] = movie_key
                        unique_recommendations.append(movie)
                        seen_ids.add(movie_key)
        
        return unique_recommendations

if __name__ == "__main__":
    # Test
    recommender = MovieRecommender()
    
    # Örnek kullanıcı filmleri
    test_films = [
        {
            'title': 'Inception',
            'rating': 5,
            'year': 2010,
            'id': 27205,
            'genres': ['Action', 'Sci-Fi', 'Thriller']
        },
        {
            'title': 'The Dark Knight',
            'rating': 5,
            'year': 2008,
            'id': 155,
            'genres': ['Action', 'Crime', 'Drama']
        },
        {
            'title': 'Interstellar',
            'rating': 4,
            'year': 2014,
            'id': 157336,
            'genres': ['Adventure', 'Drama', 'Sci-Fi']
        }
    ]
    
    # Tercih analizi
    preferences = recommender.analyze_user_preferences(test_films)
    print("Kullanıcı Tercihleri:")
    print(f"Favori Genre'ler: {preferences['favorite_genres']}")
    print(f"Tercih Edilen Dönemler: {preferences['preferred_decades']}")
    print(f"Toplam Film: {preferences['total_films']}")
    
    # Öneriler
    recommendations = recommender.get_recommendations(test_films, 5)
    print(f"\nÖnerilen Filmler ({len(recommendations)}):")
    
    for i, movie in enumerate(recommendations, 1):
        print(f"\n{i}. {movie['title']} ({movie.get('year', 'N/A')})")
        print(f"   Puan: {movie.get('vote_average', 'N/A')}")
        print(f"   Genre'ler: {', '.join(movie.get('genres', []))}")
        print(f"   Öneri Skoru: {movie.get('recommendation_score', 0):.1f}")
        
        if 'based_on_movie' in movie:
            print(f"   Dayanak: {movie['based_on_movie']} ({movie['based_on_rating']}/5)")
        elif 'recommendation_reason' in movie:
            print(f"   Sebep: {movie['recommendation_reason']}")