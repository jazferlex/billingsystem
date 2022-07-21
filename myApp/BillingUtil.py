
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *
from django.template import Context
from datetime import date
from .BillingDB import *
import base64
from django.core.files.base import ContentFile
import json,sys
from django.template.loader import render_to_string
from .forms import *
import re
from django.conf import settings 
from django.core.mail import send_mail 
from django.core.mail import EmailMessage
from django.contrib import messages
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.views import View
from xhtml2pdf import pisa
import string
import random
from django.template.loader import get_template, render_to_string
from django.views import View
import binascii
from datetime import datetime, timedelta



def add_new_authorized_personel(request):
    template = "html/add_user_account.html"
    sessionval =  ReqParams.ADMIN_LOGIN_VAL
    user = SystemUser()
    alluser = SystemUser.objects.all()

    all_userid = []
    for user in alluser:
        all_userid.append(user.userid)

    context = {
        "msg":"",
        "error_pass":"",
    }
    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
    
    userid = request.POST.get(ReqParams.userid)
    firstname = request.POST.get(ReqParams.fname)
    lastname = request.POST.get(ReqParams.lname)
    middlename = request.POST.get(ReqParams.mname)
    password = request.POST.get(ReqParams.PASS)
    email = request.POST.get(ReqParams.email)
    can_approve = request.POST.get(ReqParams.can_approve)
    password = request.POST.get(ReqParams.PASS)
    repeat_password = request.POST.get("repeatpassword")
    #user types
    admin = request.POST.get(ReqParams.admin)
    teller = request.POST.get(ReqParams.teller)
    supervisor = request.POST.get(ReqParams.supervisor)
    manager = request.POST.get(ReqParams.manager)
    inputreader = request.POST.get(ReqParams.input_reader)
    user_roles = []
    user_role_str = ""

    roles = []
    credentials = []
    
    
    for user in alluser: 
        rolestr = "" 
        separator = ""
        i = 0    
        usertype = user.usertype
        if len(user.usertype) != 1:
            separator = "|"
        lent =  len(usertype)

        while(i < lent):
            rolestr += ReqParams.user_roles[int(usertype[i]) - 1] + separator
            i +=  1

        credentials.append(user)
        roles.append(rolestr)

    user_credentials = zip(credentials,roles)    

    if request.method == "POST":
        if SystemUser.objects.filter(pk = userid).exists(): 
            context["msg"] = "Already Exists."
            return render(request,render_page(request,sessionval,template),{"all_user":user_credentials,"context":context,"ReqParams":ReqParams,"all_userid":all_userid})
        elif password != repeat_password:   
            context["error_pass"] = "Password did not match."
            return render(request,render_page(request,sessionval,template),{"all_user":user_credentials,"context":context,"ReqParams":ReqParams,"all_userid":all_userid})
        else:
            #user roles
            user_roles.append(admin)
            user_roles.append(teller)
            user_roles.append(supervisor)
            user_roles.append(manager)
            user_roles.append(inputreader)

            user.userid = userid
            user.firstname = firstname
            user.middlename = middlename
            user.lastname = lastname
            #convertion into base64
            passAscii = password.encode("ascii")
            passBytes = base64.b64encode(passAscii)
            user.password = passBytes
            user.emailaddress = email
            if can_approve == None or can_approve == "":
                user.approver_flag = "0"
            else:
                user.approver_flag = can_approve

            for role in user_roles:
                if role != None:
                    user_role_str += role
            user.usertype = user_role_str        
            user.save()

            return HttpResponseRedirect("/source_access/view-system-user")

    

    return render(request,render_page(request,sessionval,template),{"all_user":user_credentials,"context":context,"ReqParams":ReqParams,"all_userid":all_userid}) 

def view_user(request):
    template = "html/user.management.html"
    sessionval =  ReqParams.ADMIN_LOGIN_VAL
    user = SystemUser()
    alluser = SystemUser.objects.all()
    context = {}
    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
    roles = []
    credentials = []

    for user in alluser: 
        rolestr = "" 
        separator = ""
        i = 0    
        usertype = user.usertype
        if len(user.usertype) != 1:
            separator = "|"
        lent =  len(usertype)

        while(i < lent):
            rolestr += ReqParams.user_roles[int(usertype[i]) - 1] + separator
            i +=  1

        credentials.append(user)
        roles.append(rolestr)

    user_credentials = zip(credentials,roles)  

    return render(request,render_page(request,sessionval,template),{"all_user":user_credentials,"context":context,"ReqParams":ReqParams}) 

