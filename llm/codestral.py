import os
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI

from llm.base import LLMBase
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage


load_dotenv()
MODEL = "codestral:latest"

class CodestralLLM(LLMBase):
    def __init__(self, template: str) -> None:
        self.llm = ChatOpenAI(model=MODEL,
                              base_url="http://146.235.201.229:8080",
                              api_key="xd123"
                              )
        self.current_prompt = PromptTemplate.from_template(template)
        self.current_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.current_prompt.format()),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        self.llm_chain = self.current_prompt | self.llm | StrOutputParser()
        self.chat_history = []

    def add_history(self, user: str, ai: str) -> None:
        self.chat_history.extend([HumanMessage(content=user), ai])

    def predict(self, input_query: str) -> str:
        return self.llm_chain.invoke(
            input={"input": input_query, "chat_history": self.chat_history}
        )