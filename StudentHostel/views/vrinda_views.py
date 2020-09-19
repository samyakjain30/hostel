# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, F
from datetime import date
from datetime import datetime
import json
import math
from django.db.models import Q, Sum, Count, Max, F
from itertools import groupby

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType

from StudentAcademics.models import *
from Registrar.models import *
from musterroll.models import EmployeePrimdetail, Roles
from StudentHostel.models import *
from StudentSMM.models import *

from login.views import checkpermission, generate_session_table_name
from StudentSMM.views.smm_function_views import check_residential_status
from StudentAcademics.views import *
from StudentHostel.views.hostel_function import *

# Create your views here.


def Hostel_Settings(request):
    data = []
    emp_id = request.session['hash1']
    category = get_hostel_category(emp_id)
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS, rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS:
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        sem_type = request.session['sem_type']

        if (requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET, 'get_year')):
                course = request.GET['course'].split(',')
                data = get_all_year(course, {})

            elif(requestType.custom_request_type(request.GET, 'form_data')):
                if "id" in request.GET:
                    id = request.GET['id'].split(',')
                    HostelSetting.objects.filter(hostel_id__in=id).update(status="DELETE")
                    data = statusMessages.MESSAGE_DELETE
                else:
                    hostel = get_hostel(category, {}, session)
                    bed_capacity = get_seater_type({}, session)
                    floor = get_floor_type({}, session)
                    data.append({'HOSTEL NAME': hostel, 'FLOOR TYPES': floor, 'SEATER TYPE': bed_capacity})

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                qry = get_hostel_category(emp_id)
                hostel = get_hostel(qry, {}, session)
                h_id = []
                for h in hostel:
                    h_id.append(h['sno'])
                query = list(HostelSetting.objects.filter(hostel_id__hostel_id__in=h_id).exclude(status="DELETE").values('hostel_id', 'hostel_id__hostel_id', 'hostel_id__hostel_id__value', 'hostel_id__floor', 'hostel_id__floor__value', 'hostel_id__bed_capacity', 'hostel_id__bed_capacity__value', 'added_by', 'added_by__name').order_by('hostel_id__hostel_id__value', 'hostel_id__floor__value', 'hostel_id__bed_capacity__value').distinct())
                i = 0
                for q in query:
                    data.append({'ID_ID': q['hostel_id'], 'HOSTEL_ID': q['hostel_id__hostel_id'], 'HOSTEL_NAME': q['hostel_id__hostel_id__value'], 'FLOOR_ID': q['hostel_id__floor'], 'FLOOR_NAME': q['hostel_id__floor__value'], 'BED_CAPACITY_ID': q['hostel_id__bed_capacity'], 'BED_CAPACITY_NAME': q['hostel_id__bed_capacity__value'], 'ADDED_BY': q['added_by__name']})

            elif(requestType.custom_request_type(request.GET, 'update')):
                id = request.GET['id']  # id is hostel_id for that row ##################
                data = list(HostelSetting.objects.filter(hostel_id=id).exclude(status="DELETE").values('branch', 'branch__dept__value', 'branch__course', 'branch__course__value', 'year', 'admission_status', 'admission_status__value', 'admission_type', 'admission_type__value', 'added_by', 'added_by__name', 'hostel_id', 'hostel_id__hostel_id', 'hostel_id__hostel_id__value', 'hostel_id__floor', 'hostel_id__floor__value', 'hostel_id__bed_capacity', 'hostel_id__bed_capacity__value'))

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            id = data['id']  # id is hostel_id for that row  and null or new entry ##################
            hostel_id = data['hostel_id']
            floor = data['floor']
            bed_capacity = data['bed_capacity']
            branch = data['branch']
            year = data['year']
            admission_type = data['admission_type']
            admission_status = data['admission_status']
            all_id = []

            if id is not None:
                HostelSetting.objects.filter(hostel_id=id).update(status="DELETE")
                data = statusMessages.MESSAGE_UPDATE

            else:
                data = statusMessages.MESSAGE_INSERT

            ################## HOSTEL DROPDOWN ######################################
            for f in floor:
                for b in bed_capacity:
                    qry_check = list(HostelFlooring.objects.filter(hostel_id=hostel_id, floor=f, bed_capacity=b).exclude(status="DELETE").values_list('id', flat=True))
                    if len(qry_check) == 0:
                        qry = HostelFlooring.objects.create(hostel_id=HostelDropdown.objects.get(sno=hostel_id), floor=HostelDropdown.objects.get(sno=f), bed_capacity=HostelDropdown.objects.get(sno=b), added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))

                        get_id = list(HostelFlooring.objects.filter(hostel_id=hostel_id, floor=f, bed_capacity=b).values_list('id', flat=True))
                        all_id.append(get_id[0])
                    else:
                        all_id.append(qry_check[0])
            #########################################################################

            ############ REGISTRAR DROPDOWN #########################################
            for ids in all_id:
                for b in branch:
                    year_dur = list(CourseDetail.objects.filter(uid=b).values_list('course_duration', flat=True))
                    for y in range(1, int(year_dur[0]) + 1):
                        qry1 = None
                        if y in year:
                            HostelSetting.objects.filter(hostel_id=ids, branch=b, year=y).update(status="DELETE")
                            qry1 = (HostelSetting(hostel_id=HostelFlooring.objects.get(id=ids), branch=CourseDetail.objects.get(uid=b), year=y, admission_type=StudentDropdown.objects.get(sno=add_type), added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), admission_status=StudentDropdown.objects.get(sno=add_status))for add_type in admission_type for add_status in admission_status)

                        if qry1 != None:
                            query1 = HostelSetting.objects.bulk_create(qry1)
            #########################################################################

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Indiscipline_Form(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS, rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        sem_type = request.session['sem_type']
        Session = request.session['Session']

        IncidentApproval = generate_session_table_name("IncidentApproval_", session_name)
        Incident = generate_session_table_name("Incident_", session_name)
        IncidentReporting = generate_session_table_name("IncidentReporting_", session_name)
        studentSession = generate_session_table_name("studentSession_", session_name)

        if (requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET, 'get_year_startend_date')):
                data = get_year_startend_date(request.session['Session_id'])

            elif(requestType.custom_request_type(request.GET, 'get_indiscipline_students')):
                branch = request.GET['branch'].split(',')
                year = request.GET['year'].split(',')
                user = request.GET['user']
                from_date = datetime.strptime(str(request.GET['from_date']).split('T')[0], "%Y-%m-%d").date()
                from_date = from_date + timedelta(days=1)
                to_date = datetime.strptime(str(request.GET['to_date']).split('T')[0], "%Y-%m-%d").date()
                to_date = to_date + timedelta(days=1)
                hostel_stu_li = []
                students_li = []
                gender = get_gender(emp_id)
                student_li = list(studentSession.objects.filter(uniq_id__gender__value=gender[0]['gender__value'], year__in=year, sem__dept__in=branch).exclude(uniq_id__admission_status__value='EX-STUDENT').exclude(uniq_id__admission_status__value='WITHDRAWAL').values_list('uniq_id', flat=True))
                if user == "CHIEF RECTOR":
                    incidents = get_incidents_details(session_name, {'level': 1, 'appoval_status': "APPROVED", 'incident_detail__uniq_id__in': student_li, 'incident_detail__incident__date_of_incident__range': [from_date, to_date]})
                elif user == "RECTOR":
                    ############# RECTOR HOSTEL STUDENTS LIST ##################
                    incidents = get_incidents_details(session_name, {'level': 1, 'appoval_status': "PENDING", 'incident_detail__uniq_id__in': student_li, 'incident_detail__incident__date_of_incident__range': [from_date, to_date]})
                if len(incidents) > 0:
                    for s in incidents:
                        father_mob = list(StudentFamilyDetails.objects.filter(uniq_id=s['incident_detail__uniq_id']).values_list('father_mob', flat=True))
                        s['father_mob'] = father_mob
                    data = incidents

            elif(requestType.custom_request_type(request.GET, 'approve_reject_request')):
                id = request.GET['id']
                approval_status = request.GET['approval_status']
                remark = request.GET['remark']
                user = request.GET['user']

                incident_detail = list(IncidentApproval.objects.filter(id=id).exclude(status="DELETE").values_list('incident_detail', flat=True))
                ########## STATUS=DELETE  FOR HOD/RECTOR REQUEST THOSE ARE PROCESSED #######################
                IncidentApproval.objects.filter(id=id).update(status="DELETE")
                ######################################################################################

                if user == "CHIEF RECTOR":
                    IncidentApproval.objects.create(level=2, remark=remark, appoval_status=approval_status, approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), incident_detail=IncidentReporting.objects.get(id=incident_detail[0]))
                elif user == "RECTOR":
                    IncidentApproval.objects.create(level=1, remark=remark, appoval_status=approval_status, approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), incident_detail=IncidentReporting.objects.get(id=incident_detail[0]))
                data = statusMessages.CUSTOM_MESSAGE('Successfully ' + approval_status)

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                user = request.GET['user']
                gender = get_gender(emp_id)
                key = get_rector_or_chief_rector(emp_id)
                if key != user and key != "BOTH":
                    return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)
                if user == "CHIEF RECTOR":
                    query = get_incidents_details(session_name, {'level': 2, 'appoval_status__in': ["APPROVED", "REJECTED"], 'incident_detail__uniq_id__uniq_id__gender__value': gender[0]['gender__value']})
                elif user == "RECTOR":
                    query = get_incidents_details(session_name, {'level': 1, 'appoval_status__in': ["APPROVED", "REJECTED"], 'incident_detail__uniq_id__uniq_id__gender__value': gender[0]['gender__value']})
                for q in query:
                    role = get_rector_or_chief_rector(q['incident_detail__incident__added_by'])
                    flag = 0
                    if (role == 'CHIEF RECTOR'):
                        q['added_by'] = "CHIEF RECTOR"
                        flag = 1
                    elif (role == 'RECTOR'):
                        q['added_by'] = "RECTOR"
                        flag = 1
                    elif (role == 'BOTH'):
                        q['added_by'] = "CHIEF RECTOR"
                        flag = 1
                    if (flag == 0):
                        q['added_by'] = ""
                for q in query:
                    father_mob = list(StudentFamilyDetails.objects.filter(uniq_id=q['incident_detail__uniq_id__uniq_id']).values_list('father_mob', flat=True))
                    q['father_mob'] = father_mob[0]
                data = query

            elif(requestType.custom_request_type(request.GET, 'roll_back')):
                id = request.GET['id']
                incident_id = list(IncidentApproval.objects.filter(id=id).exclude(status="DELETE").values_list('incident_detail', flat=True))
                IncidentApproval.objects.filter(id=id).update(status="DELETE")
                qry = list(IncidentApproval.objects.filter(incident_detail=incident_id[0], level=-1).exclude(status="DELETE").values('remark', 'appoval_status', 'approved_by'))
                IncidentApproval.objects.filter(incident_detail=incident_id[0], level=-1).update(status="DELETE")
                IncidentApproval.objects.create(incident_detail=IncidentReporting.objects.get(id=incident_id[0]), level=1, remark=qry[0]['remark'], appoval_status=qry[0]['appoval_status'], approved_by=EmployeePrimdetail.objects.get(emp_id=qry[0]['approved_by']))
                data = statusMessages.CUSTOM_MESSAGE('Successfully ROLLED BACK')

            elif(requestType.custom_request_type(request.GET, 'delete')):
                id = request.GET['id']
                IncidentApproval.objects.filter(id=id).update(status="DELETE")
                data = statusMessages.MESSAGE_DELETE

            elif(requestType.custom_request_type(request.GET, 'get_student_list')):
                branch = request.GET['branch'].split(',')
                year = request.GET['year'].split(',')
                user = request.GET['user']
                gender = get_gender(emp_id)
                students_li = list(studentSession.objects.filter(uniq_id__gender__value=gender[0]['gender__value'], year__in=year, sem__dept__in=branch).exclude(uniq_id__admission_status__value='EX-STUDENT').exclude(uniq_id__admission_status__value='WITHDRAWAL').values('uniq_id', 'uniq_id__name', 'uniq_id__uni_roll_no').order_by('uniq_id__name'))
                data = students_li

            elif(requestType.custom_request_type(request.GET, 'get_student_data')):
                uniq_id = request.GET['uniq_id']
                data = get_student_details(uniq_id, session_name, {}, sem_type, session)

            elif(requestType.custom_request_type(request.GET, 'update')):
                id = request.GET['id']
                uniq_id = []
                qry = list(IncidentApproval.objects.filter(id=id).exclude(status="DELETE").values('incident_detail__uniq_id', 'incident_detail__incident__date_of_incident'))
                from_date = datetime.strptime(str(qry[0]['incident_detail__incident__date_of_incident']).split('T')[0], "%Y-%m-%d").date()
                from_date = from_date
                uniq_id.append(qry[0]['incident_detail__uniq_id'])
                to_date = date.today()
                details = get_incidents_details(session_name, {'incident_detail__uniq_id': uniq_id[0], 'incident_detail__incident__date_of_incident__range': [from_date, to_date]})
                details1 = get_student_details(uniq_id[0], session_name, {}, sem_type, session)
                data = ({'data': details, 'stu_details': details1})

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            id = data['id']  # for submit id is none and for update id has the updated row id ################
            uniq_id = data['uniq_id']
            date_of_incident = data['date_of_incident']
            description = data['description']
            incident_document = data['incident_document']
            action = data['action']
            comm_to_parent = data['comm_to_parent']
            student_document = data['student_document']
            remark = data['remark']
            user = data['user']

            if id != None:
                IncidentApproval.objects.filter(id=id).update(status="DELETE")

            Incident.objects.create(date_of_incident=date_of_incident, description=description, incident_document=incident_document, added_by=EmployeePrimdetail.objects.get(emp_id=emp_id))
            qry = list(Incident.objects.filter(date_of_incident=date_of_incident, description=description, incident_document=incident_document, added_by=emp_id).values_list('id', flat=True))
            IncidentReporting.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), incident=Incident.objects.get(id=qry[0]), action=action, comm_to_parent=comm_to_parent, student_document=student_document)
            qry1 = list(IncidentReporting.objects.filter(uniq_id=uniq_id, action=action, comm_to_parent=comm_to_parent, student_document=student_document, incident=qry[0]).exclude(status="DELETE").values_list('id', flat=True))
            if user == "CHIEF RECTOR":
                IncidentApproval.objects.create(level=2, remark=remark, appoval_status="APPROVED", approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), incident_detail=IncidentReporting.objects.get(id=qry1[0]))
            elif user == "RECTOR":
                IncidentApproval.objects.create(level=1, remark=remark, appoval_status="APPROVED", approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), incident_detail=IncidentReporting.objects.get(id=qry1[0]))
            data = {'msg': "Successfully ADDED"}
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Room_Settings(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS, rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        sem_type = request.session['sem_type']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        if (requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                if 'id' in request.GET:  # for delete request ###############################
                    id = request.GET['id'].split(',')
                    HostelRoomSettings.objects.filter(id__in=id).update(status="DELETE")
                    data = statusMessages.MESSAGE_DELETE
                else:
                    Hostel = get_rector_hostel(emp_id, {}, session)
                    Room_type = get_room_type({}, session)
                    data = ({'Hostel': Hostel, 'Room_type': Room_type})

            elif(requestType.custom_request_type(request.GET, 'get_floor')):
                hostel_id = request.GET['hostel_id']
                Floor = get_hostel_floor(hostel_id, {}, session)
                t = -99
                for q in Floor:
                    for n in q['floor__value']:
                        inicial_value = n[0]
                        break
                    t = int(t) + 100
                    t = '{0:03}'.format(t)
                    data.append({'floor': q['floor'], 'floor__value': q['floor__value'], 'inicial_value': inicial_value, 'room_no': t})

            elif(requestType.custom_request_type(request.GET, 'get_bed_capacity')):
                hostel_id = request.GET['hostel_id']
                floor = request.GET['floor']
                bed_capacity = get_hostel_seater_type(hostel_id, floor, {}, session)
                data = bed_capacity

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                hostel_id = request.GET['hostel_id']
                floor = request.GET['floor']
                data = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__floor=floor).exclude(status="DELETE").values('id', 'hostel_id', 'hostel_id__hostel_id', 'hostel_id__hostel_id__value', 'hostel_id__floor', 'hostel_id__floor__value', 'hostel_id__bed_capacity', 'hostel_id__bed_capacity__value', 'room_no', 'room_type', 'is_blocked', 'is_ac', 'added_by', 'added_by__name', 'allotted_status').order_by('room_no'))

            elif(requestType.custom_request_type(request.GET, 'view_previous_all')):
                data1 = []
                if academicCoordCheck.isRector(request) == True:
                    hostel = get_rector_hostel(emp_id, {}, session)
                elif checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS:
                    hostel = get_hostel("BOYS", {}, session)
                elif checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
                    hostel = get_hostel("GIRLS", {}, session)
                # hostel = get_rector_hostel(emp_id,{},8)
                hostel_id = []
                for h in hostel:
                    hostel_id.append(h['sno'])
                for h in hostel_id:
                    hostel_value = list(HostelDropdown.objects.filter(sno=h).exclude(status="DELETE").values('sno', 'value'))
                    floor = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=h).exclude(status="DELETE").values('hostel_id__floor', 'hostel_id__floor__value').distinct().order_by('hostel_id__floor__value'))
                    Floor = []
                    for f in floor:
                        bed_capacity = list(HostelRoomSettings.objects.filter(hostel_id__floor=f['hostel_id__floor'], hostel_id__hostel_id=h).exclude(status="DELETE").values('hostel_id__bed_capacity', 'hostel_id__bed_capacity__value').distinct().order_by('hostel_id__bed_capacity__value'))
                        Bed = []
                        room_total = 0
                        capacity_total = 0
                        for b in bed_capacity:
                            qry = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=h, hostel_id__floor=f['hostel_id__floor'], hostel_id__bed_capacity=b['hostel_id__bed_capacity']).exclude(status="DELETE").values('room_no').distinct())
                            d = {}
                            room_total += int(len(qry))
                            d['rooms'] = len(qry)
                            d['capacity'] = int(b['hostel_id__bed_capacity__value']) * int(len(qry))
                            capacity_total += int(d['capacity'])
                            Bed.append({b['hostel_id__bed_capacity__value']: d})
                        Floor.append({f['hostel_id__floor__value']: Bed, 'room_total': room_total, 'capacity_total': capacity_total})
                    data1.append({hostel_value[0]['value']: Floor})

                data2 = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id__in=hostel_id).exclude(status="DELETE").values('id', 'hostel_id__hostel_id', 'hostel_id__hostel_id__value', 'hostel_id__floor', 'hostel_id__floor__value', 'hostel_id__bed_capacity', 'hostel_id__bed_capacity__value', 'room_no', 'room_type', 'room_type__value', 'is_blocked', 'is_ac', 'added_by', 'added_by__name', 'allotted_status').order_by('hostel_id__floor__value', 'hostel_id__floor__value', 'hostel_id__bed_capacity__value', 'room_no'))
                for x in data2:
                    if x['is_blocked'] == 0:
                        x['is_blocked'] = "NO"
                    else:
                        x['is_blocked'] = "YES"

                    if x['is_ac'] == 0:
                        x['is_ac'] = "NO"
                    else:
                        x['is_ac'] = "YES"

                data = {'data1': data1, 'data2': data2}

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            hostel = data['hostel_id']
            floor = data['floor']
            bed_capacity = data['bed_capacity']
            room = data['room']

            flooring = dict()
            qry = list(HostelFlooring.objects.filter(hostel_id=hostel, floor=floor).exclude(status="DELETE").values('id', 'bed_capacity'))
            for x in qry:
                flooring[x['bed_capacity']] = x['id']
            query_list = []
            ############# CHANGE BY VRINDA ########
            get_all_room_ids = HostelRoomSettings.objects.filter(hostel_id__hostel_id=data['hostel_id'], hostel_id__floor=data['floor'], hostel_id__bed_capacity=data['bed_capacity']).exclude(status="DELETE").values_list('id', flat=True)
            room_ids = []
            room_ids_to_be_delete = set()
            for r in room:
                if 'id' in r:
                    room_ids.append(r['id'])
                    previous_detail = list(HostelRoomSettings.objects.filter(id=r['id']).values())[0]
                    HostelRoomSettings.objects.filter(id=r['id']).update(hostel_id=HostelFlooring.objects.get(id=flooring[r['bed_capacity']]), status="UPDATE", room_no=r['number'], room_type=r['type'], is_blocked=r['is_blocked'], is_ac=r['is_ac'])

                else:
                    status = "INSERT"
                    hostel_id = HostelFlooring.objects.get(id=flooring[r['bed_capacity']])
                    query_list.append({"hostel_id": hostel_id, "room_no": r['number'], "room_type": HostelDropdown.objects.get(sno=r['type']), "is_blocked": r['is_blocked'], "is_ac": r['is_ac'], 'added_by': EmployeePrimdetail.objects.get(emp_id=emp_id), 'status': status})
            room_ids_to_be_delete = set(get_all_room_ids) - set(room_ids)
            HostelRoomSettings.objects.filter(id__in=list(room_ids_to_be_delete)).exclude(status="DELETE").update(status="DELETE")
            #######################################
            # for r in room:
            # 	if 'id' in r:
            # 		previous_detail = list(HostelRoomSettings.objects.filter(id=r['id']).values())[0]
            # 		HostelRoomSettings.objects.filter(id=r['id']).update(hostel_id=HostelFlooring.objects.get(id=flooring[r['bed_capacity']]),status="UPDATE",room_no=r['number'],room_type=r['type'],is_blocked=r['is_blocked'],is_ac=r['is_ac'])

            # 		status = "DELETE"
            # 		hostel_id = HostelFlooring.objects.get(id=previous_detail['hostel_id_id'])
            # 		query_list.append({"hostel_id":hostel_id,"room_no":previous_detail['room_no'],"room_type":HostelDropdown.objects.get(sno=previous_detail['room_type_id']),"is_blocked":previous_detail['is_blocked'],"is_ac":previous_detail['is_ac'],'added_by':EmployeePrimdetail.objects.get(emp_id=previous_detail['added_by_id']),'status':status})
            # 	else:
            # 		status = "INSERT"
            # 		hostel_id = HostelFlooring.objects.get(id=flooring[r['bed_capacity']])
            # 		query_list.append({"hostel_id":hostel_id,"room_no":r['number'],"room_type":HostelDropdown.objects.get(sno=r['type']),"is_blocked":r['is_blocked'],"is_ac":r['is_ac'],'added_by':EmployeePrimdetail.objects.get(emp_id=emp_id),'status':status})

            bulk_query_generator = (HostelRoomSettings(hostel_id=r['hostel_id'], room_no=r['room_no'], room_type=r['room_type'], is_blocked=r['is_blocked'], is_ac=r['is_ac'], status=r['status'], added_by=r['added_by'])for r in query_list)

            query1 = HostelRoomSettings.objects.bulk_create(bulk_query_generator)

            data = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Swapping(request):
    data = []
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS, rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True or academicCoordCheck.isWarden(request) == True:
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        sem_type = request.session['sem_type']
        Session = request.session['Session']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        SwappingReport = generate_session_table_name('SwappingReport_', session_name)
        studentSession = generate_session_table_name('studentSession_', session_name)

        if (requestMethod.GET_REQUEST(request)):
            if(requestType.custom_request_type(request.GET, 'get_rooms')):
                hostel_id = request.GET['hostel_id']
                bed_capacity = request.GET['bed_capacity']


                if 'get_unoccupied_rooms' in request.GET:
                    data=list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__bed_capacity=bed_capacity, room_type__value='STUDENT ROOM', is_blocked=0).exclude(status="DELETE").exclude(allotted_status=F('hostel_id__bed_capacity__value')).values('id', 'room_no', 'hostel_id__floor__value','hostel_id__bed_capacity__value'))
                        
                else:
                    data = list(HostelRoomSettings.objects.filter(hostel_id__hostel_id=hostel_id, hostel_id__bed_capacity=bed_capacity, room_type__value='STUDENT ROOM', is_blocked=0).exclude(status="DELETE").values('id', 'room_no', 'hostel_id__floor__value','hostel_id__bed_capacity__value'))

                for d in data:
                    qry = list(HostelRoomAlloted.objects.filter(room_part=d['id']).exclude(status="DELETE").values('uniq_id', 'uniq_id__uniq_id__name'))
                    d['students'] = []
                    for q in qry:
                        d['students'].append(q['uniq_id__uniq_id__name'])
                    d['room'] = str(d['hostel_id__floor__value'] + "-" + d['room_no']) + " ( " + ",".join(d['students']) + " ) "

            ####SEAT ALLOTED STUDENTS LIST###FOR HOSTEL SWAP######BY YASH###################
            elif(requestType.custom_request_type(request.GET,'get_student_list')):
                hostel_id = request.GET['hostel_id']
                bed_capacity = request.GET['bed_capacity'].split(',')
                data = list(HostelSeatAlloted.objects.filter(hostel_part=hostel_id,seat_part__in=bed_capacity,paid_status="PAID").exclude(status='DELETE').values('uniq_id','uniq_id__uniq_id__name'))
                for d in data:
                    qry=list(HostelRoomAlloted.objects.filter(uniq_id=d['uniq_id']).exclude(status='DELETE').values('room_part__room_no'))
                    if(len(qry)>0):
                        d['room_no']=str(qry[0]['room_part__room_no'])
            ################################################################

            elif(requestType.custom_request_type(request.GET, 'student_swap')):
                student1 = request.GET['stu_1']
                student2 = request.GET['stu_2']
                qry1 = list(HostelRoomAlloted.objects.filter(uniq_id=student1).exclude(status="DELETE").values('room_part'))
                qry2 = list(HostelRoomAlloted.objects.filter(uniq_id=student2).exclude(status="DELETE").values('room_part'))

                HostelRoomAlloted.objects.filter(uniq_id=student1).update(version=F('version') + 1, room_part=qry2[0]['room_part'])
                HostelRoomAlloted.objects.filter(uniq_id=student2).update(version=F('version') + 1, room_part=qry1[0]['room_part'])

                SwappingReport.objects.create(uniq_id=studentSession.objects.get(uniq_id=student1), previous_room=HostelRoomSettings.objects.get(id=qry1[0]['room_part']), current_room=HostelRoomSettings.objects.get(id=qry2[0]['room_part']), type='STUDENT SWAP')
                SwappingReport.objects.create(uniq_id=studentSession.objects.get(uniq_id=student2), previous_room=HostelRoomSettings.objects.get(id=qry2[0]['room_part']), current_room=HostelRoomSettings.objects.get(id=qry1[0]['room_part']), type='STUDENT SWAP')

                data = statusMessages.CUSTOM_MESSAGE('Successfully student swapped')

            elif(requestType.custom_request_type(request.GET, 'room_swap')):
                room_1 = request.GET['room_1']
                room_2 = request.GET['room_2']
                qry1 = list(HostelRoomAlloted.objects.filter(room_part=room_1).exclude(status="DELETE").values_list('uniq_id', flat=True))
                qry2 = list(HostelRoomAlloted.objects.filter(room_part=room_2).exclude(status="DELETE").values_list('uniq_id', flat=True))

                HostelRoomSettings.objects.filter(id__in=[room_1, room_2]).update(allotted_status=0)

                for s1 in qry1:
                    HostelRoomAlloted.objects.filter(uniq_id=s1).update(room_part=HostelRoomSettings.objects.get(id=room_2), version=F('version') + 1)
                    SwappingReport.objects.create(uniq_id=studentSession.objects.get(uniq_id=s1), previous_room=HostelRoomSettings.objects.get(id=room_1), current_room=HostelRoomSettings.objects.get(id=room_2), type='ROOM SWAP')
                    HostelRoomSettings.objects.filter(id=room_2).update(allotted_status=F('allotted_status') + 1)
                for s2 in qry2:
                    HostelRoomAlloted.objects.filter(uniq_id=s2).update(room_part=HostelRoomSettings.objects.get(id=room_1), version=F('version') + 1)
                    SwappingReport.objects.create(uniq_id=studentSession.objects.get(uniq_id=s2), previous_room=HostelRoomSettings.objects.get(id=room_2), current_room=HostelRoomSettings.objects.get(id=room_1), type='ROOM SWAP')
                    HostelRoomSettings.objects.filter(id=room_1).update(allotted_status=F('allotted_status') + 1)


                # Swap Alloted Capacity of Rooms

                data = statusMessages.CUSTOM_MESSAGE('Successfully room swaped')

                       
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)


        elif (requestMethod.POST_REQUEST(request)):
            data = json.loads(request.body)
            to_hostel=data['to_hostel']
            seater=data['seater']
            swap_details=data['swap_details']
            uniq_ids=[]
            room_ids=[]
            query_list_swap=[]
            query_list_seat=[]
            old_room_list=[]
            for swap_detail in swap_details:
                uniq_ids.append(swap_detail['uniq_id'])
                room_ids.append(swap_detail['room_id'])
                room_alloted=list(HostelRoomAlloted.objects.filter(uniq_id=swap_detail['uniq_id']).exclude(status="DELETE").values())
                if len(room_alloted)>0:
                    old_room_list.append(room_alloted[0]['room_part_id'])
                    HostelRoomAlloted.objects.filter(uniq_id=swap_detail['uniq_id']).exclude(status="DELETE").update(room_part=HostelRoomSettings.objects.get(id=swap_detail['room_id']), version=F('version') + 1,date_of_update=datetime.now(),status="UPDATE")
                    query_list_swap.append({'uniq_id':swap_detail['uniq_id'],'previous_room':room_alloted[0]['room_part_id'],'current_room':swap_detail['room_id']})
                
                query_list_seat.append({'uniq_id':swap_detail['uniq_id'],'hostel_part':to_hostel,'seat_part':seater})
                HostelRoomSettings.objects.filter(id=swap_detail['room_id']).exclude(status="DELETE").update(allotted_status=F('allotted_status') + 1)
                
            
            if len(query_list_swap)>0:
                HostelRoomSettings.objects.filter(id__in=old_room_list).exclude(status='DELETE').update(allotted_status=F('allotted_status')-1)
                bulk_create_swap=(SwappingReport(uniq_id=studentSession.objects.get(uniq_id=r['uniq_id']),previous_room=HostelRoomSettings.objects.get(id=r['previous_room']), current_room=HostelRoomSettings.objects.get(id=r['current_room']), type='HOSTEL SWAP')for r in query_list_swap)
                qry=SwappingReport.objects.bulk_create(bulk_create_swap)

            HostelSeatAlloted.objects.filter(uniq_id__in=uniq_ids).exclude(status="DELETE").update(status="DELETE")
            bulk_create_seat=(HostelSeatAlloted(uniq_id=studentSession.objects.get(uniq_id=r['uniq_id']),hostel_part=HostelDropdown.objects.get(sno=r['hostel_part']),seat_part=HostelDropdown.objects.get(sno=r['seat_part']),paid_status='PAID')for r in query_list_seat)
            qry1=HostelSeatAlloted.objects.bulk_create(bulk_create_seat)

            
            

            data = statusMessages.CUSTOM_MESSAGE('Successfully hostel swaped')

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)         

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def ScriptsIndiscipline(request):
    HostelDropdown.objects.filter(session=1).update(status="DELETE")
    qry = list(HostelDropdown.objects.filter(session=8).exclude(status="DELETE").values())
    for q in qry:
        if q['pid'] == 0:
            HostelDropdown.objects.create(field=q['field'], value=q['value'], is_edit=q['is_edit'], is_delete=q['is_delete'], status=q['status'], session=Semtiming.objects.get(sno=7))
        else:
            get_pid = list(HostelDropdown.objects.filter(value=q['field']).exclude(value_isnull=True).values_list('sno', flat=True))
            HostelDropdown.objects.create(field=q['field'], value=q['value'], pid=get_pid[0], is_edit=q['is_edit'], is_delete=q['is_delete'], status=q['status'], session=Semtiming.objects.get(sno=1))

    flooring_data = list(HostelFlooring.objects.filter(hostel_id__session=8).exclude(status="DELETE").values('hostel_id', 'hostel_id__value', 'floor', 'floor__value', 'bed_capacity', 'bed_capacity__value', 'added_by', 'status'))
    for f in flooring_data:
        get_bed = list(HostelDropdown.objects.filter(value=f['bed_capacity__value'], session=1).exclude(value_isnull=True).values_list('sno', flat=True))
        get_floor = list(HostelDropdown.objects.filter(value=f['floor__value'], session=1).exclude(value_isnull=True).values_list('sno', flat=True))
        get_hostel = list(HostelDropdown.objects.filter(value=f['hostel_id__value'], session=1).exclude(value_isnull=True).values_list('sno', flat=True))
        HostelFlooring.objects.create(hostel_id=HostelDropdown.objects.get(sno=get_hostel[0]), floor=HostelDropdown.objects.get(sno=get_floor[0], bed_capacity=HostelDropdown.objects.get(sno=get_bed[0]), added_by=EmployeePrimdetail.objects.get(emp_id=q['added_by'])))

    hostel_data = list(HostelSetting.objects.filter(hostel_id__hostel_id__session=8).exclude(status="DELETE").values('hostel_id', 'hostel_id__hostel_id__value', 'hostel_id__floor__value', 'hostel_id__bed_capacity__value', 'branch', 'year', 'admission_status', 'admission_status__value', 'admission_type', 'admission_type__value', 'added_by', 'status'))
    for h in hostel_data:
        get_hostel = list(HostelDropdown.objects.filter(value=h['hostel_id__hostel_id__value'], session=1).exclude(values_isnull=True).values_list('sno', flat=True))
        get_flooring_id = list(HostelFlooring.objects.filter(hostel_id__value=h['hostel_id__hostel_id__value'], hostel_id__session=1, floor__value=h['hostel_id__floor__value'], bed_capacity__value=h['hostel_id__bed_capacity__value']).exclude(status="DELETE").values_list('sno', flat=True))
        HostelSetting.objects.create(hostel_id=HostelFlooring.objects.get(sno=get_flooring_id[0]), branch=CourseDetail.objects.get(sno=h['branch']), year=h['year'], admission_status=StudentDropdown.objects.get(sno=h['admission_status']), admission_type=StudentDropdown.objects.get(sno=h['admission_type']), added_by=EmployeePrimdetail.objects.get(sno=h['added_by']), status=h['status'])
    return True