def admin(request,id):
    template = "html/admin.html"
    sessionval = ReqParams.ADMIN_LOGIN_VAL
    context = {
        "name":request.session.get(ReqParams.name),
        "userid":request.session.get(ReqParams.userid)
    }

    return render(request,render_page(request,sessionval,template),{"context":context})


def edit_user(request,id):
    getId = SystemUser.objects.get(pk = id)
    user = SystemUser()
    alluser = SystemUser.objects.all()
    context = {}
    

    userid = request.POST.get(ReqParams.userid)
    firstname = request.POST.get(ReqParams.fname)
    lastname = request.POST.get(ReqParams.lname)
    middlename = request.POST.get(ReqParams.mname)
    usertype = request.POST.get(ReqParams.usertype)
    password = request.POST.get(ReqParams.PASS)
    email = request.POST.get(ReqParams.email)
    can_approve = request.POST.get(ReqParams.can_approve)
    password = request.POST.get(ReqParams.PASS)
    repeat_password = request.POST.get("repeatpassword")
    #decode password  
    reqpasswordBytes = base64.b64decode(getId.password)
    reqpasswordStr = reqpasswordBytes.decode("ascii")

    reqpassword_repeat = None
    reqpasswordBytes_repeat = None
    reqpassword_repeatStr = None
    

    context = {
        "password":reqpasswordStr,
        "repeat_password":reqpassword_repeatStr
    }

    #user types
    admin = request.POST.get(ReqParams.admin)
    teller = request.POST.get(ReqParams.teller)
    supervisor = request.POST.get(ReqParams.supervisor)
    manager = request.POST.get(ReqParams.manager)
    inputreader = request.POST.get(ReqParams.input_reader)
    user_roles = []
    user_role_str = ""
    template = ""
    loginsession = request.session.get(ReqParams.LOGIN_SESSION)

    if loginsession.__contains__(ReqParams.ADMIN_LOGIN_VAL):
        template = "html/edit_user.html"
    else:
        template = "html/unavailable.html" 
           
    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
    
    #can approve flag
    if getId.approver_flag == "1":
        context[ReqParams.can_approve] = "Supervisor"
    elif getId.approver_flag == "2": 
        context[ReqParams.can_approve] = "Engineer's Office" 
    elif getId.approver_flag == "3": 
        context[ReqParams.can_approve] = "Mayor's Office" 
    else:
        context[ReqParams.can_approve] = "Approvers for Inbound Application"    

    if request.method == "POST":
        
        #user roles
        user_roles.append(admin)
        user_roles.append(teller)
        user_roles.append(supervisor)
        user_roles.append(manager)
        user_roles.append(inputreader)

        if userid != getId.userid:
            if password != repeat_password:
                #error message
                messages.error(request,"Password did not match")
                print("error")
                return render(request,template,{"getId":getId,"alluser":alluser,"ReqParams":ReqParams,})
            else: 
                getId.delete()
                user.userid = userid
                user.firstname = firstname
                user.middlename = middlename
                user.lastname = lastname
                #convertion into base64
                passAscii = password.encode("ascii")
                passBytes = base64.b64encode(passAscii)
                user.password = passBytes
                user.emailaddress = email
                if can_approve:
                    user.approver_flag = can_approve

                for role in user_roles:
                    if role != None:
                        user_role_str += role
                user.usertype = user_role_str               
                #save     
                user.save()
                
                #print(user_role_str)
                pathstr = "/source_access" +  "/view-system-user"
                return HttpResponseRedirect(pathstr)
        else:
            if password != repeat_password:
                messages.error(request,"Password did not match")
                print("error")
                return render(request,template,{"getId":getId,"alluser":alluser,"ReqParams":ReqParams,})
            else:  

                getId.userid = userid
                getId.firstname = firstname
                getId.middlename = middlename
                getId.lastname = lastname
                #convertion into base64
                passAscii = password.encode("ascii")
                passBytes = base64.b64encode(passAscii)
                getId.password = passBytes
                getId.emailaddress = email
                if can_approve:
                    getId.approver_flag = can_approve
                    
                for role in user_roles:
                    if role != None:
                        user_role_str += role
                getId.usertype = user_role_str
                 
                #save
                getId.save()

                print(user_role_str)
                pathstr = "/source_access" + "/view-system-user"
                return HttpResponseRedirect(pathstr)
                
        
    return render(request,template,{"getId":getId,"alluser":alluser,"ReqParams":ReqParams,"context":context})
       



