import requests
import json
import os

# Cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "vh7t7ZZedA3BQfYbZn2X"

def get_tmdb(name, media_type="movie"):
    """Lấy thông tin từ TMDB dựa trên loại phim (movie hoặc tv)"""
    if not TMDB_API_KEY: return None
    
    # Sử dụng endpoint tìm kiếm riêng biệt để tăng độ chính xác
    endpoint = "movie" if media_type == "movie" else "tv"
    url = f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    
    try:
        res = requests.get(url).json()
        if res.get('results'):
            item = res['results'][0]
            
            # Lấy ngày phát hành tương ứng với loại nội dung [cite: 2]
            full_date = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
            year = full_date[:4] if full_date else "N/A"
            
            return {
                "title": item.get("title") or item.get("name"), [cite: 3]
                "year": year,
                "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
                "tmdb_id": item.get("id"),
                "type": media_type [cite: 4]
            }
    except:
        return None

def main():
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    print("🚀 Đang lấy dữ liệu từ Simplescraper...")
    
    try:
        res = requests.get(url).json()
        raw_data = res.get("data", []) [cite: 5]
        
        # Tách dữ liệu dựa trên chỉ số (index)
        # Movies: từ 1 đến 10 (index 0-9)
        # TV Shows: từ 11 đến 20 (index 10-19)
        movie_list = raw_data[0:10]
        tv_list = raw_data[10:20]
        
        final_result = {
            "movies": [],
            "tv_shows": []
        }

        # Xử lý danh sách Movies
        print("🎬 Đang xử lý danh sách Movies...")
        for i, item in enumerate(movie_list, 1):
            name = item.get("tenphim", "").strip()
            if name:
                info = get_tmdb(name, "movie")
                data = info if info else {"title": name, "year": "N/A", "status": "no_tmdb"}
                data['rank'] = i [cite: 6]
                final_result["movies"].append(data)

        # Xử lý danh sách TV Shows
        print("📺 Đang xử lý danh sách TV Shows...")
        for i, item in enumerate(tv_list, 1):
            name = item.get("tenphim", "").strip()
            if name:
                info = get_tmdb(name, "tv")
                data = info if info else {"title": name, "year": "N/A", "status": "no_tmdb"}
                data['rank'] = i 
                final_result["tv_shows"].append(data)

        # Lưu kết quả vào file JSON [cite: 7]
        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)
        
        print("✅ Thành công! Đã cập nhật Top 10 Movies và TV Shows.")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
