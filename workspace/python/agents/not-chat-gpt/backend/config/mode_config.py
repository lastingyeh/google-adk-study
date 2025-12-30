from google.genai import types

class ModeConfig:
    """思考模式配置"""
    
    @staticmethod
    def create_config_with_mode(thinking_mode: bool = False) -> types.GenerateContentConfig:
        """根據模式建立 GenerateContentConfig
        
        Args:
            thinking_mode: 是否啟用思考模式
            
        Returns:
            GenerateContentConfig: 配置物件
        """
        system_instruction = "你是 NotChatGPT，智慧對話助理。"
        
        if thinking_mode:
            system_instruction += "\n\n請展示你的思考過程。"
        
        return types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=1.0,
        )