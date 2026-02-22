import requests
from config import KINOPOISK_TOKEN

class KinopoiskAPI:
    BASE_URL = "https://api.kinopoisk.dev/v1.4/movie"
    
    def __init__(self):
        self.headers = {
            "X-API-KEY": KINOPOISK_TOKEN
        }
    
    def search_movie(self, title, year=None):
        """Поиск фильма по названию и году"""
        params = {
            "query": title,
            "limit": 5
        }
        
        if year:
            params["selectFields"] = ["name", "year", "id", "rating", "poster", "videos"]
            params["year"] = year
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/search",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json().get("docs", [])
            else:
                print(f"Ошибка API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return []
    
    def get_movie_links(self, movie_id):
        """Получение ссылок на фильм по ID"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/{movie_id}",
                headers=self.headers,
                params={
                    "selectFields": ["videos", "externalId"]
                }
            )
            
            if response.status_code == 200:
                movie_data = response.json()
                return self._extract_links(movie_data)
            return []
            
        except Exception as e:
            print(f"Ошибка при получении ссылок: {e}")
            return []
    
    def _extract_links(self, movie_data):
        """Извлечение ссылок из данных фильма"""
        links = []
        
        # Ссылки на трейлеры
        if "videos" in movie_data and "trailers" in movie_data["videos"]:
            for trailer in movie_data["videos"]["trailers"][:3]:  # Берем первые 3 трейлера
                if "url" in trailer:
                    links.append({
                        "type": "Трейлер",
                        "name": trailer.get("name", "Трейлер"),
                        "url": trailer["url"]
                    })
        
        # Ссылка на Кинопоиск
        if "externalId" in movie_data and "kpHD" in movie_data["externalId"]:
            links.append({
                "type": "Кинопоиск",
                "name": "Смотреть на Кинопоиске",
                "url": f"https://hd.kinopoisk.ru/film/{movie_data['externalId']['kpHD']}"
            })
        
        # Ссылка на IMDB если есть
        if "externalId" in movie_data and "imdb" in movie_data["externalId"]:
            links.append({
                "type": "IMDb",
                "name": "Страница на IMDb",
                "url": f"https://www.imdb.com/title/{movie_data['externalId']['imdb']}/"
            })
        
        return links