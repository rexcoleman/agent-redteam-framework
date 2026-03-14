# Report Consistency & Writing Quality Specification

> **Template version:** 1.0
> **Authority:** Tier 2 (Report Quality)
> **Source:** Kording & Mensh (2016), "Ten simple rules for structuring papers"
> **Reference:** `docs/references/Ten_Simple_Rules_Kording_Mensh.md`
> **Enforcement phases:** Phase 4 (Report Draft), Phase 5 (Pre-Submission)
> **Cross-references:** REPORT_ASSEMBLY_PLAN, FIGURES_TABLES_CONTRACT, EXECUTION_MANIFEST, PRE_SUBMISSION_CHECKLIST

---

## How to Use This Template

1. Fill all `{{PLACEHOLDER}}` values during Phase 0 (Setup) or Phase 4 (Report Draft)
2. Use the checklists as audit criteria — run through each rule after completing the report draft
3. Machine-checkable items (marked `[AUTO]`) can be verified by `scripts/audit_report.py`
4. AI-assisted items (marked `[AI-AUDIT]`) require structured prompt verification
5. Manual items (marked `[MANUAL]`) require human judgment

---

## Rule 1: One Central Contribution

**Principle:** The paper communicates exactly one main finding, stated in the title.

- [ ] `[AUTO]` Title is a declarative claim, not procedural
  - REJECT patterns: "Analysis of...", "A Study of...", "Investigation of...", "Exploring..."
  - ACCEPT patterns: "[Finding] [through/via/using] [method]", "[X] outperforms [Y] for [task]"
- [ ] `[AI-AUDIT]` Title communicates the main finding, not just the method
- [ ] `[AI-AUDIT]` A naive reader can state the paper's contribution from title alone
- [ ] `[MANUAL]` Title refined ≥3 times during writing process

**Project title:** {{REPORT_TITLE}}
**Central contribution (one sentence):** {{CENTRAL_CONTRIBUTION}}

---

## Rule 2: Write for Naive Readers

**Principle:** Define all jargon, use minimal technical language, write for someone outside your sub-specialty.

- [ ] `[AUTO]` All jargon terms defined on first use (inline or glossary)
- [ ] `[AUTO]` No acronym used without expansion on first occurrence
- [ ] `[AI-AUDIT]` Domain-specific terms have parenthetical glosses where needed
- [ ] `[AI-AUDIT]` Methods described at a level a graduate student outside the subfield can follow

### Jargon Inventory

| Term | Definition | First Occurrence (Section) |
|------|-----------|---------------------------|
| {{TERM}} | {{DEFINITION}} | {{SECTION}} |

---

## Rule 3: Context-Content-Conclusion (CCC)

**Principle:** Every unit of text (document, section, paragraph) follows CCC structure.

### Document-Level CCC
- [ ] `[AI-AUDIT]` Introduction = Context (field → subfield → specific gap)
- [ ] `[AI-AUDIT]` Results = Content (evidence sequence supporting central claim)
- [ ] `[AI-AUDIT]` Discussion = Conclusion (gap filled + limitations + future directions)

### Abstract CCC
- [ ] `[AI-AUDIT]` Sentence 1-2: Broad context → specific gap
- [ ] `[AI-AUDIT]` Sentence 3-4: "Here we..." approach + executive summary of results
- [ ] `[AI-AUDIT]` Sentence 5-6: Conclusion answering the gap + broader significance
- [ ] `[AUTO]` Abstract length ≤ {{ABSTRACT_WORD_LIMIT}} words

### Paragraph-Level CCC
- [ ] `[AI-AUDIT]` Every paragraph opens with context/topic sentence
- [ ] `[AI-AUDIT]` Every paragraph closes with conclusion/takeaway sentence
- [ ] `[AUTO]` No paragraph exceeds {{MAX_PARAGRAPH_SENTENCES}} sentences (default: 8)
- [ ] `[AI-AUDIT]` No paragraph where a reader would ask "why was I told that?" (missing context) or "so what?" (missing conclusion)

---

## Rule 4: Logical Flow (No Zig-Zag + Parallelism)

**Principle:** Each concept appears in exactly one location. Parallel ideas use parallel structure.

