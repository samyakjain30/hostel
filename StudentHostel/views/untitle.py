def Room_Allotment_Rule(request):
	if academicCoordCheck.isRector(request) == True:
		session_name = '1819o'
		session = 1
		# session_name = request.session['Session_name']
		# session = request.session['Session_id']
		if requestMethod.POST_REQUEST(request):
			HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_',session_name)
			HostelRoomAllotMulti = generate_session_table_name('HostelRoomAllotMulti_',session_name)
			studentSession = generate_session_table_name('studentSession_',session_name)

			data = json.loads(request.body)
			length=len(data)
			for i in range(0,length):
				hostel = data[i]['hostel']
				course = data[i]['course']
				branch = data[i]['branch']
				year = data[i]['year']
				phy_disabled = data[i]['phy_disabled']
				medical = data[i]['medical']
				priority = data[i]['priority']
				floor = data[i]['floor']
				course_preference = data[i]['course_preference']
# WRONG---------------START------------------------------------------------- DONE ---------------------------------------------

				if 'criteria_type' in data[i]:
					criteria_type = data[i]['criteria_type']
				else:
					criteria_type = None

				if 'criteria_value' in data[i]:
					criteria_value = data[i]['criteria_value']
					length_criteria_value = len(criteria_value)
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
# WRONG----------END------------------------------------------------------ DONE ------------------------------------------------

				length_course=len(course)
				length_branch=len(branch)
				length_year=len(year)

				course_data=[]
				sub_data=[]
				sub_floor_data=[]


# WHY---------------START------------------------------------------------- DONE ---------------------------------------------
				for x in range(0,length_course):
					qry1 = list(CourseDetail.objects.filter(course=course[x]).values('dept').distinct())
					length_qry_branch=len(qry1)

					for y in range(0,length_branch):

						for z in range(0,length_qry_branch):

							if branch[y] == qry1[z]['dept']:
								qry2 = list(studentSession.objects.filter(uniq_id__dept_detail__dept=branch[y]).values('year').distinct())
								length_qry_year=len(qry2)

								for k in range(0,length_year):

									for j in range(0,length_qry_year):

										if year[k] == qry2[j]['year']:

											course_data.append({'course':course[x],'branch':branch[y],'year':year[k]})

# WHY----------END------------------------------------------------------ DONE ------------------------------------------------
				if 'sub_rule' in data[i]:

					length_sub_rule = len(data[i]['sub_rule'])

					for x in range(0,length_sub_rule):

						sub_course_data=[]
						sub_course = data[i]['sub_rule'][x]['course']
						sub_branch = data[i]['sub_rule'][x]['branch']
						sub_year = data[i]['sub_rule'][x]['year']

						sub_priority = data[i]['sub_rule'][x]['sub_priority']

# WRONG---------------------START------------------------------------------- DONE -------------------------------------------------
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
# WRONG--------------------END-------------------------------------------- DONE ------------------------------------------------

						length_sub_course = len(sub_course)
						length_sub_branch=len(sub_branch)
						length_sub_year=len(sub_year)

						sub_floor_data.append(sub_floor)

# WHY-------------------------START--------------------------------------- DONE ------------------------------------------------

						for y in range(0,length_sub_course):
							qry1 = list(CourseDetail.objects.filter(course=sub_course[y]).values('dept').distinct())
							length_qry_branch=len(qry1)

							for z in range(0,length_sub_branch):

								for k in range(0,length_qry_branch):

									if sub_branch[z] == qry1[k]['dept']:
										qry2 = list(studentSession.objects.filter(uniq_id__dept_detail__dept=sub_branch[z]).values('year').distinct())
										length_qry_year=len(qry2)

										for m in range(0,length_sub_year):

											for j in range(0,length_qry_year):

												if sub_year[m] == qry2[j]['year']:

													sub_course_data.append({'course':sub_course[y],'branch':sub_branch[z],'year':sub_year[m]})
													sub_data.append({'course':sub_course[y],'branch':sub_branch[z],'year':sub_year[m]})

# WHY---------------------END------------------------------------------- DONE ------------------------------------------------------

