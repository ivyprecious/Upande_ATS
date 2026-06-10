frappe.ui.form.on("Job Opening", {
	refresh(frm) {
		if (frm.is_new()) return;

		frm.add_custom_button(
			__("Re-score All Candidates"),
			() => {
				frappe.confirm(
					__("Queue ATS scoring for every applicant of this opening?"),
					() => {
						frappe.call({
							method: "upande_ats.engine.rescore_opening",
							args: { opening: frm.doc.name },
							freeze: true,
						}).then((r) => {
							if (r.message) {
								frappe.show_alert({
									message: __("Queued {0} scoring jobs.", [r.message.queued]),
									indicator: "blue",
								});
							}
						});
					}
				);
			},
			__("ATS")
		);

		frm.add_custom_button(
			__("View Shortlist"),
			() => {
				frappe.route_options = {
					job_title: frm.doc.name,
					ats_passes_passmark: 1,
				};
				frappe.set_route("List", "Job Applicant");
			},
			__("ATS")
		);
	},
});
