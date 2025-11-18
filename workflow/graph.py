from langgraph.graph import StateGraph, END
from Agents.state import AgentState
from Agents import query_processing, routing, retrieval, response_generation
from langgraph.checkpoint.memory import MemorySaver

def build_workflow():
    workflow = StateGraph(AgentState)
    checkpointer = MemorySaver()

    # Register nodes
    workflow.add_node("query_enhancer", query_processing.query_enhancer)
    workflow.add_node("query_classifier", query_processing.query_classifier)
    workflow.add_node("off_topic_response", response_generation.off_topic_response)
    workflow.add_node("retrieve", retrieval.retrieve)
    workflow.add_node("retrieval_grader", retrieval.retrieval_grader)
    workflow.add_node("generate_answer", response_generation.generate_answer)
    workflow.add_node("refine_query", query_processing.refine_query)
    workflow.add_node("websearch", retrieval.websearch)
    workflow.add_node("greeting_response", response_generation.greeting_response)

    # Connect edges
    workflow.add_edge("query_enhancer", "query_classifier")
    workflow.add_conditional_edges("query_classifier", routing.on_topic_router, {
        "retrieve": "retrieve",
        "off_topic_response": "off_topic_response",
        "greeting_response": "greeting_response",
    })
    workflow.add_edge("retrieve", "retrieval_grader")
    workflow.add_conditional_edges("retrieval_grader", routing.proceed_router, {
        "generate_answer": "generate_answer",
        "refine_query": "refine_query",
        "websearch": "websearch",
    })
    workflow.add_edge("greeting_response", "generate_answer")
    workflow.add_edge("refine_query", "retrieve")
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("websearch", "generate_answer")
    workflow.add_edge("off_topic_response", "generate_answer")

    workflow.set_entry_point("query_enhancer")
    return workflow.compile(checkpointer=checkpointer)
