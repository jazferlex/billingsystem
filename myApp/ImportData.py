from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from requests import request
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
import time


def Modify_function(request,id,month,reading,yearstr):
   print("sfsdfsdfs")
   current_date = date.today()
   account = account_info.objects.get(pk = id)
   accountrecord = usage_record.objects.get(pk = id + "-" + yearstr)
   last_dec_reading = 0
   if usage_record.objects.filter(pk = id + "-" + str(int(yearstr) - 1)).exists():
      prev_record = usage_record.objects.get(pk = id + "-" + str(int(yearstr) - 1))
      last_dec_reading = prev_record.reading_dec

   userid = request.session.get(ReqParams.userid)
   user = SystemUser.objects.get(pk = userid)
   modified = MeterReadingModification()
   month_name = ReqParams.month_name
   month_val = int(month)

   accountidstr = account.accountinfoid + "-" + str(yearstr)
   thisrecord = usage_record.objects.get(pk = accountidstr)

   Reading_Month = {
      0:last_dec_reading,
      1: accountrecord.reading_jan,
      2: accountrecord.reading_feb,
      3: accountrecord.reading_mar,
      4: accountrecord.reading_apr,
      5: accountrecord.reading_may,
      6: accountrecord.reading_jun,
      7: accountrecord.reading_jul,
      8: accountrecord.reading_aug,
      9: accountrecord.reading_sept,
      10: accountrecord.reading_oct,
      11: accountrecord.reading_nov,
      12: accountrecord.reading_oct,
   }
   context = {
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "month":month_name[month_val - 1],
      "month_val":month_val,
      "reading":Reading_Month[month_val],
      "name":request.session.get(ReqParams.name),
      "error_msg":""
      
   }

   #w avoid negative results
    
   if float(reading) < Reading_Month[month_val - 1]:
      pass  
   else:    
      print("dfdfd")
      modified.accountinfoid = id
      modified.reading = float(reading)
      modified.month = month_val
      modified.meternumber = account.meternumber
      modified.name = account.firstname + " " + account.lastname
      modified.postedby = user.firstname + " " + user.lastname
      modified.date =  time.asctime( time.localtime(time.time()) )
      modified.year = int(yearstr)
      modified.save()

   return HttpResponse(json.dumps({"success":1}), content_type="application/json")   

