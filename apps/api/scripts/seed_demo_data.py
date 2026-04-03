import asyncio
import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import delete
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.engines.graph import build_relationships
from app.engines.intent import detect_buyer_intent
from app.engines.opportunities import generate_opportunities
from app.engines.scoring import compute_growth_score, compute_health_score, compute_opportunity_score
from app.engines.signals import generate_signals
from app.models.entities import Company, Opportunity, Relationship, Signal, User
from app.services.embeddings import build_company_embedding_text, format_vector_literal, generate_embedding
from app.services.tenancy import ensure_default_workspace

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


DEMO_COMPANIES = [
    {
        "name": "Bengaluru Growth Labs",
        "slug": "bengaluru-growth-labs",
        "website": "https://bengalurugrowthlabs.example.com",
        "industry": "SaaS",
        "city": "Bengaluru",
        "region": "Karnataka",
        "country": "India",
        "rating": 4.4,
        "reviews_count": 136,
        "description": "Fast-growing RevOps software company expanding across APAC.",
        "enrichment": {
            "emails": ["hello@bglabs.example.com"],
            "phones": ["+91 90000 11111"],
            "social_profiles": ["linkedin.com/bglabs"],
            "technology_stack": ["hubspot", "aws", "nextjs"],
            "crm": True,
            "automation_tools": ["zapier"],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 28, "expanding_regions": ["APAC", "MEA"]},
    },
    {
        "name": "Mumbai Dining Collective",
        "slug": "mumbai-dining-collective",
        "website": None,
        "industry": "Hospitality",
        "city": "Mumbai",
        "region": "Maharashtra",
        "country": "India",
        "rating": 3.2,
        "reviews_count": 412,
        "description": "Multi-location hospitality group with weak digital presence and strong footfall.",
        "enrichment": {
            "emails": ["ops@mdc.example.com"],
            "phones": ["+91 98888 22222"],
            "social_profiles": ["instagram.com/mdc"],
            "technology_stack": ["wordpress"],
            "crm": False,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": False, "traffic_growth": 11, "expanding_regions": []},
    },
    {
        "name": "Pune FactoryOS Supply",
        "slug": "pune-factoryos-supply",
        "website": "https://factoryos.example.com",
        "industry": "Manufacturing",
        "city": "Pune",
        "region": "Maharashtra",
        "country": "India",
        "rating": 4.0,
        "reviews_count": 84,
        "description": "Industrial operations supplier modernizing procurement and field workflows.",
        "enrichment": {
            "emails": ["sales@factoryos.example.com"],
            "phones": ["+91 97777 33333"],
            "social_profiles": ["linkedin.com/factoryos"],
            "technology_stack": ["salesforce", "sap"],
            "crm": True,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 17, "expanding_regions": ["India West"]},
    },
    {
        "name": "Delhi TalentPulse Systems",
        "slug": "delhi-talentpulse-systems",
        "website": "https://talentpulse.example.com",
        "industry": "HR Tech",
        "city": "Delhi NCR",
        "region": "Delhi",
        "country": "India",
        "rating": 4.6,
        "reviews_count": 92,
        "description": "Talent intelligence platform expanding enterprise hiring analytics across India and SEA.",
        "enrichment": {
            "emails": ["team@talentpulse.example.com"],
            "phones": ["+91 95555 44444"],
            "social_profiles": ["linkedin.com/talentpulse"],
            "technology_stack": ["hubspot", "segment", "snowflake"],
            "crm": True,
            "automation_tools": ["zapier"],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 33, "expanding_regions": ["India North", "SEA"]},
    },
    {
        "name": "Hyderabad PatientFlow Cloud",
        "slug": "hyderabad-patientflow-cloud",
        "website": "https://patientflow.example.com",
        "industry": "Healthcare",
        "city": "Hyderabad",
        "region": "Telangana",
        "country": "India",
        "rating": 4.2,
        "reviews_count": 75,
        "description": "Healthcare workflow and patient engagement platform integrating clinics and hospital groups.",
        "enrichment": {
            "emails": ["connect@patientflow.example.com"],
            "phones": ["+91 94444 55555"],
            "social_profiles": ["linkedin.com/patientflow"],
            "technology_stack": ["salesforce", "aws", "twilio"],
            "crm": True,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 22, "expanding_regions": ["India South"]},
    },
    {
        "name": "Chennai PortOps Grid",
        "slug": "chennai-portops-grid",
        "website": "https://portops.example.com",
        "industry": "Logistics",
        "city": "Chennai",
        "region": "Tamil Nadu",
        "country": "India",
        "rating": 3.9,
        "reviews_count": 61,
        "description": "Supply-chain coordination platform modernizing dispatch, fleet operations, and terminal workflows.",
        "enrichment": {
            "emails": ["ops@portops.example.com"],
            "phones": ["+91 93333 66666"],
            "social_profiles": ["linkedin.com/portops"],
            "technology_stack": ["microsoft dynamics", "azure"],
            "crm": False,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": False, "traffic_growth": 14, "expanding_regions": ["India South", "Middle East"]},
    },
    {
        "name": "Jaipur HomeCraft Commerce",
        "slug": "jaipur-homecraft-commerce",
        "website": "https://homecraft.example.com",
        "industry": "Retail",
        "city": "Jaipur",
        "region": "Rajasthan",
        "country": "India",
        "rating": 3.5,
        "reviews_count": 248,
        "description": "Multichannel retail brand with high demand and fragmented CRM and ecommerce operations.",
        "enrichment": {
            "emails": ["care@homecraft.example.com"],
            "phones": ["+91 92222 77777"],
            "social_profiles": ["instagram.com/homecraft", "facebook.com/homecraft"],
            "technology_stack": ["shopify", "klaviyo"],
            "crm": False,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 19, "expanding_regions": ["India North", "UAE"]},
    },
    {
        "name": "Kochi Marine Insight",
        "slug": "kochi-marine-insight",
        "website": "https://marineinsight.example.com",
        "industry": "Maritime",
        "city": "Kochi",
        "region": "Kerala",
        "country": "India",
        "rating": 4.1,
        "reviews_count": 43,
        "description": "Maritime analytics company digitizing vessel maintenance and coastal operations reporting.",
        "enrichment": {
            "emails": ["hello@marineinsight.example.com"],
            "phones": ["+91 91111 88888"],
            "social_profiles": ["linkedin.com/marineinsight"],
            "technology_stack": ["powerbi", "azure", "hubspot"],
            "crm": True,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": False, "traffic_growth": 16, "expanding_regions": ["India South"]},
    },
    {
        "name": "Ahmedabad Process Forge",
        "slug": "ahmedabad-process-forge",
        "website": "https://processforge.example.com",
        "industry": "Manufacturing",
        "city": "Ahmedabad",
        "region": "Gujarat",
        "country": "India",
        "rating": 4.3,
        "reviews_count": 109,
        "description": "Industrial operations software vendor connecting field service, ERP, and production analytics.",
        "enrichment": {
            "emails": ["sales@processforge.example.com"],
            "phones": ["+91 90000 99999"],
            "social_profiles": ["linkedin.com/processforge"],
            "technology_stack": ["sap", "salesforce", "aws"],
            "crm": True,
            "automation_tools": [],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 21, "expanding_regions": ["India West", "Africa"]},
    },
    {
        "name": "Gurugram RevPilot AI",
        "slug": "gurugram-revpilot-ai",
        "website": "https://revpilot.example.com",
        "industry": "SaaS",
        "city": "Gurugram",
        "region": "Haryana",
        "country": "India",
        "rating": 4.7,
        "reviews_count": 158,
        "description": "Revenue intelligence startup building AI workflow orchestration for GTM operators.",
        "enrichment": {
            "emails": ["growth@revpilot.example.com"],
            "phones": ["+91 98989 12345"],
            "social_profiles": ["linkedin.com/revpilot", "x.com/revpilot"],
            "technology_stack": ["hubspot", "salesforce", "openai", "vercel"],
            "crm": True,
            "automation_tools": ["zapier"],
        },
        "metadata": {"is_hiring": True, "traffic_growth": 41, "expanding_regions": ["India North", "US"]},
    },
]


async def main():
    async with SessionLocal() as session:
        await session.execute(delete(Relationship))
        await session.execute(delete(Signal))
        await session.execute(delete(Opportunity))
        await session.execute(delete(Company))
        await session.execute(delete(User).where(User.email == "admin@atlasbi.local"))

        existing_user = User(
            email="admin@atlasbi.local",
            full_name="AtlasBI Admin",
            role="admin",
            hashed_password=hash_password("AtlasBI-Admin-2026"),
            is_active=True,
        )
        session.add(existing_user)

        created_companies = []
        for payload in DEMO_COMPANIES:
            payload["health_score"] = compute_health_score(payload)
            payload["growth_score"] = compute_growth_score(payload)
            payload["opportunity_score"] = compute_opportunity_score(payload)
            payload["ai_summary"] = (
                f"{payload['name']} shows {payload['industry']} demand in {payload['city']} with "
                f"an intent score of {detect_buyer_intent(payload)['intent_score']}."
            )
            payload["company_metadata"] = payload.pop("metadata")
            company = Company(**payload)
            session.add(company)
            await session.flush()
            created_companies.append(company)
            embedding = format_vector_literal(generate_embedding(build_company_embedding_text({**payload, "metadata": payload["company_metadata"]})))
            await session.execute(
                text("update companies set embedding = cast(:embedding as vector) where id = :company_id"),
                {"embedding": embedding, "company_id": company.id},
            )

            for signal in generate_signals(
                {
                    **payload,
                    "metadata": company.company_metadata,
                }
            ):
                session.add(Signal(id=uuid4(), company_id=company.id, **signal))

            for opportunity in generate_opportunities(
                {
                    **payload,
                    "metadata": company.company_metadata,
                }
            ):
                session.add(Opportunity(id=uuid4(), company_id=company.id, **opportunity))

        for company in created_companies:
            for relation in build_relationships(
                {
                    "industry": company.industry,
                    "enrichment": company.enrichment,
                }
            ):
                session.add(
                    Relationship(
                        id=uuid4(),
                        source_company_id=company.id,
                        relationship_type=relation["relationship_type"],
                        weight=relation["weight"],
                        relationship_metadata=relation["metadata"],
                    )
                )

        await session.commit()
        await ensure_default_workspace(session, existing_user)
        print(f"Seeded {len(created_companies)} companies and bootstrap admin credentials.")


if __name__ == "__main__":
    asyncio.run(main())
