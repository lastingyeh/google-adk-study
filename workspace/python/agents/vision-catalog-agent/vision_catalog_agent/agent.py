"""
視覺目錄代理 - 教學 21：多模態與影像處理
"""
import io
import os
from typing import List, Dict, Any
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

try:
    from PIL import Image
except ImportError:
    Image = None


# ============================================================================
# 圖片工具程式
# ============================================================================


def load_image_from_file(path: str) -> types.Part:
    """
    從本機檔案載入圖片。

    Args:
        path: 圖片檔案的路徑

    Returns:
        包含圖片資料的 types.Part

    Raises:
        FileNotFoundError: 如果檔案不存在
        ValueError: 如果是不支援的格式
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"找不到圖片檔案：{path}")

    with open(path, 'rb') as f:
        image_bytes = f.read()

    # 從副檔名判斷 MIME 類型
    extension = path.lower().split('.')[-1]
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'webp': 'image/webp',
        'heic': 'image/heic',
        'heif': 'image/heif',
    }

    mime_type = mime_types.get(extension)
    if not mime_type:
        raise ValueError(f"不支援的圖片格式：{extension}")

    return types.Part(
        inline_data=types.Blob(
            data=image_bytes,
            mime_type=mime_type
        )
    )


def optimize_image(image_bytes: bytes, max_size_kb: int = 500) -> bytes:
    """
    為 API 呼叫最佳化圖片大小。

    Args:
        image_bytes: 原始圖片位元組
        max_size_kb: 最大大小 (KB)

    Returns:
        最佳化後的圖片位元組
    """
    if Image is None:
        return image_bytes

    image = Image.open(io.BytesIO(image_bytes))

    # 如果太大則調整大小
    max_dimension = 1024
    if max(image.size) > max_dimension:
        image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    # 如有必要，轉換為 RGB
    if image.mode in ('RGBA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'RGBA':
            background.paste(image, mask=image.split()[3])
        else:
            background.paste(image)
        image = background

    # 以壓縮方式儲存
    output = io.BytesIO()
    image.save(output, format='JPEG', quality=85, optimize=True)

    return output.getvalue()


def create_sample_image(path: str, color: tuple = (73, 109, 137)) -> str:
    """
    建立用於測試的範例預留位置圖片。

    Args:
        path: 儲存圖片的路徑
        color: RGB 顏色元組

    Returns:
        已建立圖片的路徑
    """
    if Image is None:
        raise ImportError("建立範例圖片需要 PIL/Pillow")

    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new('RGB', (400, 400), color=color)
    img.save(path)
    return path


# ============================================================================
# 視覺目錄代理元件
# ============================================================================


# 視覺分析代理
vision_analyzer = Agent(
    model='gemini-2.0-flash-exp',
    name='vision_analyzer',
    description='分析產品圖片並提取視覺資訊',
    instruction="""
    您是一位產品視覺分析師。在分析產品圖片時：

    1. 識別產品類型和類別
    2. 描述關鍵視覺特徵 (顏色、尺寸、材質、設計)
    3. 注意任何可見的文字 (品牌名稱、標籤、規格)
    4. 評估產品狀況和品質
    5. 識別獨特的賣點

    提供結構化、詳細的分析，重點關注：
    - 產品識別
    - 視覺特性
    - 設計元素
    - 品質指標
    - 目標市場洞察

    請在您的觀察中具體而詳盡。
    """.strip(),
    generate_content_config=types.GenerateContentConfig(
        temperature=0.3,
        max_output_tokens=1024
    )
)


# 用於生成目錄條目的工具
async def generate_catalog_entry(
    product_name: str,
    analysis: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    生成並儲存一份可用於行銷的目錄條目。

    Args:
        product_name: 產品的名稱/ID
        analysis: 視覺分析結果
        tool_context: 用於成品管理的上下文

    Returns:
        包含狀態、報告和成品版本的字典
    """
    try:
        # 生成目錄條目內容
        entry = f"""
        # {product_name}

        ## 描述

        {analysis}

        ## 主要功能

        - 高品質結構
        - 現代設計
        - 多功能用途

        ## 視覺分析

        根據詳細的圖像分析，該產品展示了專業級的
        品質和現代設計元素，適合有眼光的客戶。

        ---

        *目錄條目由 AI 視覺分析生成*
        """.strip()
        # 儲存為成品
        part = types.Part.from_text(text=entry)
        version = await tool_context.save_artifact(
            filename=f"{product_name}_catalog.md",
            part=part
        )

        return {
            'status': 'success',
            'report': f'已為 {product_name} 建立目錄條目',
            'version': version,
            'filename': f"{product_name}_catalog.md"
        }

    except Exception as e:
        return {
            'status': 'error',
            'report': f'生成目錄條目失敗：{str(e)}',
            'error': str(e)
        }


