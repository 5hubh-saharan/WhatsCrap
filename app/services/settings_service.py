# app/services/settings_service.py
from typing import Dict, Any

class SettingsService:
    @staticmethod
    async def get_user_settings(db, user_id: str) -> Dict[str, Any]:
        """获取用户设置"""
        try:
            import uuid
            user_uuid = uuid.UUID(user_id)
            # 这里可以从数据库中获取用户设置
            # 目前我们使用 session，但可以扩展到数据库存储
            return {}
        except Exception:
            pass
        
        return {}
    
    @staticmethod
    async def save_user_settings(db, user_id: str, settings: Dict[str, Any]) -> bool:
        """保存用户设置到数据库（未来扩展）"""
        # 目前使用 session，这里可以添加数据库存储逻辑
        return True
    
    @staticmethod
    def get_default_settings() -> Dict[str, Any]:
        """获取默认设置"""
        return {
            "theme_color": "#f5f5f5",
            "my_bubble_color": "#667eea",
            "other_bubble_color": "#f5f7fa",
            "room_display": "bubble",
            "font_size": "medium",
            "notification_sound": True,
            "auto_scroll": True,
            "show_timestamps": True,
            "show_avatars": False
        }
    
    @staticmethod
    def validate_settings(settings: Dict[str, Any]) -> tuple[bool, str]:
        """验证设置是否有效"""
        required_fields = ["theme_color", "my_bubble_color", "other_bubble_color", "room_display"]
        
        for field in required_fields:
            if field not in settings:
                return False, f"Missing required field: {field}"
        
        # 验证颜色格式
        import re
        hex_color_pattern = re.compile(r'^#(?:[0-9a-fA-F]{3}){1,2}$')
        
        color_fields = ["theme_color", "my_bubble_color", "other_bubble_color"]
        for field in color_fields:
            if not hex_color_pattern.match(settings[field]):
                return False, f"Invalid color format for {field}"
        
        # 验证 room_display
        if settings["room_display"] not in ["bubble", "grid"]:
            return False, "Invalid room display option"
        
        return True, "Settings are valid"
    
    @staticmethod
    def merge_settings(current: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """合并设置，保留未修改的字段"""
        default_settings = SettingsService.get_default_settings()
        merged = {**default_settings, **current, **new}
        return merged