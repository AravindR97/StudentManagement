# Copyright (c) 2025, Aravind and contributors
# For license information, please see license.txt

import re
import frappe
from frappe.model.document import Document


class StudentEnrollment(Document):
    def validate(self):
        self.check_missing_fields()
        self.duplicate_enrollment()
        self.validate_email_format()

    def on_update(self):
        if self.status == "Approved" and self.has_value_changed("status"):
            self.send_email_on_approval()

    def check_missing_fields(self):
        if not self.student_name or not self.course or not self.email:
            frappe.throw("Missing mandatory fields")

    # Send approval mail
    def send_email_on_approval(self):
        sub = "Course Enrollment Approved"
        content = f"""
		Dear {self.student_name},
        
        We are excited to inform you that your enrollment for course {self.course} has been approved.
        """

        frappe.sendmail(recipients=[self.email], subject=sub, message=content)

    # Additional checks
    # Prevent duplicate enrollment
    def duplicate_enrollment(self):
        is_enrolled = frappe.db.exists(
            "Student Enrollment",
            {"student_name": self.student_name, "course": self.course, "doctstatus": 1},
        )
        if is_enrolled:
            frappe.throw(f"{self.student_name} is already enrolled in {self.course}")

    # Validate email format
    def validate_email_format(self):
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, self.email):
            frappe.throw("Please enter a valid email address")

    def validate_enrollment_date(self):
        if (
            self.enrollment_date
            and frappe.utils.getdate(self.enrollment_date) > frappe.utils.getdate()
        ):
            frappe.throw("Cannot select future date")
