# 初始化 setting 类, 用pydantic导入各种key
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.openai_like import OpenAILike

from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.node_parser import SemanticSplitterNodeParser


from llama_index.core import Document, VectorStoreIndex
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
import os
from typing import List, Union
from paddleocr import PaddleOCR
from PIL import Image
import time


load_dotenv()  # 从 .env 文件加载环境变量到系统环境


class AppSettings(BaseSettings):
    agnes_api_model: str = Field(..., env="AGNES_API_MODEL")
    agnes_api_key: str = Field(..., env="AGNES_API_KEY")
    agnes_api_url: str = Field(..., env="AGNES_API_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = ""
        extra = "ignore"


setting = AppSettings()


class ImageOCRReader(BaseReader):
    """使用 PP-OCR v5 从图像中提取文本并返回 Document"""

    def __init__(self, lang="ch", **kwargs):
        """
        Args:
            lang: OCR 语言 ('ch', 'en', 'fr', etc.)
            **kwargs: 其他传递给 PaddleOCR 的参数
        """
        self.lang = lang
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,  # 通过 use_doc_orientation_classify 参数指定不使用文档方向分类模型
            use_doc_unwarping=False,  # 通过 use_doc_unwarping 参数指定不使用文本图像矫正模型
            use_textline_orientation=False,  # 通过 use_textline_orientation 参数指定不使用文本行方向分类模型
        )

    def load_data(self, file: Union[str, List[str]], **kwargs) -> List[Document]:
        """
        从单个或多个图像文件中提取文本，返回 Document 列表
        Args:
            file: 图像路径字符串 或 路径列表
            **kwargs: 其他传递给 PaddleOCR 的参数
        Returns:
            List[Document]
        """
        # 实现 OCR 提取逻辑
        # 将每张图的识别结果拼接成文本
        # 构造 Document 对象，附带元数据（如 image_path, ocr_confidence_avg）

        if isinstance(file, str):
            file = [file]
        print("----------")
        print(len(file))
        documents = []
        for f in file:
            if not os.path.exists(f):
                raise FileNotFoundError(f"文件不存在: {f}")
            if not f.endswith((".jpg", ".jpeg", ".png", ".bmp")):
                raise ValueError(f"文件格式错误: {f}")

            img = Image.open(f)
            width, height = img.size
            # 读取图像文件
            # with open(f, 'rb') as img:
            #     image_data = img.read()
            # 调用 PaddleOCR 进行识别
            result = self.ocr.ocr(f)
            text = ""
            num_text_blocks = 0
            total_confidence = 0
            for item in result[0]:  # 遍历每个文字区域
                text += item[1][0] + "\n"  # 识别的文字
                num_text_blocks = len(item[1][0])
                total_confidence += item[1][1]
                # 构造 Document 对象

            document = Document(
                text=text,
                metadata={
                    "image_path": f,
                    # 基础信息
                    "file_name": os.path.basename(f),
                    "file_size": os.path.getsize(f),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    # OCR 信息
                    "ocr_lang": "ch",
                    "ocr_word_count": len(text),
                    "ocr_model_version": "PP-OCRv4",
                    # 图片信息
                    "image_width": width,
                    "image_height": height,
                    "image_format": "png",
                    "num_text_blocks": num_text_blocks,
                    "avg_confidence": total_confidence / num_text_blocks,
                },
            )
            documents.append(document)
        return documents


from llama_index.core.node_parser import (
    TokenTextSplitter,
    SentenceSplitter,
    SemanticSplitterNodeParser,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

Settings.llm = OpenAILike(
    model=setting.agnes_api_model,
    api_base=setting.agnes_api_url,
    api_key=setting.agnes_api_key,
    is_chat_model=True,
)


Settings.embed_model = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh-v1.5"  # 中文效果好的免费模型
)


reader = ImageOCRReader(lang="ch")
documents = reader.load_data(
    ["./images/general_ocr_002.png", "./images/clock_image.png"]
)

# splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=10, separator="\n")

splitter = SentenceSplitter(
    chunk_overlap=30,
    chunk_size=200,
    separator="\n",
)

nodes = splitter.get_nodes_from_documents(documents)
print("--------document count------->>>>>>>>>-", len(documents))
for node in nodes:
    print(node.text)
    print("----------------")
    print(node.metadata)
    print("----------------")


index = VectorStoreIndex(nodes)
query_engine = index.as_query_engine()
response = query_engine.query("图片中提到了什么日期？")
print(response)
