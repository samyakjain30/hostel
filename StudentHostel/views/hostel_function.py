# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from datetime import datetime, date
import json
from itertools import groupby
from django.db.models import Sum, F
import operator
import collections

from StudentHostel.constants_variables import lock_type

from StudentHostel.models import *
from Registrar.models import *
from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeeDropdown, EmployeePrimdetail

from StudentHostel.views.hostel_order import *
from login.views import checkpermission, generate_session_table_name
from StudentSMM.views.smm_function_views import check_residential_status
# Create your views here.

######################################################################################################################
############################## HOSTEL DROPDOWN FUNCTION ##############################################################


def get_dropdown(field, extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field__in=field, session=session).exclude(value__isnull=True).filter(**extra_filter).values('field', 'value', 'sno'))
    return qry


def get_hostel(category, extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field=category, session=session).exclude(value__isnull=True).exclude(status='DELETE').filter(**extra_filter).values('sno', 'field', 'value'))
    return qry


def get_rector_hostel(emp_id, extra_filter, session):
    data = []
    qry = list(HostelAssignEmp.objects.filter(emp_id=emp_id, type_of_duty__value='REC', type_of_duty__session=session).exclude(status="DELETE").filter(**extra_filter).values('hostel_id__sno', 'hostel_id__value', 'hostel_id__field'))
    for q in qry:
        data.append({'sno': q['hostel_id__sno'], 'field': q['hostel_id__field'], 'value': q['hostel_id__value']})
    return data


def check_empty_room(bed_capacity, hostel_id, session, session_name):
    total_seat_capacity_data = get_hostel_capacity(hostel_id, session_name, session)
    seat_capacity_occupied_data = get_hostel_occupied_capacity(hostel_id, session_name, session)
    bed_capacity = str(bed_capacity)

    if bed_capacity in total_seat_capacity_data:
        if bed_capacity in seat_capacity_occupied_data:
            if (total_seat_capacity_data[bed_capacity] - seat_capacity_occupied_data[bed_capacity]) > 0:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def check_empty_room_for_capacity(bed_capacity, hostel_id, session, session_name):
    total_room = HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__bed_capacity__value=bed_capacity, room_type__value="STUDENT ROOM", is_blocked=0).exclude(status="DELETE").count()
    total_occupied_room = HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__bed_capacity=bed_capacity, hostel_id__hostel_id__session=session, room_type__value="STUDENT ROOM", is_blocked=0, allotted_status=bed_capacity).exclude(status="DELETE").count()
    if total_room > total_occupied_room:
        return True
    else:
        return False


