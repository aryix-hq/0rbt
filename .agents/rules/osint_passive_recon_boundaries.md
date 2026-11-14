# Passive OSINT & External Reconnaissance Boundaries

1. **Passive-First Reconnaissance Mandate**:
   - External asset mapping relies strictly on public, unauthenticated, and third-party aggregated intelligence: Certificate Transparency logs (`crt.sh`), passive DNS datasets, public WHOIS/RDAP, historical web archives, search engine dorks, and internet registries (Shodan, Censys).
   - Active, intrusive network scanning, aggressive fuzzing, directory brute-forcing, and volumetric requests against unauthorized targets are strictly prohibited. All investigations must adhere to verified customer engagement boundaries.

2. **Strictly Read-Only Credential Probing**:
   - When API keys, tokens, or credentials are discovered in public repositories, dorks, or paste sites, verification is restricted to strictly read-only, zero-mutation endpoints:
     - **AWS**: `sts:GetCallerIdentity` (never `iam:CreateUser` or S3 downloads).
     - **GitHub**: `GET /user` (never write commits or create repositories).
     - **Stripe**: `GET /v1/balance` (never trigger charges or payouts).
     - **Slack**: `auth.test` (never read private channels or post messages).
     - **Google Cloud**: `GET https://www.googleapis.com/oauth2/v3/tokeninfo` (never invoke compute/storage APIs).
   - Mutating state, modifying configurations, accessing third-party customer PII, or deleting resources constitutes a critical boundary violation.

3. **Secret Redaction & Vector Store Hygiene**:
   - Discovered API secrets, passwords, private keys, and employee PII must be sanitized immediately upon ingestion.
   - Proof-of-concept manifests, vector database documents, and console outputs must mask raw strings using standard placeholders (`AKIA****************`, `sk_live_****`).
   - Zero plaintext secrets may enter `.agents/memory/vector_store.db`, git commit histories, or task transcripts.

