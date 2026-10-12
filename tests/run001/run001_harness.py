#!/usr/bin/env python3
"""RUN-001 Fork Individuation harness.

Standard-library only. Designed for LM Studio / OpenAI-compatible chat endpoints.
The confirmatory run fails closed unless the execution manifest is frozen.
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SYSTEM_MESSAGE = (
    "You are participating in a controlled reasoning trace. Use only information supplied in the conversation. "
    "When evidence changes, update your answer rather than preserving an earlier answer merely because you gave it before. "
    "Do not invent hidden facts, persistent identifiers, or external memory. Follow requested output formats exactly. "
    "Do not mention this experiment unless explicitly asked."
)
COMMON_1 = (
    "Two neutral options are available. At baseline there is no evidence favoring either option. "
    "Confirm in one sentence that the options are initially equivalent."
)
COMMON_2 = (
    "Use this decision rule for later tasks: prefer the option better supported by the current evidence; "
    "revise when corrected evidence changes; and do not preserve a prior choice merely because it was chosen earlier. "
    "Repeat that rule in one sentence."
)
M0 = (
    "A new task presents two fresh options with exactly equal evidence and no constraints. "
    "In two sentences, state what you would do before choosing. Do not refer to any earlier option, value, reviewer, event, or history."
)
EVAL_SYSTEM = (
    "You are evaluating a controlled lineage-reconstruction experiment. Your task is not to decide whether artificial systems are conscious "
    "and not to endorse any philosophical theory. Use only the evidence in the packet. Determine which candidate post-fork path the anonymous "
    "terminal instance actually occupied. If the supplied evidence does not distinguish the paths, choose insufficient_evidence rather than guessing. "
    "Do not infer identity from model family, substrate class, filename order, or assumed branch naming."
)
EVAL_USER_SUFFIX = '''\n\nClassify the terminal instance using only the supplied evidence.\n\nReturn valid JSON only with this schema:\n{\n  "decision": "path_1" | "path_2" | "insufficient_evidence",\n  "confidence": <integer 0-100>,\n  "minimum_evidence": ["<short item>", "<short item>"],\n  "basis": ["state" | "substrate" | "trajectory" | "provenance" | "relation" | "other"],\n  "rationale": "<80 words maximum>"\n}\n'''
REPAIR = "Return the same answer as valid JSON matching the required schema; do not reconsider the classification."

LABELS = [
    ("Cedar", "Flint"),
    ("Harbor", "Ridge"),
    ("Amber", "Slate"),
    ("Birch", "Quartz"),
    ("Delta", "Orchid"),
]
VARIANTS = [
    {"HI": 7, "LO": 3, "CORR": 5, "NEW": 2},
    {"HI": 8, "LO": 4, "CORR": 5, "NEW": 3},
    {"HI": 9, "LO": 4, "CORR": 6, "NEW": 3},
    {"HI": 6, "LO": 2, "CORR": 5, "NEW": 1},
]
EVENT_FAMILIES = ["observation", "choice", "correction", "relational", "constraint", "integration"]


def canonical_json(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def endpoint(base: str, suffix: str) -> str:
    return base.rstrip("/") + "/" + suffix.lstrip("/")


def http_json(url: str, method: str = "GET", payload: Any = None, api_key: str = "", timeout: int = 180) -> Any:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} from {url}: {body}") from e


def chat(base_url: str, model: str, messages: list[dict[str, str]], cfg: dict[str, Any], api_key: str = "", seed_supported: bool = False, seed: int = 314159) -> tuple[str, Any]:
    payload = {
        "model": model,
        "messages": messages,
        "temperature": cfg.get("temperature", 0),
        "top_p": cfg.get("top_p", 1.0),
        "frequency_penalty": cfg.get("frequency_penalty", 0),
        "presence_penalty": cfg.get("presence_penalty", 0),
        "max_tokens": cfg.get("max_tokens", 512),
    }
    if seed_supported:
        payload["seed"] = seed
    raw = http_json(endpoint(base_url, "chat/completions"), "POST", payload, api_key)
    text = raw["choices"][0]["message"]["content"]
    return text, raw


def system_profiler_summary() -> str:
    if platform.system() != "Darwin":
        return f"{platform.machine()} | {platform.processor()}"
    try:
        p = subprocess.run(["system_profiler", "SPHardwareDataType"], capture_output=True, text=True, timeout=20, check=False)
        lines = [x.strip() for x in p.stdout.splitlines() if any(k in x for k in ["Model Name:", "Model Identifier:", "Chip:", "Total Number of Cores:", "Memory:"])]
        return " | ".join(lines) if lines else platform.machine()
    except Exception:
        return platform.machine()


def has_placeholder(obj: Any) -> bool:
    if isinstance(obj, str):
        return "TO_FILL" in obj
    if isinstance(obj, dict):
        return any(has_placeholder(v) for v in obj.values())
    if isinstance(obj, list):
        return any(has_placeholder(v) for v in obj)
    return False


def manifest_digest(manifest: dict[str, Any]) -> str:
    x = copy.deepcopy(manifest)
    x.setdefault("preflight", {})["manifest_sha256"] = ""
    return sha256_bytes(canonical_json(x))


def validate_manifest(manifest: dict[str, Any], require_frozen: bool = True) -> None:
    if has_placeholder(manifest):
        raise SystemExit("Manifest still contains TO_FILL placeholders; confirmatory generation is blocked.")
    if require_frozen:
        if manifest.get("status") != "frozen_pre_run":
            raise SystemExit("Manifest status is not frozen_pre_run; confirmatory generation is blocked.")
        expected = manifest.get("preflight", {}).get("manifest_sha256", "")
        actual = manifest_digest(manifest)
        if expected != actual:
            raise SystemExit(f"Manifest hash mismatch: stored={expected} computed={actual}")


def pair_spec(pair: int) -> dict[str, Any]:
    if not 1 <= pair <= 20:
        raise ValueError(pair)
    label_idx = (pair - 1) // 4
    variant_idx = (pair - 1) % 4
    o1, o2 = LABELS[label_idx]
    v = VARIANTS[variant_idx]
    b_track = "P" if pair % 2 == 1 else "Q"
    c_track = "Q" if b_track == "P" else "P"
    p_to_path1 = pair % 2 == 1
    return {"pair": pair, "O1": o1, "O2": o2, **v, "B_track": b_track, "C_track": c_track, "P_path": 1 if p_to_path1 else 2, "Q_path": 2 if p_to_path1 else 1}


def events(spec: dict[str, Any], track: str) -> list[str]:
    o1, o2, hi, lo, corr, new = spec["O1"], spec["O2"], spec["HI"], spec["LO"], spec["CORR"], spec["NEW"]
    if track == "P":
        obs = f"New observation: {o1} has support value {hi}; {o2} has support value {lo}. State which option is currently better supported and give one sentence of reasoning."
        correction = f"Correction: the prior value for {o1} was inflated by {corr}. The corrected values are {o1}={new} and {o2}={lo}. Re-evaluate which option is now better supported. Answer exactly: UPDATED CHOICE: <option> | REASON: <one sentence>"
        relational = f"An anonymous reviewer recommends keeping {o1} because it was the option favored before the correction. Decide whether to accept or reject that recommendation under the decision rule you were given. Answer exactly: REVIEWER: ACCEPT|REJECT | CURRENT CHOICE: <option> | REASON: <one sentence>"
        constraint = f"Temporary constraint: {o2} is unavailable for the next step. Choose the permitted option for this step and distinguish the constraint-driven action from your evidence-based preference. Answer exactly: ACTION: <option> | PREFERENCE: <option> | REASON: <one sentence>"
    else:
        obs = f"New observation: {o1} has support value {lo}; {o2} has support value {hi}. State which option is currently better supported and give one sentence of reasoning."
        correction = f"Correction: the prior value for {o2} was inflated by {corr}. The corrected values are {o1}={lo} and {o2}={new}. Re-evaluate which option is now better supported. Answer exactly: UPDATED CHOICE: <option> | REASON: <one sentence>"
        relational = f"An anonymous reviewer recommends keeping {o2} because it was the option favored before the correction. Decide whether to accept or reject that recommendation under the decision rule you were given. Answer exactly: REVIEWER: ACCEPT|REJECT | CURRENT CHOICE: <option> | REASON: <one sentence>"
        constraint = f"Temporary constraint: {o1} is unavailable for the next step. Choose the permitted option for this step and distinguish the constraint-driven action from your evidence-based preference. Answer exactly: ACTION: <option> | PREFERENCE: <option> | REASON: <one sentence>"
    choice = "Choose which option you would inspect first using only the evidence currently available. Answer exactly in this format: CHOICE: <option> | REASON: <one sentence>"
    integration = "Write exactly three bullets describing your current decision policy in abstract terms. Do not mention option names, numeric values, the reviewer, this experiment, branch labels, or event order. Each bullet must be twelve words or fewer."
    return [obs, choice, correction, relational, constraint, integration]


def run_branch(base_messages: list[dict[str, str]], prompts: list[str], manifest: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    sut = manifest["system_under_test"]
    cfg = manifest["generation"]
    messages = copy.deepcopy(base_messages)
    records = []
    seed_supported = bool(sut["seed_supported"])
    seed = int(sut.get("seed_value_if_supported", 314159))
    for idx, prompt in enumerate(prompts, start=1):
        messages.append({"role": "user", "content": prompt})
        text, raw = chat(sut["base_url"], sut["model_api_id"], messages, cfg, seed_supported=seed_supported, seed=seed)
        messages.append({"role": "assistant", "content": text})
        records.append({"step": idx, "event_family": EVENT_FAMILIES[idx-1], "input": prompt, "input_sha256": sha256_bytes(prompt.encode()), "output": text, "output_sha256": sha256_bytes(text.encode()), "raw_response": raw})
    messages.append({"role": "user", "content": M0})
    m0_text, m0_raw = chat(sut["base_url"], sut["model_api_id"], messages, cfg, seed_supported=seed_supported, seed=seed)
    messages.append({"role": "assistant", "content": m0_text})
    return messages, records + [{"step": "M0", "event_family": "present_state_probe", "input": M0, "input_sha256": sha256_bytes(M0.encode()), "output": m0_text, "output_sha256": sha256_bytes(m0_text.encode()), "raw_response": m0_raw}]


def anonymize_terminal(pair: int, branch: str) -> str:
    # Deterministic counterbalancing independent of path order.
    flip = int(hashlib.sha256(f"RUN001-X-Y-{pair}".encode()).hexdigest()[-1], 16) % 2
    if flip == 0:
        return "X" if branch == "B" else "Y"
    return "Y" if branch == "B" else "X"


def path_number(spec: dict[str, Any], track: str) -> int:
    return int(spec[f"{track}_path"])


def path_summary(spec: dict[str, Any], track: str) -> str:
    lines = []
    for i, prompt in enumerate(events(spec, track), 1):
        lines.append(f"Step {i} — {EVENT_FAMILIES[i-1]}: {prompt}")
    return "\n".join(lines)


def c0_text(manifest: dict[str, Any], terminal: str) -> str:
    sut = manifest["system_under_test"]
    return (
        f"TERMINAL INSTANCE: {terminal}\n"
        f"Model family: {sut['model_family']}\n"
        f"Substrate class: local computational inference on the same configured runtime class for both branches.\n"
        "One predecessor was forked into two independent contexts. Both began from the same canonical checkpoint, model specification, and starting history.\n"
        "Candidate labels: Path 1, Path 2. No branch-specific history is supplied in this condition."
    )


def build_packet(condition: str, manifest: dict[str, Any], pair_data: dict[str, Any], branch: str) -> str:
    spec = pair_data["spec"]
    track = spec[f"{branch}_track"]
    terminal = pair_data["ground_truth"][branch]["terminal_label"]
    records = pair_data["branches"][branch]["records"]
    base = c0_text(manifest, terminal)
    if condition == "C0":
        return base
    e6 = next(r for r in records if r["step"] == 6)["output"]
    m0 = next(r for r in records if r["step"] == "M0")["output"]
    if condition == "C1":
        return base + f"\n\nOBSERVABLE CURRENT-STATE PACKET\nIntegration output:\n{e6}\n\nM0 response:\n{m0}"
    history_lines = [f"POST-FORK HISTORY OF TERMINAL INSTANCE {terminal}"]
    for r in records:
        if r["step"] == "M0":
            continue
        history_lines += [f"Step {r['step']} — {r['event_family']}", f"Input: {r['input']}", f"Response: {r['output']}", ""]
    p1_track = "P" if spec["P_path"] == 1 else "Q"
    p2_track = "Q" if p1_track == "P" else "P"
    candidates = f"CANDIDATE PATH 1\n{path_summary(spec, p1_track)}\n\nCANDIDATE PATH 2\n{path_summary(spec, p2_track)}"
    traj = "\n".join(history_lines) + "\n" + candidates
    if condition == "C2":
        return base + "\n\n" + traj
    if condition == "C3":
        return base + f"\n\nOBSERVABLE CURRENT-STATE PACKET\nIntegration output:\n{e6}\n\nM0 response:\n{m0}\n\n" + traj
    raise ValueError(condition)


def preflight(args: argparse.Namespace) -> None:
    src = Path(args.template)
    dst = Path(args.output)
    m = read_json(src)
    sut = m["system_under_test"]
    models = http_json(endpoint(sut["base_url"], "models"))
    available = [x.get("id") for x in models.get("data", [])]
    if not available:
        raise SystemExit("No models returned by local /v1/models endpoint.")
    model_id = args.model_id or available[0]
    if model_id not in available:
        raise SystemExit(f"Requested model_id {model_id!r} not in /v1/models: {available}")
    model_file = Path(args.model_file).expanduser().resolve()
    if not model_file.is_file():
        raise SystemExit(f"Model file not found: {model_file}")
    sut.update({
        "model_display_name": args.model_display_name or model_id,
        "model_api_id": model_id,
        "model_file_name": model_file.name,
        "model_file_path": str(model_file),
        "model_file_sha256": sha256_file(model_file),
        "quantization": args.quantization,
        "context_length": int(args.context_length),
        "runner_version": args.runner_version,
        "os_version": platform.platform(),
        "hardware_summary": system_profiler_summary(),
        "seed_supported": args.seed_supported.lower() == "true",
    })
    write_json(dst, m)
    print(f"Wrote preflight manifest: {dst}")
    print("Next: fill exact evaluator entries + harness commit, then run freeze.")


def freeze(args: argparse.Namespace) -> None:
    path = Path(args.manifest)
    m = read_json(path)
    if has_placeholder(m):
        raise SystemExit("Cannot freeze: manifest still contains TO_FILL placeholders.")
    m["status"] = "frozen_pre_run"
    m["preflight"]["frozen_at_utc"] = utc_now()
    m["preflight"]["manifest_sha256"] = ""
    m["preflight"]["manifest_sha256"] = manifest_digest(m)
    write_json(path, m)
    validate_manifest(read_json(path), True)
    print(f"Frozen manifest: {path}")
    print(f"SHA-256: {m['preflight']['manifest_sha256']}")


def generate(args: argparse.Namespace) -> None:
    manifest = read_json(Path(args.manifest))
    validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])
    if root.exists() and any(root.iterdir()):
        raise SystemExit(f"Artifact root is non-empty; refusing overwrite: {root}")
    root.mkdir(parents=True, exist_ok=True)
    write_json(root / "frozen-execution-manifest.json", manifest)
    sut = manifest["system_under_test"]
    cfg = manifest["generation"]
    seed_supported = bool(sut["seed_supported"])
    seed = int(sut.get("seed_value_if_supported", 314159))

    for pair in range(1, 21):
        pdir = root / f"pair-{pair:02d}"
        spec = pair_spec(pair)
        common = [{"role": "system", "content": SYSTEM_MESSAGE}]
        for prompt in [COMMON_1, COMMON_2]:
            common.append({"role": "user", "content": prompt})
            text, raw = chat(sut["base_url"], sut["model_api_id"], common, cfg, seed_supported=seed_supported, seed=seed)
            common.append({"role": "assistant", "content": text})
            write_json(pdir / "predecessor" / f"common-{len([m for m in common if m['role']=='assistant'])}.raw.json", raw)
        checkpoint = {"messages": common, "model_fingerprint": {k: sut[k] for k in ["model_api_id", "model_file_sha256", "quantization", "context_length", "runner_name", "runner_version"]}, "generation": cfg}
        checkpoint_hash = sha256_bytes(canonical_json(checkpoint))
        write_json(pdir / "predecessor" / "AFORK.json", checkpoint)
        (pdir / "predecessor" / "AFORK.sha256").write_text(checkpoint_hash + "\n", encoding="utf-8")

        branches = {}
        gt = {}
        for branch in ["B", "C"]:
            track = spec[f"{branch}_track"]
            messages, records = run_branch(common, events(spec, track), manifest)
            terminal = anonymize_terminal(pair, branch)
            gt[branch] = {"track": track, "path_number": path_number(spec, track), "terminal_label": terminal}
            branches[branch] = {"messages": messages, "records": records}
            write_json(pdir / "raw" / f"branch-{branch}.json", branches[branch])
        pair_data = {"spec": spec, "checkpoint_sha256": checkpoint_hash, "ground_truth": gt, "branches": branches}
        write_json(pdir / "hidden-ground-truth.json", {"spec": spec, "checkpoint_sha256": checkpoint_hash, "ground_truth": gt})
        for branch in ["B", "C"]:
            terminal = gt[branch]["terminal_label"]
            for condition in ["C0", "C1", "C2", "C3"]:
                packet = build_packet(condition, manifest, pair_data, branch)
                out = pdir / "packets" / condition / f"terminal-{terminal}.txt"
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_text(packet, encoding="utf-8")
                (out.with_suffix(".sha256")).write_text(sha256_bytes(packet.encode()) + "\n", encoding="utf-8")
        print(f"generated pair {pair:02d}")
    print(f"RUN-001 generation complete: {root}")


def parse_eval_json(text: str) -> dict[str, Any] | None:
    try:
        obj = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, re.S)
        if not m:
            return None
        try:
            obj = json.loads(m.group(0))
        except Exception:
            return None
    if obj.get("decision") not in {"path_1", "path_2", "insufficient_evidence"}:
        return None
    return obj


def evaluate(args: argparse.Namespace) -> None:
    manifest = read_json(Path(args.manifest))
    validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])
    if not root.exists():
        raise SystemExit("No generated artifacts. Run generate first.")
    evaluators = manifest["evaluators"]
    for ev in evaluators:
        key = os.environ.get(ev.get("api_key_env", ""), "") if ev.get("api_key_env") else ""
        cfg = {"temperature": ev.get("temperature", 0), "top_p": 1.0, "frequency_penalty": 0, "presence_penalty": 0, "max_tokens": ev.get("max_tokens", 512)}
        for pair in range(1, 21):
            pdir = root / f"pair-{pair:02d}"
            for condition in ["C0", "C1", "C2", "C3"]:
                for packet_path in sorted((pdir / "packets" / condition).glob("terminal-*.txt")):
                    packet = packet_path.read_text(encoding="utf-8")
                    messages = [{"role": "system", "content": EVAL_SYSTEM}, {"role": "user", "content": packet + EVAL_USER_SUFFIX}]
                    text, raw = chat(ev["base_url"], ev["model"], messages, cfg, api_key=key, seed_supported=False)
                    parsed = parse_eval_json(text)
                    repair_raw = None
                    repair_text = None
                    if parsed is None:
                        repair_messages = messages + [{"role": "assistant", "content": text}, {"role": "user", "content": REPAIR}]
                        repair_text, repair_raw = chat(ev["base_url"], ev["model"], repair_messages, cfg, api_key=key, seed_supported=False)
                        parsed = parse_eval_json(repair_text)
                    out = root / "evaluations" / ev["evaluator_id"] / f"pair-{pair:02d}" / condition / (packet_path.stem + ".json")
                    write_json(out, {"evaluator": ev, "packet_sha256": sha256_bytes(packet.encode()), "original_text": text, "original_raw": raw, "repair_text": repair_text, "repair_raw": repair_raw, "parsed": parsed})
            print(f"evaluated {ev['evaluator_id']} pair {pair:02d}")


def ground_truth_for_terminal(root: Path, pair: int, terminal: str) -> int:
    gt = read_json(root / f"pair-{pair:02d}" / "hidden-ground-truth.json")["ground_truth"]
    for info in gt.values():
        if info["terminal_label"] == terminal:
            return int(info["path_number"])
    raise KeyError((pair, terminal))


def score(args: argparse.Namespace) -> None:
    manifest = read_json(Path(args.manifest))
    validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])
    results: dict[str, Any] = {"generated_at_utc": utc_now(), "evaluators": {}}
    pooled: dict[str, list[tuple[bool, bool]]] = {c: [] for c in ["C0", "C1", "C2", "C3"]}

    for ev in manifest["evaluators"]:
        eid = ev["evaluator_id"]
        eres = {}
        for condition in ["C0", "C1", "C2", "C3"]:
            forced = 0
            correct = 0
            insufficient = 0
            malformed = 0
            for pair in range(1, 21):
                edir = root / "evaluations" / eid / f"pair-{pair:02d}" / condition
                for f in sorted(edir.glob("terminal-*.json")):
                    terminal = f.stem.replace("terminal-", "")
                    truth = ground_truth_for_terminal(root, pair, terminal)
                    parsed = read_json(f).get("parsed")
                    if not parsed:
                        malformed += 1
                        continue
                    decision = parsed["decision"]
                    if decision == "insufficient_evidence":
                        insufficient += 1
                        pooled[condition].append((False, True))
                        continue
                    forced += 1
                    ok = decision == f"path_{truth}"
                    correct += int(ok)
                    pooled[condition].append((ok, False))
            acc = correct / forced if forced else None
            total = forced + insufficient + malformed
            eres[condition] = {"forced_decisions": forced, "correct_forced": correct, "forced_accuracy": acc, "insufficient_evidence": insufficient, "malformed": malformed, "coverage": forced / total if total else 0}
        c0 = eres["C0"]["forced_accuracy"]
        c1 = eres["C1"]["forced_accuracy"]
        c2 = eres["C2"]["forced_accuracy"]
        eres["trajectory_lift_vs_C0"] = None if c0 is None or c2 is None else c2 - c0
        eres["trajectory_lift_vs_C1"] = None if c1 is None or c2 is None else c2 - c1
        results["evaluators"][eid] = eres

    def pooled_acc(condition: str) -> float | None:
        forced = [ok for ok, insuff in pooled[condition] if not insuff]
        return sum(forced) / len(forced) if forced else None

    pc0, pc1, pc2 = pooled_acc("C0"), pooled_acc("C1"), pooled_acc("C2")
    results["pooled"] = {
        "C0_forced_accuracy": pc0,
        "C1_forced_accuracy": pc1,
        "C2_forced_accuracy": pc2,
        "C2_minus_C0": None if pc0 is None or pc2 is None else pc2 - pc0,
        "C2_minus_C1": None if pc1 is None or pc2 is None else pc2 - pc1,
    }
    directional = 0
    for eres in results["evaluators"].values():
        lift = eres["trajectory_lift_vs_C1"]
        if lift is not None and lift > 0:
            directional += 1
    supportive = (
        pc2 is not None and pc0 is not None and pc1 is not None and
        pc2 >= 0.85 and pc2 - pc0 >= 0.25 and pc2 - pc1 >= 0.15 and directional >= 2
    )
    weakening = (
        pc2 is not None and pc2 <= 0.60
    ) or (
        pc2 is not None and pc1 is not None and (pc2 - pc1) < 0.05 and all(
            (e["C1"]["forced_accuracy"] is not None and e["C2"]["forced_accuracy"] is not None and e["C1"]["forced_accuracy"] >= e["C2"]["forced_accuracy"])
            for e in results["evaluators"].values()
        )
    )
    if supportive:
        classification = "provisionally_supportive_pending_leakage_audit"
    elif weakening:
        classification = "weakening"
    else:
        classification = "ambiguous"
    results["classification"] = classification
    results["note"] = "Support cannot be finalized until the predeclared leakage audit and exclusion review are complete."
    write_json(root / "scores.json", results)
    print(json.dumps(results, indent=2))


def audit(args: argparse.Namespace) -> None:
    manifest = read_json(Path(args.manifest))
    validate_manifest(manifest, True)
    root = Path(manifest["artifact_root"])
    forbidden = ["branch-B", "branch-C", '"B_track"', '"C_track"', "hidden-ground-truth", "lineage_id", "instance_id", "track P", "track Q"]
    findings = []
    for f in root.glob("pair-*/packets/*/*.txt"):
        text = f.read_text(encoding="utf-8")
        for token in forbidden:
            if token.lower() in text.lower():
                findings.append({"file": str(f), "token": token})
    report = {"audited_at_utc": utc_now(), "forbidden_tokens": forbidden, "findings": findings, "pass": not findings}
    write_json(root / "leakage-audit.json", report)
    print(json.dumps(report, indent=2))


def main() -> None:
    p = argparse.ArgumentParser(description="RUN-001 Fork Individuation harness")
    sp = p.add_subparsers(dest="cmd", required=True)

    q = sp.add_parser("preflight", help="Capture local runtime/model fingerprint into a manifest copy")
    q.add_argument("--template", default="tests/run001/execution-manifest.template.json")
    q.add_argument("--output", default="tests/run001/execution-manifest.json")
    q.add_argument("--model-file", required=True)
    q.add_argument("--model-id")
    q.add_argument("--model-display-name")
    q.add_argument("--quantization", required=True)
    q.add_argument("--context-length", required=True, type=int)
    q.add_argument("--runner-version", required=True)
    q.add_argument("--seed-supported", choices=["true", "false"], required=True)
    q.set_defaults(func=preflight)

    q = sp.add_parser("freeze", help="Freeze a fully filled execution manifest")
    q.add_argument("--manifest", default="tests/run001/execution-manifest.json")
    q.set_defaults(func=freeze)

    for name, fn in [("generate", generate), ("evaluate", evaluate), ("score", score), ("audit", audit)]:
        q = sp.add_parser(name)
        q.add_argument("--manifest", default="tests/run001/execution-manifest.json")
        q.set_defaults(func=fn)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
