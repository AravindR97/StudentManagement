# Copyright (c) 2025, Aravind and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import getdate, add_days


class TestStudentEnrollment(FrappeTestCase):
    def setUp(self):
        # test data
        self.test_student = "Test Student"
        self.test_email = "test@example.com"
        self.test_course = "Course-1"

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

    def test_workflow_transitions(self):
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
    
        # Verify initial states
        self.assertEqual(enrollment.status, "Draft")
        enrollment.submit()
        self.assertEqual(enrollment.status, "Submitted")
        
        # Get the workflow
        workflow = frappe.get_doc("Workflow", "Student Enrollment Approval")
        
        # Test 1: Transition from Submitted to Approved
        workflow_transition_approve = next(
            (
                trans
                for trans in workflow.transitions
                if trans.state == "Submitted" and trans.next_state == "Approved"
            ),
            None,
        )
        
        if workflow_transition_approve:
            # Create a copy of the enrollment for the approval path
            enrollment_approve = frappe.get_doc("Student Enrollment", enrollment.name)
            
            # Instead of apply_workflow, use the workflow.transition_doctype method
            enrollment_approve.workflow_state = "Submitted"  # Ensure correct starting state
            frappe.db.set_value("Student Enrollment", enrollment_approve.name, "workflow_state", "Submitted")
            
            # Apply the transition - this is the corrected part
            from frappe.model.workflow import apply_workflow
            apply_workflow(enrollment_approve, workflow_transition_approve.action)
            
            enrollment_approve.reload()
            self.assertEqual(enrollment_approve.workflow_state, "Approved")
            self.assertEqual(enrollment_approve.status, "Approved")
        
        # Test 2: Transition from Submitted to Rejected
        workflow_transition_reject = next(
            (
                trans
                for trans in workflow.transitions
                if trans.state == "Submitted" and trans.next_state == "Rejected"
            ),
            None,
        )
        
        if workflow_transition_reject:
            # Create a new enrollment for the rejection path
            enrollment_reject = frappe.get_doc(
                {
                    "doctype": "Student Enrollment",
                    "student_name": self.test_student + "_reject",
                    "email": "reject_" + self.test_email,
                    "course": self.test_course,
                    "enrollment_date": getdate(),
                    "status": "Draft",
                }
            )
            enrollment_reject.insert()
            enrollment_reject.submit()
            
            # Apply the rejection workflow
            from frappe.model.workflow import apply_workflow
            apply_workflow(enrollment_reject, workflow_transition_reject.action)
            
            enrollment_reject.reload()
            self.assertEqual(enrollment_reject.workflow_state, "Rejected")
            self.assertEqual(enrollment_reject.status, "Rejected")
