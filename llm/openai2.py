import logging
import warnings

from dotenv import load_dotenv

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage

from llm.base import LLMBase

warnings.filterwarnings("ignore")

logger = logging.getLogger("openai2")
load_dotenv()


class OpenAILangChainV2(LLMBase):
    def __init__(self, template: str) -> None:
        self.llm_model = "gpt-4"
        self.llm = ChatOpenAI(temperature=0.0, model=self.llm_model)

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

    def predict(self, input_query: str) -> dict:
        return self.llm_chain.invoke(
            input={"input": input_query, "chat_history": self.chat_history}
        )