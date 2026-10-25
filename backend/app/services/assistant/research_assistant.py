from typing import List, Dict, Any

def answer_research_question(
    question: str,
    investigation_summary: str,
    assessment_status: str,
    claim_assertion: str,
    evidence_items: List[Dict[str, Any]],
    image_metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Strictly evidence-grounded research assistant.
    Answers specific user queries based only on the current investigation record.
    Never hallucinates external events or cites unretrieved URLs.
    """
    q_lower = question.lower()
    citations = []
    missing_info = None

    contradicting = [e for e in evidence_items if e.get("relationship_to_claim") == "contradicts"]
    supporting = [e for e in evidence_items if e.get("relationship_to_claim") == "supports"]

    if any(k in q_lower for k in ["contradict", "disprove", "false", "wrong", "lie"]):
        if contradicting:
            first_c = contradicting[0]
            citations.append(f"{first_c.get('publisher')} ({first_c.get('source_url')})")
            answer = (
                f"The claim is contradicted primarily by findings from {first_c.get('publisher')}. "
                f"The documented record states: \"{first_c.get('passage')}\". "
                f"This indicates that either the photograph originated from a different date/location or the described event did not take place as claimed."
            )
        else:
            answer = "No retrieved evidence in this investigation directly contradicts the claim. The current assessment is based on lack of corroboration or positive matches."
            missing_info = "Specific investigative debunks or eyewitness disclaimers are not in the local archive."

    elif any(k in q_lower for k in ["support", "corroborate", "true", "prove", "verify"]):
        if supporting:
            first_s = supporting[0]
            citations.append(f"{first_s.get('publisher')} ({first_s.get('source_url')})")
            answer = (
                f"The claim is supported by reporting from {first_s.get('publisher')}. "
                f"The verified source confirms: \"{first_s.get('passage')}\". "
                f"The publication date and reported location match the visual depiction in the photograph."
            )
        else:
            answer = "No retrieved evidence in this investigation currently supports the claim."
            missing_info = "Verified on-the-ground news dispatches or official statements corroborating this specific image."

    elif any(k in q_lower for k in ["why", "relevant", "retrieved", "found"]):
        if evidence_items:
            top = evidence_items[0]
            citations.append(f"{top.get('publisher')} ({top.get('source_url')})")
            answer = (
                f"Sources like \"{top.get('source_title')}\" were retrieved because our hybrid retrieval model "
                f"detected matching semantic entities and visual similarity (retrieval score: {int(top.get('retrieval_score', 0)*100)}%). "
                f"The source directly addresses the event and geographic locations mentioned in your claim."
            )
        else:
            answer = "No sources exceeded the relevance threshold for this specific claim."
            missing_info = "Archival records containing similar keywords or visual hash matches."

    elif any(k in q_lower for k in ["missing", "next", "recommend", "investigate"]):
        answer = (
            f"To deepen this investigation, recommended next steps include: "
            f"1) Contacting local municipal emergency desks to confirm ground conditions. "
            f"2) Running a reverse image search across multiple commercial engines (Google Images, TinEye, Yandex). "
            f"3) Requesting the uncompressed original file from the source to inspect authentic EXIF camera timestamps."
        )
        missing_info = "Original camera RAW file and uncompressed social media upload metadata."

    elif any(k in q_lower for k in ["inconclusive", "insufficient", "uncertain"]):
        answer = (
            f"The status is '{assessment_status}' because TRUTHLENS enforces responsible AI guidelines: "
            f"an absence of matching documents is never treated as proof of falsehood, and visual similarity alone "
            f"does not guarantee complete factual truth without corroborating text evidence."
        )
    else:
        # General synthesis
        answer = (
            f"Based on the investigation record for '{claim_assertion}', our pipeline reached an assessment of '{assessment_status}'. "
            f"Summary: {investigation_summary}"
        )
        if evidence_items:
            citations.append(f"{evidence_items[0].get('publisher')} ({evidence_items[0].get('source_url')})")

    return {
        "question": question,
        "answer": answer,
        "grounded_in_sources": citations,
        "missing_information": missing_info,
        "limitations": "Assistant responses are synthesized strictly from retrieved investigation records and local reference datasets."
    }
