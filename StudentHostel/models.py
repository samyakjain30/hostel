# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from Registrar.models import studentSession_1819o, studentSession_1920o, StudentDropdown, Semtiming, CourseDetail, studentSession_2021o
from Accounts.models import AccountsDropdown
from login.models import EmployeePrimdetail
from django.db import models

# Create your models here.


class HostelDropdown(models.Model):
    sno = models.AutoField(db_column='Sno', primary_key=True)  # Field name made lowercase.
    pid = models.IntegerField(db_column='Pid', blank=True, null=True)  # Field name made lowercase.
    field = models.CharField(db_column='Field', max_length=500, blank=True, null=True)  # Field name made lowercase.
    value = models.CharField(db_column='Value', max_length=500, blank=True, null=True)  # Field name made lowercase.
    is_edit = models.IntegerField(db_column='Is_Edit', default='1')  # Field name made lowercase.
    is_delete = models.IntegerField(db_column='Is_Delete', default='1')  # Field name made lowercase.
    status = models.CharField(db_column='status', null=True, max_length=10, default="INSERT")  # Formulatype, Valuebased
    session = models.ForeignKey(Semtiming, related_name='Hostel_HostelDropdownSession', db_column='session', null=True, on_delete=models.SET_NULL, default=1)

    class Meta:
        db_table = 'StuHostelDropdown'
        managed = True


