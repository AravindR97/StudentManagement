// Copyright (c) 2025, Aravind and contributors
// For license information, please see license.txt

frappe.ui.form.on("Student Enrollment", {
    before_save: function (frm) {
        var email_format = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!email_format.test(frm.doc.email)) {
            frappe.throw("Please enter a valid email address")
        }
    },
    enrollment_date: function (frm) {
        const today = frappe.datetime.get_today()
        if (frm.doc.enrollment_date > today) {
            frappe.throw("Cannot select future date")
        }
    }
});
