from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect

from myApp.ReportGenerator import meternumber
from .models import *  
from .forms import new_account_form
from django.template import Context
from datetime import date
from .BillingDB import *
from .BillingUtil import *
from .forms import Profilepic
from BillingSystem import settings
   
def update_consumer(request,id):
    #rendering page
    template = ""
    sessionval = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/update-consumer.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")        

    context = {}
    consumer = consumers_info.objects.get(pk = id)    
    account_list = []
    accounts = account_info.objects.filter(consumerid = id)
    usageRecord = usage_record()
    form = new_account_form(request.POST)

    lastname = request.POST.get(ReqParams.lname)
    firstname = request.POST.get(ReqParams.fname)
    middlename = request.POST.get(ReqParams.mname)
    bday = request.POST.get(ReqParams.birthday)
    sex = request.POST.get(ReqParams.sex)
    email = request.POST.get(ReqParams.email)
    mobile1 = request.POST.get(ReqParams.mobile1)
    mobile2 = request.POST.get(ReqParams.mobile2)
    address = request.POST.get(ReqParams.add)
    barangay = request.POST.get(ReqParams.barangay)
    sitio = request.POST.get(ReqParams.sitio)
    installcount = request.POST.get(ReqParams.installcount)
    profilepicform = Profilepic(request.POST,request.FILES)

    barangay_name1 = ""
    barangay_name2 = ""
    if consumer.barangay != "":
        barangay_name1 = ReqParams.barangay_list[int(consumer.barangay) - 1]
        barangay_name2 = ""


    current_year = date.today()
    get_year = str(current_year.year)


    if request.method == "POST":

        barangay_name1 = ReqParams.barangay_list[int(barangay) - 1]
        consumer.lastname = lastname
        consumer.firstname = firstname
        consumer.middlename = middlename
        consumer.birthday = bday
        consumer.emailaddress = email
        consumer.mobilenumber = mobile1
        consumer.mobilenumber2 = mobile2
        consumer.barangay = barangay
        consumer.homeaddress = barangay_name1 +",Ginatilan,Cebu"
        consumer.sitio = sitio
        #consumer.profilepic = request.FILES.get(ReqParams.profilepic) 
        consumer.save()
        account = account_info.objects.filter(consumerid = consumer.consumerid)

        for acc in account:
            install_account = account_info.objects.get(pk = acc.accountinfoid)
            install_account.lastname = lastname
            install_account.middlename = middlename
            install_account.firstname = firstname
            install_account.save()

        pathstr = "/source_access" +  "/update-this-consumer=" + id
        return HttpResponseRedirect(pathstr)   
 

    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context["barangay_residence"] = barangay_name1
    context["barangay_installation"] = barangay_name2
    return render(request,template,{"consumer":consumer,"accounts":accounts,"context":context,"ReqParams":ReqParams})


