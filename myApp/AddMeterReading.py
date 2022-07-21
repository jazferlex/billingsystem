from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *
from django.template import Context
from datetime import date
from .BillingDB import *
import datetime
from django.contrib import messages
from myApp import ReportGenerator
from .BillingUtil import *
from BillingSystem import settings
from .views import *
from io import BytesIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.views import View
from xhtml2pdf import pisa
from smtplib import SMTPException
from myApp import MeterReadingModification
import unicodedata


EMAIL_HOST_USER = settings.EMAIL_HOST_USER


def render_to_pdf(template_src, context_dict={}):
   template = get_template(template_src)
   html = template.render(context_dict)
   result = BytesIO()
   pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
   if not pdf.err:
      return result.getvalue()
   return None


def add_meter_reading(request,id):
   
   if "execute" not in request.session:
      get_stop_meter()
      request.session["execute"] = "1"
      print("execute")

   #We call our Auto Create method
   ReportGenerator.AutoCreate_NewRecord()

   current_date = date.today()
   month_name = ReqParams.month_name
   context = {
      "month_name":month_name[current_date.month - 2],
      "month_val":current_date.month - 1,
      "error_msg":"",
      "userid":request.session.get(ReqParams.userid)
   }

   year_of_reading = 0
   month_reading = request.POST.get("month")
   reading = request.POST.get("reading")
   year_of_reading = ""

   template = ""
   sessionval = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.INPUTREADER_LOGIN_VAL):
         template = "html/input-reading.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   revenue = revenuecode.objects.get(pk = "1")
   #sessions
   userid = request.session.get(ReqParams.userid)
   getuser = SystemUser.objects.get(pk = userid)
   fullname = getuser.firstname + " " + getuser.lastname

   context[ReqParams.name] = getuser.firstname
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)
   context["month"] = ReqParams.barangay_list[current_date.month - 1]

   
   

   pathstr = "/source_access/add-meter-reading/" + id

   #request
   readingjan = request.POST.get("readingjan")
   readingfeb = request.POST.get("readingfeb")
   readingmar = request.POST.get("readingmar")
   readingapr = request.POST.get("readingapr")
   readingmay = request.POST.get("readingmay")
   readingjun = request.POST.get("readingjun")
   readingjul = request.POST.get("readingjul")
   readingaug = request.POST.get("readingaug")
   readingsept = request.POST.get("readingsept")
   readingoct = request.POST.get("readingoct")
   readingnov = request.POST.get("readingnov")
   readingdec = request.POST.get("readingdec")
   user = SystemUser.objects.get(pk = request.session.get(ReqParams.userid))

   #year selection
   year_list = []
   accountrecord = usage_record.objects.filter(accountinfoid = id) 
   #for dropdown values(year)
   for element in accountrecord:
      year_list.append(element.year)
   year_list.append(current_date.year)  
   defval_year = current_date.year
   year_request = request.POST.get("year")

   account = account_info.objects.get(pk = id)
   
   if year_request:
      accountidstr = account.accountinfoid + "-" + str(year_request)
      thisrecord = usage_record.objects.get(pk = accountidstr)
      defval_year = year_request
   else:
      accountidstr = account.accountinfoid + "-" + str(defval_year)
      thisrecord = usage_record.objects.get(pk = accountidstr)

   if request.method == "POST":

      if account_info.objects.filter(pk = id).exists():
         account = account_info.objects.get(pk = id)
         
         accountid = account.accountinfoid
         if year_request:
            if month_reading == 1:#reading for december will be update on january
               year_of_reading = str(int(year_request) - 1)
            else:
               year_of_reading = str(year_request)
            defval_year = year_request  
         else:
            year_of_reading = str(current_date.year)      

         account_record = usage_record.objects.get(pk = account.accountinfoid + "-" + year_of_reading)
         #last_reading = account_record.previous_reading
         #rate
         rateid = account.rateid
         rate = rates.objects.get(rateid = rateid)
         initial_meter_reading = account.initial_meter_reading


         #get consumer info
         get_consumer = account_info.objects.get(pk =id)
         consumerid_val = get_consumer.consumerid
         consumer_obj = consumers_info.objects.get(pk = consumerid_val)

         get_current_year = current_date.year
         consumerID = accountid + "-" + year_of_reading
         usageID  = usage_record.objects.get(pk = consumerID) #pk value
         

         #january
         if readingjan:
            #reports pk
            reading = readingjan
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            get_year = current_date.year
            prev_year = get_year - 1
            prev_year_str = str(prev_year)

            #we get the usage from  december last year
            usageRecord = usage_record()
            usage_id_str = accountid + "-" + prev_year_str

            #we check if the consumer has a record last year

            consumerID = accountid + "-" + year_of_reading
            usageID  = usage_record.objects.get(pk = consumerID) #pk value

            if usage_record.objects.filter(accountid = usage_id_str).exists():

               getUsageId = usage_record.objects.get(pk = usage_id_str)
               lastdec_reading = getUsageId.previous_reading #last december reading
               lastdec_commu_bill = getUsageId.commulative_bill # last december commulative bill or unpaid bill
               lastdec_excesspay = getUsageId.excesspayment #last december excess payment
               lastyear_due = getUsageId.prevyeardue #last year due

               

               if float(reading) < lastdec_reading:
                  context["error_msg"] = "Invalid Input!"
                  return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})


               #penalty flag increments
               if usageID.commulative_bill != 0:
                  account.penalty_flag += 1
                  account.save()
               else:
                  account.penalty_flag = 0
                  account.save()

               #we set the present consumption
               usageID.commulative_bill = lastdec_commu_bill
               usageID.excesspayment = lastdec_excesspay
               usageID.prevyeardue = lastyear_due
               usageID.reading_jan = float(reading)
               usageID.reading_date_jan = str(current_date)
               usageID.dateposted_jan = str(current_date)
               usageID.reading_postedby_jan = fullname
               usageID.usage_jan = float(reading) - lastdec_reading
               usageID.previous_reading = float(reading)
               usageID.reading_postedby_jan = user.firstname + " " + user.lastname
               usageID.reading_date_jan = str(current_date)

               #we generate the bill
               if usageID.usage_jan != 0:
                  if rateid == ReqParams.residential: #residential

                     if usageID.usage_jan <= rate.minimumreading and usageID.usage_jan > 0:
                        usageID.bill_jan = rate.minimumreading_charge
                     else:
                        excess_cubic =  usageID.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        usageID.bill_jan = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_jan <= rate.minimumreading and usageID.usage_mar > 0:
                        usageID.bill_jan = rate.minimumreading_charge
                     else:
                        excess_cubic =  usageID.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        usageID.bill_jan = excess_mincharge +  rate.minimumreading_charge

               #penalty
               if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                  #via percentage
                  if revenue.percentage_penalty != 0:
                     xy = revenue.percentage_penalty * usageID.commulative_bill
                     interest = xy / 100
                     usageID.penalty_jan = interest

                  if revenue.fix_amount_penalty:
                     interest = revenue.fix_amount_penalty
                     usageID.penalty_jan = interest

               usageID.totalbill_jan = usageID.bill_jan + usageID.penalty_jan
               usageID.commulative_bill = lastdec_commu_bill + usageID.totalbill_jan
               getUsageId = usage_record

               #we set the total due
               yearly_record.total_due_january += usageID.totalbill_jan
               yearly_record.total_due_ytd += usageID.totalbill_jan
               yearly_record.usage_january += usageID.usage_jan
               yearly_record.total_usage += usageID.usage_jan
               yearly_record.save()

               brgy = account.barangay + "-" + year_of_reading
               if barangay_report.objects.filter(pk = brgy).exists():
                  barangay_record = barangay_report.objects.get(pk = brgy)
                  total_bill_jan = usageID.totalbill_jan
                  barangay_record.total_due_january += total_bill_jan
                  barangay_record.total_due_ytd += total_bill_jan
                  barangay_record.usage_january += usageID.usage_jan
                  barangay_record.total_usage += usageID.usage_jan
                  barangay_record.save()


               # excess payment affects commulative bill
               if usageID.excesspayment != 0:
                  if usageID.excesspayment > usageID.totalbill_jan:
                     usageID.excesspayment = usageID.excesspayment - usageID.totalbill_jan
                     usageID.commulative_bill = 0
                     usageID.save()
                  elif usageID.excesspayment < usageID.totalbill_jan:
                     usageID.commulative_bill = usageID.totalbill_jan - usageID.excesspayment
                     usageID.excesspayment = 0
                     usageID.save()
               else:
                  usageID.save()

               return HttpResponseRedirect(pathstr)


            elif initial_meter_reading != -1: #new Consumer has an initial meter reading
               #reports pk
               brgy = account.barangay + "-" + year_of_reading
               barangay_record = barangay_report.objects.get(pk = brgy)
               yearly_record = Year_Report.objects.get(pk = year_of_reading)

               

               if float(reading) < initial_meter_reading:
                  context["error_msg"] = "Invalid Input!"
                  return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

               #penalty flag increments
               if usageID.commulative_bill != 0:
                  account.penalty_flag += 1
                  account.save()
               else:
                  account.penalty_flag = 0
                  account.save()

               usageID.reading_jan = float(reading)
               usageID.reading_date_jan = str(current_date)
               usageID.dateposted_jan = str(current_date)
               usageID.reading_postedby_jan = fullname
               usageID.usage_jan =  float(reading) - initial_meter_reading
               usageID.previous_reading =  float(reading)
               usageID.reading_postedby_jan = user.firstname + " " + user.lastname
               usageID.reading_date_jan = str(current_date)


               #we generate the bill
               if usageID.usage_jan != 0:
                  if rateid == ReqParams.residential:  #residential

                     if usageID.usage_jan <= rate.minimumreading and usageID.usage_jan > 0:
                        usageID.bill_jan = rate.minimumreading_charge

                     else:
                        excess_cubic =  usageID.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        usageID.bill_jan = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_jan <= rate.minimumreading and usageID.usage_jan > 0:
                        usageID.bill_jan = rate.minimumreading_charge

                     else:
                        excess_cubic =  usageID.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        usageID.bill_jan = excess_mincharge +  rate.minimumreading_charge

               #penalty
               if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                  #via percentage
                  if revenue.percentage_penalty != 0:
                     xy = revenue.percentage_penalty * usageID.commulative_bill
                     interest = xy / 100
                     usageID.penalty_jan = interest

                  if revenue.fix_amount_penalty:
                     interest = revenue.fix_amount_penalty
                     usageID.penalty_jan = interest

               account.initial_meter_reading = -1
               usageID.totalbill_jan = usageID.bill_jan + usageID.penalty_jan
               usageID.commulative_bill =  usageID.totalbill_jan

               #we set the total due
               yearly_record.total_due_january += usageID.totalbill_jan
               yearly_record.total_due_ytd += usageID.totalbill_jan
               yearly_record.usage_january += usageID.usage_jan
               yearly_record.total_usage += usageID.usage_jan
               yearly_record.save()

               brgy = account.barangay + "-" + year_of_reading
               if barangay_report.objects.filter(pk = brgy).exists():
                  barangay_record = barangay_report.objects.get(pk = brgy)
                  total_bill_jan = usageID.totalbill_jan
                  barangay_record.total_due_january += total_bill_jan
                  barangay_record.total_due_ytd += total_bill_jan
                  barangay_record.usage_january += usageID.usage_jan
                  barangay_record.total_usage += usageID.usage_jan
                  barangay_record.save()

               # excess payment affects commulative bill
               if usageID.excesspayment != 0:
                  if usageID.excesspayment > usageID.totalbill_jan:
                     usageID.excesspayment = usageID.excesspayment - usageID.totalbill_jan
                     usageID.commulative_bill = 0
                     usageID.save()
                     account.save()
                  elif usageID.excesspayment < usageID.totalbill_jan:
                     usageID.commulative_bill = usageID.totalbill_jan - usageID.excesspayment
                     usageID.excesspayment = 0
                     usageID.save()
                     account.save()
               else:
                  usageID.save()
                  account.save()

               return HttpResponseRedirect(pathstr)

            #Modify
            elif usageID.reading_jan > 0 and readingjan:
               MeterReadingModification.Modify_function(request,id,1,float(reading),year_of_reading)



         ###$#######

         #February
         if readingfeb:
            last_reading = usageID.reading_jan
            reading = readingfeb
            yearly_record = Year_Report.objects.get(pk = year_of_reading)
            print(reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               

               

               if usageID.reading_feb > 0 and readingfeb:
                     MeterReadingModification.Modify_function(request,id,"2",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_feb = float(reading)
                  usageID.reading_date_feb = str(current_date)
                  usageID.dateposted_feb = str(current_date)
                  usageID.reading_postedby_feb = fullname
                  usageID.usage_feb = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_feb = user.firstname + " " + user.lastname
                  usageID.reading_date_feb = str(current_date)


                  #we generate the bill
                  if usageID.usage_feb != 0:
                     if rateid == ReqParams.residential:  #residential

                        if usageID.usage_feb <= rate.minimumreading and usageID.usage_feb > 0:
                           usageID.bill_feb = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_feb - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_feb = excess_mincharge +  rate.minimumreading_charge

                     elif rateid == ReqParams.commercial:#commercial
                        if usageID.usage_feb <= rate.minimumreading and usageID.usage_feb > 0:
                           usageID.bill_feb = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_feb - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_feb = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_feb = interest

                     if revenue.fix_amount_penalty:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_feb = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_feb = usageID.bill_feb + usageID.penalty_feb
                  usageID.commulative_bill +=  usageID.totalbill_feb

                  #we set the total due
                  yearly_record.total_due_february += usageID.totalbill_feb
                  yearly_record.total_due_ytd += usageID.totalbill_feb
                  yearly_record.usage_february += usageID.usage_feb
                  yearly_record.total_usage += usageID.usage_feb
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_feb = usageID.totalbill_feb
                     barangay_record.total_due_february += total_bill_feb
                     barangay_record.total_due_ytd += total_bill_feb
                     barangay_record.usage_february += usageID.usage_feb
                     barangay_record.total_usage += usageID.usage_feb
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_feb:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_feb
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_feb:
                        usageID.commulative_bill = usageID.totalbill_feb - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()
                  return HttpResponseRedirect(pathstr)

            else:
              
               #we get the usage from lat month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due

               

               #we set the present consumption
               
               get_reading = usageID.reading_feb



               if usageID.reading_feb > 0 and readingfeb:
                     MeterReadingModification.Modify_function(request,id,"2",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_feb = float(reading)
                  usageID.usage_feb = float(reading) - last_reading
                  usageID.reading_date_feb = str(current_date)
                  usageID.dateposted_feb = str(current_date)
                  usageID.reading_postedby_feb = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_feb = user.firstname + " " + user.lastname
                  usageID.reading_date_feb = str(current_date)

                  #we generate the bill
                  if usageID.usage_feb != 0:
                     if rateid == ReqParams.residential: #residential

                        if usageID.usage_feb <= rate.minimumreading and usageID.usage_feb > 0:
                           usageID.bill_feb = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_feb - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_feb = excess_mincharge +  rate.minimumreading_charge

                     elif rateid == ReqParams.commercial:#commercial

                        if usageID.usage_feb <= rate.minimumreading and usageID.usage_feb > 0:
                           usageID.bill_feb = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_feb - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_feb = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_feb = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_feb = interest

                  usageID.totalbill_feb = usageID.bill_feb + usageID.penalty_feb
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_feb

                  #we set the total due

                  yearly_record.total_due_february += usageID.totalbill_feb
                  yearly_record.total_due_ytd += usageID.totalbill_feb
                  yearly_record.usage_february += usageID.usage_feb
                  yearly_record.total_usage += usageID.usage_feb
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_feb = usageID.totalbill_feb
                     barangay_record.total_due_february += total_bill_feb
                     barangay_record.total_due_ytd += total_bill_feb
                     barangay_record.usage_february += usageID.usage_feb
                     barangay_record.total_usage += usageID.usage_feb
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_feb:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_feb
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_feb:
                        usageID.commulative_bill = usageID.totalbill_feb - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)

         #March
         if readingmar:
            last_reading = usageID.reading_feb
            reading = readingmar
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               

               

               if usageID.reading_mar > 0 and readingmar: #Modify
                     MeterReadingModification.Modify_function(request,id,"3",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()


                  usageID.reading_mar = float(reading)
                  usageID.reading_date_mar = str(current_date)
                  usageID.dateposted_mar = str(current_date)
                  usageID.reading_postedby_mar = fullname
                  usageID.usage_mar = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_mar = user.firstname + " " + user.lastname
                  usageID.reading_date_mar = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_mar != 0:
                        if usageID.usage_mar <= rate.minimumreading and usageID.usage_mar > 0:
                           usageID.bill_mar = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_mar - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_mar = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_mar != 0:
                        if usageID.usage_mar <= rate.minimumreading and usageID.usage_mar > 0:
                           usageID.bill_mar = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_mar - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_mar = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_mar = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_mar = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_mar = usageID.bill_mar + usageID.penalty_mar
                  usageID.commulative_bill +=  usageID.totalbill_mar

                  #we set the total due
                  yearly_record.total_due_march += usageID.totalbill_mar
                  yearly_record.total_due_ytd += usageID.totalbill_mar
                  yearly_record.usage_march += usageID.usage_mar
                  yearly_record.total_usage += usageID.usage_mar
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_mar = usageID.totalbill_mar
                     barangay_record.total_due_march += total_bill_mar
                     barangay_record.total_due_ytd += total_bill_mar
                     barangay_record.usage_march += usageID.usage_mar
                     barangay_record.total_usage += usageID.usage_mar
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_mar:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_mar
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_mar:
                        usageID.commulative_bill = usageID.totalbill_mar - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)

            else:

               #we get the usage from last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due

               #we set the present consumption
               

               

               if usageID.reading_mar > 0 and readingmar: #Modify
                     MeterReadingModification.Modify_function(request,id,"3",float(reading),year_of_reading)

               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_mar = float(reading)
                  usageID.usage_mar = float(reading) - last_reading
                  usageID.reading_date_mar = str(current_date)
                  usageID.dateposted_mar = str(current_date)
                  usageID.reading_postedby_mar = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_mar = user.firstname + " " + user.lastname
                  usageID.reading_date_mar = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_mar != 0:
                        if usageID.usage_mar <= rate.minimumreading and usageID.usage_mar > 0:
                           usageID.bill_mar = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_mar - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_mar = excess_mincharge + rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_mar != 0:
                        if usageID.usage_mar <= rate.minimumreading and usageID.usage_mar > 0:
                           usageID.bill_mar = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_mar - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_mar = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_mar = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_mar = interest

                  usageID.totalbill_mar = usageID.bill_mar + usageID.penalty_mar
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_mar

                  #we set the total due
                  yearly_record.total_due_march += usageID.totalbill_mar
                  yearly_record.total_due_ytd += usageID.totalbill_mar
                  yearly_record.usage_march += usageID.usage_mar
                  yearly_record.total_usage += usageID.usage_mar
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_mar = usageID.totalbill_mar
                     barangay_record.total_due_march += total_bill_mar
                     barangay_record.total_due_ytd += total_bill_mar
                     barangay_record.usage_march += usageID.usage_mar
                     barangay_record.total_usage += usageID.usage_mar
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_mar:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_mar
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_mar:
                        usageID.commulative_bill = usageID.totalbill_mar - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)


         #April
         if readingapr:
            last_reading = usageID.reading_mar
            reading = readingapr
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               

               

               if usageID.reading_apr > 0 and readingapr: #Modify
                     MeterReadingModification.Modify_function(request,id,"4",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_apr = float(reading)
                  usageID.reading_date_apr = str(current_date)
                  usageID.dateposted_apr = str(current_date)
                  usageID.reading_postedby_apr = fullname
                  usageID.usage_apr = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_apr = user.firstname + " " + user.lastname
                  usageID.reading_date_apr = str(current_date)


                  #we generate the bill
                  excess_cubic = 0
                  excess_mincharge = 0
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_apr != 0:
                        if usageID.usage_apr <= rate.minimumreading and usageID.usage_apr > 0:
                           usageID.bill_apr = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_apr - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_apr = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_apr != 0:
                        if usageID.usage_apr <= rate.minimumreading and usageID.usage_apr > 0:
                           usageID.bill_apr = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_apr - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_apr = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_apr = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_apr = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_apr = usageID.bill_apr + usageID.penalty_apr
                  usageID.commulative_bill +=  usageID.totalbill_apr

                  #we set the total due
                  yearly_record.total_due_april += usageID.totalbill_apr
                  yearly_record.total_due_ytd += usageID.totalbill_apr
                  yearly_record.usage_april += usageID.usage_apr
                  yearly_record.total_usage += usageID.usage_apr
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_apr = usageID.totalbill_apr
                     barangay_record.total_due_april += total_bill_apr
                     barangay_record.total_due_ytd += total_bill_apr
                     barangay_record.usage_april += usageID.usage_apr
                     barangay_record.total_usage += usageID.usage_apr
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_apr:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_apr
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_apr:
                        usageID.commulative_bill = usageID.totalbill_apr - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)


            else:

               #we get the usage from month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due

               #we set the present consumption
               

               

               if usageID.reading_apr > 0 and readingapr: #Modify
                     MeterReadingModification.Modify_function(request,id,"4",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()


                  usageID.reading_apr = float(reading)
                  usageID.usage_apr = float(reading) - last_reading
                  usageID.reading_date_apr = str(current_date)
                  usageID.dateposted_apr = str(current_date)
                  usageID.reading_postedby_apr = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_apr = user.firstname + " " + user.lastname
                  usageID.reading_date_apr = str(current_date)

                  #we generate the bill

                  excess_cubic = 0
                  excess_mincharge = 0
                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_apr != 0:
                        if usageID.usage_apr <= rate.minimumreading and usageID.usage_apr > 0:
                           usageID.bill_apr = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_apr - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_apr = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_apr != 0:
                        if usageID.usage_apr <= rate.minimumreading and usageID.usage_apr > 0:
                           usageID.bill_apr = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_apr - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_apr = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_apr = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_apr = interest


                  usageID.totalbill_apr = usageID.bill_apr + usageID.penalty_apr
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_apr

                  #we set the total due
                  yearly_record.total_due_april += usageID.totalbill_apr
                  yearly_record.total_due_ytd += usageID.totalbill_apr
                  yearly_record.usage_april += usageID.usage_apr
                  yearly_record.total_usage += usageID.usage_apr
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_apr = usageID.totalbill_apr
                     barangay_record.total_due_april += total_bill_apr
                     barangay_record.total_due_ytd += total_bill_apr
                     barangay_record.usage_april += usageID.usage_apr
                     barangay_record.total_usage += usageID.usage_apr
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_apr:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_apr
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_apr:
                        usageID.commulative_bill = usageID.totalbill_apr - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()


                  return HttpResponseRedirect(pathstr)

         #May
         if readingmay:
            last_reading = usageID.reading_apr
            reading = readingmay
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               


               

               if usageID.reading_may > 0 and readingmay: #Modify
                     MeterReadingModification.Modify_function(request,id,"5",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_may = float(reading)
                  usageID.reading_date_may = str(current_date)
                  usageID.dateposted_may = str(current_date)
                  usageID.reading_postedby_may = fullname
                  usageID.usage_may = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_may = user.firstname + " " + user.lastname
                  usageID.reading_date_may = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_may != 0:
                        if usageID.usage_may <= rate.minimumreading and usageID.usage_may > 0:
                           usageID.bill_may = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_may - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_may = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_may != 0:
                        if usageID.usage_may <= rate.minimumreading and usageID.usage_may > 0:
                           usageID.bill_may = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_may - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_may = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_may = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_may = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_may = usageID.bill_may + usageID.penalty_may
                  usageID.commulative_bill =  usageID.totalbill_may

                  #we set the total due
                  yearly_record.total_due_may += usageID.totalbill_may
                  yearly_record.total_due_ytd += usageID.totalbill_may
                  yearly_record.usage_may += usageID.usage_may
                  yearly_record.total_usage += usageID.usage_may
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_may = usageID.totalbill_may
                     barangay_record.total_due_may += total_bill_may
                     barangay_record.total_due_ytd += total_bill_may
                     barangay_record.usage_may += usageID.usage_may
                     barangay_record.total_usage += usageID.usage_may
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_may:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_may
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_may:
                        usageID.commulative_bill = usageID.totalbill_may - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)


            else:

               #we get the usage from last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due

               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value

               

               if usageID.reading_may > 0 and readingmay: #Modify
                     MeterReadingModification.Modify_function(request,id,"5",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_may = float(reading)
                  usageID.usage_may = float(reading) - last_reading
                  usageID.reading_date_may = str(current_date)
                  usageID.dateposted_may = str(current_date)
                  usageID.reading_postedby_may = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_may = user.firstname + " " + user.lastname
                  usageID.reading_date_may = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_may != 0:
                        if usageID.usage_may <= rate.minimumreading and usageID.usage_may > 0:
                           usageID.bill_may = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_may - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_may = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_may != 0:
                        if usageID.usage_may <= rate.minimumreading and usageID.usage_may > 0:
                           usageID.bill_may = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_may - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_may = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_may = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_may = interest

                  usageID.totalbill_may = usageID.bill_may + usageID.penalty_may
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_may

                  #we set the total due

                  yearly_record.total_due_may += usageID.totalbill_may
                  yearly_record.total_due_ytd += usageID.totalbill_may
                  yearly_record.usage_may += usageID.usage_may
                  yearly_record.total_usage += usageID.usage_may
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_may = usageID.totalbill_may
                     barangay_record.total_due_may += total_bill_may
                     barangay_record.total_due_ytd += total_bill_may
                     barangay_record.usage_may += usageID.usage_may
                     barangay_record.total_usage += usageID.usage_may
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_may:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_may
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_may:
                        usageID.commulative_bill = usageID.totalbill_may - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)


         #June
         if readingjun:
            last_reading = usageID.reading_may
            reading = readingjun
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               
              

               if usageID.reading_jun > 0 and readingjun: #Modify
                     MeterReadingModification.Modify_function(request,id,"6",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_jun = float(reading)
                  usageID.reading_date_jun = str(current_date)
                  usageID.dateposted_jun = str(current_date)
                  usageID.reading_postedby_jun = fullname
                  usageID.usage_jun = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_jun = user.firstname + " " + user.lastname
                  usageID.reading_date_jun = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_jun != 0:
                        if usageID.usage_jun <= rate.minimumreading and usageID.usage_jun > 0:
                           usageID.bill_jun = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_jun - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jun = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_jun != 0:
                        if usageID.usage_jun <= rate.minimumreading and usageID.usage_jun > 0:
                           usageID.bill_jun = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_jun - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jun = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_jun = interest

                     if revenue.fix_amount_penalty:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_jun = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_jun = usageID.bill_jun + usageID.penalty_jun
                  usageID.commulative_bill +=  usageID.totalbill_jun

                  #we set the total due
                  yearly_record.total_due_june += usageID.totalbill_jun
                  yearly_record.total_due_ytd += usageID.totalbill_jun
                  yearly_record.usage_june += usageID.usage_jun
                  yearly_record.total_usage += usageID.usage_jun
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_jun = usageID.totalbill_jun
                     barangay_record.total_due_june += total_bill_jun
                     barangay_record.total_due_ytd += total_bill_jun
                     barangay_record.usage_june += usageID.usage_jun
                     barangay_record.total_usage += usageID.usage_jun
                     barangay_record.save()



                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_jun:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_jun
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_jun:
                        usageID.commulative_bill = usageID.totalbill_jun - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)

            else:

               #we get the usage from last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value

               

               if usageID.reading_jun > 0 and readingjun: #Modify
                     MeterReadingModification.Modify_function(request,id,"6",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_jun = float(reading)
                  usageID.usage_jun = float(reading) - last_reading
                  usageID.reading_date_jun = str(current_date)
                  usageID.dateposted_jun = str(current_date)
                  usageID.reading_postedby_jun = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_jun = user.firstname + " " + user.lastname
                  usageID.reading_date_jun = str(current_date)


                  #we generate the bill
                  if usageID.usage_jun != 0:
                     if rateid == ReqParams.residential: #residential

                        if usageID.usage_jun <= rate.minimumreading and usageID.usage_jun > 0:
                           usageID.bill_jun = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_jun - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jun = excess_mincharge +  rate.minimumreading_charge

                     elif rateid == ReqParams.commercial:#commercial

                        if usageID.usage_jun <= rate.minimumreading and usageID.usage_jun > 0:
                           usageID.bill_jun = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_jun - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jun = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_jun = interest

                     if revenue.fix_amount_penalty:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_jun = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_jun = usageID.bill_jun + usageID.penalty_jun
                  usageID.commulative_bill += usageID.totalbill_jun

                  #we set the total due

                  yearly_record.total_due_june += usageID.totalbill_jun
                  yearly_record.total_due_ytd += usageID.totalbill_jun
                  yearly_record.usage_june += usageID.usage_jun
                  yearly_record.total_usage += usageID.usage_jun
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_jun = usageID.totalbill_jun
                     barangay_record.total_due_june += total_bill_jun
                     barangay_record.total_due_ytd += total_bill_jun
                     barangay_record.usage_june += usageID.usage_jun
                     barangay_record.total_usage += usageID.usage_jun
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_jun:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_jun
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_jun:
                        usageID.commulative_bill = usageID.totalbill_jun - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)


         #July
         if readingjul:
            last_reading = usageID.reading_jun    
            reading = readingjul
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               

               

               if usageID.reading_jul > 0 and readingjul: #Modify
                     MeterReadingModification.Modify_function(request,id,"7",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_jul = float(reading)
                  usageID.reading_date_jul = str(current_date)
                  usageID.dateposted_jul = str(current_date)
                  usageID.reading_postedby_jul = fullname
                  usageID.usage_jul = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_jul = user.firstname + " " + user.lastname
                  usageID.reading_date_jul = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_jul != 0:
                        if usageID.usage_jul <= rate.minimumreading and usageID.usage_jul > 0:
                           usageID.bill_jul = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_jul - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jul = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_jul != 0:
                        if usageID.usage_jul <= rate.minimumreading and usageID.usage_jul > 0:
                           usageID.bill_jul = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_jul - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jul = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_jul = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_jul = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_jul = usageID.bill_jul + usageID.penalty_jul
                  usageID.commulative_bill +=  usageID.totalbill_jul

                  #we set the total due

                  yearly_record.total_due_july += usageID.totalbill_jul
                  yearly_record.total_due_ytd += usageID.totalbill_jul
                  yearly_record.usage_july += usageID.usage_jul
                  yearly_record.total_usage += usageID.usage_jul
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_jul = usageID.totalbill_jul
                     barangay_record.total_due_july += total_bill_jul
                     barangay_record.total_due_ytd += total_bill_jul
                     barangay_record.usage_july += usageID.usage_jul
                     barangay_record.total_usage += usageID.usage_jul
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_jul:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_jul
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_jul:
                        usageID.commulative_bill = usageID.totalbill_jul - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)


            else:

               #we get the usage from  last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last december reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value


               if usageID.reading_jul > 0 and readingjul: #Modify
                  MeterReadingModification.Modify_function(request,id,"7",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  print(last_reading)
                  usageID.reading_jul = float(reading)
                  usageID.usage_jul = float(reading) - last_reading
                  usageID.reading_date_jul = str(current_date)
                  usageID.dateposted_jul = str(current_date)
                  usageID.reading_postedby_jul = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_jul = user.firstname + " " + user.lastname
                  usageID.reading_date_jul = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_jul != 0:
                        if usageID.usage_jul <= rate.minimumreading and usageID.usage_jul > 0:
                           usageID.bill_jul = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_jul - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jul = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_jul != 0:
                        if usageID.usage_jul <= rate.minimumreading and usageID.usage_jul > 0:
                           usageID.bill_jul = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_jul - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_jul = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_jul = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_jul = interest

                  usageID.totalbill_jul = usageID.bill_jul + usageID.penalty_jul
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_jul

                  #we set the total due
                  yearly_record.total_due_july += usageID.totalbill_jul
                  yearly_record.total_due_ytd += usageID.totalbill_jul
                  yearly_record.usage_july += usageID.usage_jul
                  yearly_record.total_usage += usageID.usage_jul
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_jul = usageID.totalbill_jul
                     barangay_record.total_due_july += total_bill_jul
                     barangay_record.total_due_ytd += total_bill_jul
                     barangay_record.usage_july += usageID.usage_jul
                     barangay_record.total_usage += usageID.usage_jul
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_jul:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_jul
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_jul:
                        usageID.commulative_bill = usageID.totalbill_jul - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)

         #August
         if readingaug:
            last_reading = usageID.reading_jul
            reading = readingaug
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               


               if usageID.reading_aug > 0 and readingaug: #Modify
                     MeterReadingModification.Modify_function(request,id,"8",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_aug = float(reading)
                  usageID.reading_date_aug = str(current_date)
                  usageID.dateposted_aug = str(current_date)
                  usageID.reading_postedby_aug = fullname
                  usageID.usage_aug = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_aug = user.firstname + " " + user.lastname
                  usageID.reading_date_aug = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_aug != 0:
                        if usageID.usage_aug <= rate.minimumreading and usageID.usage_aug > 0:
                           usageID.bill_aug = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_aug - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_aug = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_aug != 0:
                        if usageID.usage_aug <= rate.minimumreading and usageID.usage_aug > 0:
                           usageID.bill_aug = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_aug - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_aug = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_aug = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_aug = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_aug = usageID.bill_aug + usageID.penalty_aug
                  usageID.commulative_bill +=  usageID.totalbill_aug

                  #we set the total due
                  yearly_record.total_due_august += usageID.totalbill_aug
                  yearly_record.total_due_ytd += usageID.totalbill_aug
                  yearly_record.usage_august += usageID.usage_aug
                  yearly_record.total_usage += usageID.usage_aug
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_aug = usageID.totalbill_aug
                     barangay_record.total_due_august += total_bill_aug
                     barangay_record.total_due_ytd += total_bill_aug
                     barangay_record.usage_august += usageID.usage_aug
                     barangay_record.total_usage += usageID.usage_aug
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_aug:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_aug
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_aug:
                        usageID.commulative_bill = usageID.totalbill_aug - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)


            else:

               #we get the usage from  last month
               usage_id_str = accountid + "-" +year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value


               if usageID.reading_aug > 0 and readingaug: #Modify
                     MeterReadingModification.Modify_function(request,id,"8",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_aug = float(reading)
                  usageID.usage_aug = float(reading) - last_reading
                  usageID.reading_date_aug = str(current_date)
                  usageID.dateposted_aug = str(current_date)
                  usageID.reading_postedby_aug = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_aug = user.firstname + " " + user.lastname
                  usageID.reading_date_aug = str(current_date)


                  #we generate the bill

                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_aug != 0:
                        if usageID.usage_aug <= rate.minimumreading and usageID.usage_aug > 0:
                           usageID.bill_aug = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_aug - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_aug = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_aug != 0:
                        if usageID.usage_aug <= rate.minimumreading and usageID.usage_aug > 0:
                           usageID.bill_aug = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_aug - rate.minimumreading_charge
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_aug = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_aug = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_aug = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_aug = usageID.bill_aug + usageID.penalty_aug
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_aug

                  #we set the total due

                  yearly_record.total_due_august += usageID.totalbill_aug
                  yearly_record.total_due_ytd += usageID.totalbill_aug
                  yearly_record.usage_august += usageID.usage_aug
                  yearly_record.total_usage += usageID.usage_aug
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_aug = usageID.totalbill_aug
                     barangay_record.total_due_august += total_bill_aug
                     barangay_record.total_due_ytd += total_bill_aug
                     barangay_record.usage_august += usageID.usage_aug
                     barangay_record.total_usage += usageID.usage_aug
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_aug:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_aug
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_aug:
                        usageID.commulative_bill = usageID.totalbill_aug - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)


         #September
         if readingsept:
            last_reading = usageID.reading_aug    
            #reports pk
            reading = readingsept
            barangay_record = None
            brgy = account.barangay + "-" + year_of_reading
            if barangay_report.objects.filter(pk = brgy).exists():
               barangay_record = barangay_report.objects.get(pk = brgy)

            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               



               if usageID.reading_sept > 0 and readingsept: #Modify
                     MeterReadingModification.Modify_function(request,id,"9",float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})    
                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_sept = float(reading)
                  usageID.previous_reading = float(reading)
                  usageID.reading_date_sept = str(current_date)
                  usageID.dateposted_sept = str(current_date)
                  usageID.reading_postedby_sept = fullname
                  usageID.usage_sept = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_sept = user.firstname + " " + user.lastname
                  usageID.reading_date_sept = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_sept != 0:
                        if usageID.usage_sept <= rate.minimumreading and usageID.usage_sept > 0:
                           usageID.bill_sept = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_sept - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_sept = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_sept != 0:
                        if usageID.usage_sept <= rate.minimumreading and usageID.usage_sept > 0:
                           usageID.bill_sept = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_sept - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_sept = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_sept = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_sept = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_sept = usageID.bill_sept + usageID.penalty_sept
                  usageID.commulative_bill +=  usageID.totalbill_sept

                  #we set the total due

                  yearly_record.total_due_september += usageID.totalbill_sept
                  yearly_record.total_due_ytd += usageID.totalbill_sept
                  yearly_record.usage_september += usageID.usage_sept
                  yearly_record.total_usage += usageID.usage_sept
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_sept = usageID.totalbill_sept
                     barangay_record.total_due_september += total_bill_sept
                     barangay_record.total_due_ytd += total_bill_sept
                     barangay_record.usage_september += usageID.usage_sept
                     barangay_record.total_usage += usageID.usage_sept
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_sept:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_sept
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_sept:
                        usageID.commulative_bill = usageID.totalbill_sept - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)


            else:

               #we get the usage from last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value


               if usageID.reading_sept > 0 and readingsept: #Modify
                     MeterReadingModification.Modify_function(request,id,"9",float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_sept = float(reading)
                  usageID.usage_sept = float(reading) - last_reading
                  usageID.reading_date_sept = str(current_date)
                  usageID.dateposted_sept = str(current_date)
                  usageID.reading_postedby_sept = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_sept = user.firstname + " " + user.lastname
                  usageID.reading_date_sept = str(current_date)


                  #we generate the bill

                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_sept != 0:
                        if usageID.usage_sept <= rate.minimumreading and usageID.usage_sept > 0:
                           usageID.bill_sept = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_sept - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_sept = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_sept != 0:
                        if usageID.usage_sept <= rate.minimumreading and usageID.usage_sept > 0:
                           usageID.bill_sept = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_sept - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_sept = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_sept = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_sept = interest

                  usageID.totalbill_sept = usageID.bill_sept + usageID.penalty_sept
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_sept

                  #we set the total due

                  yearly_record.total_due_september += usageID.totalbill_sept
                  yearly_record.total_due_ytd += usageID.totalbill_sept
                  yearly_record.usage_september += usageID.usage_sept
                  yearly_record.total_usage += usageID.usage_sept
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_sept = usageID.totalbill_sept
                     barangay_record.total_due_september += total_bill_sept
                     barangay_record.total_due_ytd += total_bill_sept
                     barangay_record.usage_september += usageID.usage_sept
                     barangay_record.total_usage += usageID.usage_sept
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_sept:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_sept
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_sept:
                        usageID.commulative_bill = usageID.totalbill_sept - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)


         #October
         if readingoct:
            last_reading = usageID.reading_sept
            reading = readingoct
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               

               

               if usageID.reading_oct > 0 and readingoct: #Modify
                     MeterReadingModification.Modify_function(request,id,10,float(reading),year_of_reading)
               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})   

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_oct = float(reading)
                  usageID.reading_date_oct = str(current_date)
                  usageID.dateposted_oct = str(current_date)
                  usageID.reading_postedby_oct = fullname
                  usageID.usage_oct = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_oct = user.firstname + " " + user.lastname
                  usageID.reading_date_oct = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_oct != 0:
                        if usageID.usage_oct <= rate.minimumreading and usageID.usage_oct > 0:
                           usageID.bill_oct = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_oct - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_oct = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_oct != 0:
                        if usageID.usage_oct <= rate.minimumreading and usageID.usage_oct > 0:
                           usageID.bill_oct = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_oct - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_oct = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_oct = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_oct = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_oct = usageID.bill_oct + usageID.penalty_oct
                  usageID.commulative_bill =  usageID.totalbill_oct

                  #we set the total due

                  yearly_record.total_due_october += usageID.totalbill_oct
                  yearly_record.total_due_ytd += usageID.totalbill_oct
                  yearly_record.usage_october += usageID.usage_oct
                  yearly_record.total_usage += usageID.usage_oct
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_oct = usageID.totalbill_oct
                     barangay_record.total_due_october += total_bill_oct
                     barangay_record.total_due_ytd += total_bill_oct
                     barangay_record.total_usage_oct += usageID.usage_oct
                     barangay_record.total_usage += usageID.usage_oct
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_oct:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_oct
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_oct:
                        usageID.commulative_bill = usageID.totalbill_oct - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)

            else:

               #we get the usage from last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value

               


               if usageID.reading_oct > 0 and readingoct: #Modify
                     MeterReadingModification.Modify_function(request,id,10,float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_oct = float(reading)
                  usageID.usage_oct = float(reading) - last_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_oct = user.firstname + " " + user.lastname
                  usageID.reading_date_oct = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_oct != 0:
                        if usageID.usage_oct <= rate.minimumreading and usageID.usage_oct > 0:
                           usageID.bill_oct = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_oct - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_oct = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_oct != 0:
                        if usageID.usage_oct <= rate.minimumreading and usageID.usage_oct > 0:
                           usageID.bill_oct = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_oct - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_oct = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_oct = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_oct = interest

                  usageID.totalbill_oct = usageID.bill_oct + usageID.penalty_oct
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_oct

                  #we set the total due

                  yearly_record.total_due_october += usageID.totalbill_oct
                  yearly_record.total_due_ytd += usageID.totalbill_oct
                  yearly_record.usage_october += usageID.usage_oct
                  yearly_record.total_usage += usageID.usage_oct
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_oct = usageID.totalbill_oct
                     barangay_record.total_due_october += total_bill_oct
                     barangay_record.total_due_ytd += total_bill_oct
                     barangay_record.usage_october += usageID.usage_oct
                     barangay_record.total_usage += usageID.usage_oct
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_oct:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_oct
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_oct:
                        usageID.commulative_bill = usageID.totalbill_oct - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)

         if readingnov:
            last_reading = usageID.reading_oct
            reading = readingnov
            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               


               if usageID.reading_nov > 0 and readingnov: #Modify    
                  MeterReadingModification.Modify_function(request,id,11,float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})   

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_nov = float(reading)
                  usageID.reading_date_nov = str(reading)
                  usageID.dateposted_nov = str(current_date)
                  usageID.reading_postedby_nov = fullname
                  usageID.usage_nov = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_nov = user.firstname + " " + user.lastname
                  usageID.reading_date_nov = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_nov != 0:
                        if usageID.usage_nov <= rate.minimumreading and usageID.usage_nov > 0:
                           usageID.bill_nov = rate.minimumreading_charge


                        else:
                           excess_cubic =  usageID.usage_nov - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_nov = excess_mincharge +  rate.minimumreading_charge


                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_nov != 0:
                        if usageID.usage_nov <= rate.minimumreading and usageID.usage_nov > 0:
                           usageID.bill_nov = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_nov - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_nov = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_nov = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_nov = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_nov = usageID.bill_nov + usageID.penalty_nov
                  usageID.commulative_bill +=  usageID.totalbill_nov

                  #we set the total due
                  yearly_record.total_due_november += usageID.totalbill_nov
                  yearly_record.total_due_ytd += usageID.totalbill_nov
                  yearly_record.usage_november += usageID.usage_nov
                  yearly_record.total_usage += usageID.usage_nov
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_nov = usageID.totalbill_nov
                     barangay_record.total_due_november += total_bill_nov
                     barangay_record.total_due_ytd += total_bill_nov
                     barangay_record.usage_november += usageID.usage_nov
                     barangay_record.total_usage += usageID.usage_nov
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_nov:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_nov
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_nov:
                        usageID.commulative_bill = usageID.totalbill_nov - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()


                  return HttpResponseRedirect(pathstr)

            else:

               #we get the usage from month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value



               if usageID.reading_nov > 0 and readingnov: #Modify
                  MeterReadingModification.Modify_function(request,id,11,float(reading),year_of_reading)
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})   

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_nov = float(reading)
                  usageID.usage_nov = float(reading) - last_reading
                  usageID.reading_date_nov = str(current_date)
                  usageID.dateposted_nov = str(current_date)
                  usageID.reading_postedby_nov = fullname
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_nov = user.firstname + " " + user.lastname
                  usageID.reading_date_nov = str(current_date)

                  #we generate the bill

                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_nov != 0:
                        if usageID.usage_nov <= rate.minimumreading and usageID.usage_nov > 0:
                           usageID.bill_nov = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_nov - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_nov = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_nov != 0:
                        if usageID.usage_nov <= rate.minimumreading and usageID.usage_nov > 0:
                           usageID.bill_nov = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_nov - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_nov = excess_mincharge + rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_nov = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_nov = interest

                  usageID.totalbill_nov = usageID.bill_nov + usageID.penalty_nov
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_nov

                  #we set the total due
                  yearly_record.total_due_november += usageID.totalbill_nov
                  yearly_record.total_due_ytd += usageID.totalbill_nov
                  yearly_record.usage_november += usageID.usage_nov
                  yearly_record.total_usage += usageID.usage_nov
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_nov = usageID.totalbill_nov
                     barangay_record.total_due_november += total_bill_nov
                     barangay_record.total_due_ytd += total_bill_nov
                     barangay_record.usage_november += usageID.usage_nov
                     barangay_record.total_usage += usageID.usage_nov
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_nov:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_nov
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_nov:
                        usageID.commulative_bill = usageID.totalbill_nov - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()

                  return HttpResponseRedirect(pathstr)

         if readingdec:
            last_reading = usageID.reading_nov
            reading = readingdec

            yearly_record = Year_Report.objects.get(pk = year_of_reading)

            if initial_meter_reading != -1: #new Consumer has an initial meter reading
               

               if usageID.reading_dec > 0 and readingdec: #Modify
                     MeterReadingModification.Modify_function(request,id,12,float(reading),year_of_reading)

               else:
                  if float(reading) < initial_meter_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})  

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_dec = float(reading)
                  usageID.reading_date_dec = str(current_date)
                  usageID.dateposted_dec = str(current_date)
                  usageID.reading_postedby_dec = fullname
                  usageID.usage_dec = float(reading) - initial_meter_reading
                  usageID.previous_reading = float(reading)
                  usageID.reading_postedby_dec = user.firstname + " " + user.lastname
                  usageID.reading_date_dec = str(current_date)


                  #we generate the bill
                  if rateid == ReqParams.residential:  #residential
                     if usageID.usage_dec != 0:
                        if usageID.usage_dec <= rate.minimumreading and usageID.usage_dec > 0:
                           usageID.bill_dec = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_dec - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_dec = excess_mincharge +  rate.minimumreading_charge


                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_dec != 0:
                        if usageID.usage_dec <= rate.minimumreading and usageID.usage_dec > 0:
                           usageID.bill_dec = rate.minimumreading_charge

                        else:
                           excess_cubic =  usageID.usage_dec - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_dec = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_dec = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_dec = interest

                  account.initial_meter_reading = -1
                  usageID.totalbill_dec = usageID.bill_dec + usageID.penalty_dec
                  usageID.commulative_bill =  usageID.totalbill_dec

                  #we set the total due

                  yearly_record.total_due_december += usageID.totalbill_dec
                  yearly_record.total_due_ytd += usageID.totalbill_dec
                  yearly_record.usage_december += usageID.usage_dec
                  yearly_record.total_usage += usageID.usage_nov
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_dec = usageID.totalbill_dec
                     barangay_record.total_due_december += total_bill_dec
                     barangay_record.total_due_ytd += total_bill_dec
                     barangay_record.usage_december += usageID.usage_dec
                     barangay_record.total_usage += usageID.usage_dec
                     barangay_record.save()


                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_dec:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_dec
                        usageID.commulative_bill = 0
                        usageID.save()

                        account.save()
                     elif usageID.excesspayment < usageID.totalbill_dec:
                        usageID.commulative_bill = usageID.totalbill_dec - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()

                        account.save()
                  else:
                     usageID.save()
                     account.save()

                  return HttpResponseRedirect(pathstr)

            else:

               #we get the usage from last month
               usage_id_str = accountid + "-" + year_of_reading
               getUsageId = usage_record.objects.get(pk = usage_id_str)
                #last month reading
               last_commu_bill = getUsageId.commulative_bill # last month commulative bill or unpaid bill
               last_excesspay = getUsageId.excesspayment #last month excess payment
               lastyear_due = getUsageId.prevyeardue #last year due
               #we set the present consumption
               consumerID = accountid + "-" + year_of_reading
               usageID  = usage_record.objects.get(pk = consumerID) #pk value

               

               if usageID.reading_dec > 0 and readingdec: #Modify
                     MeterReadingModification.Modify_function(request,id,12,float(reading),year_of_reading)
                     
               else:
                  if float(reading) < last_reading:
                     context["error_msg"] = "Invalid Input!"
                     return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})

                  #penalty flag increments
                  if revenue.penalty_after != 0:
                     if usageID.commulative_bill != 0:
                        account.penalty_flag += 1
                        account.save()
                     else:
                        account.penalty_flag = 0
                        account.save()

                  usageID.reading_dec = float(reading)
                  usageID.usage_dec = float(reading) - last_reading
                  usageID.reading_date_dec = str(current_date)
                  usageID.dateposted_dec = str(current_date)
                  usageID.reading_postedby_dec = fullname
                  usageID.previous_reading = float(reading)

                  #we generate the bill

                  if rateid == ReqParams.residential: #residential
                     if usageID.usage_dec != 0:
                        if usageID.usage_dec <= rate.minimumreading and usageID.usage_dec > 0:
                           usageID.bill_dec = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_dec - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_dec = excess_mincharge +  rate.minimumreading_charge

                  elif rateid == ReqParams.commercial:#commercial
                     if usageID.usage_dec != 0:
                        if usageID.usage_dec <= rate.minimumreading and usageID.usage_dec > 0:
                           usageID.bill_dec = rate.minimumreading_charge
                        else:
                           excess_cubic =  usageID.usage_dec - rate.minimumreading
                           excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                           usageID.bill_dec = excess_mincharge +  rate.minimumreading_charge

                  #penalty
                  if revenue.penalty_after != 0 and account.penalty_flag >= revenue.penalty_after:
                     #via percentage
                     if revenue.percentage_penalty != 0:
                        xy = revenue.percentage_penalty * usageID.commulative_bill
                        interest = xy / 100
                        usageID.penalty_dec = interest

                     if revenue.fix_amount_penalty != 0:
                        interest = revenue.fix_amount_penalty
                        usageID.penalty_dec = interest

                  usageID.totalbill_dec = usageID.bill_dec + usageID.penalty_dec
                  usageID.commulative_bill = last_commu_bill + usageID.totalbill_dec


                  #we set the total due
                  yearly_record.total_due_december += usageID.totalbill_dec
                  yearly_record.total_due_ytd += usageID.totalbill_dec
                  yearly_record.usage_december += usageID.usage_dec
                  yearly_record.total_usage += usageID.usage_nov
                  yearly_record.save()

                  brgy = account.barangay + "-" + year_of_reading
                  if barangay_report.objects.filter(pk = brgy).exists():
                     barangay_record = barangay_report.objects.get(pk = brgy)
                     total_bill_dec = usageID.totalbill_dec
                     barangay_record.total_due_december += total_bill_dec
                     barangay_record.total_due_ytd += total_bill_dec
                     barangay_record.usage_december += usageID.usage_dec
                     barangay_record.total_usage += usageID.usage_dec
                     barangay_record.save()

                  # excess payment affects commulative bill
                  if usageID.excesspayment != 0:
                     if usageID.excesspayment > usageID.totalbill_dec:
                        usageID.excesspayment = usageID.excesspayment - usageID.totalbill_dec
                        usageID.commulative_bill = 0
                        usageID.save()
                     elif usageID.excesspayment < usageID.totalbill_dec:
                        usageID.commulative_bill = usageID.totalbill_dec - usageID.excesspayment
                        usageID.excesspayment = 0
                        usageID.save()
                  else:
                     usageID.save()
                     
                  if year_of_reading != current_date.year: 
                     accountidstr = id + "-" + str(current_date.year)
                     current_record  = usage_record.objects.get(pk = accountidstr)
                     current_record.commulative_bill += usageID.commulative_bill 
                     usageID.commulative_bill  = 0
                     usageID.save()
                     current_record.save()

                  return HttpResponseRedirect(pathstr)


   return render(request,template,{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name,"defval_year":defval_year,"year_list":year_list})