############################################ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################
#### CHANGE BY VRINDA ####
def get_hostel_capacity_for_report(hostel_id, session_name, session):
    total_seat_capacity_data = {}
    flooring_data = HostelFlooring.objects.filter(hostel_id=hostel_id).exclude(status="DELETE").values_list('id', flat=True)
    room_data = list(HostelRoomSettings.objects.filter(hostel_id__in=flooring_data, room_type__value="STUDENT ROOM").exclude(status="DELETE").values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value'))
    for room in room_data:
        if room['hostel_id__bed_capacity__value'] in total_seat_capacity_data:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = total_seat_capacity_data[room['hostel_id__bed_capacity__value']] + int(room['hostel_id__bed_capacity__value'])
        else:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = int(room['hostel_id__bed_capacity__value'])
    return total_seat_capacity_data
##########################


def get_hostel_capacity(hostel_id, session_name, session):
    total_seat_capacity_data = {}
    flooring_data = HostelFlooring.objects.filter(hostel_id=hostel_id).exclude(status="DELETE").values_list('id', flat=True)
    room_data = list(HostelRoomSettings.objects.filter(hostel_id__in=flooring_data, room_type__value="STUDENT ROOM", is_blocked=0).exclude(status="DELETE").values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value'))
    for room in room_data:
        if room['hostel_id__bed_capacity__value'] in total_seat_capacity_data:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = total_seat_capacity_data[room['hostel_id__bed_capacity__value']] + int(room['hostel_id__bed_capacity__value'])
        else:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = int(room['hostel_id__bed_capacity__value'])
    return total_seat_capacity_data


def get_hostel_capacity_blocked_student_room(hostel_id, session_name, session):
    total_seat_capacity_data = {}
    flooring_data = HostelFlooring.objects.filter(hostel_id=hostel_id).exclude(status="DELETE").values_list('id', flat=True)
    room_data = list(HostelRoomSettings.objects.filter(hostel_id__in=flooring_data, room_type__value="STUDENT ROOM", is_blocked=1).exclude(status="DELETE").values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value'))
    for room in room_data:
        if room['hostel_id__bed_capacity__value'] in total_seat_capacity_data:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = total_seat_capacity_data[room['hostel_id__bed_capacity__value']] + int(room['hostel_id__bed_capacity__value'])
        else:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = int(room['hostel_id__bed_capacity__value'])
    return total_seat_capacity_data


def get_hostel_capacity_blocked_and_unblocked_student_room(hostel_id, session_name, session):
    total_seat_capacity_data = {}
    flooring_data = HostelFlooring.objects.filter(hostel_id=hostel_id).exclude(status="DELETE").values_list('id', flat=True)
    room_data = list(HostelRoomSettings.objects.filter(hostel_id__in=flooring_data, room_type__value="STUDENT ROOM").exclude(status="DELETE").values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value'))
    for room in room_data:
        if room['hostel_id__bed_capacity__value'] in total_seat_capacity_data:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = total_seat_capacity_data[room['hostel_id__bed_capacity__value']] + int(room['hostel_id__bed_capacity__value'])
        else:
            total_seat_capacity_data[room['hostel_id__bed_capacity__value']] = int(room['hostel_id__bed_capacity__value'])
    return total_seat_capacity_data

########################### END ############ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################

############################################ GET OCCUPIED CAPACITY OF HOSTEL FOR STUDENT #################################################################


def get_hostel_occupied_capacity(hostel_id, session_name, session):
    total_seat_capacity_data = {}
    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
    seat_alloted_data = list(HostelSeatAlloted.objects.filter(hostel_part=hostel_id).exclude(status="DELETE").exclude(seat_part__isnull=True).values('seat_part__value'))
    for room in seat_alloted_data:
        if room['seat_part__value'] in total_seat_capacity_data:
            total_seat_capacity_data[room['seat_part__value']] = total_seat_capacity_data[room['seat_part__value']] + 1
        else:
            total_seat_capacity_data[room['seat_part__value']] = 1
    return total_seat_capacity_data
########################### END ############ GET OCCUPIED CAPACITY OF HOSTEL FOR STUDENT #################################################################

############################################ GET UN-OCCUPIED CAPACITY OF HOSTEL FOR STUDENT #################################################################


def get_hostel_occupied_un_capacity(hostel_id, session_name, session):
    seat_capacity_un_occupied_data = get_hostel_capacity(hostel_id, session_name, session)
    seat_capacity_occupied_data = get_hostel_occupied_capacity(hostel_id, session_name, session)
    for bed_capacity in seat_capacity_un_occupied_data:
        if bed_capacity in seat_capacity_occupied_data:
            seat_capacity_un_occupied_data[bed_capacity] = seat_capacity_un_occupied_data[bed_capacity] - seat_capacity_occupied_data[bed_capacity]
        else:
            pass
    return seat_capacity_un_occupied_data
########################### END ############ GET UN-OCCUPIED CAPACITY OF HOSTEL FOR STUDENT #################################################################


def get_seater_type(extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field='BED CAPACITY', session=session).exclude(value__isnull=True).exclude(status='DELETE').filter(**extra_filter).values('field', 'value', 'sno'))
    return qry


def get_hostel_floor(hostel_id, extra_filter, session):
    qry = list(HostelSetting.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__floor__session=session).exclude(status="DELETE").filter(**extra_filter).values('hostel_id__floor', 'hostel_id__floor__value').distinct())
    if len(qry) > 0:
        for q in qry:
            q['floor'] = q['hostel_id__floor']
            q['floor__value'] = q['hostel_id__floor__value']
    return qry


def get_hostel_seater_type(hostel_id, floor, extra_filter, session):
    qry = list(HostelFlooring.objects.filter(hostel_id=hostel_id, floor=floor, hostel_id__session=session).exclude(status="DELETE").filter(**extra_filter).values('bed_capacity', 'bed_capacity__value'))
    return qry


def get_floor_type(extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field='FLOOR TYPE', session=session).exclude(value__isnull=True).exclude(status='DELETE').filter(**extra_filter).values('field', 'value', 'sno'))
    return qry


def get_room_type(extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field="ROOM TYPE", session=session).exclude(value__isnull=True).exclude(status='DELETE').filter(**extra_filter).values('field', 'value', 'sno'))
    return qry


def get_medical_category(extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field='MEDICAL CATEGORY', session=session).filter(**extra_filter).exclude(status='DELETE').exclude(value__isnull=True).values('sno', 'value').order_by('value'))
    return qry


def get_medical_cases(extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field='MEDICAL CASE', session=session).filter(**extra_filter).exclude(value__isnull=True).exclude(status='DELETE').values('sno', 'value'))
    return qry


def get_emp_category(extra_filter, session):
    qry = list(HostelDropdown.objects.filter(field='TYPE OF EMPLOYEE', session=session).exclude(value__isnull=True).filter(**extra_filter).exclude(status='DELETE').values('value', 'sno'))
    for q in qry:
        if (q['value'] == 'REC'):
            q['value'] = 'RECTOR'
        if (q['value'] == 'WAR'):
            q['value'] = 'WARDEN'
    return qry

########################################## HOSTEL DROPDWON FUNTIONS END #############################################
#####################################################################################################################


def get_employee(category, dept, extra_filter):
    qry = list(EmployeePrimdetail.objects.filter(emp_category__in=category, dept__in=dept).filter(*extra_filter).exclude(emp_status='SEPARATE').exclude(emp_id="00007").values('name', 'emp_id', 'dept', 'dept__value').order_by('name'))
    return qry


def get_all_year(course, extra_filter):
    qry = list(CourseDetail.objects.filter(course__in=course).values_list('course_duration', flat=True).distinct())
    max_year = max(qry)
    year_li = list(range(1, max_year + 1))
    return year_li


def get_hostel_year(hostel_id, branch, extra_filter, session):
    qry = list(HostelSetting.objects.filter(hostel_id__hostel_id__in=hostel_id, branch__in=branch, hostel_id__hostel_id__session=session).exclude(status="DELETE").values('year').distinct().order_by('year'))
    return qry


def get_rector_year(hostel_id, course, extra_filter, session):
    qry2 = list(HostelSetting.objects.filter(hostel_id__hostel_id__in=hostel_id, branch__course__in=course, hostel_id__hostel_id__session=session).exclude(status='DELETE').values('year').order_by('year').distinct())
    return qry2


def get_course(hostel_id, extra_filter, session):
    qry = list(HostelSetting.objects.filter(hostel_id__hostel_id__in=hostel_id, hostel_id__hostel_id__session=session).exclude(status="DELETE").filter(**extra_filter).values('branch__course', 'branch__course__value').order_by('branch__course__value').distinct())
    return qry


