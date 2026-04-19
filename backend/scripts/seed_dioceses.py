"""Seed US Dioceses and Parishes."""

import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import Session

from app.db.session import Base, SessionLocal, engine
from app.models.diocese import Diocese
from app.models.parish import Parish

# Force table creation if Alembic hasn't been run locally
Base.metadata.create_all(bind=engine)

DIOCESES_DATA = [
    {
        "name": "Archdiocese of San Antonio",
        "state": "TX",
        "parishes": [
            {
                "name": "San Fernando Cathedral",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78205",
                "address": "115 Main Plaza",
            },
            {
                "name": "St. Mark the Evangelist",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78232",
                "address": "1602 Thousand Oaks Dr",
            },
            {
                "name": "Holy Trinity",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78258",
                "address": "20523 Huebner Rd",
            },
            {
                "name": "St. Matthew",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78230",
                "address": "10703 Wurzbach Rd",
            },
            {
                "name": "Our Lady of Guadalupe",
                "city": "Helotes",
                "state": "TX",
                "zip": "78023",
                "address": "13715 Riggs Rd",
            },
            {
                "name": "St. Peter Prince of the Apostles",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78209",
                "address": "111 Barilla Pl",
            },
            {
                "name": "St. Joseph (Downtown)",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78205",
                "address": "623 E Commerce St",
            },
            {
                "name": "St. Luke",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78229",
                "address": "4603 Manitou Dr",
            },
            {
                "name": "St. Rose of Lima",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78245",
                "address": "9883 Marbach Rd",
            },
            {
                "name": "St. Anthony de Padua",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78209",
                "address": "102 Lorenz Rd",
            },
            {
                "name": "Blessed Sacrament",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78216",
                "address": "600 Oblate Dr",
            },
            {
                "name": "Our Lady of the Atonement",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78255",
                "address": "15415 Red Robin Rd",
            },
            {
                "name": "St. Pius X",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78209",
                "address": "3303 Urban Crest Dr",
            },
        ],
    },
    {
        "name": "Diocese of Dallas",
        "state": "TX",
        "parishes": [
            {
                "name": "Cathedral Shrine of the Virgin of Guadalupe",
                "city": "Dallas",
                "state": "TX",
                "zip": "75201",
                "address": "2215 Ross Ave",
            },
            {
                "name": "St. Thomas Aquinas",
                "city": "Dallas",
                "state": "TX",
                "zip": "75214",
                "address": "6306 Kenwood Ave",
            },
            {
                "name": "Christ the King",
                "city": "Dallas",
                "state": "TX",
                "zip": "75225",
                "address": "8017 Preston Rd",
            },
            {
                "name": "St. Monica",
                "city": "Dallas",
                "state": "TX",
                "zip": "75229",
                "address": "9933 Midway Rd",
            },
            {
                "name": "St. Rita",
                "city": "Dallas",
                "state": "TX",
                "zip": "75244",
                "address": "12521 Inwood Rd",
            },
            {
                "name": "Mary Immaculate",
                "city": "Farmers Branch",
                "state": "TX",
                "zip": "75234",
                "address": "2800 Valwood Pkwy",
            },
            {
                "name": "All Saints",
                "city": "Dallas",
                "state": "TX",
                "zip": "75248",
                "address": "5231 Meadowcreek Dr",
            },
            {
                "name": "St. Mark the Evangelist",
                "city": "Plano",
                "state": "TX",
                "zip": "75075",
                "address": "1201 Alma Dr",
            },
            {
                "name": "Prince of Peace",
                "city": "Plano",
                "state": "TX",
                "zip": "75093",
                "address": "5100 W Plano Pkwy",
            },
            {
                "name": "St. Elizabeth Ann Seton",
                "city": "Plano",
                "state": "TX",
                "zip": "75025",
                "address": "2700 W Spring Creek Pkwy",
            },
            {
                "name": "Holy Trinity",
                "city": "Dallas",
                "state": "TX",
                "zip": "75219",
                "address": "3811 Oak Lawn Ave",
            },
        ],
    },
    {
        "name": "Diocese of Baton Rouge",
        "state": "LA",
        "parishes": [
            {
                "name": "St. Joseph Cathedral",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70802",
                "address": "412 North St",
            },
            {
                "name": "St. Aloysius",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70808",
                "address": "2025 Stuart Ave",
            },
            {
                "name": "St. Jude the Apostle",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70820",
                "address": "9150 Highland Rd",
            },
            {
                "name": "Our Lady of Mercy",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70806",
                "address": "445 Marquette Ave",
            },
            {
                "name": "Sacred Heart of Jesus",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70802",
                "address": "2250 Main St",
            },
            {
                "name": "St. George",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70809",
                "address": "7808 St George Dr",
            },
            {
                "name": "St. Thomas More",
                "city": "Baton Rouge",
                "state": "LA",
                "zip": "70815",
                "address": "11441 Goodwood Blvd",
            },
            {
                "name": "St. John the Evangelist",
                "city": "Prairieville",
                "state": "LA",
                "zip": "70769",
                "address": "15208 Hwy 73",
            },
        ],
    },
]


def seed_db():
    db: Session = SessionLocal()
    try:
        # Create Dioceses and Parishes
        for d_data in DIOCESES_DATA:
            diocese = db.query(Diocese).filter(Diocese.name == d_data["name"]).first()
            if not diocese:
                diocese = Diocese(name=d_data["name"], state=d_data["state"])
                db.add(diocese)
                db.flush()

            for p_data in d_data["parishes"]:
                parish = (
                    db.query(Parish)
                    .filter(Parish.name == p_data["name"], Parish.diocese_id == diocese.id)
                    .first()
                )
                if not parish:
                    parish = Parish(
                        name=p_data["name"],
                        diocese_id=diocese.id,
                        address_line1=p_data["address"],
                        city=p_data["city"],
                        state=p_data["state"],
                        zip_code=p_data["zip"],
                    )
                    db.add(parish)

        db.commit()
        print("Database seeding completed.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