def view_list_applicants(request):
    context = []
    context1 = {
        "userid":request.session.get(ReqParams.userid)
    }
    template = ""
    userid = request.session.get(ReqParams.userid)
    loginsession = request.session.get(ReqParams.LOGIN_SESSION)
    #primary key value
    get_id = SystemUser.objects.get(pk = userid)
    approverflag = int(get_id.approver_flag)
    if loginsession:
        if approverflag != 0:
            if loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or loginsession.__contains__(ReqParams.MANAGER_LOGIN_VAL):
                template = "html/list-applicants.html"
            else:
                template = "html/unavailable.html"
        else:
            template = "html/unavailable.html"
    else:
        return redirect("/")        

    context1[ReqParams.userid] = userid
    context1[ReqParams.name] = get_id.firstname
    context1["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
    context1["name"] = request.session.get(ReqParams.name)
    approve_sum = 0
    
    #only choosen employee has the key or power to approve
    if approverflag != 0:
        applicants_list = Applicants_info.objects.all()
        getUser = SystemUser.objects.get(pk = userid)
        for applicant in applicants_list:
            approve_sum = applicant.checker_approval + applicant.engineer_approval + applicant.mayor_approval

            if getUser.approver_flag == ReqParams.approverflag_level1 and approve_sum == 0:#supervisor.level 1
                context.append(applicant)
            elif getUser.approver_flag == ReqParams.approverflag_level2 and approve_sum == 1: #engineer's Office
                context.append(applicant)
            elif getUser.approver_flag == ReqParams.approverflag_level3 and approve_sum == 2: #mayors's Office
                context.append(applicant)
            

    return render(request,template,{"context":context,"context1":context1})  

def decline_application(request,id):

    applicant = Applicants_info.objects.get(pk = id)
    userid = request.session.get(ReqParams.userid)
    comment = request.POST.get("comment")
    pathstr = "/list-applicants"
    template = ""
    context = {
        "userid":request.session.get(ReqParams.userid)
    }
    loginsession = request.session.get(ReqParams.LOGIN_SESSION)
    if loginsession:
        if loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or loginsession.__contains__(ReqParams.MANAGER_LOGIN_VAL):
                template = "html/list-applicants.html"
        else:
            template = "html/unavailable.html"
    else:
        return redirect("/")

    if request.method == "POST":
        if userid.approver_flag == ReqParams.approverflag_level1:
            applicant.checker_comment = comment
            return HttpResponseRedirect(pathstr)
        elif  userid.approver_flag == ReqParams.approverflag_level2:
            applicant.engineer_comment = comment
            return HttpResponseRedirect(pathstr)
        elif userid.approver_flag == ReqParams.approverflag_level3:
            applicant.mayor_comment = comment
            return HttpResponseRedirect(pathstr)
    context["applicantid"] = applicant.applicantid
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  

    return render(request,template,{"context":context}) 

#rendering session pages
def render_page(request,sessionval,template):
    retval = ""
    LOGIN_SESSION = request.session.get(ReqParams.LOGIN_SESSION)
    if LOGIN_SESSION:
        if LOGIN_SESSION.__contains__(sessionval):
            retval = template
        else:
            retval = "html/unavailable.html"
    else:
        return redirect("/")        

    return retval  


def ConverterBlob(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

#handle files
def handle_uploaded_file(file):
    with open('myApp/static/profilepics/' + file.name,'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def handle_requirements_files(file):
    with open('myApp/static/documents_required/' + file.name,'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)                  

def handle_requirements_images(file):
    with open('myApp/static/images_required/' + file.name,'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)              

def validate_phone_number(request,phone_number):
    retval = 0

    if phone_number.isdigit():
        output = re.findall(r"((^(\+)(\d){12}$)|(^\d{11}$))",phone_number)
        if(len(output)==1):
            print("YES")
            retval = 1
        else:
            print("NO")
            retval = 0
    else:
        print("NO")
        retval = 0

    return retval 



def change_password(request):
    password = request.POST.get(ReqParams.PASS)
    repeat_password = request.POST.get("repeat_password")
    verification_code = request.POST.get(ReqParams.verification_code)
    user_email = request.session.get(ReqParams.email)
    getID = SystemUser.objects.get(emailaddress = user_email).pk

    if request.method == "POST":
        if password == repeat_password:
            getID.password = password
            getID.save()
            return HttpResponseRedirect("/") 

    return render("html/index.html",{"verification_code":verification_code})            


def chart(request):
    return render(request,"chart.html")

def view_suspended_account(request):
    #rendering page
    template = ""
    sessionval = ""
    context = {
        "userid":request.session.get(ReqParams.userid),
        "name":request.session.get(ReqParams.name)
    }
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/view-suspended-accounts.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")        

    suspended_account = account_info.objects.filter(status = "0")
    if not suspended_account:
        context["message"] = "No Suspended Account"
    
    return render(request,template,{"suspended_account":suspended_account,"context":context})

def reactivate_account(request,id):

    account = account_info.objects.get(pk = id)
    account.status = "1"
    account.save()

    pathstr = "/source_access"  + "/view-suspended-account"
    return HttpResponseRedirect(pathstr)

def suspend_account(request,id):

    account = account_info.objects.get(pk = id)
    account.status = "0"
    account.save()
    consumerid_str = account.consumerid
    consumer = consumerid_str.consumerid

    pathstr = "/source_access" + "/update-this-consumer=" + str(account.consumerid) 
    return HttpResponseRedirect(pathstr)


def Deliquent(request,id):
    #rendering page
    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL):                                     
            template = "html/deliquent.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")

    context = {
        "UserType":request.session.get(ReqParams.LOGIN_SESSION),
        "name":request.session.get(ReqParams.name),
        "0":"Pending",
        "1":"Paid"
    }
    PaidStatus = ["Pending","Paid"]
    ErrorMessagePass = ""
    index = 0
    commulative_bill = 0
    current_date = date.today()
    year_request = request.POST.get(ReqParams.year)
    account = account_info.objects.get(pk = id)
    consumer = consumers_info.objects.get(pk = account.consumerid)
    #oldconsumer = OldCosumerInfo.objects.get(pk = consumer.oldconsumerid)
    accountidstr = account.accountinfoid + "-" + str(current_date.year)
    accountrecord = usage_record.objects.get(pk = accountidstr)
    #dropdown values
    current_year = current_date.year
    year_list = []
    #default value
    retval = []
    defval_year = str(current_year)
    #prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
    #get the latest bill
    latest_record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))
    commulative_bill = latest_record.commulative_bill

    #for record that has been updated/posted on this new System
    new_record = None
    if year_request == None:
        if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year)).exists():
            new_record =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))   
    
        
    #year to choose,from year 2010 until today
    while current_year >= 2010:    
        year_list.append(current_year)
        current_year = current_year - 1 
        

    if request.method == "POST":
        retval = []
        index = 0
        if year_request != None:          
            #for record that has been updated/posted on this new System
            if usage_record.objects.filter(pk = account.accountinfoid + "-" + year_request).exists():
                new_record =  usage_record.objects.get(pk = account.accountinfoid + "-" + year_request)
                
            defval_year = year_request
          
            

    return render(request,template,{"year_list":year_list,"retval":retval,"consumer":consumer,"ErrorMessagePass":ErrorMessagePass,"context":context,
                        "PaidStatus":PaidStatus,"ReqParams":ReqParams,"defval_year":defval_year,"account":account,
                        "new_record":new_record,"index":index,"commulative_bill":commulative_bill,"account":account})


