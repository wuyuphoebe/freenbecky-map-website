import os
import json
import re

# --- 設定路徑 ---
IMAGE_DIR = 'images'
DATA_FILE = 'data.js'

def load_existing_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            start = content.find('[')
            end = content.rfind(']') + 1
            json_str = content[start:end]
            data_list = json.loads(json_str)
            return {f"{d['celebrity']}_{d['name']}": d for d in data_list}
    except Exception as e:
        print(f"讀取舊資料失敗: {e}")
        return {}

def generate_db():
    old_data_map = load_existing_data()
    new_fb_data = []
    
    if not os.path.exists(IMAGE_DIR):
        print(f"找不到 {IMAGE_DIR} 資料夾")
        return

    celeb_folders = [d for d in os.listdir(IMAGE_DIR) if os.path.isdir(os.path.join(IMAGE_DIR, d))]
    
    for celeb in celeb_folders:
        celeb_path = os.path.join(IMAGE_DIR, celeb)
        years = [y for y in os.listdir(celeb_path) if os.path.isdir(os.path.join(celeb_path, y))]
        
        for year in years:
            year_path = os.path.join(celeb_path, year)
            locations = [l for l in os.listdir(year_path) if os.path.isdir(os.path.join(year_path, l))]
            
            for loc_name in locations:
                loc_path = os.path.join(year_path, loc_name)
                # 擴展副檔名，加入影片格式
                valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.gif', '.PNG', '.mp4', '.mov', '.MP4', '.MOV')
                files = [f for f in os.listdir(loc_path) if f.lower().endswith(valid_exts)]
                files.sort()

                if not files: continue

                celeb_display = celeb.replace("FreenBecky", "Freen & Becky")
                data_key = f"{celeb_display}_{loc_name}"

                current_images = []
                for img_name in files:
                    current_images.append({
                        "url": f"{IMAGE_DIR}/{celeb}/{year}/{loc_name}/{img_name}",
                        "platform": "Instagram",
                        "category": "Life",
                        "author": celeb
                    })

                if data_key in old_data_map:
                    item = old_data_map[data_key]
                    old_urls = [img['url'] for img in item.get('images', [])]
                    new_urls = [img['url'] for img in current_images]
                    
                    if old_urls != new_urls:
                        item["images"] = current_images
                        print(f"📸 更新檔案清單 (含影片): {loc_name}")
                else:
                    print(f"✨ 發現新地點: {loc_name}")
                    detected_date = f"{year}-01-01"
                    match = re.search(r'(\d{8})', files[0])
                    if match:
                        d = match.group(1)
                        detected_date = f"{d[:4]}-{d[4:6]}-{d[6:]}"

                    item = {
                        "id": 0,
                        "name": loc_name,
                        "celebrity": celeb_display,
                        "date": detected_date,
                        "lat": 13.7563,
                        "lng": 100.5018,
                        "mapUrl": "https://www.google.com/maps",
                        "desc": "",
                        "images": current_images
                    }
                
                new_fb_data.append(item)

    new_fb_data.sort(key=lambda x: str(x['date']), reverse=True)
    for i, item in enumerate(new_fb_data):
        item['id'] = i + 1

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json_content = json.dumps(new_fb_data, ensure_ascii=False, indent=4)
        f.write(f"const FB_DATA = {json_content};")
    
    print(f"\n✅ 同步成功！已包含影片偵測。")

if __name__ == "__main__":
    generate_db()