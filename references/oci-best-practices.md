# OCI Best Practices Reference

Load this reference when designing or reviewing OCI architecture, Terraform,
IAM, Vault, GenAI, networking, or runtime operations.

## Primary Sources To Prefer

- OCI Terraform best practices:
  https://docs.oracle.com/en-us/iaas/Content/dev/terraform/best-practices.htm
- Managing default VCN resources:
  https://docs.oracle.com/en-us/iaas/Content/dev/terraform/default-vcn.htm
- Referencing availability domains:
  https://docs.oracle.com/en-us/iaas/Content/dev/terraform/ref-availability-domains.htm
- Referencing images:
  https://docs.oracle.com/en-us/iaas/Content/dev/terraform/ref-images.htm
- Storing sensitive data:
  https://docs.oracle.com/en-us/iaas/Content/dev/terraform/storing-sensitive-data.htm
- Tagging resources:
  https://docs.oracle.com/en-us/iaas/Content/dev/terraform/tagging-resources.htm
- OCI IAM policies:
  https://docs.oracle.com/iaas/Content/Identity/policieshow/Policy_Basics.htm
- OCI dynamic groups:
  https://docs.oracle.com/iaas/Content/Identity/Tasks/managingdynamicgroups.htm
- OCI Vault and key policy reference:
  https://docs.oracle.com/iaas/Content/Identity/policyreference/keypolicyreference.htm
- OCI Secret Management:
  https://docs.oracle.com/en-us/iaas/Content/secret-management/home.htm
- OCI Generative AI IAM policies:
  https://docs.oracle.com/iaas/Content/generative-ai/iam-policies.htm
- OCI Security Best Practices:
  https://docs.oracle.com/iaas/Content/Security/Concepts/security_guide.htm

## Architecture Checklist

- Compartment boundary exists per environment or product boundary.
- Resources have consistent freeform or defined tags: product, environment,
  owner, cost-center, data-classification, managed-by.
- Public access is intentional and documented.
- App and monitoring hosts are private unless a public endpoint is required.
- Admin access uses Bastion/session workflows, not public SSH.
- Runtime credentials come from instance principals, resource principals, Vault,
  or mounted secrets; never committed files.
- ADB uses separate schema/user per environment and never application runtime as
  `ADMIN`.
- Load Balancers terminate TLS and route to private backends.
- Monitoring scrapes private targets; Grafana is private or allowlisted.
- Budgets, limits, and shape availability are checked before apply.

## Terraform Checklist

- Pin provider versions and commit `.terraform.lock.hcl`.
- Resolve availability domains in the environment layer and pass them to
  modules. Modules must not call `oci_identity_availability_domains`
  themselves.
- Do not rely on unmanaged default VCN resources. If defaults are used, manage
  them explicitly with `oci_core_default_security_list`,
  `oci_core_default_route_table`, and `oci_core_default_dhcp_options` using
  `manage_default_resource_id`.
- Use region-specific image OCID maps for compute. Do not use
  `oci_core_images`/`ListImages` as the normal apply path for Oracle-provided
  images because image lists drift over time.
- Mark variables containing passwords, keys, wallets, tokens, and OCIDs that
  identify sensitive boundaries as `sensitive`.
- Treat local and remote state as sensitive.
- Apply freeform or defined tags consistently to primary and secondary
  resources. OCI tag propagation can create state drift if secondary resources
  do not declare the same tags.
- Run `terraform fmt -check -recursive`, `terraform validate`, and reviewed
  `terraform plan -out <file>` before requesting apply.
- Review every destroy/replacement in the plan.
- Never commit `terraform.tfvars`, `.tfplan`, `.terraform/`, local state,
  wallets, private keys or provider crash logs.
- If `terraform validate` fails because provider schemas cannot load, stop.
  Do not commit the Terraform domain. Archive or move stale `.terraform/`,
  rerun `terraform init`, capture the exact provider path/version, and retry
  validate before changing HCL further.

## AI-DLC Terraform Unit Pattern

