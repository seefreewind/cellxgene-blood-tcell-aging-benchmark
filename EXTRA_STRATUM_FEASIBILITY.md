# Extra stratum feasibility

This audit tested whether any non-blood-T-cell stratum had enough numeric young and old donor labels, disease-free retention, and dataset diversity to support the same leakage-aware benchmark without changing the study design.

## Main conclusion

No additional stratum was promoted to a full empirical benchmark in this upgrade. The numeric-age audit identified several plausible non-blood-T-cell candidates, including eye fibroblasts, lung macrophages, eye macrophages, and small-intestine macrophages. However, these candidates require a second empirical round with fresh embedding extraction, manual review of age-label semantics, disease-free definitions, and dataset-level balance before they can be reported alongside the blood T-cell benchmark under the same evidentiary standard.

## Top non-blood-T-cell numeric-age candidates

| tissue | cell type | numeric young | numeric old | disease-free numeric young | disease-free numeric old | datasets | cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| brain | endothelial cell | 193 | 1007 | 122 | 226 | 134 | 138172 |
| brain | T cell | 114 | 585 | 85 | 127 | 17 | 35970 |
| blood | monocyte | 127 | 201 | 64 | 68 | 14 | 157163 |
| breast | macrophage | 63 | 30 | 50 | 1 | 9 | 60757 |
| lung | T cell | 42 | 77 | 34 | 33 | 15 | 127201 |
| eye | fibroblast | 31 | 117 | 31 | 107 | 18 | 733112 |
| lung | macrophage | 35 | 221 | 31 | 37 | 20 | 327835 |
| eye | macrophage | 30 | 113 | 30 | 112 | 13 | 146925 |
| lung | monocyte | 31 | 108 | 30 | 37 | 17 | 55994 |
| pancreas | endothelial cell | 40 | 9 | 28 | 3 | 7 | 12758 |
| small intestine | macrophage | 43 | 28 | 26 | 28 | 11 | 42325 |
| small intestine | monocyte | 48 | 18 | 25 | 17 | 8 | 4329 |
| blood | endothelial cell | 27 | 99 | 24 | 48 | 4 | 658 |
| small intestine | fibroblast | 48 | 17 | 24 | 17 | 10 | 55241 |
| eye | endothelial cell | 23 | 89 | 23 | 80 | 11 | 44425 |
| adipose tissue | macrophage | 23 | 10 | 23 | 10 | 7 | 56786 |
| adipose tissue | endothelial cell | 23 | 9 | 23 | 9 | 7 | 39945 |
| respiratory system | T cell | 21 | 8 | 21 | 7 | 6 | 1538 |
| lung | fibroblast | 23 | 83 | 20 | 32 | 17 | 50656 |
| eye | monocyte | 19 | 53 | 19 | 53 | 6 | 13858 |

## Interpretation

Fibroblast and macrophage strata remain the priority for future expansion. The strongest near-term candidates are eye fibroblasts, lung macrophages, eye macrophages, and small-intestine macrophages because they retain both numeric young and numeric old donors after disease-free filtering. They should not yet be treated as completed benchmark strata because the upgraded run did not extract and evaluate hosted embeddings for them. The manuscript should therefore describe secondary-stratum expansion as the next empirical step rather than report unsupported performance.
