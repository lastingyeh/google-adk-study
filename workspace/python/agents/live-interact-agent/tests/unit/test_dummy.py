"""
您可以在此處新增您的單元測試。
您可以在這裡測試您的業務邏輯，包括代理程式功能、資料處理以及應用程式的其他核心元件。
"""

# 從 app.agent 模組中匯入 get_weather 函式
from app.agent import get_weather


def test_get_weather_san_francisco() -> None:
    """測試 get_weather 函式是否能為「San Francisco」回傳正確的天氣。"""
    # 呼叫 get_weather 函式，並傳入包含 "San Francisco" 的字串
    result = get_weather("What's the weather in San Francisco?")
    # 斷言（assert）函式的回傳結果是否與預期的天氣字串相符
    assert result == "It's 60 degrees and foggy."


def test_get_weather_san_francisco_abbreviation() -> None:
    """測試 get_weather 函式是否能為縮寫「SF」回傳正確的天氣。"""
    # 呼叫 get_weather 函式，並傳入包含 "sf"（San Francisco 縮寫）的字串
    result = get_weather("weather in sf")
    # 斷言函式的回傳結果是否與預期的天氣字串相符
    assert result == "It's 60 degrees and foggy."


def test_get_weather_other_location() -> None:
    """測試 get_weather 函式是否能為其他地點回傳預設的天氣。"""
    # 呼叫 get_weather 函式，並傳入一個非舊金山的地點
    result = get_weather("What's the weather in New York?")
    # 斷言函式的回傳結果是否與預期的預設天氣字串相符
    assert result == "It's 90 degrees and sunny."
