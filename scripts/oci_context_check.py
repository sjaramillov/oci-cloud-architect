#!/usr/bin/env python3
"""Print non-secret OCI context readiness for agent/operator use."""

from __future__ import annotations

import os
from pathlib import Path


ENV_NAMES = [
    "OCI_CONFIG_FILE",
    "OCI_PROFILE",
    "OCI_REGION",
    "MYAPP_OCI_AUTH_MODE",
    "MYAPP_OCI_REGION",
    "MYAPP_OCI_COMPARTMENT_OCID",
    "MYAPP_GENAI_MODEL_ID",
    "MYAPP_TAXONOMY_MCP_SERVICE_AUTHORIZATION",
]

SECRET_HINTS = ("KEY", "TOKEN", "PASSWORD", "SECRET", "AUTHORIZATION")


def mask(value: str) -> str:
    if not value:
        return "<unset>"
    if len(value) <= 12:
        return "<set>"
    return f"{value[:8]}...{value[-4:]}"


def should_mask(name: str) -> bool:
    return any(hint in name.upper() for hint in SECRET_HINTS)


def main() -> int:
    print("OCI context check (non-secret)")
    print("=" * 32)
    for name in ENV_NAMES:
        value = os.getenv(name, "")
        rendered = "<set>" if value and should_mask(name) else mask(value)
        print(f"{name}={rendered}")

    config_file = Path(os.getenv("OCI_CONFIG_FILE", "~/.oci/config")).expanduser()
    print(f"oci_config_file_exists={config_file.exists()}")
    if config_file.exists():
        print(f"oci_config_file_path={config_file}")

    print("\nRecommended next checks:")
    print("- oci iam region list --auth instance_principal")
    print("- oci secrets secret-bundle get --secret-id <secret_ocid> --auth instance_principal")
    print("- oci generative-ai model-collection list-models --compartment-id <compartment_ocid> --capability CHAT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
