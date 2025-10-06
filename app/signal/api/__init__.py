"""
Signal REST API Router

This module provides a centralized router for all Signal API endpoints,
organized into modular route files for better maintainability.
"""

from fastapi import APIRouter

from .accounts import router as accounts_router
from .attachments import router as attachments_router
from .contacts import router as contacts_router
from .devices import router as devices_router
from .general import router as general_router
from .groups import router as groups_router
from .identities import router as identities_router
from .messages import router as messages_router
from .profiles import router as profiles_router
from .reactions import router as reactions_router
from .receipts import router as receipts_router
from .search import router as search_router
from .stickers import router as stickers_router

# Create the main API router
router = APIRouter()

# Include all modular routers
router.include_router(
    general_router,
    prefix="/v1",
    tags=["General"]
)

router.include_router(
    accounts_router,
    prefix="/v1/accounts",
    tags=["Accounts"]
)

router.include_router(
    attachments_router,
    prefix="/v1/attachments",
    tags=["Attachments"]
)

router.include_router(
    contacts_router,
    prefix="/v1/contacts",
    tags=["Contacts"]
)

router.include_router(
    devices_router,
    prefix="/v1",
    tags=["Devices"]
)

router.include_router(
    groups_router,
    prefix="/v1/groups",
    tags=["Groups"]
)

router.include_router(
    identities_router,
    prefix="/v1/identities",
    tags=["Identities"]
)

router.include_router(
    messages_router,
    prefix="/v1",
    tags=["Messages"]
)

router.include_router(
    profiles_router,
    prefix="/v1/profiles",
    tags=["Profiles"]
)

router.include_router(
    reactions_router,
    prefix="/v1/reactions",
    tags=["Reactions"]
)

router.include_router(
    receipts_router,
    prefix="/v1/receipts",
    tags=["Receipts"]
)

router.include_router(
    search_router,
    prefix="/v1/search",
    tags=["Search"]
)

router.include_router(
    stickers_router,
    prefix="/v1/sticker-packs",
    tags=["Sticker Packs"]
)