def SendBill(request):
    #rendering page
    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):                                     
            template = "html/SendBill.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")

    context = {
        "UserType":request.session.get(ReqParams.LOGIN_SESSION),
        "name":request.session.get(ReqParams.name),
        "userid":request.session.get(ReqParams.userid)
    }    

    return render(request,template,{"context":context})    


def MyAccount(request,id):
    
    context = {
        "userid":request.session.get(ReqParams.userid),
        "name":request.session.get(ReqParams.name),
        "msg":"",
    }
    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:                                      
        template = "html/update_account(user).html"
    else:
        return redirect("/")

    user = SystemUser()
    getId = SystemUser.objects.get(pk = id)

    userid = request.POST.get(ReqParams.userid)
    firstname = request.POST.get(ReqParams.fname)
    lastname = request.POST.get(ReqParams.lname)
    middlename = request.POST.get(ReqParams.mname)
    usertype = request.POST.get(ReqParams.usertype)
    email = request.POST.get(ReqParams.email)
    pnumber = request.POST.get(ReqParams.mobile1)

    your_password = request.POST.get(ReqParams.PASS)
    new_password = request.POST.get("new_password")
    #decode password  
    reqpasswordBytes = base64.b64decode(getId.password)
    reqpasswordStr = reqpasswordBytes.decode("ascii")

    

    #User Role
    usertype = getId.usertype
    i = 0
    rolestr = ""
    separator = ""
    if len(usertype) != 1:
        separator = "|"
    lent =  len(usertype)

    while(i < lent):
        rolestr += ReqParams.user_roles[int(usertype[i]) - 1] + separator
        i +=  1
    context["role"] = rolestr


    

    if request.method == "POST":
        print(your_password)
        print(reqpasswordStr)
        print(getId.password)
        if userid != getId.userid:
        
            
            user.userid = userid
            user.firstname = firstname
            user.middlename = middlename
            user.lastname = lastname
            user.emailaddress = email 
            user.mobilenumber = pnumber
            user.password = getId.password
            user.usertype =  getId.usertype
            getId.delete()
            #save     
            user.save()
            if your_password:
                User = SystemUser.objects.get(pk = userid)
    
                if  your_password != new_password:
                    #error password
                    context["msg"] = "Wrong Password!"
                    return render(request,template,{"context":context,"getId":getId,"ReqParams":ReqParams})  
                else:
                    passAscii = new_password.encode("ascii")
                    passBytes = base64.b64encode(passAscii) 
                    User.password = passBytes
                    User.save()

            context["msg"] = "Update Successful!"
            return HttpResponseRedirect("/logout")

        else:
            if your_password:
                User = SystemUser.objects.get(pk = userid)
            
                if  your_password != new_password:
                    #error password
                    context["msg"] = "Wrong Password!"
                    return render(request,template,{"context":context,"getId":getId,"ReqParams":ReqParams})  
                else:
                    passAscii = new_password.encode("ascii")
                    passBytes = base64.b64encode(passAscii) 
                    User.password = passBytes
                    User.save()
                

            getId.userid = userid
            getId.firstname = firstname
            getId.middlename = middlename
            getId.lastname = lastname
            getId.emailaddress = email
            getId.mobilenumber = pnumber
            getId.save()
            context["msg"] = "Update Successful!"

        

        return render(request,template,{"context":context,"getId":getId,"ReqParams":ReqParams}) 


    return render(request,template,{"context":context,"getId":getId,"ReqParams":ReqParams})    

