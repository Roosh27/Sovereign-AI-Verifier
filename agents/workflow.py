from langgraph.graph import StateGraph, END
from .base import AgentState
from .validation import validation_agent
from .inference import inference_agent
from .decision import decision_agent
from .recommendation import recommendation_agent


def build_workflow():
    """
    Compiles the LangGraph workflow for the multi-agent system.
    
    Flow:
    1. Validator → Checks document consistency
        ├─ If REJECTED → END
        └─ If VALIDATED → Inferencer
    
    2. Inferencer → Runs ML model
        └─ Decider
    
    3. Decider → Makes final decision (ACCEPTED/SOFT DECLINE)
        ├─ If ACCEPTED → Advisor (recommendations)
        └─ If SOFT DECLINE → END
    
    4. Advisor → Suggests support pathway
        └─ END
    
    Returns:
        Compiled workflow graph
    """
    builder = StateGraph(AgentState)
    
    # ===== ADD NODES =====
    builder.add_node("validator", validation_agent)
    builder.add_node("inferencer", inference_agent)
    builder.add_node("decider", decision_agent)
    builder.add_node("advisor", recommendation_agent)
    
    # ===== SET ENTRY POINT =====
    builder.set_entry_point("validator")
    
    # ===== ADD CONDITIONAL EDGES =====
    
    # After Validator: REJECTED → END, VALIDATED → Inferencer
    builder.add_conditional_edges(
        "validator",
        lambda x: "end" if x.get("status") == "REJECTED" else "continue",
        {
            "end": END,
            "continue": "inferencer"
        }
    )
    
    # After Inferencer: Always go to Decider
    builder.add_edge("inferencer", "decider")
    
    # After Decider: ACCEPTED → Advisor, SOFT DECLINE → END
    builder.add_conditional_edges(
        "decider",
        lambda x: "rec" if x.get("status") == "ACCEPTED" else "end",
        {
            "rec": "advisor",
            "end": END
        }
    )
    
    # After Advisor: Always END
    builder.add_edge("advisor", END)
    
    # ===== COMPILE AND RETURN =====
    compiled_workflow = builder.compile()
    print("✅ Workflow compiled successfully")
    
    return compiled_workflow