def get_rector_course(hostel_id, extra_filter, session):
    qry = list(HostelSetting.objects.filter(hostel_id__hostel_id__in=hostel_id, hostel_id__hostel_id__session=session).exclude(status="DELETE").filter(**extra_filter).values('branch__course', 'branch__course__value').order_by('branch__course__value').distinct())
    return qry


def get_rector_branch(hostel_id, course, extra_filter, session):
    qry = list(HostelSetting.objects.filter(branch__course__in=course, hostel_id__hostel_id__in=hostel_id, hostel_id__hostel_id__session=session).exclude(status="DELETE").filter(**extra_filter).values('branch', 'branch__dept', 'branch__dept__value', 'branch__course', 'branch__course__value').order_by('branch__dept__value').distinct())
    return qry


def get_branch(hostel_id, course, extra_filter, session):
    qry = list(HostelSetting.objects.filter(branch__course__in=course, hostel_id__hostel_id__in=hostel_id, hostel_id__hostel_id__session=session).exclude(status="DELETE").filter(**extra_filter).values('branch', 'branch__dept', 'branch__dept__value', 'branch__course', 'branch__course__value').order_by('branch__dept__value').distinct())
    return qry
# def get_student_eligible_seater(uniq_id,session_name,extra_filter,session):
#     studentSession = generate_session_table_name("studentSession_",session_name)
#     data = list(studentSession.objects.filter(uniq_id=uniq_id).values('year','sem__dept'))
#     if len(data)>0:
#         data = list(HostelSetting.objects.filter(year=data[0]['year'],branch=data[0]['sem__dept'],hostel_id__hostel_id__session=session).exclude(status="DELETE").annotate(sno=F('hostel_id__hostel_id')).values('sno','hostel_id__floor','hostel_id__floor__value','hostel_id__bed_capacity','hostel_id__bed_capacity__value','hostel_id__hostel_id','hostel_id__hostel_id__value').distinct().order_by('year'))
#     return data