# WHY---------------------START------------------------------------------- DONE -----------------------------------------------------

						length_sub_course_data=len(sub_course_data)
						qr1 = list(HostelFlooring.objects.filter(hostel_id=hostel,floor=sub_floor).exclude(status='DELETE').values('floor','bed_capacity'))
						for x in range(0,length_sub_course_data):
							if bed_capacity is None:
								for q in qr1:
									qry1 = HostelRoomAllotSetting.objects.create(hostel_part=HostelFlooring.objects.get(hostel_id=hostel,floor=q['floor'],bed_capacity=q['bed_capacity']),branch=CourseDetail.objects.get(course=sub_course_data[x]['course'],dept=sub_course_data[x]['branch']),year=sub_course_data[x]['year'],course_preference=course_preference,phy_disabled=phy_disabled,medical=medical,priority=priority,sub_priority=sub_priority,indiscipline=indiscipline,att_max=att_max,att_min=att_min,uni_min=uni_min,uni_max=uni_max,carry_max=carry_max,carry_min=carry_min,room_min=room_min,room_max=room_max,session=Semtiming.objects.get(uid=session))

									if criteria_type is not None:
										objs = (HostelRoomAllotMulti(seat_setting=HostelRoomAllotSetting.objects.get(id=qry1.id),criteria_value=criteria_value[c],criteria_type=criteria_type)for c in range(0,length_criteria_value))
							else:
								qry1 = HostelRoomAllotSetting.objects.create(hostel_part=HostelFlooring.objects.get(hostel_id=hostel,floor=sub_floor,bed_capacity=bed_capacity),branch=CourseDetail.objects.get(course=sub_course_data[x]['course'],dept=sub_course_data[x]['branch']),year=sub_course_data[x]['year'],course_preference=course_preference,priority=priority,phy_disabled=phy_disabled,medical=medical,sub_priority=sub_priority,indiscipline=indiscipline,att_max=att_max,att_min=att_min,uni_min=uni_min,uni_max=uni_max,carry_max=carry_max,carry_min=carry_min,room_min=room_min,room_max=room_max,session=Semtiming.objects.get(uid=session))

								if criteria_type is not None:
									objs = (HostelRoomAllotMulti(seat_setting=HostelRoomAllotSetting.objects.get(id=qry1.id),criteria_value=criteria_value[c],criteria_type=criteria_type)for c in range(0,length_criteria_value))

							if criteria_type is not None:
								qry2 = HostelRoomAllotMulti.objects.bulk_create(objs)

				length_course_data=len(course_data)
				length_sub_floor_data=len(sub_floor_data)
				length_floor=len(floor)

				qr1 = list(HostelFlooring.objects.filter(hostel_id=hostel,floor__in=floor).exclude(status='DELETE').values('floor','bed_capacity'))
				length_sub_data=len(sub_data)
				if length_sub_data == 0:
					for x in range(0,length_course_data):
						for q in qr1:
							qry1 = (HostelRoomAllotSetting.objects.create(hostel_part=HostelFlooring.objects.get(hostel_id=hostel,floor=q['floor'],bed_capacity=q['bed_capacity']),branch=CourseDetail.objects.get(course=course_data[x]['course'],dept=course_data[x]['branch']),year=course_data[x]['year'],phy_disabled=phy_disabled,medical=medical,course_preference=course_preference,priority=priority,indiscipline=indiscipline,att_max=att_max,att_min=att_min,uni_min=uni_min,uni_max=uni_max,carry_max=carry_max,carry_min=carry_min,session=Semtiming.objects.get(uid=session)))

							if criteria_type is not None:
								objs = (HostelRoomAllotMulti(seat_setting=HostelRoomAllotSetting.objects.get(id=qry1.id),criteria_value=criteria_value[c],criteria_type=criteria_type)for c in range(0,length_criteria_value))

						if criteria_type is not None:
							qry2 = HostelRoomAllotMulti.objects.bulk_create(objs)

				else:
					for x in range(0,length_sub_data):
						y=0
						while y < length_course_data:
							if course_data[y] == sub_data[x]:
								course_data.pop(y)
								length_course_data=len(course_data)
							y=y+1

					length_course_data=len(course_data)

					for x in range(0,length_course_data):
						for q in qr1:
							qry1 = (HostelRoomAllotSetting.objects.create(hostel_part=HostelFlooring.objects.get(hostel_id=hostel,floor=q['floor'],bed_capacity=q['bed_capacity']),branch=CourseDetail.objects.get(course=course_data[x]['course'],dept=course_data[x]['branch']),year=course_data[x]['year'],phy_disabled=phy_disabled,medical=medical,course_preference=course_preference,priority=priority,indiscipline=indiscipline,att_max=att_max,att_min=att_min,uni_min=uni_min,uni_max=uni_max,carry_max=carry_max,carry_min=carry_min,session=Semtiming.objects.get(uid=session)))

							if criteria_type is not None:
								objs = (HostelRoomAllotMulti(seat_setting=HostelRoomAllotSetting.objects.get(id=qry1.id),criteria_value=criteria_value[c],criteria_type=criteria_type)for c in range(0,length_criteria_value))

						if criteria_type is not None:
							qry2 = HostelRoomAllotMulti.objects.bulk_create(objs)

