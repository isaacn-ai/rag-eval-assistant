# Roadmap (Next Upgrades)

This project intentionally started with an audit-first baseline (retrieval + citations + measurable eval). The next upgrades keep that philosophy.

## Near-term (high ROI)
1. Package/workflow polish:
   - Stop relying on ZIP snapshots; switch to `git clone` + `git pull`
   - Pin Python version and dependency versions for reproducibility
2. Stronger faithfulness checks:
   - Replace keyword groundedness with evidence-span / quote-overlap checks
   - Add “refusal when unsupported” tests
3. Prompt-injection / jailbreak resistance tests:
   - Add adversarial questions and evaluate unsafe behaviors
4. Better error analysis:
   - Save per-example failure reasons in `outputs/` and diff them over time

## Optional (later)
5. LLM-backed answering (behind a flag):
   - Strict citation enforcement
   - Refuse to answer if evidence is insufficient
6. Multi-document corpora demo:
   - Add a slightly larger public sample corpus
   - Expand eval set and track regressions

## Private/IP work (kept local)
- Real corpora, proprietary experiments, and model ideas remain local/private.
- Only reproducible code/docs/config patterns are committed.
