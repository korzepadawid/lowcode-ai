# Lowcode AI

Context-Aware Graph Querying for LLM-Based Code Generation

This project aims to make use of user prompts to extract contextual information from nodes in BPMN diagram graphs to automate code generation, transforming low-code platforms into no-code platforms.

###  Example:

User Prompt: If the discount code has the value "UAM5", reduce the premium by 5% and
display the premium field.

Generated code with variables (PF.UR_KodZnizkowy, PF.UR_Skladka) selected via graph clustering & LLM: 

```
if (PF.UR_KodZnizkowy.Value == "UAM5") {
    PF.UR_Skladka.Value = PF.UR_Skladka.Value * 0.95m;
    PF.UR_Skladka.SetVisible(true);
}
```

## How to run?

Create and activate a [virtual environment](https://docs.python.org/3/library/venv.html).


```
$ pip install -r requirements.txt
```

```
$ python manage.py migrate
```

```
$ python manage.py runserver 0.0.0.0:8000 
```

Prepare a `.env` file:
```
# OPENAI key for testing
OPENAI_API_KEY=

# authentication to RAG service
BIELIK_BASE_URL=
BIELIK_API_KEY=


# langsmith monitoring if needed
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=

```
## How to run docker?
```
$ docker run -p 8000:8000 --env-file .env_example ghcr.io/korzepadawid/lowcode-ai:latest
```
