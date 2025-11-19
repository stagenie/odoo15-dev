# -*- coding: utf-8 -*-
from . import models


def post_init_hook(cr, registry):
    """Post-installation hook to clean up orphaned records"""
    import logging
    _logger = logging.getLogger(__name__)

    try:
        # Clean up any orphaned treasury.cash.closing.line records
        # These might be causing CacheMiss errors during view rendering
        cr.execute("""
            DELETE FROM treasury_cash_closing_line
            WHERE closing_id NOT IN (SELECT id FROM treasury_cash_closing)
        """)
        _logger.info("Orphaned records cleanup completed successfully for adi_treasury_cashcount")
    except Exception as e:
        _logger.warning(f"Cleanup warning (not fatal) in adi_treasury_cashcount: {str(e)}")
