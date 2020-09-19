# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
from datetime import date
import math
from django.db.models import Q, Sum, Count, Max, F
from datetime import datetime
import json

from login.views import checkpermission, generate_session_table_name
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from StudentAcademics.models import *
from Registrar.models import *
from musterroll.models import EmployeePrimdetail, Roles
from itertools import groupby
from StudentSMM.models import *
from StudentHostel.models import *

from StudentHostel.views.hostel_function import *
from StudentAccounts.views import acc_get_hostel_component
from StudentAcademics.views import *
from StudentSMM.views.smm_function_views import check_residential_status


def Applicant_List(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        session = request.session['Session']
        session_data = get_odd_sem(session)
        session_name = session_data['session_name']
        session = session_data['session']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        valid_session = []
        sessions = list(Semtiming.objects.values('session', 'session_name'))
        for s in sessions:
            if int(s['session_name'][:2]) >= 18:
                valid_session.append(s['session_name'])
        HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
        if requestMethod.GET_REQUEST(request):
            extra_filter = {}
            dept_consolidate_data = {}
            temp_gender_array = []
            extra_filter_final = {}
            application_data_set = set()
            if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS:
                temp_gender_array.append("MALE")
            if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
                temp_gender_array.append("FEMALE")

            if academicCoordCheck.isRector(request) == True:
                rector_hostel = get_rector_hostel(emp_id, {}, session)
                for x in rector_hostel:
                    if x['field'] == "BOYS":
                        temp_gender_array.append("MALE")
                    if x['field'] == "GIRLS":
                        temp_gender_array.append("FEMALE")

            temp_gender_array = list(set(temp_gender_array))

            if 'hostel_id' in request.GET:
                flag_rector = True
                setting_detail_list = HostelSetting.objects.filter(hostel_id__hostel_id__in=list(request.GET['hostel_id'].split(','))).exclude(status="DELETE").exclude(hostel_id__status="DELETE").values('branch', 'year', 'admission_status', 'admission_type')
                for x in setting_detail_list:
                    extra_filter['uniq_id__year'] = x['year']
                    extra_filter['uniq_id__sem__dept'] = x['branch']
                    extra_filter['uniq_id__uniq_id__admission_status'] = x['admission_status']
                    extra_filter['uniq_id__uniq_id__admission_type'] = x['admission_type']
                    extra_filter['uniq_id__uniq_id__gender__value__in'] = temp_gender_array
                    application_data_set = application_data_set | set(list(HostelStudentAppliction.objects.filter(**extra_filter).exclude(status="DELETE").values_list('uniq_id', flat=True)))
                extra_filter_final = {'uniq_id__in': list(application_data_set)}
            else:
                extra_filter_final['uniq_id__uniq_id__gender__value__in'] = temp_gender_array
            application_data = list(HostelStudentAppliction.objects.filter(**extra_filter_final).exclude(status="DELETE").values('uniq_id', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'time_stamp'))

            temp_uniq_id_list = []
            for per_app in application_data:
                per_app['time_stamp'] = ' '.join(str(per_app['time_stamp']).split('T'))
                student_data = get_student_details(per_app['uniq_id'], session_name, {}, 'odd', session)
                if(len(student_data) > 0):
                    temp_student_dict = student_data[0]
                    per_app.update(temp_student_dict)
                temp_uniq_id_list.append(per_app['uniq_id'])

            medical_details = get_medical_details(temp_uniq_id_list, session_name, {})

            for per_app in application_data:

                if per_app['sem__dept__course__value'] in dept_consolidate_data:
                    dept_consolidate_data[per_app['sem__dept__course__value']] = dept_consolidate_data[per_app['sem__dept__course__value']] + 1
                else:
                    dept_consolidate_data[per_app['sem__dept__course__value']] = 1

                if per_app['uniq_id'] in medical_details:
                    temp_medical_details_list = ", ".join(list(x for x in medical_details[per_app['uniq_id']]))
                    per_app['medical_details'] = temp_medical_details_list
                ######## Indiscipline detail ############
                for s in valid_session:
                    IncidentApproval = generate_session_table_name('IncidentApproval_', s)
                    indiscipline_data = list(IncidentApproval.objects.filter(incident_detail__uniq_id=per_app['uniq_id'], level=2, appoval_status='APPROVED').exclude(status="DELETE").values('incident_detail'))

                    if len(indiscipline_data) > 0:
                        per_app['indiscipline'] = 'YES'
                        break
                    else:
                        per_app['indiscipline'] = 'NO'
                        break
                ###########################################

            prefrence_details = get_seater_prefrence_details(temp_uniq_id_list, session_name, {})

            for per_app in application_data:
                if per_app['uniq_id'] in prefrence_details:
                    temp_prefrence_details_list = " => ".join(list(str(x) for x in prefrence_details[per_app['uniq_id']]))
                    per_app['prefrence_details'] = temp_prefrence_details_list
            data = {"application_data": application_data, "dept_consolidate_data": dept_consolidate_data}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Allotted_Unallotted_Student_List(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        session_data = get_odd_sem(request.session['Session'])
        session = session_data['session']
        session_name = session_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        valid_session = []
        sessions = list(Semtiming.objects.values('session', 'session_name'))
        for s in sessions:
            if int(s['session_name'][:2]) >= 18:
                valid_session.append(s['session_name'])
        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
        if requestMethod.GET_REQUEST(request):
            extra_filter = {}
            dept_consolidate_data = {}
            total_seat_capacity_data = {}
            ####################################### GET GENDER FOR WHICH THE LIST NEED TO BE SHOWN (FETCH GENDER) #################################################
            temp_gender_array = []
            if academicCoordCheck.isRector(request) == True:
                rector_hostel = get_rector_hostel(emp_id, {}, session)
                for x in rector_hostel:
                    if x['field'] == "BOYS":
                        temp_gender_array.append("MALE")
                    if x['field'] == "GIRLS":
                        temp_gender_array.append("FEMALE")
                temp_gender_array = list(set(temp_gender_array))

            if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS:
                temp_gender_array.append("MALE")
            if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
                temp_gender_array.append("FEMALE")
            ########################### END ############ GET GENDER FOR WHICH THE LIST NEED TO BE SHOWN (FETCH GENDER) ############################################

            ############################################ GET ELIGIBLE STUDENT DATA BRANCHES, YEAR #################################################################
            filter_data = HostelSetting.objects.filter(hostel_id__hostel_id=request.GET['hostel_id']).exclude(status="DELETE").values('branch', 'year').distinct()

            allotment_list = set()
            applicant_student = set()
            for x in filter_data:
                branch = x['branch']
                year = x['year']
                ############################################ DYNAMIC FILTER DATA FOR UNIQID LISTS #################################################################
                extra_filter_application = {'uniq_id__sem__dept': branch, 'uniq_id__year': year, 'uniq_id__uniq_id__gender__value__in': temp_gender_array}
                ########################### END ############ DYNAMIC FILTER DATA FOR UNIQID LISTS #################################################################
                applicant_student = applicant_student | set(HostelStudentAppliction.objects.filter(**extra_filter_application).exclude(status="DELETE").values_list('uniq_id', flat=True))

                q = HostelStudentAppliction.objects.filter(**extra_filter_application).exclude(status="DELETE").values('uniq_id')
            ########################### END ############ GET ELIGIBLE STUDENT DATA BRANCHES, YEAR #################################################################

            ############################################ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################
            extra_filter_allot = {'hostel_part': request.GET['hostel_id']}
            allotment_list = set(HostelSeatAlloted.objects.filter(**extra_filter_allot).exclude(status="DELETE").values_list('uniq_id', flat=True))

            ##### CHANGE BY VRINDA #######
            total_seat_capacity_data = get_hostel_capacity_for_report(request.GET['hostel_id'], session_name, session)
            # total_seat_capacity_data = get_hostel_capacity(request.GET['hostel_id'], session_name, session)
            ##############################
            total_seat_capacity_data_blocked = get_hostel_capacity_blocked_student_room(request.GET['hostel_id'], session_name, session)
            total_seat_capacity_data_blocked_and_unblocked = get_hostel_capacity_blocked_and_unblocked_student_room(request.GET['hostel_id'], session_name, session)
            ########################### END ############ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################

            seat_alloted_applicant = allotment_list.intersection(applicant_student)
            seat_alloted_applicant = list(seat_alloted_applicant)

            all_student = allotment_list | applicant_student
            all_student = list(all_student)

            seat_alloted_applicant_data = list(HostelSeatAlloted.objects.filter(uniq_id__in=seat_alloted_applicant).exclude(status="DELETE").values('uniq_id', 'hostel_part', 'seat_part', 'hostel_part__value', 'seat_part__value', 'rule_used__list_no', 'paid_status').distinct().order_by('uniq_id'))

            alloted_non_applicant_student = allotment_list.difference(seat_alloted_applicant)
            alloted_non_applicant_student = list(alloted_non_applicant_student)

            # seat_alloted_student_data = list(HostelSeatAlloted.objects.filter(uniq_id__in=alloted_non_applicant_student).exclude(status="DELETE").values('uniq_id', 'hostel_part', 'seat_part', 'hostel_part__value', 'seat_part__value', 'rule_used__list_no', 'status').order_by('uniq_id'))
            prefrence_details = get_seater_prefrence_details(applicant_student, session_name, {})
            unalloted_applicant = applicant_student.difference(seat_alloted_applicant)
            unalloted_applicant = list(unalloted_applicant)

            seat_unalloted_applicant_data = list(HostelStudentAppliction.objects.filter(uniq_id__in=unalloted_applicant).exclude(status="DELETE").values('uniq_id', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'time_stamp', 'current_status', 'status').order_by('uniq_id'))

            data_values = []

            
            for seat_data in seat_alloted_applicant_data:

                applicant_student = list(HostelStudentAppliction.objects.filter(uniq_id=seat_data['uniq_id']).exclude(status="DELETE").values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'time_stamp', 'current_status', 'status').order_by('uniq_id'))
                ########## Indiscipline details #################
                for s in valid_session:
                    IncidentApproval = generate_session_table_name('IncidentApproval_', s)
                    indiscipline_data = list(IncidentApproval.objects.filter(incident_detail__uniq_id=seat_data['uniq_id'], level=2, appoval_status='APPROVED').exclude(status="DELETE").values('incident_detail'))

                    if len(indiscipline_data) > 0:
                        seat_data['indiscipline'] = 'YES'
                        break
                    else:
                        seat_data['indiscipline'] = 'NO'
                        break
                #################################################

                applicant_student[-1]['time_stamp'] = ' '.join(str(applicant_student[-1]['time_stamp']).split('T'))
                student_data = []
                student_data = get_student_details(applicant_student[-1]['uniq_id'], session_name, {}, 'odd', session)
                temp_student_dict = {}
                if(len(student_data) > 0):
                    temp_student_dict = student_data[-1]
                    applicant_student[-1].update(temp_student_dict)
                applicant_student[-1].update(seat_data)

                data_values.append(applicant_student[-1])

            for seat_un_data in seat_unalloted_applicant_data:
                temp_student_dict = {}
                student_data = []
                student_data = get_student_details(seat_un_data['uniq_id'], session_name, {}, 'odd', session)
                if(len(student_data) > 0):
                    temp_student_dict = student_data[0]
                    for x in temp_student_dict:
                        seat_un_data[x] = temp_student_dict[x]
                    ####### Indiscipline details ############
                    for s in valid_session:
                        IncidentApproval = generate_session_table_name('IncidentApproval_', s)
                        indiscipline_data = list(IncidentApproval.objects.filter(incident_detail__uniq_id=seat_un_data['uniq_id'], level=2, appoval_status='APPROVED').exclude(status="DELETE").values('incident_detail'))

                        if len(indiscipline_data) > 0:
                            seat_un_data['indiscipline'] = 'YES'
                            break
                        else:
                            seat_un_data['indiscipline'] = 'NO'
                            break
                    ########################################
                data_values.append(seat_un_data)

            medical_details = get_medical_details(all_student, session_name, {})

            dept_consolidate_data = {}
            for per_app in data_values:
                if 'seat_part__value' in per_app:
                    if per_app['seat_part__value'] in dept_consolidate_data:
                        dept_consolidate_data[per_app['seat_part__value']] = dept_consolidate_data[per_app['seat_part__value']] + 1
                    else:
                        dept_consolidate_data[per_app['seat_part__value']] = 1

                if per_app['uniq_id'] in medical_details:
                    temp_medical_details_list = ", ".join(list(x for x in medical_details[per_app['uniq_id']]))
                    per_app['medical_details'] = temp_medical_details_list
                eligiblity_data = get_student_eligible_seater(per_app['uniq_id'], session_name, {}, session)

                per_app['prefrence_details'] = " => ".join(list(str(x) for x in prefrence_details[per_app['uniq_id']]))

                seater_allowed = []
                hostel_allowed = []
                floor_allowed = []
                for x in eligiblity_data:
                    seater_allowed.append(x['hostel_id__bed_capacity__value'])
                per_app['seater_allowed'] = list(set(seater_allowed))

                per_app['alloted_status'] = 'NOT ALLOTED'
                if 'seat_part__value' in per_app:
                    if per_app['seat_part__value'] is not None:
                        per_app['alloted_status'] = 'ALLOTED'

                if 'current_status' in per_app:
                    if per_app['current_status'] == 'WITHDRAWAL':
                        per_app['alloted_status'] = 'WITHDRAWAL'

            ####### CHANGE BY VRINDA ######
            for k, v in total_seat_capacity_data.items():
                if k not in dept_consolidate_data:
                    dept_consolidate_data[k] = 0
            ###############################
            data = {"application_data": data_values, "dept_consolidate_data": dept_consolidate_data, 'hostel_total_capacity': total_seat_capacity_data, 'total_seat_capacity_data_blocked': total_seat_capacity_data_blocked, 'total_seat_capacity_data_blocked_and_unblocked': total_seat_capacity_data_blocked_and_unblocked}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.PUT_REQUEST(request):
            data = json.loads(request.body)
            if data['eligibility'] == 1:
                qry = HostelStudentAppliction.objects.filter(uniq_id=data['uniq_id']).update(status=data['eligible_status'])
                if qry:
                    return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_METHOD_NOT_ALLOWED)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Allotted_allotted_Student_List_Acc(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_STUDENT_ACCOUNTS, rolesCheck.ROLE_ACCOUNTS]) == statusCodes.STATUS_SUCCESS:
        session_data = get_odd_sem(request.session['Session'])
        session = session_data['session']
        session_name = session_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)

        if requestMethod.GET_REQUEST(request):
            extra_filter = {}
            dept_consolidate_data = {}
            total_seat_capacity_data = {}

            ############################################ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################
            allotment_list = set(HostelSeatAlloted.objects.filter(hostel_part__in=list(request.GET['hostel_id'].split(','))).exclude(status="DELETE").values_list('uniq_id', flat=True))
            ########################### END ############ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################

            seat_alloted_data = list(HostelSeatAlloted.objects.filter(hostel_part__in=list(request.GET['hostel_id'].split(','))).exclude(status="DELETE").values('uniq_id', 'paid_status', 'hostel_part', 'seat_part', 'hostel_part__value', 'seat_part__value', 'rule_used__list_no', 'status').order_by('uniq_id'))

            data_values = []

            prefrence_details = get_seater_prefrence_details(allotment_list, session_name, {})

            medical_details = get_medical_details(allotment_list, session_name, {})

            for seat_data in seat_alloted_data:
                seat_alloted_applicant_data = list(HostelStudentAppliction.objects.filter(uniq_id=seat_data['uniq_id']).exclude(status="DELETE").values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'time_stamp', 'current_status', 'status').order_by('uniq_id'))
                if len(seat_alloted_applicant_data) > 0:
                    app_data = seat_alloted_applicant_data[0]
                else:
                    continue

                app_data['time_stamp'] = ' '.join(str(app_data['time_stamp']).split('T'))
                student_data = []
                student_data = get_student_details(app_data['uniq_id'], session_name, {}, 'odd', session)
                temp_student_dict = {}
                if(len(student_data) > 0):
                    temp_student_dict = student_data[-1]
                    app_data.update(temp_student_dict)
                app_data.update(seat_data)
                app_data['prefrence_details'] = " => ".join(list(str(x) for x in prefrence_details[app_data['uniq_id']]))

                if app_data['uniq_id'] in medical_details:
                    temp_medical_details_list = ", ".join(list(x for x in medical_details[app_data['uniq_id']]))
                    app_data['medical_details'] = temp_medical_details_list

                if 'seat_part__value' in app_data:
                    app_data['alloted_status'] = 'SEAT ALLOTED'
                else:
                    app_data['alloted_status'] = 'NOT ALLOTED'

                if 'current_status' in app_data:
                    if app_data['current_status'] == 'WITHDRAWAL':
                        app_data['alloted_status'] = 'WITHDRAWAL'

                room_detail = HostelRoomAlloted.objects.filter(uniq_id=seat_data['uniq_id']).exclude(status="DELETE").values('room_part', 'room_part__room_no')
                if len(room_detail) > 0:
                    app_data['room_no'] = room_detail[0]['room_part__room_no']
                else:
                    app_data['room_no'] = '---'

                acc_data = acc_get_hostel_component(seat_data['uniq_id'], session)
                app_data.update(acc_data)

                data_values.append(app_data)

            data = {"application_data": data_values}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Allotted_room_allotted_Student_List(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        session_data = get_odd_sem(request.session['Session'])
        session = session_data['session']
        session_name = session_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
        if requestMethod.GET_REQUEST(request):
            extra_filter = {}
            dept_consolidate_data = {}
            total_seat_capacity_data = {}
            ####################################### GET GENDER FOR WHICH THE LIST NEED TO BE SHOWN (FETCH GENDER) #################################################
            temp_gender_array = []
            if academicCoordCheck.isRector(request) == True:
                rector_hostel = get_rector_hostel(emp_id, {}, session)
                for x in rector_hostel:
                    if x['field'] == "BOYS":
                        temp_gender_array.append("MALE")
                    if x['field'] == "GIRLS":
                        temp_gender_array.append("FEMALE")
                temp_gender_array = list(set(temp_gender_array))

            if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS:
                temp_gender_array.append("MALE")
            if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
                temp_gender_array.append("FEMALE")
            ########################### END ############ GET GENDER FOR WHICH THE LIST NEED TO BE SHOWN (FETCH GENDER) ############################################

            ############################################ GET ELIGIBLE STUDENT DATA BRANCHES, YEAR #################################################################
            filter_data = HostelSetting.objects.filter(hostel_id__hostel_id=request.GET['hostel_id']).values('branch', 'year').distinct()

            allotment_list = set()
            applicant_student = set()
            for x in filter_data:
                branch = x['branch']
                year = x['year']
                ############################################ DYNAMIC FILTER DATA FOR UNIQID LISTS #################################################################
                extra_filter_application = {'uniq_id__sem__dept': branch, 'uniq_id__year': year, 'uniq_id__uniq_id__gender__value__in': temp_gender_array}
                ########################### END ############ DYNAMIC FILTER DATA FOR UNIQID LISTS #################################################################
                applicant_student = applicant_student | set(HostelStudentAppliction.objects.filter(**extra_filter_application).exclude(status="DELETE").values_list('uniq_id', flat=True))
            ########################### END ############ GET ELIGIBLE STUDENT DATA BRANCHES, YEAR #################################################################

            ############################################ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################
            extra_filter_allot = {'hostel_part': request.GET['hostel_id']}
            allotment_list = set(HostelSeatAlloted.objects.filter(**extra_filter_allot).exclude(status="DELETE").values_list('uniq_id', flat=True))

            total_seat_capacity_data = get_hostel_capacity(request.GET['hostel_id'], session_name, session)
            ########################### END ############ GET TOTAL CAPACITY OF HOSTEL FOR STUDENT #################################################################

            seat_alloted_applicant = allotment_list.intersection(applicant_student)
            seat_alloted_applicant = list(seat_alloted_applicant)

            all_student = allotment_list | applicant_student
            all_student = list(all_student)

            application_data = list(HostelStudentAppliction.objects.filter(uniq_id__in=seat_alloted_applicant).exclude(status="DELETE").values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'time_stamp', 'current_status', 'status').order_by('uniq_id'))
            seat_alloted_applicant_data = list(HostelSeatAlloted.objects.filter(uniq_id__in=seat_alloted_applicant).exclude(status="DELETE").values('uniq_id', 'hostel_part', 'seat_part', 'hostel_part__value', 'seat_part__value', 'rule_used__list_no', 'paid_status').distinct().order_by('uniq_id'))

            alloted_non_applicant_student = allotment_list.difference(seat_alloted_applicant)
            alloted_non_applicant_student = list(alloted_non_applicant_student)

            seat_alloted_student_data = list(HostelSeatAlloted.objects.filter(uniq_id__in=alloted_non_applicant_student).exclude(status="DELETE").values('uniq_id', 'hostel_part', 'seat_part', 'hostel_part__value', 'seat_part__value', 'rule_used__list_no', 'status').order_by('uniq_id'))

            unalloted_applicant = applicant_student.difference(seat_alloted_applicant)
            unalloted_applicant = list(unalloted_applicant)

            seat_unalloted_applicant_data = list(HostelStudentAppliction.objects.filter(uniq_id__in=unalloted_applicant).exclude(status="DELETE").values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry', 'time_stamp', 'current_status', 'status').order_by('uniq_id'))

            data_values = []

            prefrence_details = get_seater_prefrence_details(applicant_student, session_name, {})

            for app_data, seat_data in zip(application_data, seat_alloted_applicant_data):
                app_data['time_stamp'] = ' '.join(str(app_data['time_stamp']).split('T'))
                student_data = []
                student_data = get_student_details(app_data['uniq_id'], session_name, {}, 'odd', session)
                temp_student_dict = {}
                if(len(student_data) > 0):
                    temp_student_dict = student_data[0]
                    app_data.update(temp_student_dict)
                app_data.update(seat_data)
                app_data['prefrence_details'] = " => ".join(list(str(x) for x in prefrence_details[app_data['uniq_id']]))

                data_values.append(app_data)

            for seat_al_data in seat_alloted_student_data:
                student_data = []
                student_data = get_student_details(seat_al_data['uniq_id'], session_name, {}, 'odd', session)
                temp_student_dict = {}
                if(len(student_data) > 0):
                    temp_student_dict = student_data[0]
                    for x in temp_student_dict:
                        seat_al_data[x] = temp_student_dict[x]
                    # seat_al_data.update(temp_student_dict)
                data_values.append(seat_al_data)

            for seat_un_data in seat_unalloted_applicant_data:
                temp_student_dict = {}
                student_data = []
                student_data = get_student_details(seat_un_data['uniq_id'], session_name, {}, 'odd', session)
                if(len(student_data) > 0):
                    temp_student_dict = student_data[0]
                    for x in temp_student_dict:
                        seat_un_data[x] = temp_student_dict[x]
                    # seat_un_data.update(temp_student_dict)
                seat_un_data['prefrence_details'] = " => ".join(list(str(x) for x in prefrence_details[seat_un_data['uniq_id']]))
                data_values.append(seat_un_data)

            medical_details = get_medical_details(all_student, session_name, {})

            dept_consolidate_data = {}
            for per_app in data_values:
                if 'seat_part__value' in per_app:
                    if per_app['seat_part__value'] in dept_consolidate_data:
                        dept_consolidate_data[per_app['seat_part__value']] = dept_consolidate_data[per_app['seat_part__value']] + 1
                    else:
                        dept_consolidate_data[per_app['seat_part__value']] = 1

                if per_app['uniq_id'] in medical_details:
                    temp_medical_details_list = ", ".join(list(x for x in medical_details[per_app['uniq_id']]))
                    per_app['medical_details'] = temp_medical_details_list
                eligiblity_data = get_student_eligible_seater(per_app['uniq_id'], session_name, {}, session)

                seater_allowed = []
                hostel_allowed = []
                floor_allowed = []
                for x in eligiblity_data:
                    seater_allowed.append(x['hostel_id__bed_capacity__value'])
                per_app['seater_allowed'] = list(set(seater_allowed))

                if 'seat_part__value' in per_app:
                    per_app['alloted_status'] = 'ALLOTED'
                else:
                    per_app['alloted_status'] = 'NOT ALLOTED'

                if 'current_status' in per_app:
                    if per_app['current_status'] == 'WITHDRAWAL':
                        per_app['alloted_status'] = 'WITHDRAWAL'

            data = {"application_data": data_values, "dept_consolidate_data": dept_consolidate_data, 'hostel_total_capacity': total_seat_capacity_data}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.PUT_REQUEST(request):
            data = json.loads(request.body)
            if data['eligibility'] == 1:
                qry = HostelStudentAppliction.objects.filter(uniq_id=data['uniq_id']).update(status=data['eligible_status'])
                if qry:
                    return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_METHOD_NOT_ALLOWED)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Manual_Room_Allotment_Unallotment(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS,rolesCheck.ROLE_LIBRARY_REPORT]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        session_data = get_odd_sem(request.session['Session'])
        session = session_data['session']
        session_name = session_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
        HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
        studentSession = generate_session_table_name('studentSession_', session_name)
        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelRoommatePriority = generate_session_table_name('HostelRoommatePriority_', session_name)
        if requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            uniq_id = data['uniq_id']
            room_id = data['room_id']
            if data['allot'] == 1:
                date = datetime.today().strftime('%Y-%m-%d')
                qry3 = HostelRoomAlloted.objects.filter(uniq_id=uniq_id, status="INSERT").update(status="DELETE")
                qry2 = HostelRoomAlloted.objects.create(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), room_part=HostelRoomSettings.objects.get(id=data['room_id']), date_of_inserted=date, date_of_update=date)
                if qry2:
                    qry3 = HostelRoomSettings.objects.filter(id=data['room_id']).update(allotted_status=F('allotted_status') + 1)
                    qry4 = HostelStudentAppliction.objects.filter(uniq_id=data['uniq_id'], status="INSERT").update(current_status='ROOM ALLOTED')
                    data = statusMessages.CUSTOM_MESSAGE('Successfully Allotted')
                else:
                    data = statusMessages.CUSTOM_MESSAGE('Room Could not be allotted')
                    return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
            else:
                qry2 = HostelRoomAlloted.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').update(status='DELETE')
                qry3 = HostelRoomSettings.objects.filter(id=data['room_id']).update(allotted_status=F('allotted_status') - 1)
                qry4 = HostelStudentAppliction.objects.filter(uniq_id=data['uniq_id'], status="INSERT").update(current_status='SEAT ALLOTED')
                data = statusMessages.CUSTOM_MESSAGE('Successfully unallotted')
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_student_list')):

                hostel_id = request.GET['hostel_id']
                qry1 = list(HostelSeatAlloted.objects.filter(paid_status='ALREADY PAID', hostel_part__sno=hostel_id).exclude(status="DELETE").values('uniq_id', 'hostel_part', 'seat_part', 'hostel_part__value', 'seat_part__value', 'rule_used__list_no', 'paid_status').distinct())

                for q in qry1:
                    qry2 = list(HostelStudentAppliction.objects.filter(uniq_id=q['uniq_id']).exclude(status='DELETE').exclude(current_status="PENDING").exclude(current_status="WITHDRAWAL").values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'current_status', 'attendance_avg', 'uni_marks_obt', 'uni_max_marks', 'carry'))
                    if len(qry2) > 0:
                        q.update(qry2[0])

                    qry3 = get_student_details(q['uniq_id'], session_name, {}, 'odd', session)
                    if len(qry3) > 0:
                        q.update(qry3[0])

                    if 'current_status' in q:
                        if q['current_status'] == 'ROOM ALLOTED':
                            qry4 = list(HostelRoomAlloted.objects.filter(uniq_id=q['uniq_id']).exclude(status='DELETE').exclude(room_part__status="DELETE").values('room_part__room_no', 'room_part__allotted_status', 'room_part__id'))
                            if len(qry4) > 0:
                                q.update(qry4[0])

                    else:
                        q['room_part__room_no'] = None
                        q['room_part__allotted_status'] = 0
                        q['room_part__id'] = None

                    q['roommate_priority'] = ""

                    roommate_pri = list(HostelRoommatePriority.objects.filter(application_id__uniq_id=q[
                        'uniq_id']).exclude(status="DELETE").values('priority', 'uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__sem__dept__dept__value'))
                    if len(roommate_pri) > 0:
                        q['roommate_priority'] = ",".join(list(str(x['uniq_id__uniq_id__name']) + "(" + str(x['uniq_id__sem__dept__dept__value']) + ")" for x in roommate_pri))

                return functions.RESPONSE(qry1, statusCodes.STATUS_SUCCESS)

            elif (requestType.custom_request_type(request.GET, 'get_room_list')):
                data = []
                bed_capacity = request.GET['bed_capacity']
                hostel_id = request.GET['hostel_id']
                room_available = check_empty_room_for_capacity(bed_capacity, hostel_id, session, session_name)
                if room_available == True:
                    qry1 = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, is_blocked=0, room_type__value="STUDENT ROOM", hostel_id__bed_capacity__value=bed_capacity, allotted_status__lt=bed_capacity).exclude(status="DELETE").values('id', 'allotted_status', 'room_no', 'room_type__value', 'hostel_id__floor__value', 'hostel_id__bed_capacity__value', 'hostel_id__hostel_id__value').order_by('room_no'))
                    if len(qry1) > 0:
                        data = qry1
                        return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
                    else:
                        data = statusMessages.CUSTOM_MESSAGE('NO ROOM EMPTY FOR SELECTED BED-CAPACITY')
                        return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                else:
                    data = statusMessages.CUSTOM_MESSAGE('NO ROOM EMPTY FOR SELECTED HOSTEL AND BED-CAPACITY')
                return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
