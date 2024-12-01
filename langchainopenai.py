import gradio as gr
import logging
import warnings

from typing import Optional

from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

from llm.base import LLMBase

warnings.filterwarnings('ignore')

logger = logging.getLogger("llm")
load_dotenv()


class OpenAILangChain(LLMBase):
    def __init__(self) -> None:
        self.translate_back_chain = None
        self.translate_back_prompt = None
        self.code_assistant_chain = None
        self.code_assistant_prompt = None
        self.detect_language_chain = None
        self.detect_language_prompt = None
        self.translation_chain = None
        self.translate_prompt = None

        self.llm_model = "gpt-3.5-turbo"
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key="input")
        self.llm = ChatOpenAI(temperature=0.2, model=self.llm_model)
        self.init_prompts()

    def init_prompts(self) -> None:

        self.code_assistant_prompt = ChatPromptTemplate.from_template(
            "You are an assistant for a lowcode platform, you're going to help with JavaScript and C#, be concise:"
            "\n\n{input}\n\nChat history:\n{chat_history}"
        )
        self.code_assistant_chain = LLMChain(
            llm=self.llm, prompt=self.code_assistant_prompt, output_key="assistant_help", memory=self.memory,
        )


    def predict(self, input_query: str) -> dict:
        logger.info(f"Predicting, {input_query}")
        logger.info(f"Chat history: {self.memory.load_memory_variables({})}")

        return self.code_assistant_chain(input_query)

    def add_history(self, user: Optional[str], ai: Optional[str]) -> None:
        if user:
            self.memory.chat_memory.add_user_message(user)
        if ai:
            self.memory.chat_memory.add_ai_message(ai)


def gradio_fn(_llm_chain: OpenAILangChain):
    chat_history = []

    def gradio_predict(input_text):
        result = _llm_chain.predict(input_text)
        chat_history.append((input_text, result['assistant_help']))
        _llm_chain.add_history(result['input'], result['assistant_help'])

        return chat_history

    return gradio_predict


if __name__ == "__main__":
    llm_chain = OpenAILangChain()

    with gr.Blocks() as iface:
        with gr.Column(scale=1, elem_id="chat_column"):
            chatbot = gr.Chatbot()

        with gr.Row(elem_id="input_row"):
            user_input = gr.Textbox(placeholder="Type your message...", show_label=False)

        user_input.submit(gradio_fn(llm_chain), user_input, chatbot)

    iface.launch()
