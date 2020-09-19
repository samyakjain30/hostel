
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse

from django.shortcuts import render
from datetime import date, datetime, time
import json
from itertools import groupby
import os
import csv
import copy
from django.db.models import Q, Sum, F, Value, CharField

from erp.constants_variables import statusCodes, statusMessages, rolesCheck
from erp.constants_functions import academicCoordCheck, requestByCheck, functions, requestMethod
from StudentMMS.constants_functions import requestType
from StudentHostel.constants_functions import requestBy

from Registrar.models import *
from StudentHostel.models import *
from StudentHostel.constants_variables import lock_type
from musterroll.models import EmployeePerdetail, Roles
from StudentAcademics.views import get_organization, get_department
from login.models import EmployeePrimdetail
from StudentAccounts.models import SubmitFee

from StudentHostel.views.hostel_function import *
from StudentHostel.views.hostel_script import *
from login.views import checkpermission, generate_session_table_name

# Create your views here.


def Hostel_dropdown(request):
    data = {}
    qry1 = ""

    if 'HTTP_COOKIE' in request.META:
        if request.user.is_authenticated:
            check = checkpermission(request, [404, 1353])
            if check == 200:
                session_name = request.session['Session_name']
                if request.method == 'GET':
                    session = request.session['Session_id']

                    if request.GET['request_type'] == 'general':
                        qry1 = HostelDropdown.objects.filter(value=None, session=session).extra(select={'fd': 'field', 'id': 'sno', 'parent': 'pid'}).values('fd', 'id', 'parent').exclude(status="DELETE").distinct()
                        for field1 in qry1:
                            if field1['parent'] != 0:
                                pid = field1['parent']
                                qry2 = HostelDropdown.objects.filter(sno=pid, session=session).exclude(status="DELETE").values('field')
                                field1['fd'] = field1['fd'] + '(' + qry2[0]['field'] + ')'
                        msg = "Success"
                        error = False
                        if not qry1:
                            msg = "No Data Found!!"
                        status = 200
                        data = {'msg': msg, 'data': list(qry1)}

                    elif request.GET['request_type'] == 'subcategory':
                        sno = request.GET['Sno']
                        names = HostelDropdown.objects.filter(sno=sno, session=session).exclude(status="DELETE").values('field', 'pid')
                        name = names[0]['field']
                        p_id = names[0]['pid']

                        qry1 = HostelDropdown.objects.filter(field=name, pid=p_id, session=session).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'valueid': 'sno', 'parentId': 'pid', 'cat': 'field', 'text1': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('valueid', 'parentId', 'cat', 'text1', 'edit', 'delete')
                        for x in range(0, len(qry1)):
                            test = HostelDropdown.objects.filter(pid=qry1[x]['valueid'], session=session).exclude(status="DELETE").exclude(value__isnull=True).extra(select={'subid': 'sno', 'subvalue': 'value', 'edit': 'is_edit', 'delete': 'is_delete'}).values('subid', 'subvalue', 'edit', 'delete')
                            qry1[x]['subcategory'] = list(test)
                        msg = "Success"
                        data = {'msg': msg, 'data': list(qry1)}
                        status = 200

                elif request.method == 'DELETE':
                    session = request.session['Session_id']
                    data = json.loads(request.body)

                    qry = HostelDropdown.objects.filter(sno=data['del_id'], session=session).exclude(status="DELETE").values('field')
                    if(qry.exists()):

                        sno = data['del_id']
                        fd = qry[0]['field']
                        deletec(sno, session)
                        q2 = HostelDropdown.objects.filter(field=fd, session=session).exclude(status="DELETE").exclude(value__isnull=True).values().count()
                        if q2 == 0:
                            q3 = HostelDropdown.objects.filter(field=fd, session=session).exclude(status="DELETE").update(status="DELETE")
                        msg = "Data Successfully Deleted..."
                        status = 200
                    else:
                        msg = "Data Not Found!"
                        status = 404
                    data = {'msg': msg}
                    status = 200
                elif request.method == 'POST':
                    body1 = json.loads(request.body)
                    session = request.session['Session_id']

                    for body in body1:
                        pid = body['parentid']
                        value = body['val'].upper()
                        field_id = body['cat']
                        field_qry = HostelDropdown.objects.filter(sno=field_id, session=session).exclude(status="DELETE").values('field')
                        field = field_qry[0]['field']
                        if pid != 0:
                            field_qry = HostelDropdown.objects.filter(sno=pid, session=session).exclude(status="DELETE").exclude(value__isnull=True).values('value')
                            field = field_qry[0]['value']
                            cnt = HostelDropdown.objects.filter(field=field, session=session).exclude(status="DELETE").values('sno')
                            if len(cnt) == 0:
                                add = HostelDropdown.objects.create(pid=pid, field=field, session=Semtiming.objects.get(uid=session))

                        qry_ch = HostelDropdown.objects.filter(Q(field=field) & Q(value=value)).filter(pid=pid, session=session).exclude(status="DELETE")
                        if(len(qry_ch) > 0):
                            status = 409

                        else:
                            created = HostelDropdown.objects.create(pid=pid, field=field, value=value, session=Semtiming.objects.get(uid=session))
                            msg = "Successfully Inserted"
                            data = {'msg': msg}
                            status = 200

                elif request.method == 'PUT':
                    session = request.session['Session_id']
                    body = json.loads(request.body)
                    sno = body['sno1']
                    val = body['val'].upper()
                    field_qry = HostelDropdown.objects.filter(sno=sno, session=session).exclude(status="DELETE").values('pid', 'value')
                    pid = field_qry[0]['pid']
                    value = field_qry[0]['value']
                    add = HostelDropdown.objects.filter(pid=pid, field=value, session=session).exclude(status="DELETE").update(field=val)
                    add = HostelDropdown.objects.filter(sno=sno, session=session).exclude(status="DELETE").update(value=val, status="UPDATE")
                    add = HostelDropdown.objects.filter(pid=sno, session=session).exclude(status="DELETE").update(field=val, status="UPDATE")
                    msg = "Successfully Updated"
                    data = {'msg': msg}
                    status = 200

            else:
                status = 403
        else:
            status = 401
    else:
        status = 400
    return JsonResponse(status=status, data=data)


def deletec(pid, session):
    qry = HostelDropdown.objects.filter(pid=pid, session=session).exclude(status="DELETE").values('sno')
    if len(qry) > 0:
        for x in qry:
            deletec(x['sno'], session)
    qry = HostelDropdown.objects.filter(sno=pid, session=session).exclude(status="DELETE").update(status="DELETE")


def Assign_Employee_Settings(request):
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
        data = []
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        sem_type = request.session['sem_type']

        if requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            added_by = request.session['hash1']
            hostel_id = data['hostel_id']
            emp_id = data['emp_id']
            type_of_duty = data['type_of_duty']

            qr = list(HostelAssignEmp.objects.filter(hostel_id=hostel_id, type_of_duty=type_of_duty).exclude(status='DELETE').values('id'))
            if qr:
                length = len(qr)
                for x in range(0, length):
                    qr1 = HostelAssignEmp.objects.filter(id=qr[x]['id']).update(status='DELETE')

            objs = (HostelAssignEmp(hostel_id=HostelDropdown.objects.get(sno=hostel_id), emp_id=EmployeePrimdetail.objects.get(emp_id=emp), type_of_duty=HostelDropdown.objects.get(sno=type_of_duty), added_by=EmployeePrimdetail.objects.get(emp_id=added_by))for emp in emp_id)
            qry = HostelAssignEmp.objects.bulk_create(objs)

            return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'view_previous')):
                emp_id = request.session['hash1']
                qry = get_gender(emp_id)
                if qry[0]['gender__value'] == 'MALE':
                    category = 'BOYS'
                else:
                    category = 'GIRLS'
                extra_filter = {'hostel_id__field': category}
                qry = get_hostel_emp_details(extra_filter, session)
                data = []
                for q in qry:
                    data.append({'Employee_Name': q['emp_id__name'], 'Employee_Id': q['emp_id'], 'Hostel_Name': q['hostel_id__value'], 'Duty_Assigned': q['type_of_duty__value'], 'Employee_Department': q['emp_id__dept__value'], 'Employee_Mobile_Number_1': q['emp_id__mob'], 'Employee_Mobile_Number_2': q['emp_id__mob1'], 'Employee_Email': q['emp_id__email']})

            elif(requestType.custom_request_type(request.GET, 'view_previous_hostel_emp')):
                hostel_id = request.GET['hostel_id']
                type_of_duty = request.GET['type_of_duty']
                data = []
                org = get_organization()
                for x in org:
                    dept = get_department(x['sno'])
                    for y in dept:
                        extra_filter = {'hostel_id': hostel_id, 'type_of_duty': type_of_duty, 'emp_id__dept': y['sno']}
                        qry = get_hostel_emp_details(extra_filter, session)
                        data_values = []
                        if qry:
                            for q in qry:
                                data_values.append({'Employee_Name': q['emp_id__name'], 'Employee_Id': q['emp_id'], 'Hostel_Name': q['hostel_id__value'], 'Duty_Assigned': q['type_of_duty__value'], 'Employee_Department': q['emp_id__dept__value'], 'Employee_Mobile_Number_1': q['emp_id__mob'], 'Employee_Mobile_Number_2': q['emp_id__mob1'], 'Employee_Email': q['emp_id__email'], 'Employee_Type_Key': q['emp_id__emp_type'], 'Employee_Category_Key': q['emp_id__emp_category'], 'Employee_Designation_Key': q['emp_id__desg'], 'Employee_Type': q['emp_id__emp_type__value'], 'Employee_Category': q['emp_id__emp_category__value'], 'Employee_Designation': q['emp_id__desg__value'], 'Employee_Organization_Key': q['emp_id__organization'], 'Employee_Organization': q['emp_id__organization__value']})
                            data.append({'dept': y, 'data': data_values})

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_BAD_REQUEST)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_UNAUTHORIZED)


