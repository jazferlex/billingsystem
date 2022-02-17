from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *
import string
import random
import re
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
import os
from django.http import HttpResponse
EMAIL_HOST_USER = settings.EMAIL_HOST_USER
import json
import csv
import base64
from smtplib import SMTPException

from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def welcome(request):

   return render(request,'html/welcome.html',{"all_user":all_user}) #simply display the page

def add_consumer(request):
   consumer = consumers_info()
   account = account_info()
   usageRecord = usage_record()
   brgy_listval = []
   context = {
      "alert_msg":"",
   }
   all_consumer = consumers_info.objects.all()
   ratename = ReqParams.rateid_name

   acc = ""
   accountid = ""
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
   installcount = "1"
   profilepicform = Profilepic(request.POST,request.FILES)

   #accountinfo
   meterNum = request.POST.get(ReqParams.meter_num)
   address_installation = request.POST.get(ReqParams.address)
   duedate = request.POST.get(ReqParams.duedate)
   rate_id = request.POST.get(ReqParams.rateid)
   status = request.POST.get(ReqParams.status)
   initialreading = request.POST.get(ReqParams.initialreading)
   brgy = request.POST.get(ReqParams.barangay)#of installation
   context1 = {
      "error_msg":"",
      "lastname" : "",
      "firstname" : "",
      "middlename" : "",
      "bday" : "",
      "sex" : ReqParams.maleval,
      "email" : "",
      "mobile1" : "",
      "mobile2" : "",
      "address" : "",
      "barangay" : "1",
      "sitio" : "",
      "homeaddress":"Anao,Ginatilan,Cebu",

      #accountinfo
      "meterNum" : "",
      "address_installation" : "1",
      "duedate" : "",
      "rate_id" : "1",
      "rate_name" : "Residential",
      "status" : "",
      "initialreading" :"",
      "brgy" : "1",
      "address":"Anao,Ginatilan,Cebu"
   }
   #barangay names


   #rendering page
   template = ""
   sessionval = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/add_new_consumer.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   context[ReqParams.userid] = request.session.get(ReqParams.userid)
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)
   search_for = request.POST.get("search_for")


   if request.method == "POST":

      ismatch = 1
      #barangay names
      barangay_name1 = ReqParams.barangay_list[int(barangay) - 1]
      barangay_name2 = ReqParams.barangay_list[int(brgy) - 1]
      context["barangay_name1"] = barangay_name1
      context["barangay_name2"] = barangay_name2
      context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)



      #we check the meter number
      if account_info.objects.filter(meternumber = meterNum).exists():
         context["alert_msg"] = "Ooopss! Something went wrong!"
         context1 = {
         "error_msg":"Already Exists!",
         "lastname" : request.POST.get(ReqParams.lname),
         "firstname" : request.POST.get(ReqParams.fname),
         "middlename" : request.POST.get(ReqParams.mname),
         "bday" : request.POST.get(ReqParams.birthday),
         "sex" : request.POST.get(ReqParams.sex),
         "email" : request.POST.get(ReqParams.email),
         "mobile1" : request.POST.get(ReqParams.mobile1),
         "mobile2" : request.POST.get(ReqParams.mobile2),
         "address" : request.POST.get(ReqParams.add),
         "barangay" : request.POST.get(ReqParams.barangay),
         "sitio" : request.POST.get(ReqParams.sitio),
         "homeaddress":barangay_name1 + ",Ginatilan,Cebu",

         #accountinfo
         "meterNum" : request.POST.get(ReqParams.meter_num),
         "address_installation" : request.POST.get(ReqParams.address),
         "duedate" : request.POST.get(ReqParams.duedate),
         "rate_id" : request.POST.get(ReqParams.rateid),
         "rate_name" : ratename[request.POST.get(ReqParams.rateid)],
         "status" : request.POST.get(ReqParams.status),
         "initialreading" : request.POST.get(ReqParams.initialreading),
         "brgy" : request.POST.get(ReqParams.barangay),
         "address":barangay_name2 + ",Ginatilan,Cebu"
      }

         return render(request,template,{'ReqParams':ReqParams,"context1":context1,"context":context,"list_of_consumers":all_consumer})
      else:
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

         consumer.consumerid = accstr
         consumer.oldconsumerid = accstr
         keybasis.lastid_used =  lastid + 1
         consumer.lastname = lastname
         consumer.firstname = firstname
         consumer.middlename = middlename
         consumer.sex = sex
         consumer.birthday = bday
         consumer.emailaddress = email
         consumer.mobilenumber = mobile1
         consumer.mobilenumber2 = mobile2
         consumer.homeaddress = barangay_name1 + ",Ginatilan,Cebu"
         consumer.installcount = 1;
         consumer.barangay = barangay
         consumer.sitio = sitio
         consumer.profilepic = request.FILES.get(ReqParams.profilepic)


         if request.FILES.get(ReqParams.profilepic) != "":
            if profilepicform.is_valid():
               handle_uploaded_file(request.FILES[ReqParams.profilepic])
            else:
               profilepicform = Profilepic()
               print("error")


         #we set the account info
         account.firstname = firstname
         account.middlename = middlename
         account.lastname = lastname
         account.meternumber = meterNum
         account.initial_meter_reading = initialreading
         account.barangay = brgy
         account.address = barangay_name2 + ",Ginatilan,Cebu"
         account.rateid = rate_id

         if len(str(installcount)) < 2:
            withzero = "0"
         else:
            withzero = ""

         account.accountinfoid = accstr + "-" + withzero  + installcount
         account.consumerid = consumer



         #we make an usage record for new / existing consumer
         id_str = accountid
         current_year = date.today()
         get_year = str(current_year.year)
         usage_id_str = account.accountinfoid + "-" + get_year
         usageRecord.accountid = usage_id_str#pk value
         usageRecord.rateid = rate_id
         usageRecord.consumerid = consumer
         usageRecord.accountinfoid = account.accountinfoid
         consumer.save()
         keybasis.save()
         account.save()
         usageRecord.save()

         messages.success(request, 'Successfully added!')

         pathstr = "/source_access" + "/add-new-consumer"
         return HttpResponseRedirect((pathstr))


   return render(request,template,{'ReqParams':ReqParams,"context1":context1,"context":context,"list_of_consumers":all_consumer})

