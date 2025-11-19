#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to uninstall and reinstall the adi_treasury_cashcount module.
Run this from the Odoo directory with: python cleanup_module.py
"""
import os
import sys
import django

# Add the Odoo directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Set up environment
os.environ.setdefault('ODOO_CONFIG', '/etc/odoo/odoo.conf')

# This is a standalone cleanup script
# It can be used to manually remove the module state

if __name__ == '__main__':
    print("Cleanup script for adi_treasury_cashcount module")
    print("=" * 50)
    print("\nTo use this script:")
    print("1. Access the Odoo database directly")
    print("2. Run these SQL commands:")
    print("\n-- Remove the module record")
    print("DELETE FROM ir_module_module WHERE name = 'adi_treasury_cashcount';")
    print("\n-- Remove the module views")
    print("DELETE FROM ir_ui_view WHERE module = 'adi_treasury_cashcount';")
    print("\n-- Remove model fields")
    print("DELETE FROM ir_model_fields WHERE model LIKE 'treasury.cash%' AND name IN ('count_line_ids', 'counted_total', 'use_cash_count');")
    print("\n-- Then restart Odoo and reinstall the module")
