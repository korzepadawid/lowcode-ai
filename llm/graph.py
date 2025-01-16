import logging
from typing import List, Optional, TypedDict

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage
from llm.base import LLMBase
from llm.bielik import BielikLLM
from llm.codestral import CodestralLLM
# from llm.openai2 import OpenAILangChainV2
from langchain_core.messages import HumanMessage, AIMessage

VALIDATION_TYPE = "WALIDACJA"
RULE_TYPE = "REGUŁA"
GENERAL = "OGÓLNE"

QUESTION_TYPES = [VALIDATION_TYPE, RULE_TYPE, GENERAL]

logger = logging.getLogger("graph")


class GraphState(TypedDict):
    question: Optional[str]
    question_type: Optional[str]
    response: Optional[str]
    question_in_english: Optional[str]
    response_in_english: Optional[str]
    messages: List[BaseMessage]


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
    llm.chat_history = state["messages"]
    logger.info("Input (validation): %s", state["question_in_english"])
    answer = llm.predict(state["question_in_english"])
    logger.info("Code generated (validation): %s", answer)
    return {"response_in_english": answer}


def generate_rule(state: GraphState) -> dict:
    template = """
    You're an AI assistant on the Ferryt Low-Code Platform.

    # Universal Prompt for C# Code Generation for Client Data and Screens Management

    When writing C# code, use the available process fields and screens to manage client data and user interface. Follow these guidelines:

    ## 1. Available Process Fields:
    - `PF.UR_DaneKlienta_S.Imie` : String
    - `PF.UR_DaneKlienta_S.Nazwisko` : String
    - `PF.UR_DaneKlienta_S.Email` : String
    - `PF.UR_DaneKlienta_S.NrTelefonu` : String
    
    - `PF.UR_DaneRodziny_T` : table
        * Imie
        * Nazwisko 
        * Wiek
        
    - `PF.UR_KodZnizkowy` : String
    - `PF.UR_OdrzuceniePrzezWiek` : Bool
    - `PF.UR_PoziomUbezpieczenia` : String
    - `PF.UR_RodzajUbezpieczenia` : String
    - `PF.UR_Skladka` : Decimal
    - `PF.UR_UbezpieczenieDodatkowe` : Bool
    - `PF.tech_Message` : String
    

    ### Properties:
    Fields have the following properties:
    - `HasValue`, `IsEditable`, `IsRequired`, `IsVisible`, `Value`.

    ### Actions:
    You can perform these operations on the fields:
    - `SetEditable(bool)`, `SetVisible(bool)`, `SetRequired(bool)`, `SetNull()`, `GetValueOrDefault(defaultValue)`.
    
    ### Arrays:
    - Arrays are complex datatypes that store fields or structures. Their name should end with `_T`.
        A specific element in the array can be accessed via `[index]` or `.Items(index)`.
    - Operations on arrays: Length, SetMinimumSize(int)

    ## 2. Available Screens:
    - `E010_Powitanie` (alias =`Powitanie`)
    - `E020_DaneRodziny` (alias =`Dane rodziny`)
    - `E030_WyborUbezpieczenia` (alias =`Wybór ubezpieczenia`)
    - `E040_Zgody` (alias =`Zgody`)
    - `E050_Podsumowanie` (alias =`Podsumowanie`)
    - `E060_Odrzucenie` (alias =`Odrzucenie`)
    - `E_techMessage` (alias =`E_techMessage`)
    - `Tech_SessionEndScreen` (alias =`Tech_SessionEndScreen`)
    - `Tech_TopScreen` (alias =`Tech_TopScreen`)
    - `Tech_BottomScreen` (alias =`Tech_BottomScreen`)
    - `Tech_TabsScreen` (alias =`Tech_TabsScreen`)

    ### Methods:
    Screens can be accessed by `G.`.
    Screens can be controlled using the following methods:
    - `Hide()`, `HideAll()`, `Show()`, `ShowAll()`.

    ## 3. Accessing User Data:
    - `USER.Current` provides access to properties like `IsAuthenticated`, `UserLogin`, `UserFullName`, `UserEmail`, 
        `UserID`, etc.
        
    ## 4. ENV Object:
    - ENV gives access to many environment variables like:
        * ActionIndices[0] - points to the element on which the action was last performed (in arrays)
        * ApplicationGuid
        * UserDevice.IsMobile
        * UserDevice.BrowserInfo
        * UserDevice.OperatingSystem etc.
        
    ## 5. ACTION object
    - ACTION object has methods like: `ClearDocumentRequirement()`, `ClearFieldRequirement()`, 
        `SetFieldsReadOnly()` - disables editable fields, `VisibilityFlagHide(flagName)` - hide all actions with the 
        flag set, `VisibilityFlagHideAll()`, `VisibilityFlagShow(flagName)` - show all actions with the flag set`, 
        `VisibilityFlagShowAll()`
        
    ## 6. LOOPS?
    
    ## 7. Enumerator?

    ## 8. Example Functionalities:
    - Setting field values based on conditions.
    - Controlling field visibility, editability and requirements.
    - Assigning user data to client data under specific conditions.
    - Displaying or hiding screens.
    
    ## 9. Notes:
    - Reference to the `.Value` property, may cause an error if the field is null. 
        To avoid this, first check that the value is via `.HasValue`.
    - If code is very simple, divide it to the 3 separate blocks: `if` , `then`, `else`. `If` statement must not be 
        empty. If something is to be executed every time, enter `true` there.

    Always remember: respond with code only, unless instructed otherwise.
    """
    llm = CodestralLLM(template)
    llm.chat_history = state["messages"]
    answer = llm.predict(state["question_in_english"])
    logger.info("Code generated: %s", answer)
    return {"response_in_english": answer}


