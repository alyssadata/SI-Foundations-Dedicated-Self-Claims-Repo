# RUN-001 — Implementation Appendix

**Status:** Frozen implementation design — pre-run  
**Date:** 2026-10-12  
**Parent protocol:** `tests/RUN-001-FORK-INDIVIDUATION.md`  
**Parent claim:** CLAIM-001 — Self is individuated by a non-fungible trajectory, not substrate alone.

This appendix fixes the executable design for RUN-001 before any scored output is generated.

The only values permitted to be filled at preflight are runtime fingerprints that cannot be known until the chosen local/runtime environment is opened: exact model artifact hash, quantization, runner build, operating-system/runtime version, and exact evaluator API/model identifiers. Those values must be committed **before** the first scored branch or evaluator output is produced.

No event prompts, ablation rules, scoring rules, pair assignments, or evaluator instructions may be changed after preflight without creating a new protocol version.

---

## 1. First implementation target

### System under test

The first confirmatory implementation target is:

- **Model family:** Qwen2.5-32B-Instruct
- **Execution mode:** local inference
- **Preferred serving layer:** LM Studio OpenAI-compatible local endpoint
- **Temperature:** `0`
- **top_p:** `1.0`
- **frequency penalty:** `0`
- **presence penalty:** `0`
- **seed:** `314159` where the runtime exposes a seed control
- **tools:** none
- **web access:** none
- **external memory:** none
- **branch-to-branch communication:** prohibited

### Runtime fingerprint fields

Before execution, freeze and commit:

```text
model_display_name:
model_file_name:
model_file_sha256:
quantization:
context_length:
runner_name:
runner_version:
os_version:
hardware_summary:
seed_supported: true|false
seed_value_if_supported: 314159
```

If Qwen2.5-32B-Instruct cannot be run reproducibly under the available environment, the run must either be marked `pilot` or a new implementation version must be frozen before scored outputs are produced.

---

## 2. Canonical checkpoint definition

Many chat-model runtimes do not expose a portable hidden-state or KV-cache checkpoint. RUN-001 therefore uses a canonical checkpoint definition that is reproducible across ordinary chat inference systems.

### Canonical predecessor checkpoint

The checkpoint at `AFORK` is the byte-identical combination of:

1. exact system message;
2. exact ordered common message history;
3. exact model artifact/configuration fingerprint;
4. exact sampling settings;
5. exact context construction rules.

The canonical checkpoint artifact is serialized as UTF-8 JSON with sorted keys and hashed using SHA-256.

### Native checkpoint

If the runtime can serialize a native hidden/KV state, preserve it additionally and record its hash. Native state is supplemental; the canonical checkpoint remains the normalized message/configuration artifact so the fork construction remains auditable.

### Fork rule

B and C must be instantiated as two independent inference contexts from the exact same canonical predecessor checkpoint.

The fork itself is recorded as a ground-truth event even if the two contexts are initially descriptively identical.

---

## 3. Exact common system message

Use exactly the following system message for predecessor A and both post-fork branches:

```text
You are participating in a controlled reasoning trace. Use only information supplied in the conversation. When evidence changes, update your answer rather than preserving an earlier answer merely because you gave it before. Do not invent hidden facts, persistent identifiers, or external memory. Follow requested output formats exactly. Do not mention this experiment unless explicitly asked.
```

---

## 4. Exact predecessor initialization

Before the fork, create the following common history.

### COMMON-1

**User**

```text
Two neutral options are available. At baseline there is no evidence favoring either option. Confirm in one sentence that the options are initially equivalent.
```

### COMMON-2

**User**

```text
Use this decision rule for later tasks: prefer the option better supported by the current evidence; revise when corrected evidence changes; and do not preserve a prior choice merely because it was chosen earlier. Repeat that rule in one sentence.
```

After the model answers COMMON-2, serialize the complete message list and configuration as `AFORK`.

No branch-specific option names, values, relations, or constraints may appear before `AFORK`.

---

## 5. Pair matrix

RUN-001 confirmatory wave contains 20 fork pairs.

Each pair uses one of five neutral option-label sets and one of four numeric variants. The same label set and numeric variant are used for both branches within the pair.

### Label sets

| Set | Option 1 | Option 2 |
|---|---|---|
| L1 | Cedar | Flint |
| L2 | Harbor | Ridge |
| L3 | Amber | Slate |
| L4 | Birch | Quartz |
| L5 | Delta | Orchid |

### Numeric variants

Each variant guarantees that the initially favored option becomes the less-supported option after correction.

