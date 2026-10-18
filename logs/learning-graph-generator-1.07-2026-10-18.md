# Session Log: learning-graph-generator v1.07

**Date:** 2026-10-18
**Book:** Open Study Buddy

## Tool versions

- learning-graph-generator skill: 1.07
- csv-to-json.py: 1.05
- analyze-graph.py: copied from skill (no version constant)
- taxonomy-distribution.py: copied from skill (no version constant)
- validate-learning-graph.py: copied from skill (no version constant)
- course-description-analyzer skill: 0.05

## Steps

1. Step 1 skipped: course description quality_score is 99 (above 85).
2. Step 2: 326 concepts written to `docs/learning-graph/concept-list.md`; all labels Title Case, 32 characters or fewer, unique. User reviewed and approved the list.
3. Step 3: dependency CSV built by label (resolved to ConceptIDs by script), checked for unknown labels, self-dependencies and cycles. 3 foundational concepts: Personal Agent, MicroPython Review, Sound Wave.
4. Step 4: `analyze-graph.py` reported a valid DAG, 0 orphans, 1 connected component, 96 terminal nodes (29.4%), longest chain 21, 1.64 average dependencies.
5. Steps 5-6: 15 taxonomy categories; TaxonomyID column added to the CSV.
6. Steps 7-9: `metadata.json`, `taxonomy-names.json` and `color-config.json` created; `csv-to-json.py` produced `learning-graph.json` (326 nodes, 531 edges) and validated against the schema. The top CIS concepts are MicroPython Review, Sound Wave, Personal Agent, Sampling and Modules and Imports.
7. Step 10: `taxonomy-distribution.md` generated; all categories between 4.3% and 9.2%.
8. Step 11: `index.md` rewritten from the template.
9. `mkdocs build --strict` passes with the five learning-graph pages in the nav.
