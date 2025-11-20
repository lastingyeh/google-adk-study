# Tutorial 21: 多模態與影像處理 - 視覺 AI 代理 (Multimodal & Image Processing - Visual AI Agents)

**目標**: 掌握多模態功能，包括影像輸入/輸出、視覺理解，以及使用 Gemini 模型和 Vertex AI Imagen 進行影像生成。

**先決條件**:

- Tutorial 01 (Hello World Agent)
- Tutorial 02 (Function Tools)
- Tutorial 19 (Artifacts & File Management)
- 了解影像格式和 MIME 類型

**學習內容**:

- 使用 Gemini 視覺模型處理影像
- 使用 `types.Part` 處理多模態內容
- **使用 Gemini 2.5 Flash Image 進行合成影像生成** ⭐ 新功能
- 處理 `inline_data` 與 `file_data`
- 建構具有 5 種專用工具的視覺代理
- 處理多個影像輸入
- 建立批次處理的自動化腳本
- 具備說明系統的使用者友善 Makefile
- 多模態應用程式的最佳實踐

**完成時間**: 50-65 分鐘

---

## 為什麼多模態很重要 (Why Multimodal Matters)

**問題**: 許多現實世界的應用程式需要理解和生成影像，而不僅僅是文字。

**解決方案**: **多模態模型 (Multimodal models)** 同時處理文字和影像，實現基於視覺的應用和影像生成。

**優勢**:

- [MEM] **視覺理解 (Vision Understanding)**: 分析影像，提取資訊
- 🎨 **影像生成 (Image Generation)**: 從文字描述建立影像
- [FLOW] **多模態推理 (Multimodal Reasoning)**: 結合視覺和文字語境
- 📊 **視覺分析 (Visual Analytics)**: 圖表、圖形、圖解分析
- 🏷️ **物件偵測 (Object Detection)**: 識別影像中的物件
- 📝 **OCR**: 從影像中提取文字

**使用案例**:

- 產品目錄分析
- 文件理解 (發票、收據)
- 醫學影像分析
- 視覺檢查和品質控制
- 內容審核
- 創意內容生成

---

## 1. 多模態輸入基礎 (Multimodal Input Basics)

### 理解 types.Part

**`types.Part`** 是 ADK 中多模態內容的基本單位。

**來源**: `google.genai.types`

```python
from google.genai import types

# 文字部分
text_part = types.Part.from_text("描述這張圖片")

# 影像部分 (內聯資料 inline data)
image_part = types.Part(
    inline_data=types.Blob(
        data=image_bytes,           # 原始影像位元組
        mime_type='image/png'       # MIME 類型
    )
)

# 影像部分 (檔案參考 file reference)
image_part = types.Part(
    file_data=types.FileData(
        file_uri='gs://bucket/image.jpg',  # Cloud Storage URI
        mime_type='image/jpeg'
    )
)
```

### 支援的影像格式

- **PNG**: `image/png`
- **JPEG**: `image/jpeg`
- **WEBP**: `image/webp`
- **HEIC**: `image/heic`
- **HEIF**: `image/heif`

### 載入影像

```python
import base64
from google.genai import types

# 從檔案載入
def load_image_from_file(path: str) -> types.Part:
    """從本機檔案載入影像。"""

    with open(path, 'rb') as f:
        image_bytes = f.read()

    # 根據副檔名判斷 MIME 類型
    if path.endswith('.png'):
        mime_type = 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif path.endswith('.webp'):
        mime_type = 'image/webp'
    else:
        raise ValueError(f"不支援的影像格式: {path}")

    return types.Part(
        inline_data=types.Blob(
            data=image_bytes,
            mime_type=mime_type
        )
    )


# 從 URL 載入
import requests

def load_image_from_url(url: str) -> types.Part:
    """從 URL 載入影像。"""

    response = requests.get(url)
    response.raise_for_status()

    image_bytes = response.content

    # 從 Content-Type 標頭判斷 MIME 類型
    mime_type = response.headers.get('Content-Type', 'image/jpeg')

    return types.Part(
        inline_data=types.Blob(
            data=image_bytes,
            mime_type=mime_type
        )
    )


# 從 Cloud Storage 載入
def load_image_from_gcs(uri: str) -> types.Part:
    """從 Google Cloud Storage 載入影像。"""

    # 對於 GCS，使用 file_data 而不是 inline_data
    mime_type = 'image/jpeg'  # 根據檔案副檔名判斷

    return types.Part(
        file_data=types.FileData(
            file_uri=uri,
            mime_type=mime_type
        )
    )
```

