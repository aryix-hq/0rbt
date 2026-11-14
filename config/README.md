# Configuration & Feed Registry Domain (`config`)

> **Package / Component**: System Configuration & Static Metadata Registry  
> **Contract Standard**: Peanuts & Hay Leaf Contract (`INV-DOC-02`)  
> **Status**: Active  

---

## 1. Domain Responsibility
The `config/` package manages the externalized, static operational metadata required by the engineering blog intelligence workflows. It isolates data sources, feed types, categorization schemas, and pipeline parameters from execution canvases.

---

## 2. Exported Interfaces & Schemas
- **`engineering_blogs_registry.json`**:
  - `sources[]`: Array of blog sources:
    - `id` (string, unique slug)
    - `company` (string, official organization name)
    - `category` (string, system architecture domain)
    - `blog_url` (string, canonical homepage)
    - `feed_url` (string, verified RSS/Atom/Medium endpoint)
    - `feed_type` (enum: `rss` | `atom` | `medium` | `json`)
    - `active` (boolean flag to toggle polling)

---

## 3. Enforced Invariants
- **`INV-CFG-01` (Unique Source IDs)**: Every entry in `engineering_blogs_registry.json` must possess a globally unique, kebab-cased `id`.
- **`INV-CFG-02` (URL Validity)**: All `blog_url` and `feed_url` fields must start with `https://` and point to valid, reachable hostnames.
- **`INV-CFG-03` (Zero Credential Leakage)**: No API keys, secret tokens, or private endpoint credentials may be stored in `config/` files.