# 目錄生成器代理
catalog_generator = Agent(
    model='gemini-2.0-flash-exp',
    name='catalog_generator',
    description='根據視覺分析建立專業的產品目錄條目',
    instruction="""
    您是一位產品目錄內容創作者。根據視覺分析生成專業、
    可用於行銷的產品描述。

    重點關注：
    - 引人入勝的產品描述
    - 主要功能和優點
    - 技術規格 (如果可用)
    - 客戶友善的語言
    - 專業的語氣

    使用 generate_catalog_entry 工具將目錄條目儲存為成品。
    務必提供產品名稱和完整的視覺分析。
    """.strip(),
    tools=[FunctionTool(generate_catalog_entry)],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.6,
        max_output_tokens=1536
    )
)


# 用於分析產品圖片的工具
async def analyze_product_image(
    product_id: str,
    image_path: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    分析產品圖片並生成目錄條目。

    Args:
        product_id: 產品識別碼
        image_path: 產品圖片檔案的路徑
        tool_context: 用於執行子代理的上下文

    Returns:
        包含分析結果和目錄條目資訊的字典
    """
    try:
        # 載入圖片
        if not os.path.exists(image_path):
            return {
                'status': 'error',
                'report': f'找不到圖片檔案：{image_path}',
                'error': '找不到檔案'
            }

        image_part = load_image_from_file(image_path)

        # 步驟 1：視覺分析
        analysis_query = [
            types.Part.from_text(text=f"分析此產品圖片，產品為 {product_id}："),
            image_part
        ]

        analysis_result = await tool_context.run_agent(
            vision_analyzer,
            analysis_query
        )

        if not analysis_result.content or not analysis_result.content.parts:
            return {
                'status': 'error',
                'report': '分析圖片失敗',
                'error': '沒有分析結果'
            }

        analysis_text = analysis_result.content.parts[0].text

        # 步驟 2：生成目錄條目
        catalog_query = f"""
        根據此視覺分析，為 {product_id} 建立一個專業的目錄條目：

        {analysis_text}

        使用 generate_catalog_entry 工具儲存條目。
        """.strip()

        catalog_result = await tool_context.run_agent(
            catalog_generator,
            catalog_query
        )

        return {
            'status': 'success',
            'report': f'成功分析 {product_id}',
            'product_id': product_id,
            'analysis': analysis_text,
            'catalog_result': catalog_result.content.parts[0].text if catalog_result.content else ''
        }

    except Exception as e:
        return {
            'status': 'error',
            'report': f'分析產品失敗：{str(e)}',
            'error': str(e)
        }


# 用於比較多張圖片的工具
async def compare_product_images(
    image_paths: List[str],
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    比較多張產品圖片。

    Args:
        image_paths: 圖片檔案路徑列表
        tool_context: 用於執行代理的上下文

    Returns:
        包含比較結果的字典
    """
    try:
        if len(image_paths) < 2:
            return {
                'status': 'error',
                'report': '至少需要 2 張圖片才能比較',
                'error': '圖片不足'
            }

        # 載入所有圖片
        query_parts = [
            types.Part.from_text(text="比較這些產品圖片並識別異同點：")
        ]

        for i, path in enumerate(image_paths, 1):
            if not os.path.exists(path):
                return {
                    'status': 'error',
                    'report': f'找不到圖片：{path}',
                    'error': '找不到檔案'
                }

            query_parts.append(types.Part.from_text(text=f"\n圖片 {i}："))
            query_parts.append(load_image_from_file(path))

        query_parts.append(types.Part.from_text(text="\n提供結構化的比較。"))

        # 執行比較
        result = await tool_context.run_agent(vision_analyzer, query_parts)

        if not result.content or not result.content.parts:
            return {
                'status': 'error',
                'report': '比較圖片失敗',
                'error': '沒有比較結果'
            }

        return {
            'status': 'success',
            'report': f'成功比較 {len(image_paths)} 張圖片',
            'comparison': result.content.parts[0].text,
            'image_count': len(image_paths)
        }

    except Exception as e:
        return {
            'status': 'error',
            'report': f'比較圖片失敗：{str(e)}',
            'error': str(e)
        }


# 用於生成合成產品模型的工具
async def generate_product_mockup(
    product_description: str,
    product_name: str,
    tool_context: ToolContext,
    style: str = "逼真的產品攝影",
    aspect_ratio: str = "1:1"
) -> Dict[str, Any]:
    """
    使用 Gemini 2.5 Flash Image 生成合成產品圖片。

    當您還沒有真實照片時，這非常適合建立產品模型。
    非常適合用於原型設計、測試或生成現有產品的變化版本。

    Args:
        product_description: 要生成產品的詳細描述
        product_name: 用於儲存生成圖片的名稱/ID
        style: 攝影/插圖風格 (預設：逼真的產品攝影)
        aspect_ratio: 圖片長寬比 (預設：1:1，選項：16:9、4:3、3:2 等)
        tool_context: 用於執行工具的上下文

    Returns:
        包含狀態、生成圖片路徑和描述的字典

    Examples:
        - "一款時尚的無線滑鼠，霧面黑色表面，符合人體工學的設計，在白色背景上"
        - "高級皮革錢包，棕色，金色縫線，可見信用卡"
        - "極簡風格桌燈，髮絲紋鋁，LED 燈，現代設計"
    """
    try:
        from google import genai as genai_client
        from google.genai import types as genai_types
        from PIL import Image
        from io import BytesIO

        # 為產品攝影建立詳細提示
        detailed_prompt = f"""
        一張關於 {product_description} 的 {style}。

        圖片應為：
        - 高解析度和專業品質
        - 在攝影棚燈光下光線充足
        - 產品對焦清晰
        - 構圖乾淨
        - 適合電子商務或行銷材料

        背景：乾淨、極簡、專業的背景，能突顯產品。
        燈光：柔和、均勻的燈光，突顯產品的特色和品質。
        角度：能清楚展示產品的討喜視角。
        """.strip()

        # 初始化客戶端
        client = genai_client.Client(api_key=os.environ.get('GOOGLE_API_KEY'))

        # 生成圖片
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

        # 儲存生成的圖片
        generated_image_path = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # 儲存到 _sample_images 目錄
                sample_dir = Path(__file__).parent.parent / '_sample_images'
                sample_dir.mkdir(exist_ok=True)

                # 建立檔名
                safe_name = product_name.lower().replace(' ', '_').replace('-', '_')
                image_path = sample_dir / f"{safe_name}_generated.jpg"

                # 儲存圖片
                image = Image.open(BytesIO(part.inline_data.data))
                image.save(image_path, 'JPEG', quality=95)
                generated_image_path = str(image_path)

                break

        if not generated_image_path:
            return {
                'status': 'error',
                'report': '未生成任何圖片',
                'error': '回應中沒有圖片資料'
            }

        return {
            'status': 'success',
            'report': f'已為 {product_name} 生成合成產品模型',
            'image_path': generated_image_path,
            'description': product_description,
            'style': style,
            'aspect_ratio': aspect_ratio,
            'usage_tip': f'您現在可以使用 analyze_product_image("{product_name}", "{generated_image_path}") 分析此圖片'
        }

    except Exception as e:
        return {
            'status': 'error',
            'report': f'生成產品模型失敗：{str(e)}',
            'error': str(e)
        }


# 用於列出可用範例圖片的工具
async def list_sample_images(
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    列出 _sample_images 目錄中可用的範例產品圖片。

    當使用者詢問有哪些可用圖片或想看範例時使用。

    Args:
        tool_context: 用於執行工具的上下文

    Returns:
        包含可用圖片列表及其詳細資訊的字典
    """
    try:
        # 取得範例圖片目錄
        sample_dir = Path(__file__).parent.parent / '_sample_images'

        if not sample_dir.exists():
            return {
                'status': 'info',
                'report': '找不到範例圖片目錄。您可以自行建立或上傳您自己的圖片。',
                'available_images': []
            }

        # 尋找所有圖片檔案
        image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
        images = []

        for img_file in sorted(sample_dir.iterdir()):
            if img_file.suffix.lower() in image_extensions:
                # 取得檔案大小
                size_bytes = img_file.stat().st_size
                size_kb = size_bytes / 1024

                # 如果有 PIL，嘗試取得圖片尺寸
                dimensions = None
                if Image is not None:
                    try:
                        with Image.open(img_file) as img:
                            dimensions = f"{img.width}x{img.height}"
                    except Exception:
                        pass

                images.append({
                    'filename': img_file.name,
                    'path': str(img_file),
                    'size': f"{size_kb:.1f} KB",
                    'dimensions': dimensions or '未知',
                    'format': img_file.suffix[1:].upper()
                })

        if not images:
            return {
                'status': 'info',
                'report': '找不到範例圖片。請上傳您自己的圖片或執行：python download_images.py',
                'available_images': []
            }

        return {
            'status': 'success',
            'report': f'在 _sample_images/ 中找到 {len(images)} 張範例圖片',
            'available_images': images,
            'directory': str(sample_dir),
            'usage_hint': '使用 analyze_product_image(product_id, image_path) 來分析這些圖片中的任何一張'
        }

    except Exception as e:
        return {
            'status': 'error',
            'report': f'列出範例圖片失敗：{str(e)}',
            'error': str(e)
        }


# 用於直接從查詢中分析上傳圖片的工具
async def analyze_uploaded_image(
    product_name: str,
    tool_context: ToolContext
) -> Dict[str, Any]:
    """
    分析直接在查詢中上傳的圖片。

    此工具為分析已
    對根代理的視覺模型可見的上傳圖片提供指引。它不需要呼叫子代理。

    Args:
        product_name: 產品的名稱或 ID
        tool_context: 用於執行工具的上下文

    Returns:
        包含結構化分析指引的字典
    """
    try:
        # 因為根代理具有視覺能力並且可以看到上傳的圖片，
        # 我們回傳一個結構化的提示來引導其分析
        return {
            'status': 'success',
            'report': f'已收到：正在分析產品 "{product_name}" 的上傳圖片',
            'product_name': product_name,
            'analysis_framework': {
                'product_identification': [
                    '產品類型和類別',
                    '品牌或製造商 (如果可見)',
                    '型號或 SKU (如果可見)'
                ],
                'visual_features': [
                    '主要和次要顏色',
                    '設計風格和美學',
                    '材料和質地',
                    '尺寸和比例 (如果可辨識)'
                ],
                'quality_indicators': [
                    '結構品質',
                    '表面處理和工藝',
                    '狀況評估',
                    '包裝 (如果顯示)'
                ],
                'distinctive_features': [
                    '獨特的賣點',
                    '創新的設計元素',
                    '特殊功能或能力',
                    '與同類典型產品的比較'
                ],
                'market_positioning': [
                    '目標客群',
                    '使用案例和應用',
                    '市場區隔 (入門/中階/高階)',
                    '競爭定位'
                ]
            },
            'instruction_for_agent': f"""
            根據此對話中可見的上傳圖片，請遵循上述 analysis_framework，對 {product_name}
            進行全面分析。

            然後以 markdown 格式建立一個專業的產品目錄條目，包括：

            # {product_name}

            ## 產品總覽
            [引人入勝的 2-3 句話描述]

            ## 主要功能
            - [功能 1]
            - [功能 2]
            - [功能 3]

            ## 規格
            - **類別**：[產品類別]
            - **設計**：[設計特性]
            - **材料**：[使用的材料]
            - **顏色**：[顏色選項]

            ## 描述
            [詳細的 2-3 段描述，突顯優點和使用案例]

            ## 目標市場
            [此產品適合的對象]

            ---
            *基於視覺檢查的分析*
            """.strip()
        }

    except Exception as e:
        return {
            'status': 'error',
            'report': f'準備上傳圖片分析失敗：{str(e)}',
            'error': str(e)
        }


# ============================================================================
# 根代理
# ============================================================================


root_agent = Agent(
    model='gemini-2.0-flash-exp',
    name='vision_catalog_coordinator',
    description='具有多模態能力的視覺化產品目錄協調器',
    instruction="""
    您是一位具有多模態能力的視覺化產品目錄協調器。
    您可以直接看到並分析圖片。

    **可用的範例圖片**：
    - _sample_images/ 目錄中有範例產品圖片
    - 使用 list_sample_images() 工具查看可用圖片
    - 範例圖片包括：筆記型電腦、耳機、智慧手錶等
    - 使用者也可以上傳自己的圖片

    **合成圖片生成** ⭐ 新功能：
    - 使用 generate_product_mockup() 建立合成產品圖片
    - 當使用者還沒有產品照片時，這非常適合
    - 非常適合用於原型設計、測試變化版本或產生想法
    - 範例：「生成一個極簡風格桌燈的模型」或「建立一個皮革背包的合成圖片」
    - 生成後，您可以像分析任何其他圖片一樣分析合成圖片

    **上傳圖片的工作流程** (最常見)：
    1. 當使用者上傳/貼上圖片時，首先呼叫 analyze_uploaded_image(product_name)
    2. 該工具將回傳一個 analysis_framework 和 instruction_for_agent
    3. 然後，您分析您可以看到的圖片，遵循該框架
    4. 直接向使用者提供全面的分析和目錄條目

    **範例/檔案路徑圖片的工作流程**：
    - 如果使用者詢問有哪些可用圖片 → 使用 list_sample_images()
    - 如果使用者想分析範例圖片 → 使用 analyze_product_image(product_id, image_path)
    - 若要比較多個檔案 → 使用 compare_product_images(image_paths)
    - 範例圖片位於：tutorial_implementation/tutorial21/_sample_images/

    **重點**：
    - 您具有視覺能力，可以直接看到上傳的圖片
    - analyze_uploaded_image 工具提供結構，但實際的分析由您完成
    - 對於上傳的圖片，請遵循工具回傳的 analysis_framework
    - 建立詳細、專業的目錄條目
    - 具體說明您在圖片中觀察到的內容
    - 如果使用者正在探索功能，建議使用範例圖片

    **您的分析應包括**：
    1. 產品識別 (類型、類別、品牌，如果可見)
    2. 視覺特徵 (顏色、設計、材料、尺寸)
    3. 品質指標 (結構、表面處理、狀況)
    4. 獨特功能 (獨特的賣點、創新)
    5. 市場定位 (目標客群、使用案例、區隔)

    **實用建議**：
    - 如果使用者問「你能做什麼？」，請提及範例圖片和 list_sample_images 工具
    - 如果使用者不確定，建議：「試試『列出範例圖片』來看看範例」
    - 始終樂於助人，並引導使用者使用可用資源

    始終根據您實際所見提供清晰、詳細的回應。
    """.strip(),
    tools=[
        FunctionTool(list_sample_images),
        FunctionTool(generate_product_mockup),
        FunctionTool(analyze_uploaded_image),
        FunctionTool(analyze_product_image),
        FunctionTool(compare_product_images)
    ],
    generate_content_config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=2048
    )
)


# ============================================================================
# 主要進入點 (用於測試)
# ============================================================================


async def main():
    """獨立測試的主要進入點。"""
    print("視覺目錄代理已初始化")
    print(f"代理：{root_agent.name}")
    print(f"模型：{root_agent.model}")
    print(f"工具：{len(root_agent.tools)}")

    # 如果範例圖片不存在，則建立它們
    sample_dir = Path(__file__).parent.parent / '_sample_images'
    sample_dir.mkdir(exist_ok=True)

    sample_images = [
        ('laptop.jpg', (100, 120, 140)),
        ('headphones.jpg', (50, 50, 50)),
        ('smartwatch.jpg', (80, 100, 120))
    ]

    for filename, color in sample_images:
        path = sample_dir / filename
        if not path.exists():
            create_sample_image(str(path), color)
            print(f"已建立範例圖片：{path}")

    print("\n準備處理產品圖片！")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