---

## 2. 視覺理解 (Vision Understanding)

### 基礎影像分析

```python
"""
使用 Gemini 進行基礎視覺理解。
"""

import asyncio
import os
from google.adk.agents import Agent, Runner
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'


async def analyze_image():
    """使用 Gemini 視覺功能分析影像。"""

    # 建立視覺代理
    agent = Agent(
        model='gemini-2.0-flash',  # 支援視覺功能
        name='vision_analyst',
        instruction="""
        你是一位視覺分析專家。當給定影像時，你會：

        1. 詳細描述你所看到的內容
        2. 識別關鍵物件及其關係
        3. 分析構圖和視覺元素
        4. 提取任何可見的文字 (OCR)
        5. 提供見解和觀察

        在分析中要具體且透徹。
        """.strip()
    )

    # 載入影像
    image_part = load_image_from_file('product.jpg')

    # 建立多模態查詢
    query_parts = [
        types.Part.from_text("詳細分析這張產品圖片。它是什麼，以及它有哪些關鍵特徵？"),
        image_part
    ]

    # 執行分析
    runner = Runner()
    result = await runner.run_async(
        query_parts,
        agent=agent
    )

    print("視覺分析:")
    print(result.content.parts[0].text)


if __name__ == '__main__':
    asyncio.run(analyze_image())
```

### 多影像分析

```python
async def compare_images():
    """比較多張影像。"""

    agent = Agent(
        model='gemini-2.0-flash',
        name='image_comparator',
        instruction="""
        比較提供的影像並識別：

        1. 相似點和不同點
        2. 共同元素
        3. 每個影像的獨特特徵
        4. 整體評估

        提供結構化的比較結果。
        """.strip()
    )

    # 載入多張影像
    image1 = load_image_from_file('product_v1.jpg')
    image2 = load_image_from_file('product_v2.jpg')

    # 建立包含多張影像的查詢
    query_parts = [
        types.Part.from_text("比較這兩個產品版本："),
        types.Part.from_text("版本 1:"),
        image1,
        types.Part.from_text("版本 2:"),
        image2,
        types.Part.from_text("有哪些關鍵差異？")
    ]

    runner = Runner()
    result = await runner.run_async(query_parts, agent=agent)

    print("比較結果:")
    print(result.content.parts[0].text)
```

---

## 3. 真實世界範例：視覺產品目錄分析器 (Visual Product Catalog Analyzer)

讓我們建立一個完整的具備視覺功能的產品目錄分析系統。

### 完整實作

