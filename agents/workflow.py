from langgraph.graph import StateGraph, END
from .base import AgentState
from .validation import validation_agent
from .inference import inference_agent
from .decision import decision_agent
from .recommendation import recommendation_agent
from utils.logger import setup_logger

# Setup logger for workflow
logger = setup_logger(f"Workflow_{__name__}")

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
    logger.info(" Building LangGraph workflow...")
    builder = StateGraph(AgentState)
    
    # Wrapper to merge agent outputs into state
    def merge_state(agent_func):
        def wrapper(state):
            result = agent_func(state)
            return {**state, **result}  # Merge result into state
        return wrapper
    
    logger.info(" Adding workflow nodes...")

    # ===== ADD NODES =====
    builder.add_node("validator", merge_state(validation_agent))
    builder.add_node("inferencer", merge_state(inference_agent))
    builder.add_node("decider", merge_state(decision_agent))
    builder.add_node("advisor", merge_state(recommendation_agent))
    
    # ===== SET ENTRY POINT =====
    builder.set_entry_point("validator")
    
    # ===== ADD CONDITIONAL EDGES =====
    logger.info(" Adding workflow edges...")

    # After Validator: REJECTED → END, VALIDATED → Inferencer
    logger.debug(" Adding validator conditional edge")
    builder.add_conditional_edges(
        "validator",
        lambda x: "end" if x.get("status") == "REJECTED" else "continue",
        {
            "end": END,
            "continue": "inferencer"
        }
    )
    
    # After Inferencer: Always go to Decider
    logger.debug(" Adding inferencer → decider edge")
    builder.add_edge("inferencer", "decider")
    
    # After Decider: ACCEPTED → Advisor, SOFT DECLINE → END
    logger.debug(" Adding decider conditional edge")
    builder.add_conditional_edges(
        "decider",
        lambda x: "rec" if x.get("status") == "ACCEPTED" else "end",
        {
            "rec": "advisor",
            "end": END
        }
    )
    
    # After Advisor: Always END
    logger.debug(" Adding advisor → END edge")
    builder.add_edge("advisor", END)
    
    # ===== COMPILE AND RETURN =====
    logger.info(" Compiling workflow graph...")
    compiled_workflow = builder.compile()
    logger.info(" Workflow compiled successfully!")
    print("✅ Workflow compiled successfully")
    
    return compiled_workflow