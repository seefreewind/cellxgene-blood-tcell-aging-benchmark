.PHONY: audit upgrade manuscript render all

PYTHON ?= .venv/bin/python

audit:
	$(PYTHON) analysis/metadata_feasibility_audit.py
	$(PYTHON) analysis/enhance_metadata_outputs.py
	$(PYTHON) analysis/create_figures.py

upgrade:
	$(PYTHON) analysis/upgrade_blood_tcell_benchmark.py

manuscript:
	$(PYTHON) manuscript/build_submission_ready_benchmark_v2.py

render:
	$(PYTHON) /Users/zy/.codex/plugins/cache/openai-primary-runtime/documents/26.623.12021/skills/documents/render_docx.py outputs/donor_disease_aware_sc_aging_submission_ready_v2.docx --output_dir outputs/rendered_submission_ready_v2 --emit_pdf

all: audit upgrade manuscript render
