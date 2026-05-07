import requests
import json
import os

# Cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "B5UEdm8kEDFzwkFELx8X"

def get_tmdb(name):
    """Lấy ảnh và năm phát hành từ TMDB"""
    if not TMDB_API_KEY: return None
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    try:
        res = requests.get(url).json()
        if res.get('results'):
            item = res['results'][0]
            
            # Lấy ngày phát hành (release_date cho phim, first_air_date cho TV show)
            full_date = item.get("release_date") or item.get("first_air_date") or ""
            # Trích xuất lấy 4 chữ số đầu tiên (năm)
            year = full_date[:4] if full_date else "N/A"
            
            return {
                "title": item.get("title") or item.get("name"),
                "year": year, # Thêm trường năm phát hành
                "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
                "tmdb_id": item.get("id"),
                "type": item.get("media_type", "movie")
            }
    except:
        return None

def main():
    # Bước 1: Gọi Simplescraper lấy data trực tiếp
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    print("🚀 Đang lấy dữ liệu từ Simplescraper...")
    
    try:
        res = requests.get(url).json()
        raw_movies = res.get("data", [])
        names = [m.get("tenphim").strip() for m in raw_movies if m.get("tenphim")]
        
        final_data = []
        for i, name in enumerate(names[:10], 1):
            print(f"🔍 Đang tìm TMDB cho: {name}")
            info = get_tmdb(name)
            if info:
                info['rank'] = i
                final_data.append(info)
            else:
                final_data.append({"rank": i, "title": name, "year": "N/A", "status": "no_tmdb"})

        # Bước 2: Lưu vào file JSON
        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        print("✅ Thành công! File JSON hiện đã có thêm năm phát hành.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