def search(request):

   if "execute" not in request.session:
      get_stop_meter()
      request.session["execute"] = "1"
      print("execute")

   #We call our Auto Create method
   ReportGenerator.AutoCreate_NewRecord()
     
   template = ""
   sessionval = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.INPUTREADER_LOGIN_VAL):
         template = "html/search-to-input-reading.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   all_accounts = None
   account_list = []
   current_date = date.today()
   name = request.session.get(ReqParams.name)
   
   all_accounts = account_info.objects.all()
   

   search_for = request.POST.get(ReqParams.search_for)
   
   index = 0
   maxlen = 0
   if ReqParams.index in request.session:    
      index = request.session.get(ReqParams.index)
   else:
      index = 0
   if ReqParams.max_length in request.session:   
      maxlen = request.session.get(ReqParams.max_length)  
   else:
      maxlen = 25

   table_length = all_accounts.count()

   submitbtn = request.POST.get("Post")
   
   accounts = []
   for element in range(index,maxlen):
      accounts.append(all_accounts[element]) 
   
   context = {
      "name":request.session.get(ReqParams.name),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "table_length":table_length,
      "index":index,
      "max_length":maxlen,
      "userid":request.session.get(ReqParams.userid)
   }

   if request.method == "POST":
      index = 0
      maxlen = 0
      if ReqParams.index in request.session:    
         index = request.session.get(ReqParams.index)
      else:
         index = 0
      if ReqParams.max_length in request.session:   
         maxlen = request.session.get(ReqParams.max_length)  
      else:
         maxlen = 25

      if search_for:
         retval = None
         isMatch_for_meternum = account_info.objects.filter(meternumber__icontains=search_for)
         isMatch_for_acc = account_info.objects.filter(accountinfoid__icontains=search_for) 
         isMatch_for_name = account_info.objects.filter(firstname__icontains=search_for)
         isMatch_for_lastname = account_info.objects.filter(lastname__icontains=search_for)

          #and so on
         
         if isMatch_for_meternum:
            retval = isMatch_for_meternum
         elif isMatch_for_acc:
            retval = isMatch_for_acc
         elif isMatch_for_name:
            retval = isMatch_for_name
         elif isMatch_for_lastname:
            retval = isMatch_for_lastname          
            
         return render(request,template,{"ReqParams":ReqParams,"all_accounts":retval,"name":name,"context":context})

      accounts = []
      if submitbtn == "Next":
         index = index + 25
         total = maxlen + 25
         if total > table_length:
            maxlen = table_length
         else:
            maxlen = maxlen +  25   
         for element in range(index,maxlen):
            accounts.append(all_accounts[element])  

         request.session[ReqParams.index] = index
         request.session[ReqParams.max_length] = maxlen     
         context[ReqParams.index] = index
         context[ReqParams.max_length] = maxlen
         return HttpResponseRedirect("/source_access/add-meter-reading")

      if submitbtn == "Previous":
         index = index -  25
         maxlen = maxlen - 25   
         if index < 0:
            return HttpResponseRedirect("/source_access/add-meter-reading")

         for element in range(index,maxlen):
            accounts.append(all_accounts[element])  

         request.session[ReqParams.index] = index
         request.session[ReqParams.max_length] = maxlen  
         context[ReqParams.index] = index
         context[ReqParams.max_length] = maxlen
      
         return HttpResponseRedirect("/source_access/add-meter-reading")
   


   return render(request,template,{"ReqParams":ReqParams,"all_accounts":accounts,"name":name,"context":context})

