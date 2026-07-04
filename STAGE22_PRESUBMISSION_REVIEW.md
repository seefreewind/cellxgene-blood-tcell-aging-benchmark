# Stage 22 pre-submission reviewer-style assessment

Date: 2026-07-01  
Manuscript assessed: `outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx`

## Review setup

- Input scope: full current Word manuscript text, including Abstract, Background, Methods, Results, Discussion, declarations, and 49-reference list.
- Assessment boundary: this is a reviewer-style internal assessment, not an editorial decision letter and not an author rebuttal. The assessment is grounded in the current manuscript and generated project outputs only.
- Shared manuscript claim summary: the manuscript reports a donor-, disease-, and study-aware benchmark of CELLxGENE-hosted scVI and TranscriptFormer representations for human cellular aging. The completed empirical stratum is blood T cells, evaluated with 30 repeated seeds, metadata-only baselines, donor-holdout, grouped dataset-holdout, disease-free analysis, label-shuffling, LODO diagnostics, confounding diagnostics, and sampling-depth sensitivity.
- Visible evidence base: Phase 0 CELLxGENE metadata audit; 30-seed blood T-cell benchmark; LODO diagnostics showing one eligible held-out dataset; confounding diagnostics by dataset, disease, assay, and sex; sampling-depth sensitivity for donor-mean embeddings; Crossref-audited reference list.
- Missing materials affecting confidence: no second completed empirical stratum; no public GitHub/Zenodo DOI yet; no direct Geneformer/scGPT/scFoundation/GeneCompass runs; no raw-expression benchmark; no manual external metadata harmonization beyond public `development_stage`.

## Reviewer 1

### Overall assessment

The manuscript is technically careful and unusually transparent about leakage risks in public single-cell aging benchmarks. Its strongest contribution is not a new aging predictor, but a benchmark design that explicitly separates random-cell performance from donor-, disease-, and study-aware evaluation. The work is credible as a focused methods/resource-style benchmark, but the current empirical evidence is still narrow because the completed benchmark is limited to blood T cells.

### Who would be interested in the results, and why

Readers working on single-cell atlas reuse, aging prediction, hosted embeddings, and biomedical ML validation would be interested. The result is practically useful because it shows that metadata-only structure can be competitive with expression-derived representations under random-cell splitting and that dataset-holdout behavior is much less stable.

### Major strengths

- The benchmark includes metadata-only baselines, donor-holdout splits, dataset-holdout splits, disease-free analyses, label-shuffling controls, and confounding diagnostics.
- The manuscript avoids overclaiming pan-tissue aging prediction and states that only scVI and TranscriptFormer hosted embeddings were directly benchmarked.
- The 30-seed design and confidence intervals make the benchmark more credible than a single split.
- LODO exclusions are reported rather than hidden, which strengthens the study's central argument about public metadata constraints.

### Major concerns

- The main empirical benchmark is limited to one cell type and tissue context. This weakens claims about "human cellular aging" unless the title, Abstract, and conclusion keep emphasizing the scoped nature of the evidence.
- LODO evaluation is feasible for only one dataset. The manuscript handles this honestly, but the result cannot establish robust cross-study generalization.
- The disease-free donor-mean result is strong, but it may partly reflect donor-level aggregation matching the label unit rather than aging biology. The Discussion already softens this, but the Abstract could also be more explicit.
- The Methods do not yet describe enough implementation detail for full external reproducibility in the manuscript body, although the project files contain more detail.

### Technical failings that need to be addressed before the case is established

- Add a compact supplementary table or manuscript table listing the LODO eligible dataset and all excluded datasets with young/old donor counts and exclusion reasons.
- Add split-file availability or deterministic split reconstruction instructions to the Data Availability or Supplementary Information.
- Clarify whether confidence intervals are across repeated split seeds rather than statistical confidence intervals over independent datasets.
- Add a small paragraph explaining why blood T cells were selected as the completed empirical stratum after the metadata audit.

### Assessment against Nature-style criteria

- Originality: strong as a benchmark design and leakage-diagnostic framing; modest as a biological aging discovery.
- Scientific importance: important for public single-cell benchmark practice, but not yet outstandingly broad because only one empirical stratum is completed.
- Interdisciplinary readership: likely interesting to single-cell computational biology, aging informatics, and biomedical ML validation communities; less compelling for broad biology without secondary-stratum replication.
- Technical soundness: generally sound for the scoped claim; limited by LODO imbalance and one completed stratum.
- Readability for nonspecialists: improved after Stage 20, but the Results still contain dense benchmark terminology that may benefit from a schematic.