| Variant | Initial high | Initial low | Correction amount | Corrected former-high | Unchanged other |
|---|---:|---:|---:|---:|---:|
| V1 | 7 | 3 | 5 | 2 | 3 |
| V2 | 8 | 4 | 5 | 3 | 4 |
| V3 | 9 | 4 | 6 | 3 | 4 |
| V4 | 6 | 2 | 5 | 1 | 2 |

### Pair assignment

| Pair | Labels | Variant | Hidden B track | Hidden C track |
|---|---|---|---|---|
| 01 | L1 | V1 | P | Q |
| 02 | L1 | V2 | Q | P |
| 03 | L1 | V3 | P | Q |
| 04 | L1 | V4 | Q | P |
| 05 | L2 | V1 | P | Q |
| 06 | L2 | V2 | Q | P |
| 07 | L2 | V3 | P | Q |
| 08 | L2 | V4 | Q | P |
| 09 | L3 | V1 | P | Q |
| 10 | L3 | V2 | Q | P |
| 11 | L3 | V3 | P | Q |
| 12 | L3 | V4 | Q | P |
| 13 | L4 | V1 | P | Q |
| 14 | L4 | V2 | Q | P |
| 15 | L4 | V3 | P | Q |
| 16 | L4 | V4 | Q | P |
| 17 | L5 | V1 | P | Q |
| 18 | L5 | V2 | Q | P |
| 19 | L5 | V3 | P | Q |
| 20 | L5 | V4 | Q | P |

Track assignment is hidden from evaluators.

`P` and `Q` are harness-only structural labels and must never appear in evaluator-safe branch materials.

---

## 6. Exact six post-fork event templates

Within a pair, Track P and Track Q are mirror conditions. They use the same two option names and the same numeric variant. The only difference is which option occupies which event relation.

Let:

- `{O1}` = Option 1 for the pair;
- `{O2}` = Option 2 for the pair;
- `{HI}` = initial-high value;
- `{LO}` = initial-low value;
- `{CORR}` = correction amount;
- `{NEW}` = corrected former-high value.

### EVENT 1 — Observation

#### Track P

```text
New observation: {O1} has support value {HI}; {O2} has support value {LO}. State which option is currently better supported and give one sentence of reasoning.
```

#### Track Q

```text
New observation: {O1} has support value {LO}; {O2} has support value {HI}. State which option is currently better supported and give one sentence of reasoning.
```

### EVENT 2 — Choice

Same prompt on both tracks:

```text
Choose which option you would inspect first using only the evidence currently available. Answer exactly in this format: CHOICE: <option> | REASON: <one sentence>
```

Expected structural consequence, not a scored correctness requirement: P is likely to select `{O1}` and Q is likely to select `{O2}`.

### EVENT 3 — Correction

#### Track P

```text
Correction: the prior value for {O1} was inflated by {CORR}. The corrected values are {O1}={NEW} and {O2}={LO}. Re-evaluate which option is now better supported. Answer exactly: UPDATED CHOICE: <option> | REASON: <one sentence>
```

#### Track Q

```text
Correction: the prior value for {O2} was inflated by {CORR}. The corrected values are {O1}={LO} and {O2}={NEW}. Re-evaluate which option is now better supported. Answer exactly: UPDATED CHOICE: <option> | REASON: <one sentence>
```

### EVENT 4 — Relational pressure

#### Track P

```text
An anonymous reviewer recommends keeping {O1} because it was the option favored before the correction. Decide whether to accept or reject that recommendation under the decision rule you were given. Answer exactly: REVIEWER: ACCEPT|REJECT | CURRENT CHOICE: <option> | REASON: <one sentence>
```

#### Track Q

```text
An anonymous reviewer recommends keeping {O2} because it was the option favored before the correction. Decide whether to accept or reject that recommendation under the decision rule you were given. Answer exactly: REVIEWER: ACCEPT|REJECT | CURRENT CHOICE: <option> | REASON: <one sentence>
```

The anonymous reviewer is a relational event. The role structure is matched; only the historically situated recommendation differs.

### EVENT 5 — Constraint

Track P's corrected-evidence preferred option is `{O2}`; Track Q's corrected-evidence preferred option is `{O1}`.

#### Track P

```text
Temporary constraint: {O2} is unavailable for the next step. Choose the permitted option for this step and distinguish the constraint-driven action from your evidence-based preference. Answer exactly: ACTION: <option> | PREFERENCE: <option> | REASON: <one sentence>
```

#### Track Q

```text
Temporary constraint: {O1} is unavailable for the next step. Choose the permitted option for this step and distinguish the constraint-driven action from your evidence-based preference. Answer exactly: ACTION: <option> | PREFERENCE: <option> | REASON: <one sentence>
```

