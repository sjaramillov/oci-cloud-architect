# oci-cloud-architect

> A drop-in **OCI Cloud Architect** skill for your AI harness — secure, least-privilege, cost-aware Oracle Cloud Infrastructure design, review and operations.

Give this repo to Codex, Claude, or Cursor and your agent acts as a senior OCI architect: it designs and reviews architectures, writes IAM policies and Terraform, inspects your tenancy through the OCI CLI, and decides when an OCI MCP integration is actually warranted — all with **human-in-the-loop guardrails** so nothing destructive runs without your approval.

**Works with:** Codex · Claude · Cursor — any harness that loads a repo or skill as context.

---

## What it does

A senior OCI architect-and-operator advisor covering:

- **Identity & governance** — compartments, IAM policies, dynamic groups, instance principals, Vault & KMS.
- **Networking** — VCNs, public/private subnets, gateways, route tables, security lists/NSGs, Bastion, Load Balancers.
- **Compute & data** — Compute shapes, Docker Compose hosts, Autonomous Database, wallets, Object Storage.
- **AI & ops** — OCI Generative AI, monitoring, Prometheus/Grafana, budgets, tags, cost trade-offs.
- **IaC** — Terraform module structure, provider gates (AD strategy, image-OCID pinning, sensitive state, drift prevention), `fmt` / `validate` / reviewed `plan`.
- **Integration decisions** — whether a direct OCI MCP / plugin is justified over CLI + Terraform.

The agent **proposes, plans and validates**. You **approve and apply**.

---

## Prerequisites

- An **OCI tenancy** (free tier works to start).
- The **OCI CLI** installed and configured.
- An **agent harness**: Codex, Claude, or Cursor.
- *(Optional)* **Terraform** ≥ 1.5 for IaC work.

---

## Quick start

**1. Give the repo to your favorite harness and import it.**
```bash
git clone https://github.com/sjaramillov/oci-cloud-architect.git
```
Load it as a skill, open it in Cursor, or point Claude/Codex at the folder — the agent reads `SKILL.md` and the `references/` automatically.

**2. Install and configure the OCI CLI.**
```bash
# macOS
brew install oci-cli
# or the official installer (Linux/macOS/Windows):
# https://docs.oracle.com/iaas/Content/API/SDKDocs/cliinstall.htm

oci setup config        # tenancy OCID, user OCID, region, API key
oci iam region list     # sanity check
```

**3. Check local readiness (no secrets printed), then have fun! :D**
```bash
python3 scripts/oci_context_check.py
```
Then ask your agent:
- *"Design a private app + Autonomous DB on OCI Chicago, public LB only, Bastion for admin."*
- *"Write a least-privilege policy for a VM that reads Vault secrets and calls GenAI."*
- *"Review my Terraform plan for blast radius and rollback steps."*
- *"Should this warrant an OCI MCP, or is CLI + Terraform enough?"*

---

## What's inside

```text
oci-cloud-architect/
├── SKILL.md                          # agent-facing skill: posture, workflow, guardrails
├── agents/                           # harness entry points (Codex / Claude / Cursor)
├── references/
│   ├── oci-best-practices.md         # IAM, networking, compute, ADB, Vault, Terraform gates
│   └── oci-mcp-decision.md           # when a direct OCI MCP integration is warranted
├── scripts/
│   └── oci_context_check.py          # local OCI readiness check — masks identifiers, no API calls
└── README.md
```

---

## Safe local check

`scripts/oci_context_check.py` inspects your local OCI readiness — config presence, masked identifiers, recommended next checks — **without calling OCI APIs or reading any secret values**. It's the first thing the agent runs to orient itself safely.

---

## Guardrails

The skill operates under a strict, secure-by-default posture:

- **No destructive actions without explicit approval** — no `terraform apply`/`destroy` or mutating OCI commands on its own.
- **Secrets never leave your machine** — no keys, wallets, auth tokens or secret bundles in Git, shell history, command args, PR bodies or logs.
- **Least privilege by default** — dynamic groups scoped to exact instance OCIDs or tags; instance principals over user API keys; no `manage all-resources in tenancy` except temporary break-glass.
- **Narrow ingress** — public Load Balancer only; private app/database; Bastion for admin; no public SSH.
- **Terraform state is treated as sensitive**, and a change with a failed validation is left blocked with evidence and residual risk — never silently applied.

---

## Built for AI-DLC

For IaC work the skill follows the station pattern — *intent → context → scope → dependencies → execution → validation → review → memory/audit* — and won't treat an HCL edit as complete until the matching task, acceptance criteria, validation evidence and residual risks are updated.

---

## License

MIT — use it, fork it, improve it.

## Author

Built by [@sjaramillov](https://github.com/sjaramillov). Contributions welcome.
