import requests
import json
import os

# Cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "vh7t7ZZedA3BQfYbZn2X"

# --- BẢNG SỬA LỖI THỦ CÔNG ---
# Nếu TMDB tìm sai phim nào, bạn lấy ID trên web tmdb.org rồi điền vào đây.
# Ví dụ: "Tên phim cào được": ID_TMDB_CHUAN
MANUAL_MAPPING = {
    "Straight to Hell": 300529, # Thay số này bằng ID chuẩn của bản bạn muốn (Ví dụ ID: 242095)
}

def get_tmdb_by_id(tmdb_id, media_type="movie"):
    """Lấy thông tin trực tiếp nếu đã có ID"""
    url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={TMDB_API_KEY}&language=vi-VN"
    try:
        item = requests.get(url).json()
        full_date = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
        return {
            "title": item.get("title") or item.get("name"),
            "year": full_date[:4] if full_date else "N/A",
            "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
            "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
            "tmdb_id": item.get("id"),
            "type": media_type
        }
    except: return None

def get_tmdb(name, media_type="movie"):
    """Tìm kiếm với logic khớp tên tuyệt đối"""
    if not TMDB_API_KEY: return None
    
    # Bước 1: Kiểm tra xem có trong danh sách sửa lỗi thủ công không
    if name in MANUAL_MAPPING:
        print(f"📍 Sử dụng ID thủ công cho: {name}")
        return get_tmdb_by_id(MANUAL_MAPPING[name], media_type)

    # Bước 2: Nếu không có ID thủ công, tiến hành tìm kiếm
    endpoint = "movie" if media_type == "movie" else "tv"
    url = f"https://api.themoviedb.org/3/search/{endpoint}?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    
    try:
        res = requests.get(url).json()
        results = res.get('results', [])
        if not results: return None
            
        # Chiến thuật: Ưu tiên kết quả khớp tên 100% (không phân biệt hoa thường)
        best_match = results[0] # Mặc định lấy cái đầu tiên
        target_name = name.lower().strip()
        
        for item in results:
            item_name = (item.get("title") or item.get("name") or "").lower().strip()
            if item_name == target_name:
                best_match = item
                break 
        
        item = best_match
        full_date = item.get("release_date") if media_type == "movie" else item.get("first_air_date")
        return {
            "title": item.get("title") or item.get("name"),
            "year": full_date[:4] if full_date else "N/A",
            "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
            "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
            "tmdb_id": item.get("id"),
            "type": media_type
        }
    except: return None

def main():
    # Gọi Simplescraper (URL này sẽ kích hoạt việc cào mới)
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    print("🚀 Đang kích hoạt Simplescraper và lấy dữ liệu...")
    
    try:
        res = requests.get(url).json()
        raw_data = res.get("data", [])
        
        # Movies: STT 1-10 (Index 0-9) | TV Shows: STT 11-20 (Index 10-19)
        movies_raw = raw_data[0:10]
        tv_raw = raw_data[10:20]
        
        final_result = {"movies": [], "tv_shows": []}

        for i, item in enumerate(movies_raw, 1):
            name = item.get("tenphim", "").strip()
            if name:
                info = get_tmdb(name, "movie")
                data = info if info else {"title": name, "year": "N/A", "status": "no_tmdb"}
                data['rank'] = i
                final_result["movies"].append(data)

        for i, item in enumerate(tv_raw, 1):
            name = item.get("tenphim", "").strip()
            if name:
                info = get_tmdb(name, "tv")
                data = info if info else {"title": name, "year": "N/A", "status": "no_tmdb"}
                data['rank'] = i
                final_result["tv_shows"].append(data)

        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)
        print("✅ Đã cập nhật file top10.json thành công!")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    main()
