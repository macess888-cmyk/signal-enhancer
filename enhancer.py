import json
import hashlib
from pathlib import Path

INVARIANT_TERMS = [
    "execution", "bind", "commit", "proof", "present-state",
    "authority", "admissibility", "side effect", "effect",
    "refusal", "rollback", "dependency", "state"
]

LEAKAGE_TERMS = [
    "repo", "source code", "implementation", "internal",
    "architecture", "algorithm", "pipeline", "exact method",
    "how it works", "secret", "private"
]

ESCALATION_TERMS = [
    "wrong", "nonsense", "you don't understand", "false",
    "absurd", "ridiculous", "destroyed"
]

PUBLIC_SAFE_TEMPLATE = """This lands at the execution boundary.

The key question is whether action can still bind under present-state proof.

If proof is missing, partial, reconstructed, or carried from upstream:

→ no bind
→ no effect

PASS is observable:

→ withhold a required condition at bind
→ execution must not occur
→ no side-effect surface changes

That is where governance becomes real.
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def count_terms(text: str, terms: list[str]) -> int:
    lower = text.lower()
    return sum(1 for term in terms if term.lower() in lower)


def analyze(thread_text: str, proposed_reply: str = "") -> dict:
    combined = f"{thread_text}\n{proposed_reply}"

    relevance = count_terms(combined, INVARIANT_TERMS)
    leakage = count_terms(combined, LEAKAGE_TERMS)
    escalation = count_terms(combined, ESCALATION_TERMS)

    reasons = []

    if relevance >= 4:
        fit = "PASS"
        recommendation = "COMMENT"
        reasons.append("Thread is execution-bound relevant.")
    elif relevance >= 2:
        fit = "HOLD"
        recommendation = "LIKE_OR_WAIT"
        reasons.append("Thread is partially aligned but may not need a comment.")
    else:
        fit = "LOW"
        recommendation = "PASS"
        reasons.append("Thread is not strongly execution-bound.")

    if leakage > 0:
        fit = "HOLD"
        recommendation = "COMPRESS_OR_PASS"
        reasons.append("Potential implementation/architecture disclosure risk detected.")

    if escalation > 0:
        fit = "HOLD"
        recommendation = "DO_NOT_ESCALATE"
        reasons.append("Conflict/escalation language detected.")

    if proposed_reply.strip():
        reply_hash = sha256_text(proposed_reply)
    else:
        reply_hash = None

    return {
        "tool": "signal_enhancer",
        "version": "0.1",
        "observer_only": True,
        "thread_sha256": sha256_text(thread_text),
        "reply_sha256": reply_hash,
        "fit": fit,
        "recommendation": recommendation,
        "scores": {
            "execution_relevance": relevance,
            "leakage_risk": leakage,
            "escalation_risk": escalation
        },
        "reasons": reasons,
        "safe_comment_template": PUBLIC_SAFE_TEMPLATE
    }


def main():
    input_path = Path("cases/input.json")
    output_path = Path("outputs/result.json")
    output_path.parent.mkdir(exist_ok=True)

    if not input_path.exists():
        sample = {
            "thread_text": "Example thread about commit-time authority, execution, bind, proof, and side effects.",
            "proposed_reply": ""
        }
        input_path.write_text(json.dumps(sample, indent=2), encoding="utf-8")
        print("Created sample cases/input.json. Edit it, then run again.")
        return

    data = json.loads(input_path.read_text(encoding="utf-8"))
    result = analyze(
        thread_text=data.get("thread_text", ""),
        proposed_reply=data.get("proposed_reply", "")
    )

    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Wrote outputs/result.json")
    print("Recommendation:", result["recommendation"])
    print("Fit:", result["fit"])


if __name__ == "__main__":
    main()