import re


def _tokens(text: str):
	return [t for t in re.split(r"[^A-Za-z0-9+#.\-]+", text or "") if t]


def score_fuzzy(text: str, keywords: list, synonym_map: dict, threshold: int = 85) -> dict:
	"""
	rapidfuzz partial_ratio over windows of up to 3 consecutive tokens.
	A keyword is matched if any window scores >= threshold against any of
	[keyword] + synonyms.

	Returns {sub_score, matched, missing}.
	"""
	if not text or not keywords:
		return {"sub_score": 0.0, "matched": [], "missing": []}

	from rapidfuzz import fuzz

	toks = _tokens(text)
	# Pre-build candidate phrases (1-, 2-, and 3-grams)
	candidates = set()
	for n in (1, 2, 3):
		for i in range(len(toks) - n + 1):
			candidates.add(" ".join(toks[i : i + n]).lower())

	total_weight = sum(int(k.get("weight") or 1) for k in keywords)
	earned_weight = 0
	matched, missing = [], []

	for kw in keywords:
		term = (kw.get("keyword") or "").strip().lower()
		weight = int(kw.get("weight") or 1)
		if not term:
			continue
		variants = [term] + synonym_map.get(term, [])

		best = 0
		for variant in variants:
			vlen = len(variant)
			for cand in candidates:
				if abs(len(cand) - vlen) > max(4, vlen):
					continue
				score = fuzz.partial_ratio(variant, cand)
				if score > best:
					best = score
					if best >= 100:
						break
			if best >= 100:
				break

		if best >= threshold:
			earned_weight += weight
			matched.append({"keyword": term, "weight": weight, "fuzzy_score": best})
		else:
			missing.append({"keyword": term, "weight": weight, "best_score": best})

	sub_score = (earned_weight / total_weight * 100.0) if total_weight else 0.0
	return {
		"sub_score": round(sub_score, 2),
		"matched": matched,
		"missing": missing,
	}
