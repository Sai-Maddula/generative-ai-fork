"""
Mock Multi-Cloud Cost Data Generator
====================================
Generates realistic but simulated Azure and AWS cost and resource data for POC purposes.
Uses a fixed random seed (42) for reproducibility across runs.

All data is generated using only the Python standard library -- no external
dependencies are required.
"""

import random
import uuid
import hashlib
import math
from datetime import datetime, timedelta
from typing import Any

# ---------------------------------------------------------------------------
# Fixed seed for reproducible output
# ---------------------------------------------------------------------------
_RNG = random.Random(42)

# ---------------------------------------------------------------------------
# Constants & lookup tables
# ---------------------------------------------------------------------------

AZURE_REGIONS = [
    "eastus", "eastus2", "westus", "westus2", "centralus",
    "southcentralus", "northcentralus", "westus3", "eastus3", "westcentralus",
]

VM_SKUS = [
    ("Standard_B2s", 30.37),
    ("Standard_B4ms", 60.74),
    ("Standard_D2s_v5", 70.08),
    ("Standard_D4s_v5", 140.16),
    ("Standard_D8s_v5", 280.32),
    ("Standard_D16s_v5", 560.64),
    ("Standard_E4s_v5", 182.50),
    ("Standard_E8s_v5", 365.00),
    ("Standard_F4s_v2", 122.64),
    ("Standard_F8s_v2", 245.28),
]

STORAGE_SKUS = [
    ("Standard_LRS", 0.018),   # per GB
    ("Standard_GRS", 0.036),
    ("Premium_LRS", 0.15),
    ("Standard_ZRS", 0.025),
]

SQL_TIERS = [
    ("Basic", 4.90),
    ("Standard_S0", 14.72),
    ("Standard_S1", 29.43),
    ("Standard_S2", 73.58),
    ("Standard_S3", 147.15),
    ("Premium_P1", 465.00),
    ("Premium_P2", 930.00),
    ("BusinessCritical_BC_Gen5_2", 720.90),
]

APP_SERVICE_TIERS = [
    ("Free_F1", 0.00),
    ("Basic_B1", 54.75),
    ("Basic_B2", 109.50),
    ("Standard_S1", 73.00),
    ("Standard_S2", 146.00),
    ("Premium_P1v3", 138.70),
    ("Premium_P2v3", 277.40),
]

NETWORKING_TYPES = [
    ("VNet_Gateway_VpnGw1", 140.16),
    ("VNet_Gateway_VpnGw2", 361.35),
    ("Application_Gateway_Standard_v2", 219.00),
    ("Load_Balancer_Standard", 21.90),
    ("Azure_Firewall_Standard", 912.50),
    ("Public_IP_Standard", 3.65),
    ("ExpressRoute_Standard_Metered", 438.00),
]

# ---------------------------------------------------------------------------
# AWS Constants & lookup tables
# ---------------------------------------------------------------------------

AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1",
]

EC2_INSTANCE_TYPES = [
    ("t3.micro", 7.50),
    ("t3.small", 15.00),
    ("t3.medium", 30.00),
    ("t3.large", 60.00),
    ("m5.large", 69.35),
    ("m5.xlarge", 138.70),
    ("m5.2xlarge", 277.40),
    ("c5.large", 61.32),
    ("c5.xlarge", 122.64),
    ("r5.large", 90.66),
    ("r5.xlarge", 181.32),
]

S3_STORAGE_CLASSES = [
    ("STANDARD", 0.023),  # per GB
    ("INTELLIGENT_TIERING", 0.023),
    ("STANDARD_IA", 0.0125),
    ("GLACIER", 0.004),
]

RDS_INSTANCE_CLASSES = [
    ("db.t3.micro", 11.02),
    ("db.t3.small", 22.04),
    ("db.t3.medium", 44.08),
    ("db.r5.large", 146.00),
    ("db.r5.xlarge", 292.00),
    ("db.m5.large", 124.10),
    ("db.m5.xlarge", 248.20),
]

LAMBDA_PRICING = {
    "per_request": 0.20 / 1_000_000,  # $0.20 per 1M requests
    "per_gb_second": 0.0000166667,     # $0.0000166667 per GB-second
}

# ---------------------------------------------------------------------------
# Provisioning Entities (Top-level hierarchy)
# ---------------------------------------------------------------------------

PROVISIONING_ENTITIES = [
    {
        "id": 1,
        "name": "NTT DATA Italia S.p.A",
    },
    {
        "id": 2,
        "name": "NTT Data Spain s.l.u.",
    },
]

# ---------------------------------------------------------------------------
# Organizations (Middle-level hierarchy)
# ---------------------------------------------------------------------------

