import frappe
from frappe import _
from frappe.model.document import Document


class ATSSettings(Document):
	def validate(self):
		self._validate_engine_weights()
		self._validate_thresholds()

	def _validate_engine_weights(self):
		enabled_total = sum(int(w.weight_pct or 0) for w in self.engine_weights if w.is_enabled)
		if not self.engine_weights:
			return
		if enabled_total == 0:
			frappe.throw(_("At least one scoring engine must be enabled with a non-zero weight."))
		if enabled_total != 100:
			frappe.throw(
				_("Enabled engine weights must sum to 100. Current total: {0}").format(enabled_total)
			)

	def _validate_thresholds(self):
		if self.fuzzy_match_threshold is not None and not (0 <= int(self.fuzzy_match_threshold) <= 100):
			frappe.throw(_("Fuzzy Match Threshold must be between 0 and 100."))
		if self.default_passmark is not None and not (0 <= float(self.default_passmark) <= 100):
			frappe.throw(_("Default Passmark must be between 0 and 100."))
		if self.mandatory_cap is not None and not (0 <= float(self.mandatory_cap) <= 100):
			frappe.throw(_("Mandatory Cap must be between 0 and 100."))

	def get_enabled_engines(self):
		return [
			{"engine": w.engine_name, "weight": int(w.weight_pct or 0)}
			for w in self.engine_weights
			if w.is_enabled and (w.weight_pct or 0) > 0
		]

	def get_synonym_map(self):
		mapping = {}
		for grp in self.synonym_groups:
			if not grp.is_active or not grp.canonical_term or not grp.synonyms:
				continue
			syns = [s.strip().lower() for s in grp.synonyms.split(",") if s.strip()]
			mapping[grp.canonical_term.strip().lower()] = syns
		return mapping

	def get_accepted_file_types(self):
		if not self.accepted_file_types:
			return ["pdf", "docx", "doc", "txt"]
		return [t.strip().lower().lstrip(".") for t in self.accepted_file_types.split(",") if t.strip()]
