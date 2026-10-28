# Public persona descriptions

The popup and standalone entry page show the existing description once.

- Description: existing `featured_reason` / `judge.description` fields, unchanged.
- Search tags: `judge.tags`, retained in data and search, omitted from entry display.
- Review reasons: `ranking.reason`, `editorial.reason`, and pair-review notes remain
  in the research data; they are not repeated as extra public description blocks.
- Reviewer prefixes, rubric explanations, and the browsing-label warning were UI
  text, not part of Talkie's raw reply.

Scores, neuron settings, parent links, controls, saved attempts and raw replies
are unchanged. Some historical description fields contain study prose themselves;
this display-only cleanup does not rewrite those descriptions.

The active workspace builder and share template were updated. The source snapshots
here document the new render behavior. To clean older already-rendered pages
without rebuilding other layout:

    python scripts/persona-display/clean_persona_display.py public

The utility checks that existing reply, description and score blocks are preserved.