def getComponents(request):
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS, rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_STUDENT_ACCOUNTS,rolesCheck.ROLE_LIBRARY_REPORT]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        emp_id = request.session['hash1']

        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']

        if requestMethod.GET_REQUEST(request):
            data = {}
            if requestType.custom_request_type(request.GET, 'get_gender'):
                data = get_gender_type()

            elif(requestType.custom_request_type(request.GET, 'get_hostel')):
                emp_id = request.session['hash1']
                qry = get_gender(emp_id)
                if qry[0]['gender__value'] == 'MALE':
                    category = 'BOYS'
                else:
                    category = 'GIRLS'
                data = get_hostel(category, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_all_hostel')):
                category = 'GIRLS'
                data = get_hostel(category, {}, session)
                category = 'BOYS'
                temp_data = get_hostel(category, {}, session)
                for x in temp_data:
                    data.append(x)

            elif(requestType.custom_request_type(request.GET, 'get_rector_hostel')):
                # print("academicCoordCheck.isRector(request)",academicCoordCheck.isRector(request))
                if academicCoordCheck.isRector(request) == True:
                    data = get_rector_hostel(emp_id, {}, session)
                elif checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS:
                    data = get_hostel("BOYS", {}, session)
                elif checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
                    data = get_hostel("GIRLS", {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_employee')):
                data = get_employee(request.GET['category'].split(','), request.GET['dept'].split(','), {})

            elif(requestType.custom_request_type(request.GET, 'emp_category')):
                data = get_emp_category({}, session)

            elif(requestType.custom_request_type(request.GET, 'get_course')):
                emp_id = request.session['hash1']
                qry = get_gender(emp_id)
                if qry[0]['gender__value'] == 'MALE':
                    category = 'BOYS'
                else:
                    category = 'GIRLS'

                hostel = get_hostel(category, {}, session)
                hostel_id = []
                for h in hostel:
                    hostel_id.append(h['sno'])
                data = get_course(hostel_id, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_rector_course')):
                emp_id = request.session['hash1']
                hostel = get_rector_hostel(emp_id, {}, session)
                hostel_id = []
                for h in hostel:
                    hostel_id.append(h['sno'])
                data = get_rector_course(hostel_id, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_rector_branch')):
                emp_id = request.session['hash1']
                hostel = get_rector_hostel(emp_id, {}, session)
                hostel_id = []
                for h in hostel:
                    hostel_id.append(h['sno'])
                course = request.GET['course'].split(',')
                data = get_rector_branch(hostel_id, course, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_rector_year')):
                emp_id = request.session['hash1']
                hostel = get_rector_hostel(emp_id, {}, session)
                hostel_id = []
                for h in hostel:
                    hostel_id.append(h['sno'])
                course = request.GET['course'].split(',')
                data = get_rector_year(hostel_id, course, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_branch')):
                hid = []
                emp_id = request.session['hash1']
                course = request.GET['course'].split(',')
                user = request.GET['user']
                if user == 'RECTOR':
                    hostel_id = get_rector_hostel(emp_id, {}, session)
                elif user == 'CHIEF RECTOR':
                    category = get_hostel_category(emp_id)
                    hostel_id = get_hostel(category, {}, session)
                for h in hostel_id:
                    hid.append(h['sno'])
                data = get_branch(hid, course, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_year')):
                course = request.GET['course'].split(',')
                data = get_all_year(course, {})

            elif(requestType.custom_request_type(request.GET, 'get_hostel_year')):
                branch = request.GET['branch'].split(',')
                emp_id = request.session['hash1']
                hid = []
                user = request.GET['user']
                if user == 'CHIEF RECTOR':
                    category = get_hostel_category(emp_id)
                    hostel_id = get_hostel(category, {}, session)
                elif user == 'RECTOR':
                    hostel_id = get_rector_hostel(emp_id, {}, session)
                for h in hostel_id:
                    hid.append(h['sno'])
                data = get_hostel_year(hid, branch, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_hostel_student_list')):
                emp_id = request.session['hash1']
                qry = get_gender(emp_id)
                course = request.GET['course'].split(',')
                branch = request.GET['branch'].split(',')
                year = request.GET['year'].split(',')
                extra_filter = {'uniq_id__gender__value': qry[0]['gender__value'], 'year__in': year, 'sem__dept__course__in': course, 'sem__dept__dept__in': branch}
                data = get_hostel_student_list(extra_filter, session_name)

            elif(requestType.custom_request_type(request.GET, 'get_medical_category')):
                data = get_medical_category({}, session)

            elif(requestType.custom_request_type(request.GET, 'get_medical_cases')):
                data = get_medical_cases({}, session)

            elif(requestType.custom_request_type(request.GET, 'get_student_physically_disabled')):
                uniq_id = request.GET['uniq_id']
                extra_filter = {'uniq_id': uniq_id}
                data = get_student_physically_disabled(extra_filter)

            elif(requestType.custom_request_type(request.GET, 'get_bed_capacity')):
                hostel = request.GET['hostel_id']
                data = get_bed_capacity(hostel, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_hostel_floor')):
                hostel = request.GET['hostel_id']
                data = get_hostel_floor(hostel, {}, session)

            elif(requestType.custom_request_type(request.GET, 'get_number_of_student_room')):
                hostel = request.GET['hostel_id']
                bed_capacity_id = request.GET['bed_capacity']
                bed_capacity = HostelDropdown.objects.filter(sno=bed_capacity_id).values('value')
                temp_data = get_hostel_occupied_un_capacity(hostel, session_name, session)
                if len(bed_capacity) > 0:
                    data = temp_data[bed_capacity[0]['value']]

            elif(requestType.custom_request_type(request.GET, 'get_hostel_seater_students')):
                hostel_id = request.GET['hostel_id']
                bed_capacity = request.GET['bed_capacity']
                data = get_hostel_seater_students(hostel_id, bed_capacity, {}, session_name)

            elif(requestType.custom_request_type(request.GET,'get_hostel_occupied_un_capacity')):
                hostel = request.GET['hostel_id']
                data = get_hostel_occupied_un_capacity(hostel, session_name, session)

            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def medical_form(request):
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_GIRLS, rolesCheck.ROLE_CHIEF_RECTOR_BOYS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']

        if requestMethod.POST_REQUEST(request):

            HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
            HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)
            HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
            HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)

            data = json.loads(request.body)
            uniq_id = data['uniq_id']
            medical_category = data['medical_category']
            if 'document' in data:
                document = data['document']
            emp_id = request.session['hash1']
            # key = get_rector_or_chief_rector(emp_id)
            user = data['user']

            if user == 'CHIEF RECTOR':
                level = 2
            elif user == 'RECTOR':
                level = 1

            if 'medical_cases' in data:
                medical_cases = data['medical_cases']
                length = len(medical_cases)
            else:
                length = 1

            qr1 = HostelStudentMedical.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').update(status='DELETE')
            qr2 = HostelMedicalCases.objects.filter(student_medical__uniq_id=uniq_id).exclude(status='DELETE').update(status='DELETE')
            qr3 = HostelMedicalApproval.objects.filter(student_medical__uniq_id=uniq_id).exclude(status='DELETE').update(status='DELETE')

            if 'document' in data:
                qry1 = HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), document=document, session=Semtiming.objects.get(uid=session), added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), medical_category=HostelDropdown.objects.get(sno=medical_category))
            else:
                qry1 = HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), session=Semtiming.objects.get(uid=session), added_by=EmployeePrimdetail.objects.get(emp_id=emp_id), medical_category=HostelDropdown.objects.get(sno=medical_category))
            for x in range(0, length):
                if 'medical_cases' in data:
                    qry2 = HostelMedicalCases.objects.create(student_medical=HostelStudentMedical.objects.get(id=qry1.id), cases=HostelDropdown.objects.get(sno=medical_cases[x]))
                else:
                    qry2 = HostelMedicalCases.objects.create(student_medical=HostelStudentMedical.objects.get(id=qry1.id))
            qry3 = HostelMedicalApproval.objects.create(student_medical=HostelStudentMedical.objects.get(id=qry1.id), approved_by=EmployeePrimdetail.objects.get(emp_id=emp_id), level=level, approval_status='APPROVED')

            return functions.RESPONSE(statusMessages.MESSAGE_SUCCESS, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'view_previous')):

                HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
                HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
                HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)

                emp_id = request.session['hash1']

                user = request.GET['user']
                key = get_rector_or_chief_rector(emp_id)
                if key != user and key != "BOTH":
                    return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)

                if user == 'CHIEF RECTOR':
                    editable = 2
                elif user == 'RECTOR':
                    editable = 1

                qry = get_gender(emp_id)
                if editable == 2:
                    qry1 = list(HostelStudentMedical.objects.filter(uniq_id__uniq_id__gender__value=qry[0]['gender__value']).exclude(status='DELETE').values('medical_category', 'medical_category__value', 'document', 'uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__lib', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__sem__dept__course', 'uniq_id__sem__dept__course__value', 'uniq_id__sem__dept__dept', 'uniq_id__sem__dept__dept__value', 'uniq_id__year', 'id', 'added_by', 'added_by__name'))

                elif editable == 1:
                    # WHAT IS THIS???!!!!!!----------------------------------------------------------
                    hostel = get_rector_hostel(emp_id, {}, session)
                    hostel_id = []
                    for h in hostel:
                        hostel_id.append(h['sno'])
                    course_id = get_rector_course(hostel_id, {}, session)
                    course = []
                    for c in course_id:
                        course.append(c['branch__course'])
                    branch_id = get_rector_branch(hostel_id, course, {}, session)
                    branch = []
                    for b in branch_id:
                        branch.append(b['branch__dept'])
                    year_id = get_rector_year(hostel_id, course, {}, session)
                    year = []
                    for y in year_id:
                        year.append(y['year'])

                    extra_filter = {'uniq_id__gender__value': qry[0]['gender__value'], 'year__in': year, 'sem__dept__course__in': course, 'sem__dept__dept__in': branch}
                    stu = get_hostel_student_list(extra_filter, session_name)
                    stu_list = []
                    for st in stu:
                        stu_list.append(st['uniq_id'])

                    qry1 = list(HostelStudentMedical.objects.filter(uniq_id__in=stu_list).exclude(status='DELETE').values('medical_category', 'medical_category__value', 'document', 'uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__lib', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__sem__dept__course', 'uniq_id__sem__dept__course__value', 'uniq_id__sem__dept__dept', 'uniq_id__sem__dept__dept__value', 'uniq_id__year', 'id', 'added_by', 'added_by__name'))

                length = len(qry1)
                data = []

                for x in range(0, length):
                    qry3 = list(HostelMedicalApproval.objects.filter(student_medical=qry1[x]['id'], student_medical__uniq_id=qry1[x]['uniq_id']).exclude(status='DELETE').values('approval_status', 'approved_by', 'approved_by__name', 'id', 'level').distinct())

                    extra_filter = {'uniq_id': qry1[x]['uniq_id']}

                    qry2 = list(get_student_physically_disabled(extra_filter))

                    qry = list(HostelMedicalCases.objects.filter(student_medical=qry1[x]['id'], student_medical__uniq_id=qry1[x]['uniq_id']).exclude(status='DELETE').values('cases', 'cases__value').distinct())

                    data.append({'student_data': qry1[x], 'cases': qry, 'physically_disabled': qry2, 'approval_status': qry3, 'emp_id': emp_id, 'editable': editable})

                ########################### FIRST SEND PENDING STATUS THEN APPROVED AND REJECTED STATUS ########################

                length = len(data)
                pen_index = []
                oth_index = []
                for x in range(0, length):
                    if data[x]['approval_status'] == []:
                        pen_index.append(x)
                        # pass
                    elif data[x]['approval_status'][0]['approval_status'] == 'PENDING':
                        pen_index.append(x)
                    else:
                        oth_index.append(x)

                data_values = []
                all_index = pen_index + oth_index

                length = len(all_index)

                for x in range(0, length):
                    c = all_index[x]
                    data_values.append(data[c])

                #################################################################################################################

                return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

            if(requestType.custom_request_type(request.GET, 'view_previous_medical_case')):
                data = []

                HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
                HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
                HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)

                uniq_id = request.GET['uniq_id']

                qry1 = list(HostelStudentMedical.objects.filter(uniq_id=uniq_id).exclude(status='DELETE').values('medical_category', 'medical_category__value', 'document'))

                qry2 = list(HostelMedicalCases.objects.filter(student_medical__uniq_id=uniq_id).exclude(status='DELETE').values('cases', 'cases__value'))

                if qry1:
                    data.append({'medical_category': qry1[0]['medical_category'], 'medical_category_value': qry1[0]['medical_category__value'], 'document': qry1[0]['document'], 'medical_cases': qry2})

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

        elif requestMethod.PUT_REQUEST(request):
            data = json.loads(request.body)
            approved_by = request.session['hash1']
            HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
            HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
            HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
            HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)
            length_data = len(data)

            for i in range(0, length_data):
                id = data[i]['id']
                uniq_id = data[i]['uniq_id']
                status_key = data[i]['key']
                emp_id = request.session['hash1']

                user = data[i]['user']

                if user == 'CHIEF RECTOR':
                    level = 2
                elif user == 'RECTOR':
                    level = 1

                medical_category = data[i]['medical_category']
                if 'medical_cases' in data[i]:
                    medical_cases = data[i]['medical_cases']
                    length = len(medical_cases)
                else:
                    length = 1
                if 'document' in data[i]:
                    document = data[i]['document']

                ############################## CHECK IF REQUEST IS TO APPROVE AND REJECT OR EDIT ###########################

                if 'edit' in data[i]:
                    edit = data[i]['edit']
                else:
                    edit = ""

                ############################################################################################################

                ########################### CHECK IF FORM IS ADDED BY EMPLOYEE OR STUDENT###################################

                if 'added_by' in data[i]:
                    added_by = data[i]['added_by']
                else:
                    added_by = ""

                ############################################################################################################

                HostelStudentMedical.objects.filter(id=id).update(status='DELETE')
                HostelMedicalCases.objects.filter(student_medical__id=id).update(status='DELETE')
                HostelMedicalApproval.objects.filter(student_medical__id=id).update(status='DELETE')

                ############################# IF ADDED_BY == 'S' THEN STUDENT HAS ENTERED THE DATA #########################

                if added_by == 'S':
                    if 'document' in data[i]:
                        qry1 = HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), document=document, session=Semtiming.objects.get(uid=session), medical_category=HostelDropdown.objects.get(sno=medical_category), status='UPDATE')
                    else:
                        qry1 = HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), session=Semtiming.objects.get(uid=session), medical_category=HostelDropdown.objects.get(sno=medical_category), status='UPDATE')
                else:
                    if 'document' in data[i]:
                        qry1 = HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), document=document, session=Semtiming.objects.get(uid=session), added_by=EmployeePrimdetail.objects.get(emp_id=added_by), medical_category=HostelDropdown.objects.get(sno=medical_category), status='UPDATE')
                    else:
                        qry1 = HostelStudentMedical.objects.create(uniq_id=studentSession.objects.get(uniq_id=uniq_id), session=Semtiming.objects.get(uid=session), added_by=EmployeePrimdetail.objects.get(emp_id=added_by), medical_category=HostelDropdown.objects.get(sno=medical_category), status='UPDATE')

                for x in range(0, length):
                    if 'medical_cases' in data[i]:
                        qry2 = HostelMedicalCases.objects.create(student_medical=HostelStudentMedical.objects.get(id=qry1.id), cases=HostelDropdown.objects.get(sno=medical_cases[x]), status='UPDATE')
                    else:
                        qry2 = HostelMedicalCases.objects.create(student_medical=HostelStudentMedical.objects.get(id=qry1.id), status='UPDATE')

                qry3 = HostelMedicalApproval.objects.create(student_medical=HostelStudentMedical.objects.get(id=qry1.id), approved_by=EmployeePrimdetail.objects.get(emp_id=approved_by), level=level, approval_status=status_key, status='UPDATE')

            if status_key == 'APPROVED' and edit == "":
                return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Approved Successfully'), statusCodes.STATUS_SUCCESS)

            elif status_key == 'REJECTED' and edit == "":
                return functions.RESPONSE(statusMessages.CUSTOM_MESSAGE('Rejected Successfully'), statusCodes.STATUS_SUCCESS)

            elif edit == 'UPDATE':
                return functions.RESPONSE(statusMessages.MESSAGE_UPDATE, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            data = json.loads(request.body)
            id = data['id']

            HostelMedicalApproval = generate_session_table_name('HostelMedicalApproval_', session_name)
            HostelStudentMedical = generate_session_table_name('HostelStudentMedical_', session_name)
            HostelMedicalCases = generate_session_table_name('HostelMedicalCases_', session_name)

            HostelStudentMedical.objects.filter(id=id).update(status='DELETE')
            HostelMedicalCases.objects.filter(student_medical__id=id).update(status='DELETE')
            HostelMedicalApproval.objects.filter(student_medical__id=id).update(status='DELETE')

            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.METHOD_NOT_ALLOWED, statusCodes.MESSAGE_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def LockingUnlocking(request):
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS:
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        if requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'form_data')):
                unlock_type = []
                unlock_type.append(lock_type.S)
                unlock_type.append(lock_type.F)
                unlock_type.append(lock_type.R)
                unlock_type.append(lock_type.G)

                return functions.RESPONSE(unlock_type, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                HostelLockingUnlockingStatus = generate_session_table_name('HostelLockingUnlockingStatus_', session_name)

                emp_id = request.session['hash1']
                qry = get_gender(emp_id)
                q_view_previous = HostelLockingUnlockingStatus.objects.filter(uniq_id__uniq_id__gender__value=qry[0]['gender__value']).values('uniq_id', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__gender__value', 'uniq_id__uniq_id__gender', 'LockingUnlocking__lock_type', 'LockingUnlocking__att_date_from', 'LockingUnlocking__att_date_to', 'LockingUnlocking__unlock_from', 'LockingUnlocking__unlock_to', 'LockingUnlocking__time_stamp', 'uniq_id__sem__dept__dept', 'uniq_id__sem__dept__dept__value', 'uniq_id__sem__dept__course', 'uniq_id__sem__dept__course__value', 'uniq_id__sem__sem', 'uniq_id__sem__sem_id', 'uniq_id__section__section_id', 'uniq_id__section__section', 'uniq_id__uniq_id__uni_roll_no').order_by('-LockingUnlocking__time_stamp', 'uniq_id__uniq_id__name')

                for q in q_view_previous:
                    q['LockingUnlocking__lock_type'] = get_lock_type_for_lock_code(q['LockingUnlocking__lock_type'])

                return functions.RESPONSE(list(q_view_previous), statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):

            HostelLockingUnlocking = generate_session_table_name('HostelLockingUnlocking_', session_name)
            HostelLockingUnlockingStatus = generate_session_table_name('HostelLockingUnlockingStatus_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)

            data = json.loads(request.body)
            unlock_type = data['unlock_type']
            unlock_to = datetime.strptime(str(data['unlock_to']), "%Y-%m-%d %H:%M:%S")
            unlock_from = datetime.strptime(str(data['unlock_from']), "%Y-%m-%d %H:%M:%S")
            uniq_id = data['uniq_id']

            length_uniq_id = len(uniq_id)

            for x in range(0, length_uniq_id):
                qr = HostelLockingUnlockingStatus.objects.filter(uniq_id=uniq_id[x], LockingUnlocking__lock_type=unlock_type).exclude(status='DELETE').update(status='DELETE')

            qry1 = HostelLockingUnlocking.objects.create(session=Semtiming.objects.get(uid=session), lock_type=unlock_type, unlock_from=unlock_from, unlock_to=unlock_to)

            objs = (HostelLockingUnlockingStatus(LockingUnlocking=HostelLockingUnlocking.objects.get(id=qry1.id), uniq_id=studentSession.objects.get(uniq_id=uniq_id[x]))for x in range(0, length_uniq_id))

            qry2 = HostelLockingUnlockingStatus.objects.bulk_create(objs)

            return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)

        else:
            return functions.RESPONSE(statusMessages.METHOD_NOT_ALLOWED, statusCodes.MESSAGE_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Seat_Allotment_Rule(request):
    if academicCoordCheck.isRector(request):
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        emp_id = request.session['hash1']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        if requestMethod.PUT_REQUEST(request):
            HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
            HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
            HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)

            data = json.loads(request.body)
            student_list = []
            for x in data:
                student_list.append(x['uniq_id'])
            bulk_query = (HostelSeatAlloted(rule_used=HostelSeatAllotSetting.objects.get(id=x['rule_used']), uniq_id=studentSession.objects.get(uniq_id=x['uniq_id']), seat_part=HostelDropdown.objects.get(sno=x['seat_part']), hostel_part=HostelDropdown.objects.get(sno=x['hostel_part']),) for x in data)
            HostelSeatAlloted.objects.bulk_create(bulk_query)

            HostelStudentAppliction.objects.filter(uniq_id__in=student_list, status="INSERT").update(current_status='SEAT ALLOTED')

            if len(data) > 0:
                list_no = HostelSeatAllotSetting.objects.filter(hostel_part=data[0]['hostel_part']).exclude(list_no__isnull=True).exclude(status="DELETE").values_list('list_no', flat=True).order_by('-list_no')
                if len(list_no) > 0:
                    list_no = int(list_no[0]) + 1
                else:
                    list_no = 1
                if len(data) > 0:
                    HostelSeatAllotSetting.objects.filter(hostel_part=data[0]['hostel_part'], list_no__isnull=True).update(list_no=list_no)

            return functions.RESPONSE(statusMessages.MESSAGE_INSERT, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
            HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
            HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)

            data = json.loads(request.body)
            list_no = data['list_no']
            hostel_id = data['hostel_id']

            rules_list = list(HostelSeatAllotSetting.objects.filter(hostel_part=hostel_id, list_no=list_no).values_list('id', flat=True))
            student_list = list(HostelSeatAlloted.objects.filter(rule_used__in=rules_list).values_list('uniq_id', flat=True))

            HostelStudentAppliction.objects.filter(uniq_id__in=student_list, current_status="SEAT ALLOTED").exclude(status='DELETE').update(current_status="PENDING")
            HostelSeatAlloted.objects.filter(rule_used__in=rules_list).update(status="DELETE")
            HostelSeatAllotSetting.objects.filter(id__in=rules_list).update(status="DELETE")

            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        elif requestMethod.POST_REQUEST(request):
            data_values = {}
            HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)
            HostelSeatAllotMulti = generate_session_table_name('HostelSeatAllotMulti_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)

            data = json.loads(request.body)
            length = len(data)

            HostelSeatAllotSetting.objects.filter(hostel_part=data[0]['hostel'], list_no__isnull=True).update(status="DELETE")
            for i in range(0, length):
                hostel = data[i]['hostel']
                course = data[i]['course']
                branch = data[i]['branch']
                year = data[i]['year']
                indiscipline = data[i]['indiscipline']
                criteria_type = data[i]['criteria_type']
                criteria_value = data[i]['criteria_value']
                priority = data[i]['priority']

                length_criteria_value = len(criteria_value)

                if 'att_min' in data[i]:
                    att_min = data[i]['att_min']
                else:
                    att_min = None

                if 'att_max' in data[i]:
                    att_max = data[i]['att_max']
                else:
                    att_max = None

                if 'uni_min' in data[i]:
                    uni_min = data[i]['uni_min']
                else:
                    uni_min = None

                if 'uni_max' in data[i]:
                    uni_max = data[i]['uni_max']
                else:
                    uni_max = None

                if 'carry_min' in data[i]:
                    carry_min = data[i]['carry_min']
                else:
                    carry_min = None

                if 'carry_max' in data[i]:
                    carry_max = data[i]['carry_max']
                else:
                    carry_max = None

                length_course = len(course)
                length_branch = len(branch)
                length_year = len(year)

                course_data = []
                sub_course_data = []

                for z in branch:
                    qry2 = studentSession.objects.filter(sem__dept=z, year__in=year).values_list('year', flat=True).distinct()
                    for j in qry2:
                        course_data.append({'branch': z, 'year': j})

                if 'sub_rule' in data[i]:

                    length_sub_rule = len(data[i]['sub_rule'])

                    for x in range(0, length_sub_rule):

                        sub_course = data[i]['sub_rule'][x]['course']
                        sub_branch = data[i]['sub_rule'][x]['branch']
                        sub_year = data[i]['sub_rule'][x]['year']

                        sub_priority = data[i]['sub_rule'][x]['sub_priority']

                        if 'bed_capacity' in data[i]['sub_rule'][x]:
                            bed_capacity = data[i]['sub_rule'][x]['bed_capacity']
                        else:
                            bed_capacity = None

                        if 'room_min' in data[i]['sub_rule'][x]:
                            room_min = data[i]['sub_rule'][x]['room_min']
                        else:
                            room_min = None

                        if 'room_max' in data[i]['sub_rule'][x]:
                            room_max = data[i]['sub_rule'][x]['room_max']
                        else:
                            room_max = None

                        length_sub_course = len(sub_course)
                        length_sub_branch = len(sub_branch)
                        length_sub_year = len(sub_year)

                        for z in sub_branch:
                            qry2 = studentSession.objects.filter(sem__dept=z, year__in=year).values_list('year', flat=True).distinct()
                            for j in sub_year:
                                sub_course_data.append({'branch': z, 'year': j})

                        length_sub_course_data = len(sub_course_data)
                        for x in range(0, length_sub_course_data):
                            if bed_capacity is None:
                                qry1 = HostelSeatAllotSetting.objects.create(hostel_part=HostelDropdown.objects.get(sno=hostel), branch=CourseDetail.objects.get(uid=sub_course_data[x]['branch']), year=sub_course_data[x]['year'], priority=priority, sub_priority=sub_priority, indiscipline=indiscipline, att_max=att_max, att_min=att_min, uni_min=uni_min, uni_max=uni_max, carry_max=carry_max, carry_min=carry_min, room_min=room_min, room_max=room_max, session=Semtiming.objects.get(uid=session))

                                objs = (HostelSeatAllotMulti(seat_setting=HostelSeatAllotSetting.objects.get(id=qry1.id), criteria_value=criteria_value[c], criteria_type=criteria_type)for c in range(0, length_criteria_value))
                            else:
                                qry1 = HostelSeatAllotSetting.objects.create(hostel_part=HostelDropdown.objects.get(sno=hostel), seat_part=HostelDropdown.objects.get(sno=bed_capacity), branch=CourseDetail.objects.get(uid=sub_course_data[x]['branch']), year=sub_course_data[x]['year'], priority=priority, sub_priority=sub_priority, indiscipline=indiscipline, att_max=att_max, att_min=att_min, uni_min=uni_min, uni_max=uni_max, carry_max=carry_max, carry_min=carry_min, room_min=room_min, room_max=room_max, session=Semtiming.objects.get(uid=session))

                                objs = (HostelSeatAllotMulti(seat_setting=HostelSeatAllotSetting.objects.get(id=qry1.id), criteria_value=criteria_value[c], criteria_type=criteria_type)for c in range(0, length_criteria_value))

                            qry2 = HostelSeatAllotMulti.objects.bulk_create(objs)

                        length_course_data = len(course_data)

                        if length_sub_course_data == 0:
                            for x in range(0, length_course_data):
                                qry1 = (HostelSeatAllotSetting.objects.create(hostel_part=HostelDropdown.objects.get(sno=hostel), branch=CourseDetail.objects.get(uid=course_data[x]['branch']), year=course_data[x]['year'], priority=priority, indiscipline=indiscipline, att_max=att_max, att_min=att_min, uni_min=uni_min, uni_max=uni_max, carry_max=carry_max, carry_min=carry_min, session=Semtiming.objects.get(uid=session)))

                                objs = (HostelSeatAllotMulti(seat_setting=HostelSeatAllotSetting.objects.get(id=qry1.id), criteria_value=criteria_value[c], criteria_type=criteria_type)for c in range(0, length_criteria_value))

                                qry2 = HostelSeatAllotMulti.objects.bulk_create(objs)

                        else:
                            for x in range(0, length_sub_course_data):
                                y = 0
                                while y < length_course_data:
                                    if course_data[y] == sub_course_data[x]:
                                        course_data.pop(y)
                                        length_course_data = len(course_data)
                                    y = y + 1

                length_course_data = len(course_data)

                for x in range(0, length_course_data):
                    qry1 = (HostelSeatAllotSetting.objects.create(hostel_part=HostelDropdown.objects.get(sno=hostel), branch=CourseDetail.objects.get(uid=course_data[x]['branch']), year=course_data[x]['year'], priority=priority, indiscipline=indiscipline, att_max=att_max, att_min=att_min, uni_min=uni_min, uni_max=uni_max, carry_max=carry_max, carry_min=carry_min, session=Semtiming.objects.get(uid=session)))

                    objs = (HostelSeatAllotMulti(seat_setting=HostelSeatAllotSetting.objects.get(id=qry1.id), criteria_value=criteria_value[c], criteria_type=criteria_type)for c in range(0, length_criteria_value))

                    qry2 = HostelSeatAllotMulti.objects.bulk_create(objs)

                temp_allot = Allot_Seat(emp_id, session, session_name, hostel)
                data_values['data'] = temp_allot[0]

                data_values['consolidate'] = {}
                data_values['consolidate']['capacity'] = get_hostel_capacity(hostel, session_name, session)
                data_values['consolidate']['occupied_un_capacity'] = temp_allot[1]

                occupied_capacity = copy.deepcopy(data_values['consolidate']['capacity'])

                for x in occupied_capacity:
                    if x in data_values['consolidate']['occupied_un_capacity']:
                        occupied_capacity[x] = occupied_capacity[x] - data_values['consolidate']['occupied_un_capacity'][x]

                data_values['consolidate']['occupied_capacity'] = occupied_capacity

                data_values['msg'] = statusMessages.MESSAGE_INSERT

            return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):
            if(requestType.custom_request_type(request.GET, 'get_list_no')):
                HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)
                data_set = list(HostelSeatAllotSetting.objects.filter(hostel_part=request.GET['hostel_id']).exclude(status='DELETE').exclude(list_no__isnull=True).values_list('list_no', flat=True).distinct())
                return functions.RESPONSE(data_set, statusCodes.STATUS_SUCCESS)

            elif(requestType.custom_request_type(request.GET, 'view_previous')):
                HostelSeatAllotSetting = generate_session_table_name('HostelSeatAllotSetting_', session_name)
                HostelSeatAllotMulti = generate_session_table_name('HostelSeatAllotMulti_', session_name)
                emp_id = request.session['hash1']
                rule = []
                data_set = []

                hostel_id = list(HostelDropdown.objects.filter(sno=request.GET['hostel_id']).values())

                list_no = request.GET['list_no']

                data_set = get_seat_allotment_rule_previous_data(hostel_id[0]['sno'], list_no, session_name)

                length_data = len(data_set)

                for z in range(0, length_data):
                    course = []
                    branch = []
                    year = []
                    sub_course = []
                    sub_branch = []
                    sub_year = []
                    sub_rule = []
                    room_min = []
                    room_max = []
                    seat_part = []
                    length_data_set = len(data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'])

                    for y in range(0, length_data_set):
                        length_course = len(course)
                        if length_course == 0:
                            course.append({'course': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'], 'course_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

                        if length_course != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course'] != course[length_course - 1]['course_id']:
                            course.append({'course': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'], 'course_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

                        length_branch = len(branch)
                        if length_branch == 0:
                            branch.append({'branch': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'], 'branch_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

                        if length_branch != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept'] != branch[length_branch - 1]['branch_id']:
                            branch.append({'branch': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'], 'branch_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

                        length_year = len(year)
                        if length_year == 0:
                            year.append({'year': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})
                        if length_year != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year'] != year[length_year - 1]['year']:
                            year.append({'year': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})

                        if data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['sub_priority'] != -1:

                            length_sub_course = len(sub_course)
                            if length_sub_course == 0:
                                sub_course.append({'course': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'], 'course_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})
                            if length_sub_course != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course'] != sub_course[length_sub_course - 1]['course_id']:
                                sub_course.append({'course': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'], 'course_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

                            length_sub_branch = len(sub_branch)
                            if length_sub_branch == 0:
                                sub_branch.append({'branch': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'], 'branch_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})
                            if length_sub_branch != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept'] != sub_branch[length_sub_branch - 1]['branch_id']:
                                sub_branch.append({'branch': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'], 'branch_id': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

                            length_sub_year = len(sub_year)
                            if length_sub_year == 0:
                                sub_year.append({'year': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})
                            if length_sub_year != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year'] != sub_year[length_sub_year - 1]['year']:
                                sub_year.append({'year': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})

                            length_room_min = len(room_min)
                            if length_room_min == 0:
                                room_min.append(data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['room_min'])

                            length_room_max = len(room_max)
                            if length_room_max == 0:
                                room_max.append(data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['room_max'])

                            seat_part = data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['seat_part']

                            length_sub_rule = len(sub_rule)
                            row = []
                            row.append({'sub_course': sub_course, 'sub_branch': sub_branch, 'sub_year': sub_year, 'seat_part': seat_part, 'room_min': room_min[0], 'room_max': room_max[0]})
                            if length_sub_rule == 0:
                                sub_rule.append({'sub_course': sub_course, 'sub_branch': sub_branch, 'sub_year': sub_year, 'seat_part': seat_part, 'room_min': room_min[0], 'room_max': room_max[0]})
                            if length_sub_rule != 0 and sub_rule[length_sub_rule - 1] != row[0]:
                                sub_rule.append({'sub_course': sub_course, 'sub_branch': sub_branch, 'sub_year': sub_year, 'seat_part': seat_part, 'room_min': room_min[0], 'room_max': room_max[0]})

                    qry2 = list(HostelSeatAllotMulti.objects.filter(seat_setting__list_no=list_no, seat_setting__priority=data_set[z]['priority']).values('criteria_type', 'criteria_value').distinct())
                    rule.append({'hostel_id': hostel_id[0]['sno'], 'hostel_name': hostel_id[0]['value'], 'list_no': list_no, 'course': course, 'branch': branch, 'year': year, 'priority': data_set[z]['priority'], 'indiscipline': data_set[z]['priority_set'][0]['indiscipline'], 'att_min': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min'], 'att_max': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max'], 'uni_max': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max'], 'uni_min': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min'], 'carry_min': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min'], 'carry_max': data_set[z]['priority_set'][0]['indiscipline_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max'], 'sub_rule': sub_rule, 'criteria': qry2})
                    data_set.append(rule)

                return functions.RESPONSE(data_set, statusCodes.STATUS_SUCCESS)

            else:
                return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Make_Seat_Allotment_From_Withdrawal(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:

        session = request.session['Session']
        session_data = get_odd_sem(session)
        session_name = session_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
        if requestMethod.GET_REQUEST(request):
            hostel_id = request.GET['hostel']
            gender = get_gender(emp_id)[0]['gender__value']
            data = list(HostelSeatAlloted.objects.filter(hostel_part__sno=hostel_id, uniq_id__uniq_id__gender__value=gender).exclude(status="DELETE").values('id', 'uniq_id__year', 'uniq_id__section_id__dept__course_id__value', 'uniq_id__section_id__dept__course_id', 'uniq_id__section_id__dept__dept_id__value', 'uniq_id__section_id__dept__course_id__value', 'seat_part__value', 'uniq_id__mob', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__lib_id', 'paid_status', 'uniq_id', 'hostel_part__value'))
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            id_arr = data['id']
            qr = HostelSeatAlloted.objects.filter(id__in=id_arr).exclude(status="DELETE").update(paid_status='PENDING')
            data = statusMessages.MESSAGE_SUCCESS
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Withdrawal_From_Paid_Fee(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        session = request.session['Session']
        session_data = get_odd_sem(session)
        session_name = session_data['session_name']

        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
        if requestMethod.GET_REQUEST(request):
            course = request.GET['course'].split(',')
            branch = request.GET['branch'].split(',')
            year = request.GET['year'].split(',')
            gender = get_gender(emp_id)[0]['gender__value']
            data = list(HostelSeatAlloted.objects.filter(paid_status='ALREADY PAID', uniq_id__year__in=year, uniq_id__section_id__dept__in=branch, uniq_id__uniq_id__gender__value=gender).exclude(status="DELETE").values('uniq_id__year', 'uniq_id', 'paid_status', 'uniq_id__mob', 'uniq_id__uniq_id__name', 'uniq_id__uniq_id__uni_roll_no', 'uniq_id__uniq_id__lib_id', 'uniq_id__uniq_id__dept_detail__course_id', 'uniq_id__uniq_id__dept_detail__course_id__value', 'uniq_id__uniq_id__dept_detail__course_id', 'uniq_id__uniq_id__dept_detail__dept_id', 'uniq_id__uniq_id__dept_detail__dept_id__value'))
            for q in data:
                uniq_id = q['uniq_id']
                qry = list(HostelRoomAlloted.objects.filter(uniq_id=uniq_id).exclude(status="DELETE").values('room_part__room_no', 'room_part__hostel_id__floor__value', 'room_part__hostel_id__bed_capacity__value'))
                if len(qry) != 0:
                    q['floor'] = qry[0]['room_part__hostel_id__floor__value']
                    q['room_no'] = qry[0]['room_part__room_no']
                    q['bed_capacity'] = qry[0]['room_part__hostel_id__bed_capacity__value']
                else:
                    q['floor'] = None
                    q['room_no'] = None
                    q['bed_capacity'] = None
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        elif requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)
            uniq_id_arr = data['id']
            qr1 = HostelSeatAlloted.objects.filter(uniq_id__in=uniq_id_arr).exclude(status="DELETE").update(paid_status='UNPAID')
            qr2 = HostelRoomAlloted.objects.filter(uniq_id__in=uniq_id_arr).exclude(status="DELETE").update(status="DELETE")

            ############## CHANGE : CALL FOR UPDATE RECIPT FOR REFUND FEE FOR HOSTEL ####################################

            data = statusMessages.MESSAGE_SUCCESS
            return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Change_Allotment_Status_and_Seater(request):
    emp_id = request.session['hash1']
    if checkpermission(request, [rolesCheck.ROLE_CHIEF_RECTOR_BOYS, rolesCheck.ROLE_CHIEF_RECTOR_GIRLS]) == statusCodes.STATUS_SUCCESS or academicCoordCheck.isRector(request) == True:
        session_data = get_odd_sem(request.session['Session'])
        session = session_data['session']
        session_name = session_data['session_name']
        print(session_name)
        print(int(session_name[:2]))
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

        HostelSeatAlloted = generate_session_table_name('HostelSeatAlloted_', session_name)
        HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
        studentSession = generate_session_table_name('studentSession_', session_name)
        HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)

        if requestMethod.POST_REQUEST(request):
            data = json.loads(request.body)

            if 'allotment_status' in data:
                allotment_status = data['allotment_status']
                hostel_id = data['hostel_id']
                if allotment_status == "GENERATE WITHDRAWAL":
                    uniq_id_list = HostelSeatAlloted.objects.filter(hostel_part=hostel_id, paid_status="NOT PAID").exclude(status="DELETE").values_list('uniq_id', flat=True)
                    current_status = 'WITHDRAWAL'
                else:
                    type_of_refund = ""
                    if allotment_status == "NOT ALLOTED":
                        current_status = 'PENDING'
                    elif allotment_status == "WITHDRAWAL":
                        current_status = 'WITHDRAWAL'
                    else:
                        data = statusMessages.CUSTOM_MESSAGE('NO ALLOTMENT STATUS SELECTED')
                        return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
                    type_of_refund = "W"

                    # uniq_id_data = HostelSeatAlloted.objects.filter(uniq_id=data['uniq_id'], paid_status="ALREADY PAID").exclude(status="DELETE").values_list('uniq_id', flat=True)
                    # if len(uniq_id_data)>0:
                    # 	hostel_refund_paid_fee(data['uniq_id'],session,None,emp_id,hostel_id,session_name,"REFUND",type_of_refund)
                    uniq_id_list = [data['uniq_id']]

                ######### CHANGE BY VRINDA ###################
                if allotment_status == "NOT ALLOTED":
                    qry = list(HostelSeatAlloted.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").values('uniq_id', 'paid_status'))

                    room_part = HostelRoomAlloted.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").values('room_part', 'room_part__allotted_status')

                    HostelRoomAlloted.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").update(status="DELETE")

                    if len(room_part) > 0:
                        HostelRoomSettings.objects.filter(id=room_part[0]['room_part']).exclude(status="DELETE").update(allotted_status=int(room_part[0]['room_part__allotted_status']) - 1)

                    HostelSeatAlloted.objects.filter(uniq_id__in=list(uniq_id_list)).exclude(status="DELETE").update(status='DELETE')

                    HostelStudentAppliction.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").update(current_status="PENDING")

                    if len(qry) > 0:
                        HostelSeatAlloted.objects.create(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), hostel_part=HostelDropdown.objects.get(sno=data['hostel_id']), paid_status=qry[0]['paid_status'])
                ##############################################
                if allotment_status != "NOT ALLOTED":
                    HostelSeatAlloted.objects.filter(uniq_id__in=list(uniq_id_list)).exclude(status="DELETE").update(status='DELETE')
                HostelStudentAppliction.objects.filter(uniq_id__in=list(uniq_id_list)).exclude(status="DELETE").update(current_status=current_status)
                data = statusMessages.MESSAGE_SUCCESS
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
            if 'bed_capacity' in data:
                # print(data['bed_capacity'])
                if check_empty_room(data['bed_capacity'], data['hostel_id'], session, session_name):
                    query = list(HostelSeatAlloted.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").values('paid_status'))
                    HostelSeatAlloted.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").update(status='DELETE')
                    if len(query) > 0:
                        HostelSeatAlloted.objects.create(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), seat_part=HostelDropdown.objects.get(field="BED CAPACITY", value=int(data['bed_capacity']), session=session), hostel_part=HostelDropdown.objects.get(sno=data['hostel_id']), paid_status=query[0]['paid_status'])
                    else:
                        HostelSeatAlloted.objects.create(uniq_id=studentSession.objects.get(uniq_id=data['uniq_id']), seat_part=HostelDropdown.objects.get(field="BED CAPACITY", value=int(data['bed_capacity']), session=session), hostel_part=HostelDropdown.objects.get(sno=data['hostel_id']))

                    HostelStudentAppliction.objects.filter(uniq_id=data['uniq_id']).exclude(status="DELETE").update(current_status='SEAT ALLOTED')

                    # CHANGE : CALL FOR UPDATE RECIPT FOR CHANGED SEATER TYPE ####################################3
                    # hostel_refund_paid_fee(data['uniq_id'],session,data['bed_capacity'],emp_id,data['hostel_id'],session_name,"UPDATE",type_of_refund)
                    # CHANGE : CALL FOR UPDATE RECIPT FOR CHANGED SEATER TYPE ####################################3

                    data = statusMessages.MESSAGE_SUCCESS
                else:
                    data = statusMessages.CUSTOM_MESSAGE('NO BED EMPTY FOR SELECTED HOSTEL AND BED-CAPACITY')
                    return functions.RESPONSE(data, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)

                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)
    else:
        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Room_Allotment_Rule(request):
    if academicCoordCheck.isRector(request) == True:
        emp_id = request.session['hash1']
        inicial_data = get_odd_sem(request.session['Session'])
        session = inicial_data['session']
        session_name = inicial_data['session_name']
        if int(session_name[:2]) < 19:
            return functions.RESPONSE(statusMessages.FEATURE_IS_NOT_SUPPORTED_FOR_SESSION, statusCodes.STATUS_CONFLICT_WITH_MESSAGE)
        if requestMethod.POST_REQUEST(request):

            HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)
            HostelRoomAllotMulti = generate_session_table_name('HostelRoomAllotMulti_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)
            generated_rules_id_list = []
            data_values = {}

            hostel_id = ""
            data = json.loads(request.body)
            generated_rules_id_list = []

            length = len(data)
            for i in range(0, length):
                hostel = data[i]['hostel']
                if i == 0:
                    hostel_id = hostel
                    HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel, list_no__isnull=True).delete()
                course = data[i]['course']
                branch = data[i]['branch']
                year = data[i]['year']
                phy_disabled = data[i]['phy_disabled']
                medical = data[i]['medical']
                priority = data[i]['priority']
                floor = data[i]['floor']
                course_preference = data[i]['course_preference']

                if 'criteria_type' in data[i]:
                    criteria_type = data[i]['criteria_type']
                else:
                    criteria_type = None

                if 'criteria_value' in data[i]:
                    criteria_value = data[i]['criteria_value']
                else:
                    criteria_value = None
                if 'indiscipline' in data[i]:
                    indiscipline = data[i]['indiscipline']
                else:
                    indiscipline = None

                if 'att_min' in data[i]:
                    att_min = data[i]['att_min']
                else:
                    att_min = None

                if 'att_max' in data[i]:
                    att_max = data[i]['att_max']
                else:
                    att_max = None

                if 'uni_min' in data[i]:
                    uni_min = data[i]['uni_min']
                else:
                    uni_min = None

                if 'uni_max' in data[i]:
                    uni_max = data[i]['uni_max']
                else:
                    uni_max = None

                if 'carry_min' in data[i]:
                    carry_min = data[i]['carry_min']
                else:
                    carry_min = None

                if 'carry_max' in data[i]:
                    carry_max = data[i]['carry_max']
                else:
                    carry_max = None

                course_data = []
                sub_data = []
                sub_floor_data = []

                for single_branch in branch:
                    qry2 = list(CourseDetail.objects.filter(uid=single_branch).values_list('course_duration', flat=True).distinct())

                    for year_no in range(1, qry2[-1] + 1):

                        if year_no in year:

                            course_data.append({'branch': single_branch, 'year': year_no})
                # print(course_data)
                if 'sub_rule' in data[i]:

                    length_sub_rule = len(data[i]['sub_rule'])

                    for x in range(0, length_sub_rule):

                        sub_course_data = []
                        sub_course = data[i]['sub_rule'][x]['course']
                        sub_branch = data[i]['sub_rule'][x]['branch']
                        sub_year = data[i]['sub_rule'][x]['year']

                        sub_priority = data[i]['sub_rule'][x]['sub_priority']

                        if 'sub_floor' in data[i]['sub_rule'][x]:
                            sub_floor = data[i]['sub_rule'][x]['sub_floor']
                        else:
                            sub_floor = None

                        if 'bed_capacity' in data[i]['sub_rule'][x]:
                            bed_capacity = data[i]['sub_rule'][x]['bed_capacity']
                        else:
                            bed_capacity = None

                        if 'room_min' in data[i]['sub_rule'][x]:
                            room_min = data[i]['sub_rule'][x]['room_min']
                        else:
                            room_min = None

                        if 'room_max' in data[i]['sub_rule'][x]:
                            room_max = data[i]['sub_rule'][x]['room_max']
                        else:
                            room_max = None

                        sub_floor_data.append(sub_floor)

                        for single_branch in sub_branch:
                            qry2 = list(CourseDetail.objects.filter(uid=single_branch).values_list('course_duration', flat=True).distinct())

                            for year_no in range(1, qry2[-1] + 1):
                                if year_no in sub_year:
                                    sub_course_data.append({'branch': single_branch, 'year': year_no})

                        qr1 = list(HostelFlooring.objects.filter(hostel_id=hostel, floor=sub_floor).exclude(status='DELETE').values('floor', 'bed_capacity'))

                        for x in sub_course_data:

                            create_details = {'branch': CourseDetail.objects.get(uid=x['branch']), 'year': x['year'], 'course_preference': course_preference, 'phy_disabled': phy_disabled, 'medical': medical, 'priority': priority, 'sub_priority': sub_priority, 'indiscipline': indiscipline, 'att_max': att_max, 'att_min': att_min, 'uni_min': uni_min, 'uni_max': uni_max, 'carry_max': carry_max, 'carry_min': carry_min, 'room_min': room_min, 'room_max': room_max, 'session': Semtiming.objects.get(uid=session)}

                            if bed_capacity is None:
                                for q in qr1:
                                    create_details['hostel_part'] = HostelFlooring.objects.get(hostel_id=hostel, floor=q['floor'], bed_capacity=q['bed_capacity'])
                                    generated_rules_id_list.append(create_details)

                            else:
                                create_details['hostel_part'] = HostelFlooring.objects.get(hostel_id=hostel, floor=sub_floor, bed_capacity=bed_capacity)
                                generated_rules_id_list.append(create_details)

                length_course_data = len(course_data)
                length_sub_floor_data = len(sub_floor_data)
                length_floor = len(floor)

                qr1 = list(HostelFlooring.objects.filter(hostel_id=hostel, floor__in=floor).exclude(status='DELETE').values('floor', 'bed_capacity'))
                length_sub_data = len(sub_data)
                if length_sub_data == 0:
                    for x in range(0, length_course_data):
                        for q in qr1:
                            create_details = {'hostel_part': HostelFlooring.objects.get(hostel_id=hostel, floor=q['floor'], bed_capacity=q['bed_capacity']), 'branch': CourseDetail.objects.get(uid=course_data[x]['branch']), 'year': course_data[x]['year'], 'course_preference': course_preference, 'phy_disabled': phy_disabled, 'medical': medical, 'priority': priority, 'sub_priority': -1, 'indiscipline': indiscipline, 'att_max': att_max, 'att_min': att_min, 'uni_min': uni_min, 'uni_max': uni_max, 'carry_max': carry_max, 'carry_min': carry_min, 'room_min': None, 'room_max': None, 'session': Semtiming.objects.get(uid=session)}

                            generated_rules_id_list.append(create_details)

                else:
                    for x in range(0, length_sub_data):
                        y = 0
                        while y < length_course_data:
                            if course_data[y] == sub_data[x]:
                                course_data.pop(y)
                                length_course_data = len(course_data)
                            y = y + 1

                    length_course_data = len(course_data)
                    qry = HostelRoomAllotSetting.objects.filter(hostel_part=hostel).update(status='DELETE')
                    for x in range(0, length_course_data):
                        for q in qr1:
                            create_details = {'hostel_part': HostelFlooring.objects.get(hostel_id=hostel, floor=q['floor'], bed_capacity=q['bed_capacity']), 'branch': CourseDetail.objects.get(uid=course_data[x]['branch']), 'year': course_data[x]['year'], 'course_preference': course_preference, 'phy_disabled': phy_disabled, 'medical': medical, 'priority': priority, 'sub_priority': -1, 'indiscipline': indiscipline, 'att_max': att_max, 'att_min': att_min, 'uni_min': uni_min, 'uni_max': uni_max, 'carry_max': carry_max, 'carry_min': carry_min, 'room_min': None, 'room_max': None, 'session': Semtiming.objects.get(uid=session)}

                            generated_rules_id_list.append(create_details)

            objs = (HostelRoomAllotSetting(branch=rule_id['branch'], year=rule_id['year'], course_preference=rule_id['course_preference'], phy_disabled=rule_id['phy_disabled'], medical=rule_id['medical'], priority=rule_id['priority'], sub_priority=rule_id['sub_priority'], indiscipline=rule_id['indiscipline'], att_max=rule_id['att_max'], att_min=rule_id['att_min'], uni_min=rule_id['uni_min'], uni_max=rule_id['uni_max'], carry_max=rule_id['carry_max'], carry_min=rule_id['carry_min'], room_min=rule_id['room_min'], room_max=rule_id['room_max'], session=rule_id['session'], hostel_part=rule_id['hostel_part']) for rule_id in generated_rules_id_list)
            qry2 = HostelRoomAllotSetting.objects.bulk_create(objs)

            generated_rules_id_list = list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel_id, list_no__isnull=True).values_list('id', flat=True))
            temp_allot = []
            temp_allot = Allot_Room(emp_id, session, session_name, hostel)
            data_values['data'] = temp_allot
            data_values['generated_rules_list'] = generated_rules_id_list

            return functions.RESPONSE(data_values, statusCodes.STATUS_SUCCESS)

        elif requestMethod.GET_REQUEST(request):

            if(requestType.custom_request_type(request.GET, 'view_previous')):

                HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)
                HostelRoomAllotMulti = generate_session_table_name('HostelRoomAllotMulti_', session_name)
                emp_id = request.session['hash1']
                hostel = get_rector_hostel(emp_id, {}, session)
                # print(hostel,":1")
                hostel_id = []
                for h in hostel:
                    hostel_id.append({'sno': h['sno'], 'value': h['value']})

                length_hostel = len(hostel_id)
                data = []
                for x in range(0, length_hostel):
                    rule = []
                    qry1 = list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel_id[x]['sno']).exclude(status='DELETE').exclude(list_no__isnull=True).values('list_no').distinct())
                    for q1 in qry1:

                        data_set = get_room_allotment_rule_previous_data(hostel_id[x]['sno'], q1['list_no'], session_name)
                        length_data_set = len(data_set)

                        for z in data_set:
                            course = []
                            branch = []
                            year = []

                            sub_prip_temp = z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set']

                            sub_rule = []
                            for y in sub_prip_temp:
                                sub_course = []
                                sub_branch = []
                                sub_year = []
                                room_min = []
                                room_max = []
                                bed_capacity = []
                                floor = []
                                sub_floor = []

                                sub_priority_set = y['sub_priority_set']
                                for i in sub_priority_set:
                                    length_course = len(course)
                                    if length_course == 0:
                                        course.append({
                                            'course': i['branch__course__value'],
                                            'course_id': i['branch__course']}
                                        )

                                    elif length_course != 0 and i['branch__course'] != course[length_course - 1]['course_id']:
                                        course.append({'course': i['branch__course__value'], 'course_id': i['branch__course']})

                                    length_branch = len(branch)
                                    if length_branch == 0:
                                        branch.append({'branch': i['branch__dept__value'], 'branch_id': i['branch__dept']})

                                    elif length_branch != 0 and i['branch__dept'] != branch[length_branch - 1]['branch_id']:

                                        branch.append({'branch': i['branch__dept__value'], 'branch_id': i['branch__dept']})

                                    length_year = len(year)
                                    if length_year == 0:

                                        year.append({'year': i['year']})

                                    elif length_year != 0 and i['year'] != year[length_year - 1]['year']:

                                        year.append({'year': i['year']})

                                    length_floor = len(floor)
                                    if length_floor == 0:
                                        floor.append({'floor': i['hostel_part__floor'], 'floor_value': i['hostel_part__floor__value']})

                                    elif length_floor != 0 and i['hostel_part__floor'] != floor[length_floor - 1]['floor']:

                                        floor.append({'floor': i['hostel_part__floor'], 'floor_value': i['hostel_part__floor__value']})

                                if y['sub_priority'] != -1:
                                    temp_sub_rule = y['sub_priority_set']
                                    sub_course_list_temp = []
                                    sub_branch_list_temp = []
                                    sub_year_list_temp = []
                                    sub_bed_capacity_list_temp = []
                                    sub_floor_list_temp = []

                                    for i in temp_sub_rule:

                                        if i['branch__course'] not in sub_course_list_temp:
                                            sub_course.append({'course': i['branch__course__value'], 'course_id': i['branch__course']})
                                            sub_course_list_temp.append(i['branch__course'])

                                        if i['branch__dept'] not in sub_branch_list_temp:
                                            sub_branch.append({'branch': i['branch__dept__value'], 'branch_id': i['branch__dept']})
                                            sub_branch_list_temp.append(i['branch__dept'])

                                        if i['year'] not in sub_year_list_temp:
                                            sub_year.append({'year': i['year']})
                                            sub_year_list_temp.append(i['year'])

                                        if i['hostel_part__bed_capacity'] not in sub_bed_capacity_list_temp:
                                            bed_capacity.append({'bed_capacity': i['hostel_part__bed_capacity'], 'bed_capacity_value': i['hostel_part__bed_capacity__value']})
                                            sub_bed_capacity_list_temp.append(i['hostel_part__bed_capacity'])

                                        if i['hostel_part__floor'] not in sub_floor_list_temp:
                                            sub_floor.append({'floor': i['hostel_part__floor'], 'floor_value': i['hostel_part__floor__value']})
                                            sub_floor_list_temp.append(i['hostel_part__floor'])

                                        length_room_min = len(room_min)
                                        if length_room_min == 0:
                                            room_min.append(i['room_min'])

                                        length_room_max = len(room_max)
                                        if length_room_max == 0:
                                            room_max.append(i['room_max'])

                                    sub_rule.append({'sub_priority': y['sub_priority'],
                                                     'sub_course': sub_course, 'sub_branch': sub_branch, 'sub_year': sub_year, 'bed_capacity': bed_capacity, 'sub_floor': sub_floor, 'room_min': room_min[0], 'room_max': room_max[0]
                                                     })

                            final_course = [dict(t) for t in {tuple(d.items()) for d in course}]
                            final_branch = [dict(t) for t in {tuple(d.items()) for d in branch}]
                            final_floor = [dict(t) for t in {tuple(d.items()) for d in floor}]
                            final_year = [dict(t) for t in {tuple(d.items()) for d in year}]
                            rule.append({'course': final_course, 'branch': final_branch, 'year': final_year, 'floor': final_floor, 'priority': z['priority'], 'indiscipline': z['priority_set'][0]['indiscipline'], 'course_preference': z['priority_set'][0]['indiscipline_set'][0]['course_preference'], 'phy_disabled': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled'], 'medical': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical'], 'att_min': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min'], 'att_max': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max'], 'uni_max': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max'], 'uni_min': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min'], 'carry_min': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min'], 'carry_max': z['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max'], 'sub_rule': sub_rule})

                        data.append({'hostel_id': hostel_id[x]['sno'], 'hostel_name': hostel_id[x]['value'], 'list_no': q1['list_no'], 'rule': rule})
                return functions.RESPONSE(data, statusCodes.STATUS_SUCCESS)

            if(requestType.custom_request_type(request.GET, 'get_list_no')):
                HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)
                # print(request.GET['hostel_id'])
                data_set = list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=request.GET['hostel_id']).exclude(status='DELETE').exclude(list_no__isnull=True).values_list('list_no', flat=True).distinct())
                return functions.RESPONSE(data_set, statusCodes.STATUS_SUCCESS)

        elif requestMethod.PUT_REQUEST(request):
            HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
            HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
            HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)
            studentSession = generate_session_table_name('studentSession_', session_name)
            date = datetime.today().strftime('%Y-%m-%d')
            data = json.loads(request.body)
            # print(data,'data')
            student_list = []
            for x in data:
                if x['rule_used'] != None:
                    x['rule_used'] = HostelRoomAllotSetting.objects.get(id=x['rule_used'])
                student_list.append(x['uniq_id'])

            for x in data:
                bulk_query = HostelRoomAlloted.objects.create(rule_used=x['rule_used'], uniq_id=studentSession.objects.get(uniq_id=x['uniq_id']), room_part=HostelRoomSettings.objects.get(id=x['room_part']), date_of_inserted=date, date_of_update=date)
                if bulk_query:
                    all_status = HostelRoomSettings.objects.filter(id=x['room_part']).values_list('allotted_status', flat=True)
                    qry = HostelRoomSettings.objects.filter(id=x['room_part']).update(allotted_status=int(all_status[0]) + 1)

            # HostelRoomAlloted.objects.bulk_create(bulk_query)

            HostelStudentAppliction.objects.filter(uniq_id__in=student_list, status="INSERT").update(current_status='ROOM ALLOTED')

            if len(data) > 0:
                # print(data[0],'data[0]')
                list_no = HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=data[0]['room_part__hostel_id__hostel_id']).exclude(list_no__isnull=True).exclude(status="DELETE").values_list('list_no', flat=True).order_by('-list_no')
                if len(list_no) > 0:
                    list_no = int(list_no[0]) + 1
                else:
                    list_no = 1
                if len(data) > 0:
                    HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=data[0]['room_part__hostel_id__hostel_id'], list_no__isnull=True).update(list_no=list_no)

            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)

        elif requestMethod.DELETE_REQUEST(request):
            HostelRoomAlloted = generate_session_table_name('HostelRoomAlloted_', session_name)
            HostelStudentAppliction = generate_session_table_name('HostelStudentAppliction_', session_name)
            HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_', session_name)

            data = json.loads(request.body)
            list_no = data['list_no']
            hostel_id = data['hostel_id']

            rules_list = list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel_id, list_no=list_no).values_list('id', flat=True))
            student_list = list(HostelRoomAlloted.objects.filter(rule_used__in=rules_list).exclude(status="DELETE").values_list('uniq_id', flat=True))
            room_id = list(HostelRoomAlloted.objects.filter(uniq_id__in=student_list).exclude(status="DELETE").values_list('room_part', flat=True))
            HostelRoomSettings.objects.filter(id__in=room_id).exclude(status="DELETE").update(allotted_status=0)

            HostelStudentAppliction.objects.filter(uniq_id__in=student_list, current_status="ROOM ALLOTED").exclude(status='DELETE').update(current_status="SEAT ALLOTED")
            HostelRoomAlloted.objects.filter(rule_used__in=rules_list).update(status="DELETE")
            HostelRoomAllotSetting.objects.filter(id__in=rules_list).update(status="DELETE")

            return functions.RESPONSE(statusMessages.MESSAGE_DELETE, statusCodes.STATUS_SUCCESS)
        else:
            return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED, statusCodes.STATUS_METHOD_NOT_ALLOWED)

    else:

        return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN, statusCodes.STATUS_FORBIDDEN)


def Room(request):
    hostel_id = 145
    session_name = '1920o'
    session = 8
    emp_id = request.session['hash1']
    data = Allot_Room(emp_id, session, session_name, hostel_id)
    # print(data,'data')
    return data
