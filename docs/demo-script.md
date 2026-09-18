# Demo script — EcoRestore Intelligence

A ~5 minute walkthrough for judges/reviewers.

## 1. Structured assessment (Environmental Assessment page)

1. Open the deployed frontend (or `localhost:5173`).
2. On **Environmental Assessment**, click **"Load Sundarbans sample scenario"** — this fills
   the exact flagship JSON from the challenge brief (mangrove, high salinity, aquaculture
   expansion, irregular rainfall, high fragmentation, low bird/pollinator activity).
3. Note the map panel rendering the coordinates (21.95, 88.75) via Leaflet/OpenStreetMap — no
   paid map API involved.
4. Click **"Generate Recovery Plan"**. You are taken to the Recovery Plan page.

## 2. Recovery Plan — reasoning and evidence

1. Point out the **risk level badge** (expect `high` or `critical`) and the **confidence bar**
   with its explanation (why confidence is what it is — missing fields, evidence coverage).
2. Expand **"Variables considered"** — every non-null field submitted.
3. Expand **"Reasoning trace"** — this is the deterministic rule engine's audit trail: which
   variables were detected, which multi-metric rules activated (e.g. mangrove + high salinity
   + aquaculture expansion + low biodiversity → Rule R3), how many evidence chunks were
   retrieved per intervention, and the ranking rationale.
4. Scroll through the ranked recommendation cards. For each one, point out:
   - **What to do** (action) and **why it works** (scientific reasoning, grounded in the
     activated rule + retrieved evidence).
   - **Impacted metrics** with direction (increase/decrease/stabilise) and mechanism.
   - **Time horizon** (short/medium/long).
   - **Sources/evidence** — real FAO/IPCC/UNEP/CBD/IUCN citations with clickable links and a
     retrieval relevance score. Click one to show it opens the real organization page.
   - **Limitations** — including the mandatory sentence stating no numeric estimate is
     fabricated, and (where applicable) that no directly matching evidence was retrieved.

## 3. AI Scientist Chat — clarification and memory

1. Go to **AI Scientist Chat**.
2. Type: *"Biodiversity is declining on my land."*
   Expect a **focused clarifying question** (max 3 items) rather than a guessed answer.
3. Reply with something like: *"It's a mangrove site with irregular rainfall and aquaculture
   expansion nearby; bird activity is low."*
   Expect: the assistant now has enough data, returns an assessment summary, top
   recommendation, and **retrieved evidence displayed inline** under the reply.
4. Point out the **conversation memory panel** on the right — it summarizes everything
   collected so far, proving multi-turn memory (not a stateless chatbot).
5. Click **"View Recovery Plan"** to show the same ranked plan now reflects the chat-derived
   assessment.

## 4. MRV Tracker — honest baseline/follow-up comparison

1. Go to **MRV Tracker**. The current assessment ID is pre-filled if you came from a plan.
2. Fill in baseline values (e.g. SOC 0.4%, moisture 18%, species richness 20, connectivity 15,
   pollution risk 70) and **Save baseline**.
3. Refresh — note the summary explicitly states *no improvement or decline can be claimed*
   because no follow-up observation exists yet.
4. Add a follow-up observation with improved values (e.g. SOC 0.6%, species richness 28,
   pollution risk 55) and submit.
5. The comparison table now shows real deltas and trend badges (`improved`/`declined`/
   `no_change`) computed only from entered values — never guessed.

## 5. API docs

Open `<backend URL>/docs` to show the FastAPI-generated interactive documentation covering
every endpoint listed in the README, and optionally call `GET /api/evidence/search?q=mangrove
restoration` directly to show raw RAG retrieval output with relevance scores.
