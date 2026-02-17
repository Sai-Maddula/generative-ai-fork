"""
Script to clear agent recommendations, analysis data, and gamification data from the database.
This will delete:
- All recommendations
- All analyses
- All anomalies
- All forecasts
- All gamification data (points, badges, awards)
- HITL queue entries (not in DB, but in memory)
- Reset last_analyzed_at timestamps on all subscriptions

Subscriptions, resources, cost history, and users will be preserved.
"""

import sqlite3
import os

def clear_analysis_data():
    """Clear all analysis-related and gamification data from the database."""

    # Path to the database
    db_path = os.path.join(os.path.dirname(__file__), 'databases', 'cost_data.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Nothing to clear.")
        return

    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get counts before deletion
        cursor.execute("SELECT COUNT(*) FROM recommendations")
        rec_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM analyses")
        analysis_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM anomalies")
        anomaly_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM forecasts")
        forecast_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM gamification")
        gamification_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM awards")
        awards_count = cursor.fetchone()[0]

        print("\n" + "="*60)
        print("CURRENT DATA COUNTS")
        print("="*60)
        print(f"Recommendations: {rec_count}")
        print(f"Analyses: {analysis_count}")
        print(f"Anomalies: {anomaly_count}")
        print(f"Forecasts: {forecast_count}")
        print(f"Gamification (points/badges): {gamification_count}")
        print(f"Awards: {awards_count}")
        print("="*60)

        if rec_count == 0 and analysis_count == 0 and anomaly_count == 0 and forecast_count == 0 and gamification_count == 0 and awards_count == 0:
            print("\nNo data to clear. Database is already clean.")
            conn.close()
            return

        # Confirm deletion
        print("\nThis will DELETE all the above data.")
        print("\nWARNING: This includes:")
        print("  • All user points and badges")
        print("  • All awards and achievements")
        print("  • All analysis results and recommendations")
        print("  • Reset all subscription last_analyzed_at timestamps")
        confirm = input("\nAre you sure you want to proceed? (yes/no): ").strip().lower()

        if confirm != 'yes':
            print("Operation cancelled.")
            conn.close()
            return

        # Delete data from all tables
        print("\nDeleting data...")

        cursor.execute("DELETE FROM recommendations")
        print(f"✓ Deleted {rec_count} recommendations")

        cursor.execute("DELETE FROM analyses")
        print(f"✓ Deleted {analysis_count} analyses")

        cursor.execute("DELETE FROM anomalies")
        print(f"✓ Deleted {anomaly_count} anomalies")

        cursor.execute("DELETE FROM forecasts")
        print(f"✓ Deleted {forecast_count} forecasts")

        cursor.execute("DELETE FROM gamification")
        print(f"✓ Deleted {gamification_count} gamification records (points/badges)")

        cursor.execute("DELETE FROM awards")
        print(f"✓ Deleted {awards_count} awards")

        # Reset last_analyzed_at timestamps on all subscriptions
        cursor.execute("UPDATE subscriptions SET last_analyzed_at = NULL")
        cursor.execute("SELECT COUNT(*) FROM subscriptions")
        sub_count = cursor.fetchone()[0]
        print(f"✓ Reset last_analyzed_at timestamps for {sub_count} subscriptions")

        # Commit the changes
        conn.commit()

        print("\n" + "="*60)
        print("SUCCESS! All analysis and gamification data has been cleared.")
        print("="*60)
        print("\nPreserved data:")
        print("  ✓ Subscriptions (with hierarchy)")
        print("  ✓ Resources")
        print("  ✓ Cost history")
        print("  ✓ Users")
        print("\nYou can now:")
        print("1. Run new analyses to generate fresh recommendations")
        print("2. User points/badges will start from zero")
        print("3. The HITL queue (in-memory) will be cleared on backend restart")

    except sqlite3.Error as e:
        print(f"\nError: {e}")
        print("Failed to clear data.")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CLEAR ANALYSIS & GAMIFICATION DATA SCRIPT")
    print("="*60)
    clear_analysis_data()