```python
"""
視覺產品目錄分析器
分析產品影像，提取資訊並生成描述。
"""

import asyncio
import os
from typing import List, Dict
from google.adk.agents import Agent, Runner, Session
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# 環境設定
os.environ['GOOGLE_GENAI_USE_VERTEXAI'] = '1'
os.environ['GOOGLE_CLOUD_PROJECT'] = 'your-project-id'
os.environ['GOOGLE_CLOUD_LOCATION'] = 'us-central1'


class ProductCatalogAnalyzer:
    """分析產品影像並建立目錄項目。"""

    def __init__(self):
        """初始化產品目錄分析器。"""

        self.catalog: List[Dict] = []

        # 視覺分析代理
        self.vision_agent = Agent(
            model='gemini-2.0-flash',
            name='vision_analyzer',
            instruction="""
            你是一位產品視覺分析師。在分析產品影像時：

            1. 識別產品類型和類別
            2. 描述關鍵視覺特徵（顏色、尺寸、材質、設計）
            3. 注意任何可見的文字（品牌名稱、標籤、規格）
            4. 評估產品狀況和品質
            5. 識別獨特賣點

            提供結構化、詳細的分析。
            """.strip(),
            generate_content_config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=1024
            )
        )

        # 描述生成代理
        async def generate_catalog_entry(
            product_name: str,
            analysis: str,
            tool_context: ToolContext
        ) -> str:
            """生成適合行銷的目錄項目。"""

            entry = f"""
              # {product_name}

              ## 描述

              {analysis}

              ## 關鍵特徵

              - 高品質結構
              - 現代化設計
              - 多功能使用案例

              ## 規格

              - 材質: [從分析中提取]
              - 尺寸: [從分析中提取]
              - 顏色: [從分析中提取]

              *分析生成自產品影像*
            """.strip()

            # 儲存為製品 (Artifact)
            part = types.Part.from_text(entry)
            version = await tool_context.save_artifact(
                filename=f"{product_name}_catalog_entry.md",
                part=part
            )

            return f"目錄項目已建立 (版本 {version})"

        self.catalog_agent = Agent(
            model='gemini-2.0-flash',
            name='catalog_generator',
            instruction="""
            你是一位產品目錄內容創作者。根據視覺分析生成專業、
            適合行銷的產品描述。

            專注於：
            - 引人注目的產品描述
            - 關鍵特徵和優勢
            - 技術規格（如果可用）
            - 對客戶友善的語言

            使用 generate_catalog_entry 工具儲存項目。
            """.strip(),
            tools=[FunctionTool(generate_catalog_entry)],
            generate_content_config=types.GenerateContentConfig(
                temperature=0.6,
                max_output_tokens=1536
            )
        )

        self.runner = Runner()

    async def analyze_product(self, product_id: str, image_path: str):
        """
        分析產品影像並建立目錄項目。

        Args:
            product_id: 唯一產品識別碼
            image_path: 產品影像路徑
        """

        print(f"\n{'='*70}")
        print(f"分析產品: {product_id}")
        print(f"影像: {image_path}")
        print(f"{'='*70}\n")

        # 步驟 1: 視覺分析
        print("📸 步驟 1: 視覺分析...")

        image_part = load_image_from_file(image_path)

        analysis_query = [
            types.Part.from_text(f"為 {product_id} 分析這張產品影像："),
            image_part
        ]

        analysis_result = await self.runner.run_async(
            analysis_query,
            agent=self.vision_agent
        )

        analysis_text = analysis_result.content.parts[0].text

        print(f"\n🔍 視覺分析:\n{analysis_text}\n")

        # 步驟 2: 生成目錄項目
        print("📝 步驟 2: 生成目錄項目...")

        catalog_query = f"""
          根據此視覺分析，為 {product_id} 建立專業的目錄項目：

          {analysis_text}

          使用 generate_catalog_entry 工具儲存項目。
        """.strip()

        catalog_result = await self.runner.run_async(
            catalog_query,
            agent=self.catalog_agent
        )

        print(f"\n✅ 結果:\n{catalog_result.content.parts[0].text}\n")

        # 儲存到目錄
        self.catalog.append({
            'product_id': product_id,
            'image_path': image_path,
            'analysis': analysis_text,
            'timestamp': 'timestamp_here'
        })

        print(f"{'='*70}\n")

    async def batch_analyze(self, products: List[tuple[str, str]]):
        """
        分析多個產品。

        Args:
            products: (product_id, image_path) 元組的列表
        """

        for product_id, image_path in products:
            await self.analyze_product(product_id, image_path)
            await asyncio.sleep(2)

    def get_catalog_summary(self) -> str:
        """取得已分析產品的摘要。"""

        summary = f"\n產品目錄摘要\n{'='*70}\n"
        summary += f"已分析產品總數: {len(self.catalog)}\n\n"

        for i, product in enumerate(self.catalog, 1):
            summary += f"{i}. {product['product_id']}\n"
            summary += f"   影像: {product['image_path']}\n"
            summary += f"   分析: {product['analysis'][:100]}...\n\n"

        summary += f"{'='*70}\n"

        return summary


def load_image_from_file(path: str) -> types.Part:
    """從檔案載入影像。"""

    with open(path, 'rb') as f:
        image_bytes = f.read()

    if path.endswith('.png'):
        mime_type = 'image/png'
    elif path.endswith('.jpg') or path.endswith('.jpeg'):
        mime_type = 'image/jpeg'
    elif path.endswith('.webp'):
        mime_type = 'image/webp'
    else:
        mime_type = 'image/jpeg'

    return types.Part(
        inline_data=types.Blob(
            data=image_bytes,
            mime_type=mime_type
        )
    )


async def main():
    """主程式進入點。"""

    analyzer = ProductCatalogAnalyzer()

    # 分析多個產品
    # 注意：請替換為實際影像路徑
    products = [
        ('PROD-001', 'images/laptop.jpg'),
        ('PROD-002', 'images/headphones.jpg'),
        ('PROD-003', 'images/smartwatch.jpg')
    ]

    # 用於演示，建立佔位影像
    import io
    from PIL import Image

    os.makedirs('images', exist_ok=True)

    for product_id, image_path in products:
        # 建立佔位影像
        img = Image.new('RGB', (400, 400), color=(73, 109, 137))
        img.save(image_path)

    # 批次分析
    await analyzer.batch_analyze(products)

    # 顯示摘要
    print(analyzer.get_catalog_summary())


if __name__ == '__main__':
    asyncio.run(main())
```

