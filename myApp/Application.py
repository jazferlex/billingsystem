from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *  
from django.template import Context
from datetime import date
from .BillingDB import *
from .BillingUtil import *
from .forms import *
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
import os


def application_old_consumer(request,id):
    template = "html/application(old consumer).html"
    
    applicant = Applicants_info()
    lastname = request.POST.get(ReqParams.lname)
    firstname = request.POST.get(ReqParams.fname)
    middlename = request.POST.get(ReqParams.mname)
    bday = request.POST.get(ReqParams.birthday)
    sex = request.POST.get(ReqParams.sex)
    email = request.POST.get(ReqParams.email)
    mobile1 = request.POST.get(ReqParams.mobile1)
    mobile2 = request.POST.get(ReqParams.mobile2)
    barangay_residence = request.POST.get(ReqParams.barangay)
    barangay_installation = request.POST.get(ReqParams.barangay_installation)
    sex = request.POST.get(ReqParams.sex)
    installcount = request.POST.get(ReqParams.installcount)
    address = ""
    sitio = request.POST.get(ReqParams.sitio)
    requirements_file_form = file_form(request.POST,request.FILES,)   

    account = None
    if  account_info.objects.filter(pk = id).exists():
        account = account_info.objects.get(pk = id)
    elif account_info.objects.filter(meternumber = id).exists():
        account = account_info.objects.get(meternumber = id)  

    #get the consumerid
    consumer = consumers_info.objects.get(pk = account.consumerid)


    if request.method == "POST":
        #we create the consumerid base on last id used
        applicantid = ""
        consumerid_len = 10
        keybasis = Primarykey_Basis.objects.get(pk = "applicantid")
        lastid = keybasis.lastid_used
        lastid_len = len(str(lastid + 1))
        len_zeros = consumerid_len - lastid_len

        while len_zeros != 0:
            applicantid += "0"
            len_zeros -= 1

        barangay_name1 = ReqParams.barangay_list[int(barangay_residence) - 1]
        barangay_name2 = ReqParams.barangay_list[int(barangay_installation) - 1]   

        applicantid += str(lastid + 1)
        applicant.applicantid = applicantid
        applicant.consumerid = consumer.consumerid
        applicant.firstname = firstname
        applicant.lastname = lastname
        applicant.middlename = middlename
        applicant.sex = consumer.sex
        applicant.birthday = bday
        applicant.emailaddress = email
        applicant.mobilenumber = mobile1
        applicant.mobilenumber2 = mobile2
        applicant.barangay_residence = barangay_residence
        applicant.barangay_installation = barangay_installation
        applicant.homeaddress = barangay_name1 + ",Ginatilan,Cebu"
        applicant.address_installation = barangay_name2 + ",Ginatilan,Cebu"
        applicant.sitio = sitio
        applicant.installcount = consumer.installcount + 1
        keybasis.lastid_used += 1
        applicant.save()
        keybasis.save()

        
    
        requirements_file_form = file_form(request.POST,request.FILES,)           
        if requirements_file_form.is_valid():   
            for file in request.FILES.getlist(ReqParams.file):
                if file.name.endswith('.png') or file.name.endswith('.jpg'):
                    handle_requirements_images(file)
                    applicant.required_image += file.name + "|"
                    applicant.save()
                elif file.name.endswith('.docx') or file.name.endswith('.pdf'):
                    handle_requirements_files(file)
                    applicant.required_files = +file.name + "|"
                    applicant.save()
            
        else:
            print("error")    

        #send email to applicants for instruction
        subject = 'Ginatilan Waters'
        message = f'Hello { firstname }, Your Applicant ID is { applicantid }.\n Use your Applicant ID to check status of your Application.\n Good Day!'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [email, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()

        #send notification as an email to Checker
        subject = 'Ginatilan Waters'
        message = f'Hello Maam/Sir, We have a new application request. Log-In into Your Ginatilan Waters Account to view the application request.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [ReqParams.Checker_Email, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()




    context = {
        "ID":id,
    }
    return render(request,template,{"consumer":consumer,"ReqParams":ReqParams,"context":context,'form':requirements_file_form,})


def application_new_consumer(request):
    template = "html/application(new consumer).html"
   
    applicant = Applicants_info()
    lastname = request.POST.get(ReqParams.lname)
    firstname = request.POST.get(ReqParams.fname)
    middlename = request.POST.get(ReqParams.mname)
    bday = request.POST.get(ReqParams.birthday)
    sex = request.POST.get(ReqParams.sex)
    email = request.POST.get(ReqParams.email)
    mobile1 = request.POST.get(ReqParams.mobile1)
    mobile2 = request.POST.get(ReqParams.mobile2)
    barangay_residence = request.POST.get(ReqParams.barangay)
    barangay_installation = request.POST.get(ReqParams.barangay_installation)
    sex = request.POST.get(ReqParams.sex)
    installcount = request.POST.get(ReqParams.installcount)
    address = ""
    sitio = request.POST.get(ReqParams.sitio)
    requirements_file_form = file_form(request.POST,request.FILES,)   


    if request.method == "POST":
        #we create the consumerid base on last id used
        applicantid = ""
        consumerid_len = 10
        keybasis = Primarykey_Basis.objects.get(pk = "applicantid")
        lastid = keybasis.lastid_used
        lastid_len = len(str(lastid + 1))
        len_zeros = consumerid_len - lastid_len

        while len_zeros != 0:
            applicantid += "0"
            len_zeros -= 1

        applicantid += str(lastid + 1)
        applicant.applicantid = applicantid
        #applicant.consumerid = account.consumerid
        applicant.firstname = firstname
        applicant.lastname = lastname
        applicant.middlename = middlename
        applicant.sex = sex
        applicant.birthday = bday
        applicant.emailaddress = email
        applicant.mobilenumber = mobile1
        applicant.mobilenumber2 = mobile2
        barangay_name1 = ReqParams.barangay_list[int(barangay_residence) - 1]
        barangay_name2 = ReqParams.barangay_list[int(barangay_installation) - 1]     
        applicant.barangay_residence = barangay_residence
        applicant.barangay_installation = barangay_installation
        applicant.homeaddress = barangay_name1 + ",Ginatilan,Cebu"
        applicant.address_installation = barangay_name2 + ",Ginatilan,Cebu"
        applicant.sitio = sitio
        applicant.installcount = 1
        keybasis.lastid_used += 1
        applicant.save()
        keybasis.save()

        
    
        requirements_file_form = file_form(request.POST,request.FILES,)           
        if requirements_file_form.is_valid():   
            for file in request.FILES.getlist(ReqParams.file):
                if file.name.endswith('.png') or file.name.endswith('.jpg'):
                    handle_requirements_images(file)
                    applicant.required_image += file.name + "|"
                    applicant.save()
                elif file.name.endswith('.docx') or file.name.endswith('.pdf'):
                    handle_requirements_files(file)
                    applicant.required_files += file.name + "|"
                    applicant.save()
            
        else:
            print("error")  

        #send email to applicants for instruction
        subject = 'Ginatilan Waters'
        message = f'Hello { firstname }, Your Applicant ID is { applicantid }.\n Use your Applicant ID to check status of your Application.\n Good Day!'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [email, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()

        #send notification as an email to Checker
        subject = 'Ginatilan Waters'
        message = f'Hello Maam/Sir, We have a new application request. Log-In into Your Ginatilan Waters Account to view the application request.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [ReqParams.Checker_Email, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()





    return render(request,template,{"ReqParams":ReqParams,'form':requirements_file_form,}) 

def getFilename(colname,separator):
    filelist = []
    colname_len = len(colname)
    i = 0
    j = i + 1
    filename = ""

    while i < colname_len:
        if colname[i] == separator:
            filelist.append(filename)
            i = i + 1
            filename = ""
        else:
            filename += colname[i]
            i = i + 1

    return filelist        


def view_application_status(request,id):
    template = "html/view-applicant-status.html"

    applicant = Applicants_info.objects.get(pk = id)
    separator = "|"
    #list of filenames uploaded
    required_images = getFilename(applicant.required_image,separator)
    required_files = getFilename(applicant.required_files,separator)

    checker_comments = getFilename(applicant.checker_comment,separator)
    date_checkercomments = getFilename(applicant.date_checkercommented,separator)
    engineer_comments = getFilename(applicant.engineer_comment,separator)
    date_engineercomments = getFilename(applicant.date_engineercommented,separator)
    mayor_comments = getFilename(applicant.mayor_comment,separator)
    date_mayorcomments = getFilename(applicant.date_mayorcommented,separator)

    checkerzip = zip(checker_comments,date_checkercomments)
    engineerzip = zip(engineer_comments,date_engineercomments)
    mayorzip = zip(mayor_comments,date_mayorcomments)
    

    context = {
        "ID":id,
    }

    return render(request,template,{"applicant":applicant,"context":context,"required_image":required_images,
                  "required_files":required_files,"checkerzip":checkerzip,"engineerzip":engineerzip,
                  "mayorzip":mayorzip})  

def view_applicants(request,id):
    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/view-applicants-info.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")   

    #list of filenames uploaded
    separator = "|"
    applicant = Applicants_info.objects.get(pk = id)
    required_images = getFilename(applicant.required_image,separator)
    required_files = getFilename(applicant.required_files,separator)

    current_date = date.today()
    userid = request.session.get(ReqParams.userid) 
    user = SystemUser.objects.get(pk = userid) 
    approverlevel = int(user.approver_flag)

    comment = request.POST.get("comment")

    if request.method == "POST":
        if comment != None:
            if approverlevel == 1:
                applicant.checker_comment += comment + "|"
                applicant.date_checkercommented = str(current_date) + "|"
                applicant.save()       
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir {applicant.firstname} {applicant.lastname}, Your Water Connection Application has been declined by the Supervisor for incomplete compliance.\n\n' 
                'Supervisor: "{comment}"\n\n' 'Use your application number to update your application form/request.'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [applicant.emailaddress, ]
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()
                pathstr = "/source_access/list-applicants"
                return HttpResponseRedirect(pathstr)

            elif approverlevel == 2:#engineer/second approver:
                applicant.engineer_comment += comment + "|"
                applicant.date_engineercommented = str(current_date) + "|"
                applicant.save()
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir {applicant.firstname} {applicant.lastname}, Your Water Connection Application has been declined by the Engineer`s Office for incomplete compliance.\n\n' 
                'Engineer: "{comment}"\n\n' 
                'Use your application number to update your application form/request.'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [applicant.emailaddress, ]
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()
                pathstr = "/source_access/list-applicants"
                return HttpResponseRedirect(pathstr)

            elif approverlevel == 3:
                applicant.mayor_comment = comment
                applicant.date_mayorcommented + "|"
                applicant.save()
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir {applicant.firstname} {applicant.lastname}, Your Water Connection Application has been declined by the Office of the Mayor for incomplete compliance.\n\n' 
                'Mayor: "{comment}"\n' 'Use your application number to update your application form/request.'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [applicant.emailaddress, ]
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()
                pathstr = "/source_access/list-applicants"
                return HttpResponseRedirect(pathstr)
        else:
            pass    
    

    context = {
        "ID":id,
        "UserType":request.session.get(ReqParams.LOGIN_SESSION),
        "name":request.session.get(ReqParams.name)
    }
    
    return render(request,template,{"applicant":applicant,"context":context,"required_image":required_images,
                  "required_files":required_files})  


def approve_applicants(request,id):
    current_date = date.today()
    userid = request.session.get(ReqParams.userid) 
    user = SystemUser.objects.get(pk = userid) 
    applicant = Applicants_info.objects.get(pk = id)
    approverlevel = int(user.approver_flag)

    if approverlevel == 1:#checker/first approver
        applicant.checker_approval = 1
        applicant.date_checkerapproval = str(current_date) 
        applicant.save()
        #we send notifications via email to the next Approver
        subject = 'Ginatilan Waters'
        message = f'Hello Maam/Sir, We have a new application request. Log-In into Your Ginatilan Waters Account to view the application request.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [ReqParams.Engineer_Email, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()
        pathstr = "/source_access/list-applicants"
        return HttpResponseRedirect(pathstr)
    elif approverlevel == 2:#engineer/second approver:
        applicant.engineer_approval = 1
        applicant.date_engineerapproval = str(current_date) 
        applicant.save()
        #we send notifications via email to the next Approver
        subject = 'Ginatilan Waters'
        message = f'Hello Maam/Sir, We have a new application request. Log-In into Your Ginatilan Waters Account to view the application request.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [ReqParams.Engineer_Email, ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()
        pathstr = "/source_access/list-applicants"
        return HttpResponseRedirect(pathstr)
    elif approverlevel == 3:
        #after mayor's approval. application send to teller/suppervisor
        applicant.mayor_approval = 1
        applicant.date_mayorapproval= str(current_date)
        applicant.save() 
        #we send notifications via email to the next Approver
        subject = 'Ginatilan Waters'
        message = f'Hello Maam/Sir, Water Connection Application of Mr/Ms.{applicant.firstname} {applicant.lastname} has been approved by the office of the mayor. Log-In into Your Ginatilan Waters Account and go to Approved Applicants section to view more.'
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [ReqParams.Teller_Email,ReqParams.Supervisor_Email ]
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()
        #send email to applicants for confirmation
        subject = 'Ginatilan Waters'
        message = f'Good Day Maam/Sir. Your Water Connection Application has been APPROVED by the office of the Mayor. Visit Municipalty of Ginatilan Town Hall to complete the Application. Thank You!' 
        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [applicant.emailaddress,] 
        mail = EmailMessage( subject, message, email_from, recipient_list )
        mail.send()
        pathstr = "/source_access/list-applicants"
        return HttpResponseRedirect(pathstr)


    

    

def view_approved_applicants(request):

    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL):
            template = "html/view-approved-applicants.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")
    

    all_applicant = Applicants_info.objects.all()
    applicant = []
    for approved in all_applicant:
        approved_sum = approved.checker_approval + approved.engineer_approval + approved.mayor_approval
        if(approved_sum == 3):
            applicant.append(approved)
    
    
    context = {
        "UserType":request.session.get(ReqParams.LOGIN_SESSION),
        "name":request.session.get(ReqParams.name),
        "userid":request.session.get(ReqParams.userid)
    }  

    return render(request,template,{"applicant":applicant,"context":context})

def delete_files(request,id,filename):
    directory = "myApp/static/documents_required/"
    file_to_delete = directory + filename
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)

    #delete the filename in our database
    applicant = Applicants_info.objects.get(pk = id)
    files_str = applicant.required_files
    filename_str = filename + "|"
    new_file = filename_str.replace(filename_str,"")    

    applicant.required_files = new_file
    applicant.save()

    pathstr = "/update-this-application=" + id
    return HttpResponseRedirect(pathstr)

def delete_images(request,id,filename):
    directory = "myApp/static/images_required/"
    file_to_delete = directory + filename
    if os.path.exists(file_to_delete):
        os.remove(file_to_delete)

    #delete the filename in our database
    applicant = Applicants_info.objects.get(pk = id)
    files_str = applicant.required_image
    filename_str = filename + "|"
    
    
    new_file = filename_str.replace(filename_str,"") 
   

    applicant.required_image = new_file
    applicant.save()

    pathstr = "/update-this-application=" + id
    return HttpResponseRedirect(pathstr)    

def delete_files_via_model(request,context = [],context1 = []):    
    directory1 = "myApp/static/images_required/"
    directory2 = "myApp/static/documents_required/"

    for element in context:
        file = directory1 + element
        if os.path.exists(directory1 + element):
            os.remove(file)
        else:
            print("error")    

    for element in context1:
        file = directory2 + element
        if os.path.exists(directory2 + element):
            os.remove(file)
        else:
            print("error")           

def add_this_applicant(request,id):
    #rendering page

    template = ""
    sessionval = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/add-approved-applicants.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("/")        

    context = {
        "alert_msg":""
    }
    applicant = Applicants_info.objects.get(pk = id)   
    meternumber = request.POST.get(ReqParams.meter_num)
    rate_id = request.POST.get(ReqParams.rateid)
    initialreading = request.POST.get(ReqParams.initialreading)
    context1 = {
        "meternumber":"",
        "rate_id":"",
        "initialreading":"",
    }

    current_date = date.today()
    account = account_info()
    print(applicant.applicantid)

    if request.method == "POST":
        
        if account_info.objects.filter(meternumber = meternumber).exists():
            context1 = {
                "meternumber":request.POST.get(ReqParams.meter_num),
                "rate_id":request.POST.get(ReqParams.rateid),
                "initialreading":request.POST.get(ReqParams.initialreading),
            }
            context["alert_msg"] = "Ooopps! Meter Number is allready exists!"
            
        applicantid_str = applicant.consumerid
        if applicantid_str == "":
            new_consumer = consumers_info() 
            #we create the consumerid base on last id used
            accstr = ""
            consumerid_len = 10
            keybasis = Primarykey_Basis.objects.get(pk = "consumerid")
            lastid = keybasis.lastid_used
            lastid_len = len(str(lastid + 1))
            len_zeros = consumerid_len - lastid_len

            while len_zeros != 0:
                accstr += "0"
                len_zeros -= 1

            accstr += str(lastid + 1) #new consumerid
            
            new_consumer.consumerid = accstr
            new_consumer.oldconsumerid = accstr
            keybasis.lastid_used =  lastid + 1

            new_consumer.firstname = applicant.firstname
            new_consumer.middlename = applicant.middlename
            new_consumer.lastname = applicant.lastname
            new_consumer.birthday = applicant.birthday
            new_consumer.mobilenumber = applicant.mobilenumber
            new_consumer.mobilenumber2 = applicant.mobilenumber2
            new_consumer.emailaddress = applicant.emailaddress
            new_consumer.homeaddress = applicant.homeaddress
            new_consumer.sex = applicant.sex
            new_consumer.installcount = 1
            new_consumer.profilepic = applicant.profilepic
            new_consumer.barangay = applicant.barangay_residence
            new_consumer.sitio = applicant.sitio
            new_consumer.save()

            account.consumerid = new_consumer
            account.firstname = applicant.firstname
            account.middlename = applicant.middlename
            account.lastname = applicant.lastname
            account.meternumber = meternumber
            account.initial_meter_reading = initialreading
            account.rateid = rate_id
            account.barangay = applicant.barangay_installation
            account.address = applicant.address_installation

            if len(str(new_consumer.installcount)) < 2:
                withzero = "0"
            else:
                withzero = ""

            accountrecord = usage_record()
            account.accountinfoid = new_consumer.consumerid + "-" + withzero  + str(new_consumer.installcount) 
            accountrecord.accountid = account.accountinfoid + "-" + str(current_date.year)
            accountrecord.rateid = rate_id
            accountrecord.year = current_date.year
            accountrecord.consumerid = new_consumer
            accountrecord.accountinfoid = account.accountinfoid
            accountrecord.save()
            account.save()
            keybasis.save()

            #delete the files in our System
            image_str = getFilename(applicant.required_files,"|")
            files_str = getFilename(applicant.required_files,"|")         
            delete_files_via_model(request,image_str,files_str)
            applicant.delete()
            pathstr = "/source_access/view-approved-applicants"
            return HttpResponseRedirect(pathstr)

        elif applicant.consumerid != "":
            applicantid_str = applicant.consumerid
            consumer = consumers_info.objects.get(pk = applicantid_str)
        
            account.consumerid = consumer
            account.firstname = consumer.firstname
            account.middlename = consumer.middlename
            account.lastname = consumer.lastname
            account.meternumber = meternumber
            account.initial_meter_reading = initialreading
            account.rateid = rate_id
            account.barangay = applicant.barangay_installation
            account.address = applicant.address_installation
                    
            if len(str(consumer.installcount + 1)) < 2:
                withzero = "0"
            else:
                withzero = ""

            accountrecord = usage_record()
            account.accountinfoid = consumer.consumerid + "-" + withzero  + str(consumer.installcount + 1) 
            accountrecord.accountid = account.accountinfoid + "-" + str(current_date.year)
            accountrecord.rateid = rate_id
            accountrecord.year = current_date.year
            accountrecord.accountinfoid = account.accountinfoid
            consumer.installcount += 1
            consumer.save()
            accountrecord.save()
            account.save()
                
            image_str = getFilename(applicant.required_files,"|")
            files_str = getFilename(applicant.required_files,"|")         
            delete_files_via_model(request,image_str,files_str)
            applicant.delete()

            pathstr = "/source_access/view-approved-applicants"
            return HttpResponseRedirect(pathstr)
        

    context[ReqParams.userid] = request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)
    context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)
    context["ID"] = applicant.applicantid
    search_for = request.POST.get("search_for")
    separator = "|"
    required_images = getFilename(applicant.required_image,separator)
    required_files = getFilename(applicant.required_files,separator)

    return render(request,template,{"context":context,"applicant":applicant,"required_image":required_images,"required_files":required_files,
                                    "ReqParams":ReqParams})





def update_this_application(request,id):
    template = "html/update_application.html"
    
    applicant = Applicants_info.objects.get(pk = id)
    lastname = request.POST.get(ReqParams.lname)
    firstname = request.POST.get(ReqParams.fname)
    middlename = request.POST.get(ReqParams.mname)
    bday = request.POST.get(ReqParams.birthday)
    sex = request.POST.get(ReqParams.sex)
    email = request.POST.get(ReqParams.email)
    mobile1 = request.POST.get(ReqParams.mobile1)
    mobile2 = request.POST.get(ReqParams.mobile2)
    barangay_residence = request.POST.get(ReqParams.barangay)
    barangay_installation = request.POST.get(ReqParams.barangay_installation)
    sex = request.POST.get(ReqParams.sex)
    installcount = request.POST.get(ReqParams.installcount)
    address = ""
    sitio = request.POST.get(ReqParams.sitio)
    profilepic = Profilepic(request.POST,request.FILES)
    profilepicform = Profilepic()
    requirements_file_form = request.POST 

    separator = "|"
    required_images = getFilename(applicant.required_image,separator)
    required_files = getFilename(applicant.required_files,separator)

    if request.method == "POST":
        barangay_name1 = ReqParams.barangay_list[int(barangay_residence) - 1]
        barangay_name2 = ReqParams.barangay_list[int(barangay_installation) - 1]       

        #applicant.applicantid = applicantid
        #applicant.consumerid = account.consumerid
        #uploaded a file 
        
        requirements_file_form = file_form(request.POST,request.FILES,)           
        if request.FILES.getlist('files[]') != None:  
            for file in request.FILES.getlist("files"):
                if file.name.endswith('.png') or file.name.endswith('.jpg'):
                    handle_requirements_images(file)
                    applicant.required_image += file.name + "|"
                    applicant.save()
                elif file.name.endswith('.docx') or file.name.endswith('.pdf'):
                    handle_requirements_files(file)
                    applicant.required_files += file.name + "|"
                    applicant.save()
            #we send a notification via email to the current approver
            approver_sum = applicant.checker_approval + applicant.engineer_approval + applicant.mayor_approval

            if approver_sum == approver_sum - 1:#checker/first approver
                applicant.checker_approval = 1
                applicant.date_checkerapproval = str(current_date) 
                applicant.save()
                #we send notifications via email to the next Approver
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir, We have a new application request. Log-In into Your Ginatilan Waters Account to view the application request.'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [ReqParams.Engineer_Email, ]
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()
                pathstr = "/update-this-application=" + id 
                return HttpResponseRedirect(pathstr)

            elif approver_sum == approver_sum - 1:#engineer/second approver:
                applicant.engineer_approval = 1
                applicant.date_engineerapproval = str(current_date) 
                applicant.save()
                #we send notifications via email to the next Approver
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir, Applicant {firstname} {lastname} has been update its Water Connection Application. Log-In into your Ginatilan Waters Account and check its Application on Application Request section. Good Day!'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [ReqParams.Engineer_Email, ]
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()
                pathstr = "/update-this-application=" + id 
                return HttpResponseRedirect(pathstr)

            elif approver_sum == approver_sum - 1:
                #after mayor's approval. application send to teller/suppervisor
                applicant.mayor_approval = 1
                applicant.date_mayorapproval= str(current_date)
                applicant.save() 
                #we send notifications via email to the next Approver
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir, Applicant {firstname} {lastname} has been update its Water Connection Application. Log-In into your Ginatilan Waters Account and check its Application on Application Request section. Good Day!'
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [ReqParams.Teller_Email,ReqParams.Supervisor_Email ]
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()
                #send email to applicants for confirmation
                subject = 'Ginatilan Waters'
                message = f'Hello Maam/Sir, Applicant {firstname} {lastname} has been update its Water Connection Application. Log-In into your Ginatilan Waters Account and check its Application on Application Request section. Good Day!' 
                email_from = settings.EMAIL_HOST_USER 
                recipient_list = [applicant.emailaddress,] 
                mail = EmailMessage( subject, message, email_from, recipient_list )
                mail.send()

                pathstr = "/update-this-application=" + id 
                return HttpResponseRedirect(pathstr)
                
        
        applicant.firstname = firstname
        applicant.lastname = lastname
        applicant.middlename = middlename
        applicant.sex = sex
        applicant.birthday = bday
        applicant.emailaddress = email
        applicant.mobilenumber = mobile1
        applicant.mobilenumber2 = mobile2
        applicant.barangay = barangay_residence
        applicant.barangay_installation = barangay_installation
        applicant.homeaddress = barangay_name1 + ",Ginatilan,Cebu"
        applicant.address_installation = barangay_name2 + ",Ginatilan,Cebu"
        applicant.sitio = sitio
        
        #applicant.installcount = consumer.installcount + 1
            
        if request.FILES.get(ReqParams.profilepic) != "" or request.FILES.get(ReqParams.profilepic) != None:
            if profilepicform.is_valid():
                handle_uploaded_file(request.FILES[ReqParams.profilepic])
                applicant.profilepic = request.FILES.get(ReqParams.profilepic).name + "|"
            else:
                profilepicform = Profilepic()
                print("error")

        applicant.save()  

        pathstr = "/update-this-application=" + id    
        return HttpResponseRedirect(pathstr)  

    context = {
        "ID":id,
        "image":applicant.profilepic
    }
    

    return render(request,template,{"applicant":applicant,"ReqParams":ReqParams,"context":context,"form":requirements_file_form,"required_image":required_images,
                                    "required_files":required_files})      


def view_account(request,id):
    template = "html/consumer-bill-usage.html" 
    account = account_info.objects.get(pk = id) 
    context = {
        "name":account.firstname
    }    
    
    return render(request,template,{"account":account,"context":context})                              