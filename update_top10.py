import requests
import json
import os

# Cấu hình
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "vh7t7ZZedA3BQfYbZn2X"

def get_tmdb(name, media_type="movie"):
    """Lấy thông tin từ TMDB (phân loại movie/tv để tìm chính xác hơn)"""
    if not TMDB_API_KEY: return None
    endpoint = "movie" if media_type == "movie" else "tv"
    url = f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    try:
        res = requests.get(url).json()
        if res.get('results'):
            item = res['results'][0]
            full_date = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
            year = full_date[:4] if full_date else "N/A"
            return {
                "title": item.get("title") or item.get("name"),
                "year": year,
                "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
                "tmdb_id": item.get("id"),
                "type": media_type
            }
    except:
        return None

def main():
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    print("🚀 Đang lấy dữ liệu từ Simplescraper...")
    
    try:
        res = requests.get(url).json()
        raw_data = res.get("data", []) # Simplescraper trả về mảng tất cả các dòng
        
        # CHIA TÁCH DỮ LIỆU
        # STT 1-10 trên web = Index 0 đến 9 trong Python
        # STT 11-20 trên web = Index 10 đến 19 trong Python
        movies_raw = raw_data[0:10]
        tv_raw = raw_data[10:20]
        
        final_result = {"movies": [], "tv_shows": []}

        # Xử lý Movies
        print("🎬 Processing Movies (1-10)...")
        for i, item in enumerate(movies_raw, 1):
            name = item.get("tenphim", "").strip()
            if name:
                info = get_tmdb(name, "movie")
                data = info if info else {"title": name, "year": "N/A", "status": "no_tmdb"}
                data['rank'] = i
                final_result["movies"].append(data)

        # Xử lý TV Shows
        print("📺 Processing TV Shows (11-20)...")
        for i, item in enumerate(tv_raw, 1):
            name = item.get("tenphim", "").strip()
            if name:
                info = get_tmdb(name, "tv")
                data = info if info else {"title": name, "year": "N/A", "status": "no_tmdb"}
                data['rank'] = i # Rank vẫn đánh từ 1 cho danh sách TV riêng
                final_result["tv_shows"].append(data)

        # Lưu vào file JSON
        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)
        print("✅ Đã cập nhật xong file top10.json!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