def send_bill(request):
   all_accounts = account_info.objects.all()
   previous_reading = 0
   current_reading = 0
   emailaddress = ""
   monthname = ""
   bill = 0
   current_date = date.today()

   for account in all_accounts:
      accountid = account.accountinfoid + "-" + str(current_date.year)
      accountrecord = usage_record.objects.get(pk = accountid)
      prev_accountid = account.accountinfoid + "-" + str(current_date.year - 1)
      #we get the previous reading



      if current_date.month == 1:
         previous_record = usage_record.objects.get(pk = prev_accountid)
         previous_reading = previous_record.reading_dec
         current_reading = accountrecord.reading_jan
         bill = accountrecord.totalbill_jan
         monthname = "January"
      elif current_date.month == 2:
         previous_reading = accountrecord.reading_jan
         current_reading = accountrecord.reading_feb
         bill = accountrecord.totalbill_feb
         monthname = "February"
      elif current_date.month == 3:
         previous_reading = accountrecord.reading_feb
         current_reading = accountrecord.reading_mar
         bill = accountrecord.totalbill_mar
         monthname = "March"
      elif current_date.month == 4:
         previous_reading = accountrecord.reading_mar
         current_reading = accountrecord.reading_apr
         bill = accountrecord.totalbill_apr
         monthname = "April"
      elif current_date.month == 5:
         previous_reading = accountrecord.reading_apr
         current_reading = accountrecord.reading_may
         monthname = "May"
      elif current_date.month == 6:
         previous_reading = accountrecord.reading_may
         current_reading = accountrecord.reading_jun
         bill = accountrecord.totalbill_jun
         monthname = "June"
      elif current_date.month == 7:
         previous_reading = accountrecord.reading_jun
         current_reading = accountrecord.reading_jul
         bill = accountrecord.totalbill_jul
         monthname = "July"
      elif current_date.month == 8:
         previous_reading = accountrecord.reading_jul
         current_reading = accountrecord.reading_aug
         bill = accountrecord.totalbill_aug
         monthname = "August"
      elif current_date.month == 9:
         previous_reading = accountrecord.reading_aug
         current_reading = accountrecord.reading_sept
         bill = accountrecord.totalbill_sept
         monthname = "September"
      elif current_date.month == 10:
         previous_reading = accountrecord.reading_sept
         current_reading = accountrecord.reading_oct
         bill = accountrecord.totalbill_oct
         monthname = "October"
      elif current_date.month == 11:
         previous_reading = accountrecord.reading_oct
         current_reading = accountrecord.reading_nov
         bill = accountrecord.totalbill_nov
         monthname = "November"
      elif current_date.month == 12:
         previous_reading = accountrecord.reading_nov
         current_reading = accountrecord.reading_dec
         bill = accountrecord.totalbill_dec
         monthname = "December"

      consumer = consumers_info.objects.get(pk = account.consumerid)
      fname = unicodedata.normalize('NFKD',consumer.firstname).encode('ASCII', 'ignore')
      lname = unicodedata.normalize('NFKD',consumer.lastname).encode('ASCII', 'ignore')
      data = {
               "company": "Ginatilan Waters",

               "city": "Cebu",
               "municipality": "Ginatilan",
               "zipcode": "6028",


               "phone": "555-555-2345",
               "email": "ginatilancebuwater@gmail.com",
               "website": "apps.ginatilan.com",

               "consumername":  fname.decode() + " " + lname.decode(),
               "accountid": account.accountinfoid,
               "bill": bill,
               "month": monthname,
               "prevreading": previous_reading,
               "curreading": current_reading,
               "balance": accountrecord.commulative_bill - bill,
               "duedate": "",
               "total": accountrecord.commulative_bill,
               "address":account.address,
               "usage":accountrecord.usage_dec,
               "rateid":ReqParams.rateid_name[accountrecord.rateid]
      }
      
      if consumer.emailaddress:
         pdf = render_to_pdf('html/payments.html', data)
         message = "This is your bill for the month"
         subject = "Water Bill"
         email_from =  ReqParams.EMAIL_HOST_USER
         recipient_list = [consumer.emailaddress, ]
         email = EmailMessage( subject, message, email_from, recipient_list )
         email.attach('bill.pdf',pdf,'application/pdf')
         try:
            email.send()
            print("hello")
         except SMTPException as e:          # It will catch other errors related to SMTP.
            print('There was an error sending an email.'+ e)
         except:                             # It will catch All other possible errors.
            print("Mail Sending Failed!")

   return render(request,"LoaderPage.html")
