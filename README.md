# Student Management Module

## Overview
The Student Management module is designed to manage student enrollments for courses. It provides functionality for creating, submitting, approving, and rejecting student enrollments, along with automated email notifications on approving enrollment.


## Installation

### Prerequisites
- Frappe Framework v15

### Steps
1. Create Frappe v15 bench
2. Get the student_management app from github:

```
bench get-app https://github.com/AravindR97/StudentManagement.git
```

3. Create a new site to install the app (Enter new password)

```
bench new-site <sitename>
```

4. Install the app on the site

```
bench --site <sitename> install-app student_management
```

5. Start the server using `bench start` and access the site on browser

6. Log In to the app using username 'Administrator' and Password entered during site creation.

7. Setup Email Account:
- Go to Email > Email Account > New Email Account
- Configure your SMTP settings for sending emails

## Usage

### Creating a Student Enrollment
1. Go to Student Enrollment Doctype
2. Click "Add Student Enrollment" button
3. Fill in the required fields:
- Student Name
- Email
- Course
- Enrollment Date
4. Save the enrollment

### Workflow
The Student Enrollment follows this workflow:
1. **Draft**: Initial state when created
2. **Submitted**: After submission
3. **Approved**: When the enrollment is approved
4. **Rejected**: If the enrollment is not approved

## Testing
Enable tests:
```
bench --site <sitename> set-config allow_tests true
```

Run the tests using:
```
bench --site <sitename> run-tests --module "student_management.student_management.doctype.student_enrollment.test_student_enrollment"
```