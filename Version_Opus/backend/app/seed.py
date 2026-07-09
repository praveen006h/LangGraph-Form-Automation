from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Material, Sample, HCPProfile, ProductKnowledge


def seed_database():
    """Insert seed data if tables are empty."""
    db = SessionLocal()
    try:
        # Only seed if materials table is empty
        if db.query(Material).count() > 0:
            return

        # Seed materials
        materials = [
            Material(name="Product X Brochure", type="brochure", description="Detailed brochure for Product X with efficacy data"),
            Material(name="Product X Clinical Study", type="study", description="Phase III clinical study results for Product X"),
            Material(name="Product Y Whitepaper", type="whitepaper", description="Comprehensive whitepaper on Product Y mechanism of action"),
            Material(name="Product Z Presentation", type="presentation", description="Sales presentation deck for Product Z"),
            Material(name="Dosing Guide - Product X", type="brochure", description="Quick reference dosing guide for Product X"),
        ]
        db.add_all(materials)

        # Seed samples
        samples = [
            Sample(product_name="Product X", dosage="10mg", quantity_available=100),
            Sample(product_name="Product X", dosage="25mg", quantity_available=75),
            Sample(product_name="Product Y", dosage="50mg", quantity_available=50),
            Sample(product_name="Product Z", dosage="100mg", quantity_available=30),
        ]
        db.add_all(samples)

        # Seed HCP profiles
        hcps = [
            HCPProfile(first_name="Sarah", last_name="Smith", specialty="Cardiology", institution="City General Hospital"),
            HCPProfile(first_name="John", last_name="Williams", specialty="Oncology", institution="Memorial Cancer Center"),
            HCPProfile(first_name="Emily", last_name="Chen", specialty="Neurology", institution="University Medical Center"),
            HCPProfile(first_name="Michael", last_name="Johnson", specialty="Internal Medicine", institution="Community Health Clinic"),
            HCPProfile(first_name="Priya", last_name="Patel", specialty="Endocrinology", institution="Metro Healthcare System"),
        ]
        db.add_all(hcps)

        # Seed product knowledge
        products = [
            ProductKnowledge(
                product_name="Product X",
                description="A novel cardiovascular drug targeting hypertension.",
                indications="Hypertension, Heart Failure",
                contraindications="Pregnancy, Severe Renal Impairment",
                key_studies="HEART-1 Trial: 40% reduction in systolic BP. CARDIO-SAFE Study: Superior safety profile.",
                competitive_advantages="Once-daily dosing, fewer side effects than ACE inhibitors, proven CV outcomes benefit.",
            ),
            ProductKnowledge(
                product_name="Product Y",
                description="An advanced oncology therapy for solid tumors.",
                indications="Non-small cell lung cancer, Melanoma",
                contraindications="Autoimmune disorders, Organ transplant recipients",
                key_studies="TUMOR-HALT Trial: 35% improvement in PFS. ONCO-LIFE Study: Improved overall survival.",
                competitive_advantages="Oral formulation, combination-friendly, manageable toxicity profile.",
            ),
            ProductKnowledge(
                product_name="Product Z",
                description="A breakthrough neurological treatment for migraine prevention.",
                indications="Chronic Migraine, Episodic Migraine",
                contraindications="Cardiovascular disease, Hepatic impairment",
                key_studies="MIGRAINE-FREE Trial: 50% reduction in monthly migraine days. NEURO-SAFE Study: Minimal cognitive side effects.",
                competitive_advantages="Monthly injection, rapid onset of action, no drug interactions.",
            ),
        ]
        db.add_all(products)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()