### 預期輸出

```
======================================================================
分析產品: PROD-001
影像: images/laptop.jpg
======================================================================

📸 步驟 1: 視覺分析...

🔍 視覺分析:
這是一台具有現代化、時尚設計的筆記型電腦。關鍵觀察如下：

**產品類型**: 筆記型電腦/筆電

**視覺特徵**:
- 顏色: 深灰色或太空灰金屬外觀
- 設計: 薄型機身，窄邊框
- 螢幕: 約 13-15 吋顯示器
- 結構品質: 高級鋁合金一體成型
- 鍵盤: 全尺寸背光鍵盤
- 觸控板: 大型整合式觸控板

**品牌**: [蓋子上可見品牌標誌]

**狀況**: 看起來是全新且完美無瑕

**獨特特徵**:
- 超便攜設計
- 現代化埠配置 (USB-C)
- 高解析度顯示器
- 專業外觀

**目標市場**: 商務人士、學生、創意專業人士

📝 步驟 2: 生成目錄項目...

✅ 結果:
目錄項目已建立 (版本 1)

我已為 PROD-001 建立了一個全面的目錄項目，突出了其高級結構品質、現代設計和專業功能。該項目強調了其便攜性和多功能性以滿足各種用戶需求。

======================================================================

======================================================================
分析產品: PROD-002
影像: images/headphones.jpg
======================================================================

📸 步驟 1: 視覺分析...

🔍 視覺分析:
這是一副具備高級功能的無線耳罩式耳機。

**產品類型**: 無線耳罩式耳機

**視覺特徵**:
- 顏色: 消光黑色外觀
- 設計: 封閉式、環耳設計
- 耳罩: 大型、柔軟的耳墊
- 頭帶: 可調節，帶有柔軟填充
- 結構: 金屬與高品質塑料的結合
- 控制: 耳罩上可見實體按鈕

**技術指標**:
- 無線功能 (無可見線纜)
- 可能具備主動降噪功能 (根據設計)
- 可折疊機制以便攜帶

**狀況**: 全新，適合零售

**關鍵特徵**:
- 高級舒適設計
- 專業音質
- 配備攜帶盒，便於攜帶
- 現代美學

**目標市場**: 音樂愛好者、通勤族、內容創作者

📝 步驟 2: 生成目錄項目...

✅ 結果:
目錄項目已建立 (版本 1)

已為 PROD-002 生成專業目錄項目，強調音質、舒適性和無線便利性。目標用戶為尋求高級音頻體驗的用戶。

======================================================================

======================================================================
分析產品: PROD-003
影像: images/smartwatch.jpg
======================================================================

📸 步驟 1: 視覺分析...

🔍 視覺分析:
這是一款具備健身和健康追蹤功能的智慧手錶。

**產品類型**: 智慧手錶 / 健身追蹤器

**視覺特徵**:
- 顯示器: 圓形 AMOLED 觸控螢幕
- 機殼: 不鏽鋼或鋁合金
- 顏色: 黑色，搭配相配的錶帶
- 錶帶: 矽膠運動錶帶，佩戴舒適
- 介面: 可見數位旋鈕
- 設計: 現代、極簡美學

**可見技術功能**:
- 背面有心率感測器
- 防水設計
- 多按鈕/旋鈕控制
- 可能具備 GPS 功能 (根據外型)

**狀況**: 全新狀態

**關鍵特徵**:
- 健康與健身追蹤
- 常亮顯示器 (可能)
- 可更換錶帶
- 智慧通知
- 現代設計，適合任何場合

**目標市場**: 健身愛好者、注重健康的用戶、科技愛好者

📝 步驟 2: 生成目錄項目...

✅ 結果:
目錄項目已建立 (版本 1)

已為 PROD-003 建立目錄項目，突出了健康追蹤功能、現代設計以及適合健身和日常穿戴的多功能性。

======================================================================


產品目錄摘要
======================================================================
已分析產品總數: 3

1. PROD-001
  影像: images/laptop.jpg
  分析: 這是一台具有現代化、時尚設計的筆記型電腦。關鍵觀察如下：

**產品類型**: 筆記型電腦...

2. PROD-002
  影像: images/headphones.jpg
  分析: 這是一副具備高級功能的無線耳罩式耳機。

**產品類型**: 無線耳罩式耳機...

3. PROD-003
  影像: images/smartwatch.jpg
  分析: 這是一款具備健身和健康追蹤功能的智慧手錶。

**產品類型**: 智慧手錶 / ...

======================================================================
```
---

