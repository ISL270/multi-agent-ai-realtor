---
trigger: always_on
---

# Langgraph rules

## When to Use Trustcall
**Complex or Nested Schema Extraction**
- The output is expected to match a deeply nested or multi-layer Pydantic model.
- Example: user profiles, memory documents, structured logs with nested fields.

**Incremental Updates / Patching**
- The agent needs to update parts of a document without re-generating the full object.
- Useful for memory updates, profile enrichment, or task tracking.

**Strict Schema Validation**
- The downstream tool requires well-formed, schema-validated JSON (e.g., API requests, DB inserts).
- Business logic rules (e.g., lists with minimum length, enums) must be enforced reliably.

**Resilient, Efficient Output Generation**
- When failures due to invalid outputs are costly (e.g., large inputs or token-heavy generations).
- When output patching (not full regeneration) improves efficiency and cost.

**When not needed**
- The schema is flat/simple (e.g., single-layer key-value dicts).
- The output does not need to be validated against a Pydantic model.
- The tool or agent consumes free-form text or summaries.

**Rule of thumb:**  
If structured output is critical to the tool's function *and* there's risk of failure due to complexity → **use Trustcall**.

## When to Use Structured Outputs

Structured outputs should be used in LangGraph agents when:

**Tool Chaining / Downstream Consumption**
- The output is passed to another tool, API, or database that expects machine-readable, structured data (e.g., JSON, Pydantic model).
- Example: search filters, API request bodies, DB inserts.

**Schema Validation & Safety**
- The agent's response must match a strict schema for correctness.
- Example: structured configurations, task objects, structured logs.

**Memory & Analytics**
- The output will be stored for long-term memory, logging, or analytics where structure ensures consistency.
- Example: user preferences, conversation summaries, extracted entities.

**Business Logic Enforcement**
- When rules like required fields, enum validation, or numeric constraints should be automatically enforced.
- Example: minimum price >= 0, valid property types, required user ID.

**When not needed**
- The tool or downstream consumer works with free-form text (e.g., summaries, creative writing, natural language responses).
- The data does not need validation or strict machine-readable structure.

**Rule of thumb:**  
If another tool, database, or system depends on consuming the output reliably → **use structured outputs**.

## Writing tool descriptions for LangGraph
- Keep the description before `Args` focused on what the tool *does* — not how it is implemented.
- It’s okay to use multiple sentences or paragraphs; no need to limit to one-liners.
Ensure descriptions highlight the key inputs or criteria the tool operates on, and briefly mention what the tool returns.
- Follow Google-style formatting for the `Args` section to ensure proper parsing.
- Do not use nested bullet lists inside `Args`. Describe subfields in prose or as top-level parameters if needed.