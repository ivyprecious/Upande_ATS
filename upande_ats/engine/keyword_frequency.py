import re


def _expand_terms(keyword: str, synonym_map: dict) -> list:
	"""Return [keyword] + any synonyms registered for this canonical term."""
	terms = [keyword.lower()]
	synonyms = synonym_map.get(keyword.lower(), [])
	terms.extend(synonyms)
	# Dedupe preserving order
	seen, out = set(), []
	for t in terms:
		if t and t not in seen:
			seen.add(t)
			out.append(t)
	return out


def _count_term(text: str, term: str) -> int:
	"""Word-boundary case-insensitive count. Handles multi-word phrases."""
	if not term:
		return 0
	pattern = r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
	return len(re.findall(pattern, text, flags=re.IGNORECASE))


def score_keyword_frequency(text: str, keywords: list, synonym_map: dict) -> dict:
	"""
	Args:
	  text: normalized CV text (already lowercased).
	  keywords: list of dicts with keys keyword, weight, is_mandatory.
	  synonym_map: {canonical_lower: [synonym_lower, ...]}.

	Returns:
	  {sub_score: 0-100, matched: [...], missing: [...], mandatory_unmatched: [...]}
	"""
	if not keywords:
		return {"sub_score": 0.0, "matched": [], "missing": [], "mandatory_unmatched": []}

	total_weight = sum(int(k.get("weight") or 1) for k in keywords)
	earned_weight = 0
	matched, missing, mandatory_unmatched = [], [], []

	for kw in keywords:
		term = (kw.get("keyword") or "").strip()
		weight = int(kw.get("weight") or 1)
		is_mandatory = bool(kw.get("is_mandatory"))
		if not term:
			continue

		terms = _expand_terms(term, synonym_map)
		hits = sum(_count_term(text, t) for t in terms)
		if hits > 0:
			earned_weight += weight
			matched.append({"keyword": term, "weight": weight, "hits": hits, "via": terms})
		else:
			missing.append({"keyword": term, "weight": weight, "is_mandatory": is_mandatory})
			if is_mandatory:
				mandatory_unmatched.append(term)

	sub_score = (earned_weight / total_weight * 100.0) if total_weight else 0.0
	return {
		"sub_score": round(sub_score, 2),
		"matched": matched,
		"missing": missing,
		"mandatory_unmatched": mandatory_unmatched,
	}
