frappe.listview_settings["Job Applicant"] = Object.assign(
	frappe.listview_settings["Job Applicant"] || {},
	{
		add_fields: ["ats_score", "ats_passes_passmark"],
		formatters: {
			ats_score(value, _df, doc) {
				if (value === null || value === undefined) return "";
				let color = "red";
				if (value >= 70) color = "green";
				else if (value >= 40) color = "orange";
				const passes = doc.ats_passes_passmark
					? "<span class='indicator-pill green' style='margin-left:6px'>pass</span>"
					: "";
				return `<span style="color:${color};font-weight:600">${Number(value).toFixed(1)}%</span>${passes}`;
			},
		},
		onload(listview) {
			listview.page.add_inner_button(
				__("Show only passing"),
				() => {
					listview.filter_area.add([
						["Job Applicant", "ats_passes_passmark", "=", 1],
					]);
				},
				__("ATS")
			);
		},
	}
);
