# Vault Secrets Management & Zero-Plaintext Invariants

1. **Zero Plaintext Secrets Invariant**:
   - Committing API keys, database passwords, private certificates, or tokens to git or unencrypted configuration files (`.env`, `config.json`) is strictly prohibited.
   - Any detected credential leak during `./bin/deploy-preview.sh` immediately blocks preview builds and invalidates the PR.

2. **HashiCorp Vault KV v2 Standards**:
   - Production and staging application secrets must be stored in HashiCorp Vault under structured mount paths: `secret/data/<environment>/<service-name>`.
   - Applications must consume secrets via Vault Agent injection, AppRole authentication tokens, or runtime environment injection (`vault kv get`).

3. **Dynamic Database Credentials & Lease Expiration**:
   - Services and worker pipelines must prefer Vault dynamic secrets engines (e.g., database dynamic roles with bounded TTLs) over static database passwords.
   - All applications must implement token renewal and graceful re-authentication upon lease expiration.

4. **Local Development Vault Protocol**:
   - In local environments, services must connect to a local Vault dev instance (`hashicorp/vault:latest` on port 8200) or consume encrypted envelopes.
   - Real production or staging third-party credentials (Stripe, AWS, OpenAI, Apollo) must never be pasted into local unencrypted `.env` files.

5. **DevSecOps Audit Sign-off**:
   - The DevSecOps Engineer (`@devsecops`) must verify Vault secret paths, AppRole CIDR restrictions, and least-privilege policies (`capabilities = ["read"]`) before `@engineering-manager` grants PR merge sign-off.

