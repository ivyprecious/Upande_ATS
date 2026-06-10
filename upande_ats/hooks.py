app_name = "upande_ats"
app_title = "Upande ATS"
app_publisher = "Upande"
app_description = "ATS scoring on top of Frappe HRMS"
app_email = "teddy@upande.com"
app_license = "mit"

required_apps = ["hrms"]

after_install = "upande_ats.install.after_install"

doc_events = {
	"Job Applicant": {
		"after_insert": "upande_ats.events.maybe_score_on_save",
		"on_update": "upande_ats.events.maybe_score_on_save",
	},
}

doctype_js = {
	"Job Applicant": "public/js/job_applicant.js",
	"Job Opening": "public/js/job_opening.js",
}

doctype_list_js = {
	"Job Applicant": "public/js/job_applicant_list.js",
}

fixtures = [
	{"dt": "Custom Field", "filters": [["dt", "in", ["Job Opening", "Job Applicant"]], ["fieldname", "like", "ats_%"]]},
]