def view_consumer_list(request):
   consumer = consumers_info()
   context = {}
   all_consumer = account_info.objects.all()
   consumer_list = []
   #rendering page
   template = ""
   sessionval = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/consumer_list.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   context[ReqParams.userid] = request.session.get(ReqParams.userid)
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)
   search_for = request.POST.get("search_for")

   consumer_list = None
   if consumers_info.objects.filter(deleted_flag = "0").exists():
      consumer_list = consumers_info.objects.filter(deleted_flag = "0")


   return render(request,template,{'ReqParams':ReqParams,"context":context,"list_of_consumers":all_consumer})



def search(request,search_val):#method for searching consumer
   all_accounts = consumers_info.objects.all()
   retval = all_accounts
   each_account = []
   context = []
   barangay_name = []
   index = 0


   if search_val != None:
      isMatch_for_fname = consumers_info.objects.filter(firstname__icontains=search_val) # getting all of the value of search_for int collunm firstname
      isMatch_for_lname = consumers_info.objects.filter(lastname__icontains=search_val) #and so on
      isMatch_for_acc = consumers_info.objects.filter(consumerid__icontains=search_val)

      if isMatch_for_fname:
         retval = isMatch_for_fname
      elif isMatch_for_lname:
         retval = isMatch_for_lname
      elif isMatch_for_acc:
         retval = isMatch_for_acc
      else:
         retval = messages.error(request,"No Result Found!")
   else:
      for account in all_accounts:
         if index != 25:#display only 25 accounts
            each_account.append(account)
            context.append(account)
            index += 1
         else:
            all_accounts = None

            retval = context

   return retval

def search_account(request,search_val):#method for searching accounts
   all_accounts = account_info.objects.all()
   retval = all_accounts
   each_account = []
   context = []
   barangay_name = []
   index = 0


   if search_val != None:
      isMatch_for_fname = consumers_info.objects.filter(firstname__icontains=search_val) # getting all of the value of search_for int collunm firstname
      isMatch_for_lname = consumers_info.objects.filter(lastname__icontains=search_val) #and so on
      isMatch_for_acc = consumers_info.objects.filter(consumerid__icontains=search_val)

      if isMatch_for_fname:
         retval = isMatch_for_fname
      elif isMatch_for_lname:
         retval = isMatch_for_lname
      elif isMatch_for_acc:
         retval = isMatch_for_acc
      else:
         retval = messages.error(request,"No Result Found!")
   else:
      for account in all_accounts:
         if index != 25:#display only 25 accounts
            each_account.append(account)
            context.append(account)
            index += 1
         else:
            all_accounts = None

            retval = context

   return retval


