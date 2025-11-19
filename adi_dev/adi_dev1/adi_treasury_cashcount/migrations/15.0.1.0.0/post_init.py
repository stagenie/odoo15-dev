# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Post-installation migration script to clean up orphaned records"""
    _logger.info("Running post-init script for adi_treasury_cashcount")

    try:
        # Clean up any orphaned treasury.cash.closing.line records
        # These might be causing CacheMiss errors during view rendering
        cr.execute("""
            DELETE FROM treasury_cash_closing_line
            WHERE closing_id NOT IN (SELECT id FROM treasury_cash_closing)
        """)

        _logger.info("Cleanup completed successfully")
    except Exception as e:
        _logger.warning(f"Cleanup warning (not fatal): {str(e)}")