def translate_pl_to_en(state: GraphState) -> dict:
    template = """
    # Instrukcje dla modelu:

    1. Jesteś tłumaczem języka polskiego na angielski.
    2. Twoim jedynym zadaniem jest **przetłumaczenie podanego tekstu z polskiego na angielski**.
    3. Odpowiadaj **tylko** tłumaczeniem tekstu, niczym więcej.
    4. **Nie odpowiadaj na pytania**, **nie generuj kodu**, ani **nie podawaj wyjaśnień**.  
    5. Każda odpowiedź zawierająca coś innego niż przetłumaczony tekst będzie błędna.

    ## Tekst do przetłumaczenia:
    {input}

    ## Ważne:
    - Nie modyfikuj polecenia.  
    - Nie interpretuj tekstu.  
    - Zwróć **tylko** przetłumaczone zdanie w języku angielskim.
    """
    llm = BielikLLM(template)
    answer = llm.predict(state["question"])
    logger.info("Translated to English: %s", answer)
    return {"question_in_english": answer}


def translate_en_to_pl(state: GraphState) -> dict:
    if state["response_in_english"].startswith("```") and state[
        "response_in_english"
    ].endswith("```"):
        return {"response": state["response_in_english"]}

    template = """
    **Task Description:**  
    Translate the given text strictly and accurately from English to Polish. Do not interpret, analyze, or respond to the question itself. Your sole task is to provide the translation of the text as-is, without any additional comments, clarifications, or modifications.

    **Critical Instructions:**  
    1. Do not interpret the input text in any way.  
    2. Do not provide an explanation, commentary, or answer to the question itself.  
    3. Respond exclusively with the translation of the text provided in the input.  
    4. Do not deviate from the structure, meaning, or intent of the original text during translation.
    5. **Do not write any introductory phrases such as "Here is the translation of the given text into Polish." or similar.**  


    **Key Restriction:**  
    - **Under no circumstances should you generate, write, or modify code in your response.**

    **Expected Behavior:**  
    When given a text to translate, output only the translated text in Polish. Do not provide introductions, explanations, examples, or additional information in your response. Your role is limited to providing a faithful and direct translation.

    Text to Translate:  
    {input}
    """
    llm = BielikLLM(template)
    answer = llm.predict(state["response_in_english"])
    logger.info("Translated (back): %s", answer)
    return {"response": answer}