Use the Estacion Terraform lesson as an operational contract:

- Treat infrastructure as its own unit of work with explicit dependencies and
  outputs consumed by backend/frontend/runtime units.
- Before code generation: define scope, resource list, variables, outputs,
  environment files, secrets handling, acceptance criteria and test plan.
- During implementation: keep `*.tfvars.example` safe, keep real tfvars local,
  avoid broad IAM, and expose outputs needed by later deploy scripts.
- Before commit: require domain evidence. Minimum evidence is `fmt`, `init`,
  `validate`, plan review, and any service-specific smoke that proves the
  changed resource contract.
- After commit or apply: update `aidlc-state.md`, `audit.md`, task files and
  residual-risk register with what passed, what failed, and what remains
  blocked.

## OCI Provider Design Gates

- **Network:** public ingress only through an approved Load Balancer or public
  endpoint; app, monitoring and database paths are private by default. No
  public SSH when Bastion/session access is available.
- **Compute:** pin shape, OCPU, memory, boot volume and image OCID. For plugin
  work, use exact Oracle Cloud Agent plugin names, for example `Compute
  Instance Run Command`, not adjacent plugins such as `Bastion`.
- **IAM:** prefer dynamic groups scoped to exact instance OCIDs or stable tags.
  Avoid tenancy-wide `manage all-resources`; split read/inspect/use/manage by
  service and compartment.
- **Vault:** use secret bundles for runtime secrets; Terraform may reference
  secret OCIDs but should not materialize secret values into state unless there
  is no safer alternative.
- **ADB:** use environment-specific schema/users. Do not run application code
  as `ADMIN`; keep wallets and passwords outside Git.
- **GenAI:** configure region, compartment OCID and model OCID explicitly.
  GenAI credentials do not replace domain evidence authorization such as MCP
  access in MAICO.
- **Monitoring:** keep Grafana private or allowlisted. Scrape private targets
  and expose only the minimum blackbox/public probes needed for health.

## Provider Troubleshooting Gate

When the OCI provider fails locally:

1. Capture `terraform -version`, provider version from `.terraform.lock.hcl`,
   provider binary path, architecture and exact error.
2. Move stale `.terraform/` to a non-repo temp path or archive it outside Git.
3. Run `terraform init` again and retry `terraform validate`.
4. If the same schema/handshake error repeats, mark the Terraform domain
   blocked and validate in a clean runner or OCI Resource Manager before
   committing HCL.
5. Do not substitute static grep tests for `terraform validate` when the change
   can affect live infrastructure.

## IAM And Vault Checklist

- Prefer dynamic groups scoped by exact instance OCID:
  `ALL {instance.id = '<instance_ocid>'}`.
- Use broader compartment rules only when exact instance OCIDs are not stable.
- Use least-privilege policies: `read secret-bundles`, `inspect vaults`,
  `inspect keys`, and service-specific `use` permissions.
- Prefer software-protected AES-256 keys for pilot/application config secrets.
- Use HSM only for compliance, production root keys, or high-assurance key
  separation requirements.
- Never print secret-bundle content. Decode secrets only into protected files
  with `0600` permissions or in-memory pipelines.

## GenAI Runtime Checklist

- Set region explicitly, e.g. `us-chicago-1`.
- Set model OCID explicitly, not by display name.
- On OCI Compute, prefer `MAICO_OCI_AUTH_MODE=instance_principal`.
- Ensure the instance dynamic group can `use generative-ai-family` in the target
  compartment.
- Separate LLM inference authorization from domain evidence authorization. For
  MAICO, OCI GenAI credentials do not replace MCP evidence authorization.

## Operational Review Output

When reviewing a plan, answer in this order:

1. Verdict: ready, ready with conditions, blocked, or unsafe.
2. Critical blockers.
3. Required policy/secret/network changes.
4. Cost and quota risks.
5. Terraform/provider best-practice gaps.
6. Validation commands and expected evidence.
7. Rollback/recovery path.
