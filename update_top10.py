import requests
import time
import json
import os

# Lấy cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "Fd9BZ7Gxl59ooovbUyTQ"

def run_ss():
    """Kích hoạt Simplescraper"""
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            print("🚀 Đã ra lệnh cho Simplescraper. Đợi 60s để hoàn tất...")
            time.sleep(60)
            return True
    except: pass
    return False

def get_ss_data():
    """Lấy tên phim từ Simplescraper"""
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/last_run?apikey={SS_API_KEY}"
    try:
        data = requests.get(url).json().get("data", [])
        # Lấy cột 'title' hoặc 'name'. Hãy đảm bảo tên cột trong SS là 'title'
        return [item.get("title") for item in data if item.get("title")][:10]
    except: return []

def get_tmdb(name):
    """Lấy ảnh và info từ TMDB"""
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    try:
        res = requests.get(url).json()
        if res.get('results'):
            item = res['results'][0]
            return {
                "title": item.get("title") or item.get("name"),
                "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}",
                "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}",
                "id": item["id"],
                "type": item.get("media_type", "movie")
            }
    except: return None

def main():
    if run_ss():
        names = get_ss_data()
        print(f"🎬 Đã cào được: {names}")
        
        final_list = []
        for i, n in enumerate(names, 1):
            info = get_tmdb(n)
            if info:
                info['rank'] = i
                final_list.append(info)
        
        if final_list:
            with open('top10.json', 'w', encoding='utf-8') as f:
                json.dump(final_list, f, ensure_ascii=False, indent=4)
            print("✅ Đã cập nhật top10.json")

if __name__ == "__main__":
    main()