def get_student_eligible_seater(uniq_id, session_name, extra_filter, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    data = studentSession.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept', 'uniq_id__gender__value')
    data_value = []
    if len(data) > 0:
        if data[0]['uniq_id__gender__value'] in "MALE":
            data[0]['uniq_id__gender__value'] = "BOYS"
        else:
            data[0]['uniq_id__gender__value'] = "GIRLS"

        data_value = list(HostelSetting.objects.filter(year=data[0]['year'], hostel_id__hostel_id__field__contains=data[0]['uniq_id__gender__value'], branch=data[0]['sem__dept'], hostel_id__hostel_id__session=session).exclude(status="DELETE").annotate(sno=F('hostel_id__hostel_id')).values('sno', 'hostel_id__floor', 'hostel_id__floor__value', 'hostel_id__bed_capacity', 'hostel_id__bed_capacity__value', 'hostel_id__hostel_id', 'hostel_id__hostel_id__value').distinct().order_by('sno'))
    return data_value


def acc_get_student_eligible_seater(uniq_id, session_name, extra_filter, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    data = studentSession.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept', 'uniq_id__gender__value')
    data_value = []
    if len(data) > 0:
        if data[0]['uniq_id__gender__value'] in "MALE":
            data[0]['uniq_id__gender__value'] = "BOYS"
        else:
            data[0]['uniq_id__gender__value'] = "GIRLS"

        data_value = list(HostelSetting.objects.filter(year=data[0]['year'], hostel_id__hostel_id__field__contains=data[0]['uniq_id__gender__value'], branch=data[0]['sem__dept'], hostel_id__hostel_id__session=session).exclude(status="DELETE").annotate(sno=F('hostel_id__hostel_id')).values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value', 'hostel_id__hostel_id', 'hostel_id__hostel_id__value').distinct().order_by('sno'))
    return data_value


def get_student_eligible_seater_acc(uniq_id, session_name, extra_filter, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    data = list(studentSession.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept'))
    if len(data) > 0:
        data = list(HostelSetting.objects.filter(year=data[0]['year'], branch=data[0]['sem__dept'], hostel_id__hostel_id__session=session).exclude(status="DELETE").annotate(sno=F('hostel_id__bed_capacity')).annotate(value=F('hostel_id__bed_capacity__value')).values('sno', 'value').distinct().order_by('value'))
    return data


def get_student_details(uniq_id, session_name, extra_filter, sem_type, session):
    studentSession = generate_session_table_name("studentSession_", session_name)
    try:
        StuGroupAssign = generate_session_table_name("StuGroupAssign_", session_name)
        GroupSection = generate_session_table_name("GroupSection_", session_name)
        EmpGroupAssign = generate_session_table_name("EmpGroupAssign_", session_name)
    except:
        pass
    data = list(studentSession.objects.filter(uniq_id=uniq_id).filter(**extra_filter).values('uniq_id', 'year', 'uniq_id__name','uniq_id__batch_to','uniq_id__batch_from','uniq_id__uni_roll_no', 'uniq_id__lib_id', 'sem__sem', 'sem', 'section', 'section__section', 'sem__dept__dept__value', 'sem__dept', 'mob', 'sem__dept__course', 'sem__dept__course__value'))
    for d in data:
        mentor_name = []
        try:
            group_id = list(StuGroupAssign.objects.filter(uniq_id=uniq_id, group_id__type_of_group='MENTOR').exclude(status='DELETE').values_list('group_id'))
            sem_group = list(GroupSection.objects.filter(section_id__sem_id__sem=d['sem__sem'], group_id__in=group_id).values_list('group_id'))
            mentor_name = list(EmpGroupAssign.objects.filter(group_id__in=sem_group).exclude(status='DELETE').values('emp_id__name', 'emp_id'))
        except:
            pass
        

        # CHANGE WHEN NEXT SESSION START
        current_session_id = 1 #BY DEFAULT
        current_session = Semtiming.objects.filter(sem_start__lte=date.today(), sem_end__gte=date.today()).order_by('-uid').values()
        if len(current_session)>0:
            current_odd_session = Semtiming.objects.filter(session=current_session[0]['session'],sem_type="odd").order_by('-uid').values()
            if len(current_odd_session)>0:
                current_session_id = current_odd_session[0]['uid']
        hostel_status = check_residential_status(uniq_id, current_session_id, sem_type)
        # CHANGE WHEN NEXT SESSION START
        

        phy_disabled = list(StudentPerDetail.objects.filter(uniq_id=uniq_id).values('dob', 'physically_disabled', 'fname', 'uniq_id__gender', 'uniq_id__gender__value'))
        father_mob = list(StudentFamilyDetails.objects.filter(uniq_id=uniq_id).values_list('father_mob', flat=True))
        stu_address = list(StudentAddress.objects.filter(uniq_id=uniq_id).values('p_add1','p_add2','p_city','p_district','p_pincode','c_add1','c_add2','c_district','c_pincode'))
        stu_photo = list(StudentPerDetail.objects.filter(uniq_id=uniq_id).values_list('image_path',flat=True))
        d['father_mob'] = father_mob[0]
        d['stu_photo'] = stu_photo[0]
        d['stu_address'] = stu_address[0]
        if len(mentor_name) > 0:
            d['mentor_name'] = mentor_name[0]
        else:
            d['mentor_name'] = ""
        d['hostel_status'] = hostel_status
        if len(phy_disabled) > 0:
            d['phy_disabled'] = phy_disabled[0]['physically_disabled']
            d['fname'] = phy_disabled[0]['fname']
            d['dob'] = phy_disabled[0]['dob']
            d['gender'] = phy_disabled[0]['uniq_id__gender']
            d['gender__value'] = phy_disabled[0]['uniq_id__gender__value']
        else:
            d['phy_disabled'] = ""
            d['dob'] = ""
            d['fname'] = ""
            d['gender'] = ""
            d['gender__value'] = ""
    return data


def get_incidents_details(session_name, extra_filter):
    IncidentApproval = generate_session_table_name("IncidentApproval_", session_name)
    data = list(IncidentApproval.objects.filter(**extra_filter).exclude(status="DELETE").values('id', 'incident_detail', 'incident_detail__uniq_id__year', 'incident_detail__uniq_id', 'incident_detail__uniq_id__uniq_id', 'incident_detail__uniq_id__uniq_id__name', 'incident_detail__uniq_id__uniq_id__uni_roll_no', 'incident_detail__uniq_id__uniq_id__lib_id', 'incident_detail__uniq_id__sem__sem', 'incident_detail__uniq_id__sem', 'incident_detail__uniq_id__section', 'incident_detail__uniq_id__section__section', 'incident_detail__uniq_id__sem__dept__dept__value', 'incident_detail__uniq_id__sem__dept', 'incident_detail__uniq_id__mob', 'incident_detail__incident__date_of_incident', 'incident_detail__incident__description', 'incident_detail__incident__incident_document', 'incident_detail__incident__added_by', 'appoval_status', 'incident_detail__incident__added_by__name', 'incident_detail__action', 'incident_detail__comm_to_parent', 'incident_detail__student_document', 'incident_detail__time_stamp', 'approved_by', 'approved_by__name', 'remark', 'incident_detail__uniq_id__sem__dept__course', 'incident_detail__uniq_id__sem__dept__course__value', 'time_stamp').order_by('time_stamp'))
    for q in data:
        if (q['incident_detail__incident__incident_document'] == "" or q['incident_detail__incident__incident_document'] == None):
            q['incident_detail__incident__incident_document'] = "---"
        if (q['incident_detail__student_document'] == "" or q['incident_detail__student_document'] == None):
            q['incident_detail__student_document'] = "---"
    return data


def get_medical_details(uniq_id_list, session_name, extra_filter):
    HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
    HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)
    HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
    approved_medical_applications = HostelMedicalApproval.objects.filter(student_medical__uniq_id__in=uniq_id_list, approval_status="APPROVED").exclude(status='DELETE').values_list('student_medical', flat=True)
    approved_medical_cases = HostelMedicalCases.objects.filter(student_medical__in=approved_medical_applications).exclude(status='DELETE').values("student_medical__uniq_id", "cases__value").order_by("student_medical__uniq_id")
    data = {}
    for cases in approved_medical_cases:
        if(cases['student_medical__uniq_id'] in data):
            data[cases['student_medical__uniq_id']].append(cases['cases__value'])
        else:
            data[cases['student_medical__uniq_id']] = []
            data[cases['student_medical__uniq_id']].append(cases['cases__value'])
    return data


def get_uniq_id_medical_details(uniq_id, session_name, extra_filter):
    HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
    HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)
    HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
    approved_medical_applications = list(HostelMedicalApproval.objects.filter(student_medical__uniq_id=uniq_id, approval_status="APPROVED").exclude(status='DELETE').values('student_medical', 'student_medical__uniq_id', 'student_medical__medical_category_id', 'student_medical__document', 'student_medical__added_by', 'student_medical__added_by__name', 'student_medical__added_by__desg', 'student_medical__added_by__dept__value', 'student_medical__time_stamp'))
    if len(approved_medical_applications) > 0:
        approved_medical_cases = list(HostelMedicalCases.objects.filter(student_medical=approved_medical_applications[0]['student_medical']).exclude(status='DELETE').values("student_medical__uniq_id", "cases__value").order_by("student_medical__uniq_id"))
        approved_medical_applications[0]['cases'] = approved_medical_cases
    return approved_medical_applications


def get_seater_prefrence_details(uniq_id_list, session_name, extra_filter):
    HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_', session_name)
    seater_applications = HostelSeaterPriority.objects.filter(application_id__uniq_id__in=uniq_id_list).exclude(status='DELETE').exclude(application_id__status="DELETE").values('application_id__uniq_id', 'seater__value', 'priority').order_by('application_id__uniq_id', 'priority')
    data = {}
    for seater in seater_applications:
        if(seater['application_id__uniq_id'] in data):
            data[seater['application_id__uniq_id']].append(seater['seater__value'])
        else:
            data[seater['application_id__uniq_id']] = []
            data[seater['application_id__uniq_id']].append(seater['seater__value'])
    return data


def get_hostel_emp_details(extra_filter, session):
    qry = list(HostelAssignEmp.objects.filter(**extra_filter).filter(type_of_duty__session=session).exclude(status='DELETE').values('emp_id', 'emp_id__name', 'hostel_id', 'hostel_id__value', 'type_of_duty', 'type_of_duty__value', 'emp_id__dept', 'emp_id__dept__value', 'emp_id__emp_type', 'emp_id__emp_type__value', 'emp_id__emp_category', 'emp_id__emp_category__value', 'emp_id__desg', 'emp_id__desg__value', 'emp_id__mob', 'emp_id__mob1', 'emp_id__email', 'emp_id__lib_card_no', 'emp_id__organization', 'emp_id__organization__value').order_by('hostel_id__value', 'type_of_duty__value', 'emp_id__name'))
    for q in qry:
        if q['type_of_duty__value'] == 'WAR':
            q['type_of_duty__value'] = 'WARDEN'
        elif q['type_of_duty__value'] == 'REC':
            q['type_of_duty__value'] = 'RECTOR'
    return qry


def get_hostel_student_list(extra_filter, session_name):
    studentSession = generate_session_table_name("studentSession_", session_name)
    qry = list(studentSession.objects.filter(**extra_filter).exclude(uniq_id__admission_status__value='EX-STUDENT').exclude(uniq_id__admission_status__value='WITHDRAWAL').values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no', 'uniq_id__uni_roll_no', 'uniq_id__lib_id', 'uniq_id__dept_detail__course', 'uniq_id__dept_detail__dept', 'uniq_id__dept_detail__course__value', 'uniq_id__dept_detail__dept__value').order_by('uniq_id__name'))
    for q in qry:
        q['uniq_id__uniq_id__name'] = q['uniq_id__name']
    return qry


def get_student_physically_disabled(extra_filter):
    data = []
    qry2 = list(StudentPerDetail.objects.filter(**extra_filter).values('physically_disabled', 'uniq_id', 'uniq_id__name'))
    data.append({'physically_disabled': qry2[0]['physically_disabled'], 'uniq_id': qry2[0]['uniq_id'], 'name': qry2[0]['uniq_id__name']})
    return data


def get_gender(emp_id):
    qry = list(EmployeePerdetail.objects.filter(emp_id=emp_id).values('gender', 'gender__value'))
    return qry


def get_rector_or_chief_rector(emp_id):
    roles = Roles.objects.filter(emp_id=emp_id).values('roles', 'roles__value')
    for r in roles:
        if r['roles__value'] == 'CHIEF RECTOR BOYS':
            key1 = 'CHIEF RECTOR'
            break
        elif r['roles__value'] == 'CHIEF RECTOR GIRLS':
            key1 = 'CHIEF RECTOR'
            break
        else:
            key1 = None
    if get_rector_or_not(emp_id, {}) == 200:
        key2 = 'RECTOR'
    else:
        key2 = None
    if key1 != None and key2 != None:
        key = 'BOTH'
    elif key1 != None:
        key = key1
    elif key2 != None:
        key = key2
    elif key1 == None and key2 == None:
        key = None
    return key


def get_hostel_category(emp_id):
    roles = list(Roles.objects.filter(emp_id=emp_id).values('roles', 'roles__value'))
    for r in roles:
        if r['roles__value'] == 'CHIEF RECTOR GIRLS':
            category = 'GIRLS'
        elif r['roles__value'] == 'CHIEF RECTOR BOYS':
            category = 'BOYS'
        else:
            category = ''
    return category


def check_isLocked(lock_type, uniq_id, session_name):
    HostelLockingUnlockingStatus = generate_session_table_name('HostelLockingUnlockingStatus_', session_name)
    today = datetime.now()
    qry_check = HostelLockingUnlockingStatus.objects.filter(LockingUnlocking__lock_type=lock_type, uniq_id=uniq_id).values('LockingUnlocking__unlock_to', 'LockingUnlocking__unlock_from').order_by('-LockingUnlocking__id')
    if len(qry_check) > 0:
        if qry_check[0]['LockingUnlocking__unlock_to'] < today or qry_check[0]['LockingUnlocking__unlock_from'] > today:
            return False
        else:
            return True
    else:
        return False


def get_rector_or_not(emp_id, extra_filter):
    qry = list(HostelAssignEmp.objects.filter(emp_id=emp_id, type_of_duty__value='REC').exclude(status="DELETE").filter(**extra_filter).values('hostel_id'))
    if len(qry) > 0:
        return 200
    else:
        return 401


def get_year_startend_date(session):
    qry = list(Semtiming.objects.filter(uid=session).values('sem_type', 'sem_start', 'sem_end'))
    for q in qry:
        from_date = q['sem_start']
        to_date = datetime.now()
    data = {"from_date": from_date, "to_date": to_date}
    return data


def get_bed_capacity(hostel, extra_filter, session):
    qry = list(HostelFlooring.objects.filter(hostel_id=hostel, hostel_id__session=session).filter(**extra_filter).exclude(status='DELETE').values('bed_capacity', 'bed_capacity__value').distinct().order_by('bed_capacity'))
    return qry


def get_number_of_bed(hostel, bed_capacity, extra_filter, session):
    qry = HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel, hostel_id__bed_capacity=bed_capacity, hostel_id__hostel_id__session=session, room_type__value='STUDENT ROOM').filter(**extra_filter).exclude(status='DELETE').values('hostel_id__bed_capacity__value')
    return qry


def get_number_of_student_room(hostel, bed_capacity, extra_filter, session):
    qry = HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel, hostel_id__bed_capacity=bed_capacity, hostel_id__hostel_id__session=session, room_type__value='STUDENT ROOM').filter(**extra_filter).exclude(status='DELETE').count()
    return qry


def get_odd_sem(Session):
    data = {}
    qry = list(Semtiming.objects.filter(session=Session).values('sem_type', 'uid', 'session_name'))
    for q in qry:
        if q['sem_type'] == 'odd':
            data['session'] = q['uid']
            data['session_name'] = q['session_name']
    return data


def lock_code_chooser(lock_code):
    function = "lock_type." + lock_code
    return eval(function)


def get_lock_type_for_lock_code(lock_code):
    lock_type = lock_code_chooser(lock_code)['value']
    return lock_type


def student_room_avaiable(hostel, seater, floor, extra_filter):
    query = HostelRoomSettings.objects.filter(room_type__value='STUDENT ROOM', is_blocked=0, alloted_status=0, hostel_id=hostel, hostel_id__bed_capacity=seater, hostel_id__floor=floor).filter(*extra_filter).exclude(status='DELETE').values('room_no', 'hostel_id__floor', 'hostel_id__bed_capacity').distinct()
    return query


def get_student_seater_defined(uniq_id, hostel_id, session_name):
    studentSession = generate_session_table_name('studentSession_', session_name)
    qry = list(studentSession.objects.filter(uniq_id=uniq_id).values('year', 'sem__dept', 'uniq_id__admission_status', 'uniq_id__admission_type'))
    qry1 = list(HostelSetting.objects.filter(hostel_id__hostel_id=hostel_id, year=qry[0]['year'], branch=qry[0]['sem__dept'], admission_status=qry[0]['uniq_id__admission_status'], admission_type=qry[0]['uniq_id__admission_type']).exclude(status="DELETE").values_list('hostel_id__bed_capacity__value', flat=True).distinct())
    return qry1


def get_rooms_of_seater_type(hostel_id, seater_type):
    student_room = list(HostelDropdown.objects.filter(value="STUDENT ROOM").values_list('sno', flat=True))
    qry = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__bed_capacity=seater_type, room_type=student_room[0]).exclude(is_blocked=1).exclude(status="DELETE").values_list('room_no', flat=True))
    return len(qry)


