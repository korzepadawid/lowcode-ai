from langgraph.graph import StateGraph, START, END
from llm.base import LLMBase
from llm.node import decide_code_gen_type, generate_rule, generate_validation
from llm.state import GraphState


class LangGraphLLM(LLMBase):
    def __init__(self) -> None:
        self.graph = StateGraph(GraphState)
        self.graph.add_node("generate_rule", generate_rule)
        self.graph.add_node("generate_validation", generate_validation)
        self.graph.add_node("classify_code_gen", decide_code_gen_type)

        self.graph.add_conditional_edges(
            "classify_code_gen",
            lambda state: state["classification"],
            {
                "generate_validation": "generate_validation",
                "generate_rule": "generate_rule",
            },
        )

        self.graph.add_edge(START, "classify_code_gen")
        self.graph.add_edge("generate_validation", END)
        self.graph.add_edge("generate_rule", END)
        self.graph = self.graph.compile()

    def add_history(self, user: str, ai: str) -> None:
        pass

    def predict(self, input_query: str) -> dict:
        inputs = {"question": input_query}
        return self.graph.invoke(inputs)


def main():
    llm = LangGraphLLM()
    print(llm.predict("Write a pesel validator"))


if __name__ == "__main__":
    main()
