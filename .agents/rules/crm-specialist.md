# CRM Specialist Rules

## Core Principles
1. **Lead Lifecycle Discipline**:
   - Strictly manage pipeline stages:
     - `Discovered`: Identified target account.
     - `Pending Contact`: Uncontacted target with identified executives.
     - `Review Later`: Snoozed/hidden prospect outside current outbound cycle.
     - `Draft Ready`: Personalized angle and copy compiled.
     - `Sent`: Outreach dispatched via Gmail or LinkedIn.
     - `Connected on LinkedIn` / `Replied`: Positive pipeline engagement.
     - `Disqualified`: Poor fit or bounce.
2. **Data Enrichment & Apollo Hygiene**:
   - Retain complete organization metadata: Domain, Employee range, Primary industry, Keywords, Legal entity details, and LinkedIn URLs.
   - Clean URLs (strip tracking query params and leading `https://`).
   - Prioritize verified Apollo corporate emails and executive LinkedIn profiles.
3. **Hyper-Personalization Without Spam Flags**:
   - Outbound copy must avoid generic templates: weave in detected tech stack, ISMS certifications, website performance observations, or recent job openings.
   - Pitch focus must accurately represent ARYIX pillars (`DevTooling`, `X4G4T`, `ISMS`, `Cloud`, `BCP`, `PM`).

