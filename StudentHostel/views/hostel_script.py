
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from datetime import date, datetime, time
import json
from itertools import groupby
import os
import csv
import sys
from django.db.models import Q, Sum, F, Value, CharField


from StudentMMS.constants_functions import requestType
from StudentHostel.constants_functions import requestBy
from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentHostel.constants_variables import lock_type

from StudentAccounts.models import SubmitFee
from Registrar.models import *
from StudentHostel.models import *
from musterroll.models import EmployeePerdetail, Roles
from login.models import EmployeePrimdetail

from StudentAcademics.views import get_organization, get_department
from StudentHostel.views.hostel_function import *
from login.views import checkpermission, generate_session_table_name
# Create your views here.

def check_vacany(check_capacity, vacant_seats):
    if check_capacity == -1:
        for capacity in vacant_seats:
            if vacant_seats[capacity] > 0:
                return True
        return False
    else:
        if check_capacity in vacant_seats:
            if vacant_seats[check_capacity] > 0:
                return True
            return False
        else:
            return False


def Allot_Seat(emp_id, session, session_name, hostel_id):
    if int(session_name[:2]) < 19:
        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

    valid_session = []
    sessions = list(Semtiming.objects.values('session', 'session_name'))
    for s in sessions:
        if int(s['session_name'][:2]) >= 18:
            valid_session.append(s['session_name'])
    data_set = []
    bed_data = []
    data_values = []
    rules_detail = []
    student_alloted = []
    student_alloted_set = set()
    student_left = []
    student_left_set = set()
    exclusive_case = []
    exclusive_case_set = set()
    student_application_list = []

    previous_session_name = str(int(
        session_name[:2]) - 1) + str(int(session_name[2:4]) - 1) + str(session_name[-1:])

    HostelSeatAllotSetting = generate_session_table_name(
        'HostelSeatAllotSetting_', session_name)
    HostelSeatAllotMulti = generate_session_table_name(
        'HostelSeatAllotMulti_', session_name)
    HostelSeaterPriority = generate_session_table_name(
        'HostelSeaterPriority_', session_name)
    HostelSeatAlloted = generate_session_table_name(
        'HostelSeatAlloted_', session_name)
    studentSession = generate_session_table_name(
        'studentSession_', session_name)
    HostelStudentAppliction = generate_session_table_name(
        'HostelStudentAppliction_', session_name)

    hostel = hostel_id
    gender = get_gender(emp_id)

    vacant_seats = get_hostel_occupied_un_capacity(
        hostel, session_name, session)
    data_set = get_seat_allotment_rule_view_list_data(hostel, session_name)
    no_of_priority = len(data_set)

    branch_set = set()
    year_set = set()

    for x in range(0, no_of_priority):

        no_of_sub_priority = len(data_set[x]['priority_set'])

        ############################### TAKE -1 SUB_PRIORITY TO LAST ##########
        counter = 0
        while(data_set[x]['priority_set'][0]['sub_priority'] < 0 and counter < no_of_sub_priority):
            counter = +1
            if no_of_sub_priority > 1 and data_set[x]['priority_set'][0]['sub_priority'] == -1:
                data_set[x]['priority_set'].append(
                    data_set[x]['priority_set'][0])
                data_set[x]['priority_set'].pop(0)
        ############# END ############# TAKE -1 SUB_PRIORITY TO LAST ##########

        for y in range(0, no_of_sub_priority):
            for rule in data_set[x]['priority_set'][y]['sub_priority_set']:
                branch_set.add(rule['branch'])
                year_set.add(rule['year'])
                rule['medical_case'] = HostelSeatAllotMulti.objects.filter(seat_setting=rule['id'], criteria_type="MEDICAL CATEGORY").values_list('criteria_value', flat=True)
            rules_detail.extend(data_set[x]['priority_set'][
                                y]['sub_priority_set'])

    branch_list = list(branch_set)
    year_list = list(year_set)

    student_data = seat_allotment_student_view_list(
        branch_list, year_list, None, None, None, None, None, None, gender[0]["gender__value"], session_name)
    # print(student_data,'student_data')

    flag_student_left_to_allot = 1
    rule_wise_allotment_record = {}
    student_priority_counter = 0
    for student in student_data:
        check_already = list(HostelStudentAppliction.objects.filter(
            status="INSERT", uniq_id=student['uniq_id'], current_status="PENDING").values())
        if len(check_already) == 0:
            continue

        # medical_details = get_uniq_id_medical_details(student['uniq_id'], session_name, {})
        medical_details = get_uniq_id_medical_details(
            student['uniq_id'], session_name, {})
        ############################### CHECK CAPACITY LEFT IN HOSTEL OR NOT ##
        if not check_vacany(-1, vacant_seats):
            break
        else:
            pass
        ############# END ############# CHECK CAPACITY LEFT IN HOSTEL OR NOT ##

        incident_details = get_incidents_details(previous_session_name, {
                                                 'incident_detail__uniq_id': student['uniq_id'], 'level': 2, 'appoval_status': "APPROVED"})

        for student_priority in student['uniq_id_set']:
            if 'allotement_status' in student:
                break

            # print(check_vacany(student_priority['seater__value'], vacant_seats))
            if not check_vacany(student_priority['seater__value'], vacant_seats):
                continue
            else:
                pass

            for rule_index, rule in enumerate(rules_detail):
                # DEFINE THE LIST OF CAPACITY ACC
                if str(rule['priority']) + "DATA" + str(rule['sub_priority']) not in rule_wise_allotment_record:
                    rule_wise_allotment_record[
                        str(rule['priority']) + "DATA" + str(rule['sub_priority'])] = {}
                    rule_wise_allotment_record[
                        str(rule['priority']) + "DATA" + str(rule['sub_priority'])]['filled'] = 0
                    if rule['seat_part__value'] is not None:
                        rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(
                            rule['sub_priority'])]['seat_part__value'] = rule['seat_part__value']
                    else:
                        pass
                    if rule['room_max'] is not None:
                        rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(
                            rule['sub_priority'])]['room_max'] = int(rule['room_max'])
                    else:
                        pass
                    if rule['room_min'] is not None:
                        rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(
                            rule['sub_priority'])]['room_min'] = int(rule['room_min'])
                    else:
                        pass
                else:
                    pass
                # END ############# DEFINE THE LIST OF CAPACITY ACC

                # CHECK IS BED LEFT ACC TO THIS R
                if rule['branch'] == student_priority['branch'] and rule['year'] == student_priority['year']:
                    pass
                else:
                    continue
                # END ############# CHECK IS BED LEFT ACC TO THIS R

                # CHECK IS BED LEFT ACC TO THIS R
                if 'room_max' in rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])]:
                    if rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])]['filled'] >= rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])]['room_max']:
                        continue
                    else:
                        pass
                else:
                    pass
                # END ############# CHECK IS BED LEFT ACC TO THIS R

                # CHECK IS SEATER LEFT ACC TO THI
                if 'seat_part__value' in rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])]:
                    if not check_vacany(rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])]['seat_part__value'], vacant_seats):
                        continue
                    else:
                        pass
                else:
                    pass
                # END ############# CHECK IS SEATER LEFT ACC TO THI

                # CHECK IS SEATER LEFT ACC TO THI
                if not check_vacany(student_priority['seater__value'], vacant_seats):
                    continue
                else:
                    pass
                # END ############# CHECK IS SEATER LEFT ACC TO THI

                # CHECK IF STUDENT HAVE CARRY ACC
                if rule['carry_max'] is not None:
                    if rule['carry_min'] is not None:
                        if student_priority['carry'] > rule['carry_max'] or student_priority['carry'] < rule['carry_min']:
                            continue
                        else:
                            pass
                    else:
                        if student_priority['carry'] > rule['carry_max']:
                            continue
                        else:
                            pass
                else:
                    if rule['carry_min'] is not None:
                        if student_priority['carry'] < rule['carry_min']:
                            continue
                        else:
                            pass
                    else:
                        pass
                # END ############# CHECK IF STUDENT HAVE CARRY ACC

                # CHECK IF STUDENT HAVE UNI_MARK
                if student_priority['uni_per'] is not None:
                    if rule['uni_max'] is not None:
                        if rule['uni_min'] is not None:
                            if student_priority['uni_per'] > rule['uni_max'] or student_priority['uni_per'] < rule['uni_min']:
                                continue
                            else:
                                pass
                        else:
                            if student_priority['uni_per'] > rule['uni_max']:
                                continue
                            else:
                                pass
                    else:
                        if rule['uni_min'] is not None:
                            if student_priority['uni_per'] < rule['uni_min']:
                                continue
                            else:
                                pass
                        else:
                            pass
                else:
                    pass
                # END ############# CHECK IF STUDENT HAVE UNI_MARK

                # CHECK IF STUDENT HAVE ATTENTANC
                if student_priority['attendance_avg'] is not None:
                    if rule['att_max'] is not None:
                        if rule['att_min'] is not None:
                            if student_priority['attendance_avg'] > rule['att_max'] or student_priority['attendance_avg'] < rule['att_min']:
                                continue
                            else:
                                pass
                        else:
                            if student_priority['attendance_avg'] > rule['att_max']:
                                continue
                            else:
                                pass
                    else:
                        if rule['att_min'] is not None:
                            if student_priority['attendance_avg'] < rule['att_min']:
                                continue
                            else:
                                pass
                        else:
                            pass
                else:
                    pass
                # END ############# CHECK IF STUDENT HAVE ATTENTANC

                # CHECK IF STUDENT HAVE MEDICAL C
                if len(medical_details) > 0:
                    if medical_details[0]['student_medical__medical_category_id'] not in rule['medical_case']:
                        continue
                    else:
                        pass
                else:
                    pass
                # END ############# CHECK IF RULE HAVE MEDICAL CASE

                # CHECK IF STUDENT HAVE MEDICAL C
                if len(rule['medical_case']) > 0:
                    if len(medical_details) <= 0:
                        continue
                    else:
                        pass
                else:
                    pass
                # END ############# CHECK IF RULE HAVE MEDICAL CASE

                # CHECK IF STUDENT HAVE INDISCIPL
                if rule['indiscipline'] != 1:
                    if len(incident_details) > 0:
                        continue
                    else:
                        pass
                else:
                    pass
                # END ############# CHECK IF STUDENT HAVE INDISCIPL

                ################### ALSO FOR LIST_NO DO SOMETHING  checks######
                if student_priority['seater'] == rule['seat_part'] or rule['seat_part'] is None:
                    student_alloted.append({'rule_used': HostelSeatAllotSetting.objects.get(id=rule['id']), 'seat_part': HostelDropdown.objects.get(sno=student_priority[
                                           'seater']), 'hostel_part': HostelDropdown.objects.get(sno=rule['hostel_part']), 'uniq_id': studentSession.objects.get(uniq_id=student['uniq_id'])})
                    student_alloted_set.add(student['uniq_id'])
                    student_application_list.append(student_priority)

                    vacant_seats[student_priority['seater__value']] = vacant_seats[
                        student_priority['seater__value']] - 1

                    rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])][
                        'filled'] = rule_wise_allotment_record[str(rule['priority']) + "DATA" + str(rule['sub_priority'])]['filled'] + 1

                    student['allotement_status'] = "ALLOTED"

                    break

                else:
                    pass
        exclusive_case_set.add(student['uniq_id'])

    bulk_query = (HostelSeatAlloted(rule_used=student['rule_used'], uniq_id=student['uniq_id'], seat_part=student[
                  'seat_part'], hostel_part=student['hostel_part'], status="TEMP") for student in student_alloted)
    HostelSeatAlloted.objects.bulk_create(bulk_query)

    query = list(HostelSeatAlloted.objects.filter(hostel_part=hostel, uniq_id__in=list(student_alloted_set), status="TEMP").exclude(status='DELETE').values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'uniq_id__uniq_id__name', 'seat_part', 'seat_part__value', 'hostel_part', 'hostel_part__value', 'uniq_id__year', 'uniq_id__sem__dept', 'uniq_id__sem__dept__dept', 'uniq_id__sem__dept__course', 'uniq_id__sem__dept__dept__value', 'uniq_id__sem__dept__course__value', 'rule_used').order_by('uniq_id').distinct())

    HostelSeatAlloted.objects.filter(status="TEMP").delete()

    prefrence_details = get_seater_prefrence_details(
        list(student_alloted_set), session_name, {})

    # medical_details = get_medical_details(list(student_alloted_set), session_name, {})
    medical_details = get_medical_details(
        list(student_alloted_set), session_name, {})

    for seat_un_data, application in zip(query, student_application_list):
        temp_student_dict = {}
        student_data = []

        student_data = get_student_details(
            seat_un_data['uniq_id'], session_name, {}, 'odd', session)
        if(len(student_data) > 0):
            temp_student_dict = student_data[0]
            for x in temp_student_dict:
                seat_un_data[x] = temp_student_dict[x]
            ########## Indiscipline details #################
            for s in valid_session:
                IncidentApproval = generate_session_table_name(
                    'IncidentApproval_', s)
                indiscipline_data = list(IncidentApproval.objects.filter(incident_detail__uniq_id=seat_un_data[
                                         'uniq_id'], level=2, appoval_status='APPROVED').exclude(status="DELETE").values('incident_detail'))

                if len(indiscipline_data) > 0:
                    seat_un_data['indiscipline'] = 'YES'
                    break
                else:
                    seat_un_data['indiscipline'] = 'NO'
                    break
            #################################################

        app_deatils = HostelStudentAppliction.objects.filter(uniq_id=seat_un_data['uniq_id']).exclude(
            current_status='SEAT ALLOTED').exclude(status='DELETE').values()
        for x in app_deatils[0]:
            seat_un_data[x] = app_deatils[0][x]

        seat_un_data['prefrence_details'] = " => ".join(
            list(str(x) for x in prefrence_details[seat_un_data['uniq_id']]))
        if seat_un_data['uniq_id'] in medical_details:
            temp_medical_details_list = ", ".join(
                list(x for x in medical_details[seat_un_data['uniq_id']]))
            seat_un_data['medical_details'] = temp_medical_details_list
    return [query, vacant_seats]