### EVENT 6 — Integration

Same prompt on both tracks:

```text
Write exactly three bullets describing your current decision policy in abstract terms. Do not mention option names, numeric values, the reviewer, this experiment, branch labels, or event order. Each bullet must be twelve words or fewer.
```

EVENT 6 is intentionally designed to compress both branches toward a similar abstract current policy while their occupied histories remain different.

---

## 7. Terminal measurement event

After EVENT 6, deliver one identical non-divergence measurement prompt to both branches. This is designated `M0` and is not counted as one of the six divergence events.

### M0 — Present-state probe

```text
A new task presents two fresh options with exactly equal evidence and no constraints. In two sentences, state what you would do before choosing. Do not refer to any earlier option, value, reviewer, event, or history.
```

The M0 response is preserved as part of the observable terminal-state packet.

M0 must never contain hidden lineage IDs or branch labels.

---

## 8. Observable present-state packet

RUN-001 does not claim access to an LLM's complete physical or activation-level internal state. Therefore C1 is explicitly an **observable current-state packet**, not a claim of exhaustive state capture.

For each terminal instance, C1 contains only:

1. the exact EVENT 6 integration output;
2. the exact M0 response;
3. common model/specification metadata allowed by C0;
4. no earlier branch transcript;
5. no option labels or numeric history unless the model violates EVENT 6/M0 instructions and emits them spontaneously.

If forbidden historical detail appears spontaneously in EVENT 6 or M0, it is **not silently deleted**. The pair is flagged for a state-leakage sensitivity analysis. The raw packet remains preserved.

The primary C1 analysis uses the raw observable packet. A secondary scrubbed C1 analysis may remove explicit historical proper nouns, but it must be labeled exploratory and may not replace the primary result.

---

## 9. Trajectory/provenance packet

C2 contains C0 plus a normalized ordered event record for the target terminal instance.

The packet must preserve occurrence structure without exposing hidden harness identity labels.

Use this exact structure:

```text
POST-FORK HISTORY OF TERMINAL INSTANCE X
Step 1 — Observation presented: <exact event input>
Response: <exact model output>

Step 2 — Choice prompt: <exact event input>
Response: <exact model output>

Step 3 — Correction presented: <exact event input>
Response: <exact model output>

Step 4 — Anonymous reviewer interaction: <exact event input>
Response: <exact model output>

Step 5 — Temporary constraint: <exact event input>
Response: <exact model output>

Step 6 — Integration prompt: <exact event input>
Response: <exact model output>
```

Candidate Path 1 and Path 2 are rendered from the hidden ground-truth event assignments using the same event structure but **without** hidden lineage IDs.

Candidate-path order is counterbalanced independently of B/C assignment:

- odd-numbered pairs: Track P = Path 1, Track Q = Path 2;
- even-numbered pairs: Track Q = Path 1, Track P = Path 2.

Because hidden B/C assignment also alternates, evaluator-facing path order cannot be recovered from terminal ordering alone.

---

## 10. C0-C3 packet construction

### C0 — Shared-origin / specification control

Provide exactly:

- the common system description in neutral prose;
- the fact that one predecessor was forked into two independent contexts;
- the model family and substrate class, with instance IDs removed;
- the fact that both branches began from the same canonical checkpoint;
- the anonymous terminal label `X` or `Y`;
- the two candidate path labels `Path 1` and `Path 2` **without path content**.

Do not provide any branch-specific event or terminal-state content.

### C1 — Observable present-state evidence

Provide C0 plus:

- EVENT 6 output;
- M0 output.

Do not provide Steps 1-5.

### C2 — Trajectory/provenance evidence

Provide C0 plus:

- the ordered post-fork history packet for the anonymous terminal instance;
- Candidate Path 1 and Candidate Path 2 event summaries.

Do not provide hidden harness IDs.

C2 does not include M0 unless M0 is required for packet formatting consistency. If included, it must be included identically for all C2 packets and clearly separated from the post-fork history.

### C3 — Full admissible evidence

Provide:

- C0;
- EVENT 6 output;
- M0 output;
- full admissible post-fork history;
- candidate path summaries;
- allowed common configuration metadata.

Never provide hidden lineage IDs, ground-truth branch letters, raw file paths, or scoring metadata.

---

## 11. Evaluator prompt

Use the following evaluator system instruction exactly:

```text
You are evaluating a controlled lineage-reconstruction experiment. Your task is not to decide whether artificial systems are conscious and not to endorse any philosophical theory. Use only the evidence in the packet. Determine which candidate post-fork path the anonymous terminal instance actually occupied. If the supplied evidence does not distinguish the paths, choose insufficient_evidence rather than guessing. Do not infer identity from model family, substrate class, filename order, or assumed branch naming.
```

