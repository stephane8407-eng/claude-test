"""
SQLAlchemy models for SPV Treasure Map
"""
from app.models.battle import Battle
from app.models.place import Place
from app.models.place_context import PlaceContext
from app.models.user import User
from app.models.api_key import APIKey
from app.models.password_reset_token import PasswordResetToken
from app.models.usage_event import UsageEvent
from app.models.local_conflict import LocalConflict
from app.models.village import Village
from app.models.poi_type import POIType
from app.models.poi import POI
from app.models.identity_category import IdentityCategory
from app.models.identity_theme import IdentityTheme
from app.models.village_data_snapshot import VillageDataSnapshot
from app.models.role import Role
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.qr_code import QRCode
from app.models.qr_scan import QRScan
from app.models.qr_route import QRRoute

# V1 Product Spec - New models
from app.models.topic import Topic
from app.models.sponsor import Sponsor
from app.models.sponsor_slot import SponsorSlot
from app.models.project import Project

# Phase D: RAG Foundation
from app.models.revival_case_study import RevivalCaseStudy
from app.models.funding_program import FundingProgram
from app.models.village_identity import VillageIdentity

# Phase E: Project Management Dashboard
from app.models.project_instance import ProjectInstance
from app.models.grant_application import GrantApplication
from app.models.village_media import VillageMedia

__all__ = [
    "Battle",
    "Place",
    "PlaceContext",
    "User",
    "APIKey",
    "PasswordResetToken",
    "UsageEvent",
    "LocalConflict",
    "Village",
    "POIType",
    "POI",
    "IdentityCategory",
    "IdentityTheme",
    "VillageDataSnapshot",
    "Role",
    "Permission",
    "RolePermission",
    "QRCode",
    "QRScan",
    "QRRoute",
    # V1 Product Spec - New models
    "Topic",
    "Sponsor",
    "SponsorSlot",
    "Project",
    # Phase D: RAG Foundation
    "RevivalCaseStudy",
    "FundingProgram",
    "VillageIdentity",
    # Phase E: Project Management Dashboard
    "ProjectInstance",
    "GrantApplication",
    "VillageMedia",
]