def add_account(request,id):
    #rendering page
    context = {
        "msg":""
    } 
    context1 = {
        "meterNum" : "",
        "address_installation": "",
        "duedate" :"",
        "status" : "",
        "initialreading" :"",
        "brgy": "1",#of installation  
        "address": "Anao,Ginatilan,Cebu"
    }
    consumer = consumers_info.objects.get(pk = id)
    new_account = account_info()
    usageRecord = usage_record()
    template = ""
    sessionval = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/add_account.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")        
       

    meterNum = request.POST.get(ReqParams.meter_num)
    address_installation = request.POST.get(ReqParams.address)
    duedate = request.POST.get(ReqParams.duedate)
    rate_id = request.POST.get(ReqParams.rateid)
    status = request.POST.get(ReqParams.status)
    initialreading = request.POST.get(ReqParams.initialreading)
    brgy = request.POST.get(ReqParams.barangay)#of installation

    current_year = date.today()
    get_year = str(current_year.year)

    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
    context["id"] = id

    if request.method == "POST":
        
        if account_info.objects.filter(meternumber = meterNum).exists():
            context["msg"] = "Ooopps! Meter Number is already exists!"
            context1 = {
                "meterNum" : request.POST.get(ReqParams.meter_num),
                "address_installation": request.POST.get(ReqParams.address),
                "duedate" :"",
                
                "status" : "",
                "initialreading" : request.POST.get(ReqParams.initialreading),
                "brgy": request.POST.get(ReqParams.barangay),
                "address": ReqParams.barangay_list[int(brgy) - 1] + ",Ginatilan,Cebu"   
            }
            return render(request,template,{"context":context,"context1":context1,"ReqParams":ReqParams,"consumer":consumer})
        else:    
            new_account.firstname = consumer.firstname
            new_account.middlename = consumer.middlename
            new_account.lastname = consumer.lastname
            new_account.meternumber = meterNum
            new_account.initial_meter_reading = initialreading
            new_account.barangay = brgy
            #barangay name
            barangay_name = ReqParams.barangay_list[int(brgy) - 1]
            new_account.address = barangay_name + ",Ginatilan,Cebu"
            new_account.rateid = rate_id
            #we set the new Accountinfo
            withzero = "" 
            if len(str(consumer.installcount + 1)) < 2:
                withzero = "0"
            else:
                withzero = ""

            new_account.accountinfoid = id + "-" + withzero + str(consumer.installcount + 1)
            new_account.consumerid = consumer
            consumer.installcount += 1 #increment the installcount
            new_account.save()
            consumer.save()

            #we make an usage record for new / existing consumer            
            usageRecord.accountid = new_account.accountinfoid + "-" + get_year#pk value
            usageRecord.accountinfoid = new_account.accountinfoid
            usageRecord.rateid = rate_id
            usageRecord.consumerid = consumer
            usageRecord.save()
            pathstr = "/source_access" + "/update-this-consumer=" + id
            return HttpResponseRedirect(pathstr)     


    return render(request,template,{"context":context,"context1":context1,"ReqParams":ReqParams,"consumer":consumer})

def update_account(request,id):

    account = account_info.objects.get(pk = id)
    context = {}
    template = ""
    sessionval = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/update-account.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")

    #accountinfo
    lastname = request.POST.get(ReqParams.lname)
    firstname = request.POST.get(ReqParams.fname)
    middlename = request.POST.get(ReqParams.mname)
    meterNum = request.POST.get(ReqParams.meter_num)
    address_installation = request.POST.get(ReqParams.address)
    duedate = request.POST.get(ReqParams.duedate)
    rate_id = request.POST.get(ReqParams.rateid)
    status = request.POST.get(ReqParams.status)
    initialreading = request.POST.get(ReqParams.initialreading)
    brgy = request.POST.get(ReqParams.barangay)#of installation

    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context[ReqParams.rateid] = ReqParams.rateid_name[account.rateid]
    context[ReqParams.pk] = account.consumerid_id
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  

    if request.method == "POST":
        account.firstname = firstname
        account.middlename = middlename
        account.lastname = lastname
        if meterNum != account.meternumber:
            if account_info.objects.filter(meternumber = meterNum).exists():
                context["metermsg"] = " is allready in used!" 
                return render(request,template,{"account":account,"context":context,"ReqParams":ReqParams})

            if initialreading:
                account.meternumber = meterNum
                account.initial_meter_reading = float(initialreading)
            else:
                context["msg"] = "Please input initial reading!" 
                return render(request,template,{"account":account,"context":context,"ReqParams":ReqParams})
        else:
            account.meternumber = meterNum

        account.barangay = brgy
        barangay_name = ReqParams.barangay_list[int(brgy) - 1]
        account.address = barangay_name + ",Ginatilan,Cebu"
        account.rateid = rate_id
        if initialreading:
            account.initial_meter_reading = float(initialreading)
        account.save()

        pathstr = "/source_access" + "/update-this-account=" + id
        return HttpResponseRedirect(pathstr)


    return render(request,template,{"account":account,"context":context,"ReqParams":ReqParams})