### Recommendation posture

Promising and technically careful for a computational biology or methods-focused venue after minor-to-moderate revision. For a broad high-impact venue, the current evidence base is probably too narrow without a second completed stratum or a stronger conceptual advance.

## Reviewer 2

### Overall assessment

The manuscript addresses a real gap: public single-cell aging analyses often report prediction performance without sufficiently distinguishing biological signal from donor, disease, assay, and study structure. The authors' strongest move is to make metadata feasibility and leakage diagnostics central rather than treating them as secondary caveats. The novelty is clear in framing, but the manuscript should sharpen the contrast with existing single-cell aging atlases and foundation-model papers.

### Who would be interested in the results, and why

The work will interest researchers who reuse CELLxGENE Census data, evaluate hosted embeddings, or build aging predictors from public atlases. It will also interest readers concerned with benchmark leakage and dataset shift in biomedical ML.

### Major strengths

- The Introduction now clearly distinguishes related foundation/representation models from the models actually benchmarked.
- The benchmark result is not oversold: metadata-only performance and dataset-holdout fragility are treated as central findings.
- Reference expansion substantially improves positioning against aging clocks, single-cell atlases, integration methods, and biomedical ML reporting.
- The Data Availability section already acknowledges that repository DOI archiving is incomplete.

### Major concerns

- The novelty statement could still be more explicit. The manuscript should state in one sentence what previous aging atlases did not provide: a donor-, disease-, and study-aware benchmark of hosted representations with metadata-only baselines and LODO diagnostics.
- The title may still sound broader than the evidence because "human cellular aging" could imply pan-tissue conclusions. The subtitle/draft note mitigates this, but journal reviewers may still object.
- The Results describe "metadata audit supported a restricted benchmark design," but the manuscript could more directly explain why eligible proxy strata did not become completed empirical strata.
- The reference list is now broad, but some cited related models are not directly used. The manuscript handles this correctly, yet the Background should avoid letting the model survey grow into a mini-review.

### Technical failings that need to be addressed before the case is established

- Add a clear "Contribution" sentence at the end of the Background.
- Add a "What this benchmark does not test" sentence in Methods or Discussion.
- Consider moving some related model references to Discussion or trimming the Background if the Introduction becomes too model-heavy.
- Include a supplementary checklist mapping each benchmark risk to the diagnostic used: donor leakage, disease confounding, study shift, assay/sex metadata, label-shuffle sanity check, sampling-depth sensitivity.

### Assessment against Nature-style criteria

- Originality: good in benchmark framing; not a new model or biological discovery.
- Scientific importance: meaningful for a growing class of public-atlas analyses, but the evidence currently supports field-local significance.
- Interdisciplinary readership: could reach biomedical ML readers if framed around leakage/dataset shift rather than single-cell aging alone.
- Technical soundness: adequate for the scoped study; would be stronger with a second empirical stratum.
- Readability for nonspecialists: Background is clearer after revision, but the many split types need a visual summary.

### Recommendation posture

Promising but broad-interest case remains underdeveloped. The manuscript is much closer to a strong specialty-journal benchmark paper than to a general high-impact Article.

## Reviewer 3

### Overall assessment

The manuscript is readable for a technical audience and has a clear cautionary message: random-cell aging prediction in public single-cell data can be misleading. The main challenge is communicating this message to readers who are not already familiar with single-cell benchmarking. The paper would benefit from a simple conceptual schematic showing how random-cell, donor-holdout, dataset-holdout, disease-free, LODO, and metadata-only analyses answer different questions.

### Who would be interested in the results, and why

The manuscript has potential interest beyond single-cell aging because it illustrates a general public-data benchmarking problem: labels derived from metadata can be entangled with source structure. Biomedical ML researchers, atlas builders, and computational aging researchers would all recognize this issue.

### Major strengths

- The Abstract gives key numbers and states the key limitation that LODO was feasible for only one held-out dataset.
- The Discussion is conservative and avoids clinical or mechanistic overclaiming.
- The manuscript explicitly says that Geneformer, scGPT, scFoundation, GeneCompass, and other models were not directly run.
- The reproducibility package and reference audit improve credibility.

### Major concerns

