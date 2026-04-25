# Staff Management (HRM) Database Design

## 1. StaffProfile (Extends User)
Represents all employees (Teachers, Staff, Admin).
- `user`: OneToOneField(User)
- `employee_id`: CharField(unique) - e.g., EMP-2025-001
- `role`: CharField(choices=['teacher', 'staff', 'admin'])
- `department`: ForeignKey(Department)
- `designation`: CharField
- `gender`: CharField
- `phone`: CharField
- `blood_group`: CharField
- `date_of_joining`: DateField
- `status`: CharField(choices=['active', 'inactive', 'on_leave'])
- `marital_status`: CharField
- `qualification`: TextField
- `experience`: TextField
- `address`: TextField
- `permanent_address`: TextField

## 2. StaffPayroll (Financial Info)
- `staff`: OneToOneField(StaffProfile)
- `basic_salary`: DecimalField
- `contract_type`: CharField(choices=['permanent', 'contract', 'part_time'])
- `work_shift`: CharField
- `bank_name`: CharField
- `account_number`: CharField
- `ifsc_code`: CharField

## 3. StaffLeave (Leave Management)
- `staff`: ForeignKey(StaffProfile)
- `leave_type`: ForeignKey(LeaveType)
- `start_date`: DateField
- `end_date`: DateField
- `status`: CharField(choices=['pending', 'approved', 'rejected'])
- `reason`: TextField
- `substitute_staff`: ForeignKey(StaffProfile, null=True)

## 4. WorkDistribution
- `assigned_by`: ForeignKey(User)
- `assigned_to`: ForeignKey(StaffProfile)
- `title`: CharField
- `description`: TextField
- `due_date`: DateField
- `priority`: CharField(choices=['low', 'medium', 'high'])
- `attachment`: FileField
- `status`: CharField(choices=['pending', 'ongoing', 'completed'])

## 5. CommitteeMember
- `staff`: ForeignKey(StaffProfile, null=True)
- `external_name`: CharField(null=True) # For non-staff members
- `committee_type`: CharField(choices=['PTA', 'MMC', 'Cabinet'])
- `position`: CharField
- `term_start`: DateField
- `term_end`: DateField
- `is_active`: BooleanField
