from llm.codestral import CodestralLLM
from llm.state import GraphState


def generate_validation(state: GraphState) -> GraphState:
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
    answer = llm.predict(state['question'])
    print(answer)
    return {"response": answer}


def generate_rule(state: GraphState) -> GraphState:
    return {"response": "Your rule code here"}


def decide_code_gen_type(state: GraphState) -> GraphState:
    return {"classification": "generate_validation"}