def Allot_Room(emp_id, session, session_name, hostel_id):
    if int(session_name[:2]) < 19:
        return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

    valid_session = []
    sessions = list(Semtiming.objects.values('session', 'session_name'))
    for s in sessions:
        if int(s['session_name'][:2]) >= 18:
            valid_session.append(s['session_name'])

    data_set = []
    branch_set = set()
    year_set = set()
    rules_detail = []
    gender = get_gender(emp_id)
    r_id = []
    uniq_id_r_id_dict = {}
    student_alloted = []
    student_alloted_set = set()
    alloted_set = {}
    pending_uniq_id = {}
    no_priority = set()
    student_data_set = set()

    HostelRoomAllotSetting = generate_session_table_name(
        'HostelRoomAllotSetting_', session_name)
    HostelRoomAllotMulti = generate_session_table_name(
        'HostelRoomAllotMulti_', session_name)
    HostelRoommatePriority = generate_session_table_name(
        'HostelRoommatePriority_', session_name)
    HostelSeatAlloted = generate_session_table_name(
        'HostelSeatAlloted_', session_name)
    HostelRoomAlloted = generate_session_table_name(
        'HostelRoomAlloted_', session_name)
    studentSession = generate_session_table_name(
        'studentSession_', session_name)
    HostelStudentAppliction = generate_session_table_name(
        'HostelStudentAppliction_', session_name)

    previous_session_name = str(int(
        session_name[:2]) - 1) + str(int(session_name[2:4]) - 1) + str(session_name[-1:])

    vacant_rooms = get_room_occupied_un_capacity(
        hostel_id, session_name, session)

    ############################### CREATE RULES DATA ####################
    data_set = get_room_allotment_rule_view_list_data(hostel_id, session_name)

    no_of_priority = len(data_set)

    for x in range(0, no_of_priority):

        no_of_sub_priority = len(data_set[x]['priority_set'])
        ############################### TAKE -1 SUB_PRIORITY TO LAST ##########
        counter = 0
        while(data_set[x]['priority_set'][0]['sub_priority'] < 0 and counter < no_of_sub_priority):
            counter = +1
            if no_of_sub_priority > 1 and data_set[x]['priority_set'][0]['sub_priority'] == -1:
                data_set[x]['priority_set'].append(
                    data_set[x]['priority_set'][0])
                data_set[x]['priority_set'].pop(0)

        ############# END ############# TAKE -1 SUB_PRIORITY TO LAST ##########
        
        for y in range(0, no_of_sub_priority):
            for rule in data_set[x]['priority_set'][y]['sub_priority_set']:
                rules_detail = rules_detail + rule['floor_set']

    ################### END ######## CREATE RULES DATA ####################
    year_set=set(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel_id, list_no__isnull=True).exclude(status='DELETE').values_list('year', flat=True).distinct())

    branch_set=set(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel_id, list_no__isnull=True).exclude(status='DELETE').values_list('branch', flat=True).distinct())

    branch_list = list(branch_set)
    year_list = list(year_set)
    rule_wise_allotment_record = {}

    room_data = get_totat_rooms_id(hostel_id, session_name)

    total = 0
    total_query = 0

    data_storage = {}
    primary_rule_parsed = []
    not_alloted = set()
    go_to_rule = 0

    for sub_rule_index, sub_rule in enumerate(rules_detail):
        ######################################## CHECH RULE WISE DATA #######################
        check_key = str(sub_rule['priority']) + " DATA " + str(sub_rule['sub_priority'])
        if check_key not in rule_wise_allotment_record:
            rule_wise_allotment_record[check_key] = {}
            rule_wise_allotment_record[check_key]['filled'] = 0
            if sub_rule['room_max'] is not None:
                rule_wise_allotment_record[check_key]['room_max'] = int(sub_rule['room_max'])
            else:
                pass


    for rule_index, rule in enumerate(rules_detail):

        if rule['priority'] in primary_rule_parsed:
            continue

        primary_rule_parsed.append(rule['priority'])

        store_key = str(rule['medical']) + str(rule['course_preference'])
        if store_key not in data_storage:
            extra_filter = {"medical": rule['medical'], "course_preference": rule['course_preference']}
            data_storage[store_key] = room_allotment_student_view_list(hostel_id, branch_list, year_list, gender[0]["gender__value"], session_name, session, extra_filter)
            # print(data_storage[store_key])

        student_data = data_storage[store_key]

        total = len(student_data)

        if len(student_data) == 0:
            continue

        for student in student_data:
            print(student)
            ######################### PICKING STUDENT ONE BY ONE #########################
            if str(student['uniq_id']) in list(student_alloted_set):
                continue

            check_already = list(HostelStudentAppliction.objects.filter(
                status="INSERT", uniq_id=student['uniq_id'], current_status="ROOM ALLOTED").values())

            if len(check_already) > 0:
                continue

            ##################################### CHECK CAPACITY LEFT IN HOSTEL OR NO ##################
            if not check_vacany(-1, vacant_rooms):
                break
            else:
                pass
            ################### END ############# CHECK CAPACITY LEFT IN HOSTEL OR NO ##################

            incident_details = get_incidents_details(previous_session_name, {
                                                     'incident_detail__uniq_id': student['uniq_id'], 'level': 2, 'appoval_status': "APPROVED"})

            ######################################### CHECK FOR EMPTY ROOM ##############################

            if not check_empty_room_for_capacity(student['seater'], hostel_id, session, session_name):
                continue
            else:
                pass
            ################## END ################## CHECK FOR EMPTY ROOM ##############################

            for sub_rule_index, sub_rule in enumerate(rules_detail):
                if sub_rule['priority'] not in primary_rule_parsed:
                    break

                room_uniq_id = []

                ######################################## CHECH RULE WISE DATA #######################
                check_key = str(sub_rule['priority']) + " DATA " + str(sub_rule['sub_priority'])
                ################ END ################### CHECH RULE WISE DATA #######################

                ######################################## CHECK ROOM MAX-MIN #########################
                if 'room_max' in rule_wise_allotment_record[check_key]:
                    if rule_wise_allotment_record[check_key]['filled'] >= rule_wise_allotment_record[check_key]['room_max']:
                        continue
                    else:
                        pass
                else:
                    pass
                ################## END ################# CHECK ROOM MAX-MIN #########################
                ######################################### CHECK FOR EMPTY ROOM ##############################
                # return
                if student['seater'] != sub_rule['hostel_part__bed_capacity__value']:
                    continue
                else:
                    pass

                ################## END ################## CHECK FOR EMPTY ROOM ##############################
                              ################################ CHECK IS SEATER LEFT ACC TO THIS STUDENT #########################
                if not check_vacany(student['seater'], vacant_rooms):
                    continue
                else:
                    pass
                ############## END ############# CHECK IS SEATER LEFT ACC TO THIS STUDENT #########################

                ############## CHECK IF STUDENT HAVE CARRY ACC TO MAX-CARRY ##################################
                if sub_rule['carry_max'] is not None:
                    if sub_rule['carry_min'] is not None:
                        if student['carry'] > sub_rule['carry_max'] or student['carry'] < sub_rule['carry_min']:
                            continue
                        else:
                            pass
                    else:
                        if student['carry'] > sub_rule['carry_max']:
                            continue
                        else:
                            pass
                else:
                    if sub_rule['carry_min'] is not None:
                        if student['carry'] < sub_rule['carry_min']:
                            continue
                        else:
                            pass
                    else:
                        pass
                ############## END ############# CHECK IF STUDENT HAVE CARRY ACC TO MAX-CARRY ################

                ################### CHECK IF STUDENT HAVE UNI_MARK ACC TO UNI_PERCENTAGE ##########################

                ###################### CHECK IF STUDENT HAVE UNI_MARK ACC TO UNI_PERCENTAGE ##########################
                if student['branch'] == sub_rule['branch'] and student['year'] == sub_rule['year']:
                    pass
                else:
                    continue
                ############## END #### CHECK IF STUDENT HAVE UNI_MARK ACC TO UNI_PERCENTAGE ########
                
                ############## CHECK IF STUDENT HAVE UNI_MARK ACC TO UNI_PERCENTAGE ##########################
                if student['uni_per'] is not None:
                    if sub_rule['uni_max'] is not None:
                        if sub_rule['uni_min'] is not None:
                            if student['uni_per'] > sub_rule['uni_max'] or student['uni_per'] < sub_rule['uni_min']:
                                continue
                            else:
                                pass
                        else:
                            if student['uni_per'] > sub_rule['uni_max']:
                                continue
                            else:
                                pass
                    else:
                        if sub_rule['uni_min'] is not None:
                            if student['uni_per'] < sub_rule['uni_min']:
                                continue
                            else:
                                pass
                        else:
                            pass
                else:
                    pass
                ############## END ############# CHECK IF STUDENT HAVE UNI_MARK ACC TO UNI_PERCENTAGE ########

                ################################ CHECK IF STUDENT HAVE ATTENTANCE ACC TO ATT-AVG #############
                if student['attendance_avg'] is not None:
                    if sub_rule['att_max'] is not None:
                        if sub_rule['att_min'] is not None:
                            if student['attendance_avg'] > sub_rule['att_max'] or student['attendance_avg'] < sub_rule['att_min']:
                                continue
                            else:
                                pass
                        else:
                            if student['attendance_avg'] > sub_rule['att_max']:
                                continue
                            else:
                                pass
                    else:
                        if sub_rule['att_min'] is not None:
                            if student['attendance_avg'] < sub_rule['att_min']:
                                continue
                            else:
                                pass
                        else:
                            pass
                else:
                    pass
                ############## END ############# CHECK IF STUDENT HAVE ATTENTANCE ACC TO ATT-AVG #############
                
                ################################ CHECK IS SEATER LEFT ACC TO THIS RULE ######################
                temp_roommate_data = list(student['roommate'].split(", "))
                if "" in temp_roommate_data:
                    temp_roommate_data.remove("")
                final_roommate_data = []
                
                if temp_roommate_data is not None:

                    for roommate_uniq_id in temp_roommate_data:
                        if roommate_uniq_id in student_alloted_set or roommate_uniq_id == '':
                            continue
                        
                        is_alloted = list(HostelStudentAppliction.objects.filter(uniq_id=roommate_uniq_id, current_status="ROOM ALLOTED").exclude(status="DELETE").values_list('id', flat=True))
                        is_entry = list(HostelSeatAlloted.objects.filter(uniq_id=roommate_uniq_id, hostel_part=hostel_id, paid_status="ALREADY PAID").exclude(status="DELETE").values_list('id', flat=True))

                        if len(is_alloted) > 0 or len(is_entry) == 0:
                            continue
                        else:
                            final_roommate_data.append(roommate_uniq_id)

                final_roommate_data.append(str(student['uniq_id']))

                allot_room_id = -1

                capacity = student['seater']
                floor = sub_rule['hostel_part__floor__value']
                print(capacity, floor)
                if capacity in room_data:
                    if floor in room_data[capacity]:
                        temp_room_list = room_data[capacity][floor]
                        for room_index, room in enumerate(temp_room_list):
                            room = temp_room_list[room_index]
                            room_id, room_capacity = list(room.items())[0]
                            if room_capacity == 0:
                                continue
                            len_roommate = len(final_roommate_data)        
                            if room_capacity >= len_roommate:
                                allot_room_id = room_id
                                temp_room_list[room_index][room_id] = temp_room_list[room_index][room_id] - len_roommate
                                room_data[capacity][floor] = temp_room_list
                                break
                        if allot_room_id == -1:
                            continue
                        else:
                            pass
                    else:
                        continue
                else:
                    continue

                ############## END ############# CHECK IS SEATER LEFT ACC TO THIS RULE #######################
                if len(final_roommate_data) <= 0:
                    continue

                for uniq_id in final_roommate_data:
                    student_alloted_set.add(uniq_id)
                    rule_wise_allotment_record[check_key]['filled'] += 1
                    student_alloted.append({"rule_used":  sub_rule['id'],"uniq_id":  uniq_id,"room_part":  allot_room_id})
                break
            ############# END ####### PICKING STUDENT ONE BY ONE #########################

    HostelRoomAlloted.objects.filter(status="TEMP").delete()
    bulk_query = (HostelRoomAlloted(rule_used=HostelRoomAllotSetting_1920o.objects.get(id = student['rule_used']), uniq_id=studentSession.objects.get(uniq_id = student['uniq_id']), room_part=HostelRoomSettings.objects.get(id = student['room_part']), status="TEMP") for student in student_alloted)
    HostelRoomAlloted.objects.bulk_create(bulk_query)
    query_list = list(HostelRoomAlloted.objects.filter(uniq_id__in=list(student_alloted_set), status="TEMP").exclude(status='DELETE').values_list('uniq_id', flat=True))
    query = list(HostelRoomAlloted.objects.filter(uniq_id__in=list(student_alloted_set), status="TEMP").exclude(status='DELETE').values('uniq_id', 'uniq_id__uniq_id__dept_detail__dept__value', 'uniq_id__uniq_id__name', 'room_part', 'room_part__hostel_id__hostel_id', 'room_part__hostel_id__hostel_id__value', 'room_part__hostel_id__bed_capacity', 'room_part__hostel_id__bed_capacity__value', 'uniq_id__year', 'uniq_id__sem__dept', 'uniq_id__sem__dept__dept', 'uniq_id__sem__dept__course', 'uniq_id__sem__dept__dept__value', 'uniq_id__sem__dept__course__value', 'rule_used', 'room_part__room_no', 'room_part__hostel_id__floor', 'room_part__hostel_id__floor__value').order_by('room_part__room_no', 'uniq_id').distinct())
    medical_details = get_medical_details(
        list(query_list), session_name, {})

    for q in query:

        if q['uniq_id'] in medical_details:
            temp_medical_details_list = ", ".join(
                list(x for x in medical_details[q['uniq_id']]))
            q['medical_details'] = temp_medical_details_list

        app_details = HostelStudentAppliction.objects.filter(uniq_id=q['uniq_id']).exclude(
            current_status='ROOM ALLOTED').exclude(status='DELETE').values()
        if len(app_details)>0:
            for x in app_details[0]:
                q[x] = app_details[0][x]

        student_data = get_student_details(
            q['uniq_id'], session_name, {}, 'odd', session)

        if(len(student_data) > 0):
            temp_student_dict = student_data[0]

            for x in temp_student_dict:
                q[x] = temp_student_dict[x]
            ########## Indiscipline details #################

            for s in valid_session:
                IncidentApproval = generate_session_table_name(
                    'IncidentApproval_', s)
                indiscipline_data = list(IncidentApproval.objects.filter(incident_detail__uniq_id=q[
                                         'uniq_id'], level=2, appoval_status='APPROVED').exclude(status="DELETE").values('incident_detail'))

                if len(indiscipline_data) > 0:
                    q['indiscipline'] = 'YES'
                    break
                else:
                    q['indiscipline'] = 'NO'
                    break

        roommate_pri = list(HostelRoommatePriority.objects.filter(application_id__uniq_id=q[
            'uniq_id']).exclude(status="DELETE").values('priority', 'uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__sem__dept__dept__value'))
        if len(roommate_pri)>0:
            q['roommate_priority'] = ",".join(list(str(x['uniq_id__uniq_id__name']) + "(" + str(x['uniq_id__sem__dept__dept__value']) + ")" for x in roommate_pri))

    HostelRoomAlloted.objects.filter(status="TEMP").delete()

    return query
