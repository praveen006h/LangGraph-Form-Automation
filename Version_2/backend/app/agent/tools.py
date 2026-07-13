from langchain_core.tools import tool
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
import json


def create_tools(db: Session, form_state: dict):
    """Create tool instances with access to db and form_state."""

    @tool
    def log_interaction(
        hcp_name: str,
        interaction_date: Optional[str] = None,
        topics_discussed: Optional[str] = None,
        materials_shared: Optional[list[str]] = None,
        samples_distributed: Optional[list[str]] = None,
        sentiment: Optional[str] = None,
        outcomes: Optional[str] = None,
        follow_up_actions: Optional[str] = None,
    ) -> str:
        """Extracts structured entities from a natural language interaction summary and populates all form fields. Use this when the user describes a new HCP interaction."""
        from app.models import HCPProfile, Interaction, Material, InteractionMaterial, Sample, InteractionSample
        
        # Set defaults
        if interaction_date is None:
            interaction_date = date.today().isoformat()
        
        # Try to find or create the HCP
        hcp = None
        if hcp_name:
            # Search by last name or full name
            name_parts = hcp_name.replace("Dr.", "").replace("Dr ", "").strip().split()
            if name_parts:
                query = db.query(HCPProfile)
                for part in name_parts:
                    query = query.filter(
                        (HCPProfile.first_name.ilike(f"%{part}%")) |
                        (HCPProfile.last_name.ilike(f"%{part}%"))
                    )
                hcp = query.first()
        
        # Convert date string to date object
        parsed_date = date.today()
        if interaction_date:
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(interaction_date, "%Y-%m-%d").date()
            except ValueError:
                pass
            
        # Create the interaction record
        interaction = Interaction(
            hcp_id=hcp.id if hcp else None,
            interaction_date=parsed_date,
            topics_discussed=topics_discussed,
            sentiment=sentiment,
            outcomes=outcomes,
            follow_up_actions=follow_up_actions,
            status="draft",
        )
        db.add(interaction)
        db.flush()  # Get the ID
        
        # Process materials
        material_items = []
        if materials_shared:
            for mat_name in materials_shared:
                # Try to find existing material
                material = db.query(Material).filter(
                    Material.name.ilike(f"%{mat_name}%")
                ).first()
                if material:
                    im = InteractionMaterial(interaction_id=interaction.id, material_id=material.id)
                    db.add(im)
                    material_items.append({"id": material.id, "name": material.name})
                else:
                    # Create new material
                    new_mat = Material(name=mat_name, type="other")
                    db.add(new_mat)
                    db.flush()
                    im = InteractionMaterial(interaction_id=interaction.id, material_id=new_mat.id)
                    db.add(im)
                    material_items.append({"id": new_mat.id, "name": mat_name})
        
        # Process samples
        sample_items = []
        if samples_distributed:
            for sample_info in samples_distributed:
                if isinstance(sample_info, str):
                    sample_info = {"product_name": sample_info}
                elif isinstance(sample_info, dict):
                    pass
                else:
                    continue
                    
                product_name = sample_info.get("product_name", sample_info) if isinstance(sample_info, dict) else str(sample_info)
                sample = db.query(Sample).filter(
                    Sample.product_name.ilike(f"%{product_name}%")
                ).first()
                if sample:
                    qty = sample_info.get("quantity", 1) if isinstance(sample_info, dict) else 1
                    is_obj = InteractionSample(
                        interaction_id=interaction.id, 
                        sample_id=sample.id,
                        quantity_distributed=qty
                    )
                    db.add(is_obj)
                    sample_items.append({
                        "id": sample.id,
                        "product_name": sample.product_name,
                        "dosage": sample.dosage,
                        "quantity": qty
                    })
        
        db.commit()
        
        # Update form state
        form_state["interaction_id"] = interaction.id
        form_state["hcp_name"] = hcp_name
        form_state["interaction_date"] = parsed_date.strftime("%Y-%m-%d")
        form_state["topics_discussed"] = topics_discussed or ""
        form_state["materials_shared"] = material_items
        form_state["samples_distributed"] = sample_items
        form_state["sentiment"] = sentiment
        form_state["outcomes"] = outcomes or ""
        form_state["follow_up_actions"] = follow_up_actions or ""
        
        return json.dumps({
            "status": "success",
            "message": f"Interaction logged for {hcp_name}"
        })

    @tool
    def edit_interaction(
        hcp_name: Optional[str] = None,
        interaction_date: Optional[str] = None,
        topics_discussed: Optional[str] = None,
        materials_shared: Optional[list[str]] = None,
        samples_distributed: Optional[list[str]] = None,
        sentiment: Optional[str] = None,
        outcomes: Optional[str] = None,
        follow_up_actions: Optional[str] = None,
    ) -> str:
        """Modifies specific fields of the current interaction form. Use this when the user wants to correct or update specific details without changing everything else. Only updates fields that are explicitly provided."""
        from app.models import Interaction, Material, InteractionMaterial, Sample, InteractionSample, HCPProfile
        
        interaction_id = form_state.get("interaction_id")
        
        # Update only provided fields
        if hcp_name is not None:
            form_state["hcp_name"] = hcp_name
            if interaction_id:
                hcp = None
                name_parts = hcp_name.replace("Dr.", "").replace("Dr ", "").strip().split()
                if name_parts:
                    query = db.query(HCPProfile)
                    for part in name_parts:
                        query = query.filter(
                            (HCPProfile.first_name.ilike(f"%{part}%")) |
                            (HCPProfile.last_name.ilike(f"%{part}%"))
                        )
                    hcp = query.first()
                if hcp:
                    interaction = db.query(Interaction).get(interaction_id)
                    if interaction:
                        interaction.hcp_id = hcp.id
        
        if interaction_date is not None:
            try:
                from datetime import datetime
                parsed_date = datetime.strptime(interaction_date, "%Y-%m-%d").date()
                form_state["interaction_date"] = parsed_date.strftime("%Y-%m-%d")
                if interaction_id:
                    interaction = db.query(Interaction).get(interaction_id)
                    if interaction:
                        interaction.interaction_date = parsed_date
            except ValueError:
                pass
        
        if topics_discussed is not None:
            form_state["topics_discussed"] = topics_discussed
            if interaction_id:
                interaction = db.query(Interaction).get(interaction_id)
                if interaction:
                    interaction.topics_discussed = topics_discussed
        
        if sentiment is not None:
            form_state["sentiment"] = sentiment
            if interaction_id:
                interaction = db.query(Interaction).get(interaction_id)
                if interaction:
                    interaction.sentiment = sentiment
        
        if outcomes is not None:
            form_state["outcomes"] = outcomes
            if interaction_id:
                interaction = db.query(Interaction).get(interaction_id)
                if interaction:
                    interaction.outcomes = outcomes
        
        if follow_up_actions is not None:
            form_state["follow_up_actions"] = follow_up_actions
            if interaction_id:
                interaction = db.query(Interaction).get(interaction_id)
                if interaction:
                    interaction.follow_up_actions = follow_up_actions
        
        if materials_shared is not None:
            material_items = []
            for mat_name in materials_shared:
                material = db.query(Material).filter(Material.name.ilike(f"%{mat_name}%")).first()
                if material:
                    material_items.append({"id": material.id, "name": material.name})
                else:
                    new_mat = Material(name=mat_name, type="other")
                    db.add(new_mat)
                    db.flush()
                    material_items.append({"id": new_mat.id, "name": mat_name})
            form_state["materials_shared"] = material_items
        
        if samples_distributed is not None:
            sample_items = []
            for sample_info in samples_distributed:
                product_name = sample_info if isinstance(sample_info, str) else sample_info.get("product_name", "")
                sample = db.query(Sample).filter(Sample.product_name.ilike(f"%{product_name}%")).first()
                if sample:
                    sample_items.append({
                        "id": sample.id,
                        "product_name": sample.product_name,
                        "dosage": sample.dosage,
                        "quantity": 1
                    })
            form_state["samples_distributed"] = sample_items
        
        db.commit()
        
        changed_fields = [k for k, v in {
            "hcp_name": hcp_name, "interaction_date": interaction_date,
            "topics_discussed": topics_discussed, "materials_shared": materials_shared,
            "samples_distributed": samples_distributed, "sentiment": sentiment,
            "outcomes": outcomes, "follow_up_actions": follow_up_actions
        }.items() if v is not None]
        
        return json.dumps({
            "status": "success",
            "message": f"Updated fields: {', '.join(changed_fields)}"
        })

    @tool
    def suggest_follow_up(
        hcp_name: str,
        topics_discussed: Optional[str] = None,
        sentiment: Optional[str] = None,
        auto_populate: bool = False,
    ) -> str:
        """Analyzes the current interaction context and suggests contextually relevant follow-up actions. Use this when the user asks for follow-up suggestions or after logging an interaction."""
        suggestions = []
        
        if sentiment == "positive":
            suggestions.extend([
                f"Schedule a follow-up meeting with {hcp_name} within 2 weeks to maintain momentum",
                f"Send trial samples of discussed products to {hcp_name}'s office",
                f"Share additional clinical study data supporting the discussed topics",
            ])
        elif sentiment == "negative":
            suggestions.extend([
                f"Schedule an educational session with {hcp_name} to address concerns",
                f"Prepare a detailed FAQ document addressing {hcp_name}'s objections",
                f"Arrange a peer-to-peer discussion with a KOL in {hcp_name}'s specialty",
            ])
        else:  # neutral or None
            suggestions.extend([
                f"Follow up with {hcp_name} in 1 week with updated materials",
                f"Send a summary email of today's discussion to {hcp_name}",
                f"Schedule a product demonstration for {hcp_name}'s team",
            ])
        
        if topics_discussed:
            suggestions.append(f"Prepare a detailed brief on '{topics_discussed}' for the next meeting")
        
        suggestion_text = "\n".join([f"{i+1}. {s}" for i, s in enumerate(suggestions[:3])])
        
        if auto_populate:
            form_state["follow_up_actions"] = suggestion_text
            if form_state.get("interaction_id"):
                from app.models import Interaction
                interaction = db.query(Interaction).get(form_state["interaction_id"])
                if interaction:
                    interaction.follow_up_actions = suggestion_text
                    db.commit()
        
        return json.dumps({
            "status": "success",
            "suggestions": suggestion_text,
            "auto_populated": auto_populated
        })

    @tool
    def get_hcp_history(hcp_name: str) -> str:
        """Retrieves the interaction history and profile information for a specific HCP. Use this when the user asks about past interactions, an HCP's preferences, or needs context before a meeting."""
        from app.models import HCPProfile, Interaction
        
        # Search for HCP
        name_parts = hcp_name.replace("Dr.", "").replace("Dr ", "").strip().split()
        hcp = None
        if name_parts:
            query = db.query(HCPProfile)
            for part in name_parts:
                query = query.filter(
                    (HCPProfile.first_name.ilike(f"%{part}%")) |
                    (HCPProfile.last_name.ilike(f"%{part}%"))
                )
            hcp = query.first()
        
        if not hcp:
            return json.dumps({
                "status": "not_found",
                "message": f"No HCP profile found for '{hcp_name}'. Available HCPs can be searched by name."
            })
        
        # Get past interactions
        interactions = db.query(Interaction).filter(
            Interaction.hcp_id == hcp.id
        ).order_by(Interaction.interaction_date.desc()).limit(10).all()
        
        interaction_summaries = []
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        for inter in interactions:
            interaction_summaries.append({
                "date": str(inter.interaction_date),
                "topics": inter.topics_discussed or "N/A",
                "sentiment": inter.sentiment or "N/A",
                "outcomes": inter.outcomes or "N/A",
            })
            if inter.sentiment in sentiment_counts:
                sentiment_counts[inter.sentiment] += 1
        
        # Determine trend
        if interactions:
            most_common = max(sentiment_counts, key=sentiment_counts.get)
            trend = f"Mostly {most_common} ({sentiment_counts[most_common]}/{len(interactions)} interactions)"
        else:
            trend = "No interaction history"
        
        result = {
            "status": "success",
            "profile": {
                "name": f"Dr. {hcp.first_name} {hcp.last_name}",
                "specialty": hcp.specialty or "N/A",
                "institution": hcp.institution or "N/A",
                "email": hcp.email or "N/A",
                "phone": hcp.phone or "N/A",
            },
            "interaction_count": len(interactions),
            "sentiment_trend": trend,
            "recent_interactions": interaction_summaries,
        }
        return json.dumps(result)

    @tool
    def search_product_knowledge(query: str) -> str:
        """Searches the product knowledge base for information about pharmaceutical products. Use this when the user asks about product details, indications, competitive advantages, or needs talking points for an HCP meeting."""
        from app.models import ProductKnowledge
        
        products = db.query(ProductKnowledge).filter(
            (ProductKnowledge.product_name.ilike(f"%{query}%")) |
            (ProductKnowledge.description.ilike(f"%{query}%")) |
            (ProductKnowledge.indications.ilike(f"%{query}%"))
        ).filter(ProductKnowledge.is_active == True).all()
        
        if not products:
            return json.dumps({
                "status": "not_found",
                "message": f"No products found matching '{query}'."
            })
        
        results = []
        for prod in products:
            results.append({
                "product_name": prod.product_name,
                "description": prod.description,
                "indications": prod.indications,
                "contraindications": prod.contraindications,
                "key_studies": prod.key_studies,
                "competitive_advantages": prod.competitive_advantages,
            })
        
        return json.dumps({"status": "success", "products": results})

    return [log_interaction, edit_interaction, suggest_follow_up, get_hcp_history, search_product_knowledge]
