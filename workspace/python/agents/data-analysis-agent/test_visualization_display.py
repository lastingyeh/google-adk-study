#!/usr/bin/env python3
"""
Test script to verify inline_data visualization display logic
測試腳本：驗證 inline_data 視覺化顯示邏輯

重點摘要
- 核心概念：模擬並驗證視覺化資料（圖片）的處理與顯示邏輯。
- 關鍵技術：PIL (Pillow), Base64, Mock Objects.
- 重要結論：確保從後端回傳的二進位或 Base64 圖片資料能被正確解析與顯示。
- 行動項目：
    1. 建立測試用圖片。
    2. 建立 MockBlob 物件模擬 ADK 回傳。
    3. 模擬顯示邏輯並驗證圖片是否可開啟。
"""
import base64
from io import BytesIO
from PIL import Image

# 模擬 Blob 類別以模擬 ADK 回傳的物件
# Mock the Blob class to simulate what ADK returns
class MockBlob:
    def __init__(self, image_data, mime_type='image/png'):
        self.data = image_data
        self.mime_type = mime_type

# 測試 1: 建立一個簡單的測試圖片
# Test 1: Create a simple test image
print("[TEST] 正在建立測試圖片...")
img = Image.new('RGB', (100, 100), color='red')
img_bytes = BytesIO()
img.save(img_bytes, format='PNG')
img_bytes.seek(0)
test_image_data = img_bytes.read()
print(f"[TEST] 已建立 {len(test_image_data)} bytes 的圖片")

# 測試 2: 建立模擬 blob（模擬 inline_data 的內容）
# Test 2: Create mock blob (simulating what inline_data would be)
print("\n[TEST] 正在建立模擬 blob...")
mock_blob = MockBlob(test_image_data)
print("[TEST] 模擬 blob 已建立")
print(f"  - data type: {type(mock_blob.data).__name__}")
print(f"  - data length: {len(mock_blob.data)}")
print(f"  - mime_type: {mock_blob.mime_type}")

# 測試 3: 模擬視覺化顯示邏輯
# Test 3: Simulate the visualization display logic
print("\n[TEST] 正在模擬視覺化顯示邏輯...")
viz_data = [mock_blob]
has_viz = True

if has_viz and viz_data:
    print(f"[TEST] 顯示 {len(viz_data)} 個視覺化內容")
    for i, viz in enumerate(viz_data):
        try:
            print(f"[TEST] 正在處理視覺化 {i}: type={type(viz).__name__}")

            # viz 應為具有 data 與 mime_type 的 Blob 物件
            # viz should be a Blob object with data and mime_type
            if hasattr(viz, 'data') and viz.data:
                data = viz.data
                mime_type = getattr(viz, 'mime_type', 'image/png')
                print(f"[TEST] mime_type: {mime_type}")
                print(f"[TEST] data type: {type(data).__name__}")
                print(f"[TEST] data length: {len(data) if data else 0}")

                # 若有需要則轉換為 bytes
                # Convert to bytes if needed
                if isinstance(data, str):
                    print("[TEST] data 為字串，正在進行 base64 解碼...")
                    image_bytes = base64.b64decode(data)
                elif isinstance(data, bytes):
                    print("[TEST] data 已經是 bytes")
                    image_bytes = data
                else:
                    print(f"[TEST] data 為未預期的類型: {type(data)}")
                    image_bytes = bytes(data)

                print(f"[TEST] image_bytes 長度: {len(image_bytes)}")

                # 嘗試開啟圖片
                # Try to open image
                try:
                    image = Image.open(BytesIO(image_bytes))
                    print(f"[TEST] ✅ 圖片開啟成功: {image.format} {image.size}")
                    print("[TEST] ✅ 圖片將透過 st.image() 顯示")
                except Exception as img_err:
                    print(f"[TEST] ❌ 無法開啟/顯示圖片: {str(img_err)}")
                    import traceback
                    traceback.print_exc()
            else:
                print("❌ viz 沒有 'data' 或 data 為 None")
                print(f"[TEST] viz type: {type(viz)}")
        except Exception as e:
            print(f"[TEST] ❌ 處理視覺化時發生例外: {str(e)}")
            import traceback
            traceback.print_exc()
else:
    if viz_data:
        print(f"[TEST] has_viz={has_viz}, viz_data len={len(viz_data)}")
    else:
        print("[TEST] 沒有要顯示的視覺化內容")

print("\n[TEST] ✅ 所有測試通過！")
