#!/usr/bin/env python3
"""
Script untuk verify dan test integration: Decision → Threat Assessment → KB Cards matching
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal
from app.models import Decision, ThreatLiteAssessment, KBCard


def verify_and_test():
    """Verify data integrity and test KB matching logic."""
    
    print("\n" + "="*80)
    print("🔍 VERIFICATION & TESTING: Decisions → Assessments → KB Cards")
    print("="*80 + "\n")
    
    db = SessionLocal()
    
    try:
        # ========== VERIFY DECISIONS ==========
        print("📋 DECISIONS IN DATABASE")
        print("-" * 80)
        
        decisions = db.query(Decision).all()
        print(f"Total: {len(decisions)}\n")
        
        for d in decisions:
            print(f"✓ ID {d.id}: {d.title}")
            print(f"  Context: {d.context[:80]}...")
            print(f"  Status: {d.status}")
        
        # ========== VERIFY THREAT ASSESSMENTS ==========
        print("\n\n⚠️  THREAT LITE ASSESSMENTS IN DATABASE")
        print("-" * 80)
        
        assessments = db.query(ThreatLiteAssessment).all()
        print(f"Total: {len(assessments)}\n")
        
        for a in assessments:
            decision = db.query(Decision).filter(Decision.id == a.decision_id).first()
            print(f"✓ Assessment ID {a.id} → Decision ID {a.decision_id}")
            if decision:
                print(f"  Decision: {decision.title}")
            print(f"  Threat Scenarios: {a.threat_scenarios[:100]}...")
        
        # ========== VERIFY KB CARDS ==========
        print("\n\n📚 KNOWLEDGE BASE CARDS IN DATABASE")
        print("-" * 80)
        
        cards = db.query(KBCard).all()
        print(f"Total: {len(cards)}\n")
        
        # Group by category
        by_category = {}
        for c in cards:
            if c.category not in by_category:
                by_category[c.category] = []
            by_category[c.category].append(c)
        
        for category in sorted(by_category.keys()):
            cards_in_cat = by_category[category]
            print(f"📦 {category} ({len(cards_in_cat)} cards)")
            for c in cards_in_cat:
                assessment_ids = c.threat_lite_assessment_ids or []
                print(f"   ✓ {c.id}: {c.title}")
                print(f"     Severity: {c.severity} | Assessments: {assessment_ids}")
        
        # ========== TEST KB MATCHING ==========
        print("\n\n🔗 KB MATCHING TEST")
        print("-" * 80)
        
        # Example: Match KB cards for Assessment 1
        assessment_id = 1
        assessment = db.query(ThreatLiteAssessment).filter(
            ThreatLiteAssessment.id == assessment_id
        ).first()
        
        if assessment:
            print(f"\nAssessment {assessment_id}:")
            print(f"  Threat Scenarios:\n{assessment.threat_scenarios[:200]}...\n")
            
            # Find KB cards that mention this assessment
            matched_cards = db.query(KBCard).filter(
                KBCard.threat_lite_assessment_ids.op('like')(f'%{assessment_id}%') 
                | (KBCard.threat_lite_assessment_ids == None)
            ).all()
            
            # Filter to only cards that list this assessment
            matched_cards = [
                c for c in cards 
                if c.threat_lite_assessment_ids and assessment_id in c.threat_lite_assessment_ids
            ]
            
            print(f"  Matched KB Cards: {len(matched_cards)}")
            for c in matched_cards[:5]:
                print(f"    ✓ {c.id}: {c.title}")
        
        # ========== DATA INTEGRITY CHECKS ==========
        print("\n\n✅ DATA INTEGRITY CHECKS")
        print("-" * 80)
        
        checks = {
            "✓ Decisions exist": len(decisions) > 0,
            "✓ Assessments exist": len(assessments) > 0,
            "✓ KB Cards exist": len(cards) > 0,
            "✓ All assessments have decisions": all(
                db.query(Decision).filter(Decision.id == a.decision_id).first() 
                for a in assessments
            ),
            "✓ KB cards have valid severity": all(
                c.severity in ['CRITICAL', 'HIGH', 'MEDIUM-HIGH', 'MEDIUM', 'LOW']
                for c in cards
            ),
            "✓ KB cards have category": all(c.category for c in cards),
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
        
        all_passed = all(checks.values())
        
        print("\n" + "="*80)
        if all_passed:
            print("✅ ALL INTEGRITY CHECKS PASSED")
        else:
            print("❌ SOME CHECKS FAILED")
        print("="*80 + "\n")
        
        return 0 if all_passed else 1
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    exit_code = verify_and_test()
    exit(exit_code)
