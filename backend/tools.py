from langchain_core.tools import tool
from typing import List, Optional

@tool
def log_interaction(
    hcp_name: Optional[str] = None,
    date: Optional[str] = None,
    sentiment: Optional[str] = None,
    topics: Optional[str] = None,
    materials_shared: Optional[List[str]] = None,
    samples_distributed: Optional[List[str]] = None
) -> dict:
    """
    Extracts entities from a new interaction summary and populates the form state.
    Use this when the user describes a new interaction they just had with an HCP.
    """
    # Defensive programming
    updates = {}
    if hcp_name is not None: updates["hcpName"] = str(hcp_name)
    if date is not None: updates["date"] = str(date)
    if sentiment is not None: updates["sentiment"] = str(sentiment)
    if topics is not None: updates["topics"] = str(topics)
    if materials_shared is not None: 
        updates["materials"] = materials_shared if isinstance(materials_shared, list) else []
    if samples_distributed is not None: 
        updates["samples"] = samples_distributed if isinstance(samples_distributed, list) else []

    return {
        "action": "update_form",
        "updates": updates,
        "message": "Form populated successfully."
    }

@tool
def edit_interaction(field_to_update: Optional[str] = None, new_value: Optional[str] = None) -> dict:
    """
    Modifies specific fields in the form based on user corrections.
    Valid fields: hcpName, date, sentiment, topics, materials, samples, outcomes, followUp.
    """
    if not field_to_update:
        return {"action": "none", "message": "No field provided to update."}
        
    return {
        "action": "edit_field",
        "field": str(field_to_update),
        "value": new_value if new_value is not None else "",
        "message": f"Updated {field_to_update} to {new_value}."
    }

@tool
def suggest_follow_up(topics_discussed: Optional[str] = None, sentiment: Optional[str] = None) -> str:
    """
    Analyzes the topics discussed and sentiment to suggest tactical next steps.
    Returns a string of suggested follow up actions.
    """
    safe_sentiment = str(sentiment).lower() if sentiment else ""
    
    if "negative" in safe_sentiment:
        return "Suggestion: Schedule a follow-up call next week to address concerns. Send additional safety data."
    elif "positive" in safe_sentiment:
        return "Suggestion: Share advanced clinical trial data. Invite to upcoming webinar."
    else:
        return "Suggestion: Send standard follow-up email with product summary."

@tool
def get_hcp_history(hcp_name: Optional[str] = None) -> str:
    """
    Retrieves past interaction summaries for a mentioned HCP.
    Use this to get context about the HCP before logging the new interaction.
    """
    safe_name = str(hcp_name) if hcp_name else ""
    mock_history = {
        "Dr. Smith": "Last met on Oct 10th. Discussed Product Y. Sentiment was neutral.",
        "Dr. John": "Frequent prescriber. Highly interested in Product X efficacy."
    }
    
    for key, value in mock_history.items():
        if key.lower() in safe_name.lower():
            return value
            
    return "No previous history found for this HCP."

@tool
def search_knowledge_base(search_query: Optional[str] = None) -> str:
    """
    Searches clinical guidelines or product details if the rep asks a question during logging.
    """
    safe_query = str(search_query).lower() if search_query else ""
    if "product x" in safe_query:
        return "Product X has shown a 25% increase in efficacy in Phase 3 trials compared to standard of care."
    return "Knowledge base search returned no specific results for this query."
