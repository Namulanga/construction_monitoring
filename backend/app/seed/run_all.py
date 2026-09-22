from app.database import SessionLocal
from app.seed import seed_equipment, seed_zones, seed_rules


def main():
    db = SessionLocal()
    try:
        seed_equipment.run(db)
        seed_zones.run(db)
        seed_rules.run(db)
    finally:
        db.close()
    print("seed: done")


if __name__ == "__main__":
    main()