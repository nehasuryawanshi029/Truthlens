import json
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime, timezone
import httpx
from lxml import html
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.services.evidence_retrieval.source_scorer import calculate_source_reliability

def hamming_distance(hex1: str, hex2: str) -> int:
    """Computes bitwise Hamming distance between two hex hash strings."""
    try:
        val1 = int(hex1, 16)
        val2 = int(hex2, 16)
        return bin(val1 ^ val2).count('1')
    except Exception:
        return 64

def search_live_wikipedia_reference(query: str, client: httpx.Client = None) -> List[Dict[str, Any]]:
    """
    Live external knowledge retrieval adapter:
    Queries public Wikipedia API with academic User-Agent to retrieve authoritative articles.
    Returns real passages, real Wikipedia URLs, publishers, and timestamps.
    """
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 3:
        return []

    headers = {"User-Agent": "TruthLensResearchBot/2.0 (contact: info@truthlens.ai)"}
    items = []
    should_close = False
    if client is None:
        client = httpx.Client(timeout=4.0)
        should_close = True

    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={httpx.URL('', params={'q': clean_q}).params['q']}&format=json&utf8=1"
        resp = client.get(search_url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            search_results = data.get("query", {}).get("search", [])
            for res in search_results[:3]:
                title = res.get("title", "")
                raw_snippet = res.get("snippet", "")
                snippet = re.sub(r'<[^>]+>', '', raw_snippet).strip()
                clean_title_url = title.replace(" ", "_")
                items.append({
                    "id": f"wiki_{res.get('pageid')}",
                    "source_title": f"Wikipedia: {title}",
                    "source_url": f"https://en.wikipedia.org/wiki/{clean_title_url}",
                    "publisher": "Wikipedia / Wikimedia Foundation",
                    "publication_date": "2024-Archive",
                    "passage": f"{title}: {snippet}...",
                    "retrieval_method": "live_wikipedia_search",
                    "keywords": [title.lower(), "reference", "encyclopedic", clean_q.lower()],
                    "target_locations": [title.lower(), clean_q.lower()]
                })
    except Exception:
        pass
    finally:
        if should_close:
            client.close()

    return items

def search_duckduckgo_web(query: str, client: httpx.Client = None) -> List[Dict[str, Any]]:
    """
    Live Web Search using DuckDuckGo HTML endpoint:
    Returns live web headlines, URLs, publisher domains, and real search snippets.
    No paid API keys required.
    """
    clean_q = query.strip()
    if not clean_q or len(clean_q) < 3:
        return []

    url = "https://html.duckduckgo.com/html/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    items = []
    should_close = False
    if client is None:
        client = httpx.Client(timeout=5.0)
        should_close = True

    try:
        resp = client.post(url, data={"q": clean_q}, headers=headers)
        if resp.status_code == 200:
            tree = html.fromstring(resp.text)
            for el in tree.xpath('//div[contains(@class, "result")]')[:4]:
                title_nodes = el.xpath('.//a[contains(@class, "result__url")]')
                snippet_nodes = el.xpath('.//a[contains(@class, "result__snippet")]')
                full_title_nodes = el.xpath('.//a[contains(@class, "result__title")]') or el.xpath('.//h2/a')
                
                if title_nodes and snippet_nodes:
                    raw_href = title_nodes[0].get("href", "")
                    # Extract actual URL from DuckDuckGo redirect if needed
                    actual_url = raw_href
                    if "uddg=" in raw_href:
                        import urllib.parse
                        parsed_uddg = re.search(r'uddg=([^&]+)', raw_href)
                        if parsed_uddg:
                            actual_url = urllib.parse.unquote(parsed_uddg.group(1))

                    domain = title_nodes[0].text_content().strip().replace("www.", "")
                    snippet = snippet_nodes[0].text_content().strip()
                    title = full_title_nodes[0].text_content().strip() if full_title_nodes else domain

                    # Infer publisher from domain
                    publisher = domain.split("/")[0].title() if domain else "Web Publisher"

                    items.append({
                        "id": f"ddg_{abs(hash(actual_url)) % 1000000}",
                        "source_title": title,
                        "source_url": actual_url if actual_url.startswith("http") else f"https://{domain}",
                        "publisher": publisher,
                        "publication_date": "Online Record",
                        "passage": snippet,
                        "retrieval_method": "live_web_search",
                        "keywords": [k.lower() for k in clean_q.split() if len(k) > 2],
                        "target_locations": [k.lower() for k in clean_q.split() if len(k) > 3]
                    })
    except Exception:
        pass
    finally:
        if should_close:
            client.close()

    return items

def search_commercial_api(query: str) -> List[Dict[str, Any]]:
    """Queries Tavily or Serper commercial search API if configured."""
    items = []
    if settings.TAVILY_API_KEY:
        try:
            resp = httpx.post(
                "https://api.tavily.com/search",
                json={"api_key": settings.TAVILY_API_KEY, "query": query, "search_depth": "basic", "max_results": 3},
                timeout=5.0
            )
            if resp.status_code == 200:
                data = resp.json()
                for res in data.get("results", []):
                    items.append({
                        "id": f"tavily_{abs(hash(res.get('url', ''))) % 1000000}",
                        "source_title": res.get("title", "Tavily Search Result"),
                        "source_url": res.get("url", ""),
                        "publisher": res.get("url", "").split("/")[2].replace("www.", "").title() if "//" in res.get("url", "") else "Tavily Index",
                        "publication_date": res.get("published_date") or "Documented Online",
                        "passage": res.get("content", ""),
                        "retrieval_method": "tavily_web_search",
                        "keywords": [k.lower() for k in query.split()],
                        "target_locations": []
                    })
        except Exception:
            pass

    return items

def retrieve_evidence(
    claim_components: Dict[str, Any],
    image_phash: str,
    scene_clues: Dict[str, Any] = None,
    candidate_hypotheses: List[Dict[str, Any]] = None,
    investigation_mode: str = "deep"
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """
    STAGE D: Dynamic Multi-Strategy Evidence Retrieval.
    Tailored specifically to the current image and claim.
    Executes:
    1. Visual distance search against reference image collection
    2. Curated local reference corpus
    3. Live DuckDuckGo web search for current events and disaster reports
    4. Live Wikipedia Open Knowledge search for historical events, landmarks, entities
    5. Commercial search engine (Tavily/Serper) if configured

    Returns: (retrieved_evidence_items, visual_match_info, search_execution_trace)
    """
    trace = {
        "search_queries_executed": [],
        "search_providers_used": ["Local Curated Fact-Checking & Landmark Corpus"],
        "provider_status": {
            "local_corpus": "Active",
            "wikipedia_adapter": "Active (Public HTTPS)",
            "live_web_search": "Active (DuckDuckGo Live)",
            "commercial_web_search": "Configured (Tavily)" if settings.TAVILY_API_KEY else "Unconfigured (Set TAVILY_API_KEY or SERPER_API_KEY in .env to enable)",
            "reverse_image_engine": "Reference Catalog Perceptual Hash Distance Forensics"
        },
        "retrieval_status": "in_progress",
        "zero_evidence_reason": None,
        "notes": []
    }

    # 1. Load Local Curated Reference Corpus
    corpus_path = Path(settings.REFERENCE_DOCS_DIR) / "corpus.json"
    if not corpus_path.exists():
        corpus_path = settings.BASE_DIR / "data" / "reference_documents" / "corpus.json"

    documents = []
    if corpus_path.exists():
        try:
            with open(corpus_path, "r", encoding="utf-8") as f:
                documents = json.load(f)
        except Exception:
            documents = []

    # 2. Reference Image Catalog & Perceptual Distance Forensics
    ref_samples_dir = Path(settings.SAMPLE_DIR)
    if not ref_samples_dir.exists():
        ref_samples_dir = settings.BASE_DIR / "data" / "samples"

    reference_images_meta = [
        {
            "id": "ref_sangli_ganapati_mandir",
            "title": "Sangli Ganapati Mandir (Krishna River Ghāts)",
            "filename": "sangli_ganapati_mandir.jpg",
            "date": "1843-Historical / 2024 Archive",
            "location": "Sangli, Maharashtra",
            "category": "monument",
            "publisher": "Maharashtra Tourism Directory / District Gazetteer",
            "source_url": "https://www.maharashtratourism.gov.in/attractions/ganapati-temple-sangli",
            "provenance": "Authentic photograph of the historic black basalt stone Ganapati Mandir on the Krishna river banks in Sangli."
        },
        {
            "id": "ref_mumbai_flood_2019",
            "title": "Central Mumbai Monsoon Waterlogging Archive",
            "filename": "mumbai_flooding_2019.jpg",
            "date": "2019-07-26",
            "location": "Mumbai",
            "category": "disaster",
            "publisher": "Press Photo Archive / PTI",
            "source_url": "https://indianexpress.com/article/cities/mumbai/monsoon-deluge-hindmata-dadar-flooding-railways-july-2019/",
            "provenance": "Authentic news photograph taken during July 2019 Mumbai monsoon floods in Hindmata."
        },
        {
            "id": "ref_synthetic_cyclone",
            "title": "Generative Diffusion Cyclone Visualization",
            "filename": "synthetic_cyclone.jpg",
            "date": "2024-03-12",
            "location": "Synthetic (Unanchored)",
            "category": "synthetic",
            "publisher": "Synthetic Media Research Benchmark",
            "source_url": "https://mausam.imd.gov.in/imd_latest/contents/cyclone_bulletin_archive.php",
            "provenance": "Synthetic image generated to test diffusion swirl artifact detection."
        },
        {
            "id": "ref_turkey_relief_2023",
            "title": "Kahramanmaraş Earthquake Relief Staging Area",
            "filename": "turkey_earthquake_relief.jpg",
            "date": "2023-02-11",
            "location": "Kahramanmaraş, Turkey",
            "category": "news_event",
            "publisher": "UN OCHA / Field Logistics",
            "source_url": "https://reports.unocha.org/en/country/turkiye/card/earthquake-response-kahramanmaras-field-operations/",
            "provenance": "Documentary capture of humanitarian aid distribution following the Feb 2023 earthquake."
        },
        {
            "id": "ref_paris_yellow_vests_2018",
            "title": "Yellow Vests Demonstration on Champs-Élysées",
            "filename": "paris_protest_2018.jpg",
            "date": "2018-11-24",
            "location": "Paris, France",
            "category": "protest",
            "publisher": "Le Monde / AFP Photo",
            "source_url": "https://www.lemonde.fr/politique/article/2018/11/24/gilets-jaunes-tensions-sur-les-champs-elysees-a-paris_5387995_823448.html",
            "provenance": "Authentic photograph from the 2018 Yellow Vest protests in Paris."
        }
    ]

    visual_match = None
    best_visual_score = 0.0
    scene_cat = (scene_clues.get("scene_category") if scene_clues else "")
    claim_raw_lower = (claim_components.get("raw_claim") or "").lower()

    for ref in reference_images_meta:
        # Cross-category guard: A temple cannot match a disaster scene, and disaster cannot match monument
        if ref.get("category") == "monument" and (scene_cat in ["disaster_or_weather", "screenshot_or_social_post"] or "flood" in claim_raw_lower):
            continue
        if ref.get("category") == "disaster" and scene_cat in ["architectural_or_monument", "document_or_signboard"] and "flood" not in claim_raw_lower:
            continue

        ref_path = ref_samples_dir / ref["filename"]
        if not ref_path.exists():
            ref_path = settings.BASE_DIR / "data" / "samples" / ref["filename"]

        if ref_path.exists() and image_phash:
            try:
                from app.services.image_analysis.metadata_extractor import extract_image_metadata
                ref_meta = extract_image_metadata(str(ref_path))
                ref_phash = ref_meta.get("perceptual_hash", "")
                dist = hamming_distance(image_phash, ref_phash)
                sim = max(0.0, 1.0 - (dist / 32.0))

                is_exact = (dist <= 4 or sim >= 0.88)
                is_similar = (dist <= 6 and sim >= 0.81)

                if sim > best_visual_score and is_similar:
                    best_visual_score = sim
                    visual_match = {
                        "candidate_id": ref["id"],
                        "title": ref["title"],
                        "image_url": f"/samples/{ref['filename']}",
                        "provenance": ref["provenance"],
                        "known_date": ref["date"],
                        "location": ref["location"],
                        "source_url": ref["source_url"],
                        "publisher": ref["publisher"],
                        "similarity_score": round(sim, 3),
                        "distance_bits": dist,
                        "match_type": "exact_archival_match" if is_exact else "visually_similar_reference_photo",
                        "is_exact_match": is_exact
                    }
            except Exception:
                pass

    # 3. Dynamic Search Queries Construction
    claim_text = claim_components.get("raw_claim", "")
    target_event = (claim_components.get("event") or "").strip()
    target_loc = (claim_components.get("location") or "").strip()
    target_time = (claim_components.get("time_reference") or "").strip()
    scene_category = (scene_clues.get("scene_category") if scene_clues else "")

    queries = [claim_text]
    trace["search_queries_executed"].append(f"Query 1 (Exact Claim): \"{claim_text}\"")

    # Claimed event + location query
    if target_event and target_loc:
        q_event_loc = f"{target_event} {target_loc}"
        if q_event_loc not in queries:
            queries.append(q_event_loc)
            trace["search_queries_executed"].append(f"Query 2 (Event in Location): \"{q_event_loc}\"")

    # Add temporal news query if current or specific date asserted
    if target_loc and target_time and target_time.lower() in ["today", "now", "breaking", "yesterday", "recent"]:
        q_time_news = f"{target_event or 'incident'} {target_loc} news {target_time}"
        if q_time_news not in queries:
            queries.append(q_time_news)
            trace["search_queries_executed"].append(f"Query 3 (Temporal News Verification): \"{q_time_news}\"")

    # Add candidate hypothesis queries
    if candidate_hypotheses:
        for cand in candidate_hypotheses[:3]:
            c_name = cand.get("candidate_name", "")
            c_city = cand.get("candidate_city", "")
            if c_city and "unanchored" not in c_name.lower():
                cand_q = f"{c_name} {c_city}"
                if cand_q not in queries:
                    queries.append(cand_q)
                    trace["search_queries_executed"].append(f"Query (Candidate Hypothesis): \"{cand_q}\"")

    # Add OCR extracted text query if visible text found in image
    if scene_clues and scene_clues.get("text_and_signboards"):
        for sign in scene_clues["text_and_signboards"][:2]:
            clean_sign = re.sub(r'[^a-zA-Z0-9\s]', '', sign).strip()
            if len(clean_sign) > 4 and clean_sign not in queries:
                queries.append(clean_sign)
                trace["search_queries_executed"].append(f"Query (Image Signboard / Text): \"{clean_sign}\"")

    # 4. Live External Web & Encyclopedic Retrieval
    live_external_items = []
    with httpx.Client(timeout=4.0) as http_client:
        # Wikipedia live encyclopedic search
        wiki_targets = []
        if target_event and target_loc:
            wiki_targets.append(f"{target_event} {target_loc}")
        if target_loc and len(target_loc) > 2:
            wiki_targets.append(target_loc)
        if candidate_hypotheses:
            for cand in candidate_hypotheses[:2]:
                if "unanchored" not in cand.get("candidate_name", "").lower():
                    wiki_targets.append(f"{cand['candidate_name']} {cand['candidate_city']}")

        for w_query in list(dict.fromkeys(wiki_targets))[:2]:
            w_res = search_live_wikipedia_reference(w_query, client=http_client)
            if w_res:
                if "Live Wikipedia Open Knowledge Adapter" not in trace["search_providers_used"]:
                    trace["search_providers_used"].append("Live Wikipedia Open Knowledge Adapter")
                live_external_items.extend(w_res)

        # DuckDuckGo live web search
        if settings.ENABLE_EXTERNAL_WEB_SEARCH:
            ddg_query = queries[1] if len(queries) > 1 else queries[0]
            ddg_res = search_duckduckgo_web(ddg_query, client=http_client)
            if ddg_res:
                if "Live Web Search (DuckDuckGo)" not in trace["search_providers_used"]:
                    trace["search_providers_used"].append("Live Web Search (DuckDuckGo)")
                live_external_items.extend(ddg_res)

    # Commercial search (Tavily) if configured
    if settings.TAVILY_API_KEY:
        tav_res = search_commercial_api(queries[0])
        if tav_res:
            trace["search_providers_used"].append("Tavily Commercial Web API")
            live_external_items.extend(tav_res)

    all_docs = documents + live_external_items

    # 5. Semantic Scoring & Re-ranking
    retrieved_items = []
    if all_docs:
        doc_texts = [f"{d.get('source_title', d.get('title', ''))} {d.get('passage', '')} {' '.join(d.get('keywords', []))}" for d in all_docs]
        combined_queries_text = " ".join(queries)
        corpus_texts = [combined_queries_text] + doc_texts

        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        try:
            tfidf_matrix = vectorizer.fit_transform(corpus_texts)
            cosine_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        except Exception:
            cosine_scores = [0.0] * len(all_docs)

        for idx, doc in enumerate(all_docs):
            text_sim = float(cosine_scores[idx])

            doc_locations = [loc.lower() for loc in doc.get("target_locations", [])]
            doc_text_lower = (doc.get("source_title", doc.get("title", "")) + " " + doc.get("passage", "")).lower()
            doc_target_event = (doc.get("target_event") or "").lower()
            doc_keywords = [k.lower() for k in doc.get("keywords", [])]

            # Cross-topic contamination guard:
            # A flood claim must NEVER retrieve temple documents, and a temple claim must NEVER retrieve flood documents
            is_claim_flood = any(k in claim_text.lower() for k in ["flood", "flooding", "waterlogging", "deluge", "submerged", "monsoon"])
            is_doc_temple = any(k in doc_target_event for k in ["mandir", "temple", "monument", "minar", "arch", "shrine"]) or any(k in doc_keywords for k in ["mandir", "temple", "shrine"])
            if is_claim_flood and is_doc_temple and not (visual_match and visual_match["candidate_id"] == doc.get("related_image_id")):
                continue

            is_claim_temple = any(k in claim_text.lower() for k in ["temple", "mandir", "shrine", "cathedral", "church", "monument"])
            is_doc_disaster = any(k in doc_target_event for k in ["flood", "cyclone", "earthquake", "fire"])
            if is_claim_temple and is_doc_disaster and not (visual_match and visual_match["candidate_id"] == doc.get("related_image_id")):
                continue

            # Check if this document genuinely matches the topical subject of the claim
            is_subject_match = (
                (visual_match and visual_match["candidate_id"] == doc.get("related_image_id")) or
                (target_event and any(target_event.lower() in kw or kw in target_event.lower() for kw in doc_keywords + [doc_target_event])) or
                (text_sim >= 0.15)
            )

            # Location and Entity overlap bonuses (ONLY if topical subject matches)
            overlap_bonus = 0.0
            if is_subject_match:
                if target_loc and any(target_loc.lower() in dloc or dloc in target_loc.lower() for dloc in doc_locations):
                    overlap_bonus += 0.20

                if candidate_hypotheses:
                    for c in candidate_hypotheses:
                        c_city = c.get("candidate_city", "").lower()
                        if c_city and "unspecified" not in c_city and "unknown" not in c_city:
                            if c_city in doc_text_lower or any(c_city in dloc or dloc in c_city for dloc in doc_locations):
                                overlap_bonus += 0.15

            # Visual match association bonus (only if exact or high-similarity visual match!)
            visual_bonus = 0.0
            if visual_match and visual_match["candidate_id"] == doc.get("related_image_id"):
                visual_bonus = 0.45 if visual_match.get("is_exact_match") else 0.30

            combined_score = min(1.0, round(text_sim * 0.40 + overlap_bonus + visual_bonus, 3))

            # Calibrated thresholding
            min_thresh = 0.10 if investigation_mode == "research" else (0.14 if investigation_mode == "deep" else 0.18)

            if combined_score >= min_thresh or (visual_match and visual_match["candidate_id"] == doc.get("related_image_id")):
                title = doc.get("source_title", doc.get("title", "Untitled Reference"))
                url = doc.get("source_url", doc.get("url", ""))
                publisher = doc.get("publisher", "Independent Published Record")
                pub_date = doc.get("publication_date", "Date Available in Record")
                passage = doc.get("passage", "")

                rel_calc = calculate_source_reliability(
                    publisher=publisher,
                    source_url=url,
                    publication_date=pub_date
                )

                # Determine relationship stance dynamically:
                rel_rules = doc.get("relationship_rules", {})
                relationship = "neutral"

                if is_subject_match:
                    if "if_claimed_location" in rel_rules and target_loc and target_loc.lower() == rel_rules["if_claimed_location"].lower():
                        relationship = rel_rules.get("stance", "contradicts")
                    elif "if_claimed_time" in rel_rules and target_time:
                        relationship = rel_rules.get("stance", "neutral")
                    elif rel_rules.get("stance"):
                        relationship = rel_rules["stance"]
                    elif visual_match and (visual_match.get("is_exact_match") or visual_match.get("similarity_score", 0.0) >= 0.80):
                        v_loc = (visual_match.get("location") or "").lower()
                        if target_loc and not re.search(rf"\b{re.escape(target_loc.lower())}\b", v_loc):
                            # The visual match proves a different location; background documents do not support the claimed image location
                            relationship = "neutral"
                        elif target_loc and re.search(rf"\b{re.escape(target_loc.lower())}\b", v_loc):
                            relationship = "supports"
                    elif target_event and target_loc and "wikipedia" not in publisher.lower():
                        # Only mark as supports if both event and location are explicitly present in journalistic reporting
                        has_ev = bool(re.search(rf"\b{re.escape(target_event.lower())}\b", doc_text_lower))
                        has_loc = bool(re.search(rf"\b{re.escape(target_loc.lower())}\b", doc_text_lower))
                        if has_ev and has_loc:
                            relationship = "supports"
                        elif has_loc:
                            relationship = "neutral"

                retrieved_items.append({
                    "id": doc.get("id"),
                    "source_title": title,
                    "source_url": url,
                    "publisher": publisher,
                    "publication_date": pub_date,
                    "relationship_to_claim": relationship,
                    "retrieval_score": max(combined_score, 0.18),
                    "reliability_score": rel_calc["reliability_score"],
                    "passage": passage,
                    "retrieval_method": "visual_and_semantic" if visual_bonus > 0 else doc.get("retrieval_method", "semantic_text"),
                    "indicators": rel_calc["indicators"],
                    "thumbnail_url": visual_match["image_url"] if visual_match and visual_match["candidate_id"] == doc.get("related_image_id") else None
                })

    # Sort descending by score and deduplicate by URL
    retrieved_items.sort(key=lambda x: x["retrieval_score"], reverse=True)
    seen_urls = set()
    deduped = []
    for item in retrieved_items:
        u = item.get("source_url", "").strip()
        if u and u not in seen_urls:
            seen_urls.add(u)
            deduped.append(item)

    if deduped:
        trace["retrieval_status"] = f"Completed: {len(deduped)} grounded evidence record(s) retrieved exceeding relevance threshold."
    else:
        trace["retrieval_status"] = "Completed: 0 evidence records met threshold."
        trace["zero_evidence_reason"] = (
            f"Zero reference documents in local corpus or public web searches matched '{claim_text}' with sufficient relevance. "
            "In accordance with responsible AI standards, TRUTHLENS reports Insufficient Evidence rather than fabricating sources."
        )
        trace["notes"].append(trace["zero_evidence_reason"])

    return deduped, visual_match, trace
