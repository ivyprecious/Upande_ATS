"""Smoke test runner. Use: bench --site <site> execute "frappe.get_attr('upande_ats.smoke.<fn>')()" """

import json
import os

import frappe
from frappe.utils.file_manager import save_file

from upande_ats.engine import score_applicant


OPENING_NAME = "ATS Smoke Python Developer"
APPLICANT_EMAIL = "smoketest@example.com"


def _company():
	return frappe.db.get_default("Company") or frappe.get_all("Company", limit=1)[0].name


def setup_all():
	"""Idempotent setup: opening + applicant + CV."""
	# Disable auto-scoring for setup so save() doesn't try to enqueue (no redis in tests)
	settings = frappe.get_single("ATS Settings")
	if settings.auto_score_on_resume_upload:
		settings.auto_score_on_resume_upload = 0
		settings.flags.ignore_permissions = True
		settings.save()

	if not frappe.db.exists("Designation", "Senior Python Developer"):
		frappe.get_doc({"doctype": "Designation", "designation_name": "Senior Python Developer"}).insert(
			ignore_permissions=True
		)

	for s in frappe.get_all("ATS Score", filters={"applicant": APPLICANT_EMAIL}, pluck="name"):
		frappe.delete_doc("ATS Score", s, force=True, ignore_permissions=True)
	if frappe.db.exists("Job Applicant", APPLICANT_EMAIL):
		frappe.delete_doc("Job Applicant", APPLICANT_EMAIL, force=True, ignore_permissions=True)
	for jo in frappe.get_all("Job Opening", filters={"job_title": OPENING_NAME}, pluck="name"):
		frappe.delete_doc("Job Opening", jo, force=True, ignore_permissions=True)

	opening = frappe.get_doc({
		"doctype": "Job Opening",
		"job_title": OPENING_NAME,
		"company": _company(),
		"status": "Open",
		"designation": "Senior Python Developer",
		"description": "Senior python role.",
		"ats_keywords": [
			{"keyword": "Python", "weight": 5, "is_mandatory": 1},
			{"keyword": "Django", "weight": 4},
			{"keyword": "JavaScript", "weight": 3},
			{"keyword": "React", "weight": 3},
			{"keyword": "Leadership", "weight": 2},
			{"keyword": "Kubernetes", "weight": 2},
			{"keyword": "Rust", "weight": 2},
			{"keyword": "AWS", "weight": 2},
		],
	}).insert(ignore_permissions=True)

	applicant = frappe.get_doc({
		"doctype": "Job Applicant",
		"applicant_name": "ATS Smoke Test",
		"email_id": APPLICANT_EMAIL,
		"job_title": opening.name,
		"status": "Open",
	}).insert(ignore_permissions=True)

	cv_path = "/tmp/test_cv.txt"
	if not os.path.exists(cv_path):
		raise RuntimeError("Run the setup with /tmp/test_cv.txt available")
	with open(cv_path, "rb") as f:
		content = f.read()
	file_doc = save_file(
		fname="smoketest_cv.txt", content=content, dt="Job Applicant", dn=applicant.name, is_private=1
	)
	applicant.resume_attachment = file_doc.file_url
	applicant.save(ignore_permissions=True)
	frappe.db.commit()

	print(f"Opening: {opening.name}")
	print(f"Applicant: {applicant.name}")
	print(f"Resume: {applicant.resume_attachment}")
	return opening.name, applicant.name


def run_baseline():
	opening_name, applicant_name = setup_all()
	result = score_applicant(applicant_name, opening_name)
	_print_result("BASELINE (Rust not mandatory)", result)
	return result


def run_mandatory():
	opening_name, applicant_name = setup_all()
	opening = frappe.get_doc("Job Opening", opening_name)
	for kw in opening.ats_keywords:
		if kw.keyword == "Rust":
			kw.is_mandatory = 1
	opening.save(ignore_permissions=True)
	frappe.db.commit()

	result = score_applicant(applicant_name, opening_name)
	_print_result("MANDATORY (Rust mandatory but missing -> should be capped at 40)", result)
	return result


def _print_result(label, result):
	print(f"\n=== {label} ===")
	print(f"Score: {result['score_pct']}%")
	print(f"Passmark used: {result['passmark_used']}")
	print(f"Passes: {bool(result['passes_passmark'])}")
	print(f"Mandatory unmatched: {result['mandatory_unmatched']!r}")
	print(f"Note: {result.get('note') or '-'}")
	if result.get("score_breakdown"):
		bd = json.loads(result["score_breakdown"])
		for engine, data in bd.items():
			print(f"  [{engine}] = {data.get('sub_score')}%")
			if "matched" in data:
				print(f"    matched: {[m['keyword'] for m in data['matched']]}")
			if "missing" in data:
				print(f"    missing: {[m['keyword'] for m in data['missing']]}")