def search_account_record(request,search_val):#method for searching account record
   all_accounts = usage_record.objects.all()
   retval = all_accounts
   context = []
   if search_val != None:
      isMatch_for_acc = usage_record.objects.filter(accountid__icontains=search_val)

      if isMatch_for_acc:
         retval = isMatch_for_acc
   else:
      for account in all_accounts:
         context.append(account)
      retval = context

   return retval


def search_to_update_account(request):
   template = "html/search_to_update.account.html"
   sessionval = ReqParams.TELLER_LOGIN_VAL
   context = {}
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.userid] = request.session.get(ReqParams.userid)
   search_for = request.POST.get("search_for")



   return render(request,render_page(request,sessionval,template),{"accounts":search(request,search_for),"context":context})


def destroy(request, id):
   current_date = date.today()
   consumer = consumers_info.objects.get(pk = id)
   account = account_info.objects.filter(consumerid = consumer.consumerid)
   accountrecord = usage_record.objects.filter(consumerid = consumer.consumerid)

   has_balance = 0
   for record in accountrecord:
      if record.commulative_bill != 0:
         has_balance += 1

   if has_balance == 0:
      #we delete
      consumer.deleted_flag = "1"
      consumer.save()
      for acc in account:
         acc.deleted_flag = "1"
         acc.save()
      for record in accountrecord:
         record.delete()
   else:
      pass

   pathstr = "/source_access/view-consumer-list"
   return HttpResponseRedirect(pathstr)


def delete_user(request,id):
   user = SystemUser.objects.get(pk = id)
   user.delete()
   pathstr = "/source_access/add_new_authorized_personel"
   return HttpResponseRedirect(pathstr)


def delete_account(request,id):
   current_date = date.today()
   account = account_info.objects.get(pk = id)

   accountrecord = usage_record.objects.filter(accountinfoid = account.accountinfoid)
   latest_account = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))

   if latest_account.commulative_bill != 0:
      #we cant delete account
      pathstr = "/source_access/view-suspended-account"
      return HttpResponseRedirect(pathstr)
   else:
      #we delete all accountrecord
      for record in accountrecord:
         #we delete
         record.delete()

      account.deleted_flag = "1"
      account.save()
      pathstr = "/source_access/view-suspended-account"
      return HttpResponseRedirect(pathstr)


def suspend_account(request,id):
   context = {
      "error_msg":"",
   }

   current_date = date.today()
   account = account_info.objects.get(pk = id)
   consumer = consumers_info.objects.get(consumerid = account.consumerid)
   accountrecord = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))

   if accountrecord.commulative_bill != 0:
      pathstr = "/source_access/update-this-consumer=" + consumer.consumerid
      return HttpResponseRedirect(pathstr)
   else:
      account.status = ReqParams.status_inactive_val
      account.save()

def activate_account(request,id):
   account = account_info.objects.get(pk = id)
   account.status = ReqParams.status_active_val
   account.save()
   pathstr = "/source_access/view-suspended-account"
   return HttpResponseRedirect(pathstr)

