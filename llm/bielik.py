import logging
import warnings
import os

from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

from llm.base import LLMBase

warnings.filterwarnings("ignore")

logger = logging.getLogger("bielik")
load_dotenv()


class BielikLLM(LLMBase):
    def __init__(self, template: str) -> None:
        self.llm = ChatOpenAI(
            temperature=0.0,
            model=os.environ.get("BIELIK_MODEL"),
            base_url=os.environ.get("BIELIK_BASE_URL"),
            api_key=os.environ.get("BIELIK_API_KEY"),
        )
        self.current_prompt = PromptTemplate.from_template(template)
        self.llm_chain = self.current_prompt | self.llm | StrOutputParser()

    def add_history(self, user: str, ai: str) -> None:
        pass

    def predict(self, input_query: str) -> str:
        return self.llm_chain.invoke(input={"input": input_query})
