from .state import AgentState
from chains.rag_chain import *

def on_topic_router(state: AgentState):
    print("Entering on_topic_router")
    on_topic = state.get("on_topic", "").strip().lower()
    if on_topic == "yes":
        print("Routing to retrieve")
        return "retrieve"
    elif on_topic == "greeting":
        print("Routing to greeting_response")
        return "greeting_response"
    else:
        print("Routing to off_topic_response")
        return "off_topic_response"
    
def proceed_router(state: AgentState):
    print("Entering proceed_router")
    rephrase_count = state.get("rephrase_count", 0)

    if state.get("proceed_to_generate", False):
        print("Relevant documents found. Routing to generate_answer.")
        return "generate_answer"
    
    if rephrase_count >= 2:
        print("No relevant docs and rephrased 2 times. Routing to websearch.")
        return "websearch"
    
    print("No relevant docs. Will try refining the query.")
    return "refine_query"