def send_code(request,id):
    
    # generating random digits(string)
    letters = string.digits
    verification_code_str = ""
    verification_code = ( ''.join(random.choice(letters) for i in range(5)))
    code_len = len(verification_code)
    i = 0
    while i < code_len:
        verification_code_str += verification_code[i]
        i += 1

    #credentials    
    user = SystemUser.objects.get(pk = id)
    email_to = user.emailaddress

    if email_to:
        subject = 'Ginatilan Waters'
        message = f'Your Verification Code is {verification_code_str}.\n Note: Verification Code will expire after 5 minutes.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [email_to, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()

        now =  datetime.now()
        vcode_expiry = now + timedelta(minutes=5)
        request.session[ReqParams.vcode_expiry] = str(vcode_expiry)
        request.session[ReqParams.verification_code] = verification_code_str

        return HttpResponseRedirect("/account-recovery=" + id + "/verification_code")    


def verification_code(request,id):
    template = "html/verification_code.html"
    now = datetime.now()
    user = SystemUser.objects.get(pk = id)
    
    vcode_session = request.session.get(ReqParams.verification_code)
    vcode = request.POST.get("vcode")
    vcode_expiry = request.session.get(ReqParams.vcode_expiry)

    context = {
        "userid":user.userid,
        "error_msg":"",
        "success_msg":"Changing Password Success!"
    }
    if request.method == "POST":
        if str(now) > vcode_expiry :
            context["error_msg"] = "Verification Code has been expired."  
            return render(request,template,{"context":context})  
        else:    
            if vcode ==  vcode_session:
                return HttpResponseRedirect("/account-recovery=" + id + "/change-pass") 
                
            else:
                context["error_msg"] = "Verification Code did not match!"   
                return render(request,template,{"context":context})

    return render(request,template,{"context":context})

