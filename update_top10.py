import requests
import time
import json
import os

# Lấy cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "B5UEdm8kEDFzwkFELx8X"

def run_ss():
    """Kích hoạt Simplescraper và in lỗi nếu có"""
    if not SS_API_KEY:
        print("❌ Lỗi: Không tìm thấy SIMPLESCRAPER_API_KEY trong Secrets!")
        return False
        
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    try:
        res = requests.get(url)
        res_data = res.json()
        
        if res.status_code == 200 and res_data.get("status") == "success":
            print(f"✅ Đã kích hoạt Simplescraper thành công! Execution ID: {res_data.get('execution_id')}")
            print("⏳ Đợi 60s để máy chủ Simplescraper xử lý...")
            time.sleep(60)
            return True
        else:
            print(f"❌ Simplescraper từ chối lệnh! Phản hồi: {res_data}")
            return False
    except Exception as e:
        print(f"❌ Lỗi kết nối đến Simplescraper: {e}")
        return False

def get_ss_data():
    """Lấy tên phim từ Simplescraper dựa trên cột 'tenphim'"""
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/last_run?apikey={SS_API_KEY}"
    try:
        response = requests.get(url)
        full_res = response.json()
        data = full_res.get("data", [])
        
        # Sửa từ 'title' thành 'tenphim' theo đúng log của bạn
        movie_names = []
        for item in data:
            name = item.get("tenphim")
            if name:
                movie_names.append(name.strip())
        
        return movie_names[:10]
    except Exception as e:
        print(f"❌ Lỗi lấy dữ liệu: {e}")
        return []

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
    # Gọi Simplescraper
    run_ss() 
    
    # Lấy dữ liệu
    names = get_ss_data()
    print(f"🎬 Đã tìm thấy các tên phim: {names}")
    
    if not names:
        print("❌ Không tìm thấy phim nào trong cột 'tenphim'. Hãy kiểm tra lại Recipe!")
        return

    final_list = []
    for i, n in enumerate(names, 1):
        info = get_tmdb(n)
        if info:
            info['rank'] = i
            final_list.append(info)
        else:
            # Nếu TMDB không thấy, vẫn lưu tên phim từ Simplescraper
            final_list.append({"title": n, "rank": i, "note": "Không tìm thấy ảnh trên TMDB"})
    
    # Lưu file
    with open('top10.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)
    print("✅ Đã tạo file top10.json thành công!")
        
        if final_list:
            with open('top10.json', 'w', encoding='utf-8') as f:
                json.dump(final_list, f, ensure_ascii=False, indent=4)
            print("✅ Đã cập nhật top10.json")

if __name__ == "__main__":
    main()
