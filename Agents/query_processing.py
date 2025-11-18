
from .state import AgentState
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from chains.rag_chain import *


class GradeQuestion(BaseModel):
    score: str = Field(
        description="Question is about the specified topics? If yes -> 'Yes' if not -> 'No'"
    )

def query_enhancer(state: AgentState):
    print(f"Entering question_rewriter with following state: {state}")

    # Reset state variables except for 'question' and 'messages'
    state["documents"] = []
    state["on_topic"] = ""
    state["enhanced_query"] = ""
    state["proceed_to_generate"] = False
    state["rephrase_count"] = 0

    if "messages" not in state or state["messages"] is None:
        state["messages"] = []

    if state["question"] not in state["messages"]:
        state["messages"].append(state["question"])

    if len(state["messages"]) > 1:
        conversation = state["messages"][:-1]
        current_question = state["question"].content
        messages = [
            SystemMessage(
                content="You are a helpful assistant that rephrases the user's question to be a standalone question optimized for retrieval."
            )
        ]
        messages.extend(conversation)
        messages.append(HumanMessage(content=current_question))
        rephrase_prompt = ChatPromptTemplate.from_messages(messages)
        prompt = rephrase_prompt.format()
        try:
            response = llm.invoke(prompt)
            better_question = response.content.strip()
        except Exception as e:
            # Fallback: if the LLM fails, keep the original question as-is
            print(f"query_enhancer: LLM invoke failed: {e}")
            better_question = state["question"].content
        # print(f"query_enhancer: Rephrased question: {better_question}")
        state["enhanced_query"] = better_question
    else:
        state["enhanced_query"] = state["question"].content
    return state

def query_classifier(state: AgentState):
    print("Entering question_classifier")
    system_message = SystemMessage(
        content="""You are a classifier that determines whether a user's question is about the following health-related topics:
    
    0. health-related topics
    1. Symptoms and causes of diseases (e.g., diabetes, hypertension, etc.)
    2. Treatment options and medications
    3. Preventive healthcare (e.g., vaccinations, screenings)
    4. Diet and nutrition advice
    5. Exercise and fitness recommendations
    6. Mental health and well-being
    7. General healthcare information or healthy lifestyle tips
    8. Health technology and innovations (e.g., telemedicine, health apps)
    
    If the question IS about any of these topics, respond with 'Yes'.
    If the query is about Greetings and salutations and Asking about you and your concern(e.g., "Hello", "Hi", "Good morning" etc) respond with 'greeting'. Otherwise, respond with 'No'.
    
    """
    )


    human_message = HumanMessage(
        content=f"User question: {state['enhanced_query']}\n\n"
    )
    grade_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    prompt = grade_prompt.format_messages()
    structured_llm = llm.with_structured_output(GradeQuestion)
    try:
        result = structured_llm.invoke(prompt)
        state["on_topic"] = result.score.strip()
    except Exception as e:
        # Heuristic fallback classifier when LLM is unavailable
        print(f"query_classifier: structured LLM invoke failed: {e}")
        q = state.get("enhanced_query", "").lower()
        greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
        health_keywords = [
            "symptom",
            "symptoms",
            "treatment",
            "treat",
            "diabetes",
            "hypertension",
            "blood pressure",
            "fever",
            "cough",
            "pain",
            "vaccine",
            "nutrition",
            "diet",
            "exercise",
            "mental",
            "health",
        ]
        if any(g in q for g in greetings):
            state["on_topic"] = "greeting"
        elif any(k in q for k in health_keywords):
            state["on_topic"] = "Yes"
        else:
            state["on_topic"] = "No"
    print(f"question_classifier: on_topic = {state['on_topic']}")
    return state

def refine_query(state: AgentState):
    print("Entering refine_question")
    rephrase_count = state.get("rephrase_count", 0)
    if rephrase_count >= 2:
        # print("Maximum rephrase attempts reached")
        return state
    question_to_refine = state["enhanced_query"]
    system_message = SystemMessage(
        content="""You are a helpful assistant that slightly refines the user's question to improve retrieval results.
Provide a slightly adjusted version of the question."""
    )
    human_message = HumanMessage(
        content=f"Original question: {question_to_refine}\n\nProvide a slightly refined question."
    )
    refine_prompt = ChatPromptTemplate.from_messages([system_message, human_message])
    prompt = refine_prompt.format()
    try:
        response = llm.invoke(prompt)
        refined_question = response.content.strip()
        print(f"refine_question: Refined question: {refined_question}")
        state["enhanced_query"] = refined_question
    except Exception as e:
        # If LLM fails, keep the previous enhanced query unchanged
        print(f"refine_question: LLM invoke failed: {e}")
        # leave enhanced_query as-is
    state["rephrase_count"] = rephrase_count + 1
    return state