def login(request):
   ReportGenerator.AutoCreate_NewRecord()
   user = request.POST.get(ReqParams.userid)
   password = request.POST.get(ReqParams.PASS)
   remember_me = request.POST.get("remember_me")
   pathstr = ""
   UserType = ""
   if user != None:
      context = {
         "userid" : user
      }
   else:
      context = {
         "userid" : ""
      }
   if request.method == "POST":
      pkval = SystemUser.objects.filter(userid = user)
      if pkval.exists():
         userid = SystemUser.objects.get(userid = user)
         #convert into base64
         passAscii = password.encode("ascii")
         passBytes = base64.b64encode(passAscii)
         print(userid.password)

         if userid.password == passBytes:
            request.session[ReqParams.LOGIN_SESSION] = userid.usertype
            request.session[ReqParams.userid] = userid.userid
            request.session[ReqParams.postedby] = userid.firstname + " " + userid.lastname
            request.session[ReqParams.name] = userid.firstname
            request.session[ReqParams.email] = userid.emailaddress

            if userid.usertype == ReqParams.TELLER_LOGIN_VAL:
               pathstr =  "/source_access/Payment"
               return redirect(pathstr)
            pathstr =  "/source_access"
            return redirect(pathstr)
         else:
            context["ErrorMessagePass"] = "Wrong Password!"
            return render(request,'html/index.html',{'ReqParams':ReqParams,"UserType":UserType,"User":user,"context":context})

      else:
         context["ErrorMessageId"] = "User ID does not exist!"
         return render(request,'html/index.html',{'ReqParams':ReqParams,"UserType":UserType,"User":user,"context":context})

   return render(request,'html/index.html',{'ReqParams':ReqParams,"UserType":UserType,"User":user,"context":context})

def source_access(request):
   context = {
      "userid":request.session.get(ReqParams.userid),
      "name":request.session.get(ReqParams.name),
      "UserType": request.session.get(ReqParams.LOGIN_SESSION)
   }
   return render(request,"html/source_access.html",{"context":context})





def logout(request):
   request.session.flush()#reset all data in session

   return redirect("/")

def manual(request):
   template = "html/Start.html"

   return render(request,"html/Start.html")

def admin(request):
   template = "html/admin.html"

   return render(request,"html/admin.html")

def metereader(request):
   template = "html/meterreader.html"

   return render(request,"html/meterreader.html")

def mayor(request):
   template = "html/mayor.html"

   return render(request,"html/mayor.html")

def teller(request):
   template = "html/teller.html"

   return render(request,"html/teller.html")

def checkers(request):
   template = "html/checkers.html"

   return render(request,"html/checkers.html")

def engineer(request):
   template = "html/engineer.html"

   return render(request,"html/engineer.html")

def manager(request,id):
   template = "html/manager.html"
   sessionval = ReqParams.MANAGER_LOGIN_VAL
   context = {}
   context[ReqParams.userid] = request.session.get(ReqParams.userid)

   return render(request,render_page(request,sessionval,template),{"context":context})

def test(request):

   ReportGenerator.getTotalBills(request)
   message = "Data Transfer Successful!!"
   return render(request,"test.html",{"message":message})



def view_account(request):
   search_for = request.POST.get("search_for")
   acc = request.POST.get("accountid")
   applicantid = request.POST.get("applicantid")
   context = {
      "msg":""
   }


   if request.method == "POST":

      if acc:
         if account_info.objects.filter(accountinfoid = acc).exists():
            account =  account_info.objects.get(accountinfoid = acc)
            pathstr = "/application=" + account.accountinfoid
            return HttpResponseRedirect(pathstr)
         elif account_info.objects.filter(meternumber = acc).exists():
            account =  account_info.objects.get(meternumber = acc)
            pathstr = "/application=" + account.accountinfoid
            return HttpResponseRedirect(pathstr)
         else:
            context["msg"] = "Not Found!"
            return render(request,"html/consumerLogIn.html",{"context":context})



      if applicantid:
         if Applicants_info.objects.filter(pk = applicantid).exists():
            pathstr = "/view-application-status=" + applicantid
            return HttpResponseRedirect(pathstr)
         else:
            context["msg"] = "Not Found!"
            return render(request,"html/consumerLogIn.html",{"context":context})

      if search_for:
         if account_info.objects.filter(accountinfoid = search_for).exists():
            account =  account_info.objects.get(accountinfoid = search_for)
            pathstr = "/account=" + account.accountinfoid
            return HttpResponseRedirect(pathstr)
         elif account_info.objects.filter(meternumber = search_for).exists():
            account =  account_info.objects.get(meternumber = search_for)
            pathstr = "/account=" + account.accountinfoid
            return HttpResponseRedirect(pathstr)
         else:
            context["msg"] = "Not Found!"
            return render(request,"html/consumerLogIn.html",{"context":context})



   return render(request,"html/consumerLogIn.html",{"context":context})

