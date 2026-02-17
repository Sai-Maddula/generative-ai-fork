"""
Script to completely reset the database.
This will delete the entire database file and recreate it with fresh mock data.

WARNING: This will delete ALL data including:
- Subscriptions
- Resources
- Cost history
- Recommendations
- Analyses
- Anomalies
- Forecasts
- Users (except the default demo users will be recreated)
- Gamification data (points, badges, etc.)
"""

import os
import sys

def reset_database():
    """Completely reset the database by deleting the file."""

    # Path to the database
    db_path = os.path.join(os.path.dirname(__file__), 'databases', 'cost_data.db')

    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        print("Nothing to reset. It will be created on next backend start.")
        return

    print("\n" + "="*60)
    print("DATABASE RESET SCRIPT")
    print("="*60)
    print("\nWARNING: This will DELETE the entire database file!")
    print("\nAll data will be lost including:")
    print("  • All subscriptions and resources")
    print("  • All cost history")
    print("  • All recommendations and analyses")
    print("  • All anomalies and forecasts")
    print("  • All gamification data (points, badges, awards)")
    print("  • User activity history")
    print("\nThe database will be recreated with fresh mock data")
    print("when you restart the backend server.")
    print("="*60)

    confirm = input("\nAre you ABSOLUTELY sure? Type 'DELETE' to confirm: ").strip()

    if confirm != 'DELETE':
        print("\nOperation cancelled. Database was not deleted.")
        return

    try:
        os.remove(db_path)
        print("\n✓ Database file deleted successfully!")
        print("\nNext steps:")
        print("1. Restart the backend server")
        print("2. Fresh database with new mock data will be created automatically")
        print("3. New hierarchy structure will be loaded with updated subscriptions")
    except Exception as e:
        print(f"\nError deleting database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()