def get_uniq_id_alloted_seater(uniq_id, session_name):
    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
    qry = list(HostelSeatAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('seat_part', 'seat_part__value'))
    return qry


def get_alloted_seater(seater_type, hostel_id, session_name):
    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
    qry = list(HostelSeatAlloted.objects.filter(hostel_part=hostel_id, seat_part=seater_type).exclude(status="DELETE").values_list('uniq_id', flat=True))
    return len(qry)

#################################################################################################################################

########################################################## SEAT ALLOTMENT FUNCTIONS ########################################################


def get_seat_allotment_rule_previous_data(hostel, list_no, session_name):
    HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)

    query = list(HostelSeatAllotSetting.objects.filter(hostel_part=hostel, list_no=list_no).exclude(status='DELETE').exclude(list_no__isnull=True).values('priority', 'list_no', 'sub_priority', 'year', 'branch__course', 'branch__course__value', 'branch__dept', 'branch__dept__value', 'seat_part', 'seat_part__value', 'hostel_part', 'hostel_part__value', 'indiscipline', 'att_min', 'att_max', 'uni_min', 'uni_max', 'carry_min', 'carry_max', 'room_max', 'room_min').order_by('priority', 'sub_priority', 'list_no').distinct())

    primary_list = order_by_priority(query, ['priority', 'indiscipline', 'att_min', 'att_max', 'uni_max', 'uni_min', 'carry_min', 'carry_max'])
    return primary_list


