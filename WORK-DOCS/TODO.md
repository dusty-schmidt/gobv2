 # TO DO
 
 - Clean house: update docs/tests that still reference “Nano” or old CLI options; fix failing imports like core.summarizer_agent to the new module layout.
 - Make conversations durable: audit UniversalConversationManager and related async calls so every save/load is awaited and exercised by a regression test.
 - Unify prompts + logging: point Mini/Main/Max at core.prompts.manager and standardize their logging setup on core.logging.
 - Wire DI where it matters: introduce core.di.Container to main/ for communal brain, LLM client, and storage so Tier 2 code is ready for shared services.
 - Prove the integration: add/repair tests that cover end-to-end chat flows (Mini vs. Main) and communal brain stats to confirm the foundation before advancing to Stage 2 milestones.