ORGANIZATIONS = [
    # Organizations under NTT DATA Italia S.p.A (Provisioning Entity 1)
    {
        "id": "74f7f528-3000-zenSOC",
        "name": "zenSOC - Global SOC",
        "provisioning_entity_id": 1,
    },
    {
        "id": "a3db800f-8d6d-zenSOC",
        "name": "zenSOC - Infrastructure and Applications",
        "provisioning_entity_id": 1,
    },
    {
        "id": "ff005a24-0da4-NTT-DATA-ITALIA-1",
        "name": "NTT DATA ITALIA - Production",
        "provisioning_entity_id": 1,
    },
    {
        "id": "ff005a24-0da4-NTT-DATA-ITALIA-2",
        "name": "NTT DATA ITALIA - Development",
        "provisioning_entity_id": 1,
    },
    # Organizations under NTT Data Spain s.l.u. (Provisioning Entity 2)
    {
        "id": "180f8f4e-bbca-Firewall",
        "name": "Firewall",
        "provisioning_entity_id": 2,
    },
    {
        "id": "1a6cb836-7aeb-ManagementCnS",
        "name": "ManagementCnS",
        "provisioning_entity_id": 2,
    },
    {
        "id": "65fc09f1-00d9-BigContent-1",
        "name": "Big Content - Development",
        "provisioning_entity_id": 2,
    },
    {
        "id": "65fc09f1-00d9-BigContent-2",
        "name": "Big Content - Production",
        "provisioning_entity_id": 2,
    },
    {
        "id": "9324 02f6-f39e-Clonika",
        "name": "Clonika",
        "provisioning_entity_id": 2,
    },
    {
        "id": "99dc4afe-7b81-Knowler-1",
        "name": "Knowler - Cloud Infrastructure",
        "provisioning_entity_id": 2,
    },
    {
        "id": "99dc4afe-7b81-Knowler-2",
        "name": "Knowler - Application Services",
        "provisioning_entity_id": 2,
    },
    {
        "id": "fcbd932d-d8e6-Orkestra-1",
        "name": "Orkestra - West Europe",
        "provisioning_entity_id": 2,
    },
    {
        "id": "fcbd932d-d8e6-Orkestra-2",
        "name": "Orkestra - LATAM",
        "provisioning_entity_id": 2,
    },
    {
        "id": "fe6a2f79-00b4-Everilion-1",
        "name": "Everilion - EU Region",
        "provisioning_entity_id": 2,
    },
    {
        "id": "fe6a2f79-00b4-Everilion-2",
        "name": "Everilion - US Region",
        "provisioning_entity_id": 2,
    },
]

# ---------------------------------------------------------------------------
# Subscription/Account profiles (Azure + AWS)
# ---------------------------------------------------------------------------

