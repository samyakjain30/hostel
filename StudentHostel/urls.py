"""erp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
# from .views import *

from StudentHostel.views.vrinda_views import Hostel_Settings,Indiscipline_Form,Swapping,Room_Settings
from StudentHostel.views.hostel_views import Hostel_dropdown,Assign_Employee_Settings,getComponents,medical_form,LockingUnlocking,Seat_Allotment_Rule,Room_Allotment_Rule,Make_Seat_Allotment_From_Withdrawal,Withdrawal_From_Paid_Fee,Change_Allotment_Status_and_Seater
from StudentHostel.views.hostel_report import Manual_Room_Allotment_Unallotment, Applicant_List, Allotted_Unallotted_Student_List, Allotted_allotted_Student_List_Acc

urlpatterns = [
    url(r'^fields/$',Hostel_dropdown),
    url(r'^fields_category/$',Hostel_dropdown),
    url(r'^add_category/$',Hostel_dropdown),
    url(r'^update_category/$',Hostel_dropdown),
    url(r'^delete_category/$',Hostel_dropdown),
	url(r'^Hostel_Settings/$',Hostel_Settings),
	url(r'^Indiscipline_Form/$',Indiscipline_Form),
	url(r'^Assign_Employee_Settings/$',Assign_Employee_Settings),
	url(r'^getComponents/$',getComponents),
    url(r'^medical_form/$',medical_form),
    url(r'^Room_Settings/$',Room_Settings),
    url(r'^LockingUnlocking/$',LockingUnlocking),
    url(r'^Seat_Allotment_Rule/$',Seat_Allotment_Rule),
    url(r'^Room_Allotment_Rule/$',Room_Allotment_Rule),
    url(r'^Make_Seat_Allotment_From_Withdrawal/$',Make_Seat_Allotment_From_Withdrawal),
    url(r'^Withdrawal_From_Paid_Fee/$',Withdrawal_From_Paid_Fee),
    url(r'^Swapping/$',Swapping),
    url(r'^Applicant_List/$',Applicant_List),
    url(r'^Allotted_Unallotted_Student_List/$',Allotted_Unallotted_Student_List),
    url(r'^Change_Allotment_Status_and_Seater/$',Change_Allotment_Status_and_Seater),
    url(r'^Allotted_allotted_Student_List_Acc/$',Allotted_allotted_Student_List_Acc),
    url(r'^Manual_Room_Allotment_Unallotment/$',Manual_Room_Allotment_Unallotment),
    

]
