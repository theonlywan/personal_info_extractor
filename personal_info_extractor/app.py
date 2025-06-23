from langgraph.graph import StateGraph, START, END
from agents.preprocess_agent import preprocess
from agents.extractor_agent import extract_info
from agents.validator_agent import validate_extracted_info
from schema.personal_profile import State

graph = StateGraph(State)
graph.add_node("preprocess", preprocess)
graph.add_node("extract", extract_info)
graph.add_node("validate", validate_extracted_info)

graph.add_edge(START, "preprocess")
graph.add_edge("preprocess", "extract")
graph.add_edge("extract", "validate")
graph.add_edge("validate", END)

app = graph.compile()