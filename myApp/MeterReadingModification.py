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
import calendar
import time









def Modify_Reading_Request(request):

    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    template = ""
    if LogInSession:
        if LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL):
            template = "html/ModifiedMeterReading.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("")        
        
    tobeModified = MeterReadingModification.objects.all()
    #sessions
    userid = request.session.get(ReqParams.userid)
    getuser = SystemUser.objects.get(pk = userid)

    context= {}
    context[ReqParams.name] = getuser.firstname
    context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION) 
    context["userid"] = request.session.get(ReqParams.userid)

    return render(request,template,{"modified":tobeModified,"context":context})


     

def Confirm_Modification_Request(request,id):

    current_date = date.today()    
    current_year = str(current_date.year)
    
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    template = ""
    if LogInSession:
        if LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL):
            template = "html/ModifiedMeterReading.html"
        else: 
            template = "html/unavailable.html"
    else:
        return redirect("")        
        
    tobeModified = MeterReadingModification.objects.all()

    mdf = MeterReadingModification.objects.get(pk = id)

    account = account_info.objects.get(pk = mdf.accountinfoid)
    month_val = mdf.month
    reading = mdf.reading

    accountrecord = usage_record.objects.get(pk = mdf.accountinfoid + "-" + str(mdf.year))
    rate = rates.objects.get(pk = account.rateid)
    rateid = rate.rateid
    context = {
        "UserType":request.session.get(ReqParams.LOGIN_SESSION),
        "month":month,
        "reading":mdf.reading,
        "name":request.session.get(ReqParams.name)
        
    }
    yearly_record = Year_Report.objects.get(pk = current_date.year)
    #January
    if month_val == 1:

        #we get the previous reading last year december
        prev_reading = 0
        if usage_record.objects.filter(pk = id + "-" + str(mdf.year - 1)).exists():
            prevrecord = usage_record.objects.get(pk = id + "-" + str(mdf.year - 1))
            prev_reading = prevrecord.reading_dec

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_jan
        accountrecord.usage_jan = float(reading) - prev_reading
        accountrecord.reading_jan = float(reading)

        #we generate the bill  
        if accountrecord.usage_jan != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_jan != 0:
                    if accountrecord.usage_jan <= rate.minimumreading and accountrecord.usage_jan > 0:
                        accountrecord.bill_jan = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_jan = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_jan != 0:
                    if accountrecord.usage_jan <= rate.minimumreading and accountrecord.usage_jan > 0:
                        accountrecord.bill_jan = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_jan = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_jan = 0

        accountrecord.totalbill_jan = accountrecord.penalty_jan + accountrecord.bill_jan
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_jan
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_january - float(reading)
        totaldue_month = yearly_record.total_due_january - accountrecord.totalbill_jan
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_jan

        yearly_record.total_due_january = totaldue_month + accountrecord.totalbill_jan
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_jan
        yearly_record.usage_january = totalusage + accountrecord.usage_jan
        yearly_record.total_usage = totaldue + accountrecord.totalbill_jan
        yearly_record.save()

        

        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_january - float(reading)
            brgy_totaldue_month = barangay_record.total_due_january - accountrecord.totalbill_jan
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_jan

            barangay_record.total_due_january = brgy_totaldue_month + accountrecord.totalbill_jan
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_jan
            barangay_record.usage_january = brgy_totalusage_month + accountrecord.usage_jan
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_jan
            barangay_record.save()

                   

    #February
    if month_val == 2:
        #we get the previous reading 
        prev_reading = accountrecord.reading_jan

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_feb
        accountrecord.usage_feb = float(reading) - prev_reading
        accountrecord.reading_feb = float(reading)

        #we generate the bill  
        if accountrecord.usage_feb != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_feb != 0:
                    if accountrecord.usage_feb <= rate.minimumreading and accountrecord.usage_feb > 0:
                        accountrecord.bill_feb = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_feb - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_feb = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_feb != 0:
                    if accountrecord.usage_feb <= rate.minimumreading and accountrecord.usage_feb > 0:
                        accountrecord.bill_feb = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_feb - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_feb = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_feb = 0

        accountrecord.totalbill_feb = accountrecord.penalty_feb + accountrecord.bill_feb
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_feb
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_february - float(reading)
        totaldue_month = yearly_record.total_due_february - accountrecord.totalbill_feb
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_feb

        yearly_record.total_due_february = totaldue_month + accountrecord.totalbill_feb
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_feb
        yearly_record.usage_february = totalusage + accountrecord.usage_feb
        yearly_record.total_usage = totaldue + accountrecord.totalbill_feb
        yearly_record.save()

        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_february - float(reading)
            brgy_totaldue_month = barangay_record.total_due_february - accountrecord.totalbill_feb
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_feb

            barangay_record.total_due_february = brgy_totaldue_month + accountrecord.totalbill_feb
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_feb
            barangay_record.usage_february = brgy_totalusage_month + accountrecord.usage_feb
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_feb
            barangay_record.save()

            

    if month_val == 3:
        #we get the previous reading 
        prev_reading = accountrecord.reading_feb

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_mar
        accountrecord.usage_mar = float(reading) - prev_reading
        accountrecord.reading_mar = float(reading)

        #we generate the bill  
        if accountrecord.usage_mar != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_mar != 0:
                    if accountrecord.usage_mar <= rate.minimumreading and accountrecord.usage_mar > 0:
                        accountrecord.bill_mar = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_mar - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_mar = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_mar != 0:
                    if accountrecord.usage_mar <= rate.minimumreading and accountrecord.usage_mar > 0:
                        accountrecord.bill_mar = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_mar - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_mar = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_mar = 0

        accountrecord.totalbill_mar = accountrecord.penalty_mar + accountrecord.bill_mar
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_mar
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_march - float(reading)
        totaldue_month = yearly_record.total_due_march - accountrecord.totalbill_mar
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_mar

        yearly_record.total_due_march = totaldue_month + accountrecord.totalbill_mar
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_mar
        yearly_record.usage_march = totalusage + accountrecord.usage_mar
        yearly_record.total_usage = totaldue + accountrecord.totalbill_mar
        yearly_record.save()


        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_march - float(reading)
            brgy_totaldue_month = barangay_record.total_due_march - accountrecord.totalbill_mar
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_mar

            barangay_record.total_due_march = brgy_totaldue_month + accountrecord.totalbill_mar
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_mar
            barangay_record.usage_march = brgy_totalusage_month + accountrecord.usage_mar
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_mar
            barangay_record.save()



    if month_val == 4:
        #we get the previous reading 
        prev_reading = accountrecord.reading_mar

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_apr
        accountrecord.usage_apr = float(reading) - prev_reading
        accountrecord.reading_apr = float(reading)

        #we generate the bill  
        if accountrecord.usage_apr != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_apr != 0:
                    if accountrecord.usage_apr <= rate.minimumreading and accountrecord.usage_apr > 0:
                        accountrecord.bill_apr = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_apr - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_apr = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_apr != 0:
                    if accountrecord.usage_apr <= rate.minimumreading and accountrecord.usage_apr > 0:
                        accountrecord.bill_apr = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_apr - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_apr = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_apr = 0

        accountrecord.totalbill_apr = accountrecord.penalty_apr + accountrecord.bill_apr
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_apr
        accountrecord.save()
        
        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_april - float(reading)
        totaldue_month = yearly_record.total_due_april - accountrecord.totalbill_apr
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_apr

        yearly_record.total_due_april = totaldue_month + accountrecord.totalbill_apr
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_apr
        yearly_record.usage_april = totalusage + accountrecord.usage_apr
        yearly_record.total_usage = totaldue + accountrecord.totalbill_apr
        yearly_record.save()

        

        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_april - float(reading)
            brgy_totaldue_month = barangay_record.total_due_april - accountrecord.totalbill_apr
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_apr
            barangay_record.total_due_april = brgy_totaldue_month + accountrecord.totalbill_apr
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_apr
            barangay_record.usage_april = brgy_totalusage_month + accountrecord.usage_apr
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_apr
            barangay_record.save()


    if month_val == 5:
        #we get the previous reading 
        prev_reading = accountrecord.reading_apr

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_may
        accountrecord.usage_may = float(reading) - prev_reading
        accountrecord.reading_may = float(reading)

        #we generate the bill  
        if accountrecord.usage_may != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_may != 0:
                    if accountrecord.usage_may <= rate.minimumreading and accountrecord.usage_may > 0:
                        accountrecord.bill_may = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_may - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_may = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_may != 0:
                    if accountrecord.usage_may <= rate.minimumreading and accountrecord.usage_may > 0:
                        accountrecord.bill_may = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_may - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_may = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_may = 0

        accountrecord.totalbill_may = accountrecord.penalty_may + accountrecord.bill_may
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_may
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_may - float(reading)
        totaldue_month = yearly_record.total_due_may - accountrecord.totalbill_may
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_may

        yearly_record.total_due_may = totaldue_month + accountrecord.totalbill_may
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_may
        yearly_record.usage_may = totalusage + accountrecord.usage_may
        yearly_record.total_usage = totaldue + accountrecord.totalbill_may
        yearly_record.save()

        

        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_may - float(reading)
            brgy_totaldue_month = barangay_record.total_due_may - accountrecord.totalbill_may
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_may

            barangay_record.total_due_may = brgy_totaldue_month + accountrecord.totalbill_may
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_may
            barangay_record.usage_may = brgy_totalusage_month + accountrecord.usage_may
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_may
            barangay_record.save()

            



            
    if month_val == 6:
        #we get the previous reading 
        prev_reading = accountrecord.reading_may

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_jun
        accountrecord.usage_jun = float(reading) - prev_reading
        accountrecord.reading_jun = float(reading)

        #we generate the bill  
        if accountrecord.usage_jun != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_jun != 0:
                    if accountrecord.usage_jun <= rate.minimumreading and accountrecord.usage_jun > 0:
                        accountrecord.bill_jun = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_jun - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_jun = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_jun != 0:
                    if accountrecord.usage_jun <= rate.minimumreading and accountrecord.usage_jun > 0:
                        accountrecord.bill_jun = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_jun - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_jun = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_jun = 0

        accountrecord.totalbill_jun = accountrecord.penalty_jun + accountrecord.bill_jun
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_jun
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_june - float(reading)
        totaldue_month = yearly_record.total_due_june - accountrecord.totalbill_jun
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_jun

        yearly_record.total_due_june = totaldue_month + accountrecord.totalbill_jun
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_jun
        yearly_record.usage_jun = totalusage + accountrecord.usage_jun
        yearly_record.total_usage = totaldue + accountrecord.totalbill_jun
        yearly_record.save()

        

        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_june - float(reading)
            brgy_totaldue_month = barangay_record.total_due_june - accountrecord.totalbill_jun
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_jun
            barangay_record.total_due_june = brgy_totaldue_month + accountrecord.totalbill_jun
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_jun
            barangay_record.usage_june = brgy_totalusage_month + accountrecord.usage_jun
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_jun
            barangay_record.save()

            


    if month_val == 7:
        #we get the previous reading 
        prev_reading = accountrecord.reading_jun

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_jul
        accountrecord.usage_jul = float(reading) - prev_reading
        accountrecord.reading_jul = float(reading)

        #we generate the bill  
        if accountrecord.usage_jul != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_jul != 0:
                    if accountrecord.usage_jul <= rate.minimumreading and accountrecord.usage_jul > 0:
                        accountrecord.bill_jul = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_jul - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_jul = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_jul != 0:
                    if accountrecord.usage_jul <= rate.minimumreading and accountrecord.usage_jul > 0:
                        accountrecord.bill_jul = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_jul - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_jul = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_jul = 0

        accountrecord.totalbill_jul = accountrecord.penalty_jul + accountrecord.bill_jul
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_jul
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_july - float(reading)
        totaldue_month = yearly_record.total_due_july - accountrecord.totalbill_jul
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_jul

        yearly_record.total_due_july = totaldue_month + accountrecord.totalbill_jul
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_jul
        yearly_record.usage_july = totalusage + accountrecord.usage_jul
        yearly_record.total_usage = totaldue + accountrecord.totalbill_jul
        yearly_record.save()


        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)

            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_july - float(reading)
            brgy_totaldue_month = barangay_record.total_due_july - accountrecord.totalbill_jul
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_jun
            barangay_record.total_due_july = brgy_totaldue_month + accountrecord.totalbill_jul
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_jul
            barangay_record.usage_july = brgy_totalusage_month + accountrecord.usage_jul
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_jul
            barangay_record.save()

                


    if month_val == 8:
        #we get the previous reading 
        prev_reading = accountrecord.reading_jul

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_aug
        accountrecord.usage_aug = float(reading) - prev_reading
        accountrecord.reading_aug = float(reading)

        #we generate the bill  
        if accountrecord.usage_aug != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_aug != 0:
                    if accountrecord.usage_aug <= rate.minimumreading and accountrecord.usage_aug > 0:
                        accountrecord.bill_aug = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_aug - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_aug = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_aug != 0:
                    if accountrecord.usage_aug <= rate.minimumreading and accountrecord.usage_aug > 0:
                        accountrecord.bill_aug = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_aug - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_aug = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_aug = 0

        accountrecord.totalbill_aug = accountrecord.penalty_aug + accountrecord.bill_aug
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_aug
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_august - float(reading)
        totaldue_month = yearly_record.total_due_august - accountrecord.totalbill_aug
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_aug

        yearly_record.total_due_august = totaldue_month + accountrecord.totalbill_aug
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_aug
        yearly_record.usage_august = totalusage + accountrecord.usage_aug
        yearly_record.total_usage = totaldue + accountrecord.totalbill_aug
        yearly_record.save()


        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_august - float(reading)
            brgy_totaldue_month = barangay_record.total_due_august - accountrecord.totalbill_aug
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_jun
            barangay_record.total_due_august = brgy_totaldue_month + accountrecord.totalbill_aug
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_aug
            barangay_record.usage_august = brgy_totalusage_month + accountrecord.usage_aug
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_aug
            barangay_record.save()

            



    if month_val == 9:
        #we get the previous reading 
        prev_reading = accountrecord.reading_aug

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_sept
        accountrecord.usage_sept = float(reading) - prev_reading
        accountrecord.reading_sept = float(reading)

        #we generate the bill  
        if accountrecord.usage_sept != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_sept != 0:
                    if accountrecord.usage_sept <= rate.minimumreading and accountrecord.usage_sept > 0:
                        accountrecord.bill_sept = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_sept - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_sept = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_sept != 0:
                    if accountrecord.usage_sept <= rate.minimumreading and accountrecord.usage_sept > 0:
                        accountrecord.bill_sept = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_aug - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_sept = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_sept = 0

        accountrecord.totalbill_sept = accountrecord.penalty_sept + accountrecord.bill_sept
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_sept
        accountrecord.save()

        #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_september - float(reading)
        totaldue_month = yearly_record.total_due_september - accountrecord.totalbill_sept
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_sept

        yearly_record.total_due_september = totaldue_month + accountrecord.totalbill_sept
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_sept
        yearly_record.usage_september = totalusage + accountrecord.usage_sept
        yearly_record.total_usage = totaldue + accountrecord.totalbill_sept
        yearly_record.save()

        
        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_september - float(reading)
            brgy_totaldue_month = barangay_record.total_due_september - accountrecord.totalbill_sept
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_sept

            barangay_record.total_due_september = brgy_totaldue_month + accountrecord.totalbill_sept
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_sept
            barangay_record.usage_september = brgy_totalusage_month + accountrecord.usage_sept
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_sept
            barangay_record.save()

            



    if month_val == 10:
        #we get the previous reading 
        prev_reading = accountrecord.reading_sept

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_oct
        accountrecord.usage_oct = float(reading) - prev_reading
        accountrecord.reading_oct = float(reading)

        #we generate the bill  
        if accountrecord.usage_oct != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_oct != 0:
                    if accountrecord.usage_oct <= rate.minimumreading and accountrecord.usage_oct > 0:
                        accountrecord.bill_oct = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_oct - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_oct = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_oct != 0:
                    if accountrecord.usage_oct <= rate.minimumreading and accountrecord.usage_oct > 0:
                        accountrecord.bill_oct = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_oct - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_sept = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_oct = 0

        accountrecord.totalbill_oct = accountrecord.penalty_oct + accountrecord.bill_oct
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_oct
        accountrecord.save()

            #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_october - float(reading)
        totaldue_month = yearly_record.total_due_october - accountrecord.totalbill_oct
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_oct

        yearly_record.total_due_october = totaldue_month + accountrecord.totalbill_oct
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_oct
        yearly_record.usage_october = totalusage + accountrecord.usage_oct
        yearly_record.total_usage = totaldue + accountrecord.totalbill_oct
        yearly_record.save()


        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_october - float(reading)
            brgy_totaldue_month = barangay_record.total_due_october - accountrecord.totalbill_oct
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_oct
            barangay_record.total_due_october = brgy_totaldue_month + accountrecord.totalbill_oct
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_oct
            barangay_record.usage_october = brgy_totalusage_month + accountrecord.usage_oct
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_oct
            barangay_record.save()

            


    if month_val == 11:
        #we get the previous reading 
        prev_reading = accountrecord.reading_oct

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_nov
        accountrecord.usage_nov = float(reading) - prev_reading
        accountrecord.reading_nov = float(reading)

        #we generate the bill  
        if accountrecord.usage_nov != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_nov != 0:
                    if accountrecord.usage_nov <= rate.minimumreading and accountrecord.usage_nov > 0:
                        accountrecord.bill_nov = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_nov - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_nov = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_nov != 0:
                    if accountrecord.usage_nov <= rate.minimumreading and accountrecord.usage_nov > 0:
                        accountrecord.bill_nov = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_nov - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_nov = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_nov = 0

        accountrecord.totalbill_nov = accountrecord.penalty_nov + accountrecord.bill_nov
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_nov
        accountrecord.save()

            #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_november - float(reading)
        totaldue_month = yearly_record.total_due_november - accountrecord.totalbill_nov
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_nov

        yearly_record.total_due_november = totaldue_month + accountrecord.totalbill_nov
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_nov
        yearly_record.usage_november = totalusage + accountrecord.usage_nov
        yearly_record.total_usage = totaldue + accountrecord.totalbill_nov
        yearly_record.save()


        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_november - float(reading)
            brgy_totaldue_month = barangay_record.total_due_november - accountrecord.totalbill_nov
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_nov
            barangay_record.total_due_november = brgy_totaldue_month + accountrecord.totalbill_nov
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_nov
            barangay_record.usage_november = brgy_totalusage_month + accountrecord.usage_nov
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_nov
            barangay_record.save()

            


    if month_val == 12:
        #we get the previous reading 
        prev_reading = accountrecord.reading_nov

        #we subtract the january totalbill to commulative bill
        commu_bill = accountrecord.commulative_bill - accountrecord.totalbill_dec
        accountrecord.usage_dec = float(reading) - prev_reading
        accountrecord.reading_dec = float(reading)

        #we generate the bill  
        if accountrecord.usage_dec != 0:
            if rateid == ReqParams.residential:  #residential
                if accountrecord.usage_dec != 0:
                    if accountrecord.usage_dec <= rate.minimumreading and accountrecord.usage_dec > 0:
                        accountrecord.bill_dec = rate.minimumreading_charge 

                    else:
                        excess_cubic =  accountrecord.usage_dec - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_dec = excess_mincharge +  rate.minimumreading_charge

            elif rateid == ReqParams.commercial:#commercial
                if accountrecord.usage_dec != 0:
                    if accountrecord.usage_dec <= rate.minimumreading and accountrecord.usage_dec > 0:
                        accountrecord.bill_dec = rate.minimumreading_charge

                    else:
                        excess_cubic =  accountrecord.usage_nov - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        accountrecord.bill_dec = excess_mincharge +  rate.minimumreading_charge 
        else:
            accountrecord.bill_dec = 0

        accountrecord.totalbill_dec = accountrecord.penalty_dec + accountrecord.bill_dec
        accountrecord.commulative_bill = commu_bill + accountrecord.totalbill_dec
        accountrecord.save()

            #update reports
        totalusage =  yearly_record.total_usage - float(reading)
        totalusage_month =  yearly_record.usage_december - float(reading)
        totaldue_month = yearly_record.total_due_december - accountrecord.totalbill_dec
        totaldue = yearly_record.total_due_ytd - accountrecord.totalbill_dec

        yearly_record.total_due_december = totaldue_month + accountrecord.totalbill_dec
        yearly_record.total_due_ytd = totaldue + accountrecord.totalbill_dec
        yearly_record.usage_december = totalusage + accountrecord.usage_dec
        yearly_record.total_usage = totaldue + accountrecord.totalbill_dec
        yearly_record.save()


        brgy = account.barangay + "-" + current_year
        if barangay_report.objects.filter(pk = brgy).exists():
            barangay_record = barangay_report.objects.get(pk = brgy)
            brgy_totalusage =  barangay_record.total_usage - float(reading)
            brgy_totalusage_month =  barangay_record.usage_december - float(reading)
            brgy_totaldue_month = barangay_record.total_due_december - accountrecord.totalbill_dec
            brgy_totaldue = barangay_record.total_due_ytd - accountrecord.totalbill_dec
            barangay_record.total_due_december = brgy_totaldue_month + accountrecord.totalbill_dec
            barangay_record.total_due_ytd = brgy_totaldue + accountrecord.totalbill_dec
            barangay_record.usage_december = brgy_totalusage_month + accountrecord.usage_dec
            barangay_record.total_usage = brgy_totalusage + accountrecord.usage_dec
            barangay_record.save()

    mdf.delete()
    return render(request,template,{"modified":tobeModified,"context":context})    

                                            

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
        context["error_msg"] = "Invalid Input! We avoid negative results!"
        return render(request,"html/input-reading.html",{"context":context,"account":account,"thisrecord":thisrecord,"Reqparams":ReqParams,"month_name":month_name})     
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

    return HttpResponseRedirect("/source_access/add-meter-reading/" + id)