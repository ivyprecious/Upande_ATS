import frappe


def maybe_score_on_save(doc, method=None):
	"""Trigger background scoring when a Job Applicant gets a new/changed resume."""
	try:
		settings = frappe.get_single("ATS Settings")
	except Exception:
		return

	if not bool(settings.auto_score_on_resume_upload):
		return
	if not doc.get("resume_attachment"):
		return
	if not doc.get("job_title"):
		return

	previous = doc.get_doc_before_save()
	if (
		previous is not None
		and previous.get("resume_attachment") == doc.get("resume_attachment")
		and doc.get("ats_score_link")
	):
		return

	try:
		frappe.enqueue(
			"upande_ats.engine.score_applicant",
			queue="long",
			job_name=f"ats-score-{doc.name}",
			enqueue_after_commit=True,
			applicant=doc.name,
			opening=doc.job_title,
		)
	except Exception:
		# Redis unavailable (e.g. in dev/console). Log and skip — scoring can be
		# triggered manually via the Re-score button.
		frappe.log_error(frappe.get_traceback(), "ATS auto-score enqueue failed")
