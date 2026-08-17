from __future__ import annotations
from typing import List, Dict, Any, Tuple
import re
import logging

from backend.app.agents.base import AgentOutput

_LOG = logging.getLogger(__name__)


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    # naive sentence splitter
    parts = re.split(r'(?<=[.!?])\s+', text.strip())
    return [p.strip() for p in parts if p.strip()]


def _normalize_sentence(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _sentence_in_sources(sentence: str, sources: List[Dict[str, Any]]) -> bool:
    s_norm = sentence.lower()
    for m in sources:
        txt = (m.get("text") or "").lower()
        if txt and s_norm in txt:
            return True
    return False


def _extract_numbers(s: str) -> List[str]:
    return re.findall(r"\d+", s)


def aggregate_agent_responses(agent_outputs: List[AgentOutput]) -> Dict[str, Any]:
    """Aggregate multiple AgentOutput into a single customer-facing response.

    Returns dict with keys: final_answer (str), escalate (bool), sources (list), confidence (float)
    """
    # Normalize inputs
    outs = []
    for o in agent_outputs:
        if isinstance(o, AgentOutput):
            outs.append(o.dict())
        elif isinstance(o, dict):
            outs.append(o)

    if not outs:
        return {"final_answer": "I don't have any information to answer that right now.", "escalate": True, "sources": [], "confidence": 0.0}

    # determine escalate if any agent requests it or failed
    escalate = any(o.get("requires_escalation") for o in outs)

    # Collect sources
    sources = []
    source_ids = set()
    for o in outs:
        for s in (o.get("sources") or []):
            sid = s.get("doc_id") or s.get("source_path") or str(s)
            if sid not in source_ids:
                source_ids.add(sid)
                sources.append(s)

    # Collect sentences, tag as evidence-backed or not, keep provenance agent and confidence
    sentence_map: Dict[str, Dict[str, Any]] = {}
    for o in outs:
        agent = o.get("agent")
        conf = float(o.get("confidence", 0.0) or 0.0)
        answer = o.get("answer") or ""
        srcs = o.get("sources") or []
        for sent in _split_sentences(answer):
            norm = _normalize_sentence(sent)
            if not norm:
                continue
            evidence = _sentence_in_sources(sent, srcs) or _sentence_in_sources(sent, sources)
            existing = sentence_map.get(norm)
            if existing:
                # keep the one with higher confidence or evidence
                if evidence and not existing["evidence"]:
                    sentence_map[norm] = {"text": sent, "agents": {agent}, "confidence": conf, "evidence": evidence}
                else:
                    existing["agents"].add(agent)
                    existing["confidence"] = max(existing["confidence"], conf)
            else:
                sentence_map[norm] = {"text": sent, "agents": {agent}, "confidence": conf, "evidence": evidence}

    # Resolve contradictions: numeric conflicts for same topic
    # Group sentences by key topics (simple keyword matching)
    topic_groups: Dict[str, List[str]] = {}
    keywords = ["refund", "return", "warranty", "shipping", "price", "charged", "login", "password", "activate", "locked"]
    for norm, meta in sentence_map.items():
        assigned = False
        for kw in keywords:
            if kw in norm:
                topic_groups.setdefault(kw, []).append(norm)
                assigned = True
                break
        if not assigned:
            topic_groups.setdefault("other", []).append(norm)

    final_sentences: List[str] = []
    # For each topic, detect numeric conflicts
    for topic, norms in topic_groups.items():
        if len(norms) == 1:
            final_sentences.append(sentence_map[norms[0]]["text"])
            continue
        # check numbers in sentences
        numbers = {n: _extract_numbers(sentence_map[n]["text"] ) for n in norms}
        # if numbers differ and any sentence has evidence, prefer evidence-backed ones
        evidence_norms = [n for n in norms if sentence_map[n]["evidence"]]
        chosen = None
        if evidence_norms:
            # pick highest confidence among evidence-backed
            chosen = max(evidence_norms, key=lambda x: sentence_map[x]["confidence"])
        else:
            # pick highest confidence
            chosen = max(norms, key=lambda x: sentence_map[x]["confidence"])
        final_sentences.append(sentence_map[chosen]["text"])
        # If there are conflicting numeric values and no evidence, add uncertainty note
        numeric_sets = set(tuple(v) for v in numbers.values())
        if len(numeric_sets) > 1 and not evidence_norms:
            final_sentences.append("Note: sources differ on details; please contact support@astrahome.com for confirmation.")

    # Remove duplicates while preserving order
    seen = set()
    unique_final = []
    for s in final_sentences:
        n = _normalize_sentence(s)
        if n not in seen:
            unique_final.append(s)
            seen.add(n)

    # Build customer-friendly response
    header_parts = []
    # Collect unique agents (agent is a string, not a list)
    agents_involved = sorted({o.get("agent") for o in outs if o.get("agent")})
    if agents_involved:
        header_parts.append("I asked our " + ", ".join(agents_involved) + " teams for help.")

    body = "\n\n".join(unique_final) if unique_final else "I don't have any information to provide on this topic right now."

    footer = ""
    if escalate:
        footer = "\n\nI've flagged this for human review and can escalate it now."
    elif not sources:
        footer = "\n\nNote: I couldn't find direct evidence in our knowledge base for some details; contact support@astrahome.com for confirmation."

    final_answer = " ".join(header_parts) + "\n\n" + body + footer

    # Aggregate confidence as max of agents' confidences
    conf = max((float(o.get("confidence", 0.0) or 0.0) for o in outs), default=0.0)

    return {"final_answer": final_answer.strip(), "escalate": escalate, "sources": sources, "confidence": conf}
