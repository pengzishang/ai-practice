# 初始化 setting 类, 用pydantic导入各种key
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载环境变量到系统环境


class Settings(BaseSettings):
    
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    openai_api_base: str = Field(..., env='OPENAI_API_BASE')
    openai_api_model: str = Field(..., env='OPENAI_API_MODEL')
    amap_api_key: str = Field(..., env='AMAP_API_KEY')
    amap_api_base: str = Field(..., env='AMAP_API_BASE')
    tavily_api_key: str = Field(..., env='TAVILY_API_KEY')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_prefix = ''


settings = Settings()  # 创建 APISettings 实例