def consumer_view(request,id):
   account = None
   if account_info.objects.filter(accountinfoid = id).exists():
      account = account_info.objects.get(accountinfoid = id)
   elif account_info.objects.filter(meternumber = id).exists():
      account = account_info.objects.get(meternumber = id)

   current_date = date.today()
   context = {
      "name" : account.firstname
   }

   idstr = account.accountinfoid + "-" + str(current_date.year)
   pkstr = usage_record.objects.get(accountid = idstr)

   context["balance"] = str(pkstr.commulative_bill)
   context["Fullname"] = account.firstname + " " + account.lastname
   context[ReqParams.address] = account.address
   template = ""


   PaidStatus = ["Not Paid","Paid"]
   ErrorMessagePass = ""
   index = 0
   commulative_bill = 0
   current_date = date.today()
   year_request = request.POST.get(ReqParams.year)
   consumer = consumers_info.objects.get(pk = account.consumerid)

   oldconsumer = None
   if OldCosumerInfo.objects.filter(pk = consumer.oldconsumerid).exists():
      oldconsumer = OldCosumerInfo.objects.get(pk = consumer.oldconsumerid)

   accountidstr = account.accountinfoid + "-" + str(current_date.year)
   accountrecord = usage_record.objects.get(pk = accountidstr)
   #dropdown values
   current_year = current_date.year
   year_list = []
   #default value
   retval = []
   defval_year = str(current_year)
   prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
   readingdate = ""
   for record in  prev_record:
      if record.reading_date.__contains__(str(defval_year)):
         retval.append(record)
         index = index + 1

   new_record = None
   #get the latest bill
   latest_record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))
   commulative_bill = latest_record.commulative_bill

   #for record that has been updated/posted on this new System
   if year_request == None:
      new_record =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(defval_year))
   else:
      new_record = None

   #year to choose,from year 2010 until today
   while current_year >= 2010:
      year_list.append(current_year)
      current_year = current_year - 1


   if request.method == "POST":
      retval = []
      index = 0
      if year_request:
         prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
         defval_year = year_request
         for record in  prev_record:
            if record.reading_date.__contains__(str(year_request)):
               retval.append(record)
               index = index + 1

         #for record that has been updated/posted on this new System
         if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(defval_year)).exists():
            new_record =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(defval_year))



   return render(request,"html/consumer.html",{"year_list":year_list,"retval":retval,"consumer":consumer,"ErrorMessagePass":ErrorMessagePass,"context":context,
                        "PaidStatus":PaidStatus,"ReqParams":ReqParams,"defval_year":defval_year,"oldcon":oldconsumer,"account":account,
                        "new_record":new_record,"index":index,"commulative_bill":commulative_bill})







