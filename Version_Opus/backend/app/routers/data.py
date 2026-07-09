from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Material, Sample, HCPProfile, Interaction
from app.schemas import FormState
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["data"])


class MaterialResponse(BaseModel):
    id: int
    name: str
    type: str
    description: str | None = None


class SampleResponse(BaseModel):
    id: int
    product_name: str
    dosage: str | None = None
    quantity_available: int


class HCPProfileResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    specialty: str | None = None
    institution: str | None = None


@router.get("/materials", response_model=list[MaterialResponse])
async def get_materials(db: Session = Depends(get_db)):
    materials = db.query(Material).filter(Material.is_active == True).all()
    return [MaterialResponse(id=m.id, name=m.name, type=m.type, description=m.description) for m in materials]


@router.get("/samples", response_model=list[SampleResponse])
async def get_samples(db: Session = Depends(get_db)):
    samples = db.query(Sample).filter(Sample.is_active == True).all()
    return [SampleResponse(id=s.id, product_name=s.product_name, dosage=s.dosage, quantity_available=s.quantity_available) for s in samples]


@router.get("/hcp-profiles", response_model=list[HCPProfileResponse])
async def get_hcp_profiles(db: Session = Depends(get_db)):
    hcps = db.query(HCPProfile).all()
    return [HCPProfileResponse(id=h.id, first_name=h.first_name, last_name=h.last_name, specialty=h.specialty, institution=h.institution) for h in hcps]


@router.post("/interactions/submit")
async def submit_interaction(form_state: FormState, db: Session = Depends(get_db)):
    if form_state.interaction_id:
        interaction = db.query(Interaction).get(form_state.interaction_id)
        if interaction:
            interaction.status = "submitted"
            db.commit()
            return {"success": True, "interaction_id": interaction.id, "message": "Interaction submitted successfully"}
    return {"success": False, "message": "No interaction found to submit"}