## 4. 使用 Gemini 2.5 Flash Image 進行合成影像生成 (Synthetic Image Generation) ⭐ 新功能

### 概述

**Gemini 2.5 Flash Image** 是一個文字轉影像 (text-to-image) 模型，可從文字描述生成逼真的產品影像。非常適合：

- 🎨 **快速原型製作 (Rapid Prototyping)**: 在攝影之前測試目錄設計
- 💡 **概念視覺化 (Concept Visualization)**: 向客戶展示產品概念
- 🔄 **變體 (Variations)**: 快速生成多種風格/顏色變體
- 📐 **版面測試 (Layout Testing)**: 為不同的長寬比建立模型
- 💰 **節省成本 (Cost Savings)**: 不需要攝影棚設備或攝影師

### 基礎合成生成

```python
"""
使用 Gemini 2.5 Flash Image 生成合成產品影像。
"""

import os
from google import genai
from google.genai import types as genai_types
from PIL import Image
from io import BytesIO


async def generate_product_mockup(
    product_description: str,
    style: str = "photorealistic product photography",
    aspect_ratio: str = "1:1"
) -> str:
    """
    生成合成產品影像。

    Args:
        product_description: 詳細的產品描述
        style: 攝影風格 (photorealistic, studio, lifestyle)
        aspect_ratio: 影像長寬比 (1:1, 16:9, 4:3, 3:2 等)

    Returns:
        生成影像的路徑
    """

    # 建立詳細的專業提示詞
    detailed_prompt = f"""
      A {style} of {product_description}.

      品質要求：
      - 高解析度、商業級品質
      - 影棚級均勻打光，柔光無強烈陰影
      - 產品主體銳利清晰對焦
      - 構圖簡潔、背景乾淨無干擾
      - 適用電商與行銷素材
    """.strip()

    # 初始化客戶端
    client = genai.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

    # 生成影像
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=[detailed_prompt],
        config=genai_types.GenerateContentConfig(
            response_modalities=['Image'],
            image_config=genai_types.ImageConfig(
                aspect_ratio=aspect_ratio
            )
        )
    )

    # 提取並儲存影像
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            image = Image.open(BytesIO(part.inline_data.data))
            image_path = f"generated_{product_description[:20]}.jpg"
            image.save(image_path, 'JPEG', quality=95)

            return image_path

    raise ValueError("未生成影像")


# 範例用法
async def demo_synthetic_generation():
    """演示合成影像生成。"""

    # 生成檯燈模型
    lamp_path = await generate_product_mockup(
        product_description="minimalist desk lamp with brushed aluminum finish and LED light",
        style="photorealistic product photography",
        aspect_ratio="1:1"
    )

    print(f"已生成檯燈模型: {lamp_path}")

    # 生成皮夾模型
    wallet_path = await generate_product_mockup(
      product_description="高級真皮皮夾，金色縫線，多卡片插槽",
      style="大理石表面上的寫實產品攝影",
      aspect_ratio="4:3"
    )
    print(f"已生成皮夾模型: {wallet_path}")

    # 生成電競滑鼠模型
    mouse_path = await generate_product_mockup(
      product_description="無線電競滑鼠，RGB 燈效，人體工學設計",
      style="具有戲劇化打光的寫實產品攝影",
      aspect_ratio="16:9"
    )
    print(f"已生成滑鼠模型: {mouse_path}")   print(f"已生成滑鼠模型: {mouse_path}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(demo_synthetic_generation())
```

### 支援的長寬比

Gemini 2.5 Flash Image 支援各種長寬比：

