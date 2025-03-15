# Copyright (c) 2025, Aravind and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days
from frappe.workflow.doctype.workflow.workflow import apply_workflow


class TestStudentEnrollment(FrappeTestCase):
    def setUp(self):
        # test data
        self.test_student = "Test Student"
        self.test_email = "test@example.com"
        self.test_course = "Test Course"

    def tearDown(self):
        # Clean up
        for enrollment in frappe.get_all(
            "Student Enrollment", filters={"student_name": self.test_student}
        ):
            doc = frappe.get_doc("Student Enrollment", enrollment.name)
            if doc.docstatus == 1:
                doc.cancel()
            frappe.delete_doc("Student Enrollment", doc.name)

    def test_validation_enrollment_date(self):
        """Test that future enrollment dates are not allowed"""
        # Create enrollment with future date
        enrollment = frappe.get_doc(
            {
                "doctype": "Student Enrollment",
                "student_name": self.test_student,
                "email": self.test_email,
                "course": self.test_course,
                "enrollment_date": add_days(getdate(), 5),
                "status": "Draft",
            }
        )

        self.assertRaises(frappe.ValidationError, enrollment.insert)

    def test_validation_email_format(self):
        # Create enrollment with invalid email
        enrollment = frappe.get_doc(
            {
                "doctype": "Student Enrollment",
                "student_name": self.test_student,
                "email": "invalid_email",
                "course": self.test_course,
                "enrollment_date": getdate(),
                "status": "Draft",
            }
        )

        self.assertRaises(frappe.ValidationError, enrollment.insert)

    def test_workflow_transition(self):
        # Create enrollment with valid data
        enrollment = frappe.get_doc(
            {
                "doctype": "Student Enrollment",
                "student_name": self.test_student,
                "email": self.test_email,
                "course": self.test_course,
                "enrollment_date": getdate(),
                "status": "Draft",
            }
        )
        enrollment.insert()

        # Verify states
        self.assertEqual(enrollment.status, "Draft")
        enrollment.submit()
        self.assertEqual(enrollment.status, "Submitted")

        # Apply workflow to change status to Approved
        workflow = frappe.get_doc("Workflow", "Student Enrollment Approval")
        workflow_transition = next(
            (
                trans
                for trans in workflow.transitions
                if trans.state == "Submitted" and trans.next_state == "Approved"
            ),
            None,
        )

        if workflow_transition:
            apply_workflow(enrollment, workflow_transition.action)
            enrollment.reload()
            self.assertEqual(enrollment.status, "Approved")
