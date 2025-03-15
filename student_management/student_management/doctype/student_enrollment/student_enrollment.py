# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class StudentEnrollment(Document):
    def validate(self):
        self.check_missing_fields()
        self.duplicate_enrollment()

    def check_missing_fields(self):
        if not self.student_name or not self.course or not self.email:
            frappe.throw("Missing mandatory fields")

    # Additional checks
    def duplicate_enrollment(self):
        is_enrolled = frappe.db.exists(
            "Student Enrollment",
            {"student_name": self.student_name, "course": self.course, "doctstatus": 1},
        )
        if is_enrolled:
            frappe.throw(f"{self.student_name} is already enrolled in {self.course}")