- [ ] `[AI-AUDIT]` Each concept introduced in exactly one location (no A-B-A bouncing)
- [ ] `[AI-AUDIT]` Related ideas grouped together, not scattered across sections
- [ ] `[AI-AUDIT]` Parallel arguments use parallel syntactic structure
- [ ] `[AUTO]` One canonical term per concept (no synonym drift)

### Terminology Lock

| Canonical Term | Rejected Variants | Rationale |
|---------------|-------------------|-----------|
| {{CANONICAL}} | {{REJECTED_VARIANTS}} | {{RATIONALE}} |

---

## Rule 5: Abstract Completeness

**Principle:** The abstract is self-contained and tells the complete story.

- [ ] `[AUTO]` Abstract ≤ {{ABSTRACT_WORD_LIMIT}} words
- [ ] `[AI-AUDIT]` No undefined terms or forward references in abstract
- [ ] `[AI-AUDIT]` Abstract covers: gap, method, key results, conclusion
- [ ] `[AI-AUDIT]` Broad-narrow-broad structure (field → results → significance)
- [ ] `[AI-AUDIT]` Results "fill the gap like a lock and key" — conclusion answers the gap question

---

## Rule 6: Introduction — Why It Matters

**Principle:** Introduction narrows from field to specific gap, then previews results.

- [ ] `[AI-AUDIT]` Paragraphs progress: broad field → subfield → specific gap
- [ ] `[AI-AUDIT]` Gap statement is explicit ("However, ... remains unknown/untested/unvalidated")
- [ ] `[AI-AUDIT]` No literature review beyond gap motivation
- [ ] `[AI-AUDIT]` Final intro paragraph previews results (compact summary, no context needed)
- [ ] `[AI-AUDIT]` Each paragraph: context (topic) → knowns (literature) → unknown (gap at this scale)

---

## Rule 7: Results — Declarative Sequence

**Principle:** Results subsections are declarative findings. Each paragraph: question → evidence → answer.

- [ ] `[AUTO]` Subsection headers are declarative statements (not "Experiment 1" but "PCA reduces dimensionality by 85% with minimal information loss")
- [ ] `[AI-AUDIT]` First results paragraph summarizes the overall approach
- [ ] `[AI-AUDIT]` Each subsequent paragraph: poses question → presents data/logic → answers question
- [ ] `[AI-AUDIT]` Paragraph conclusions build on each other (theorem-chain structure)

### Figure & Table Quality (cross-ref: FIGURES_TABLES_CONTRACT)
- [ ] `[AI-AUDIT]` Figures tell the story without requiring legend text
- [ ] `[AUTO]` Every caption contains a takeaway interpretation (not just "Figure 1 shows...")
- [ ] `[AUTO]` Seed aggregation uses median+IQR or mean±std (no bare means)
- [ ] `[AUTO]` Method-specific settings disclosed in captions or notes

---

## Rule 8: Discussion — Gap Filled + Limitations + Future

**Principle:** Discussion summarizes, acknowledges limitations, and opens new directions.

- [ ] `[AI-AUDIT]` First paragraph summarizes key findings from Results
- [ ] `[AI-AUDIT]` Subsequent paragraphs: weakness/strength → literature evaluation → author interpretation
- [ ] `[AI-AUDIT]` Limitations acknowledged with specific mitigation or future work
- [ ] `[AI-AUDIT]` Final paragraph(s) describe broader impact and future directions
- [ ] `[AUTO]` No new results introduced in Discussion

---

## Rule 9: Time Allocation

**Principle:** Invest most time in title, abstract, figures, and outlining.

- [ ] `[MANUAL]` Title refined ≥3 times (verify via git log or CHANGELOG)
- [ ] `[MANUAL]` Abstract refined ≥3 times
- [ ] `[AUTO]` All figures are publication-quality (labeled axes, readable fonts, ≥300 DPI)
- [ ] `[MANUAL]` Outline created before prose (verify via REPORT_ASSEMBLY_PLAN)

---

## Rule 10: Iterate with Feedback

**Principle:** Get test-reader feedback; iterate the story, not just the sentences.

