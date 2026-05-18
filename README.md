# Symphonix Health Docs

Internal documentation, marketing, research, brand assets, and strategy for Symphonix Health.

## Structure

```
marketing/
  symphonix-health-marketing.md   # Master messaging document
  countries/                       # Country-specific marketing pages
    ghana.md
    ireland.md
    kenya.md
    nigeria.md
    rwanda.md
    uk.md
research/
  healthcare-challenges-research.md  # Six-country health system analysis
brand/
  logos/                             # SVG logo variants
  showcase.html                     # Brand showcase page
strategy/
  bullettrain-integration-doctrine.md # Cross-system data-sharing doctrine
  agent-first.md                       # AI-agent platform strategy
  prompt-engineering-system.md       # BulletTrain prompt DSL specification
```

## Relationships

- `research/` feeds `marketing/countries/` (each country page draws on the research analysis)
- `marketing/symphonix-health-marketing.md` is the master messaging that country pages localise
- `brand/logos/` are used by `symphonix-public` (website) and `symphonix-health.github.io`
- `strategy/bullettrain-integration-doctrine.md` defines the no point-to-point sibling integration rule
- `strategy/prompt-engineering-system.md` defines the prompt DSL used by BulletTrain services
