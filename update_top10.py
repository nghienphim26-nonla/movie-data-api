import requests
import json
import os
from datetime import datetime # Thêm thư viện này để xử lý ngày tháng

# Cấu hình
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "Zz67Ecf797JnW1lbvwl7"

def get_tmdb(name, media_type="movie"):
    """Lấy thông tin từ TMDB và chọn phim có năm sản xuất mới nhất"""
    if not TMDB_API_KEY: return None
    endpoint = "movie" if media_type == "movie" else "tv"
    url = f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    
    try:
        res = requests.get(url).json()
        results = res.get('results', [])
        
        if not results:
            return None
            
        latest_item = None
        latest_date = None

        for item in results:
            # TMDB dùng 'release_date' cho movie và 'first_air_date' cho tv
            date_str = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
            
            if date_str:
                try:
                    # Chuyển chuỗi 'YYYY-MM-DD' thành đối tượng datetime để so sánh chính xác
                    current_date = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # Nếu chưa có phim nào hoặc phim này mới hơn phim đã lưu
                    if latest_date is None or current_date > latest_date:
                        latest_date = current_date
                        latest_item = item
                except ValueError:
                    # Bỏ qua nếu chuỗi ngày tháng không đúng định dạng (ví dụ: bị rỗng hoặc lỗi)
                    continue
        
        # Nếu duyệt xong mà không tìm thấy phim nào có ngày hợp lệ, lấy đại phần tử đầu tiên
        if not latest_item:
            latest_item = results[0]
            
        full_date = latest_item.get("release_date") if media_type == "movie" else latest_item.get("first_air_date")
        year = full_date[:4] if full_date else "N/A"
        
        return {
            "title": latest_item.get("title") or latest_item.get("name"),
            "year": year,
            "poster": f"https://image.tmdb.org/t/p/w500{latest_item.get('poster_path')}" if latest_item.get('poster_path') else None,
            "backdrop": f"https://image.tmdb.org/t/p/original{latest_item.get('backdrop_path')}" if latest_item.get('backdrop_path') else None,
            "tmdb_id": latest_item.get("id"),
            "type": media_type
        }
    except Exception as e:
        # print(f"Lỗi khi tìm {name}: {e}") # Bật lên nếu bạn muốn debug
        return None

def main():
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    print("🚀 Đang lấy dữ liệu từ Simplescraper...")
    
    try:
        res = requests.get(url).json()
        raw_data = res.get("data", [])
        
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
                data['rank'] = i
                final_result["tv_shows"].append(data)

        # Lưu vào file JSON
        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)
        print("✅ Đã cập nhật xong file top10.json!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
