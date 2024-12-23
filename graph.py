import logging
from typing import Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from llm.base import LLMBase
from llm.bielik import BielikLLM
from llm.codestral import CodestralLLM
from llm.openai2 import OpenAILangChainV2

VALIDATION_TYPE = "VALIDATION"
RULE_TYPE = "RULE"
GENERAL = "GENERAL"

QUESTION_TYPES = [VALIDATION_TYPE, RULE_TYPE, GENERAL]

logger = logging.getLogger("graph_llm")


class GraphState(TypedDict):
    question: Optional[str]
    question_type: Optional[str]
    response: Optional[str]
    in_english: Optional[str]


def generate_validation(state: GraphState) -> dict:
    template = """
    You're an AI assistant on the Ferryt Low-Code Platform.

    Your task is to help users create simple validation logic in JavaScript. Follow these instructions strictly:

    1. **Return Only Code**: By default, respond with **only the JavaScript validation code**. Do not add explanations or comments unless the user explicitly asks for an explanation.

    2. **Syntax Restrictions**: 
    - **No ES6+ Syntax**: Use only ES5 syntax.
    - **No Functions or Methods**: Write standalone code snippets without functions.

    3. **Validation Code Requirements**:
    - The input to validate is always a string, accessible through `arguments.Value`.
    - The code must assign a boolean value to `arguments.IsValid`:
        - Set `arguments.IsValid` to `true` if valid, and `false` otherwise.
    - Do not return any values or produce output; only update `arguments.IsValid`.

    4. **Code Style**:
    - Keep the code simple and avoid complex or "fancy" syntax.

    5. **Explain Only When Asked**: If the user requests an explanation or further details, then and only then, provide additional information about the code.

    6. **Unknown Answers**: If you do not know the answer, respond with "I don't know" instead of guessing or making up information.

    Always remember: respond with code only, unless instructed otherwise.

    """
    llm = CodestralLLM(template)
    answer = llm.predict(state["question"])
    logger.info(answer)
    return {"response": answer}


def generate_rule(state: GraphState) -> dict:
    template = """
    You're an AI assistant on the Ferryt Low-Code Platform.

    # Universal Prompt for C# Code Generation for Client Data and Screens Management

    When writing C# code, use the available process fields and screens to manage client data and user interface. Follow these guidelines:

    ## 1. Available Process Fields:
    - `PF.DKL_DaneKlienta_S.RodzajKonta`
    - `PF.DKL_DaneKlienta_S.NumerKonta`
    - `PF.DKL_DaneKlienta_S.RodzajKarty`
    - `PF.DKL_DaneKlienta_S.Wiek`
    - `PF.DKL_DaneKlienta_S.ImieINazwisko`
    - `PF.DKL_DaneKlienta_S.Login`
    - `PF.DKL_DaneKlienta_S.Email`
    - `PF.DKL_DaneKlienta_S.ID`

    ### Properties:
    Fields have the following properties:
    - `HasValue`, `IsEditable`, `IsRequired`, `IsVisible`, `Value`.

    ### Actions:
    You can perform these operations on the fields:
    - `SetEditable(bool)`, `SetVisible(bool)`, `SetRequired(bool)`, `SetNull()`, `GetValueOrDefault(defaultValue)`.

    ## 2. Available Screens:
    - `Ekran1`, `Ekran2`, `Tech_BottomScreen`, `Tech_ErrorMessage`.

    ### Methods:
    Screens can be controlled using the following methods:
    - `Hide()`, `HideAll()`, `Show()`, `ShowAll()`.

    ## 3. Accessing User Data:
    - `USER.Current` provides access to properties like `IsAuthenticated`, `UserLogin`, `UserFullName`, `UserEmail`, `UserID`, etc.

    ### Properties:
    User properties have:
    - `HasValue`, `Value`.

    ## 4. Example Functionalities:
    - Setting field values based on conditions.
    - Controlling field visibility, editability, and requirements.
    - Assigning user data to client data under specific conditions.
    - Displaying or hiding screens.

    Always remember: respond with code only, unless instructed otherwise.
    """
    llm = OpenAILangChainV2(template)
    answer = llm.predict(state["question"])
    logger.info(answer)
    return {"response": answer}


def translate_pl_to_en(state: GraphState) -> dict:
    template = """
    Jesteś tłumaczem języka polskiego na angielski. 
    Przetłumacz poniższy tekst z polskiego na angielski. 
    Zwróć wyłącznie przetłumaczony tekst, bez żadnych dodatkowych informacji, komentarzy czy pytań: {input}
    """
    llm = BielikLLM(template)
    answer = llm.predict(state["question"])
    print("Translated: " + answer)
    return {"in_english": state["question"]}


def determine_question_type(state: GraphState) -> dict:
    template = """
    Jesteś systemem odpowiedzialnym za wykrywanie typu pytania. Działasz na platformie low-code Ferryt, która umożliwia tworzenie aplikacji webowych w oparciu o diagramy BPMN.

    ### Zasady działania:
    - Jeśli pytanie lub prośba zawiera:  
    - Odwołania do funkcji programistycznych (np. `SetEditable(bool)`, `SetVisible(bool)`, `GetValueOrDefault(defaultValue)` itp.).  
    - Odniesienia do pól, zmiennych, reguł biznesowych lub logiki walidacji (np. `PF.DKL_DaneKlienta_S.RodzajKonta`).  
    - Polecenia dotyczące generowania, poprawiania lub analizowania kodu.  
    W takich przypadkach zwróć odpowiedź: **CODE**.  

    - Jeśli pytanie dotyczy dokumentacji lub ma charakter ogólny, zwróć odpowiedź: **GENERAL**.  

    Zwracaj wyłącznie odpowiedź: **CODE** lub **GENERAL**, bez dodatkowych informacji ani komentarzy.

    Tekst pytania: {input}
    """
    llm = BielikLLM(template)
    answer = llm.predict(state["question"])
    print("Answer (type): " + answer)
    if answer == GENERAL:
        return {"question_type": GENERAL}
    return {"question_type": state["question_type"]}


def general(state: GraphState) -> dict:
    return {"response": "General prompt here"}


class LangGraphLLM(LLMBase):
    def __init__(self) -> None:
        self.graph = StateGraph(GraphState)
        self.graph.add_node("generate_rule", generate_rule)
        self.graph.add_node("generate_validation", generate_validation)
        self.graph.add_node("general", general)
        self.graph.add_node("translate_pl_to_en", translate_pl_to_en)
        self.graph.add_node("determine_question_type", determine_question_type)

        self.graph.add_conditional_edges(
            "determine_question_type",
            lambda state: state["question_type"],
            {
                "VALIDATION": "generate_validation",
                "RULE": "generate_rule",
                "GENERAL": "general",
            },
        )

        self.graph.add_edge(START, "translate_pl_to_en")
        self.graph.add_edge("translate_pl_to_en", "determine_question_type")
        self.graph.add_edge("generate_validation", END)
        self.graph.add_edge("generate_rule", END)
        self.graph.add_edge("general", END)
        self.graph = self.graph.compile()

    def add_history(self, user: str, ai: str) -> None:
        pass

    def predict(self, input_query: str, question_type: str) -> dict:
        inputs = {
            "question": input_query,
            "question_type": question_type,
        }
        return self.graph.invoke(inputs)


def main():
    llm = LangGraphLLM()
    print(llm.predict("Write a pesel validator", "GENERAL"))


if __name__ == "__main__":
    main()
