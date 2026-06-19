# 初始化 setting 类, 用pydantic导入各种key
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # 从 .env 文件加载环境变量到系统环境


class Settings(BaseSettings):
    
    autogen_model: str = Field(..., env='AUTOGEN_MODEL')
    autogen_api_key: str = Field(..., env='AUTOGEN_API_KEY')
    autogen_base_url: str = Field(..., env='AUTOGEN_BASE_URL')
    autogen_temperature: float = Field(..., env='AUTOGEN_TEMPERATURE')
    autogen_timeout: int = Field(..., env='AUTOGEN_TIMEOUT')
    max_round: int = Field(..., env='MAX_ROUND')
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = False
        env_prefix = ''
        extra = 'ignore'
