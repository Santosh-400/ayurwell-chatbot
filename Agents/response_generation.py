from .state import AgentState
from langchain_core.messages import AIMessage
from chains.rag_chain import *

def generate_answer(state: AgentState) -> AgentState:
    """
    Generates an answer using RAG based on the chat history, context, and the enhanced query.
    Appends the answer as an AIMessage to the state.
    """
    print("Entering generate_answer")

    if "messages" not in state or not state["messages"]:
        raise ValueError("State must include 'messages' before generating an answer.")

    history = state["messages"]
    documents = state.get("documents", [])
    rephrased_query = state.get("enhanced_query", "")

    if llm is None:
        generation = "I'm sorry, but the AI service is not properly configured. Please check the API keys and try again later."
    else:
        try:
            response = rag_chain.invoke({
                "history": history,
                "context": documents,
                "question": rephrased_query
            })
            generation = response.content.strip()
        except Exception as e:
            # Fallback: if retrieval documents exist, summarize or return top snippets
            print(f"rag_chain.invoke failed: {e}")
            if documents:
                snippets = []
                for d in documents[:3]:
                    text = getattr(d, 'page_content', str(d))
                    snippets.append(text.strip()[:600])
                generation = (
                    "I couldn't generate a full answer using the LLM, but here are the most relevant snippets I found:\n\n" +
                    "\n\n---\n\n".join(snippets)
                )
            else:
                generation = "I couldn't generate an answer right now due to an internal error. Please try again later."

    state["messages"].append(AIMessage(content=generation))

    print(f"AyurWell: {generation}")
    return state


def off_topic_response(state: AgentState) -> AgentState:
    """
    Handles off-topic queries by returning a polite rejection message.
    """
    print("Entering off_topic_response")

    if "messages" not in state or state["messages"] is None:
        state["messages"] = []

    state["messages"].append(
        AIMessage(content="I'm sorry! I am a health assistant. Please ask related to health topics.")
    )
    return state


def greeting_response(state: AgentState) -> AgentState:
    """
    Handles greetings by setting proceed_to_generate to True, but returns an empty document list.
    """
    print("Entering greeting_response")
    state['proceed_to_generate'] = True
    state["documents"] = []
    return state