# WHY-------------------------END--------------------------------------- DONE -------------------------------------------------

			return functions.RESPONSE(statusMessages.MESSAGE_INSERT,statusCodes.STATUS_SUCCESS)

		elif requestMethod.GET_REQUEST(request):
			if(requestType.custom_request_type(request.GET,'view_previous')):
				HostelRoomAllotSetting = generate_session_table_name('HostelRoomAllotSetting_',session_name)
				HostelRoomAllotMulti = generate_session_table_name('HostelRoomAllotMulti_',session_name)
				emp_id=request.session['hash1']
				hostel=get_rector_hostel(emp_id,{},session)
				hostel_id=[]
				for h in hostel:
					hostel_id.append({'sno':h['sno'],'value':h['value']})

				length_hostel=len(hostel_id)
				rule=[]

				for x in range(0,length_hostel):
					qry1=list(HostelRoomAllotSetting.objects.filter(hostel_part__hostel_id=hostel_id[x]['sno']).exclude(status='DELETE').exclude(list_no__isnull=True).values('list_no').distinct())

					for q1 in qry1:
						data_set = get_room_allotment_rule_previous_data(hostel_id[x]['sno'],q1['list_no'],session_name)

						length_data=len(data_set)

						for z in range(0,length_data):
							course=[]
							branch=[]
							year=[]
							sub_course=[]
							sub_branch=[]
							sub_year=[]
							sub_data=[]
							sub_rule=[]
							room_min=[]
							room_max=[]
							bed_capacity=[]
							floor=[]
							sub_floor=[]
							length_data_set=len(data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'])

							for y in range(0,length_data_set):
								length_course=len(course)
								if length_course == 0:

									course.append({'course':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'],'course_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

								if length_course !=0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course'] != course[length_course-1]['course_id']:

									course.append({'course':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'],'course_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

								length_branch=len(branch)
								if length_branch == 0:

									branch.append({'branch':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'],'branch_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

								if length_branch !=0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept'] != branch[length_branch-1]['branch_id']:

									branch.append({'branch':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'],'branch_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

								length_year=len(year)
								if length_year == 0:

									year.append({'year':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})

								if length_year !=0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year'] != year[length_year-1]['year']:

									year.append({'year':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})

								length_floor=len(floor)
								if length_floor == 0:

									floor.append({'floor':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor'],'floor_value':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor__value']})

								if length_floor !=0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor'] != floor[length_floor-1]['floor']:

									floor.append({'floor':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor'],'floor_value':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor__value']})
									
									sub_course=[]
									sub_branch=[]
									sub_year=[]
									sub_rule=[]
									room_min=[]
									room_max=[]
									bed_capacity=[]
									sub_floor=[]

								if data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['sub_priority'] != -1:

									length_sub_course=len(sub_course)
									if length_sub_course == 0:

										sub_course.append({'course':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'],'course_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

									elif length_sub_course != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course'] != sub_course[length_sub_course-1]['course_id']:

										sub_course.append({'course':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course__value'],'course_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__course']})

									length_sub_branch=len(sub_branch)
									if length_sub_branch == 0:

										sub_branch.append({'branch':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'],'branch_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

									elif length_sub_branch != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept'] != sub_branch[length_sub_branch-1]['branch_id']:

										sub_branch.append({'branch':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept__value'],'branch_id':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['branch__dept']})

									length_sub_year=len(sub_year)
									if length_sub_year == 0:

										sub_year.append({'year':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})

									elif length_sub_year != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year'] != sub_year[length_sub_year-1]['year']:

										sub_year.append({'year':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['year']})

									length_room_min=len(room_min)
									if length_room_min == 0:
										room_min.append(data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['room_min'])

									length_room_max=len(room_max)
									if length_room_max == 0:
										room_max.append(data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['room_max'])

									length_bed_capacity=len(bed_capacity)
									if length_bed_capacity == 0:
										bed_capacity.append({'bed_capacity':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__bed_capacity'],'bed_capacity_value':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__bed_capacity__value']})

									elif length_bed_capacity != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__bed_capacity'] != bed_capacity[length_bed_capacity-1]['bed_capacity']:

										bed_capacity.append({'bed_capacity':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__bed_capacity'],'bed_capacity_value':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__bed_capacity__value']})

									length_sub_floor=len(sub_floor)
									if length_sub_floor == 0:
										sub_floor.append({'floor':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor'],'floor_value':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor__value']})

									elif length_sub_floor != 0 and data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor'] != sub_floor[length_sub_floor-1]['floor']:

										sub_floor.append({'floor':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor'],'floor_value':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['hostel_part__floor__value']})

									length_sub_rule=len(sub_rule)
									row=[]
									row.append({'sub_course':sub_course,'sub_branch':sub_branch,'sub_year':sub_year,'bed_capacity':bed_capacity,'sub_floor':sub_floor,'room_min':room_min[0],'room_max':room_max[0]})
									if length_sub_rule == 0:
										sub_rule.append({'sub_priority':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['sub_priority'],'sub_course':sub_course,'sub_branch':sub_branch,'sub_year':sub_year,'bed_capacity':bed_capacity,'sub_floor':sub_floor,'room_min':room_min[0],'room_max':room_max[0]})
									elif length_sub_rule != 0 and sub_rule[length_sub_rule-1] != row[0]:
										sub_rule.append({'sub_priority':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max_set'][y]['sub_priority'],'sub_course':sub_course,'sub_branch':sub_branch,'sub_year':sub_year,'bed_capacity':bed_capacity,'sub_floor':sub_floor,'room_min':room_min[0],'room_max':room_max[0]})

									sub_data.append({'sub_rule':sub_rule})

							length_sub_data=len(sub_data)
							for s1 in sub_data:
								length_sub_rule=len(s1['sub_rule'])
								for s2 in s1['sub_rule']:
									if s2['bed_capacity'] != None:
										length_sub_rule_bed_capacity=len(s2['bed_capacity'])
										if length_sub_rule_bed_capacity > 1:
											s2['bed_capacity'] = None

							for s1 in sub_data:
								dup_sub_rule=s1['sub_rule']

								length_sub_rule = len(s1['sub_rule'])

								if length_sub_rule > 1:
									length_dup_sub_rule = len(dup_sub_rule)
									for d in range(0,length_dup_sub_rule):
										s=0
										while s < length_sub_rule and length_sub_rule > 1:
											print(s,length_sub_rule)
											if dup_sub_rule[d] == s1['sub_rule'][s]:
												s1['sub_rule'].pop(s)
												length_sub_rule=len(sub_rule)
											s+=1

							qry2=list(HostelRoomAllotMulti.objects.filter(seat_setting__list_no=q1['list_no'],seat_setting__priority=data_set[z]['priority']).values('criteria_type','criteria_value').distinct())

							rule.append({'hostel_id':hostel_id[x]['sno'],'hostel_name':hostel_id[x]['value'],'list_no':q1['list_no'],'course':course,'branch':branch,'year':year,'floor':floor,'priority':data_set[z]['priority'],'indiscipline':data_set[z]['priority_set'][0]['indiscipline'],'course_preference':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference'],'phy_disabled':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled'],'medical':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical'],'att_min':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min'],'att_max':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max'],'uni_max':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max'],'uni_min':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min'],'carry_min':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min'],'carry_max':data_set[z]['priority_set'][0]['indiscipline_set'][0]['course_preference_set'][0]['phy_disabled_set'][0]['medical_set'][0]['att_min_set'][0]['att_max_set'][0]['uni_max_set'][0]['uni_min_set'][0]['carry_min_set'][0]['carry_max'],'sub_data':sub_data,'criteria':qry2})

				return functions.RESPONSE(data_set,statusCodes.STATUS_SUCCESS)

		else:
			return functions.RESPONSE(statusMessages.MESSAGE_METHOD_NOT_ALLOWED,statusCodes.STATUS_METHOD_NOT_ALLOWED)

	else:
		return functions.RESPONSE(statusMessages.MESSAGE_FORBIDDEN,statusCodes.STATUS_FORBIDDEN)