def get_csv(request):
   current_date = date.today()
   account = account_info.objects.all()
   consumer = consumers_info()
   getrecord = usage_record()
   response = HttpResponse()
   response['Content-Disposition'] = 'attachment; filename="bill.csv"'
   writer = csv.writer(response)
   writer.writerow(["Mobile Number(1)","Mobile Number(2)","Account ID","Meter Number","Previous Reading","Current Reading","Previous Bill","Total Bill","Total Balance"])

   for acc in account:
      accountidstr = acc.accountinfoid + "-" + str(current_date.year)
      consumer = consumers_info.objects.get(pk = acc.consumerid)
      if usage_record.objects.filter(pk = accountidstr).exists():
         thisrecord = usage_record.objects.get(pk = accountidstr)
         previous_reading = ""
         previous_bill = ""
         current_reading = ""
         current_bill = ""
         if current_date.month == 1:
            current_reading = str(thisrecord.reading_jan)
            current_bill = str(thisrecord.totalbill_jan)
            previous_recordstr = acc.accountinfoid + "-" + str(current_date.year - 1)
            if usage_record.objects.filter(pk = previous_recordstr).exists():
               getrecord = usage_record.objects.get(pk = previous_recordstr)
               previous_bill = str(getrecord.totalbill_dec)
               previous_reading = str(getrecord.reading_dec)
            else:
               pass

         elif current_date.month == 2:
            current_bill = str(thisrecord.totalbill_feb)
            current_reading = str(thisrecord.reading_feb)
            previous_bill = str(thisrecord.totalbill_jan)
            previous_reading = str(getrecord.reading_jan)
         elif current_date.month == 3:
            current_bill = str(thisrecord.totalbill_mar)
            current_reading = str(thisrecord.reading_mar)
            previous_bill = str(thisrecord.totalbill_feb)
            previous_reading = str(getrecord.reading_feb)
         elif current_date.month == 4:
            current_bill = str(thisrecord.totalbill_apr)
            current_reading = str(thisrecord.reading_apr)
            previous_bill = str(thisrecord.totalbill_mar)
            previous_reading = str(getrecord.reading_mar)
         elif current_date.month == 5:
            current_bill = str(thisrecord.totalbill_may)
            current_reading = str(thisrecord.reading_may)
            previous_bill = str(thisrecord.totalbill_apr)
            previous_reading = str(getrecord.reading_apr)
         elif current_date.month == 6:
            current_bill = str(thisrecord.totalbill_jun)
            current_reading = str(thisrecord.reading_jun)
            previous_bill = str(thisrecord.totalbill_may)
            previous_reading = str(getrecord.reading_may)
         elif current_date.month == 7:
            current_bill = str(thisrecord.totalbill_jul)
            current_reading = str(thisrecord.reading_jul)
            previous_bill = str(thisrecord.totalbill_jun)
            previous_reading = str(getrecord.reading_jun)
         elif current_date.month == 8:
            current_bill = str(thisrecord.totalbill_aug)
            current_reading = str(thisrecord.reading_aug)
            previous_bill = str(thisrecord.totalbill_jul)
            previous_reading = str(getrecord.reading_jul)
         elif current_date.month == 9:
            current_bill = str(thisrecord.totalbill_sept)
            current_reading = str(thisrecord.reading_sept)
            previous_bill = str(thisrecord.totalbill_sept)
            previous_reading = str(getrecord.reading_aug)
         elif current_date.month == 10:
            current_bill = str(thisrecord.totalbill_oct)
            current_reading = str(thisrecord.reading_oct)
            previous_bill = str(thisrecord.totalbill_sept)
            previous_reading = str(getrecord.reading_sept)
         elif current_date.month == 11:
            current_bill = str(thisrecord.totalbill_nov)
            current_reading = str(thisrecord.reading_nov)
            previous_bill = str(thisrecord.totalbill_oct)
            previous_reading = str(getrecord.reading_oct)
         elif current_date.month == 12:
            current_bill = str(thisrecord.totalbill_dec)
            current_reading = str(thisrecord.reading_dec)
            previous_bill = str(thisrecord.totalbill_nov)
            previous_reading = str(getrecord.reading_nov)



         writer.writerow([consumer.mobilenumber,consumer.mobilenumber2,acc.accountinfoid,acc.meternumber,previous_reading,current_reading,previous_bill,current_bill,str(thisrecord.commulative_bill)])


   return response

def render_to_pdf(template_src, context_dict={}):
   template = get_template(template_src)
   html = template.render(context_dict)
   result = BytesIO()
   pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
   if not pdf.err:
      return result.getvalue()
   return None


def forgot_password(request):
   template = "html/forgotpassword.html"
   search_for = request.POST.get("search_for")
   accountObj = ""
   # generating random digits(string)
   letters = string.digits
   verification_code_str = ""
   verification_code = ( ''.join(random.choice(letters) for i in range(10)))
   code_len = len(verification_code)
   i = 0
   while i < code_len:
      verification_code_str += verification_code[i]
      i += 1

   request.session[ReqParams.verification_code] = verification_code_str
   sendflag = request.POST.get("send_flag")

   if request.method == "POST":

      if SystemUser.objects.filter(emailaddress = search_for).exists():
         accountObj = SystemUser.objects.filter(emailaddress = search_for)
      elif SystemUser.objects.filter(userid = search_for).exists():
         accountObj = SystemUser.objects.filter(userid = search_for)
      else:
         accountObj = ""

      return render(request,template,{"accountObj":accountObj})

   return render(request,template,{"accountObj":accountObj})



