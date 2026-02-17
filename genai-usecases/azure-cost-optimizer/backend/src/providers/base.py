"""
Base Cloud Provider Interface

Defines the abstract interface that all cloud providers must implement
to work with the cost optimization agent system.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


class ProviderType(str, Enum):
    """Supported cloud providers."""
    AZURE = "azure"
    AWS = "aws"
    GCP = "gcp"


class CloudProvider(ABC):
    """
    Abstract base class for cloud provider integrations.

    Each provider must implement methods to:
    - Fetch cost data and resource information
    - Normalize data to a common format for agent processing
    - Generate provider-specific recommendations
    """

    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize the cloud provider with credentials.

        Args:
            credentials: Provider-specific authentication credentials
        """
        self.credentials = credentials
        self.provider_type = self._get_provider_type()

    @abstractmethod
    def _get_provider_type(self) -> ProviderType:
        """Return the provider type."""
        pass

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the cloud provider.

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get list of accounts/subscriptions for this provider.

        Returns:
            List of account dictionaries with normalized structure:
            {
                "id": str,
                "name": str,
                "provider": ProviderType,
                "status": str,
                "region": str (primary region),
                "tags": Dict[str, str]
            }
        """
        pass

    @abstractmethod
    def get_cost_data(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch cost data for an account within a date range.

        Args:
            account_id: Account/subscription identifier
            start_date: Start of date range
            end_date: End of date range
            granularity: "daily", "weekly", or "monthly"

        Returns:
            List of cost records with normalized structure:
            {
                "date": str (ISO format),
                "cost": float,
                "currency": str,
                "service": str (optional breakdown by service)
            }
        """
        pass

    @abstractmethod
    def get_resources(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get all billable resources for an account.

        Returns:
            List of resource dictionaries with normalized structure:
            {
                "id": str,
                "name": str,
                "type": str (normalized: "vm", "storage", "database", etc.),
                "provider_type": str (provider-specific type),
                "region": str,
                "status": str,
                "tags": Dict[str, str],
                "monthly_cost": float,
                "utilization": Dict[str, float] (cpu, memory, etc.),
                "metadata": Dict[str, Any] (provider-specific details)
            }
        """
        pass

    @abstractmethod
    def get_resource_utilization(
        self,
        resource_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get utilization metrics for a specific resource.

        Args:
            resource_id: Resource identifier
            days: Number of days of historical data

        Returns:
            {
                "cpu": {"avg": float, "max": float, "p95": float},
                "memory": {"avg": float, "max": float, "p95": float},
                "network": {"avg": float, "max": float},
                "storage": {"used": float, "total": float}
            }
        """
        pass

    @abstractmethod
    def normalize_resource_type(self, provider_resource_type: str) -> str:
        """
        Convert provider-specific resource type to normalized type.

        Examples:
            Azure: "Microsoft.Compute/virtualMachines" -> "vm"
            AWS: "AWS::EC2::Instance" -> "vm"

        Args:
            provider_resource_type: Provider-specific resource type string

        Returns:
            Normalized type: "vm", "storage", "database", "network", etc.
        """
        pass

    @abstractmethod
    def generate_recommendations(
        self,
        resources: List[Dict[str, Any]],
        cost_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate provider-specific cost optimization recommendations.

        Args:
            resources: List of resources from get_resources()
            cost_data: Historical cost data from get_cost_data()

        Returns:
            List of recommendation dictionaries:
            {
                "id": str,
                "type": str (e.g., "rightsizing", "reserved_instance"),
                "resource_id": str,
                "resource_name": str,
                "title": str,
                "description": str,
                "current_cost": float,
                "projected_cost": float,
                "savings": float,
                "risk_level": str ("low", "medium", "high"),
                "provider_specific": Dict[str, Any]
            }
        """
        pass

    def get_cost_summary(self, account_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Get high-level cost summary for an account.

        This is a helper method that uses get_cost_data() to compute summary stats.
        Can be overridden for provider-specific optimizations.

        Args:
            account_id: Account/subscription identifier
            days: Number of days to analyze

        Returns:
            {
                "total_cost": float,
                "average_daily_cost": float,
                "trend": str ("increasing", "decreasing", "stable"),
                "top_services": List[Dict] (service name and cost)
            }
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        cost_data = self.get_cost_data(account_id, start_date, end_date)

        if not cost_data:
            return {
                "total_cost": 0,
                "average_daily_cost": 0,
                "trend": "stable",
                "top_services": []
            }

        total = sum(record["cost"] for record in cost_data)
        avg_daily = total / len(cost_data) if cost_data else 0

        # Simple trend detection
        if len(cost_data) >= 2:
            first_half_avg = sum(r["cost"] for r in cost_data[:len(cost_data)//2]) / (len(cost_data)//2)
            second_half_avg = sum(r["cost"] for r in cost_data[len(cost_data)//2:]) / (len(cost_data) - len(cost_data)//2)

            if second_half_avg > first_half_avg * 1.1:
                trend = "increasing"
            elif second_half_avg < first_half_avg * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

        # Aggregate by service
        service_costs = {}
        for record in cost_data:
            service = record.get("service", "Other")
            service_costs[service] = service_costs.get(service, 0) + record["cost"]

        top_services = [
            {"service": k, "cost": v}
            for k, v in sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        return {
            "total_cost": total,
            "average_daily_cost": avg_daily,
            "trend": trend,
            "top_services": top_services
        }
