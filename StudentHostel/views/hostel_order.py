# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from datetime import datetime,date
import json
from itertools import groupby
from django.db.models import Sum,F
import operator

from StudentHostel.constants_variables import lock_type

from StudentHostel.models import *
from Registrar.models import *
from musterroll.models import EmployeePerdetail,Roles
from login.models import EmployeeDropdown,EmployeePrimdetail

from StudentSMM.views.smm_function_views import check_residential_status
from login.views import checkpermission,generate_session_table_name
# Create your views here.

######################################################################################################################

def create_order_chooser(pet_name):
	function="order_by_"+pet_name
	return eval(function)

def order_by_priority(list_data,sort_by_again):
	data=[]
	for priority_sno,(priority_name,priority_group) in enumerate(groupby(list_data,key=lambda group_priority:group_priority['priority'])):
		data.append({})
		data[-1]['priority']=priority_name
		temp_priority=list(priority_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['priority_set']=create_order_chooser(temp_key)(temp_priority,sort_by_again[1:])
		else:
			data[-1]['priority_set']=temp_priority

	return data

def order_by_course_preference(list_data,sort_by_again):
	data=[]
	for course_preference_sno,(course_preference_name,course_preference_group) in enumerate(groupby(list_data,key=lambda group_course_preference:group_course_preference['course_preference'])):
		data.append({})
		data[-1]['course_preference']=course_preference_name
		temp_course_preference=list(course_preference_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['course_preference_set']=create_order_chooser(temp_key)(temp_course_preference,sort_by_again[1:])
		else:
			data[-1]['course_preference_set']=temp_course_preference

	return data

def order_by_indiscipline(list_data,sort_by_again):
	data=[]
	for indiscipline_sno,(indiscipline_name,indiscipline_group) in enumerate(groupby(list_data,key=lambda group_indiscipline:group_indiscipline['indiscipline'])):
		data.append({})
		data[-1]['indiscipline']=indiscipline_name
		temp_indiscipline=list(indiscipline_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['indiscipline_set']=create_order_chooser(temp_key)(temp_indiscipline,sort_by_again[1:])
		else:
			data[-1]['indiscipline_set']=temp_indiscipline

	return data

def order_by_phy_disabled(list_data,sort_by_again):
	data=[]
	for phy_disabled_sno,(phy_disabled_name,phy_disabled_group) in enumerate(groupby(list_data,key=lambda group_phy_disabled:group_phy_disabled['phy_disabled'])):
		data.append({})
		data[-1]['phy_disabled']=phy_disabled_name
		temp_phy_disabled=list(phy_disabled_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['phy_disabled_set']=create_order_chooser(temp_key)(temp_phy_disabled,sort_by_again[1:])
		else:
			data[-1]['phy_disabled_set']=temp_phy_disabled

	return data

def order_by_medical(list_data,sort_by_again):
	data=[]
	for medical_sno,(medical_name,medical_group) in enumerate(groupby(list_data,key=lambda group_medical:group_medical['medical'])):
		data.append({})
		data[-1]['medical']=medical_name
		temp_medical=list(medical_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['medical_set']=create_order_chooser(temp_key)(temp_medical,sort_by_again[1:])
		else:
			data[-1]['medical_set']=temp_medical

	return data

def order_by_att_min(list_data,sort_by_again):
	data=[]
	for att_min_sno,(att_min_name,att_min_group) in enumerate(groupby(list_data,key=lambda group_att_min:group_att_min['att_min'])):
		data.append({})
		data[-1]['att_min']=att_min_name
		temp_att_min=list(att_min_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['att_min_set']=create_order_chooser(temp_key)(temp_att_min,sort_by_again[1:])
		else:
			data[-1]['att_min_set']=temp_att_min

	return data

def order_by_att_max(list_data,sort_by_again):
	data=[]
	for att_max_sno,(att_max_name,att_max_group) in enumerate(groupby(list_data,key=lambda group_att_max:group_att_max['att_max'])):
		data.append({})
		data[-1]['att_max']=att_max_name
		temp_att_max=list(att_max_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['att_max_set']=create_order_chooser(temp_key)(temp_att_max,sort_by_again[1:])
		else:
			data[-1]['att_max_set']=temp_att_max

	return data

def order_by_carry_min(list_data,sort_by_again):
	data=[]
	for carry_min_sno,(carry_min_name,carry_min_group) in enumerate(groupby(list_data,key=lambda group_carry_min:group_carry_min['carry_min'])):
		data.append({})
		data[-1]['carry_min']=carry_min_name
		temp_carry_min=list(carry_min_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['carry_min_set']=create_order_chooser(temp_key)(temp_carry_min,sort_by_again[1:])
		else:
			data[-1]['carry_min_set']=temp_carry_min

	return data

def order_by_uni_max(list_data,sort_by_again):
	data=[]
	for uni_max_sno,(uni_max_name,uni_max_group) in enumerate(groupby(list_data,key=lambda group_uni_max:group_uni_max['uni_max'])):
		data.append({})
		data[-1]['uni_max']=uni_max_name
		temp_uni_max=list(uni_max_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['uni_max_set']=create_order_chooser(temp_key)(temp_uni_max,sort_by_again[1:])
		else:
			data[-1]['uni_max_set']=temp_uni_max

	return data

def order_by_uni_min(list_data,sort_by_again):
	data=[]
	for uni_max_sno,(uni_min_name,uni_min_group) in enumerate(groupby(list_data,key=lambda group_uni_min:group_uni_min['uni_min'])):
		data.append({})
		data[-1]['uni_min']=uni_min_name
		temp_uni_min=list(uni_min_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['uni_min_set']=create_order_chooser(temp_key)(temp_uni_min,sort_by_again[1:])
		else:
			data[-1]['uni_min_set']=temp_uni_min

	return data

def order_by_carry_min(list_data,sort_by_again):
	data=[]
	for carry_min_sno,(carry_min_name,carry_min_group) in enumerate(groupby(list_data,key=lambda group_carry_min:group_carry_min['carry_min'])):
		data.append({})
		data[-1]['carry_min']=carry_min_name
		temp_carry_min=list(carry_min_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['carry_min_set']=create_order_chooser(temp_key)(temp_carry_min,sort_by_again[1:])
		else:
			data[-1]['carry_min_set']=temp_carry_min

	return data

def order_by_carry_max(list_data,sort_by_again):
	data=[]
	for carry_max_sno,(carry_max_name,carry_max_group) in enumerate(groupby(list_data,key=lambda group_carry_max:group_carry_max['carry_max'])):
		data.append({})
		data[-1]['carry_max']=carry_max_name
		temp_carry_max=list(carry_max_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['carry_max_set']=create_order_chooser(temp_key)(temp_carry_max,sort_by_again[1:])
		else:
			data[-1]['carry_max_set']=temp_carry_max

	return data

def order_by_sub_priority(list_data,sort_by_again):
	data=[]
	for sub_priority_sno,(sub_priority_name,sub_priority_group) in enumerate(groupby(list_data,key=lambda group_sub_priority:group_sub_priority['sub_priority'])):
		data.append({})
		data[-1]['sub_priority']=sub_priority_name
		temp_sub_priority=list(sub_priority_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['sub_priority_set']=create_order_chooser(temp_key)(temp_sub_priority,sort_by_again[1:])
		else:
			data[-1]['sub_priority_set']=temp_sub_priority

	return data

def order_by_current_status(list_data,sort_by_again):
	data=[]
	for current_status_sno,(current_status_name,current_status_group) in enumerate(groupby(list_data,key=lambda group_current_status:group_current_status['current_status'])):
		data.append({})
		data[-1]['current_status']=current_status_name
		temp_current_status=list(current_status_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['current_status_set']=create_order_chooser(temp_key)(temp_current_status,sort_by_again[1:])
		else:
			data[-1]['current_status_set']=temp_current_status

		for temp in data[-1]['current_status_set']:
			sorted_d = sorted(temp.items(), key=operator.itemgetter(0))

	return data

def order_by_branch(list_data,sort_by_again):
	data=[]
	for branch_sno,(branch_name,branch_group) in enumerate(groupby(list_data,key=lambda group_branch:group_branch['branch'])):
		data.append({})
		data[-1]['branch']=branch_name
		temp_branch=list(branch_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['branch_set']=create_order_chooser(temp_key)(temp_branch,sort_by_again[1:])
		else:
			data[-1]['branch_set']=temp_branch

	return data

def order_by_uniq_id(list_data,sort_by_again):
	data=[]
	for uniq_id_sno,(uniq_id_name,uniq_id_group) in enumerate(groupby(list_data,key=lambda group_uniq_id:group_uniq_id['uniq_id'])):
		data.append({})
		data[-1]['uniq_id']=uniq_id_name
		temp_uniq_id=list(uniq_id_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['uniq_id_set']=create_order_chooser(temp_key)(temp_uniq_id,sort_by_again[1:])
		else:
			data[-1]['uniq_id_set']=temp_uniq_id

	return data

def order_by_student_name(list_data,sort_by_again):
	data=[]
	for student_name_sno,(student_name_name,student_name_group) in enumerate(groupby(list_data,key=lambda group_student_name:group_student_name['name'])):
		data.append({})
		data[-1]['student_name']=student_name_name
		temp_student_name=list(student_name_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['student_name_set']=create_order_chooser(temp_key)(temp_student_name,sort_by_again[1:])
		else:
			data[-1]['student_name_set']=temp_student_name

	return data

def order_by_dept(list_data,sort_by_again):
	data=[]
	for dept_sno,(dept_name,dept_group) in enumerate(groupby(list_data,key=lambda group_dept:group_dept['branch'])):
		data.append({})
		data[-1]['dept']=dept_name
		temp_dept=list(dept_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['dept_set']=create_order_chooser(temp_key)(temp_dept,sort_by_again[1:])
		else:
			data[-1]['dept_set']=temp_dept

	return data

def order_by_year(list_data,sort_by_again):
	data=[]
	for year_sno,(year_name,year_group) in enumerate(groupby(list_data,key=lambda group_year:group_year['year'])):
		data.append({})
		data[-1]['year']=year_name
		temp_year=list(year_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['year_set']=create_order_chooser(temp_key)(temp_year,sort_by_again[1:])
		else:
			data[-1]['year_set']=temp_year

	return data

def order_by_paid_status(list_data,sort_by_again):
	data=[]
	for paid_status_sno,(paid_status_name,paid_status_group) in enumerate(groupby(list_data,key=lambda group_paid_status:group_paid_status['paid_status'])):
		data.append({})
		data[-1]['paid_status']=paid_status_name
		temp_paid_status=list(paid_status_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['paid_status_set']=create_order_chooser(temp_key)(temp_paid_status,sort_by_again[1:])
		else:
			data[-1]['paid_status_set']=temp_paid_status

		for temp in data[-1]['paid_status_set']:
			sorted_d = sorted(temp.items(), key=operator.itemgetter(0))

	return data

######## ROOM ORDER ####################
def order_by_seater(list_data,sort_by_again):
	data=[]
	for seater,(seater,seater_group) in enumerate(groupby(list_data,key=lambda group_uniq_id:group_uniq_id['seater'])):
		data.append({})
		data[-1]['seater']=seater
		temp_seater=list(seater_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['seater_set']=create_order_chooser(temp_key)(temp_seater,sort_by_again[1:])
		else:
			data[-1]['seater_set']=temp_seater

	return data

def room_view_list_create_order_by_priority(list_data,sort_by_again):
	data=[]
	for priority_sno,(priority_name,priority_group) in enumerate(groupby(list_data,key=lambda group_priority:group_priority['priority'])):
		data.append({})
		data[-1]['priority']=priority_name
		temp_priority=list(priority_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['priority_set']=create_order_chooser(temp_key)(temp_priority,sort_by_again[1:])
		else:
			data[-1]['priority_set']=temp_priority

	return data

def order_by_floor(list_data,sort_by_again):
	data=[]
	print(list_data)
	for floor,(floor,floor_group) in enumerate(groupby(list_data,key=lambda group_uniq_id:group_uniq_id['floor'])):
		data.append({})
		data[-1]['floor']=floor
		temp_floor=list(floor_group)
		if(len(sort_by_again)>1):
			temp_key=sort_by_again[1]
			data[-1]['floor_set']=create_order_chooser(temp_key)(temp_floor,sort_by_again[1:])
		else:
			data[-1]['floor_set']=temp_floor

	return data