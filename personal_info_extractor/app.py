from langgraph.graph import StateGraph, START, END
from agents.preprocess_agent import preprocess
from agents.extractor_agent import extract_info
from agents.validator_agent import validate_extracted_info
from agents.vectorDB_agent import embed_and_store_profile
from schema.personal_profile import State

graph = StateGraph(State)
graph.add_node("preprocess", preprocess)
graph.add_node("extract", extract_info)
graph.add_node("validate", validate_extracted_info)
graph.add_node("vector_db", embed_and_store_profile)

graph.add_edge(START, "preprocess")
graph.add_edge("preprocess", "extract")
graph.add_edge("extract", "validate")
graph.add_edge("validate", "vector_db")
graph.add_edge("vector_db", END)

app = graph.compile()