- **1:1** (1024x1024) - 適合社群媒體、產品目錄
- **16:9** (1344x768) - 寬幅產品照、生活風格攝影
- **4:3** (1184x864) - 標準產品照
- **3:2** (1248x832) - 專業攝影格式
- **9:16** (768x1344) - 垂直/行動優先版面

### 風格選項

在提示詞中自訂攝影風格：

- **寫實產品攝影** (預設)
- **影棚打光＋白色背景**
- **生活情境／場景式攝影**
- **藝術／創意產品視覺**
- **極簡構圖**
- **戲劇化光影**

### 與視覺分析整合

結合合成生成與視覺分析：

```python
async def generate_and_analyze_product():
    """生成合成影像並進行分析。"""

    # 步驟 1: 生成合成模型
    image_path = await generate_product_mockup(
        product_description="現代無線耳機，配備充電盒",
          aspect_ratio="1:1"
    )

    # 步驟 2: 載入生成影像
    image_part = load_image_from_file(image_path)

    # 步驟 3: 使用視覺模型進行分析
    vision_agent = Agent(
        model='gemini-2.0-flash-exp',
        name='vision_analyzer'
    )

    runner = Runner()
    analysis = await runner.run_async(
        [
            types.Part.from_text("分析此產品模型並建立目錄項目："),
            image_part
        ],
        agent=vision_agent
    )

    print(f"生成影像: {image_path}")
    print(f"分析: {analysis.content.parts[0].text}")
```
### 使用案例

**電商原型設計:**
```python
# 生成產品變體
for color in ['black', 'white', 'silver']:
  await generate_product_mockup(
    f"智慧型手機，顏色為 {color}，現代設計",
    aspect_ratio="1:1"
  )
```

**行銷素材:**
```python
# 創建生活情境照片
await generate_product_mockup(
  "木桌上的咖啡杯，晨光灑落",
  style="帶有暖色調的生活情境攝影",
  aspect_ratio="16:9"
)
```

**概念測試:**
```python
# 測試不同設計
for design in ['極簡', '奢華', '運動']:
  await generate_product_mockup(
    f"水瓶，{design} 設計美學",
    aspect_ratio="3:2"
  )
```

---

## 5. 使用 Vertex AI Imagen 進行影像生成 (替代方案) (Image Generation with Vertex AI Imagen)

### 基礎影像生成

```python
"""
使用 Vertex AI Imagen 生成影像 (Gemini 2.5 Flash Image 的替代方案)。
"""

from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel


def generate_image(prompt: str, output_path: str):
    """
    從文字提示生成影像。

    Args:
        prompt: 期望影像的文字描述
        output_path: 儲存生成影像的位置
    """

    # 初始化 Vertex AI
    aiplatform.init(
        project='your-project-id',
        location='us-central1'
    )

    # 載入 Imagen 模型
    model = ImageGenerationModel.from_pretrained('imagen-3.0-generate-001')

    # 生成影像
    response = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio='1:1',  # 選項: 1:1, 9:16, 16:9, 4:3, 3:4
        safety_filter_level='block_some',  # 選項: block_most, block_some, block_few
        person_generation='allow_all'  # 選項: allow_all, allow_adult, block_all
    )

    # 儲存第一張生成影像
    image = response.images[0]
    image.save(output_path)

    print(f"影像已儲存至: {output_path}")
```

### 影像生成代理

```python
async def create_image_generation_agent():
    """根據請求生成影像的代理。"""

    def generate_product_image(description: str, style: str = 'photorealistic') -> str:
        """根據描述生成產品影像。"""

        # 建構提示詞
        prompt = f"{description}, {style} style, professional product photography, "
        prompt += "high quality, detailed, studio lighting, white background"

        # 生成影像
        output_path = f"generated_{hash(description) % 10000}.png"
        generate_image(prompt, output_path)

        return f"影像已生成: {output_path}"

    agent = Agent(
        model='gemini-2.0-flash',
        name='image_generator',
        instruction="""
        你協助根據描述生成產品影像。

        當被要求建立影像時：
        1. 釐清需求
        2. 使用詳細描述呼叫 generate_product_image 工具
        3. 指定風格 (photorealistic, illustration 等)

        始終提供有幫助的描述以獲得最佳結果。
        """.strip(),
        tools=[FunctionTool(generate_product_image)]
    )

    return agent
```

---

## 6. 最佳實踐 (Best Practices)

### ✅ DO: 最佳化影像大小