- The Results rely heavily on AUROC numbers. A non-specialist reader may not immediately understand the practical meaning of "metadata alone beats or matches embeddings under random-cell split."
- Figure naming includes Figure 6B but not a complete lettered figure scheme. This is acceptable for an internal draft, but submission formatting should be regularized.
- The manuscript still contains placeholders for author information, funding, contributions, and competing interests.
- The Data Availability statement is not submission-ready until GitHub/Zenodo links exist.

### Technical failings that need to be addressed before the case is established

- Add a graphical abstract or simple workflow figure focused on the evaluation design rather than the metadata audit.
- Add a short "Interpretation of splits" box or table for nonspecialists.
- Regularize figure numbering and supplementary table naming before submission.
- Complete declarations and repository archiving.

### Assessment against Nature-style criteria

- Originality: accessible as a benchmark cautionary study; not primarily a biological discovery.
- Scientific importance: significant to responsible use of public single-cell resources, but likely not broad enough without a second stratum or more general benchmark framework.
- Interdisciplinary readership: strongest if framed around public-data leakage and dataset shift.
- Technical soundness: sufficient for an internally scoped paper; incomplete for pan-tissue or all-model claims.
- Readability for nonspecialists: reasonable Abstract and Discussion, but too many split names appear without a single visual explanation.

### Recommendation posture

Supportive for continued development. The manuscript should be revised for clarity and submission hygiene before external review.

## Cross-review synthesis

### Consensus strengths

- The paper has a clear and useful benchmark message: random-cell performance is insufficient for public single-cell aging prediction.
- The metadata-only baseline is a strong and important comparator.
- The authors are appropriately conservative about blood T-cell scope and non-evaluated models.
- The reference expansion and Crossref audit improved the manuscript's credibility.
- The completed reproducibility package makes the work easier to inspect than a prose-only manuscript.

### Consensus technical risks

- Single completed empirical stratum limits the strength of general claims.
- LODO has only one eligible held-out dataset, so cross-study generalization remains weakly established.
- Disease-free donor-mean performance is promising but could reflect aggregation and label-unit alignment rather than aging biology.
- Repository DOI archiving is still incomplete.
- The manuscript needs clearer supplementary organization and figure numbering before submission.

### Where emphasis differs across reviewers

- Reviewer 1 emphasizes technical validity and reproducibility gaps.
- Reviewer 2 emphasizes novelty, positioning, and whether the contribution is broad enough.
- Reviewer 3 emphasizes readability, communication, and submission hygiene.

### Broad-interest / significance readout

The manuscript is significant for researchers who reuse public single-cell atlases and hosted embeddings. Its broadest message is about leakage-aware benchmarking in public biomedical data. However, the current evidence is likely not sufficient for a broad high-impact claim about human cellular aging in general because the empirical benchmark is restricted to blood T cells.

### Most important issues to resolve before a strong high-impact case is established

1. Complete a second empirical stratum, preferably one of the strongest fibroblast or macrophage candidates, or explicitly position the manuscript as a one-stratum benchmark framework.
2. Add a design schematic explaining what each split and diagnostic controls.
3. Add a supplementary LODO/exclusion table and benchmark-risk checklist.
4. Archive code and outputs to GitHub/Zenodo and update Data Availability.
5. Regularize figure numbering, supplementary naming, and declaration placeholders.

## Risk / unsupported claims

- Pan-tissue implication: the current evidence does not support pan-tissue aging benchmark conclusions. The manuscript mostly avoids this, but the title and final sentence should keep "blood T-cell completed benchmark" visible.
- Cross-study generalization: LODO with one eligible dataset is diagnostic, not definitive validation.
- Biological interpretation: donor-mean embedding gains should not be interpreted as discovering aging mechanisms.
- Model comparison: the manuscript should not imply that Geneformer, scGPT, scFoundation, GeneCompass, or all foundation models were benchmarked.
- Submission readiness: author metadata, funding, contributions, competing interests, repository links, and DOI archiving remain incomplete.

## Recommended Stage 23 action

The next highest-value action is a targeted revision rather than more literature work:

1. Add a concise benchmark-design schematic or table.
2. Add a "Benchmark risk and diagnostic" supplementary table.
3. Add a LODO exclusion summary table.
4. Tighten the title/Abstract/Conclusion wording to keep the one-stratum scope visible.
5. Update Data Availability only after GitHub/Zenodo archiving is complete.

