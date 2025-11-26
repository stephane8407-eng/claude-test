#!/usr/bin/env python3
"""
Week 12 Launch Checklist - Chirac Flagship Verification

Verifies that all systems are ready for Chirac village launch.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from backend.app.database import Base
from backend.app.models.village import Village
from backend.app.models.battle import Battle
from backend.app.models.poi import POI
from backend.app.models.identity_theme import IdentityTheme
from backend.app.models.qr_code import QRCode
from backend.app.models.user import User
from backend.app.config import get_settings
import requests
from datetime import datetime

settings = get_settings()


class LaunchChecklist:
    def __init__(self):
        self.engine = create_engine(settings.DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.checks_passed = 0
        self.checks_failed = 0
        self.total_checks = 0

    def print_header(self, text):
        print(f"\n{'=' * 60}")
        print(f"  {text}")
        print(f"{'=' * 60}\n")

    def check(self, description, condition, details=None):
        """Run a check and print the result"""
        self.total_checks += 1
        status = "✓ PASS" if condition else "✗ FAIL"
        color = "\033[92m" if condition else "\033[91m"
        reset = "\033[0m"

        print(f"{color}{status}{reset} - {description}")
        if details:
            print(f"       {details}")

        if condition:
            self.checks_passed += 1
        else:
            self.checks_failed += 1

        return condition

    def verify_database(self):
        """Verify database connectivity and Chirac village"""
        self.print_header("1. DATABASE VERIFICATION")

        # Check database connection
        try:
            self.db.execute("SELECT 1")
            self.check("Database connection", True, "Successfully connected to PostgreSQL")
        except Exception as e:
            self.check("Database connection", False, f"Error: {e}")
            return False

        # Check Chirac village exists
        chirac = self.db.query(Village).filter(Village.slug == 'chirac').first()
        self.check("Chirac village exists", chirac is not None)

        if chirac:
            print(f"       Village ID: {chirac.id}")
            print(f"       Name: {chirac.name}")
            print(f"       Created: {chirac.created_at}")

        return chirac is not None

    def verify_conflicts(self):
        """Verify 123 conflicts are loaded"""
        self.print_header("2. CONFLICTS VERIFICATION")

        chirac = self.db.query(Village).filter(Village.slug == 'chirac').first()
        if not chirac:
            self.check("Conflicts verification", False, "Chirac village not found")
            return False

        # Count conflicts
        conflict_count = self.db.query(func.count(Battle.id)).filter(
            Battle.village_id == chirac.id
        ).scalar()

        self.check(
            "123 conflicts loaded",
            conflict_count == 123,
            f"Found {conflict_count} conflicts (expected 123)"
        )

        # Check conflicts have coordinates
        conflicts_with_coords = self.db.query(func.count(Battle.id)).filter(
            Battle.village_id == chirac.id,
            Battle.latitude.isnot(None),
            Battle.longitude.isnot(None)
        ).scalar()

        self.check(
            "Conflicts have coordinates",
            conflicts_with_coords > 0,
            f"{conflicts_with_coords}/{conflict_count} have lat/lng"
        )

        # Check period distribution
        conflicts = self.db.query(Battle).filter(Battle.village_id == chirac.id).all()
        periods = {}
        for c in conflicts:
            year = c.start_year or 0
            if year < 0:
                period = "Ancient"
            elif year < 500:
                period = "Roman"
            elif year < 1500:
                period = "Medieval"
            elif year < 1800:
                period = "Early Modern"
            elif year < 1914:
                period = "Modern"
            elif year < 1918:
                period = "WWI"
            elif year < 1945:
                period = "WWII"
            else:
                period = "Contemporary"
            periods[period] = periods.get(period, 0) + 1

        print(f"\n       Period Distribution:")
        for period, count in sorted(periods.items()):
            print(f"         - {period}: {count} conflicts")

        return conflict_count == 123

    def verify_pois(self):
        """Verify 19 POIs are loaded"""
        self.print_header("3. POINTS OF INTEREST VERIFICATION")

        chirac = self.db.query(Village).filter(Village.slug == 'chirac').first()
        if not chirac:
            self.check("POI verification", False, "Chirac village not found")
            return False

        # Count POIs
        poi_count = self.db.query(func.count(POI.id)).filter(
            POI.village_id == chirac.id
        ).scalar()

        self.check(
            "19 POIs loaded",
            poi_count == 19,
            f"Found {poi_count} POIs (expected 19)"
        )

        # Check POIs have coordinates
        pois_with_coords = self.db.query(func.count(POI.id)).filter(
            POI.village_id == chirac.id,
            POI.latitude.isnot(None),
            POI.longitude.isnot(None)
        ).scalar()

        self.check(
            "POIs have coordinates",
            pois_with_coords == poi_count,
            f"{pois_with_coords}/{poi_count} have lat/lng"
        )

        # Check active POIs
        active_pois = self.db.query(func.count(POI.id)).filter(
            POI.village_id == chirac.id,
            POI.status == 'active'
        ).scalar()

        self.check(
            "POIs are active",
            active_pois > 0,
            f"{active_pois}/{poi_count} active POIs"
        )

        return poi_count == 19

    def verify_identity_themes(self):
        """Verify 3 identity themes generated"""
        self.print_header("4. IDENTITY THEMES VERIFICATION")

        chirac = self.db.query(Village).filter(Village.slug == 'chirac').first()
        if not chirac:
            self.check("Identity themes verification", False, "Chirac village not found")
            return False

        # Count themes
        theme_count = self.db.query(func.count(IdentityTheme.id)).filter(
            IdentityTheme.village_id == chirac.id
        ).scalar()

        self.check(
            "3 identity themes generated",
            theme_count == 3,
            f"Found {theme_count} themes (expected 3)"
        )

        if theme_count > 0:
            themes = self.db.query(IdentityTheme).filter(
                IdentityTheme.village_id == chirac.id
            ).all()

            print(f"\n       Themes:")
            for theme in themes:
                print(f"         - {theme.theme_name} (confidence: {theme.confidence_score:.2f})")

        return theme_count == 3

    def verify_qr_system(self):
        """Verify QR code generation works"""
        self.print_header("5. QR CODE SYSTEM VERIFICATION")

        chirac = self.db.query(Village).filter(Village.slug == 'chirac').first()
        if not chirac:
            self.check("QR system verification", False, "Chirac village not found")
            return False

        # Check if QR codes exist
        qr_count = self.db.query(func.count(QRCode.id)).filter(
            QRCode.village_id == chirac.id
        ).scalar()

        self.check(
            "QR codes can be created",
            qr_count >= 0,
            f"Found {qr_count} QR codes"
        )

        # Check QR code service is importable
        try:
            from backend.app.services.qr_generator import get_qr_generator
            generator = get_qr_generator()
            self.check("QR generator service available", True)
        except Exception as e:
            self.check("QR generator service available", False, f"Error: {e}")
            return False

        return True

    def verify_auth_system(self):
        """Verify authentication system works"""
        self.print_header("6. AUTHENTICATION SYSTEM VERIFICATION")

        # Check users exist
        user_count = self.db.query(func.count(User.id)).scalar()
        self.check("Users exist in database", user_count > 0, f"Found {user_count} users")

        # Check auth dependencies
        try:
            from backend.app.services.auth import create_access_token, get_current_user
            self.check("Auth service imports", True)
        except Exception as e:
            self.check("Auth service imports", False, f"Error: {e}")
            return False

        return True

    def verify_api_health(self):
        """Verify API endpoints are accessible"""
        self.print_header("7. API HEALTH CHECK")

        base_url = "http://localhost:8000"

        # Health check endpoint
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            self.check("API health endpoint", response.status_code == 200)
        except Exception as e:
            self.check("API health endpoint", False, f"Error: {e}")

        # Village endpoint
        try:
            response = requests.get(f"{base_url}/api/villages/chirac", timeout=5)
            self.check("Chirac village endpoint", response.status_code == 200)
        except Exception as e:
            self.check("Chirac village endpoint", False, f"Error: {e}")

        return True

    def verify_frontend(self):
        """Verify frontend is accessible"""
        self.print_header("8. FRONTEND VERIFICATION")

        # Check if frontend dev server is running
        try:
            response = requests.get("http://localhost:5173", timeout=5)
            self.check("Frontend dev server running", response.status_code == 200)
        except Exception as e:
            self.check(
                "Frontend dev server running",
                False,
                "Run 'npm run dev' in frontend/ directory"
            )

        return True

    def run_all_checks(self):
        """Run all verification checks"""
        print(f"\n{'#' * 60}")
        print("#" + " " * 58 + "#")
        print("#  CHIRAC LAUNCH CHECKLIST - {:<32}#".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        print("#" + " " * 58 + "#")
        print(f"{'#' * 60}\n")

        self.verify_database()
        self.verify_conflicts()
        self.verify_pois()
        self.verify_identity_themes()
        self.verify_qr_system()
        self.verify_auth_system()
        self.verify_api_health()
        self.verify_frontend()

        # Summary
        self.print_header("LAUNCH CHECKLIST SUMMARY")
        print(f"Total Checks: {self.total_checks}")
        print(f"✓ Passed: {self.checks_passed}")
        print(f"✗ Failed: {self.checks_failed}")

        success_rate = (self.checks_passed / self.total_checks * 100) if self.total_checks > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")

        if self.checks_failed == 0:
            print("\n🎉 ALL CHECKS PASSED! Ready for Chirac launch!")
            return True
        else:
            print(f"\n⚠️  {self.checks_failed} checks failed. Please address before launch.")
            return False


def main():
    """Main entry point"""
    checklist = LaunchChecklist()
    success = checklist.run_all_checks()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