def change_pass(request,id):
    template = "html/change_pass.html"
    user = SystemUser.objects.get(pk = id)
    context = {
        "userid":user.userid,
        "error_msg":"",
        "success_msg":""
    }
    new_pass = request.POST.get("new_pass")
    confirm_pass = request.POST.get("confirm_pass")

    if request.method == "POST":
        if new_pass == confirm_pass:
            passAscii = new_pass.encode("ascii")
            passBytes = base64.b64encode(passAscii) 
            user.password = passBytes
            user.save()
            context["success_msg"] = "Your Password has been changed!"
            #delete session value
            try:
                del request.session[ReqParams.vcode_expiry]
                del request.session[ReqParams.verification_code]
            except  KeyError:
                pass
            return render(request,template,{"context":context})
        
        else:
            #throw error
            context["error_msg"] = "Password did not match."
            return render(request,template,{"context":context})

    return render(request,template,{"context":context})

def get_stop_meter():
    all_account = account_info.objects.filter(stop_meter_flag = 1)
    current_date = date.today()
    
    for account in all_account:
        usage = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))
        prev_usage = None
        if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year - 1)).exists():
            prev_usage = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year - 1))
   
        if account.stop_meter_flag == 1:
            
            if current_date.month == 1:
                if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year - 1)).exists():
                    prev_usage.totalbill_dec = prev_usage.totalbill_nov
                    prev_usage.commulative_bill += prev_usage.totalbill_nov
                    prev_usage.reading_dec = usage.reading_nov
                    prev_usage.usage_dec = usage.usage_nov
                    prev_usage.save()

            if current_date.month == 2:
                if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year - 1)).exists():
                    usage.totalbill_jan = prev_usage.totalbill_dec
                    usage.commulative_bill += prev_usage.totalbill_dec
                    usage.reading_jan = prev_usage.reading_dec
                    usage.usage_jan = prev_usage.usage_dec
                    usage.save()

            if current_date.month == 3:
                usage.totalbill_feb = usage.totalbill_jan
                usage.commulative_bill += usage.totalbill_jan
                usage.reading_feb = usage.reading_jan
                usage.usage_feb = usage.usage_jan
                usage.save()

            if current_date.month == 4:
                usage.totalbill_mar = usage.totalbill_feb
                usage.commulative_bill += usage.totalbill_feb
                usage.reading_mar = usage.reading_feb
                usage.usage_mar = usage.usage_feb
                usage.save()

            if current_date.month == 5:
                usage.totalbill_apr = usage.totalbill_mar
                usage.commulative_bill += usage.totalbill_mar
                usage.reading_apr = usage.reading_mar
                usage.usage_apr = usage.usage_mar
                usage.save()

            if current_date.month == 6:
                usage.totalbill_may = usage.totalbill_apr
                usage.commulative_bill += usage.totalbill_apr
                usage.reading_may = usage.reading_apr
                usage.usage_may = usage.usage_apr
                usage.save()

            if current_date.month == 7:
                usage.totalbill_jun = usage.totalbill_may
                usage.commulative_bill += usage.totalbill_may
                usage.reading_jun = usage.reading_may
                usage.usage_jun = usage.usage_may
                usage.save()    

            if current_date.month == 8:
                usage.totalbill_jul = usage.totalbill_jun
                usage.commulative_bill += usage.totalbill_jun
                usage.reading_jul = usage.reading_jun
                usage.usage_jul = usage.usage_jun
                usage.save()

            if current_date.month == 9:
                usage.totalbill_aug = usage.totalbill_jul
                usage.commulative_bill += usage.totalbill_jul
                usage.reading_aug = usage.reading_jul
                usage.usage_aug = usage.usage_jul
                usage.save() 

            if current_date.month == 10:
                usage.totalbill_sept = usage.totalbill_aug
                usage.commulative_bill += usage.totalbill_aug
                usage.reading_sept = usage.reading_aug
                usage.usage_sept = usage.usage_aug
                usage.save()

            if current_date.month == 11:
                usage.totalbill_oct = usage.totalbill_sept
                usage.commulative_bill += usage.totalbill_sept
                usage.reading_oct = usage.reading_sept
                usage.usage_oct = usage.usage_sept
                usage.save()   

            if current_date.month == 12:
                usage.totalbill_nov = usage.totalbill_oct
                usage.commulative_bill += usage.totalbill_oct
                usage.reading_nov = usage.reading_oct
                usage.usage_nov = usage.usage_oct
                usage.save()           
    

