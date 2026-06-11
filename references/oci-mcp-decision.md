# OCI MCP Decision Reference

Load this when the user asks whether to create or use an MCP for OCI resource
management.

## Decision

Do not create an OCI MCP just because OCI CLI exists. Use OCI CLI and Terraform
for most operations. Create or install an OCI MCP only when at least one is
true:

- The workflow needs repeated stateful read/write OCI operations across turns.
- The agent must expose constrained tools to subagents without giving broad CLI
  access.
- The user wants a governed internal tool boundary with audit logs.
- Operations need typed tool contracts, not ad hoc shell commands.

## Required MCP Guardrails

- Read-only tools first: compartments, instances, load balancers, vault secrets
  metadata, policies, work requests, budgets.
- Write tools must require explicit user approval and resource-specific input.
- No tool may return secret values, private keys, wallet contents, or tokens.
- Auth should use instance principal/resource principal where hosted in OCI.
- Every tool response should include request IDs or work request IDs.
- Provide dry-run or plan mode before live mutation.
- Keep destructive operations unavailable unless a separate break-glass tool is
  explicitly installed and approved.

## Minimal OCI MCP Tool Set

- `oci_identity_list_compartments`
- `oci_compute_get_instance`
- `oci_compute_list_instances`
- `oci_network_get_load_balancer`
- `oci_vault_list_secrets_metadata`
- `oci_vault_get_secret_metadata`
- `oci_iam_list_policies`
- `oci_genai_list_models`
- `oci_work_request_get`

## When Implementing

- Prefer a separate repo or plugin/MCP package over embedding in product code.
- Use the official OCI SDK.
- Expose only allowlisted compartments/regions by configuration.
- Add unit tests that prove secret payloads are never returned.
- Add contract tests for least-privilege failure modes.
