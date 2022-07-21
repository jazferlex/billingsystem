from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *  
from django.template import Context
from datetime import date
from .BillingDB import *
from .BillingUtil import *
from .forms import Profilepic
from BillingSystem import settings
from myApp import ReportGenerator
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.views import View
from xhtml2pdf import pisa
from .models import *
from django.conf import settings



def Update_Revenue(request):

    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession == (ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/Rates.html"
        elif LogInSession == (ReqParams.MANAGER_LOGIN_VAL):
            template = "html/Rates(Manager).html"
        else:
            template = "html/unavailable.html" 
    else:
        return redirect("/")
        
    revenue = revenuecode.objects.get(pk = 1)
    userid = request.session.get(ReqParams.userid)
    getUser = SystemUser.objects.get(pk = userid)
    residential = rates.objects.get(pk = ReqParams.residential)
    commercial = rates.objects.get(pk = ReqParams.commercial)
    context = {
        "userid":userid,
        "name": request.session.get(ReqParams.name),
    }
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  

    application_fee = request.POST.get(ReqParams.application_fee)
    mayors_permit = request.POST.get(ReqParams.mayors_permit)
    gravel_excavation = request.POST.get(ReqParams.gravel_excavation)
    asphalted_road = request.POST.get(ReqParams.asphalted_road)
    cemented_road = request.POST.get(ReqParams.cemented_road)
    residential_service = request.POST.get(ReqParams.residential_service)
    commercial_service = request.POST.get(ReqParams.commercial_service)
    residential_excess_fee = request.POST.get(ReqParams.residential_excess_fee)
    commercial_excess_fee = request.POST.get(ReqParams.commercial_excess_fee)
    drilling_from_mainline = request.POST.get(ReqParams.drilling_from_mainline)
    reinstallation_fee = request.POST.get(ReqParams.reinstallation_fee)
    tapping_fee = request.POST.get(ReqParams.tapping_fee)
    transfer_fee = request.POST.get(ReqParams.transfer_fee)
    repair_fee = request.POST.get(ReqParams.repair_fee)
    three_month_penalty = request.POST.get(ReqParams.three_month_penalty)
    additionalfee_pipe_of_20_lineal_feet = request.POST.get(ReqParams.additionalfee_pipe_of_20_lineal_feet)
    disconnection_after = request.POST.get(ReqParams.disconnection_after)
    disconnection_notice_after = request.POST.get(ReqParams.disconnection_notice_after)
    penalty_after = request.POST.get(ReqParams.month)
    percentage = request.POST.get(ReqParams.percentage)
    fix_amount = request.POST.get(ReqParams.fix_amount)
    password = request.POST.get(ReqParams.PASS)

    print(residential_excess_fee)

    if request.method == "POST":
        #convertion to base64
        passAscii = password.encode("ascii")
        passBytes = base64.b64encode(passAscii)
        if passBytes == getUser.password:
            revenue.application_fee = application_fee
            revenue.mayors_permit = mayors_permit
            revenue.gravel_excavation = gravel_excavation
            revenue.asphalted_road = asphalted_road
            revenue.cemented_road = cemented_road
            revenue.residentialservice_per_month = residential_service
            revenue.commercialservice_per_month = commercial_service
            revenue.residentialservice_excess_per_cubicmeter = residential_excess_fee
            revenue.commercialservice_excess_per_cubicmeter = commercial_excess_fee 
            revenue.drilling_from_mainline = drilling_from_mainline
            revenue.reinstallation_fee = reinstallation_fee
            revenue.tapping_fee = tapping_fee
            revenue.transfer_fee = transfer_fee
            revenue.repair_fee = repair_fee
            #revenue.three_month_penalty = three_month_penalty
            revenue.additionalfee_pipe_of_20_lineal_feet = additionalfee_pipe_of_20_lineal_feet
            revenue.send_disconnection_notice_after = disconnection_notice_after
            revenue.disconnection_after = disconnection_after
            revenue.penalty_after = penalty_after
            if percentage:
                revenue.fix_amount_penalty = 0
                revenue.percentage_penalty = percentage
            if fix_amount:
                revenue.fix_amount_penalty = fix_amount
                revenue.percentage_penalty = 0
                
            #update rates table
            residential.rateafterminimum = residential_excess_fee
            commercial.rateafterminimum = commercial_excess_fee
            #save
            revenue.save()
            residential.save()
            commercial.save()

            pathstr = "/source_access" +  "/update-revenue-code"
            return HttpResponseRedirect(pathstr)

        else:
            #error
            context["error_message"] = "Wrong Password!"
            return render(request,template,{"revenue":revenue,"ReqParams":ReqParams,"context":context}) 

    return render(request,template,{"revenue":revenue,"ReqParams":ReqParams,"context":context}) 

     