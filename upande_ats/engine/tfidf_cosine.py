def score_tfidf(text: str, keywords: list, synonym_map: dict) -> dict:
	"""
	Build a 'keyword document' (each keyword weighted by repetition based on its
	weight) and compute cosine similarity vs CV text.

	Returns {sub_score: 0-100}.
	"""
	if not text or not keywords:
		return {"sub_score": 0.0}

	from sklearn.feature_extraction.text import TfidfVectorizer
	from sklearn.metrics.pairwise import cosine_similarity

	terms = []
	for kw in keywords:
		term = (kw.get("keyword") or "").strip().lower()
		if not term:
			continue
		weight = max(1, int(kw.get("weight") or 1))
		terms.extend([term] * weight)
		for syn in synonym_map.get(term, []):
			terms.append(syn)

	if not terms:
		return {"sub_score": 0.0}

	keyword_doc = " ".join(terms)

	try:
		vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
		matrix = vec.fit_transform([keyword_doc, text])
		sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
	except ValueError:
		return {"sub_score": 0.0}

	sub_score = max(0.0, min(1.0, float(sim))) * 100.0
	return {"sub_score": round(sub_score, 2)}
