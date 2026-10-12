# RUN-001 Execution

This directory contains the executable harness for `RUN-001 — Fork Individuation`.

The confirmatory harness is intentionally fail-closed. It will not generate scored outputs until `execution-manifest.json` is fully populated and frozen.

## Files

- `run001_harness.py` — base generation/evaluation implementation.
- `run001_harness_v2.py` — confirmatory entry point containing the pre-run freeze and scoring corrections recorded in v0.1.2.
- `execution-manifest.template.json` — preflight template pinned to the frozen protocol, implementation appendix, scoring clarification, and harness commits.
- `execution-manifest.json` — local runtime-specific manifest created during preflight. Do not commit secrets; API keys are referenced only by environment-variable name.
- `artifacts/` — generated raw traces, packets, evaluations, audit, and score files.

Use `run001_harness_v2.py` for every confirmatory command.

## 1. Start LM Studio

Load the exact Qwen2.5-32B-Instruct artifact selected for RUN-001 and enable the OpenAI-compatible local server at the manifest endpoint, default:

```text
http://127.0.0.1:1234/v1
```

Do not begin confirmatory generation yet.

## 2. Preflight

From the repository root:

```bash
python3 tests/run001/run001_harness_v2.py preflight \
  --model-file "/absolute/path/to/the/model-file" \
  --quantization "EXACT_QUANTIZATION" \
  --context-length EXACT_CONTEXT_LENGTH \
  --runner-version "EXACT_LM_STUDIO_VERSION" \
  --seed-supported true
```

If LM Studio exposes more than one loaded model, add:

```bash
--model-id "EXACT_ID_RETURNED_BY_/v1/models"
```

The preflight command captures:

- exact API model ID;
- SHA-256 of the local model artifact;
- OS fingerprint;
- hardware summary;
- runner/runtime settings.

It writes `tests/run001/execution-manifest.json`.

## 3. Fill evaluator runtime fields

Edit only the runtime fields that the appendix explicitly permits at preflight. Fill E1/E2/E3 with exact evaluator provider, OpenAI-compatible base URL, exact model ID, and the environment-variable name containing the API key.

Do not put an API secret in the manifest.

If an evaluator is local and needs no API key, set `api_key_env` to an empty string.

## 4. Freeze

Once the runtime/evaluator placeholders are filled:

```bash
python3 tests/run001/run001_harness_v2.py freeze
```

The freeze command itself supplies the freeze timestamp and canonical manifest SHA-256. It changes the manifest status to `frozen_pre_run`.

After this command, do not alter the frozen manifest for the confirmatory run.

## 5. Generate the fork pairs

```bash
python3 tests/run001/run001_harness_v2.py generate
```

The harness refuses to overwrite a non-empty artifact directory.

Generation produces all 20 fork pairs, raw branch traces, hidden ground truth, canonical predecessor checkpoint hashes, and C0-C3 evaluator packets.

## 6. Leakage audit

Run before interpreting scores:

```bash
python3 tests/run001/run001_harness_v2.py audit
```

This is a mechanical first-pass audit. The predeclared blinded leakage review still remains required before a supportive classification is finalized.

## 7. Evaluate

Set any evaluator API-key environment variables named in the manifest, then run:

```bash
python3 tests/run001/run001_harness_v2.py evaluate
```

The original evaluator response is always preserved. A malformed JSON response receives exactly one protocol-permitted formatting repair attempt; both outputs are retained.

## 8. Score

```bash
python3 tests/run001/run001_harness_v2.py score
```

The scorer writes:

```text
tests/run001/artifacts/scores.json
```

Per `RUN-001-SCORING-CLARIFICATION.md`, trajectory lift uses **correct-path resolution rate across all valid evaluations**. Forced-choice accuracy and insufficient-evidence rate remain separate diagnostics.

A threshold-passing result is labeled `provisionally_supportive_pending_leakage_audit`, not final support, until the exclusion and leakage review is complete.

## Non-overstatement rule

RUN-001 tests whether post-fork occupied history provides lineage-resolution information beyond shared starting state/specification and observable terminal-state controls. It does not by itself prove numerical identity, consciousness, or the entire theory of individuation.
