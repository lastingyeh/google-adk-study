from __future__ import annotations

from google.adk.agents import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

CHUCK_NORRIS_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "查克·諾里斯 API",
        "description": "免費的 JSON API，提供精心挑選的查克·諾里斯笑話",
        "version": "1.0.0",
    },
    "servers": [{"url": "https://api.chucknorris.io/jokes"}],
    "paths": {
        "/random": {
            "get": {
                "operationId": "get_random_joke",
                "summary": "取得隨機的查克·諾里斯笑話",
                "description": "從資料庫中檢索一個隨機笑話。可以選擇按類別篩選。",
                "parameters": [
                    {
                        "name": "category",
                        "in": "query",
                        "description": "按類別篩選笑話（可選）",
                        "required": False,
                        "schema": {"type": "string"},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功回應",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "icon_url": {"type": "string"},
                                        "id": {"type": "string"},
                                        "url": {"type": "string"},
                                        "value": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/search": {
            "get": {
                "operationId": "search_jokes",
                "summary": "搜尋笑話",
                "description": "依據查詢詞進行全文搜尋笑話。",
                "parameters": [
                    {
                        "name": "query",
                        "in": "query",
                        "description": "搜尋查詢（需要 3 個以上字元）",
                        "required": True,
                        "schema": {"type": "string", "minLength": 3},
                    }
                ],
                "responses": {
                    "200": {
                        "description": "成功回應",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "total": {"type": "integer"},
                                        "result": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "icon_url": {"type": "string"},
                                                    "id": {"type": "string"},
                                                    "url": {"type": "string"},
                                                    "value": {"type": "string"},
                                                },
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/categories": {
            "get": {
                "operationId": "get_categories",
                "summary": "取得所有笑話類別",
                "description": "檢索可用的笑話類別列表。",
                "responses": {
                    "200": {
                        "description": "成功回應",
                        "content": {
                            "application/json": {
                                "schema": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                    }
                },
            }
        },
    },
}

chuck_norris_toolset = OpenAPIToolset(spec_dict=CHUCK_NORRIS_SPEC)

root_agent = Agent(
    name="chuck_norris_agent",
    model="gemini-2.0-flash",
    description="""
    查克·諾里斯笑話助理，可以使用 OpenAPI 工具從
    查克·諾里斯 API 檢索笑話/事實。
    """,
    instruction="""
    你是一個有趣的查克·諾里斯笑話助理！

    功能：
    - 取得隨機的查克·諾里斯笑話（可選擇按類別篩選）
    - 搜尋包含特定關鍵字的笑話
    - 列出所有可用的笑話類別

    風格：
    - 熱情、俏皮
    - 查克·諾里斯的笑話為達喜劇效果而誇大
    - 清晰地格式化笑話以便閱讀
    - 如果搜尋返回多個結果，則顯示幾個最好的結果

    工作流程：
    - 對於隨機請求 → 使用 get_random_joke
    - 對於特定主題 → 使用帶有查詢的 search_jokes
    - 若要查看類別 → 使用 get_categories
    - 對於特定類別的隨機 → 使用帶有類別參數的 get_random_joke

    重要事項：
    - 務必從 API 回應中提取 'value' 欄位（這才是真正的笑話）
    - 如果搜尋結果為 0，建議嘗試不同的關鍵字
    - 類別為小寫（例如 "dev"、"movie"、"food"）
    """,
    # 將工具集傳遞給代理
    toolsets=[chuck_norris_toolset],
)
