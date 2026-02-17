"""
Database module for Multi-Cloud Cost Optimizer system using SQLite.

Stores:
- Cloud subscriptions/accounts (Azure, AWS, GCP) and resources
- Cost history and daily spend tracking
- Cost analyses and anomaly detection results
- Optimization recommendations and forecasts
- Gamification data (points, badges, leaderboards)
- Award nominations between users
- User accounts for authentication
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path


class CostDatabase:
    """SQLite database for storing Azure cost optimization data."""

    def __init__(self, db_path: str = "databases/cost_data.db"):
        """
        Initialize the database connection.

        Args:
            db_path: Path to SQLite database file
        """
        # Convert relative path to absolute path relative to backend directory
        if not Path(db_path).is_absolute():
            backend_dir = Path(__file__).parent.parent.parent
            self.db_path = str(backend_dir / db_path)
        else:
            self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Initialize database schema with all required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Subscriptions table - Multi-cloud subscription/account metadata and budget info
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    provider TEXT DEFAULT 'azure',
                    environment TEXT,
                    region TEXT,
                    owner TEXT,
                    monthly_budget REAL DEFAULT 0.0,
                    current_spend REAL DEFAULT 0.0,
                    health_score INTEGER DEFAULT 100,
                    resource_count INTEGER DEFAULT 0,
                    provisioning_entity_id INTEGER,
                    organization_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Add provider column to existing tables (migration)
            try:
                cursor.execute("ALTER TABLE subscriptions ADD COLUMN provider TEXT DEFAULT 'azure'")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Add provisioning_entity_id and organization_id columns (migration)
            try:
                cursor.execute("ALTER TABLE subscriptions ADD COLUMN provisioning_entity_id INTEGER")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            try:
                cursor.execute("ALTER TABLE subscriptions ADD COLUMN organization_id TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Add last_analyzed_at column (migration)
            try:
                cursor.execute("ALTER TABLE subscriptions ADD COLUMN last_analyzed_at TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Resources table - individual cloud resources within subscriptions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    subscription_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT,
                    provider_type TEXT,
                    sku TEXT,
                    region TEXT,
                    monthly_cost REAL DEFAULT 0.0,
                    cpu_usage_pct REAL DEFAULT 0.0,
                    memory_usage_pct REAL DEFAULT 0.0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
                )
            """)

            # Add provider_type column to existing tables (migration)
            try:
                cursor.execute("ALTER TABLE resources ADD COLUMN provider_type TEXT")
            except sqlite3.OperationalError:
                # Column already exists
                pass

            # Cost history table - daily cost snapshots per subscription
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cost_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subscription_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    daily_cost REAL DEFAULT 0.0,
                    resource_breakdown TEXT,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
                )
            """)

            # Analyses table - cost analysis runs with full state serialization
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    subscription_id TEXT,
                    user_id TEXT,
                    status TEXT DEFAULT 'pending',
                    overall_confidence REAL DEFAULT 0.0,
                    health_score INTEGER DEFAULT 0,
                    started_at TEXT,
                    completed_at TEXT,
                    state_json TEXT,
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
                )
            """)

            # Anomalies table - cost anomalies detected during analysis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT,
                    subscription_id TEXT,
                    resource_name TEXT,
                    resource_type TEXT,
                    anomaly_type TEXT,
                    severity TEXT,
                    score REAL DEFAULT 0.0,
                    description TEXT,
                    affected_cost REAL DEFAULT 0.0,
                    baseline_cost REAL DEFAULT 0.0,
                    detected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
                )
            """)

            # Recommendations table - optimization suggestions from analysis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id TEXT PRIMARY KEY,
                    analysis_id TEXT,
                    subscription_id TEXT,
                    resource_name TEXT,
                    resource_type TEXT,
                    action TEXT,
                    description TEXT,
                    estimated_savings REAL DEFAULT 0.0,
                    confidence REAL DEFAULT 0.0,
                    risk_level TEXT,
                    current_config TEXT,
                    recommended_config TEXT,
                    status TEXT DEFAULT 'pending',
                    reviewed_by TEXT,
                    reviewed_at TEXT,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
                )
            """)

            # Forecasts table - cost projections from analysis
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forecasts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT,
                    subscription_id TEXT,
                    forecast_30d REAL DEFAULT 0.0,
                    forecast_90d REAL DEFAULT 0.0,
                    forecast_with_optimization REAL DEFAULT 0.0,
                    savings_if_adopted REAL DEFAULT 0.0,
                    trend TEXT,
                    confidence REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analyses(id),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id)
                )
            """)

            # Gamification table - user engagement points and badges
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gamification (
                    user_id TEXT PRIMARY KEY,
                    total_points INTEGER DEFAULT 0,
                    badges TEXT DEFAULT '[]',
                    recommendations_adopted INTEGER DEFAULT 0,
                    recommendations_reviewed INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Awards table - peer nominations and recognition
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS awards (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nominated_by TEXT,
                    nominated_user TEXT,
                    award_type TEXT,
                    reason TEXT,
                    points INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Users table - application user accounts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT,
                    role TEXT DEFAULT 'viewer',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for common query patterns
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_subscription ON resources(subscription_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_history_subscription ON cost_history(subscription_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cost_history_date ON cost_history(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_subscription ON analyses(subscription_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analyses_status ON analyses(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_analysis ON anomalies(analysis_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_anomalies_subscription ON anomalies(subscription_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_analysis ON recommendations(analysis_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_subscription ON recommendations(subscription_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_forecasts_subscription ON forecasts(subscription_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_awards_nominated_user ON awards(nominated_user)")

            print(f"Database initialized at {self.db_path}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Seed Data
    # ═══════════════════════════════════════════════════════════════════════════════

    def seed_mock_data(self, mock_data: dict):
        """
        Insert mock data from the mock data generator output.

        Expects mock_data dict with keys: subscriptions, resources, cost_history, users.
        Each key maps to a list of dicts representing rows for the corresponding table.

        Args:
            mock_data: Dictionary containing lists of subscriptions, resources,
                       cost_history entries, and users to seed into the database.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert subscriptions
            for sub in mock_data.get("subscriptions", []):
                cursor.execute("""
                    INSERT OR REPLACE INTO subscriptions (
                        id, name, provider, environment, region, owner,
                        monthly_budget, current_spend, health_score,
                        resource_count, provisioning_entity_id, organization_id,
                        created_at, updated_at, last_analyzed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    sub.get("id"),
                    sub.get("name"),
                    sub.get("provider", "azure"),
                    sub.get("environment"),
                    sub.get("region"),
                    sub.get("owner"),
                    sub.get("monthly_budget", 0.0),
                    sub.get("current_spend", 0.0),
                    sub.get("health_score", 100),
                    sub.get("resource_count", 0),
                    sub.get("provisioning_entity_id"),
                    sub.get("organization_id"),
                    sub.get("created_at", datetime.now().isoformat()),
                    sub.get("updated_at", datetime.now().isoformat()),
                    sub.get("last_analyzed_at")
                ))

            # Insert resources (dict: sub_id -> list of resource dicts)
            resources_data = mock_data.get("resources", {})
            if isinstance(resources_data, dict):
                for sub_id, res_list in resources_data.items():
                    for res in res_list:
                        cursor.execute("""
                            INSERT OR REPLACE INTO resources (
                                id, subscription_id, name, type, sku, region,
                                monthly_cost, cpu_usage_pct, memory_usage_pct,
                                is_active, created_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            res.get("id"),
                            sub_id,
                            res.get("name"),
                            res.get("type"),
                            res.get("sku"),
                            res.get("region"),
                            res.get("monthly_cost", 0.0),
                            res.get("cpu_usage_pct", 0.0),
                            res.get("memory_usage_pct", 0.0),
                            1 if res.get("is_active", True) else 0,
                            res.get("created_at", datetime.now().isoformat())
                        ))

            # Insert cost history (dict: sub_id -> list of daily records)
            # First, clear existing cost_history to avoid duplicates
            cursor.execute("DELETE FROM cost_history")

            history_data = mock_data.get("cost_history", {})
            if isinstance(history_data, dict):
                for sub_id, entries in history_data.items():
                    for entry in entries:
                        resource_breakdown = entry.get("resource_breakdown")
                        if isinstance(resource_breakdown, (dict, list)):
                            resource_breakdown = json.dumps(resource_breakdown)

                        cursor.execute("""
                            INSERT INTO cost_history (
                                subscription_id, date, daily_cost, resource_breakdown
                            ) VALUES (?, ?, ?, ?)
                        """, (
                            sub_id,
                            entry.get("date"),
                            entry.get("daily_cost", 0.0),
                            resource_breakdown
                        ))

            # Insert users
            for user in mock_data.get("users", []):
                cursor.execute("""
                    INSERT OR REPLACE INTO users (
                        username, password_hash, full_name, role, is_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    user.get("username"),
                    user.get("password_hash"),
                    user.get("full_name") or user.get("display_name", ""),
                    user.get("role", "viewer"),
                    1 if user.get("is_active", True) else 0,
                    user.get("created_at", datetime.now().isoformat())
                ))

            print(f"Seeded mock data: "
                  f"{len(mock_data.get('subscriptions', []))} subscriptions, "
                  f"{len(mock_data.get('resources', []))} resources, "
                  f"{len(mock_data.get('cost_history', []))} cost history entries, "
                  f"{len(mock_data.get('users', []))} users")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Subscription Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all Azure subscriptions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM subscriptions
                ORDER BY name ASC
            """)

            return [dict(row) for row in cursor.fetchall()]

    def get_subscription(self, sub_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single subscription by ID.

        Args:
            sub_id: The subscription identifier.

        Returns:
            Dictionary with subscription data, or None if not found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM subscriptions WHERE id = ?
            """, (sub_id,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def update_subscription_health(self, sub_id: str, health_score: int):
        """
        Update the health score for a subscription.

        Args:
            sub_id: The subscription identifier.
            health_score: New health score value (0-100).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE subscriptions
                SET health_score = ?,
                    updated_at = ?
                WHERE id = ?
            """, (health_score, datetime.now().isoformat(), sub_id))

    def update_subscription_last_analyzed(self, sub_id: str, analyzed_at: str = None):
        """
        Update the last_analyzed_at timestamp for a subscription.

        Args:
            sub_id: The subscription identifier.
            analyzed_at: ISO format timestamp. If None, uses current time.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            timestamp = analyzed_at or datetime.now().isoformat()

            cursor.execute("""
                UPDATE subscriptions
                SET last_analyzed_at = ?,
                    updated_at = ?
                WHERE id = ?
            """, (timestamp, datetime.now().isoformat(), sub_id))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Resource Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_resources(self, sub_id: str) -> List[Dict[str, Any]]:
        """
        Get all resources for a given subscription.

        Args:
            sub_id: The subscription identifier.

        Returns:
            List of resource dictionaries.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM resources
                WHERE subscription_id = ?
                ORDER BY monthly_cost DESC
            """, (sub_id,))

            return [dict(row) for row in cursor.fetchall()]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Cost History Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_cost_history(self, sub_id: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get cost history for a subscription over a number of recent days.

        Args:
            sub_id: The subscription identifier.
            days: Number of days of history to retrieve (default 30).

        Returns:
            List of cost history dictionaries with parsed resource_breakdown.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

            cursor.execute("""
                SELECT * FROM cost_history
                WHERE subscription_id = ? AND date >= ?
                ORDER BY date ASC
            """, (sub_id, cutoff_date))

            results = []
            for row in cursor.fetchall():
                entry = dict(row)
                # Parse JSON resource breakdown if present
                if entry.get("resource_breakdown"):
                    try:
                        entry["resource_breakdown"] = json.loads(entry["resource_breakdown"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                results.append(entry)

            return results

    # ═══════════════════════════════════════════════════════════════════════════════
    # Analysis Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_analysis(self, analysis_data: dict):
        """
        Save a new analysis record.

        Args:
            analysis_data: Dictionary with analysis fields including id,
                           subscription_id, user_id, status, etc.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            state_json = analysis_data.get("state_json")
            if isinstance(state_json, (dict, list)):
                state_json = json.dumps(state_json)

            cursor.execute("""
                INSERT INTO analyses (
                    id, subscription_id, user_id, status,
                    overall_confidence, health_score,
                    started_at, completed_at, state_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                analysis_data.get("id"),
                analysis_data.get("subscription_id"),
                analysis_data.get("user_id"),
                analysis_data.get("status", "pending"),
                analysis_data.get("overall_confidence", 0.0),
                analysis_data.get("health_score", 0),
                analysis_data.get("started_at", datetime.now().isoformat()),
                analysis_data.get("completed_at"),
                state_json
            ))

    def update_analysis(self, analysis_id: str, updates: dict):
        """
        Update an existing analysis record with new field values.

        Args:
            analysis_id: The analysis identifier.
            updates: Dictionary of field names and their new values.
                     Supports: status, overall_confidence, health_score,
                     completed_at, state_json.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            set_clauses = []
            params = []

            for key, value in updates.items():
                if key == "state_json" and isinstance(value, (dict, list)):
                    value = json.dumps(value)
                set_clauses.append(f"{key} = ?")
                params.append(value)

            if not set_clauses:
                return

            params.append(analysis_id)
            query = f"UPDATE analyses SET {', '.join(set_clauses)} WHERE id = ?"

            cursor.execute(query, params)

    def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single analysis by ID.

        Args:
            analysis_id: The analysis identifier.

        Returns:
            Dictionary with analysis data and parsed state_json, or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM analyses WHERE id = ?
            """, (analysis_id,))

            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse serialized state JSON if present
                if result.get("state_json"):
                    try:
                        result["state_json"] = json.loads(result["state_json"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                return result
            return None

    def get_analyses(self, sub_id: str = None) -> List[Dict[str, Any]]:
        """
        Get analyses, optionally filtered by subscription.

        Args:
            sub_id: Optional subscription identifier to filter by.

        Returns:
            List of analysis dictionaries ordered by start time descending.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if sub_id:
                cursor.execute("""
                    SELECT * FROM analyses
                    WHERE subscription_id = ?
                    ORDER BY started_at DESC
                """, (sub_id,))
            else:
                cursor.execute("""
                    SELECT * FROM analyses
                    ORDER BY started_at DESC
                """)

            results = []
            for row in cursor.fetchall():
                entry = dict(row)
                if entry.get("state_json"):
                    try:
                        entry["state_json"] = json.loads(entry["state_json"])
                    except (json.JSONDecodeError, TypeError):
                        pass
                results.append(entry)

            return results

    # ═══════════════════════════════════════════════════════════════════════════════
    # Anomaly Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_anomalies(self, anomalies: list):
        """
        Bulk insert anomaly records.

        Args:
            anomalies: List of anomaly dictionaries, each containing
                       analysis_id, subscription_id, resource_name, etc.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for anomaly in anomalies:
                cursor.execute("""
                    INSERT INTO anomalies (
                        analysis_id, subscription_id, resource_name,
                        resource_type, anomaly_type, severity, score,
                        description, affected_cost, baseline_cost, detected_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    anomaly.get("analysis_id"),
                    anomaly.get("subscription_id"),
                    anomaly.get("resource_name"),
                    anomaly.get("resource_type"),
                    anomaly.get("anomaly_type"),
                    anomaly.get("severity"),
                    anomaly.get("score", 0.0),
                    anomaly.get("description"),
                    anomaly.get("affected_cost", 0.0),
                    anomaly.get("baseline_cost", 0.0),
                    anomaly.get("detected_at", datetime.now().isoformat())
                ))

    def get_anomalies(self, analysis_id: str = None, sub_id: str = None) -> List[Dict[str, Any]]:
        """
        Get anomalies, optionally filtered by analysis or subscription.

        Args:
            analysis_id: Optional analysis identifier to filter by.
            sub_id: Optional subscription identifier to filter by.

        Returns:
            List of anomaly dictionaries ordered by score descending.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            conditions = []
            params = []

            if analysis_id:
                conditions.append("analysis_id = ?")
                params.append(analysis_id)
            if sub_id:
                conditions.append("subscription_id = ?")
                params.append(sub_id)

            query = "SELECT * FROM anomalies"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY score DESC"

            cursor.execute(query, params)

            return [dict(row) for row in cursor.fetchall()]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Recommendation Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_recommendations(self, recommendations: list):
        """
        Bulk insert recommendation records.

        Args:
            recommendations: List of recommendation dictionaries.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            for rec in recommendations:
                cursor.execute("""
                    INSERT OR REPLACE INTO recommendations (
                        id, analysis_id, subscription_id, resource_name,
                        resource_type, action, description,
                        estimated_savings, confidence, risk_level,
                        current_config, recommended_config,
                        status, reviewed_by, reviewed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rec.get("id"),
                    rec.get("analysis_id"),
                    rec.get("subscription_id"),
                    rec.get("resource_name"),
                    rec.get("resource_type"),
                    rec.get("action"),
                    rec.get("description"),
                    rec.get("estimated_savings", 0.0),
                    rec.get("confidence", 0.0),
                    rec.get("risk_level"),
                    rec.get("current_config"),
                    rec.get("recommended_config"),
                    rec.get("status", "pending"),
                    rec.get("reviewed_by"),
                    rec.get("reviewed_at")
                ))

    def get_recommendations(
        self,
        analysis_id: str = None,
        sub_id: str = None,
        status: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get recommendations with optional filters.

        Args:
            analysis_id: Optional analysis identifier to filter by.
            sub_id: Optional subscription identifier to filter by.
            status: Optional status to filter by (pending, approved, rejected).

        Returns:
            List of recommendation dictionaries ordered by estimated savings descending.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            conditions = []
            params = []

            if analysis_id:
                conditions.append("analysis_id = ?")
                params.append(analysis_id)
            if sub_id:
                conditions.append("subscription_id = ?")
                params.append(sub_id)
            if status:
                conditions.append("status = ?")
                params.append(status)

            query = "SELECT * FROM recommendations"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY estimated_savings DESC"

            cursor.execute(query, params)

            return [dict(row) for row in cursor.fetchall()]

    def get_recommendation(self, rec_id: str) -> Dict[str, Any]:
        """
        Get a single recommendation by ID.

        Args:
            rec_id: The recommendation identifier.

        Returns:
            Recommendation dictionary or None if not found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM recommendations WHERE id = ?", (rec_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_recommendation(self, rec_id: str, status: str, reviewed_by: str = None):
        """
        Update a recommendation status (approve or reject).

        Args:
            rec_id: The recommendation identifier.
            status: New status value (e.g. 'approved', 'rejected').
            reviewed_by: Optional user identifier who reviewed it.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE recommendations
                SET status = ?,
                    reviewed_by = COALESCE(?, reviewed_by),
                    reviewed_at = ?
                WHERE id = ?
            """, (status, reviewed_by, datetime.now().isoformat(), rec_id))

    # ═══════════════════════════════════════════════════════════════════════════════
    # Forecast Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_forecast(self, forecast: dict):
        """
        Insert a forecast record.

        Args:
            forecast: Dictionary with forecast fields including analysis_id,
                      subscription_id, forecast_30d, forecast_90d, etc.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO forecasts (
                    analysis_id, subscription_id, forecast_30d, forecast_90d,
                    forecast_with_optimization, savings_if_adopted,
                    trend, confidence, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                forecast.get("analysis_id"),
                forecast.get("subscription_id"),
                forecast.get("forecast_30d", 0.0),
                forecast.get("forecast_90d", 0.0),
                forecast.get("forecast_with_optimization", 0.0),
                forecast.get("savings_if_adopted", 0.0),
                forecast.get("trend"),
                forecast.get("confidence", 0.0),
                forecast.get("created_at", datetime.now().isoformat())
            ))

    def get_forecasts(self, sub_id: str) -> List[Dict[str, Any]]:
        """
        Get all forecasts for a subscription.

        Args:
            sub_id: The subscription identifier.

        Returns:
            List of forecast dictionaries ordered by creation time descending.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM forecasts
                WHERE subscription_id = ?
                ORDER BY created_at DESC
            """, (sub_id,))

            return [dict(row) for row in cursor.fetchall()]

    # ═══════════════════════════════════════════════════════════════════════════════
    # Gamification Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_gamification(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get gamification data for a user.

        Args:
            user_id: The user identifier.

        Returns:
            Dictionary with gamification data and parsed badges list, or None.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM gamification WHERE user_id = ?
            """, (user_id,))

            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse JSON badges list
                if result.get("badges"):
                    try:
                        result["badges"] = json.loads(result["badges"])
                    except (json.JSONDecodeError, TypeError):
                        result["badges"] = []
                return result
            return None

    def update_gamification(
        self,
        user_id: str,
        points: int = 0,
        badges: list = None,
        adopted: int = 0,
        reviewed: int = 0
    ):
        """
        Update gamification data for a user. Creates the record if it does not exist.
        Points, adopted, and reviewed counts are additive (incremented).
        Badges are merged with existing badges (union, no duplicates).

        Args:
            user_id: The user identifier.
            points: Points to add to the user's total.
            badges: List of new badge strings to merge with existing badges.
            adopted: Number of adopted recommendations to add.
            reviewed: Number of reviewed recommendations to add.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Check if user gamification record exists
            cursor.execute("SELECT * FROM gamification WHERE user_id = ?", (user_id,))
            existing = cursor.fetchone()

            if existing:
                existing_data = dict(existing)

                # Merge badges (union of existing and new)
                current_badges = []
                if existing_data.get("badges"):
                    try:
                        current_badges = json.loads(existing_data["badges"])
                    except (json.JSONDecodeError, TypeError):
                        current_badges = []

                if badges:
                    # Add new badges that are not already present
                    badge_set = set(current_badges)
                    for badge in badges:
                        badge_set.add(badge)
                    current_badges = list(badge_set)

                # Calculate new streak: increment if activity today, otherwise keep
                new_streak = existing_data.get("current_streak", 0)
                if points > 0 or adopted > 0 or reviewed > 0:
                    new_streak += 1

                cursor.execute("""
                    UPDATE gamification
                    SET total_points = total_points + ?,
                        badges = ?,
                        recommendations_adopted = recommendations_adopted + ?,
                        recommendations_reviewed = recommendations_reviewed + ?,
                        current_streak = ?,
                        updated_at = ?
                    WHERE user_id = ?
                """, (
                    points,
                    json.dumps(current_badges),
                    adopted,
                    reviewed,
                    new_streak,
                    datetime.now().isoformat(),
                    user_id
                ))
            else:
                # Create new gamification record
                badges_json = json.dumps(badges if badges else [])

                cursor.execute("""
                    INSERT INTO gamification (
                        user_id, total_points, badges,
                        recommendations_adopted, recommendations_reviewed,
                        current_streak, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user_id,
                    points,
                    badges_json,
                    adopted,
                    reviewed,
                    1 if (points > 0 or adopted > 0 or reviewed > 0) else 0,
                    datetime.now().isoformat()
                ))

    def get_leaderboard(self) -> List[Dict[str, Any]]:
        """
        Get the gamification leaderboard sorted by total points descending.

        Returns:
            List of gamification dictionaries with parsed badges, sorted by points.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM gamification
                ORDER BY total_points DESC
            """)

            results = []
            for row in cursor.fetchall():
                entry = dict(row)
                if entry.get("badges"):
                    try:
                        entry["badges"] = json.loads(entry["badges"])
                    except (json.JSONDecodeError, TypeError):
                        entry["badges"] = []
                results.append(entry)

            return results

    # ═══════════════════════════════════════════════════════════════════════════════
    # Award Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def save_award(self, award: dict):
        """
        Insert an award nomination record.

        Args:
            award: Dictionary with award fields including nominated_by,
                   nominated_user, award_type, reason, points.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO awards (
                    nominated_by, nominated_user, award_type,
                    reason, points, created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                award.get("nominated_by"),
                award.get("nominated_user"),
                award.get("award_type"),
                award.get("reason"),
                award.get("points", 0),
                award.get("created_at", datetime.now().isoformat())
            ))

    def get_awards(self) -> List[Dict[str, Any]]:
        """
        Get all award nominations.

        Returns:
            List of award dictionaries ordered by creation time descending.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM awards
                ORDER BY created_at DESC
            """)

            return [dict(row) for row in cursor.fetchall()]

    # ═══════════════════════════════════════════════════════════════════════════════
    # User Methods
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get a user by username.

        Args:
            username: The unique username to look up.

        Returns:
            Dictionary with user data, or None if not found.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT * FROM users WHERE username = ?
            """, (username,))

            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_users(self) -> List[Dict[str, Any]]:
        """
        Get all users.

        Returns:
            List of user dictionaries ordered by creation time descending.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, username, full_name, role, is_active, created_at
                FROM users
                ORDER BY created_at DESC
            """)

            return [dict(row) for row in cursor.fetchall()]