def stop_meter(request,id):
    
    current_date = date.today()
    
    account = account_info.objects.get(pk = id)
    usage = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))
    prev_usage = None
    if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year - 1)).exists():
        prev_usage = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year - 1))
    
    if account.stop_meter_flag == 0:
        account.stop_meter_flag = 1
        account.save()
        
        if current_date.month == 1:
            if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year - 1)).exists():
                prev_usage.totalbill_dec = prev_usage.totalbill_nov
                prev_usage.commulative_bill += prev_usage.totalbill_nov
                prev_usage.reading_dec = prev_usage.reading_nov
                prev_usage.usage_dec = prev_usage.usage_nov
                prev_usage.save()

        if current_date.month == 2:
            if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_date.year - 1)).exists():
                usage.totalbill_jan = prev_usage.totalbill_dec
                usage.commulative_bill += prev_usage.totalbill_dec
                usage.reading_jan = prev_usage.reading_dec
                usage.usage_jan = prev_usage.usage_dec
                usage.save()

        if current_date.month == 3:
            usage.totalbill_feb = usage.totalbill_jan
            usage.commulative_bill += usage.totalbill_jan
            usage.reading_feb = usage.reading_jan
            usage.usage_feb = usage.usage_jan
            usage.save()

        if current_date.month == 4:
            usage.totalbill_mar = usage.totalbill_feb
            usage.commulative_bill += usage.totalbill_feb
            usage.reading_mar = usage.reading_feb
            usage.usage_mar = usage.usage_feb
            usage.save()

        if current_date.month == 5:
            usage.totalbill_apr = usage.totalbill_mar
            usage.commulative_bill += usage.totalbill_mar
            usage.reading_apr = usage.reading_mar
            usage.usage_apr = usage.usage_mar
            usage.save()

        if current_date.month == 6:
            usage.totalbill_may = usage.totalbill_apr
            usage.commulative_bill += usage.totalbill_apr
            usage.reading_may = usage.reading_apr
            usage.usage_may = usage.usage_apr
            usage.save()

        if current_date.month == 7:
            usage.totalbill_jun = usage.totalbill_may
            usage.commulative_bill += usage.totalbill_may
            usage.reading_jun = usage.reading_may
            usage.usage_jun = usage.usage_may
            usage.save()    

        if current_date.month == 8:
            usage.totalbill_jul = usage.totalbill_jun
            usage.commulative_bill += usage.totalbill_jun
            usage.reading_jul = usage.reading_jun
            usage.usage_jul = usage.usage_jun
            usage.save()

        if current_date.month == 9:
            usage.totalbill_aug = usage.totalbill_jul
            usage.commulative_bill += usage.totalbill_jul
            usage.reading_aug = usage.reading_jul
            usage.usage_aug = usage.usage_jul
            usage.save() 

        if current_date.month == 10:
            usage.totalbill_sept = usage.totalbill_aug
            usage.commulative_bill += usage.totalbill_aug
            usage.reading_sept = usage.reading_aug
            usage.usage_sept = usage.usage_aug
            usage.save()

        if current_date.month == 11:
            usage.totalbill_oct = usage.totalbill_sept
            usage.commulative_bill += usage.totalbill_sept
            usage.reading_oct = usage.reading_sept
            usage.usage_oct = usage.usage_sept
            usage.save()   

        if current_date.month == 12:
            usage.totalbill_nov = usage.totalbill_oct
            usage.commulative_bill += usage.totalbill_oct
            usage.reading_nov = usage.reading_oct
            usage.usage_nov = usage.usage_oct
            usage.save()   

    elif account.stop_meter_flag == 1:
        account.stop_meter_flag = 0
        account.save()
       

    return HttpResponseRedirect(f"/source_access/add-meter-reading/{id}")