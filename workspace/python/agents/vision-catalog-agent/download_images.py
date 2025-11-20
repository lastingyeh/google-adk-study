#!/usr/bin/env python3
"""
為教學 21 下載範例產品圖片
"""
import urllib.request
from pathlib import Path

# 範例圖片目錄
sample_dir = Path(__file__).parent / '_sample_images'
sample_dir.mkdir(exist_ok=True)

# 來自 Unsplash 的免費產品圖片 (免版稅)
images = {
    'laptop.jpg': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80',
    'headphones.jpg': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
    'smartwatch.jpg': 'https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&q=80'
}

print("正在下載範例產品圖片...")
print(f"目標目錄：{sample_dir}")
print()

# 遍歷圖片字典並下載
for filename, url in images.items():
    output_path = sample_dir / filename

    try:
        print(f"正在下載 {filename}...")
        print(f"  URL：{url}")

        # 使用適當的標頭下載
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )

        # 開啟 URL 並讀取回應
        with urllib.request.urlopen(req) as response:
            data = response.read()

        # 將下載的資料寫入檔案
        with open(output_path, 'wb') as f:
            f.write(data)

        print(f"  ✓ 已儲存至 {output_path} ({len(data):,} 位元組)")
        print()

    except Exception as e:
        print(f"  ✗ 下載 {filename} 時發生錯誤：{e}")
        print()

print("完成！範例圖片已可使用。")
print("\n圖片來源：Unsplash (https://unsplash.com)")
print("授權：可根據 Unsplash 授權免費使用")
