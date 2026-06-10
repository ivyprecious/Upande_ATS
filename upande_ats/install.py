import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


CUSTOM_FIELDS = {
	"Job Opening": [
		{
			"fieldname": "ats_section",
			"fieldtype": "Section Break",
			"label": "ATS Configuration",
			"insert_after": "description",
			"collapsible": 1,
		},
		{
			"fieldname": "ats_keywords",
			"fieldtype": "Table",
			"label": "ATS Keywords",
			"options": "ATS Keyword",
			"insert_after": "ats_section",
		},
		{
			"fieldname": "ats_passmark_override",
			"fieldtype": "Percent",
			"label": "Passmark Override %",
			"description": "Overrides default passmark from ATS Settings for this opening only.",
			"insert_after": "ats_keywords",
		},
	],
	"Job Applicant": [
		{
			"fieldname": "ats_section",
			"fieldtype": "Section Break",
			"label": "ATS",
			"insert_after": "resume_attachment",
		},
		{
			"fieldname": "ats_score",
			"fieldtype": "Percent",
			"label": "ATS Score %",
			"read_only": 1,
			"in_list_view": 1,
			"in_standard_filter": 1,
			"insert_after": "ats_section",
		},
		{
			"fieldname": "ats_passes_passmark",
			"fieldtype": "Check",
			"label": "Passes Passmark",
			"read_only": 1,
			"in_standard_filter": 1,
			"insert_after": "ats_score",
		},
		{
			"fieldname": "ats_score_link",
			"fieldtype": "Link",
			"label": "Latest Score Record",
			"options": "ATS Score",
			"read_only": 1,
			"insert_after": "ats_passes_passmark",
		},
		{
			"fieldname": "ats_breakdown_html",
			"fieldtype": "HTML",
			"label": "ATS Breakdown",
			"insert_after": "ats_score_link",
		},
	],
}


def after_install():
	create_custom_fields(CUSTOM_FIELDS, update=True)
	_seed_settings()
	frappe.db.commit()


def _seed_settings():
	settings = frappe.get_single("ATS Settings")

	if not settings.engine_weights:
		settings.append("engine_weights", {"engine_name": "Keyword Frequency", "weight_pct": 60, "is_enabled": 1})
		settings.append("engine_weights", {"engine_name": "TF-IDF Cosine", "weight_pct": 25, "is_enabled": 1})
		settings.append("engine_weights", {"engine_name": "Fuzzy Match", "weight_pct": 15, "is_enabled": 1})

	if settings.default_passmark is None:
		settings.default_passmark = 60
	if settings.fuzzy_match_threshold is None:
		settings.fuzzy_match_threshold = 85
	if not settings.mandatory_keyword_rule:
		settings.mandatory_keyword_rule = "Cap Score"
	if settings.mandatory_cap is None:
		settings.mandatory_cap = 40
	if settings.min_resume_chars is None:
		settings.min_resume_chars = 200
	if not settings.accepted_file_types:
		settings.accepted_file_types = "pdf,docx,doc,txt"
	if settings.auto_score_on_resume_upload is None:
		settings.auto_score_on_resume_upload = 1
	if settings.keep_score_history is None:
		settings.keep_score_history = 1

	if not settings.synonym_groups:
		seed = [
			("JavaScript", "js, ecmascript, node.js, nodejs"),
			("Python", "py, python3"),
			("Communication", "communicator, communicating, communications"),
			("Management", "managing, managed, manager"),
			("Leadership", "leader, leading, led"),
		]
		for canonical, syns in seed:
			settings.append(
				"synonym_groups",
				{"canonical_term": canonical, "synonyms": syns, "is_active": 1},
			)

	settings.flags.ignore_permissions = True
	settings.save()
