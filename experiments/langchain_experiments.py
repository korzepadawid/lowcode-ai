import warnings

from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SequentialChain

warnings.filterwarnings('ignore')

llm_model = "gpt-3.5-turbo"
llm = ChatOpenAI(temperature=0.2, model=llm_model)
memory = ConversationBufferMemory(memory_key="chat_history", input_key="english_input")
memory.chat_memory.add_user_message("Can you write a JavaScript function to validate a polish PESEL?")
memory.chat_memory.add_ai_message(
    """
    function isValidPesel(pesel) {
        let weight = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3];
        let sum = 0;
        let controlNumber = parseInt(pesel.substring(10, 11));

        for (let i = 0; i < weight.length; i++) {
            sum += (parseInt(pesel.substring(i, i + 1)) * weight[i]);
        }
        sum = sum % 10;
        return (10 - sum) % 10 === controlNumber;
    }
    """
)

translate_prompt = ChatPromptTemplate.from_template(
    "Translate the following input to english, don't translate programming code, leave it as it is"
    "\n\n{input}"
)
translation_chain = LLMChain(
    llm=llm, prompt=translate_prompt, output_key="english_input",
)

detect_language_prompt = ChatPromptTemplate.from_template(
    "What language is the following input:\n\n{input}"
)
detect_language_chain = LLMChain(
    llm=llm, prompt=detect_language_prompt, output_key="language"
)

code_assistant_prompt = ChatPromptTemplate.from_template(
    "You are a code assistant specializing in JavaScript and C# for a low-code platform. "
    "Your task is to assist with coding queries, including debugging, code suggestions, and explanations."
    "\n\nInput:\n{english_input}\n"
    "{% if chat_history %}\nChat History:\n{chat_history}\n{% else %}\n(No prior chat history)\n{% endif %}"
    "\nPlease respond with a detailed and helpful explanation, and include code examples where appropriate."
)
code_assistant_chain = LLMChain(
    llm=llm, prompt=code_assistant_prompt, output_key="assistant_help", memory=memory
)

translate_back_prompt = ChatPromptTemplate.from_template(
    "Translate the following text to {language}:\n\n\n{assistant_help}",
)
translate_back_chain = LLMChain(
    llm=llm, prompt=translate_back_prompt, output_key="final_response"
)

print(memory.load_memory_variables({}))
overall_chain = SequentialChain(
    chains=[translation_chain, detect_language_chain, code_assistant_chain, translate_back_chain],
    input_variables=["input"],
    output_variables=["english_input", "language", "assistant_help", "final_response"],
    verbose=False,
)

response = overall_chain(
    "Mozesz przerobić to na C#?"
)
print(response)