SUBSCRIPTION_PROFILES: list[dict[str, Any]] = [
    # Azure Subscriptions under NTT DATA Italia S.p.A
    {
        "id": "6bee0f3a-1982-4ab8-ccf36e96-9df9-43b5",
        "name": "zenSOC - Global SOC",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "platform-team@nttdata.com",
        "monthly_budget": 15000.00,
        "target_spend": 12500.00,
        "health_score": 78,
        "resource_range": (10, 15),
        "anomaly_chance": 0.20,
        "spike_count": 2,
        "organization_id": "74f7f528-3000-zenSOC",
        "provisioning_entity_id": 1,
    },
    {
        "id": "ccf36e96-9df9-43b5-a-0c096db-b5d7-46d3",
        "name": "zenSOC - Shared SIEM",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "platform-team@nttdata.com",
        "monthly_budget": 18000.00,
        "target_spend": 14200.00,
        "health_score": 82,
        "resource_range": (12, 18),
        "anomaly_chance": 0.15,
        "spike_count": 2,
        "organization_id": "a3db800f-8d6d-zenSOC",
        "provisioning_entity_id": 1,
    },
    {
        "id": "0c096ddb-b5d7-46d3-sub-robocop-prod-001",
        "name": "sub-robocop-prod-001",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "robocop-team@nttdata.com",
        "monthly_budget": 8000.00,
        "target_spend": 6800.00,
        "health_score": 65,
        "resource_range": (8, 12),
        "anomaly_chance": 0.25,
        "spike_count": 3,
        "organization_id": "ff005a24-0da4-NTT-DATA-ITALIA-1",
        "provisioning_entity_id": 1,
    },
    {
        "id": "12591e3f-639e-4db5-sub-urbanvision-dev-001",
        "name": "sub-urbanvision-dev-001",
        "provider": "azure",
        "environment": "development",
        "region": "westeurope",
        "owner": "urbanvision-team@nttdata.com",
        "monthly_budget": 4500.00,
        "target_spend": 3200.00,
        "health_score": 58,
        "resource_range": (5, 8),
        "anomaly_chance": 0.30,
        "spike_count": 2,
        "organization_id": "ff005a24-0da4-NTT-DATA-ITALIA-2",
        "provisioning_entity_id": 1,
    },
    # Azure Subscriptions under NTT Data Spain s.l.u.
    {
        "id": "b9ad9b2b-5054-437d-Adriano-Azure",
        "name": "Adriano Azure",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "firewall-team@nttdata.com",
        "monthly_budget": 5000.00,
        "target_spend": 4100.00,
        "health_score": 72,
        "resource_range": (6, 10),
        "anomaly_chance": 0.18,
        "spike_count": 2,
        "organization_id": "180f8f4e-bbca-Firewall",
        "provisioning_entity_id": 2,
    },
    {
        "id": "51a77d98-28b1-4ded-NTT-Cns-PSZ",
        "name": "NTT Cns PSZ",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "managementcns-team@nttdata.com",
        "monthly_budget": 9000.00,
        "target_spend": 7500.00,
        "health_score": 68,
        "resource_range": (8, 13),
        "anomaly_chance": 0.22,
        "spike_count": 2,
        "organization_id": "1a6cb836-7aeb-ManagementCnS",
        "provisioning_entity_id": 2,
    },
    {
        "id": "0c177963-9811-4462-Dev-BigContent-1014108",
        "name": "Dev_BigContent #1014108",
        "provider": "azure",
        "environment": "development",
        "region": "westeurope",
        "owner": "bigcontent-team@nttdata.com",
        "monthly_budget": 6500.00,
        "target_spend": 5200.00,
        "health_score": 61,
        "resource_range": (7, 11),
        "anomaly_chance": 0.28,
        "spike_count": 3,
        "organization_id": "65fc09f1-00d9-BigContent-1",
        "provisioning_entity_id": 2,
    },
    {
        "id": "de473ac2-ec59-45e9-GNF-AZURE",
        "name": "GNF -AZURE",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "gnf-team@nttdata.com",
        "monthly_budget": 7200.00,
        "target_spend": 6100.00,
        "health_score": 74,
        "resource_range": (8, 12),
        "anomaly_chance": 0.19,
        "spike_count": 2,
        "organization_id": "65fc09f1-00d9-BigContent-2",
        "provisioning_entity_id": 2,
    },
    {
        "id": "7285aa8b-d8bb-467a-blueprism-1014421",
        "name": "blueprism #1014421",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "clonika-team@nttdata.com",
        "monthly_budget": 5500.00,
        "target_spend": 4600.00,
        "health_score": 70,
        "resource_range": (6, 9),
        "anomaly_chance": 0.20,
        "spike_count": 2,
        "organization_id": "9324 02f6-f39e-Clonika",
        "provisioning_entity_id": 2,
    },
    {
        "id": "3fa81b66-6b4d-44c8-Microsoft-Azure-skmntt-1016881",
        "name": "Microsoft Azure (skmntt): #1016881",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "knowler-team@nttdata.com",
        "monthly_budget": 11000.00,
        "target_spend": 9200.00,
        "health_score": 76,
        "resource_range": (10, 14),
        "anomaly_chance": 0.17,
        "spike_count": 2,
        "organization_id": "99dc4afe-7b81-Knowler-1",
        "provisioning_entity_id": 2,
    },
    {
        "id": "7273044b-59da-412a-knowler-1022996",
        "name": "knowler #1022996",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "knowler-team@nttdata.com",
        "monthly_budget": 8500.00,
        "target_spend": 7100.00,
        "health_score": 69,
        "resource_range": (8, 12),
        "anomaly_chance": 0.23,
        "spike_count": 2,
        "organization_id": "99dc4afe-7b81-Knowler-2",
        "provisioning_entity_id": 2,
    },
    {
        "id": "7b28091d-c2a9-491d-eAsset-WE",
        "name": "eAsset.WE",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "orkestra-team@nttdata.com",
        "monthly_budget": 6800.00,
        "target_spend": 5700.00,
        "health_score": 73,
        "resource_range": (7, 11),
        "anomaly_chance": 0.21,
        "spike_count": 2,
        "organization_id": "fcbd932d-d8e6-Orkestra-1",
        "provisioning_entity_id": 2,
    },
    {
        "id": "8af942cc-6491-4270-eAsset-LATAM",
        "name": "eAsset.LATAM",
        "provider": "azure",
        "environment": "production",
        "region": "brazilsouth",
        "owner": "orkestra-latam-team@nttdata.com",
        "monthly_budget": 7500.00,
        "target_spend": 6300.00,
        "health_score": 67,
        "resource_range": (8, 12),
        "anomaly_chance": 0.24,
        "spike_count": 3,
        "organization_id": "fcbd932d-d8e6-Orkestra-2",
        "provisioning_entity_id": 2,
    },
    {
        "id": "297e386b-62dd-4507-everSaaS-EUpro01",
        "name": "everSaaS- EUpro01",
        "provider": "azure",
        "environment": "production",
        "region": "westeurope",
        "owner": "everilion-team@nttdata.com",
        "monthly_budget": 9500.00,
        "target_spend": 7800.00,
        "health_score": 80,
        "resource_range": (9, 13),
        "anomaly_chance": 0.16,
        "spike_count": 2,
        "organization_id": "fe6a2f79-00b4-Everilion-1",
        "provisioning_entity_id": 2,
    },
    {
        "id": "3578a8e9-477d-470e-everSaaS-USpro01",
        "name": "everSaaS- USpro01",
        "provider": "azure",
        "environment": "production",
        "region": "eastus",
        "owner": "everilion-us-team@nttdata.com",
        "monthly_budget": 10500.00,
        "target_spend": 8900.00,
        "health_score": 75,
        "resource_range": (10, 14),
        "anomaly_chance": 0.18,
        "spike_count": 2,
        "organization_id": "fe6a2f79-00b4-Everilion-2",
        "provisioning_entity_id": 2,
    },
    # AWS Accounts (Simple structure - no provisioning entity/organization hierarchy)
    {
        "id": "aws-123456789012",
        "name": "AWS Production - US East",
        "provider": "aws",
        "environment": "production",
        "region": "us-east-1",
        "owner": "cloudops@techinnovate.com",
        "monthly_budget": 14000.00,
        "target_spend": 11250.00,
        "health_score": 68,
        "resource_range": (10, 14),
        "anomaly_chance": 0.22,
        "spike_count": 3,
    },
    {
        "id": "aws-123456789013",
        "name": "AWS Production - US West",
        "provider": "aws",
        "environment": "production",
        "region": "us-west-2",
        "owner": "cloudops@techinnovate.com",
        "monthly_budget": 9500.00,
        "target_spend": 7920.00,
        "health_score": 75,
        "resource_range": (8, 12),
        "anomaly_chance": 0.15,
        "spike_count": 2,
    },
    {
        "id": "aws-123456789014",
        "name": "AWS Development - East",
        "provider": "aws",
        "environment": "development",
        "region": "us-east-1",
        "owner": "dev-team@techinnovate.com",
        "monthly_budget": 5500.00,
        "target_spend": 4180.00,
        "health_score": 61,
        "resource_range": (6, 9),
        "anomaly_chance": 0.28,
        "spike_count": 2,
    },
    {
        "id": "aws-987654321001",
        "name": "AWS Production - EU West",
        "provider": "aws",
        "environment": "production",
        "region": "eu-west-1",
        "owner": "eu-platform@globaltech.io",
        "monthly_budget": 12000.00,
        "target_spend": 9850.00,
        "health_score": 72,
        "resource_range": (9, 13),
        "anomaly_chance": 0.19,
        "spike_count": 2,
    },
    {
        "id": "aws-987654321002",
        "name": "AWS Staging - US",
        "provider": "aws",
        "environment": "staging",
        "region": "us-west-1",
        "owner": "qa-team@techinnovate.com",
        "monthly_budget": 6800.00,
        "target_spend": 5320.00,
        "health_score": 64,
        "resource_range": (7, 10),
        "anomaly_chance": 0.24,
        "spike_count": 2,
    },
    {
        "id": "aws-555666777888",
        "name": "AWS Analytics - Data Lake",
        "provider": "aws",
        "environment": "production",
        "region": "us-east-2",
        "owner": "data-team@techinnovate.com",
        "monthly_budget": 18000.00,
        "target_spend": 15200.00,
        "health_score": 70,
        "resource_range": (11, 15),
        "anomaly_chance": 0.20,
        "spike_count": 3,
    },
]

