import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.db.session import SessionLocal
from app.models.models import University, RankTier, CompetitionLevel

def seed_universities():
    db = SessionLocal()
    try:
        # Extended list of universities
        universities_data = [
            # Original 8 (Ensure they are preserved or re-checked)
            University(name="Global Tech Institute", country="USA", annual_cost=55000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="North State University", country="USA", annual_cost=30000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
            University(name="City College of Engineering", country="USA", annual_cost=20000, ranking_tier=RankTier.LOW, competition_level=CompetitionLevel.LOW),
            University(name="Royal Science Academy", country="UK", annual_cost=40000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="Central London Poly", country="UK", annual_cost=25000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
            University(name="Berlin Tech Hoch", country="Germany", annual_cost=5000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
            University(name="Munich Applied Sciences", country="Germany", annual_cost=2000, ranking_tier=RankTier.LOW, competition_level=CompetitionLevel.LOW),
            University(name="Future Systems Univ", country="Canada", annual_cost=35000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
            
            # 15 NEW Universities
            University(name="Massachusetts Inst. of Tech (MIT)", country="USA", annual_cost=60000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="Stanford University", country="USA", annual_cost=62000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="Harvard University", country="USA", annual_cost=61000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="University of Oxford", country="UK", annual_cost=45000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="University of Cambridge", country="UK", annual_cost=46000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="ETH Zurich", country="Switzerland", annual_cost=2000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="EPFL", country="Switzerland", annual_cost=2000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="National Univ. of Singapore (NUS)", country="Singapore", annual_cost=30000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="Nanyang Tech Univ (NTU)", country="Singapore", annual_cost=28000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="University of Toronto", country="Canada", annual_cost=45000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.MEDIUM),
            University(name="University of British Columbia", country="Canada", annual_cost=40000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
            University(name="University of Melbourne", country="Australia", annual_cost=38000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.MEDIUM),
            University(name="University of Sydney", country="Australia", annual_cost=37000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
            University(name="Tsinghua University", country="China", annual_cost=10000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="University of Tokyo", country="Japan", annual_cost=12000, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="Technical Univ. of Munich (TUM)", country="Germany", annual_cost=1500, ranking_tier=RankTier.HIGH, competition_level=CompetitionLevel.HIGH),
            University(name="University of Amsterdam", country="Netherlands", annual_cost=18000, ranking_tier=RankTier.MID, competition_level=CompetitionLevel.MEDIUM),
        ]

        count = 0
        for uni in universities_data:
            exists = db.query(University).filter(University.name == uni.name).first()
            if not exists:
                db.add(uni)
                count += 1
        
        db.commit()
        print(f"Seeding Complete. Added {count} new universities.")
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_universities()