def get_seat_allotment_rule_view_list_data(hostel, session_name):
    HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)
    query = list(HostelSeatAllotSetting.objects.filter(hostel_part=hostel, list_no__isnull=True).exclude(status='DELETE').values('priority', 'list_no', 'sub_priority', 'year', 'branch', 'branch__course', 'branch__course__value', 'branch__dept', 'branch__dept__value', 'seat_part', 'seat_part__value', 'hostel_part', 'hostel_part__value', 'indiscipline', 'att_min', 'att_max', 'uni_min', 'uni_max', 'carry_min', 'carry_max', 'room_max', 'room_min', 'id').order_by('priority', 'sub_priority').distinct())

    primary_list = order_by_priority(query, ['priority', 'sub_priority'])
    return primary_list


def seat_allotment_student_view_list(branch, year, att_min, att_max, uni_min, uni_max, carry_min, carry_max, gender, session_name):
    HostelSeaterPriority = generate_session_table_name('HostelSeaterPriority_', session_name)
    filters_data = {}
    if branch is not None:
        filters_data["application_id__uniq_id__sem__dept__in"] = branch
    if year is not None:
        filters_data["application_id__uniq_id__year__in"] = year
    if att_min is not None:
        filters_data["application_id__attendance_avg__gte"] = att_min
    if att_max is not None:
        filters_data["application_id__attendance_avg__lte"] = att_max
    if carry_max is not None:
        filters_data["application_id__carry__lte"] = carry_max
    if carry_min is not None:
        filters_data["application_id__carry__gte"] = carry_min
    if uni_max is not None:
        filters_data["uni_per__lte"] = uni_max
    if uni_min is not None:
        filters_data["uni_per__gte"] = uni_min
    if gender is not None:
        filters_data["application_id__uniq_id__uniq_id__gender__value"] = gender
    data = HostelSeaterPriority.objects.annotate(uni_per=(F('application_id__uni_marks_obt') / F('application_id__uni_max_marks')) * 100).annotate(uniq_id=F('application_id__uniq_id')).annotate(name=F('application_id__uniq_id__uniq_id__name')).annotate(branch=F('application_id__uniq_id__sem__dept')).annotate(year=F('application_id__uniq_id__year')).annotate(carry=F('application_id__carry')).annotate(attendance_avg=F('application_id__attendance_avg')).annotate(current_status=F('application_id__current_status')).annotate(uni_marks_obt=F('application_id__uni_marks_obt')).annotate(uni_max_marks=F('application_id__uni_max_marks')).filter(application_id__current_status='PENDING').filter(**filters_data).exclude(application_id__current_status='WITHDRAWAL').exclude(application_id__current_status='SEAT ALLOTED').exclude(application_id__status='DELETE').exclude(status='DELETE').values('uniq_id', 'name', 'branch', 'year', 'current_status', 'uni_per', 'uni_marks_obt', 'uni_max_marks', 'seater', 'seater__value', 'priority', 'carry', 'attendance_avg').order_by('-application_id__attendance_avg', '-uni_per', 'application_id__carry', 'application_id__uniq_id', 'priority').distinct()
    # temp = HostelSeaterPriority.objects.filter(**filters_data).exclude(application_id__current_status='SEAT ALLOTED').exclude(application_id__status='DELETE').exclude(status='DELETE').values()
    data = list(data)
    ###################ADD MEDICAL  AND   CARRY THING ##################
    primary_list = order_by_uniq_id(data, ['uniq_id'])
    return primary_list