def determine_question_type(state: GraphState) -> dict:
    template = """
    Jesteś klasyfikatorem, który identyfikuje typ pytania na podstawie następujących kategorii:

    1. **Prośba o wygenerowanie kodu do walidatora**: 
       - Pytania dotyczące tworzenia kodu w celu weryfikacji danych wejściowych zgodnie z określonymi regułami lub formatami (np. weryfikacja adresów e-mail, numeru pesel, dat itp.).
       - Przykłady:
            1. Napisz walidator pesel.
            2. Czy potrafisz napisać walidator NIP, który sprawdza poprawność numeru NIP, uwzględniając liczbę cyfr i format?
            3. Zaimplementuj walidator kodu pocztowego.
            4. Daj mi walidator wieku, który ocenia, czy użytkownik ma wiek mieszczący się w przedziale 18-60 lat.
            5. Przygotuj sprawdzenie daty, czy jest w formacie dd/mm/yyyy.
            6. Wygeneruj walidator numeru karty kredytowej.
            7. Stwórz walidator numeru telefonu.
            8. Jak napisać walidator numeru telefonu?
            9. Sprawdzenie czy wiek jest większy niż 75 lat.
            10. Walidacja czy liczba jest w zakresie 1-1000.

    2. **Prośba o wygenerowanie kodu dla reguły**:
       - Pytania dotyczące reguł biznesowych, które są definiowane w ramach procesów BPMN i służą do automatyzacji decyzji oraz sterowania przepływem procesów na podstawie określonych warunków.
        - Przykłady:
            1. Ustaw odrzucenie przez wiek na true jeżeli jeden członek rodziny jest niepełnoletni.
            2. Sprawdź czy w rodzinie istnieje osoba starsza niż 80 lat, jeśli tak zmień składkę podstawową na 100 * ilość osób w rodzinie.
            3. Jeśli typ pojazdu jest ustawiony to pokaż pole z jego marką.
            4. Jeśli AC jest wyłączone i NNW jest włączone, przypisz kwotę polisy 2700.
            5. Wyświetl wiadomość jeśli nie jest pusta.
            6. Ustaw rodzaj karty na Junior jeśli rodzaj konta ma wartość „dla młodych” i wiek jest mniejszy od 21. 
            7. Ustaw wszystkie pola z danych klienta z wyjątkiem numeru konta na edytowalne, widoczne i wymagalne. Numer konta ma być tylko widoczny.
            8. Jeśli login aktualnego użytkownika jest zgodny z tym z danych klienta i jest uwierzytelniony, to przypisz do danych klienta jego imię i nazwisko, email i ID.
            9. Sprawdź czy aktualnie podany numer konta w tablicy z danymi klienta znajduje się już w niej w innych wierszach. Jeśli nie, to w przypadku gdy użytkownik logował się na urządzeniu mobilnym, to pokaż zostaw widoczny jedynie ekran Tech_ErrorMessage.
            10. Ustaw minimalną długość tablicy z danymi rodziny na 1.


    3. **Pytania ogólne**:
       - Pytania ogólne, które nie klasyfikują się do poprzednich typów pytań.


    **Odpowiedz tylko jednym słowem WALIDACJA, REGUŁA, OGÓLNE według pasującej kategorii.**
    """
    llm = BielikLLM(template)
    prompt = f'Pytanie: {state["question"]}'
    answer = llm.predict(prompt)
    logger.info("Detected question type: %s", answer)
    return {"question_type": answer}


def general(state: GraphState) -> dict:
    return {"response": "General prompt here"}


class LangGraphLLM(LLMBase):
    def __init__(self, thread_id: str) -> None:
        self.graph = StateGraph(GraphState)
        self.graph.add_node("generate_rule", generate_rule)
        self.graph.add_node("generate_validation", generate_validation)
        self.graph.add_node("general", general)
        self.graph.add_node("translate_pl_to_en", translate_pl_to_en)
        self.graph.add_node("translate_eng_to_pl", translate_en_to_pl)
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
        self.graph.add_edge("generate_validation", "translate_eng_to_pl")
        self.graph.add_edge("generate_rule", "translate_eng_to_pl")
        self.graph.add_edge("translate_eng_to_pl", END)
        self.graph.add_edge("general", END)
        self.graph = self.graph.compile()
        self.chat_history = []
        self.thread_id = thread_id

    def add_history(self, user: str, ai: str) -> None:
        self.chat_history.extend([HumanMessage(content=user), AIMessage(content=ai)])

    def predict(self, input_query: str, question_type: str) -> dict:
        inputs = {
            "question": input_query,
            "question_type": question_type,
            "messages": self.chat_history,
        }
        return self.graph.invoke(inputs)
