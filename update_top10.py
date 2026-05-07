import requests
import time
import json
import os

# Cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "B5UEdm8kEDFzwkFELx8X"

def run_ss():
    """Kích hoạt Simplescraper"""
    if not SS_API_KEY:
        print("❌ Thiếu SIMPLESCRAPER_API_KEY")
        return False
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    try:
        res = requests.get(url)
        # In phản hồi để kiểm tra nếu lỗi
        print(f"📡 Phản hồi kích hoạt: {res.text}")
        if res.status_code == 200:
            print("🚀 Đã kích hoạt Simplescraper. Đợi 60s để máy chủ xử lý dữ liệu...")
            time.sleep(60)
            return True
    except Exception as e:
        print(f"❌ Lỗi kích hoạt: {e}")
    return False

def get_ss_data():
    """Lấy danh sách phim từ Simplescraper"""
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/last_run?apikey={SS_API_KEY}"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Simplescraper trả về mã lỗi: {response.status_code}")
            return []
            
        res = response.json()
        data = res.get("data", [])
        
        # Thử lấy cột 'tenphim', nếu không có thì thử lấy 'title' hoặc 'name'
        movie_names = []
        for item in data:
            name = item.get("tenphim") or item.get("title") or item.get("name")
            if name:
                movie_names.append(name.strip())
        
        return movie_names[:10]
    except Exception as e:
        print(f"❌ Lỗi phân tích dữ liệu JSON: {e}")
        return []

def get_tmdb(name):
    """Lấy ảnh từ TMDB"""
    if not TMDB_API_KEY: return None
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
    try:
        res = requests.get(url).json()
        if res.get('results'):
            item = res['results'][0]
            return {
                "title": item.get("title") or item.get("name"),
                "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
                "tmdb_id": item.get("id"),
                "type": item.get("media_type", "movie")
            }
    except:
        return None

def main():
    # Bước 1: Kích hoạt cào
    run_ss()
    
    # Bước 2: Lấy dữ liệu tên phim
    names = get_ss_data()
    print(f"🎬 Tên phim tìm thấy: {names}")
    
    if not names:
        print("❌ Không có dữ liệu phim. Hãy kiểm tra Recipe ID đã được Save và Run thành công trên Simplescraper chưa!")
        return

    # Bước 3: Mix với TMDB
    final_list = []
    for i, name in enumerate(names, 1):
        info = get_tmdb(name)
        if info:
            info['rank'] = i
            final_list.append(info)
        else:
            final_list.append({"title": name, "rank": i, "status": "no_tmdb_data"})

    # Bước 4: Lưu file JSON
    if final_list:
        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_list, f, ensure_ascii=False, indent=4)
        print("✅ Đã cập nhật file top10.json thành công!")

if __name__ == "__main__":
    main()