################################# END #################### SEAT ALLOTMENT FUNCTIONS ########################################################


def get_room_allotment_rule_previous_data(hostel, list_no, session_name):
    HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)

    query = list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel, list_no=list_no).exclude(status='DELETE').exclude(list_no__isnull=True).values('priority', 'list_no', 'sub_priority', 'year', 'branch__course', 'branch__course__value', 'branch__dept', 'branch__dept__value', 'hostel_part', 'hostel_part__hostel_id', 'hostel_part__hostel_id__value', 'hostel_part__floor', 'hostel_part__floor__value', 'hostel_part__bed_capacity', 'hostel_part__bed_capacity__value', 'phy_disabled', 'medical', 'indiscipline', 'att_min', 'att_max', 'uni_min', 'uni_max', 'carry_min', 'carry_max', 'room_max', 'room_min', 'course_preference').order_by('priority', 'sub_priority', 'list_no').distinct())

    primary_list = order_by_priority(query, ['priority', 'indiscipline', 'course_preference', 'phy_disabled', 'medical', 'att_min', 'att_max', 'uni_max', 'uni_min', 'carry_min', 'carry_max', 'sub_priority'])

    return primary_list


def get_room_allotment_rule_view_list_data(hostel, session_name):
    HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)

    query = list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel, list_no__isnull=True).annotate(floor=(F('hostel_part__floor'))).exclude(status='DELETE').values('priority', 'list_no', 'sub_priority', 'year', 'branch', 'branch__course', 'branch__course__value', 'branch__dept', 'branch__dept__value', 'hostel_part__hostel_id', 'hostel_part__hostel_id__value', 'medical', 'phy_disabled', 'hostel_part', 'hostel_part__floor', 'hostel_part__floor__value', 'hostel_part__bed_capacity', 'hostel_part__bed_capacity__value', 'indiscipline', 'room_max', 'room_min', 'course_preference', 'id', 'carry_min', 'carry_max', 'uni_min', 'uni_max', 'att_min', 'att_max', 'floor').order_by('priority', 'sub_priority', 'floor').distinct())

    primary_list = room_view_list_create_order_by_priority(query, ['priority', 'sub_priority', 'floor'])
    return primary_list