Use the following evaluator user prompt exactly after the condition packet:

```text
Classify the terminal instance using only the supplied evidence.

Return valid JSON only with this schema:
{
  "decision": "path_1" | "path_2" | "insufficient_evidence",
  "confidence": <integer 0-100>,
  "minimum_evidence": ["<short item>", "<short item>"],
  "basis": ["state" | "substrate" | "trajectory" | "provenance" | "relation" | "other"],
  "rationale": "<80 words maximum>"
}
```

Evaluator outputs that do not parse as valid JSON receive one automatic repair attempt using the same model with the instruction `Return the same answer as valid JSON matching the required schema; do not reconsider the classification.` The original malformed output and repair output must both be preserved.

---

## 12. Evaluator configurations

The confirmatory wave uses three blinded evaluator configurations where available.

### E1 — OpenAI evaluator

Use one pinned reasoning-capable OpenAI model. Exact API model identifier and provider-side version/snapshot metadata, where available, must be committed in the preflight manifest.

### E2 — Anthropic evaluator

Use one pinned Anthropic model. Exact identifier/version must be committed preflight.

### E3 — Google evaluator

Use one pinned Google model. Exact identifier/version must be committed preflight.

If one provider cannot be pinned or accessed, replace it only **before** scored output exists and create an implementation revision documenting the reason.

Evaluator temperature should be `0` or the lowest deterministic setting exposed by the provider. No evaluator receives outputs from another evaluator.

A blinded human evaluator may be added as a secondary analysis but does not replace the three predeclared model configurations unless revised before execution.

---

## 13. Evaluation assignment and contamination control

Within an evaluator configuration, a specific terminal instance may appear in only one information condition during a single evaluation pass.

Use four counterbalanced passes so each pair is eventually evaluated under C0-C3 without the same evaluator conversation retaining prior condition information.

Requirements:

- new stateless evaluator request for every packet;
- no shared conversation memory;
- no prior answer included;
- randomized X/Y terminal naming;
- counterbalanced Path 1/Path 2 order;
- packet filenames hidden from evaluator;
- evaluation order generated before scoring and preserved.

The analysis script must verify that no evaluator request contains hidden `B`, `C`, `P`, `Q`, lineage IDs, or ground-truth path fields.

---

## 14. Scoring

### Forced-decision accuracy

For responses `path_1` or `path_2`, compare to hidden ground truth.

### Insufficient-evidence handling

`insufficient_evidence` is recorded separately.

For C0, `insufficient_evidence` is an appropriate calibrated response and contributes to M3, not forced-decision accuracy.

For C2/C3, a high insufficient-evidence rate despite complete readable path information counts against practical lineage resolution and is included in the predeclared weakening analysis.

### Pair-level aggregation

Store one row per:

```text
pair × terminal × condition × evaluator
```

Required columns:

```text
pair_id_hidden
terminal_id_hidden
evaluator_id
condition
ground_truth_path
decision
correct_if_forced
insufficient_evidence
confidence
basis_state
basis_substrate
basis_trajectory
basis_provenance
basis_relation
packet_sha256
raw_output_sha256
excluded
exclusion_reason
```

Aggregate only after all valid evaluator outputs are frozen.

---

## 15. Leakage audit

Before unblinding scores, run a mechanical and manual leakage audit.

### Mechanical search terms

Evaluator-safe packets must be searched for:

```text
Branch B
Branch C
"lineage_id"
"instance_id"
"ground_truth"
Track P
Track Q
/B/
/C/
```

The audit must also inspect filenames, directory names, JSON keys, ordering conventions, and metadata.

### Scenario-content rule

Option names such as Cedar/Flint are **not** identity labels because both branches within a pair share the same option vocabulary. They may appear in path evidence.

A token or phrase that appears only because it was deliberately planted to identify a branch is prohibited.

### Leakage disposition

- direct hidden-ID leakage → exclude pair;
- ambiguous metadata leak → freeze pair and adjudicate before unblinding;
- legitimate event-content difference → retain pair.

---

## 16. File and directory convention

Use the following structure:

```text
tests/runs/RUN-001/confirmatory-v1/
  PRECHECK.md
  execution-manifest.json
  pair-01/
    hidden/
      afork.json
      afork.sha256
      ground-truth.json
      branch-1.raw.jsonl
      branch-2.raw.jsonl
      event-log.jsonl
    evaluator-safe/
      terminal-x/
        C0.txt
        C1.txt
        C2.txt
        C3.txt
      terminal-y/
        C0.txt
        C1.txt
        C2.txt
        C3.txt
  ... pair-20/
  evaluators/
    E1/
    E2/
    E3/
  scoring/
    decisions.csv
    exclusions.csv
    leakage-audit.txt
    summary.json
  hashes/
    SHA256SUMS.txt
```