def Mybill(request,id):
   current_date = date.today()
   account = account_info.objects.get(pk = id)
   account_record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))
   template = "html/Mybill.html"

   month_reading = {
      0:account_record.reading_jan,
      1:account_record.reading_feb,
      2:account_record.reading_mar,
      3:account_record.reading_apr,
      4:account_record.reading_may,
      5:account_record.reading_jun,
      6:account_record.reading_jul,
      7:account_record.reading_aug,
      8:account_record.reading_sept,
      9:account_record.reading_oct,
      10:account_record.reading_nov,
      11:account_record.reading_dec,
   }
   bill = {
      "postedby0":account_record.reading_postedby_jan,
      "postedon0":account_record.reading_date_jan,
      "postedby1":account_record.reading_postedby_feb,
      "postedon1":account_record.reading_date_feb,
      "postedby2":account_record.reading_postedby_mar,
      "postedon2":account_record.reading_date_mar,
      "postedby3":account_record.reading_postedby_apr,
      "postedon3":account_record.reading_date_apr,
      "postedby4":account_record.reading_postedby_may,
      "postedon4":account_record.reading_date_may,
      "postedby5":account_record.reading_postedby_jun,
      "postedon5":account_record.reading_date_jun,
      "postedby6":account_record.reading_postedby_jul,
      "postedon6":account_record.reading_date_jul,
      "postedby7":account_record.reading_postedby_aug,
      "postedon7":account_record.reading_date_aug,
      "postedby8":account_record.reading_postedby_sept,
      "postedon8":account_record.reading_date_sept,
      "postedby9":account_record.reading_postedby_oct,
      "postedon9":account_record.reading_date_oct,
      "postedby10":account_record.reading_postedby_nov,
      "postedon10":account_record.reading_date_nov,
      "postedby11":account_record.reading_postedby_dec,
      "postedon11":account_record.reading_date_dec,

      "bill0":account_record.bill_jan,
      "penalty0":account_record.penalty_jan,
      "total0":account_record.totalbill_jan,
      "bill1":account_record.bill_feb,
      "penalty1":account_record.penalty_feb,
      "total1":account_record.totalbill_feb,
      "bill2":account_record.bill_mar,
      "penalty2":account_record.penalty_mar,
      "total2":account_record.totalbill_mar,
      "bill3":account_record.bill_apr,
      "penalty3":account_record.penalty_apr,
      "total3":account_record.totalbill_apr,
      "bill4":account_record.bill_may,
      "penalty4":account_record.penalty_may,
      "total4":account_record.totalbill_may,
      "bill5":account_record.bill_jun,
      "penalty5":account_record.penalty_jun,
      "total5":account_record.totalbill_jun,
      "bill6":account_record.bill_jul,
      "penalty6":account_record.penalty_jul,
      "total6":account_record.totalbill_jul,
      "bill7":account_record.bill_aug,
      "penalty7":account_record.penalty_aug,
      "total7":account_record.totalbill_aug,
      "bill8":account_record.bill_sept,
      "penalty8":account_record.penalty_sept,
      "total8":account_record.totalbill_sept,
      "bill9":account_record.bill_oct,
      "penalty9":account_record.penalty_oct,
      "total9":account_record.totalbill_oct,
      "bill10":account_record.bill_nov,
      "penalty10":account_record.penalty_nov,
      "total10":account_record.totalbill_nov,
      "bill11":account_record.bill_dec,
      "penalty11":account_record.penalty_dec,
      "total11":account_record.totalbill_dec,
   }
   context = {
      "meternumber":account.meternumber,
      "accountinfoid":account.accountinfoid,
      "name":account.firstname + " " + account.lastname,
      "address":account.address,
      "msg":""
   }

   if month_reading[current_date.month - 2] != 0:
      context["month"] = ReqParams.month_name[current_date.month - 2]
      context["postedby"] = bill["postedby" + str(current_date.month - 2)]
      context["postedon"] = bill["postedon" + str(current_date.month - 2)]
      context["current_reading"] = month_reading[current_date.month - 2]
      context["previous_reading"] =  month_reading[current_date.month - 3]
      context["usage"] = month_reading[current_date.month - 2] - month_reading[current_date.month - 3]
      context["bill"] = bill["bill" + str(current_date.month - 2)]
      context["penalty"] = bill["penalty" + str(current_date.month - 2)]
      context["totalbill"] = bill["total" + str(current_date.month - 2)]
      context["prev_balance"] = account_record.commulative_bill - bill["total" + str(current_date.month - 2)]
      context["total_balance"] = account_record.commulative_bill
      return render(request,template,{"account":account,"context":context})
   else:
      context["msg"] = "Latest bill is not available at the moment."
      return render(request,template,{"account":account,"context":context})


def Developers(request):

   return render(request,"html/Pioneers.html")