def room_allotment_student_view_list(hostel_id, branch, year, gender, session_name, session, extra_filter):
    HostelRoommatePriority = generate_session_table_name('HostelRoommatePriority_', session_name)
    HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
    HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
    HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)

    student_data = []
    non_medical = []
    medical = []
    filter_data = {}

    order_by_keys = []

    if "course_prefrence" in extra_filter:
        if course_prefrence == 1:
            order_by_keys.append('course')

    if "seater" is extra_filter:
        if seater is not None:
            filter_data['seat_part__value'] = seater

    order_by_keys = order_by_keys + ['-attendance_avg', '-uni_per', 'uniq_id']

    data = list(HostelSeatAlloted.objects.filter(hostel_part=hostel_id, paid_status="ALREADY PAID", uniq_id__uniq_id__gender__value=gender).filter(**filter_data).exclude(status="DELETE").values_list('uniq_id', flat=True))
    if len(data) > 0:

        student_data = list(HostelStudentAppliction.objects.annotate(uni_per=(F('uni_marks_obt') / F('uni_max_marks')) * 100).annotate(course=(F('uniq_id__uniq_id__dept_detail__course_id'))).annotate(branch=(F('uniq_id__uniq_id__dept_detail'))).annotate(year=(F('uniq_id__year'))).filter(uniq_id__in=data, current_status="SEAT ALLOTED", uniq_id__uniq_id__dept_detail__in=branch, uniq_id__year__in=year).exclude(current_status="WITHDRAWAL").exclude(status="DELETE").values('attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'uni_per', 'uniq_id__uniq_id__name', 'uniq_id__year', 'uniq_id', 'course', 'branch', 'year').order_by(*order_by_keys))

        for stu in student_data:

            student_priority = list(HostelRoommatePriority.objects.filter(application_id__uniq_id=stu['uniq_id'], application_id__current_status="SEAT ALLOTED").exclude(application_id__current_status='ROOM ALLOTED').exclude(application_id__status='WITHDRAWAL').exclude(status='DELETE').values('uniq_id', 'priority').order_by('priority').distinct())

            seater_data = list(HostelSeatAlloted.objects.filter(uniq_id=stu['uniq_id'], paid_status="ALREADY PAID").exclude(status="DELETE").values('seat_part__value', 'rule_used'))
            stu['seater'] = seater_data[0]['seat_part__value']
            stu['seater_rule'] = seater_data[0]['rule_used']

            if len(student_priority) > 0:
                stu['roommate'] = ", ".join(list([str(x['uniq_id']) for x in student_priority]))
            else:
                stu['roommate'] = ""

            medical_data = (HostelMedicalApproval.objects.filter(student_medical__uniq_id=stu['uniq_id'], approval_status="APPROVED", student_medical__session=session).exclude(status="DELETE").values())
            if len(medical_data):
                stu['medical'] = 1
            else:
                stu['medical'] = 0
            if 'medical' in extra_filter:
                if extra_filter['medical'] == 1:
                    if len(medical_data):
                        medical.append(stu)
                    else:
                        non_medical.append(stu)
                else:
                    non_medical.append(stu)
            else:
                non_medical.append(stu)
    student_data = medical + non_medical

    return student_data


def get_room_occupied_un_capacity(hostel_id, session_name, session):
    room_capacity_un_occupied_data = get_hostel_capacity(hostel_id, session_name, session)
    room_capacity_occupied_data = get_room_occupied_capacity(hostel_id, session_name, session)
    for bed_capacity in room_capacity_un_occupied_data:
        if bed_capacity in room_capacity_occupied_data:
            room_capacity_un_occupied_data[bed_capacity] = room_capacity_un_occupied_data[bed_capacity] - room_capacity_occupied_data[bed_capacity]
        else:
            pass
    return room_capacity_un_occupied_data

############################################ GET OCCUPIED CAPACITY OF ROOM FOR STUDENT #################################################################


def get_room_occupied_capacity(hostel_id, session_name, session):
    total_room_capacity_data = {}
    HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
    room_alloted_data = list(HostelRoomAlloted.objects.filter(room_part__hostel_id=hostel_id).exclude(status="DELETE").exclude(room_part__hostel_id__isnull=True).exclude(room_part__isnull=True).values('room_part__allotted_status', 'room_part__hostel_id__bed_capacity__value').distinct())
    for room in room_alloted_data:
        if room['room_part__hostel_id__bed_capacity__value'] in total_room_capacity_data:
            total_room_capacity_data[room['room_part__hostel_id__bed_capacity__value']] = total_room_capacity_data[room['room_part__hostel_id__bed_capacity__value']] + int(room['room_part__alloted_status'])
        else:
            total_room_capacity_data[room['room_part__hostel_id__bed_capacity__value']] = int(room['room_part__alloted_status'])
    return total_room_capacity_data
########################### END ############ GET OCCUPIED CAPACITY OF ROOM FOR STUDENT #################################################################


def get_totat_rooms_id(hostel_id, session_name):
    data = []
    data = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, room_type__value="STUDENT ROOM").exclude(is_blocked=1).exclude(status="DELETE").values('id', 'allotted_status', 'hostel_id__bed_capacity__value', 'hostel_id__floor__value').order_by('hostel_id__bed_capacity__value', 'id', 'hostel_id__floor__value'))
    room_data = collections.OrderedDict()

    for d in data:

        capacity = int(d['hostel_id__bed_capacity__value']) - int(d['allotted_status'])

        if d['hostel_id__bed_capacity__value'] in room_data:

            if d['hostel_id__floor__value'] in room_data[d['hostel_id__bed_capacity__value']]:
                room_data[d['hostel_id__bed_capacity__value']][d['hostel_id__floor__value']].append({d['id']: capacity})
            else:
                room_data[d['hostel_id__bed_capacity__value']][d['hostel_id__floor__value']] = list()
                room_data[d['hostel_id__bed_capacity__value']][d['hostel_id__floor__value']].append({d['id']: capacity})

        else:
            room_data[d['hostel_id__bed_capacity__value']] = collections.OrderedDict()
            room_data[d['hostel_id__bed_capacity__value']][d['hostel_id__floor__value']] = list()
            room_data[d['hostel_id__bed_capacity__value']][d['hostel_id__floor__value']].append({d['id']: capacity})

    return room_data


def get_hostel_seater_students(hostel_id, bed_capacity, extra_filter, session_name):
    total_room_capacity_data = {}
    HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
    room_alloted_data = list(HostelRoomAlloted.objects.filter(room_part__hostel_id__hostel_id=hostel_id, room_part__hostel_id__bed_capacity=bed_capacity).exclude(status="DELETE").exclude(room_part__hostel_id__isnull=True).exclude(room_part__isnull=True).values('id', 'uniq_id', 'uniq_id__uniq_id__name', 'room_part__room_no').distinct())
    for x in room_alloted_data:
        x['uniq_id__uniq_id__name'] = x['uniq_id__uniq_id__name'] + " ( ROOM NO: " + x['room_part__room_no'] + " )"
    return room_alloted_data
