#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour le tableau de bord trésorerie
Exécuter avec : python3 diagnostic_treasury.py
"""

import psycopg2
import sys

# Configuration - Modifier selon votre base
DB_NAME = "o15_ab"  # Changez par le nom de votre base
DB_USER = "odoo"
DB_PASSWORD = "odoo"
DB_HOST = "localhost"
DB_PORT = "5432"

def run_diagnostic():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()

        print("=" * 60)
        print("DIAGNOSTIC TABLEAU DE BORD TRÉSORERIE")
        print("=" * 60)

        # 1. Vérifier les coffres
        print("\n1. COFFRES (treasury_safe):")
        print("-" * 40)
        cur.execute("SELECT id, name, code, current_balance, state, active FROM treasury_safe ORDER BY id")
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"  ID={row[0]}, Nom='{row[1]}', Code='{row[2]}', Solde={row[3]}, État={row[4]}, Actif={row[5]}")
        else:
            print("  Aucun coffre trouvé!")

        # 2. Vérifier les caisses et leurs clôtures en cours
        print("\n2. CAISSES ET CLÔTURES EN COURS:")
        print("-" * 40)
        cur.execute("""
            SELECT c.id, c.name, c.code,
                   (SELECT COUNT(*) FROM treasury_cash_closing cc
                    WHERE cc.cash_id = c.id AND cc.state IN ('draft', 'confirmed')) as pending_count,
                   (SELECT string_agg(cc.state, ', ') FROM treasury_cash_closing cc
                    WHERE cc.cash_id = c.id AND cc.state IN ('draft', 'confirmed')) as pending_states
            FROM treasury_cash c
            WHERE c.active = true
            ORDER BY c.id
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  Caisse '{row[1]}' (ID={row[0]}): {row[3]} clôtures en cours, États: {row[4]}")

        # 3. Vérifier la vue treasury_dashboard
        print("\n3. VUE TREASURY_DASHBOARD:")
        print("-" * 40)
        cur.execute("""
            SELECT id, name, code, type, balance, has_pending_closing, is_balance_final
            FROM treasury_dashboard
            ORDER BY sequence, type
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  [{row[3]:12}] {row[1]:20} | Solde={row[4]:>12} | EnCours={row[5]} | Finalisé={row[6]}")

        # 4. Vérifier si la vue existe et sa définition
        print("\n4. DÉFINITION DE LA VUE:")
        print("-" * 40)
        cur.execute("""
            SELECT pg_get_viewdef('treasury_dashboard'::regclass, true)
        """)
        view_def = cur.fetchone()[0]
        # Afficher seulement les premières lignes
        lines = view_def.split('\n')[:10]
        for line in lines:
            print(f"  {line}")
        print("  ...")

        # 5. Compter les éléments par type
        print("\n5. COMPTAGE PAR TYPE:")
        print("-" * 40)
        cur.execute("""
            SELECT type, COUNT(*) FROM treasury_dashboard GROUP BY type ORDER BY type
        """)
        rows = cur.fetchall()
        for row in rows:
            print(f"  {row[0]}: {row[1]} élément(s)")

        conn.close()
        print("\n" + "=" * 60)
        print("FIN DU DIAGNOSTIC")
        print("=" * 60)

    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_diagnostic()
