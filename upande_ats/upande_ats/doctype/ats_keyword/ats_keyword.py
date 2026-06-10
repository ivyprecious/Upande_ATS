from frappe.model.document import Document


class ATSKeyword(Document):
	def validate(self):
		if self.weight is None or self.weight < 0:
			self.weight = 1
		if self.weight > 5:
			self.weight = 5
