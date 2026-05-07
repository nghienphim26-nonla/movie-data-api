import requests
import json
import os

# Cấu hình từ GitHub Secrets
SS_API_KEY = os.getenv("SIMPLESCRAPER_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
RECIPE_ID = "B5UEdm8kEDFzwkFELx8X"

def main():
    # 1. Gọi API để kích hoạt và nhận data cùng lúc
    url = f"https://api.simplescraper.io/v1/recipes/{RECIPE_ID}/run?apikey={SS_API_KEY}"
    
    print("🚀 Đang kết nối Simplescraper (Real-time mode)...")
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"❌ Lỗi API Simplescraper: {response.status_code}")
            return

        data_json = response.json()
        raw_movies = data_json.get("data", [])
        
        if not raw_movies:
            print("⚠️ Simplescraper không trả về dữ liệu phim. Hãy kiểm tra lại Recipe trên web.")
            return

        # 2. Lấy danh sách tên phim (khớp với cột 'tenphim')
        names = [m.get("tenphim").strip() for m in raw_movies if m.get("tenphim")]
        print(f"✅ Đã lấy được {len(names)} phim: {names}")

        # 3. Kết hợp với dữ liệu ảnh từ TMDB
        final_data = []
        for i, name in enumerate(names[:10], 1):
            print(f"🔍 Đang tìm TMDB cho: {name}")
            
            tmdb_url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={name}&language=vi-VN"
            try:
                tmdb_res = requests.get(tmdb_url).json()
                if tmdb_res.get('results'):
                    item = tmdb_res['results'][0]
                    final_data.append({
                        "rank": i,
                        "title": item.get("title") or item.get("name") or name,
                        "tmdb_id": item.get("id"),
                        "poster": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get('poster_path') else None,
                        "backdrop": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get('backdrop_path') else None,
                        "type": item.get("media_type", "movie")
                    })
                else:
                    final_data.append({"rank": i, "title": name, "status": "no_tmdb"})
            except:
                final_data.append({"rank": i, "title": name, "status": "error_tmdb"})

        # 4. Ghi vào file JSON
        with open('top10.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print("🎉 Hoàn tất! File top10.json đã sẵn sàng trên GitHub Pages.")

    except Exception as e:
        print(f"❌ Lỗi hệ thống: {e}")

if __name__ == "__main__":
    main()