class HostelSettings(models.Model):
    hostel_id = models.ForeignKey(HostelDropdown, related_name="settings_hostel", db_column="hostel_id", null=True, on_delete=models.SET_NULL)
    gender = models.ForeignKey(StudentDropdown, db_column='gender', related_name='hostel_Gender', blank=True, null=True, on_delete=models.SET_NULL)  # Field name made lowercase.
    course_id = models.ForeignKey(StudentDropdown, related_name='HostelSettingsCourse_id', db_column='Course_id', null=True, on_delete=models.SET_NULL)
    year = models.IntegerField()
    priority = models.IntegerField()  # define priority for filling hostel for particular course students i.e. 1,2,3 etc.
    session_id = models.ForeignKey(Semtiming, related_name="session1", db_column="session", null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "StuHostelSettings"
        managed = True


class HostelFlooring(models.Model):
    hostel_id = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelFlooring_hostel_id", db_column="hostel_id", blank=True, null=True, on_delete=models.SET_NULL)
    floor = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelFlooring_floor", db_column="floor", blank=True, null=True, on_delete=models.SET_NULL)
    bed_capacity = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelFlooring_bed_capacity", db_column="bed_capacity", blank=True, null=True, on_delete=models.SET_NULL)  # 2seater, 3 seater, etc.
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelFlooring_Added_by", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelFlooring"
        managed = True


class HostelSetting(models.Model):
    hostel_id = models.ForeignKey(HostelFlooring, related_name="Hostel_HostelSettings_hostel_id", db_column="hostel_id", blank=True, null=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelSettings_Course_id', db_column='branch', blank=True, null=True, on_delete=models.SET_NULL)
    year = models.IntegerField()
    admission_status = models.ForeignKey(StudentDropdown, related_name='Hostel_HostelSettings_Admission_through', db_column='admission_through', blank=True, null=True, on_delete=models.SET_NULL)
    admission_type = models.ForeignKey(StudentDropdown, related_name='Hostel_HostelSettings_Admission_type', db_column='admission_type', blank=True, null=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelSettings_Added_by", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSetting"
        managed = True


class HostelRoomSettings(models.Model):
    hostel_id = models.ForeignKey(HostelFlooring, related_name="Hostel_HostelRoomSetting_hostel_id", db_column="hostel_id", blank=True, null=True, on_delete=models.SET_NULL)
    room_no = models.CharField(max_length=100, default="N/A")  # A101, A202 etc.
    room_type = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelRoomSettings_room_type", db_column="room_type", blank=True, null=True, on_delete=models.SET_NULL)
    is_blocked = models.IntegerField()  # 0 for open, 1 for block
    is_ac = models.IntegerField(db_column='is_ac', blank=True, null=True)
    allotted_status = models.IntegerField(blank=True, null=True, default=0)  # 1 for alloted, 0 for not alloted
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelRoomSettings_Added_by", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoomSetting"
        managed = True


class HostelAssignEmp(models.Model):
    hostel_id = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelAssignEmp_hostel_id", db_column="hostel_id", blank=True, null=True, on_delete=models.SET_NULL)
    emp_id = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelAssignEmp_emp_id", null=True, blank=True, on_delete=models.SET_NULL)
    type_of_duty = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelAssignEmp_type_of_duty", db_column="type_of_duty", blank=True, null=True, on_delete=models.SET_NULL)
    added_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelAssignEmp_Added_by", null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelAssignEmp"
        managed = True


# old table ###############33
class HostelEligible(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True)
    uni_id = models.CharField(db_column='Uni_Id', max_length=45, blank=True, null=True)
    hostel_id = models.IntegerField(db_column='Hostel_Id', blank=True, null=True)
    room_alloted = models.CharField(db_column='Room_Alloted', max_length=30, blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=40, blank=True, null=True, default="INSERT")

    class Meta:
        managed = False
        db_table = 'hostel_eligible'

######################################################################
   ###################### 1819o ##########################
######################################################################


class HostelLockingUnlocking_1819o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='Hostel_HostelLockingUnlocking_1819o_session', db_column='session', blank=True, null=True, on_delete=models.SET_NULL)
    lock_type = models.CharField(default='A', max_length=5)
    att_date_from = models.DateField(default=None, null=True)
    att_date_to = models.DateField(default=None, null=True)
    unlock_from = models.DateTimeField(default=None, null=True)
    unlock_to = models.DateTimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuHostelLockingUnlocking_1819o'


class HostelLockingUnlockingStatus_1819o(models.Model):
    LockingUnlocking = models.ForeignKey(HostelLockingUnlocking_1819o, related_name='Hostel_HostelLockingUnlockingStatus_1819o_LockingUnlocking', db_column='LockingUnlocking', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819o, related_name="Hostel_HostelLockingUnlockingStatus_1819o_uniq_id", db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")

    class Meta:
        managed = True
        db_table = 'StuHostelLockingUnlockingStatus_1819o'


class HostelStudentAppliction_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name="Hostel_HostelStudentAppliction_1819o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    current_status = models.CharField(db_column='current_status', max_length=40, blank=True, null=True)  # PENDING,SEAT ALLOTED,ROOM ALLOTED,WITHDRAWL,ELIGIBLE,NOT ELIGIBLE,
    attendance_avg = models.IntegerField(db_column='attendance_avg', blank=True, null=True)
    uni_marks_obt = models.IntegerField(db_column='uni_marks_obt', blank=True, null=True)
    uni_max_marks = models.IntegerField(db_column='uni_max_marks', blank=True, null=True)
    carry = models.IntegerField(default=0, db_column='carry', blank=True, null=True)
    agree = models.IntegerField(db_column='agree', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelStudentAppliction_1819o"
        managed = True


class HostelSeaterPriority_1819o(models.Model):
    application_id = models.ForeignKey(HostelStudentAppliction_1819o, related_name="Hostel_HostelSeaterPriority_1819o_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
    seater = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelSeaterPriority_1819o_seater", db_column="seater", blank=True, null=True, on_delete=models.SET_NULL)
    priority = models.IntegerField(db_column='priority', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeaterPriority_1819o"
        managed = True


class HostelRoommatePriority_1819o(models.Model):
    application_id = models.ForeignKey(HostelStudentAppliction_1819o, related_name="Hostel_HostelRoommatePriority_1819o_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819o, related_name="Hostel_HostelRoommatePriority_1819o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    priority = models.IntegerField(db_column='priority', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoommatePriority_1819o"
        managed = True


class HostelStudentMedical_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name="Hostel_HostelStudentMedical_1819o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    medical_category = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelStudentMedical_1819o_medical_category", db_column="medical_category", blank=True, null=True, on_delete=models.SET_NULL)
    document = models.CharField(db_column='document', max_length=40, blank=True, null=True)
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelStudentMedical_1819o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='Hostel_MedicalForm_1819o_AddedBy', db_column="added_by", blank=True, null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelStudentMedical_1819o"
        managed = True


class HostelMedicalCases_1819o(models.Model):
    student_medical = models.ForeignKey(HostelStudentMedical_1819o, related_name="Hostel_HostelMedicalCases_1819o_student", db_column="student_medical", blank=True, null=True, on_delete=models.SET_NULL)
    cases = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelMedicalCases_medical_1819o_category", db_column="cases", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelMedicalCases_1819o"
        managed = True


class HostelMedicalApproval_1819o(models.Model):
    student_medical = models.ForeignKey(HostelStudentMedical_1819o, related_name="Hostel_HostelMedicalApproval_1819o_student", db_column="student_medical", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelMedicalApproval_1819o_approved_by", db_column="approved_by", null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(db_column='level', blank=True, null=True)
    approval_status = models.CharField(db_column='approval_status', max_length=40, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelMedicalApproval_1819o"
        managed = True


class HostelSeatAllotSetting_1819o(models.Model):
    hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_1819o_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
    seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_1819o_seat_part', db_column='seat_part', null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelSeatAllotSetting_1819o_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(default=1, blank=True, null=True)
    sub_priority = models.IntegerField(default=-1, blank=True, null=True)
    star_priority = models.IntegerField(default=-1, blank=True, null=True)
    indiscipline = models.IntegerField(default=1, blank=True, null=True)
    att_min = models.IntegerField(default=0, blank=True, null=True)
    att_max = models.IntegerField(default=100, blank=True, null=True)
    uni_min = models.IntegerField(default=0, blank=True, null=True)
    uni_max = models.IntegerField(default=100, blank=True, null=True)
    carry_min = models.IntegerField(default=0, blank=True, null=True)
    carry_max = models.IntegerField(default=100, blank=True, null=True)
    room_min = models.IntegerField(blank=True, null=True)
    room_max = models.IntegerField(blank=True, null=True)
    list_no = models.IntegerField(blank=True, null=True)  # On generate list
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelSeatAllotSetting_1819o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeatAllotSetting_1819o"
        managed = True


class HostelSeatAllotMulti_1819o(models.Model):
    seat_setting = models.ForeignKey(HostelSeatAllotSetting_1819o, related_name='Hostel_HostelSeatAllotMulti_1819o_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
    criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
    criteria_value = models.IntegerField(default=-1, blank=True, null=True)

    class Meta:
        db_table = "StuHostelSeatAllotMulti_1819o"
        managed = True


class HostelSeatAlloted_1819o(models.Model):
    rule_used = models.ForeignKey(HostelSeatAllotSetting_1819o, related_name='Hostel_HostelSeatAlloted_1819o_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='Hostel_HostelSeatAlloted_1819o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_1819o_hostel_part', db_column='hostel_part', null=True, on_delete=models.SET_NULL)
    seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_1819o_seat_part', db_column='seat_part', null=True, on_delete=models.SET_NULL)
    paid_status = models.CharField(db_column='paid_status', max_length=40, blank=True, null=True, default="NOT PAID")
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeatAlloted_1819o"
        managed = True
    # status=INSERT,WITHDRAWAL,DELETE
    # paid_status=PAID,NOT PAID


class HostelRoomAllotSetting_1819o(models.Model):
    hostel_part = models.ForeignKey(HostelFlooring, related_name='Hostel_HostelRoomAllotSetting_1819o_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelRoomAllotSetting_1819o_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(default=1, blank=True, null=True)
    sub_priority = models.IntegerField(default=-1, blank=True, null=True)
    course_preference = models.IntegerField(default=-1, blank=True, null=True)
    indiscipline = models.IntegerField(default=1, blank=True, null=True)
    medical = models.IntegerField(default=1, blank=True, null=True)
    phy_disabled = models.IntegerField(default=1, blank=True, null=True)
    att_min = models.IntegerField(default=0, blank=True, null=True)
    att_max = models.IntegerField(default=100, blank=True, null=True)
    uni_min = models.IntegerField(default=0, blank=True, null=True)
    uni_max = models.IntegerField(default=100, blank=True, null=True)
    carry_min = models.IntegerField(default=0, blank=True, null=True)
    carry_max = models.IntegerField(default=100, blank=True, null=True)
    room_min = models.IntegerField(default=1, blank=True, null=True)
    room_max = models.IntegerField(default=1000000, blank=True, null=True)
    list_no = models.IntegerField(blank=True, null=True)
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelRoomAllotSetting_1819o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoomAllotSetting_1819o"
        managed = True


class HostelRoomAllotMulti_1819o(models.Model):
    seat_setting = models.ForeignKey(HostelRoomAllotSetting_1819o, related_name='Hostel_HostelRoomAllotMulti_1819o_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
    criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
    criteria_value = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = "StuHostelRoomAllotMulti_1819o"
        managed = True


class HostelRoomAlloted_1819o(models.Model):
    rule_used = models.ForeignKey(HostelRoomAllotSetting_1819o, related_name='Hostel_HostelRoomAlloted_1819o_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='Hostel_HostelRoomAlloted_1819o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    room_part = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelRoomAlloted_1819o_hostel_part', db_column='room_part', null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    date_of_inserted = models.DateTimeField(db_column='date_of_inserted', auto_now_add=True)  # date the document inserted
    date_of_update = models.DateTimeField(db_column='date_of_update', auto_now=True)  # last date the document inserted
    version = models.IntegerField(default=1, blank=True, null=True)  # it will increase on every update

    class Meta:
        db_table = "StuHostelRoomAlloted_1819o"
        managed = True
    # status=INSERT,WITHDRAWAL,DELETE


class SwappingReport_1819o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1819o, related_name='Hostel_HostelSwappingReport_1819o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    previous_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_1819o_previous_room', db_column='previous_room', null=True, on_delete=models.SET_NULL)
    current_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_1819o_current_room', db_column='current_room', null=True, on_delete=models.SET_NULL)
    type = models.CharField(db_column='type', max_length=40, blank=True, null=True)  # STUDENT SWAP,ROOM SWAP
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSwappingReport_1819o"
        managed = True


######################################################################
   ###################### 1920o ##########################
######################################################################


class HostelLockingUnlocking_1920o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='Hostel_HostelLockingUnlocking_1920o_session', db_column='session', blank=True, null=True, on_delete=models.SET_NULL)
    lock_type = models.CharField(default='A', max_length=5)
    att_date_from = models.DateField(default=None, null=True)
    att_date_to = models.DateField(default=None, null=True)
    unlock_from = models.DateTimeField(default=None, null=True)
    unlock_to = models.DateTimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuHostelLockingUnlocking_1920o'


class HostelLockingUnlockingStatus_1920o(models.Model):
    LockingUnlocking = models.ForeignKey(HostelLockingUnlocking_1920o, related_name='Hostel_HostelLockingUnlockingStatus_1920o_LockingUnlocking', db_column='LockingUnlocking', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="Hostel_HostelLockingUnlockingStatus_1920o_uniq_id", db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")

    class Meta:
        managed = True
        db_table = 'StuHostelLockingUnlockingStatus_1920o'


class HostelStudentAppliction_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="Hostel_HostelStudentAppliction_1920o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    current_status = models.CharField(db_column='current_status', max_length=40, blank=True, null=True)  # PENDING,SEAT ALLOTED,ROOM ALLOTED,WITHDRAWL,
    attendance_avg = models.IntegerField(db_column='attendance_avg', blank=True, null=True)
    uni_marks_obt = models.IntegerField(db_column='uni_marks_obt', blank=True, null=True)
    uni_max_marks = models.IntegerField(db_column='uni_max_marks', blank=True, null=True)
    carry = models.IntegerField(default=0, db_column='carry', blank=True, null=True)
    agree = models.IntegerField(db_column='agree', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelStudentAppliction_1920o"
        managed = True


class HostelSeaterPriority_1920o(models.Model):
    application_id = models.ForeignKey(HostelStudentAppliction_1920o, related_name="Hostel_HostelSeaterPriority_1920o_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
    seater = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelSeaterPriority_1920o_seater", db_column="seater", blank=True, null=True, on_delete=models.SET_NULL)
    priority = models.IntegerField(db_column='priority', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeaterPriority_1920o"
        managed = True


class HostelRoommatePriority_1920o(models.Model):
    application_id = models.ForeignKey(HostelStudentAppliction_1920o, related_name="Hostel_HostelRoommatePriority_1920o_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="Hostel_HostelRoommatePriority_1920o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    priority = models.IntegerField(db_column='priority', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoommatePriority_1920o"
        managed = True


class HostelStudentMedical_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name="Hostel_HostelStudentMedical_1920o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    medical_category = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelStudentMedical_1920o_medical_category", db_column="medical_category", blank=True, null=True, on_delete=models.SET_NULL)
    document = models.CharField(db_column='document', max_length=40, blank=True, null=True)
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelStudentMedical_1920o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='Hostel_MedicalForm_1920o_AddedBy', db_column="added_by", blank=True, null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelStudentMedical_1920o"
        managed = True


class HostelMedicalCases_1920o(models.Model):
    student_medical = models.ForeignKey(HostelStudentMedical_1920o, related_name="Hostel_HostelMedicalCases_1920o_student", db_column="student_medical", blank=True, null=True, on_delete=models.SET_NULL)
    cases = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelMedicalCases_medical_1920o_category", db_column="cases", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelMedicalCases_1920o"
        managed = True


class HostelMedicalApproval_1920o(models.Model):
    student_medical = models.ForeignKey(HostelStudentMedical_1920o, related_name="Hostel_HostelMedicalApproval_1920o_student", db_column="student_medical", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelMedicalApproval_1920o_approved_by", db_column="approved_by", null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(db_column='level', blank=True, null=True)
    approval_status = models.CharField(db_column='approval_status', max_length=40, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelMedicalApproval_1920o"
        managed = True


class HostelSeatAllotSetting_1920o(models.Model):
    hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_1920o_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
    seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_1920o_seat_part', db_column='seat_part', null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelSeatAllotSetting_1920o_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(default=1, blank=True, null=True)
    sub_priority = models.IntegerField(default=-1, blank=True, null=True)
    star_priority = models.IntegerField(default=-1, blank=True, null=True)
    indiscipline = models.IntegerField(default=1, blank=True, null=True)
    att_min = models.IntegerField(default=0, blank=True, null=True)
    att_max = models.IntegerField(default=100, blank=True, null=True)
    uni_min = models.IntegerField(default=0, blank=True, null=True)
    uni_max = models.IntegerField(default=100, blank=True, null=True)
    carry_min = models.IntegerField(default=0, blank=True, null=True)
    carry_max = models.IntegerField(default=100, blank=True, null=True)
    room_min = models.IntegerField(blank=True, null=True)
    room_max = models.IntegerField(blank=True, null=True)
    list_no = models.IntegerField(blank=True, null=True)  # On generate list
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelSeatAllotSetting_1920o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeatAllotSetting_1920o"
        managed = True


class HostelSeatAllotMulti_1920o(models.Model):
    seat_setting = models.ForeignKey(HostelSeatAllotSetting_1920o, related_name='Hostel_HostelSeatAllotMulti_1920o_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
    criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
    criteria_value = models.IntegerField(default=-1, blank=True, null=True)

    class Meta:
        db_table = "StuHostelSeatAllotMulti_1920o"
        managed = True


class HostelSeatAlloted_1920o(models.Model):
    rule_used = models.ForeignKey(HostelSeatAllotSetting_1920o, related_name='Hostel_HostelSeatAlloted_1920o_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='Hostel_HostelSeatAlloted_1920o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_1920o_hostel_part', db_column='hostel_part', null=True, on_delete=models.SET_NULL)
    seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_1920o_seat_part', db_column='seat_part', null=True, on_delete=models.SET_NULL)
    paid_status = models.CharField(db_column='paid_status', max_length=40, blank=True, null=True, default="NOT PAID")
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeatAlloted_1920o"
        managed = True
    # status=INSERT,DELETE
    # paid_status=PAID,NOT PAID


class HostelRoomAllotSetting_1920o(models.Model):
    hostel_part = models.ForeignKey(HostelFlooring, related_name='Hostel_HostelRoomAllotSetting_1920o_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelRoomAllotSetting_1920o_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(default=1, blank=True, null=True)
    sub_priority = models.IntegerField(default=-1, blank=True, null=True)
    course_preference = models.IntegerField(default=-1, blank=True, null=True)
    indiscipline = models.IntegerField(default=1, blank=True, null=True)
    medical = models.IntegerField(default=1, blank=True, null=True)
    phy_disabled = models.IntegerField(default=1, blank=True, null=True)
    att_min = models.IntegerField(default=0, blank=True, null=True)
    att_max = models.IntegerField(default=100, blank=True, null=True)
    uni_min = models.IntegerField(default=0, blank=True, null=True)
    uni_max = models.IntegerField(default=100, blank=True, null=True)
    carry_min = models.IntegerField(default=0, blank=True, null=True)
    carry_max = models.IntegerField(default=100, blank=True, null=True)
    room_min = models.IntegerField(default=1, blank=True, null=True)
    room_max = models.IntegerField(default=1000000, blank=True, null=True)
    list_no = models.IntegerField(blank=True, null=True)
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelRoomAllotSetting_1920o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoomAllotSetting_1920o"
        managed = True


class HostelRoomAllotMulti_1920o(models.Model):
    seat_setting = models.ForeignKey(HostelRoomAllotSetting_1920o, related_name='Hostel_HostelRoomAllotMulti_1920o_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
    criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
    criteria_value = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = "StuHostelRoomAllotMulti_1920o"
        managed = True


class HostelRoomAlloted_1920o(models.Model):
    rule_used = models.ForeignKey(HostelRoomAllotSetting_1920o, related_name='Hostel_HostelRoomAlloted_1920o_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='Hostel_HostelRoomAlloted_1920o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    room_part = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelRoomAlloted_1920o_hostel_part', db_column='room_part', null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    date_of_inserted = models.DateTimeField(db_column='date_of_inserted', auto_now_add=True)  # date the document inserted
    date_of_update = models.DateTimeField(db_column='date_of_update', auto_now=True)  # last date the document inserted
    version = models.IntegerField(default=1, blank=True, null=True)  # it will increase on every update

    class Meta:
        db_table = "StuHostelRoomAlloted_1920o"
        managed = True
    # status=INSERT,WITHDRAWAL,DELETE


class SwappingReport_1920o(models.Model):
    uniq_id = models.ForeignKey(studentSession_1920o, related_name='Hostel_HostelSwappingReport_1920o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    previous_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_1920o_previous_room', db_column='previous_room', null=True, on_delete=models.SET_NULL)
    current_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_1920o_current_room', db_column='current_room', null=True, on_delete=models.SET_NULL)
    type = models.CharField(db_column='type', max_length=40, blank=True, null=True)  # STUDENT SWAP,ROOM SWAP
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSwappingReport_1920o"
        managed = True

######################################################################################################################################################
########################################################## 1920e #####################################################################################
######################################################################################################################################################


# class HostelLockingUnlocking_1920e(models.Model):
#     session = models.ForeignKey(Semtiming, related_name='Hostel_HostelLockingUnlocking_1920e_session', db_column='session', blank=True, null=True, on_delete=models.SET_NULL)
#     lock_type = models.CharField(default='A', max_length=5)
#     att_date_from = models.DateField(default=None, null=True)
#     att_date_to = models.DateField(default=None, null=True)
#     unlock_from = models.DateTimeField(default=None, null=True)
#     unlock_to = models.DateTimeField(default=None, null=True)
#     time_stamp = models.DateTimeField(auto_now=True)

#     class Meta:
#         managed = True
#         db_table = 'StuHostelLockingUnlocking_1920e'


# class HostelLockingUnlockingStatus_1920e(models.Model):
#     LockingUnlocking = models.ForeignKey(HostelLockingUnlocking_1920e, related_name='Hostel_HostelLockingUnlockingStatus_1920e_LockingUnlocking', db_column='LockingUnlocking', blank=True, null=True, on_delete=models.SET_NULL)
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name="Hostel_HostelLockingUnlockingStatus_1920e_uniq_id", db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")

#     class Meta:
#         managed = True
#         db_table = 'StuHostelLockingUnlockingStatus_1920e'


# class HostelStudentAppliction_1920e(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name="Hostel_HostelStudentAppliction_1920e_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     current_status = models.CharField(db_column='current_status', max_length=40, blank=True, null=True)  # PENDING,SEAT ALLOTED,ROOM ALLOTED,WITHDRAWL,
#     attendance_avg = models.IntegerField(db_column='attendance_avg', blank=True, null=True)
#     uni_marks_obt = models.IntegerField(db_column='uni_marks_obt', blank=True, null=True)
#     uni_max_marks = models.IntegerField(db_column='uni_max_marks', blank=True, null=True)
#     carry = models.IntegerField(default=0, db_column='carry', blank=True, null=True)
#     agree = models.IntegerField(db_column='agree', blank=True, null=True)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelStudentAppliction_1920e"
#         managed = True


# class HostelSeaterPriority_1920e(models.Model):
#     application_id = models.ForeignKey(HostelStudentAppliction_1920e, related_name="Hostel_HostelSeaterPriority_1920e_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
#     seater = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelSeaterPriority_1920e_seater", db_column="seater", blank=True, null=True, on_delete=models.SET_NULL)
#     priority = models.IntegerField(db_column='priority', blank=True, null=True)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelSeaterPriority_1920e"
#         managed = True


# class HostelRoommatePriority_1920e(models.Model):
#     application_id = models.ForeignKey(HostelStudentAppliction_1920e, related_name="Hostel_HostelRoommatePriority_1920e_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name="Hostel_HostelRoommatePriority_1920e_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     priority = models.IntegerField(db_column='priority', blank=True, null=True)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelRoommatePriority_1920e"
#         managed = True


# class HostelStudentMedical_1920e(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name="Hostel_HostelStudentMedical_1920e_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
#     medical_category = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelStudentMedical_1920e_medical_category", db_column="medical_category", blank=True, null=True, on_delete=models.SET_NULL)
#     document = models.CharField(db_column='document', max_length=40, blank=True, null=True)
#     session = models.ForeignKey(Semtiming, related_name="Hostel_HostelStudentMedical_1920e_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     added_by = models.ForeignKey(EmployeePrimdetail, related_name='Hostel_MedicalForm_1920e_AddedBy', db_column="added_by", blank=True, null=True, on_delete=models.SET_NULL)
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelStudentMedical_1920e"
#         managed = True


# class HostelMedicalCases_1920e(models.Model):
#     student_medical = models.ForeignKey(HostelStudentMedical_1920e, related_name="Hostel_HostelMedicalCases_1920e_student", db_column="student_medical", blank=True, null=True, on_delete=models.SET_NULL)
#     cases = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelMedicalCases_medical_1920e_category", db_column="cases", blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelMedicalCases_1920e"
#         managed = True


# class HostelMedicalApproval_1920e(models.Model):
#     student_medical = models.ForeignKey(HostelStudentMedical_1920e, related_name="Hostel_HostelMedicalApproval_1920e_student", db_column="student_medical", null=True, on_delete=models.SET_NULL)
#     approved_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelMedicalApproval_1920e_approved_by", db_column="approved_by", null=True, on_delete=models.SET_NULL)
#     level = models.IntegerField(db_column='level', blank=True, null=True)
#     approval_status = models.CharField(db_column='approval_status', max_length=40, blank=True, null=True)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelMedicalApproval_1920e"
#         managed = True


# class HostelSeatAllotSetting_1920e(models.Model):
#     hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_1920e_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
#     seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_1920e_seat_part', db_column='seat_part', null=True, blank=True, on_delete=models.SET_NULL)
#     branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelSeatAllotSetting_1920e_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
#     year = models.IntegerField(blank=True, null=True)
#     priority = models.IntegerField(default=1, blank=True, null=True)
#     sub_priority = models.IntegerField(default=-1, blank=True, null=True)
#     star_priority = models.IntegerField(default=-1, blank=True, null=True)
#     indiscipline = models.IntegerField(default=1, blank=True, null=True)
#     att_min = models.IntegerField(default=0, blank=True, null=True)
#     att_max = models.IntegerField(default=100, blank=True, null=True)
#     uni_min = models.IntegerField(default=0, blank=True, null=True)
#     uni_max = models.IntegerField(default=100, blank=True, null=True)
#     carry_min = models.IntegerField(default=0, blank=True, null=True)
#     carry_max = models.IntegerField(default=100, blank=True, null=True)
#     room_min = models.IntegerField(blank=True, null=True)
#     room_max = models.IntegerField(blank=True, null=True)
#     list_no = models.IntegerField(blank=True, null=True)  # On generate list
#     session = models.ForeignKey(Semtiming, related_name="Hostel_HostelSeatAllotSetting_1920e_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelSeatAllotSetting_1920e"
#         managed = True


# class HostelSeatAllotMulti_1920e(models.Model):
#     seat_setting = models.ForeignKey(HostelSeatAllotSetting_1920e, related_name='Hostel_HostelSeatAllotMulti_1920e_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
#     criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
#     criteria_value = models.IntegerField(default=-1, blank=True, null=True)

#     class Meta:
#         db_table = "StuHostelSeatAllotMulti_1920e"
#         managed = True


# class HostelSeatAlloted_1920e(models.Model):
#     rule_used = models.ForeignKey(HostelSeatAllotSetting_1920e, related_name='Hostel_HostelSeatAlloted_1920e_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name='Hostel_HostelSeatAlloted_1920e_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
#     hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_1920e_hostel_part', db_column='hostel_part', null=True, on_delete=models.SET_NULL)
#     seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_1920e_seat_part', db_column='seat_part', null=True, on_delete=models.SET_NULL)
#     paid_status = models.CharField(db_column='paid_status', max_length=40, blank=True, null=True, default="NOT PAID")
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelSeatAlloted_1920e"
#         managed = True
#     # status=INSERT,DELETE
#     # paid_status=ALREADY PAID,NOT PAID


# class HostelRoomAllotSetting_1920e(models.Model):
#     hostel_part = models.ForeignKey(HostelFlooring, related_name='Hostel_HostelRoomAllotSetting_1920e_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
#     branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelRoomAllotSetting_1920e_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
#     year = models.IntegerField(blank=True, null=True)
#     priority = models.IntegerField(default=1, blank=True, null=True)
#     sub_priority = models.IntegerField(default=-1, blank=True, null=True)
#     course_preference = models.IntegerField(default=-1, blank=True, null=True)
#     indiscipline = models.IntegerField(default=1, blank=True, null=True)
#     medical = models.IntegerField(default=1, blank=True, null=True)
#     phy_disabled = models.IntegerField(default=1, blank=True, null=True)
#     att_min = models.IntegerField(default=0, blank=True, null=True)
#     att_max = models.IntegerField(default=100, blank=True, null=True)
#     uni_min = models.IntegerField(default=0, blank=True, null=True)
#     uni_max = models.IntegerField(default=100, blank=True, null=True)
#     carry_min = models.IntegerField(default=0, blank=True, null=True)
#     carry_max = models.IntegerField(default=100, blank=True, null=True)
#     room_min = models.IntegerField(default=1, blank=True, null=True)
#     room_max = models.IntegerField(default=1000000, blank=True, null=True)
#     list_no = models.IntegerField(blank=True, null=True)
#     session = models.ForeignKey(Semtiming, related_name="Hostel_HostelRoomAllotSetting_1920e_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelRoomAllotSetting_1920e"
#         managed = True


# class HostelRoomAllotMulti_1920e(models.Model):
#     seat_setting = models.ForeignKey(HostelRoomAllotSetting_1920e, related_name='Hostel_HostelRoomAllotMulti_1920e_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
#     criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
#     criteria_value = models.IntegerField(default=1, blank=True, null=True)

#     class Meta:
#         db_table = "StuHostelRoomAllotMulti_1920e"
#         managed = True


# class HostelRoomAlloted_1920e(models.Model):
#     rule_used = models.ForeignKey(HostelRoomAllotSetting_1920e, related_name='Hostel_HostelRoomAlloted_1920e_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name='Hostel_HostelRoomAlloted_1920e_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
#     room_part = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelRoomAlloted_1920e_hostel_part', db_column='room_part', null=True, on_delete=models.SET_NULL)
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
#     date_of_inserted = models.DateTimeField(db_column='date_of_inserted', auto_now_add=True)  # date the document inserted
#     date_of_update = models.DateTimeField(db_column='date_of_update', auto_now=True)  # last date the document inserted
#     version = models.IntegerField(default=1, blank=True, null=True)  # it will increase on every update

#     class Meta:
#         db_table = "StuHostelRoomAlloted_1920e"
#         managed = True
#     # status=INSERT,WITHDRAWAL,DELETE


# class SwappingReport_1920e(models.Model):
#     uniq_id = models.ForeignKey(studentSession_1920e, related_name='Hostel_HostelSwappingReport_1920e_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
#     previous_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_1920e_previous_room', db_column='previous_room', null=True, on_delete=models.SET_NULL)
#     current_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_1920e_current_room', db_column='current_room', null=True, on_delete=models.SET_NULL)
#     type = models.CharField(db_column='type', max_length=40, blank=True, null=True)  # STUDENT SWAP,ROOM SWAP
#     status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
#     time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

#     class Meta:
#         db_table = "StuHostelSwappingReport_1920e"
#         managed = True


####################################################################### 2021o #######################################################################
class HostelLockingUnlocking_2021o(models.Model):
    session = models.ForeignKey(Semtiming, related_name='Hostel_HostelLockingUnlocking_2021o_session', db_column='session', blank=True, null=True, on_delete=models.SET_NULL)
    lock_type = models.CharField(default='A', max_length=5)
    att_date_from = models.DateField(default=None, null=True)
    att_date_to = models.DateField(default=None, null=True)
    unlock_from = models.DateTimeField(default=None, null=True)
    unlock_to = models.DateTimeField(default=None, null=True)
    time_stamp = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'StuHostelLockingUnlocking_2021o'


class HostelLockingUnlockingStatus_2021o(models.Model):
    LockingUnlocking = models.ForeignKey(HostelLockingUnlocking_2021o, related_name='Hostel_HostelLockingUnlockingStatus_2021o_LockingUnlocking', db_column='LockingUnlocking', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="Hostel_HostelLockingUnlockingStatus_2021o_uniq_id", db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")

    class Meta:
        managed = True
        db_table = 'StuHostelLockingUnlockingStatus_2021o'


class HostelStudentAppliction_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="Hostel_HostelStudentAppliction_2021o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    current_status = models.CharField(db_column='current_status', max_length=40, blank=True, null=True)  # PENDING,SEAT ALLOTED,ROOM ALLOTED,WITHDRAWL,
    attendance_avg = models.IntegerField(db_column='attendance_avg', blank=True, null=True)
    uni_marks_obt = models.IntegerField(db_column='uni_marks_obt', blank=True, null=True)
    uni_max_marks = models.IntegerField(db_column='uni_max_marks', blank=True, null=True)
    carry = models.IntegerField(default=0, db_column='carry', blank=True, null=True)
    agree = models.IntegerField(db_column='agree', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelStudentAppliction_2021o"
        managed = True


class HostelSeaterPriority_2021o(models.Model):
    application_id = models.ForeignKey(HostelStudentAppliction_2021o, related_name="Hostel_HostelSeaterPriority_2021o_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
    seater = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelSeaterPriority_2021o_seater", db_column="seater", blank=True, null=True, on_delete=models.SET_NULL)
    priority = models.IntegerField(db_column='priority', blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeaterPriority_2021o"
        managed = True


class HostelRoommatePriority_2021o(models.Model):
    application_id = models.ForeignKey(HostelStudentAppliction_2021o, related_name="Hostel_HostelRoommatePriority_2021o_application_id", db_column="application_id", blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="Hostel_HostelRoommatePriority_2021o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    priority = models.IntegerField(db_column='priority', blank=True, null=True)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoommatePriority_2021o"
        managed = True


class HostelStudentMedical_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name="Hostel_HostelStudentMedical_2021o_uniq_id", db_column="uniq_id", blank=True, null=True, on_delete=models.SET_NULL)
    medical_category = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelStudentMedical_2021o_medical_category", db_column="medical_category", blank=True, null=True, on_delete=models.SET_NULL)
    document = models.CharField(db_column='document', max_length=40, blank=True, null=True)
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelStudentMedical_2021o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    added_by = models.ForeignKey(EmployeePrimdetail, related_name='Hostel_MedicalForm_2021o_AddedBy', db_column="added_by", blank=True, null=True, on_delete=models.SET_NULL)
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelStudentMedical_2021o"
        managed = True


class HostelMedicalCases_2021o(models.Model):
    student_medical = models.ForeignKey(HostelStudentMedical_2021o, related_name="Hostel_HostelMedicalCases_2021o_student", db_column="student_medical", blank=True, null=True, on_delete=models.SET_NULL)
    cases = models.ForeignKey(HostelDropdown, related_name="Hostel_HostelMedicalCases_medical_2021o_category", db_column="cases", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelMedicalCases_2021o"
        managed = True


class HostelMedicalApproval_2021o(models.Model):
    student_medical = models.ForeignKey(HostelStudentMedical_2021o, related_name="Hostel_HostelMedicalApproval_2021o_student", db_column="student_medical", null=True, on_delete=models.SET_NULL)
    approved_by = models.ForeignKey(EmployeePrimdetail, related_name="Hostel_HostelMedicalApproval_2021o_approved_by", db_column="approved_by", null=True, on_delete=models.SET_NULL)
    level = models.IntegerField(db_column='level', blank=True, null=True)
    approval_status = models.CharField(db_column='approval_status', max_length=40, blank=True, null=True)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelMedicalApproval_2021o"
        managed = True


class HostelSeatAllotSetting_2021o(models.Model):
    hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_2021o_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
    seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAllotSetting_2021o_seat_part', db_column='seat_part', null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelSeatAllotSetting_2021o_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(default=1, blank=True, null=True)
    sub_priority = models.IntegerField(default=-1, blank=True, null=True)
    star_priority = models.IntegerField(default=-1, blank=True, null=True)
    indiscipline = models.IntegerField(default=1, blank=True, null=True)
    att_min = models.IntegerField(default=0, blank=True, null=True)
    att_max = models.IntegerField(default=100, blank=True, null=True)
    uni_min = models.IntegerField(default=0, blank=True, null=True)
    uni_max = models.IntegerField(default=100, blank=True, null=True)
    carry_min = models.IntegerField(default=0, blank=True, null=True)
    carry_max = models.IntegerField(default=100, blank=True, null=True)
    room_min = models.IntegerField(blank=True, null=True)
    room_max = models.IntegerField(blank=True, null=True)
    list_no = models.IntegerField(blank=True, null=True)  # On generate list
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelSeatAllotSetting_2021o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeatAllotSetting_2021o"
        managed = True


class HostelSeatAllotMulti_2021o(models.Model):
    seat_setting = models.ForeignKey(HostelSeatAllotSetting_2021o, related_name='Hostel_HostelSeatAllotMulti_2021o_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
    criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
    criteria_value = models.IntegerField(default=-1, blank=True, null=True)

    class Meta:
        db_table = "StuHostelSeatAllotMulti_2021o"
        managed = True


class HostelSeatAlloted_2021o(models.Model):
    rule_used = models.ForeignKey(HostelSeatAllotSetting_2021o, related_name='Hostel_HostelSeatAlloted_2021o_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='Hostel_HostelSeatAlloted_2021o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    hostel_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_2021o_hostel_part', db_column='hostel_part', null=True, on_delete=models.SET_NULL)
    seat_part = models.ForeignKey(HostelDropdown, related_name='Hostel_HostelSeatAlloted_2021o_seat_part', db_column='seat_part', null=True, on_delete=models.SET_NULL)
    paid_status = models.CharField(db_column='paid_status', max_length=40, blank=True, null=True, default="NOT PAID")
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSeatAlloted_2021o"
        managed = True
    # status=INSERT,DELETE
    # paid_status=PAID,NOT PAID


class HostelRoomAllotSetting_2021o(models.Model):
    hostel_part = models.ForeignKey(HostelFlooring, related_name='Hostel_HostelRoomAllotSetting_2021o_hostel_part', db_column='hostel_part', null=True, blank=True, on_delete=models.SET_NULL)
    branch = models.ForeignKey(CourseDetail, related_name='Hostel_HostelRoomAllotSetting_2021o_branch', db_column='branch', null=True, blank=True, on_delete=models.SET_NULL)
    year = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(default=1, blank=True, null=True)
    sub_priority = models.IntegerField(default=-1, blank=True, null=True)
    course_preference = models.IntegerField(default=-1, blank=True, null=True)
    indiscipline = models.IntegerField(default=1, blank=True, null=True)
    medical = models.IntegerField(default=1, blank=True, null=True)
    phy_disabled = models.IntegerField(default=1, blank=True, null=True)
    att_min = models.IntegerField(default=0, blank=True, null=True)
    att_max = models.IntegerField(default=100, blank=True, null=True)
    uni_min = models.IntegerField(default=0, blank=True, null=True)
    uni_max = models.IntegerField(default=100, blank=True, null=True)
    carry_min = models.IntegerField(default=0, blank=True, null=True)
    carry_max = models.IntegerField(default=100, blank=True, null=True)
    room_min = models.IntegerField(default=1, blank=True, null=True)
    room_max = models.IntegerField(default=1000000, blank=True, null=True)
    list_no = models.IntegerField(blank=True, null=True)
    session = models.ForeignKey(Semtiming, related_name="Hostel_HostelRoomAllotSetting_2021o_session", db_column="session", blank=True, null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelRoomAllotSetting_2021o"
        managed = True


class HostelRoomAllotMulti_2021o(models.Model):
    seat_setting = models.ForeignKey(HostelRoomAllotSetting_2021o, related_name='Hostel_HostelRoomAllotMulti_2021o_seat_setting', db_column='seat_setting', blank=True, null=True, on_delete=models.SET_NULL)
    criteria_type = models.CharField(max_length=20, default="A")  # MEDICAL/ etc
    criteria_value = models.IntegerField(default=1, blank=True, null=True)

    class Meta:
        db_table = "StuHostelRoomAllotMulti_2021o"
        managed = True


class HostelRoomAlloted_2021o(models.Model):
    rule_used = models.ForeignKey(HostelRoomAllotSetting_2021o, related_name='Hostel_HostelRoomAlloted_2021o_rule_used', db_column='rule_used', blank=True, null=True, on_delete=models.SET_NULL)
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='Hostel_HostelRoomAlloted_2021o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    room_part = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelRoomAlloted_2021o_hostel_part', db_column='room_part', null=True, on_delete=models.SET_NULL)
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")
    date_of_inserted = models.DateTimeField(db_column='date_of_inserted', auto_now_add=True)  # date the document inserted
    date_of_update = models.DateTimeField(db_column='date_of_update', auto_now=True)  # last date the document inserted
    version = models.IntegerField(default=1, blank=True, null=True)  # it will increase on every update

    class Meta:
        db_table = "StuHostelRoomAlloted_2021o"
        managed = True
    # status=INSERT,WITHDRAWAL,DELETE


class SwappingReport_2021o(models.Model):
    uniq_id = models.ForeignKey(studentSession_2021o, related_name='Hostel_HostelSwappingReport_2021o_uniq_id', db_column='uniq_id', blank=True, null=True, on_delete=models.SET_NULL)
    previous_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_2021o_previous_room', db_column='previous_room', null=True, on_delete=models.SET_NULL)
    current_room = models.ForeignKey(HostelRoomSettings, related_name='Hostel_HostelSwappingReport_2021o_current_room', db_column='current_room', null=True, on_delete=models.SET_NULL)
    type = models.CharField(db_column='type', max_length=40, blank=True, null=True)  # STUDENT SWAP,ROOM SWAP
    status = models.CharField(db_column='status', max_length=40, blank=True, null=True, default="INSERT")  # Field name made lowercase.
    time_stamp = models.DateTimeField(db_column='time_stamp', auto_now=True)

    class Meta:
        db_table = "StuHostelSwappingReport_2021o"
        managed = True
#####################################################################################################################################################