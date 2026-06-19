from langchain_openai import ChatOpenAI

from config import settings

from tool.amap_weather_tool import amap_weather_tool

from langchain_core.prompts import ChatPromptTemplate, prompt

from langchain_core.output_parsers import StrOutputParser


class Agent:
    # init
    def __init__(self):
        # 基于langchain的ChatOpenAI
        self.llm = ChatOpenAI(
            model=settings.openai_api_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
            temperature=0,
            max_tokens=1024,
            streaming=True
        )
        self.tools = [amap_weather_tool]
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        prompt = ChatPromptTemplate.from_template(
            "你是一个友好的助手。用户可能会询问某个城市的天气情况。"
            "如果用户询问天气，使用提供的天气查询工具获取信息。"
            "用户说: {query}"
        )

        self.llmChain = prompt | self.llm_with_tools

    def chat(self, message):
        dict = {"query": message}
        response = self.llmChain.invoke(input=dict)
        tool_messages = []
        if response.tool_calls:
            
            for tool_call in response.tool_calls:
                if tool_call["name"] == "amap_weather_tool":
                    args = tool_call["args"]
                    result = amap_weather_tool.invoke(args)
                    tool_messages.append(result)
                    
        format_prompt = ChatPromptTemplate.from_template("""
        你是一个友好的天气助手。

        用户问题: {user_input}
        工具结果: {tool_result}
        
        请根据工具结果回答用户问题，要求：
        1. 回答自然、简洁、友好；
        2. 不要编造工具结果中没有的信息；
        3. 如果包含多个城市，请分别说明。
        """)
        format_chain = format_prompt | self.llm | StrOutputParser()
        response = format_chain.invoke(
            {"user_input": message, "tool_result": tool_messages})
        return response