# ---------------------------------------------------------------------------
# Demo users
# ---------------------------------------------------------------------------

DEMO_USERS = [
    {
        "id": "user-001",
        "username": "rajeshk.srivastava@global.ntt",
        "password_hash": hashlib.sha256(b"Raj@777037").hexdigest(),
        "password_plain": "Raj@777037",
        "display_name": "Azure Admin",
        "email": "admin@techinnovate.us",
        "role": "admin",
    },
    {
        "id": "user-002",
        "username": "cloudops",
        "password_hash": hashlib.sha256(b"cloudops123").hexdigest(),
        "password_plain": "cloudops123",
        "display_name": "Cloud Operations",
        "email": "cloudops@techinnovate.us",
        "role": "cloudops",
    },
    {
        "id": "user-003",
        "username": "finance",
        "password_hash": hashlib.sha256(b"finance123").hexdigest(),
        "password_plain": "finance123",
        "display_name": "Finance Analyst",
        "email": "finance@techinnovate.us",
        "role": "finance",
    },
]

# ---------------------------------------------------------------------------
# Deterministic UUID helper (seeded from name so output is stable)
# ---------------------------------------------------------------------------

def _stable_uuid(name: str) -> str:
    """Return a UUID-like string derived deterministically from *name*."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))


# ---------------------------------------------------------------------------
# Resource generators (one per resource type)
# ---------------------------------------------------------------------------

def _generate_vm(sub_id: str, index: int, region: str, environment: str) -> dict:
    sku_name, base_price = _RNG.choice(VM_SKUS)
    # Dev/staging VMs tend to be smaller
    if environment in ("development", "staging"):
        sku_name, base_price = _RNG.choice(VM_SKUS[:5])

    name = f"vm-{sub_id}-{index:03d}"
    monthly_cost = round(base_price * _RNG.uniform(0.85, 1.15), 2)

    # Usage patterns vary by environment
    if environment == "production":
        cpu = round(_RNG.uniform(25.0, 85.0), 1)
        mem = round(_RNG.uniform(30.0, 90.0), 1)
    elif environment == "development":
        # Over-provisioned: low usage on potentially large SKUs
        cpu = round(_RNG.uniform(3.0, 25.0), 1)
        mem = round(_RNG.uniform(8.0, 35.0), 1)
    else:
        cpu = round(_RNG.uniform(10.0, 50.0), 1)
        mem = round(_RNG.uniform(15.0, 55.0), 1)

    return {
        "id": _stable_uuid(f"{sub_id}-vm-{index}"),
        "name": name,
        "type": "Virtual Machine",
        "provider_type": "Microsoft.Compute/virtualMachines",
        "sku": sku_name,
        "tier": sku_name.split("_")[1] if "_" in sku_name else sku_name,
        "region": region,
        "monthly_cost": monthly_cost,
        "cpu_usage_pct": cpu,
        "memory_usage_pct": mem,
        "is_active": _RNG.random() > 0.05,
        "tags": {
            "environment": environment,
            "managed_by": "terraform",
        },
    }


def _generate_storage(sub_id: str, index: int, region: str, environment: str) -> dict:
    sku_name, price_per_gb = _RNG.choice(STORAGE_SKUS)
    # Data-Analytics sub gets large storage
    if sub_id == "sub-005":
        storage_gb = _RNG.randint(5000, 50000)
    elif environment == "production":
        storage_gb = _RNG.randint(500, 10000)
    else:
        storage_gb = _RNG.randint(50, 2000)

    monthly_cost = round(price_per_gb * storage_gb, 2)
    name = f"stor{sub_id.replace('-', '')}{index:03d}"

    return {
        "id": _stable_uuid(f"{sub_id}-storage-{index}"),
        "name": name,
        "type": "Storage Account",
        "provider_type": "Microsoft.Storage/storageAccounts",
        "sku": sku_name,
        "tier": sku_name.split("_")[0],
        "region": region,
        "monthly_cost": monthly_cost,
        "storage_gb": storage_gb,
        "cpu_usage_pct": 0.0,
        "memory_usage_pct": 0.0,
        "is_active": True,
        "tags": {
            "environment": environment,
            "data_classification": "internal",
        },
    }


def _generate_sql(sub_id: str, index: int, region: str, environment: str) -> dict:
    if environment == "production":
        tier_name, base_price = _RNG.choice(SQL_TIERS[3:])
    elif environment == "development":
        tier_name, base_price = _RNG.choice(SQL_TIERS[:3])
    else:
        tier_name, base_price = _RNG.choice(SQL_TIERS[1:5])

    monthly_cost = round(base_price * _RNG.uniform(0.90, 1.10), 2)
    name = f"sqldb-{sub_id}-{index:03d}"

    cpu = round(_RNG.uniform(10.0, 75.0), 1) if environment == "production" else round(_RNG.uniform(2.0, 30.0), 1)
    mem = round(_RNG.uniform(20.0, 80.0), 1) if environment == "production" else round(_RNG.uniform(5.0, 40.0), 1)

    return {
        "id": _stable_uuid(f"{sub_id}-sql-{index}"),
        "name": name,
        "type": "SQL Database",
        "provider_type": "Microsoft.Sql/servers/databases",
        "sku": tier_name,
        "tier": tier_name.split("_")[0],
        "region": region,
        "monthly_cost": monthly_cost,
        "cpu_usage_pct": cpu,
        "memory_usage_pct": mem,
        "is_active": True,
        "tags": {
            "environment": environment,
        },
    }


def _generate_app_service(sub_id: str, index: int, region: str, environment: str) -> dict:
    if environment == "production":
        tier_name, base_price = _RNG.choice(APP_SERVICE_TIERS[3:])
    elif environment == "development":
        tier_name, base_price = _RNG.choice(APP_SERVICE_TIERS[:4])
    else:
        tier_name, base_price = _RNG.choice(APP_SERVICE_TIERS[1:5])

    monthly_cost = round(base_price * _RNG.uniform(0.90, 1.15), 2)
    name = f"app-{sub_id}-{index:03d}"

    cpu = round(_RNG.uniform(15.0, 70.0), 1)
    mem = round(_RNG.uniform(20.0, 75.0), 1)

    return {
        "id": _stable_uuid(f"{sub_id}-app-{index}"),
        "name": name,
        "type": "App Service",
        "provider_type": "Microsoft.Web/sites",
        "sku": tier_name,
        "tier": tier_name.split("_")[0],
        "region": region,
        "monthly_cost": monthly_cost,
        "cpu_usage_pct": cpu,
        "memory_usage_pct": mem,
        "is_active": _RNG.random() > 0.03,
        "tags": {
            "environment": environment,
            "framework": _RNG.choice(["dotnet", "python", "node", "java"]),
        },
    }


def _generate_networking(sub_id: str, index: int, region: str, environment: str) -> dict:
    net_name, base_price = _RNG.choice(NETWORKING_TYPES)

    # Smaller networking footprint for non-prod
    if environment in ("development", "staging"):
        net_name, base_price = _RNG.choice(NETWORKING_TYPES[3:6])

    monthly_cost = round(base_price * _RNG.uniform(0.90, 1.10), 2)
    name = f"net-{sub_id}-{index:03d}"

    return {
        "id": _stable_uuid(f"{sub_id}-net-{index}"),
        "name": name,
        "type": "Networking",
        "provider_type": "Microsoft.Network/virtualNetworks",
        "sku": net_name,
        "tier": net_name.split("_")[0],
        "region": region,
        "monthly_cost": monthly_cost,
        "cpu_usage_pct": 0.0,
        "memory_usage_pct": 0.0,
        "is_active": True,
        "tags": {
            "environment": environment,
        },
    }


# Azure resource generators
_RESOURCE_GENERATORS = [
    _generate_vm,
    _generate_storage,
    _generate_sql,
    _generate_app_service,
    _generate_networking,
]


# ---------------------------------------------------------------------------
# AWS Resource Generators
# ---------------------------------------------------------------------------

def _generate_ec2(account_id: str, index: int, region: str, environment: str) -> dict:
    """Generate an AWS EC2 instance."""
    instance_type, base_price = _RNG.choice(EC2_INSTANCE_TYPES)

    # Dev/staging instances tend to be smaller
    if environment in ("development", "staging"):
        instance_type, base_price = _RNG.choice(EC2_INSTANCE_TYPES[:6])

    name = f"ec2-{account_id.split('-')[-1]}-{index:03d}"
    monthly_cost = round(base_price * _RNG.uniform(0.85, 1.15), 2)

    # Usage patterns vary by environment
    if environment == "production":
        cpu = round(_RNG.uniform(20.0, 80.0), 1)
        mem = round(_RNG.uniform(25.0, 85.0), 1)
    elif environment == "development":
        # Over-provisioned: low usage
        cpu = round(_RNG.uniform(5.0, 20.0), 1)
        mem = round(_RNG.uniform(10.0, 30.0), 1)
    else:
        cpu = round(_RNG.uniform(15.0, 55.0), 1)
        mem = round(_RNG.uniform(20.0, 60.0), 1)

    return {
        "id": _stable_uuid(f"{account_id}-ec2-{index}"),
        "name": name,
        "type": "EC2 Instance",
        "provider_type": "AWS::EC2::Instance",
        "sku": instance_type,
        "tier": instance_type.split(".")[0],
        "region": region,
        "monthly_cost": monthly_cost,
        "cpu_usage_pct": cpu,
        "memory_usage_pct": mem,
        "is_active": _RNG.random() > 0.05,
        "tags": {
            "environment": environment,
            "managed_by": "terraform",
        },
    }


def _generate_s3(account_id: str, index: int, region: str, environment: str) -> dict:
    """Generate an AWS S3 bucket."""
    storage_class, price_per_gb = _RNG.choice(S3_STORAGE_CLASSES)

    # Production gets larger buckets
    if environment == "production":
        storage_gb = _RNG.randint(1000, 20000)
    else:
        storage_gb = _RNG.randint(100, 5000)

    monthly_cost = round(price_per_gb * storage_gb, 2)
    # Add request costs
    requests = _RNG.randint(10000, 1000000)
    request_cost = round((requests / 1000) * 0.0004, 2)
    monthly_cost += request_cost

    name = f"s3-bucket-{account_id.split('-')[-1]}-{index:03d}"

    return {
        "id": _stable_uuid(f"{account_id}-s3-{index}"),
        "name": name,
        "type": "S3 Bucket",
        "provider_type": "AWS::S3::Bucket",
        "sku": storage_class,
        "tier": storage_class.split("_")[0],
        "region": region,
        "monthly_cost": monthly_cost,
        "storage_gb": storage_gb,
        "cpu_usage_pct": 0.0,
        "memory_usage_pct": 0.0,
        "is_active": True,
        "tags": {
            "environment": environment,
            "purpose": _RNG.choice(["backups", "logs", "assets", "data-lake"]),
        },
    }


def _generate_rds(account_id: str, index: int, region: str, environment: str) -> dict:
    """Generate an AWS RDS database instance."""
    if environment == "production":
        instance_class, base_price = _RNG.choice(RDS_INSTANCE_CLASSES[4:])
    elif environment == "development":
        instance_class, base_price = _RNG.choice(RDS_INSTANCE_CLASSES[:3])
    else:
        instance_class, base_price = _RNG.choice(RDS_INSTANCE_CLASSES[2:5])

    monthly_cost = round(base_price * _RNG.uniform(0.90, 1.10), 2)

    # Multi-AZ doubles the cost for production
    multi_az = environment == "production" and _RNG.random() > 0.3
    if multi_az:
        monthly_cost = round(monthly_cost * 2.0, 2)

    name = f"rds-{account_id.split('-')[-1]}-{index:03d}"

    cpu = round(_RNG.uniform(15.0, 70.0), 1) if environment == "production" else round(_RNG.uniform(5.0, 35.0), 1)
    mem = round(_RNG.uniform(25.0, 75.0), 1) if environment == "production" else round(_RNG.uniform(10.0, 45.0), 1)

    return {
        "id": _stable_uuid(f"{account_id}-rds-{index}"),
        "name": name,
        "type": "RDS Database",
        "provider_type": "AWS::RDS::DBInstance",
        "sku": instance_class,
        "tier": instance_class.split(".")[1] if "." in instance_class else instance_class,
        "region": region,
        "monthly_cost": monthly_cost,
        "cpu_usage_pct": cpu,
        "memory_usage_pct": mem,
        "is_active": True,
        "multi_az": multi_az,
        "tags": {
            "environment": environment,
            "engine": _RNG.choice(["postgres", "mysql", "aurora-postgresql"]),
        },
    }


def _generate_lambda(account_id: str, index: int, region: str, environment: str) -> dict:
    """Generate an AWS Lambda function."""
    invocations = _RNG.randint(50000, 2000000)
    memory_mb = _RNG.choice([128, 256, 512, 1024, 2048])
    avg_duration_ms = _RNG.uniform(100, 3000)

    # Calculate cost: requests + compute (GB-seconds)
    request_cost = invocations * LAMBDA_PRICING["per_request"]
    gb_seconds = (invocations * avg_duration_ms / 1000) * (memory_mb / 1024)
    compute_cost = gb_seconds * LAMBDA_PRICING["per_gb_second"]
    monthly_cost = round(request_cost + compute_cost, 2)

    name = f"lambda-{account_id.split('-')[-1]}-{index:03d}"

    return {
        "id": _stable_uuid(f"{account_id}-lambda-{index}"),
        "name": name,
        "type": "Lambda Function",
        "provider_type": "AWS::Lambda::Function",
        "sku": f"{memory_mb}MB",
        "tier": "Serverless",
        "region": region,
        "monthly_cost": monthly_cost,
        "invocations": invocations,
        "cpu_usage_pct": 0.0,
        "memory_usage_pct": 0.0,
        "is_active": True,
        "tags": {
            "environment": environment,
            "runtime": _RNG.choice(["python3.11", "nodejs18.x", "java11"]),
        },
    }


def _generate_ebs(account_id: str, index: int, region: str, environment: str) -> dict:
    """Generate an AWS EBS volume (some orphaned)."""
    volume_type = _RNG.choice(["gp3", "gp2", "io2"])
    size_gb = _RNG.randint(50, 500)

    # Pricing varies by type
    price_per_gb = 0.08 if volume_type == "gp3" else 0.10
    monthly_cost = round(size_gb * price_per_gb, 2)

    # Some EBS volumes are orphaned (not attached)
    is_orphaned = _RNG.random() < 0.15

    name = f"ebs-{account_id.split('-')[-1]}-{index:03d}"
    if is_orphaned:
        name = f"ebs-orphaned-{index:03d}"

    return {
        "id": _stable_uuid(f"{account_id}-ebs-{index}"),
        "name": name,
        "type": "EBS Volume",
        "provider_type": "AWS::EC2::Volume",
        "sku": volume_type,
        "tier": volume_type,
        "region": region,
        "monthly_cost": monthly_cost,
        "storage_gb": size_gb,
        "cpu_usage_pct": 0.0,
        "memory_usage_pct": 0.0,
        "is_active": not is_orphaned,
        "attached": not is_orphaned,
        "tags": {
            "environment": environment,
            "orphaned": str(is_orphaned).lower(),
        },
    }


# AWS resource generators
_AWS_RESOURCE_GENERATORS = [
    _generate_ec2,
    _generate_s3,
    _generate_rds,
    _generate_lambda,
    _generate_ebs,
]


# ---------------------------------------------------------------------------
# Resource allocation per subscription
# ---------------------------------------------------------------------------

def _generate_resources_for_subscription(profile: dict) -> list[dict]:
    """Generate a realistic set of resources for a single subscription/account."""
    sub_id = profile["id"]
    region = profile["region"]
    env = profile["environment"]
    provider = profile.get("provider", "azure")
    lo, hi = profile["resource_range"]
    resource_count = _RNG.randint(lo, hi)

    # Choose resource generators based on provider
    if provider == "aws":
        generators = _AWS_RESOURCE_GENERATORS
        regions_list = AWS_REGIONS
    else:  # azure
        generators = _RESOURCE_GENERATORS
        regions_list = AZURE_REGIONS

    resources: list[dict] = []
    # Ensure at least one of each type, then fill the rest randomly
    guaranteed_types = list(generators)
    _RNG.shuffle(guaranteed_types)

    for i, gen_fn in enumerate(guaranteed_types[:min(resource_count, len(guaranteed_types))]):
        secondary_region = _RNG.choice(regions_list) if _RNG.random() < 0.2 else region
        resources.append(gen_fn(sub_id, i, secondary_region, env))

    remaining = resource_count - len(resources)
    for j in range(remaining):
        idx = len(resources)
        gen_fn = _RNG.choice(generators)
        secondary_region = _RNG.choice(regions_list) if _RNG.random() < 0.2 else region
        resources.append(gen_fn(sub_id, idx, secondary_region, env))

    # For sub-005 (Azure Data-Analytics), bias towards extra storage resources
    if sub_id == "sub-005":
        extra_storage = _RNG.randint(1, 3)
        for k in range(extra_storage):
            idx = len(resources)
            resources.append(_generate_storage(sub_id, idx, region, env))

    # For AWS production accounts, add extra Lambda functions (serverless-heavy)
    if provider == "aws" and env == "production":
        extra_lambda = _RNG.randint(2, 4)
        for k in range(extra_lambda):
            idx = len(resources)
            resources.append(_generate_lambda(sub_id, idx, region, env))

    # Scale resource costs so total roughly matches the target monthly spend
    raw_total = sum(r["monthly_cost"] for r in resources)
    if raw_total > 0:
        scale_factor = profile["target_spend"] / raw_total
        for r in resources:
            r["monthly_cost"] = round(r["monthly_cost"] * scale_factor, 2)

    return resources


# ---------------------------------------------------------------------------
# Daily cost history generator
# ---------------------------------------------------------------------------

def _generate_cost_history(
    profile: dict,
    days: int = 180,
) -> list[dict]:
    """
    Generate *days* worth of daily cost records for one subscription.

    Patterns applied:
    - Base daily cost derived from target monthly spend / 30.
    - Weekday multiplier ~1.05, weekend ~0.88.
    - Gradual monthly growth of 2-5 %.
    - Random spike events scattered across the window.
    - Small daily noise +/- 6 %.
    """
    target_daily = profile["target_spend"] / 30.0
    monthly_growth_rate = _RNG.uniform(0.02, 0.05)
    daily_growth = (1 + monthly_growth_rate) ** (1 / 30) - 1

    # Pre-select spike days
    spike_days: set[int] = set()
    spike_count = profile.get("spike_count", 2)
    while len(spike_days) < spike_count:
        spike_days.add(_RNG.randint(10, days - 5))

    end_date = datetime(2026, 1, 31)
    start_date = end_date - timedelta(days=days - 1)

    history: list[dict] = []
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        day_of_week = current_date.weekday()  # 0=Mon .. 6=Sun

        # Growth multiplier
        growth_mult = (1 + daily_growth) ** day_offset

        # Weekday / weekend pattern
        if day_of_week < 5:
            weekday_mult = _RNG.uniform(1.02, 1.08)
        else:
            weekday_mult = _RNG.uniform(0.82, 0.92)

        # Daily noise
        noise = _RNG.uniform(0.94, 1.06)

        # Spike
        spike_mult = 1.0
        if day_offset in spike_days:
            spike_mult = _RNG.uniform(1.35, 1.85)
        # Small residual tail the day after a spike
        elif (day_offset - 1) in spike_days:
            spike_mult = _RNG.uniform(1.08, 1.20)

        daily_cost = target_daily * growth_mult * weekday_mult * noise * spike_mult
        daily_cost = round(daily_cost, 2)

        # Break the daily cost into service categories
        compute_share = _RNG.uniform(0.38, 0.52)
        storage_share = _RNG.uniform(0.10, 0.22)
        database_share = _RNG.uniform(0.10, 0.18)
        networking_share = _RNG.uniform(0.03, 0.08)
        other_share = 1.0 - (compute_share + storage_share + database_share + networking_share)
        if other_share < 0:
            other_share = 0.02

        # For Data-Analytics, storage is larger
        if profile["id"] == "sub-005":
            storage_share += 0.15
            compute_share -= 0.10

        total_shares = compute_share + storage_share + database_share + networking_share + other_share

        history.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "subscription_id": profile["id"],
            "daily_cost": daily_cost,
            "compute_cost": round(daily_cost * (compute_share / total_shares), 2),
            "storage_cost": round(daily_cost * (storage_share / total_shares), 2),
            "database_cost": round(daily_cost * (database_share / total_shares), 2),
            "networking_cost": round(daily_cost * (networking_share / total_shares), 2),
            "other_cost": round(daily_cost * (other_share / total_shares), 2),
            "is_anomaly": day_offset in spike_days,
            "day_of_week": current_date.strftime("%A"),
        })

    return history


# ---------------------------------------------------------------------------
# Subscription dict builder
# ---------------------------------------------------------------------------

def _build_subscription_dict(profile: dict, resources: list[dict]) -> dict:
    """Build the final subscription summary dict."""
    current_spend = round(sum(r["monthly_cost"] for r in resources), 2)
    # Add small jitter so current_spend is not identical to target
    jitter = _RNG.uniform(-0.03, 0.05)
    current_spend = round(current_spend * (1 + jitter), 2)

    # Get organization and provisioning entity info
    organization_id = profile.get("organization_id")
    provisioning_entity_id = profile.get("provisioning_entity_id")

    # Find organization name
    organization_name = None
    if organization_id:
        org = next((o for o in ORGANIZATIONS if o["id"] == organization_id), None)
        if org:
            organization_name = org["name"]

    # Find provisioning entity name
    provisioning_entity_name = None
    if provisioning_entity_id:
        entity = next((e for e in PROVISIONING_ENTITIES if e["id"] == provisioning_entity_id), None)
        if entity:
            provisioning_entity_name = entity["name"]

    return {
        "id": profile["id"],
        "name": profile["name"],
        "provider": profile.get("provider", "azure"),  # Support multi-cloud
        "environment": profile["environment"],
        "region": profile["region"],
        "owner": profile["owner"],
        "monthly_budget": profile["monthly_budget"],
        "current_spend": current_spend,
        "health_score": profile["health_score"],
        "resource_count": len(resources),
        "created_at": "2024-03-15T08:00:00Z",
        "last_assessed": datetime(2026, 1, 31, 12, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currency": "USD",
        "organization_id": organization_id,
        "organization_name": organization_name,
        "provisioning_entity_id": provisioning_entity_id,
        "provisioning_entity_name": provisioning_entity_name,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_all_mock_data() -> dict:
    """
    Generate the complete set of mock Azure cost data.

    Returns a dict with six top-level keys:

    - ``subscriptions``: List of subscription summary dicts.
    - ``resources``:     Dict mapping subscription_id -> list of resource dicts.
    - ``cost_history``:  Dict mapping subscription_id -> list of daily cost records.
    - ``users``:         List of demo user dicts.
    - ``provisioning_entities``: List of provisioning entity dicts.
    - ``organizations``: List of organization dicts.

    The random seed is reset to 42 at the start of every call so the output
    is deterministic regardless of prior state.
    """
    # Reset seed for reproducibility
    _RNG.seed(42)

    subscriptions: list[dict] = []
    resources: dict[str, list[dict]] = {}
    cost_history: dict[str, list[dict]] = {}

    for profile in SUBSCRIPTION_PROFILES:
        sub_resources = _generate_resources_for_subscription(profile)
        resources[profile["id"]] = sub_resources
        subscriptions.append(_build_subscription_dict(profile, sub_resources))
        cost_history[profile["id"]] = _generate_cost_history(profile, days=180)

    return {
        "subscriptions": subscriptions,
        "resources": resources,
        "cost_history": cost_history,
        "users": DEMO_USERS,
        "provisioning_entities": PROVISIONING_ENTITIES,
        "organizations": ORGANIZATIONS,
    }


# ---------------------------------------------------------------------------
# Convenience helpers (used by other modules)
# ---------------------------------------------------------------------------

def get_subscriptions() -> list[dict]:
    """Return only the subscription summaries."""
    return generate_all_mock_data()["subscriptions"]


def get_resources(subscription_id: str) -> list[dict]:
    """Return resources for a given subscription."""
    all_data = generate_all_mock_data()
    return all_data["resources"].get(subscription_id, [])


def get_cost_history(subscription_id: str, days: int = 30) -> list[dict]:
    """Return the last *days* cost history entries for a subscription."""
    all_data = generate_all_mock_data()
    history = all_data["cost_history"].get(subscription_id, [])
    return history[-days:] if days < len(history) else history


def get_users() -> list[dict]:
    """Return the list of demo users."""
    return list(DEMO_USERS)


def authenticate_user(username: str, password: str) -> dict | None:
    """
    Validate credentials against the demo user list.

    Returns the user dict (without password fields) on success, or *None*.
    """
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    for user in DEMO_USERS:
        if user["username"] == username and user["password_hash"] == pw_hash:
            return {
                "id": user["id"],
                "username": user["username"],
                "display_name": user["display_name"],
                "email": user["email"],
                "role": user["role"],
            }
    return None


def get_provisioning_entities() -> list[dict]:
    """Return the list of provisioning entities."""
    return list(PROVISIONING_ENTITIES)


def get_organizations(provisioning_entity_id: int = None) -> list[dict]:
    """Return the list of organizations, optionally filtered by provisioning entity."""
    if provisioning_entity_id is None:
        return list(ORGANIZATIONS)
    return [org for org in ORGANIZATIONS if org["provisioning_entity_id"] == provisioning_entity_id]


# ---------------------------------------------------------------------------
# Quick smoke-test when run directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    data = generate_all_mock_data()

    print("=== Mock Data Summary ===\n")
    print(f"Subscriptions: {len(data['subscriptions'])}")
    for sub in data["subscriptions"]:
        res_count = len(data["resources"][sub["id"]])
        history_len = len(data["cost_history"][sub["id"]])
        total_resource_cost = sum(r["monthly_cost"] for r in data["resources"][sub["id"]])
        print(
            f"  [{sub['id']}] {sub['name']:<20s}  "
            f"health={sub['health_score']:>3d}  "
            f"spend=${sub['current_spend']:>10,.2f}  "
            f"budget=${sub['monthly_budget']:>10,.2f}  "
            f"resources={res_count:<3d}  "
            f"history_days={history_len}"
        )

    print(f"\nDemo Users: {len(data['users'])}")
    for u in data["users"]:
        print(f"  {u['username']:<12s} role={u['role']:<10s} ({u['email']})")

    # Show a sample of cost history for the first subscription
    first_sub_id = data["subscriptions"][0]["id"]
    history = data["cost_history"][first_sub_id]
    print(f"\nCost History Sample (first 5 days) for {first_sub_id}:")
    for record in history[:5]:
        print(
            f"  {record['date']}  {record['day_of_week']:<10s}  "
            f"total=${record['total_cost']:>8,.2f}  "
            f"compute=${record['compute_cost']:>8,.2f}  "
            f"anomaly={record['is_anomaly']}"
        )

    # Verify reproducibility
    data2 = generate_all_mock_data()
    assert data["subscriptions"] == data2["subscriptions"], "Reproducibility check failed!"
    print("\nReproducibility check: PASSED")