```python
from PIL import Image
import io

def optimize_image(image_bytes: bytes, max_size_kb: int = 500) -> bytes:
    """為 API 呼叫最佳化影像大小。"""

    image = Image.open(io.BytesIO(image_bytes))

    # 如果太大則調整大小
    max_dimension = 1024
    if max(image.size) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.LANCZOS)

    # 使用壓縮儲存
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=85, optimize=True)

    return output.getvalue()


# 使用最佳化後的影像
original_bytes = open('large_image.jpg', 'rb').read()
optimized_bytes = optimize_image(original_bytes)

image_part = types.Part(
    inline_data=types.Blob(
        data=optimized_bytes,
        mime_type='image/jpeg'
    )
)
```

### ✅ DO: 處理多種影像格式

```python
def get_mime_type(file_path: str) -> str:
    """從檔案副檔名判斷 MIME 類型。"""

    extension = file_path.lower().split('.')[-1]

    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'webp': 'image/webp',
        'heic': 'image/heic',
        'heif': 'image/heif'
    }

    return mime_types.get(extension, 'image/jpeg')
```

### ✅ DO: 提供清晰的影像語境

```python
# ✅ Good - 清晰的語境
query = [
    types.Part.from_text("這是我們新產品發布的影像："),
    image_part,
    types.Part.from_text("分析產品設計並識別影像中可見的關鍵特徵。")
]

# ❌ Bad - 模稜兩可
query = [image_part, types.Part.from_text("這是什麼？")]
```
---
## 摘要

您已掌握多模態功能與合成影像生成：

**重點回顧**:

- ✅ 使用 `types.Part` 處理多模態內容（文字 + 影像）
- ✅ `inline_data` 嵌入影像，`file_data` 引用影像檔案
- ✅ Gemini 2.0 Flash 支援視覺理解
- ✅ **Gemini 2.5 Flash Image 用於合成影像生成** ⭐ 新功能
- ✅ Vertex AI Imagen 作為影像生成替代方案
- ✅ 多影像分析與比較
- ✅ 基於視覺的產品目錄應用（5 種工具）
- ✅ 批次處理的自動化腳本
- ✅ 具備說明系統的使用者友善 Makefile
- ✅ API 效率的影像最佳化

**實作亮點**:

- 🎨 **5 種專用工具**: 列出、生成、上傳、分析、比較
- 📸 **4 個自動化腳本**: 下載、分析、生成、演示
- 🧪 **70 項測試**，涵蓋率達 63%
- 📚 **使用者友善的 Makefile**: 完整的說明系統
- ⭐ **合成生成**: 整合 Gemini 2.5 Flash Image

**生產驗收清單**:

- [ ] 已實現影像最佳化（大小、格式）
- [ ] 無效影像的錯誤處理
- [ ] MIME 類型驗證
- [ ] 在代表性影像上測試視覺模型
- [ ] **使用多種提示測試合成生成** ⭐
- [ ] 審核生成影像的品質
- [ ] 監控影像操作的成本
- [ ] 定義影像儲存策略
- [ ] 符合影像生成政策
- [ ] **記錄 Makefile 說明系統**
- [ ] **批次操作的自動化腳本**

**資源**:

- [Gemini 視覺文件](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/overview)
- [Imagen 文件](https://cloud.google.com/vertex-ai/docs/generative-ai/image/overview)
- [多模態最佳實踐](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/best-practices)
- [完整實作](https://github.com/raphaelmansuy/adk_training/tree/main/tutorial_implementation/tutorial21) - 完整且經測試的程式碼

---

- **具備 5 種專用工具的視覺目錄代理**
- **70 項通過測試**（涵蓋率 63%）
- **使用 Gemini 2.5 Flash Image 的合成影像生成** ⭐
- **4 個自動化腳本**（下載、分析、生成、演示）
- **使用者友善的 Makefile**，具備完整說明系統
- **影像處理工具**與最佳化
- **多代理工作流程**（視覺 + 目錄）
- **互動式演示**與範例影像
- **完整文件**

**快速開始**:
```bash
cd tutorial_implementation/tutorial21
make                # 顯示所有指令
make setup          # 安裝依賴
make generate       # 生成合成模型 ⭐
make dev            # 啟動互動代理
```

---

## 程式碼實現 (Code Implementation)

- visiion-catalog-agent：[程式碼連結](../../../python/agents/vision-catalog-agent/)