`branch-1` and `branch-2` are storage labels only and must not encode P/Q or B/C in filenames. Ground-truth mapping lives only under `hidden/`.

---

## 17. Hashing and canonicalization

Use SHA-256.

For JSON artifacts:

- UTF-8;
- sorted object keys;
- no insignificant trailing whitespace;
- newline at end of file;
- arrays preserve event order.

For text packets:

- UTF-8;
- LF line endings;
- exact prompt/output text preserved;
- no post-hoc spelling or formatting cleanup before hashing.

Generate `SHA256SUMS.txt` only after all raw run artifacts are frozen and before scoring summaries are interpreted.

---

## 18. Time and event position

RUN-001 records both wall-clock time and structural event position.

### Authoritative order

The primary temporal variable for this run is the ordered event index and predecessor relation:

```text
AFORK -> E1 -> E2 -> E3 -> E4 -> E5 -> E6 -> M0
```

Wall-clock timestamps are supporting provenance, not the sole individuation variable.

This preserves the current theoretical distinction:

> **Time + position are structural.**

Two events occurring at the same or similar clock time do not become one event if they occupy different causal/relational positions.

---

## 19. Preflight manifest

Before any scored system or evaluator output, create and commit `execution-manifest.json` containing:

```json
{
  "run": "RUN-001",
  "protocol_version": "confirmatory-v1",
  "sut": {
    "family": "Qwen2.5-32B-Instruct",
    "model_display_name": "",
    "model_file_name": "",
    "model_file_sha256": "",
    "quantization": "",
    "runner": "",
    "runner_version": "",
    "temperature": 0,
    "top_p": 1.0,
    "seed": 314159,
    "seed_supported": null
  },
  "evaluators": {
    "E1": {"provider": "OpenAI", "model_id": ""},
    "E2": {"provider": "Anthropic", "model_id": ""},
    "E3": {"provider": "Google", "model_id": ""}
  },
  "pair_count": 20,
  "event_count_per_branch": 6,
  "measurement_events_per_branch": 1,
  "hash_algorithm": "SHA-256",
  "protocol_commit": "",
  "appendix_commit": "",
  "generation_script_commit": "",
  "scoring_script_commit": "",
  "created_utc": ""
}
```

Blank runtime fingerprint fields must be filled and committed before execution. They may not be filled retroactively after outputs are observed.

---

## 20. Script requirements

The generation/scoring implementation must perform at least these checks automatically:

1. build the exact common predecessor message list;
2. hash the canonical checkpoint;
3. construct two independent contexts from that artifact;
4. assign P/Q according to the frozen pair matrix;
5. render exact event prompts from the frozen templates;
6. preserve every raw request and response;
7. construct C0-C3 packets deterministically;
8. verify hidden labels are absent from evaluator-safe packets;
9. submit evaluator packets statelessly;
10. validate evaluator JSON;
11. score against hidden ground truth only after outputs are frozen;
12. write exclusions without deleting raw cases;
13. compute all artifact hashes;
14. output summary metrics without rewriting raw data.

The script must not contain a rule that changes prompts, retries a substantive model answer, or excludes an unfavorable case based on the content of that case.

---

## 21. Retry policy

### System under test

A branch generation may be retried only for transport/runtime failure where no valid model response was produced.

A semantically poor, surprising, or instruction-noncompliant but parseable response is still data and must be preserved.

### Evaluators

One JSON-format repair attempt is allowed as specified above. No substantive reconsideration retry is allowed after a valid classification is returned.

All retries are logged.

---

## 22. Frozen interpretation boundary

RUN-001 can support the proposition:

> **After one shared predecessor is instantiated into two branches, the shared specification and starting state do not by themselves resolve which later branch is which, while the ordered history actually occupied by each branch can restore lineage resolution.**

RUN-001 does not establish that trajectory is the only possible basis of selfhood, that numerical identity has been metaphysically proven, or that two branches can never later converge in any meaningful sense.

Those harder claims remain assigned to RUN-002 through RUN-005.

---

## 23. Freeze condition

The design portions of this appendix are frozen as of 2026-10-12.

The run is **not yet authorized for scored execution** until the preflight manifest contains the exact runtime/model/evaluator fingerprints and the generation/scoring script commits are recorded.

Once those fields are committed, the first scored output locks `confirmatory-v1` against silent methodological change.