def add_meter_reading1(request,yearval,month,id,readingval,userid):
   revenue = revenuecode.objects.get(pk = "1")
   user = SystemUser.objects.get(pk = userid)
   fullname = user.firstname + " " + user.lastname
   #year selection
   year_list = []
   accountrecord = usage_record.objects.filter(accountinfoid = id)
   #for dropdown values(year)

   account = account_info.objects.get(pk = id)
   year_request = yearval
   if year_request:
      accountidstr = account.accountinfoid + "-" + str(year_request)
      thisrecord = usage_record.objects.get(pk = accountidstr)

   else:
      accountidstr = account.accountinfoid + "-" + str(defval_year)
      thisrecord = usage_record.objects.get(pk = accountidstr)
   print(readingval)
   readingjan = None
   readingfeb = None
   readingmar = None
   readingapr = None
   readingmay = None
   readingjun = None
   readingjul = None
   readingaug = None
   readingsept = None
   readingoct = None
   readingnov = None
   readingdec = None

   if month == "1":
      readingjan = readingval
   if month == "2":
      readingfeb = readingval
   if month == "3":
      readingmar = readingval
   if month == "4":
      readingapr = readingval
   if month == "5":
      readingapr = readingval
   if month == "6":
      readingjun = readingval
   if month == "7":
      readingjul = readingval
   if month == "8":
      readingaug = readingval
   if month == "9":
      readingsept = readingval
   if month == "10":
      readingoct = readingval
   if month == "11":
      readingnov = readingval
   if month == "12":
      readingdec = readingval
   
   month_reading = month
   current_date = date.today()
   
   if account_info.objects.filter(pk = id).exists():
      account = account_info.objects.get(pk = id)
      this_record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_date.year))
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
         prev_year = int(year_request) - 1
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
               pass


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
            this_record.commulative_bill =  usageID.commulative_bill
            this_record.save()
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

            this_record.commulative_bill =  usageID.commulative_bill
            this_record.save()


         elif initial_meter_reading != -1: #new Consumer has an initial meter reading
            #reports pk
            brgy = account.barangay + "-" + year_of_reading
            barangay_record = barangay_report.objects.get(pk = brgy)
            yearly_record = Year_Report.objects.get(pk = year_of_reading)



            if float(reading) < initial_meter_reading:
               pass

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
            this_record.commulative_bill =  usageID.commulative_bill
            this_record.save()

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


         #Modify
         elif usageID.reading_jan > 0 and readingjan:
            Modify_function(request,id,1,float(reading),year_of_reading)



      ###$#######

      #February
      if readingfeb:
         last_reading = usageID.reading_jan
         reading = readingfeb
         yearly_record = Year_Report.objects.get(pk = year_of_reading)
         print(reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading




            if usageID.reading_feb > 0 and readingfeb:
                  Modify_function(request,id,"2",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"2",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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



      #March
      if readingmar:
         last_reading = usageID.reading_feb
         reading = readingmar
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading




            if usageID.reading_mar > 0 and readingmar: #Modify
                  Modify_function(request,id,"3",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"3",float(reading),year_of_reading)

            else:
               if float(reading) < last_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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




      #April
      if readingapr:
         last_reading = usageID.reading_mar
         reading = readingapr
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading




            if usageID.reading_apr > 0 and readingapr: #Modify
                  Modify_function(request,id,"4",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"4",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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




      #May
      if readingmay:
         last_reading = usageID.reading_apr
         reading = readingmay
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading





            if usageID.reading_may > 0 and readingmay: #Modify
                  Modify_function(request,id,"5",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"5",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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




      #June
      if readingjun:
         last_reading = usageID.reading_may
         reading = readingjun
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading



            if usageID.reading_jun > 0 and readingjun: #Modify
                  Modify_function(request,id,"6",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"6",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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




      #July
      if readingjul:
         last_reading = usageID.reading_jun
         reading = readingjul
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading




            if usageID.reading_jul > 0 and readingjul: #Modify
                  Modify_function(request,id,"7",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
               Modify_function(request,id,"7",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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



      #August
      if readingaug:
         last_reading = usageID.reading_jul
         reading = readingaug
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading



            if usageID.reading_aug > 0 and readingaug: #Modify
                  Modify_function(request,id,"8",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"8",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"9",float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass
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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,"9",float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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




      #October
      if readingoct:
         last_reading = usageID.reading_sept
         reading = readingoct
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading




            if usageID.reading_oct > 0 and readingoct: #Modify
                  Modify_function(request,id,10,float(reading),year_of_reading)
            else:
               if float(reading) < initial_meter_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,10,float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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



      if readingnov:
         last_reading = usageID.reading_oct
         reading = readingnov
         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading



            if usageID.reading_nov > 0 and readingnov: #Modify
               Modify_function(request,id,11,float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
               Modify_function(request,id,11,float(reading),year_of_reading)
            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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


      if readingdec:
         last_reading = usageID.reading_nov
         reading = readingdec

         yearly_record = Year_Report.objects.get(pk = year_of_reading)

         if initial_meter_reading != -1: #new Consumer has an initial meter reading


            if usageID.reading_dec > 0 and readingdec: #Modify
                  Modify_function(request,id,12,float(reading),year_of_reading)

            else:
               if float(reading) < initial_meter_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()

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
                  Modify_function(request,id,12,float(reading),year_of_reading)

            else:
               if float(reading) < last_reading:
                  pass

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
               this_record.commulative_bill =  usageID.commulative_bill
               this_record.save()


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

   return HttpResponse(json.dumps({"success":1}), content_type="application/json")

def import_data(request):

    
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.INPUTREADER_LOGIN_VAL):
         template = "html/import_data.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   context = {}
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)


   if "bulk_reading_month" in request.session:
      context["month"] = request.session.get("bulk_reading_month")
   if "bulk_reading_year" in request.session:
      context["year"] = request.session.get("bulk_reading_year")  
   print(context)
   all_accounts = account_info.objects.all()
   account_record = usage_record.objects.filter(year = request.session.get("bulk_reading_year"))
   prev_record = usage_record.objects.filter(year = int(request.session.get("bulk_reading_year")) - 1)
   this_year = request.session.get("bulk_reading_year")

   if request.method == "POST":

      for account in all_accounts:
         if request.POST.get("current_reading" + account.accountinfoid):
            idstr = account.accountinfoid + "-" + this_year
            if usage_record.objects.filter(pk = idstr).exists():
               print("here")
               add_meter_reading1(request,request.session.get("bulk_reading_year"),request.session.get("bulk_reading_month"),account.accountinfoid, request.POST.get("current_reading" + account.accountinfoid),request.session.get(ReqParams.userid))

   return render(request,template,{"context":context,"all_accounts":all_accounts,"account_record":account_record,"prev_record":prev_record})

def bulkreading(request):
   context = {}
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.INPUTREADER_LOGIN_VAL):
         template = "html/bulk_input_reading.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")
   year_list = []
   #accountrecord = usage_record.objects.filter(accountinfoid = id) 
   year_record = Year_Report.objects.all()
   #for dropdown values(year)
   current_date = date.today()
   for element in year_record:
      year_list.append(element.year)

   year_request = request.POST.get("year")
   monthval = request.POST.get("month")
   context["defmonth"] = current_date.month
   context["defyear"] = current_date.year
   
   if request.method == "POST":
      request.session["bulk_reading_month"] = monthval
      request.session["bulk_reading_year"] = year_request
      return HttpResponseRedirect("/source_access/import_data")
   return render(request,template,{"year_list":year_list,"context":context,})