- [ ] `[MANUAL]` At least one test-reader or AI audit pass documented
- [ ] `[AUTO]` Rubric/FAQ compliance verified (see RUBRIC_TRACEABILITY)
- [ ] `[MANUAL]` All audit findings resolved before submission
- [ ] `[MANUAL]` Feedback integrated into structure, not just surface edits

---

## Numeric Consistency Rules

**Source:** UL/RL audit findings — numeric errors are the highest-severity quality failures.

- [ ] `[AUTO]` Every number in the report traces to a specific output artifact (per EXECUTION_MANIFEST)
- [ ] `[AUTO]` No manually transcribed numbers — all extracted via `post_compute.py` or equivalent
- [ ] `[AUTO]` Rounding follows specification below
- [ ] `[AUTO]` Percentage claims verified against raw data
- [ ] `[AUTO]` Multiplier/ratio claims verified (numerator ÷ denominator = stated ratio)
- [ ] `[AUTO]` "Improvement" language matches positive delta; "degradation" matches negative delta
- [ ] `[AUTO]` Min/max/mean claims verified against actual distributions

### Rounding Specification

| Metric Type | Decimal Places | Example |
|------------|---------------|---------|
| {{METRIC_TYPE}} | {{DECIMAL_PLACES}} | {{EXAMPLE}} |

---

## Cross-Reference Integrity

- [ ] `[AUTO]` Every figure referenced in text (no orphan figures)
- [ ] `[AUTO]` Every table referenced in text (no orphan tables)
- [ ] `[AUTO]` Figure/table numbers are sequential and consistent
- [ ] `[AUTO]` All \cite{} keys appear in bibliography
- [ ] `[AUTO]` All bibliography entries cited in text (no orphan references)
- [ ] `[AUTO]` Internal section references (\ref{}) resolve correctly
- [ ] `[AUTO]` Terminology consistent throughout (see Terminology Lock above)

---

## Assignment-Specific Compliance

- [ ] `[AUTO]` All rubric items addressed (see RUBRIC_TRACEABILITY)
- [ ] `[AUTO]` All FAQ items addressed (see RUBRIC_TRACEABILITY)
- [ ] `[AUTO]` Deliverable filenames match convention: `{{DELIVERABLE_NAMING_CONVENTION}}`
- [ ] `[AUTO]` Author/ID format: `{{AUTHOR_FORMAT}}`
- [ ] `[AI-AUDIT]` AI Use Statement meets policy requirements
  - First-person voice
  - Tool-specific (name the tool, not "AI")
  - Ownership declaration for design, hypotheses, conclusions
  - Verification statement

---

## Build Verification

- [ ] `[AUTO]` LaTeX compiles without errors (`pdflatex` exit code 0)
- [ ] `[AUTO]` All figure paths resolve (no missing file warnings)
- [ ] `[AUTO]` No overfull hbox warnings > {{OVERFULL_THRESHOLD}}pt (default: 10)
- [ ] `[AUTO]` PDF page count ≤ {{PAGE_LIMIT}}
- [ ] `[AUTO]` URLs properly escaped (# → \# in LaTeX)
- [ ] `[AUTO]` graphicspath correctly set for target build environment

---

## Audit Execution Protocol

### Phase 4 Audit (Post-Draft)
Run lenses: L5 (Data-vs-Report), L6 (Rubric/FAQ), L7 (Ten Simple Rules), L10 (Cross-References)

```bash
python scripts/audit_report.py --phase 4
```

### Phase 5 Audit (Pre-Submission)
Run all lenses: L1-L10

```bash
python scripts/audit_report.py --phase full
```

### Fix Protocol
1. Review FINDINGS.md
2. Fix all CRITICAL items first (data integrity)
3. Fix all HIGH items (compliance gaps)
4. Fix MEDIUM items (writing quality)
5. Re-run audit to verify fixes
6. Repeat until 0 CRITICAL + 0 HIGH

### Audit History

| Date | Phase | Lenses | Pass | Fail | Findings Resolved |
|------|-------|--------|------|------|-------------------|
| {{DATE}} | {{PHASE}} | {{LENSES}} | {{PASS}} | {{FAIL}} | {{RESOLVED}} |
