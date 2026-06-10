import os
import re

import frappe


def normalize(text: str) -> str:
	text = text.lower()
	text = re.sub(r"[\t\r\f\v]+", " ", text)
	text = re.sub(r" {2,}", " ", text)
	return text.strip()


def _local_path(file_url: str) -> str:
	if not file_url:
		return ""
	site_path = frappe.get_site_path()
	if file_url.startswith("/private/files/"):
		return os.path.join(site_path, "private", "files", os.path.basename(file_url))
	if file_url.startswith("/files/"):
		return os.path.join(site_path, "public", "files", os.path.basename(file_url))
	return os.path.join(site_path, "public", file_url.lstrip("/"))


def extract_text(file_url: str) -> str:
	"""Return lowercased, whitespace-normalized text content of file at file_url. Empty string on failure."""
	if not file_url:
		return ""

	path = _local_path(file_url)
	if not os.path.exists(path):
		return ""

	ext = os.path.splitext(path)[1].lower().lstrip(".")
	try:
		if ext == "pdf":
			return normalize(_extract_pdf(path))
		if ext in ("docx",):
			return normalize(_extract_docx(path))
		if ext in ("txt", "md"):
			with open(path, encoding="utf-8", errors="ignore") as f:
				return normalize(f.read())
		if ext == "doc":
			return ""
	except Exception:
		frappe.log_error(frappe.get_traceback(), "ATS text extraction failed")
		return ""
	return ""


def _extract_pdf(path: str) -> str:
	import pdfplumber

	parts = []
	with pdfplumber.open(path) as pdf:
		for page in pdf.pages:
			parts.append(page.extract_text() or "")
	return "\n".join(parts)


def _extract_docx(path: str) -> str:
	import docx2txt

	return docx2txt.process(path) or ""
