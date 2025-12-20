from .start import router as start_router
from .buy import router as buy_router
from .payments import router as payments_router
from .support import router as support_router
from .referral import router as referral_router
from .admin import router as admin_router

__all__ = [
    'start_router',
    'buy_router',
    'payments_router',
    'support_router',
    'referral_router',
    'admin_router'
]