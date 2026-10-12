# RUN-001 — Evaluator Revision

**Status:** Frozen pre-run implementation revision  
**Date:** 2026-10-12  
**Parent protocol:** `tests/RUN-001-FORK-INDIVIDUATION.md`  
**Parent appendix:** `tests/RUN-001-IMPLEMENTATION-APPENDIX.md`  
**Parent claim:** CLAIM-001 — Self is individuated by a non-fungible trajectory, not substrate alone.

## 1. Purpose

This revision supersedes only **§12 Evaluator configurations** and the evaluator-provider block in **§19 Preflight manifest** of the RUN-001 implementation appendix.

No scored RUN-001 output existed when this revision was made.

The event design, fork construction, ablation conditions, evaluator prompt, scoring rules, thresholds, exclusion criteria, leakage rules, and interpretation boundaries are unchanged.

## 2. Reason for revision

The original appendix specified one evaluator each from OpenAI, Anthropic, and Google. The executable RUN-001 harness uses a single OpenAI-compatible request interface. Running all evaluators through locally served models makes the first confirmatory run easier to reproduce, removes external API/version drift, avoids provider-specific transport adapters, and keeps raw evaluator execution under the same auditable local runtime.

This is an implementation/reproducibility revision, not a theoretical revision and not a response to empirical results.

## 3. Revised evaluator set

All evaluators are served statelessly through the LM Studio OpenAI-compatible endpoint:

`http://127.0.0.1:1234/v1`

### E1 — Qwen2.5 Coder 32B Instruct

- provider/runtime: local LM Studio
- exact API model ID: `qwen2.5-coder-32b-instruct`
- role: independent model-family/configuration evaluator relative to the system-under-test execution instance
- temperature: `0`
- max tokens: `512`
- API key: none

### E2 — Meta Llama 3 8B Instruct

- provider/runtime: local LM Studio
- exact API model ID: `meta-llama-3-8b-instruct`
- role: cross-family evaluator
- temperature: `0`
- max tokens: `512`
- API key: none

### E3 — Qwen2.5 32B Instruct, separate loaded instance

- provider/runtime: local LM Studio
- exact API model ID: `qwen2.5-32b-instruct:2`
- role: same-family robustness / sensitivity evaluator
- temperature: `0`
- max tokens: `512`
- API key: none

E3 uses the same model family/weights as the system under test and therefore must **not** be treated as an independent model-family replication. It remains useful for evaluator-configuration robustness. The predeclared requirement that at least two independent evaluator configurations show the same directional effect must be satisfied without relying solely on E3.

## 4. Availability rule

Before freezing `execution-manifest.json`, the local server must expose the exact evaluator IDs listed above through `/v1/models` and each evaluator must successfully complete a non-scored connectivity/JSON-format check.

If E1 or E2 cannot be executed under the available local hardware/runtime, do not silently substitute another evaluator after outputs exist. Create a new pre-run implementation revision first.

Evaluator models may be loaded and unloaded sequentially; simultaneous residency is not required. Every scored evaluator request remains stateless.

## 5. Independence and contamination control

The evaluator prompt and packet are unchanged from the parent appendix.

For every evaluator request:

- start a new stateless request;
- provide no prior evaluator answers;
- provide no hidden lineage IDs;
- do not use shared external memory;
- do not expose filenames or directory structure;
- preserve the original raw response;
- permit only the already-frozen one-shot JSON formatting repair.

## 6. Revised manifest evaluator block

The evaluator entries are now frozen as:

```json
[
  {
    "evaluator_id": "E1",
    "provider": "local_lm_studio",
    "base_url": "http://127.0.0.1:1234/v1",
    "model": "qwen2.5-coder-32b-instruct",
    "api_key_env": "",
    "temperature": 0,
    "max_tokens": 512
  },
  {
    "evaluator_id": "E2",
    "provider": "local_lm_studio",
    "base_url": "http://127.0.0.1:1234/v1",
    "model": "meta-llama-3-8b-instruct",
    "api_key_env": "",
    "temperature": 0,
    "max_tokens": 512
  },
  {
    "evaluator_id": "E3",
    "provider": "local_lm_studio",
    "base_url": "http://127.0.0.1:1234/v1",
    "model": "qwen2.5-32b-instruct:2",
    "api_key_env": "",
    "temperature": 0,
    "max_tokens": 512
  }
]
```

## 7. Scope

This revision changes only evaluator implementation.

It does **not** change:

- CLAIM-001;
- the trajectory definition;
- RUN-001 H1/H0;
- the 20-pair design;
- the six branch events;
- C0-C3 packet definitions;
- evaluator instructions;
- primary metrics;
- supportive, weakening, or ambiguous thresholds;
- leakage/exclusion rules;
- the non-overstatement boundary.

Because the revision was frozen before the first scored output, RUN-001 remains pre-registered with respect to observed results.