from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *
from django.template import Context
from datetime import date
from django.contrib import messages
from .BillingDB import *
from .BillingUtil import *
from .Payment import *
import datetime



def Search(request):
    
   #rendering page
   template = "html/Search_ToEditReading.html"
   sessionval = ""
   if request.session.get(ReqParams.LOGIN_SESSION) == ReqParams.TELLER_LOGIN_VAL:
      sessionval = ReqParams.TELLER_LOGIN_VAL
   elif request.session.get(ReqParams.LOGIN_SESSION) == ReqParams.INPUTREADER_LOGIN_VAL:
      sessionval =  ReqParams.INPUTREADER_LOGIN_VAL

   message = ""
   index = 0
   params = ReqParams()
   account = account_info()  
   current_date = date.today()
   year = str(current_date.year)
   usage = usage_record()
   all_accounts = account_info.objects.all()
   all_record = usage_record.objects.all()  
   account_list = []
   usage_list = []
   all_list = []

   context = {}               
   context[ReqParams.userid] =  request.session.get(ReqParams.userid)
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
   search_for = request.POST.get('search_for')       
   index = 0

   
                   
   if request.method == "POST":

      if search_for:
         isMatch_for_fname = account_info.objects.filter(firstname__icontains=search_for)  #getting all of the value of search_for int collunm firstname
         isMatch_for_lname = account_info.objects.filter(lastname__icontains=search_for) #and so on
         isMatch_for_acc = account_info.objects.filter(accountinfoid__icontains=search_for)
         
         if isMatch_for_fname:
            #we get the usage id from accountinfo
            for x in isMatch_for_fname:
               accstr = x.accountinfoid
               accID = account_info.objects.get(pk = accstr)
               account_list.append(accID)
               

            return render(request,render_page(request,sessionval,template),{'all_list': account_list,"context":context})
         elif isMatch_for_lname:
            #we get the usage id from accountinfo
            for x in isMatch_for_lname: 
               accstr = x.accountinfoid
               accID = account_info.objects.get(pk = accstr)
               account_list.append(accID)
            
            return render(request,render_page(request,sessionval,template),{'all_list': account_list,"context":context})
         elif isMatch_for_acc:
            #we get the usage id from accountinfo
            for x in isMatch_for_acc:
               accstr = x.accountinfoid        
               accID = account_info.objects.get(pk = accstr)
               account_list.append(accID)

            return render(request,render_page(request,sessionval,template),{'all_list': account_list,"context":context})
         else:
            message = "No Result Found for " + search_for

   for account in all_accounts:       
         if index != 25:#display only 25 accounts
            account_list.append(account)
            index += 1        
         else:
            all_accounts = None    
      

   return render(request,render_page(request,sessionval,template),{'all_list': account_list,"context":context,"message":message})



def Edit_MeterReading(request,id):
    #rendering the exact page
    #Teller and input reader can access this function but not on the same pages
    template = ""
    sessionval = ""
    loginsession = request.session.get(ReqParams.LOGIN_SESSION)
    if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.INPUTREADER_LOGIN_VAL):
        template = "html/Edit_MeterReading.html"
    else:
        template = "html/unavailable.html"

    current_date = date.today()
    context = {}               
    context[ReqParams.userid] =  request.session.get(ReqParams.userid)
    context[ReqParams.name] = request.session.get(ReqParams.name)

    current_date = date.today()
    reading_january = request.POST.get("reading_jan")
    reading_february = request.POST.get("reading_feb")  
    reading_march = request.POST.get("reading_mar") 
    reading_april = request.POST.get("reading_apr")
    reading_may = request.POST.get("reading_may") 
    reading_june = request.POST.get("reading_jun")
    reading_july = request.POST.get("reading_jul")
    reading_august = request.POST.get("reading_aug")
    reading_september = request.POST.get("reading_sept")
    reading_october = request.POST.get("reading_oct")
    reading_november = request.POST.get("reading_nov")
    reading_december = request.POST.get("reading_dec")

    pkval = id + "-" + str(current_date.year)
    account_record = usage_record.objects.get(pk = pkval)
    account = account_info.objects.get(pk = id)
    rate = rates.objects.get(pk = account_record.rateid)
    rateid = rate.rateid
    brgyval = account.barangay + "-" + str(current_date.year)
    brgy_record = barangay_report.objects.get(pk = brgyval)
    year_record = Year_Report.objects.get(pk = current_date.year)

    if request.method == "POST":

    
        if float(reading_january) != account_record.reading_jan:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_jan
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_jan
            year_balance = year_record.total_due_ytd - account_record.totalbill_jan
            brgy_balance_jan = brgy_record.total_due_january - account_record.totalbill_jan
            year_balance_jan = year_record.total_due_january - account_record.totalbill_jan
            year_usage = year_record.total_usage - account_record.usage_jan
            year_usage_jan = year_record.usage_january - account_record.usage_jan
            brgy_usage = brgy_record.total_usage - account_record.usage_jan
            brgy_usage_jan = brgy_record.usage_january - account_record.usage_jan

            #get the previous reading
            prev_year_record = usage_record.objects.filter(pk = str(current_date.year - 1))
            if prev_year_record.exists():
                account_record.usage_jan = float(reading_january) - prev_year_record.reading_dec
            else:
                #get the initial meter reading
                initial_reading = account_record.usage_jan + account_record.reading_jan
                account_record.usage_jan = float(reading_january) - initial_reading


            #we generate the bill
            if reading_january != 0:  
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_jan <= rate.minimumreading and account_record.usage_jan > 0:
                        account_record.bill_jan = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jan = reading_january                       
                        account_record.totalbill_jan = account_record.bill_jan + account_record.penalty_jan
                        new_balance = balance + account_record.totalbill_jan
                        account_record.commulative_bill = new_balance
                        account_record.save()   
                    else:
                        excess_cubic = float(reading_january) - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_jan = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jan = reading_january                       
                        account_record.totalbill_jan = account_record.bill_jan + account_record.penalty_jan
                        new_balance = balance + account_record.totalbill_jan
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_jan <= rate.minimumreading and account_record.usage_jan > 0:
                        account_record.bill_jan = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jan = reading_january                       
                        account_record.totalbill_jan = account_record.bill_jan + account_record.penalty_jan
                        new_balance = balance + account_record.totalbill_jan
                        account_record.commulative_bill = new_balance
                        account_record.save() 
                            
                    else:
                        excess_cubic =  account_record.usage_jan - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_jan = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jan = reading_january                       
                        account_record.totalbill_jan = account_record.bill_jan + account_record.penalty_jan
                        new_balance = balance + account_record.totalbill_jan
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_jan
                new_jan_balance = brgy_balance_jan + account_record.totalbill_jan                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_january = new_jan_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_jan
                new_jan_balance = year_balance_jan + account_record.totalbill_jan                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_january = new_jan_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_jan
                new_jan_usage = brgy_usage_jan + account_record.usage_jan                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_january = new_jan_usage
                
                new_year_usage = year_usage + account_record.usage_jan
                new_jan_usage = year_usage_jan + account_record.usage_jan                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_january = new_jan_usage
                #save
                year_record.save()
                brgy_record.save()

                         

            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_jan = 0
                account_record.usage_jan = 0
                account_record.bill_jan = 0
                account_record.totalbill_jan = 0
                account_record.penalty_jan = 0
                account_record.save()
        


        #February
    
        if float(reading_february) != account_record.reading_feb:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_feb
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_feb
            year_balance = year_record.total_due_ytd - account_record.totalbill_feb
            brgy_balance_feb = brgy_record.total_due_february - account_record.totalbill_feb
            year_balance_feb = year_record.total_due_february - account_record.totalbill_feb
            year_usage = year_record.total_usage - account_record.usage_feb
            year_usage_feb = year_record.usage_february - account_record.usage_feb
            brgy_usage = brgy_record.total_usage - account_record.usage_feb
            brgy_usage_feb = brgy_record.usage_february - account_record.usage_feb

            #we set the new usage
            account_record.usage_feb = float(reading_february) - float(account_record.reading_jan)

            #we generate the bill 
            if reading_february != 0:  
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_feb <= rate.minimumreading and account_record.usage_feb > 0:
                        account_record.bill_jan = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_feb = reading_february
                        account_record.totalbill_feb = account_record.bill_feb + account_record.penalty_feb
                        new_balance = balance + account_record.totalbill_feb
                        account_record.commulative_bill = new_balance
                        account_record.save()
                    else:
                        excess_cubic = account_record.usage_feb - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_feb = excess_mincharge +  rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_feb = reading_february
                        account_record.totalbill_feb = account_record.bill_feb + account_record.penalty_feb
                        new_balance = balance + account_record.totalbill_feb
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_feb <= rate.minimumreading and account_record.usage_feb > 0:
                        account_record.bill_feb = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_feb = reading_february
                        account_record.totalbill_feb = account_record.bill_feb + account_record.penalty_feb
                        new_balance = balance + account_record.totalbill_feb
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic =  account_record.usage_feb - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_feb = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_feb = reading_february
                        account_record.totalbill_feb = account_record.bill_feb + account_record.penalty_feb
                        new_balance = balance + account_record.totalbill_feb
                        account_record.commulative_bill = new_balance
                        account_record.save()
   
                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_feb
                new_feb_balance = brgy_balance_feb + account_record.totalbill_feb                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_february = new_feb_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_feb
                new_jan_balance = year_balance_feb + account_record.totalbill_feb                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_february = new_feb_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_feb
                new_feb_usage = brgy_usage_feb + account_record.usage_feb                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_february = new_feb_usage
                
                new_year_usage = year_usage + account_record.usage_feb
                new_feb_usage = year_usage_feb + account_record.usage_feb                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_february = new_feb_usage
                #save
                year_record.save()
                brgy_record.save()
                


            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_feb = 0
                account_record.bill_feb = 0
                account_record.totalbill_feb = 0
                account_record.usage_feb = 0
                account_record.penalty_feb = 0
                account_record.save()
        

        


        #March
        
        if float(reading_march) != account_record.reading_mar:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_mar
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_mar
            year_balance = year_record.total_due_ytd - account_record.totalbill_mar
            brgy_balance_mar = brgy_record.total_due_march - account_record.totalbill_mar
            year_balance_mar = year_record.total_due_march - account_record.totalbill_mar
            year_usage = year_record.total_usage - account_record.usage_mar
            year_usage_mar = year_record.usage_march - account_record.usage_mar
            brgy_usage = brgy_record.total_usage - account_record.usage_mar
            brgy_usage_jan = brgy_record.usage_march - account_record.usage_mar
            
            #we set the new usage
            account_record.usage_mar = float(reading_march) - float(account_record.reading_feb)

            #we generate the bill.
            if reading_march:   
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_mar <= rate.minimumreading and account_record.usage_mar > 0:
                        account_record.bill_mar = rate.minimumreading_charge
                        # update the current record
                        account_record.reading_mar = reading_march
                        account_record.totalbill_mar = account_record.bill_mar + account_record.penalty_mar
                        new_balance = balance + account_record.totalbill_mar
                        account_record.commulative_bill = new_balance
                        account_record.save()
                    else:
                        excess_cubic = account_record.usage_mar - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_mar = excess_mincharge +  rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_mar = reading_march
                        account_record.totalbill_mar = account_record.bill_mar + account_record.penalty_mar
                        new_balance = balance + account_record.totalbill_mar
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_mar <= rate.minimumreading and account_record.usage_mar > 0:
                        account_record.bill_mar = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_mar = reading_march
                        account_record.totalbill_mar = account_record.bill_mar + account_record.penalty_mar
                        new_balance = balance + account_record.totalbill_mar
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic =  account_record.usage_mar - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_mar = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_mar = reading_march
                        account_record.totalbill_mar = account_record.bill_mar + account_record.penalty_mar
                        new_balance = balance + account_record.totalbill_mar
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_mar
                new_mar_balance = brgy_balance_mar + account_record.totalbill_mar                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_march = new_mar_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_mar
                new_mar_balance = year_balance_mar + account_record.totalbill_mar                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_march = new_mar_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_mar
                new_mar_usage = brgy_usage_mar + account_record.usage_mar                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_march = new_mar_usage
                
                new_year_usage = year_usage + account_record.usage_mar
                new_mar_usage = year_usage_mar + account_record.usage_mar                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_march = new_mar_usage
                #save
                year_record.save()
                brgy_record.save()
                


            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_mar = 0
                account_record.bill_mar = 0
                account_record.totalbill_mar = 0
                account_record.usage_mar = 0
                account_record.penalty_mar = 0
                account_record.save()
            



        #April
        if float(reading_april) != account_record.reading_apr:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_apr
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_apr
            year_balance = year_record.total_due_ytd - account_record.totalbill_apr
            brgy_balance_apr = brgy_record.total_due_april - account_record.totalbill_apr
            year_balance_apr = year_record.total_due_april - account_record.totalbill_apr
            year_usage = year_record.total_usage - account_record.usage_apr
            year_usage_apr = year_record.usage_april - account_record.usage_apr
            brgy_usage = brgy_record.total_usage - account_record.usage_apr
            brgy_usage_apr = brgy_record.usage_april - account_record.usage_apr

            #we set the new usage
            account_record.usage_apr = float(reading_april) - float(account_record.reading_mar)

            #we generate the bill
            if reading_april != 0:   
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_apr <= rate.minimumreading and account_record.usage_apr > 0:
                        account_record.bill_apr = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_apr = reading_april
                        account_record.totalbill_apr = account_record.bill_apr + account_record.penalty_apr
                        new_balance = balance + account_record.totalbill_apr
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                    else:
                        excess_cubic = account_record.usage_apr - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_apr = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_apr = reading_april
                        account_record.totalbill_apr = account_record.bill_apr + account_record.penalty_apr
                        new_balance = balance + account_record.totalbill_apr
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_apr <= rate.minimumreading and account_record.usage_apr > 0:
                        account_record.bill_apr = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_apr = reading_april
                        account_record.totalbill_apr = account_record.bill_apr + account_record.penalty_apr
                        new_balance = balance + account_record.totalbill_apr
                        account_record.commulative_bill = new_balance
                        account_record.save()                      
                    else:
                        excess_cubic =  account_record.usage_apr - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_apr = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_apr = reading_april
                        account_record.totalbill_apr = account_record.bill_apr + account_record.penalty_apr
                        new_balance = balance + account_record.totalbill_apr
                        account_record.commulative_bill = new_balance
                        account_record.save()  

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_apr
                new_apr_balance = brgy_balance_apr + account_record.totalbill_apr                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_april = new_apr_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_apr
                new_apr_balance = year_balance_apr + account_record.totalbill_apr                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_april = new_apr_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_apr
                new_apr_usage = brgy_usage_apr + account_record.usage_apr                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_april = new_apr_usage
                
                new_year_usage = year_usage + account_record.usage_apr
                new_apr_usage = year_usage_apr + account_record.usage_apr                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_april = new_apr_usage
                #save
                year_record.save()
                brgy_record.save()
                
                    

            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_apr = 0
                account_record.bill_apr = 0
                account_record.totalbill_apr = 0
                account_record.usage_apr = 0
                account_record.penalty_apr = 0
                account_record.save()
        

        
        #May
        if float(reading_may) != account_record.reading_may:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_may
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_may
            year_balance = year_record.total_due_ytd - account_record.totalbill_may
            brgy_balance_may = brgy_record.total_due_may - account_record.totalbill_may
            year_balance_may = year_record.total_due_may - account_record.totalbill_may
            year_usage = year_record.total_usage - account_record.usage_may
            year_usage_may = year_record.usage_may - account_record.usage_may
            brgy_usage = brgy_record.total_usage - account_record.usage_may
            brgy_usage_may = brgy_record.usage_may - account_record.usage_may

            #we set the new usage
            account_record.usage_may = float(reading_may) - float(account_record.reading_apr)

            #we generate the bill 
            if reading_may != 0:  
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_may <= rate.minimumreading and account_record.usage_may > 0:
                        account_record.bill_may = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_may = reading_may
                        account_record.totalbill_may = account_record.bill_may + account_record.penalty_may
                        new_balance = balance + account_record.totalbill_may
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                    else:
                        excess_cubic = account_record.usage_may - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_may = excess_mincharge +  rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_may = reading_may
                        account_record.totalbill_may = account_record.bill_may + account_record.penalty_may
                        new_balance = balance + account_record.totalbill_may
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_may <= rate.minimumreading and account_record.usage_may > 0:
                        account_record.bill_may = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_may = reading_may
                        account_record.totalbill_may = account_record.bill_may + account_record.penalty_may
                        new_balance = balance + account_record.totalbill_may
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                    else:
                        excess_cubic =  account_record.usage_may - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_may = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_may = reading_may
                        account_record.totalbill_may = account_record.bill_may + account_record.penalty_may
                        new_balance = balance + account_record.totalbill_may
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_may
                new_may_balance = brgy_balance_may + account_record.totalbill_may                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_may = new_may_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_may
                new_may_balance = year_balance_may + account_record.totalbill_may                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_may = new_may_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_may
                new_may_usage = brgy_usage_may + account_record.usage_may                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_may = new_may_usage
                
                new_year_usage = year_usage + account_record.usage_may
                new_may_usage = year_usage_may + account_record.usage_may                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_may = new_may_usage
                #save
                year_record.save()
                brgy_record.save()
                


            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_may = 0
                account_record.bill_may = 0
                account_record.totalbill_may = 0
                account_record.usage_may = 0
                account_record.penalty_may = 0
                account_record.save()


        if float(reading_june) != account_record.reading_jun:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_jun
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_jun
            year_balance = year_record.total_due_ytd - account_record.totalbill_jun
            brgy_balance_jun = brgy_record.total_due_june - account_record.totalbill_jun
            year_balance_jun = year_record.total_due_june - account_record.totalbill_jun
            year_usage = year_record.total_usage - account_record.usage_jun
            year_usage_jun = year_record.usage_january - account_record.usage_jun
            brgy_usage = brgy_record.total_usage - account_record.usage_jun
            brgy_usage_jun = brgy_record.usage_june - account_record.usage_jun

            #we set the new usage
            account_record.usage_jun = float(reading_june) - float(account_record.reading_may)

            #we generate the bill 
            if reading_june != 0:  
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_jun <= rate.minimumreading and account_record.usage_jun > 0:
                        account_record.bill_jun = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_jun = reading_june
                        account_record.totalbill_jun = account_record.bill_jun + account_record.penalty_jun
                        new_balance = balance + account_record.totalbill_jun
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                    else:
                        excess_cubic = account_record.usage_jun - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_jun = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jun = reading_june
                        account_record.totalbill_jun = account_record.bill_jun + account_record.penalty_jun
                        new_balance = balance + account_record.totalbill_jun
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_jun <= rate.minimumreading and account_record.usage_jun > 0:
                        account_record.bill_jun = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jun = reading_june
                        account_record.totalbill_jun = account_record.bill_jun + account_record.penalty_jun
                        new_balance = balance + account_record.totalbill_jun
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic =  account_record.usage_jun - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_jun = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jun = reading_june
                        account_record.totalbill_jun = account_record.bill_jun + account_record.penalty_jun
                        new_balance = balance + account_record.totalbill_jun
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_jun
                new_jun_balance = brgy_balance_jun + account_record.totalbill_jun                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_june = new_jun_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_jun
                new_jun_balance = year_balance_jun + account_record.totalbill_jun                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_june = new_jun_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_jun
                new_jun_usage = brgy_usage_jun + account_record.usage_jun                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_june = new_jun_usage
                
                new_year_usage = year_usage + account_record.usage_jun
                new_jun_usage = year_usage_jun + account_record.usage_jun                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_june = new_jun_usage
                #save
                year_record.save()
                brgy_record.save()
                


            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_jun = 0
                account_record.bill_jun = 0
                account_record.totalbill_jun = 0
                account_record.usage_jun = 0
                account_record.penalty_jun = 0
                account_record.save()
        
        #July
        if float(reading_july) != account_record.reading_jul:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_jul
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_jul
            year_balance = year_record.total_due_ytd - account_record.totalbill_jul
            brgy_balance_jul = brgy_record.total_due_july - account_record.totalbill_jul
            year_balance_jul = year_record.total_due_july - account_record.totalbill_jul
            year_usage = year_record.total_usage - account_record.usage_jul
            year_usage_jul = year_record.usage_july - account_record.usage_jul
            brgy_usage = brgy_record.total_usage - account_record.usage_jul
            brgy_usage_jul = brgy_record.usage_july - account_record.usage_jul

            #we set the new usage
            account_record.usage_jul = float(reading_july) - float(account_record.reading_jun)

            #we generate the bill 
            if reading_july != 0:  
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_jul <= rate.minimumreading and account_record.usage_jul > 0:
                        account_record.bill_jan = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jul = reading_july
                        account_record.totalbill_jul = account_record.bill_jul + account_record.penalty_jul
                        new_balance = balance + account_record.totalbill_jul
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic = account_record.usage_jul - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_jul = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jul = reading_july
                        account_record.totalbill_jul = account_record.bill_jul + account_record.penalty_jul
                        new_balance = balance + account_record.totalbill_jul
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_jul <= rate.minimumreading and account_record.usage_jul > 0:
                        account_record.bill_jul = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jul = reading_july
                        account_record.totalbill_jul = account_record.bill_jul + account_record.penalty_jul
                        new_balance = balance + account_record.totalbill_jul
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                    else:
                        excess_cubic =  account_record.usage_jul - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_jul = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_jul = reading_july
                        account_record.totalbill_jul = account_record.bill_jul + account_record.penalty_jul
                        new_balance = balance + account_record.totalbill_jul
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_jul
                new_jul_balance = brgy_balance_jul + account_record.totalbill_jul                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_july = new_jul_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_jul
                new_jul_balance = year_balance_jul + account_record.totalbill_jul                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_july = new_jul_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_jul
                new_jul_usage = brgy_usage_jul + account_record.usage_jul                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_july = new_jul_usage
                
                new_year_usage = year_usage + account_record.usage_jul
                new_jul_usage = year_usage_jul + account_record.usage_jul                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_july = new_jul_usage
                #save
                year_record.save()
                brgy_record.save()
                

                
            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_jul = 0
                account_record.bill_jul = 0
                account_record.totalbill_jul = 0
                account_record.usage_jul = 0
                account_record.penalty_jul = 0
                account_record.save()


        #August
        if float(reading_august) != account_record.reading_aug:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_aug
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_aug
            year_balance = year_record.total_due_ytd - account_record.totalbill_aug
            brgy_balance_aug = brgy_record.total_due_august - account_record.totalbill_aug
            year_balance_aug = year_record.total_due_august - account_record.totalbill_aug
            year_usage = year_record.total_usage - account_record.usage_aug
            year_usage_aug = year_record.usage_august - account_record.usage_aug
            brgy_usage = brgy_record.total_usage - account_record.usage_aug
            brgy_usage_aug = brgy_record.usage_august - account_record.usage_aug

            #we set the new usage
            account_record.usage_aug = float(reading_august) - float(account_record.reading_jul)

            #we generate the bill 
            if reading_august != 0:  
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_aug <= rate.minimumreading and account_record.usage_aug > 0:
                        account_record.bill_jan = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_aug = reading_august
                        account_record.totalbill_aug = account_record.bill_aug + account_record.penalty_aug
                        new_balance = balance + account_record.totalbill_aug
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic = account_record.usage_aug - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_aug = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_aug = reading_august
                        account_record.totalbill_aug = account_record.bill_aug + account_record.penalty_aug
                        new_balance = balance + account_record.totalbill_aug
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_aug <= rate.minimumreading and reading_august > 0:
                        account_record.bill_aug = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_aug = reading_august
                        account_record.totalbill_aug = account_record.bill_aug + account_record.penalty_aug
                        new_balance = balance + account_record.totalbill_aug
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic =  account_record.usage_aug - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_aug = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_aug = reading_august
                        account_record.totalbill_aug = account_record.bill_aug + account_record.penalty_aug
                        new_balance = balance + account_record.totalbill_aug
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_aug
                new_aug_balance = brgy_balance_aug + account_record.totalbill_aug                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_august = new_aug_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_aug
                new_apr_balance = year_balance_aug + account_record.totalbill_aug                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_august = new_aug_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_aug
                new_aug_usage = brgy_usage_aug + account_record.usage_aug                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_august = new_aug_usage
                
                new_year_usage = year_usage + account_record.usage_aug
                new_aug_usage = year_usage_aug + account_record.usage_aug                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_august = new_aug_usage
                #save
                year_record.save()
                brgy_record.save()
                

                    
            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_mar = 0
                account_record.bill_mar = 0
                account_record.totalbill_mar = 0
                account_record.usage_aug = 0
                account_record.penalty_mar = 0
                account_record.save()


        #September
        if float(reading_september) != account_record.reading_sept:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_sept
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_sept
            year_balance = year_record.total_due_ytd - account_record.totalbill_sept
            brgy_balance_sept = brgy_record.total_due_september - account_record.totalbill_sept
            year_balance_sept = year_record.total_due_september - account_record.totalbill_sept
            year_usage = year_record.total_usage - account_record.usage_sept
            year_usage_sept = year_record.usage_september - account_record.usage_sept
            brgy_usage = brgy_record.total_usage - account_record.usage_sept
            brgy_usage_sept = brgy_record.usage_september - account_record.usage_sept

            #we set the new usage
            account_record.usage_sept = float(reading_september) - float(account_record.reading_aug)

            #we generate the bill
            if reading_september != 0:   
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_sept <= rate.minimumreading and account_record.usage_sept > 0:
                        account_record.bill_sept = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_sept = reading_september
                        account_record.totalbill_sept = account_record.bill_sept + account_record.penalty_sept
                        new_balance = balance + account_record.totalbill_sept
                        account_record.commulative_bill = new_balance
                        account_record.save()
                    else:
                        excess_cubic = account_record.usage_sept - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_sept = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_sept = reading_september
                        account_record.totalbill_sept = account_record.bill_sept + account_record.penalty_sept
                        new_balance = balance + account_record.totalbill_sept
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_sept <= rate.minimumreading and reading_september > 0:
                        account_record.bill_sept = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_sept = reading_september
                        account_record.totalbill_sept = account_record.bill_sept + account_record.penalty_sept
                        new_balance = balance + account_record.totalbill_sept
                        account_record.commulative_bill = new_balance
                        account_record.save()                    
                    else:
                        excess_cubic =  account_record.usage_sept - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_sept = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_sept = reading_september
                        account_record.totalbill_sept = account_record.bill_sept + account_record.penalty_sept
                        new_balance = balance + account_record.totalbill_sept
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_sept
                new_sept_balance = brgy_balance_sept + account_record.totalbill_sept                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_september = new_sept_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_sept
                new_sept_balance = year_balance_sept + account_record.totalbill_sept                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_september = new_sept_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_sept
                new_sept_usage = brgy_usage_sept + account_record.usage_sept                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_september = new_sept_usage
                
                new_year_usage = year_usage + account_record.usage_sept
                new_sept_usage = year_usage_sept + account_record.usage_sept                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_september = new_sept_usage
                #save
                year_record.save()
                brgy_record.save()
                


            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_sept = 0
                account_record.bill_sept = 0
                account_record.totalbill_sept = 0
                account_record.usage_sept = 0
                account_record.penalty_sept = 0
                account_record.save()

        
        #October
    
        if float(reading_october) != account_record.reading_oct:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_oct
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_oct
            year_balance = year_record.total_due_ytd - account_record.totalbill_oct
            brgy_balance_oct = brgy_record.total_due_oct - account_record.totalbill_oct
            year_balance_oct = year_record.total_due_october - account_record.totalbill_oct
            year_usage = year_record.total_usage - account_record.usage_oct
            year_usage_oct = year_record.usage_october - account_record.usage_oct
            brgy_usage = brgy_record.total_usage - account_record.usage_oct
            brgy_usage_oct = brgy_record.usage_october - account_record.usage_oct

            #we set the new usage
            account_record.usage_oct = float(reading_october) - float(account_record.reading_sept)

            #we generate the bill
            if reading_october != 0:   
                if rateid == ReqParams.residential:  #residential
                    if reading_october <= rate.minimumreading and reading_october > 0:
                        account_record.bill_oct = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_oct = reading_october
                        account_record.totalbill_oct = account_record.bill_oct + account_record.penalty_oct
                        new_balance = balance + account_record.totalbill_oct
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic = reading_october - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_oct = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_oct = reading_october
                        account_record.totalbill_oct = account_record.bill_oct + account_record.penalty_oct
                        new_balance = balance + account_record.totalbill_oct
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if reading_october <= rate.minimumreading and reading_october > 0:
                        account_record.bill_oct = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_oct = reading_october
                        account_record.totalbill_oct = account_record.bill_oct + account_record.penalty_oct
                        new_balance = balance + account_record.totalbill_oct
                        account_record.commulative_bill = new_balance
                        account_record.save()                     

                    else:
                        excess_cubic =  reading_october - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_oct = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_oct = reading_october
                        account_record.totalbill_oct = account_record.bill_oct + account_record.penalty_oct
                        new_balance = balance + account_record.totalbill_oct
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_oct
                new_oct_balance = brgy_balance_oct + account_record.totalbill_oct                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_october = new_oct_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_oct
                new_oct_balance = year_balance_oct + account_record.totalbill_oct                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_oct = new_oct_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_oct
                new_oct_usage = brgy_usage_oct + account_record.usage_aug                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_october = new_oct_usage
                
                new_year_usage = year_usage + account_record.usage_oct
                new_oct_usage = year_usage_oct + account_record.usage_oct                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_october = new_oct_usage
                #save
                year_record.save()
                brgy_record.save()
                                   

            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_oct = 0
                account_record.bill_oct = 0
                account_record.totalbill_oct = 0
                account_record.usage_oct = 0
                account_record.penalty_oct = 0
                account_record.save()


        #November
        if float(reading_november) != account_record.reading_nov:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_nov
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_nov
            year_balance = year_record.total_due_ytd - account_record.totalbill_nov
            brgy_balance_nov = brgy_record.total_due_november - account_record.totalbill_nov
            year_balance_nov = year_record.total_due_november - account_record.totalbill_nov
            year_usage = year_record.total_usage - account_record.usage_nov
            year_usage_nov = year_record.usage_november - account_record.usage_nov
            brgy_usage = brgy_record.total_usage - account_record.usage_nov
            brgy_usage_nov = brgy_record.usage_november - account_record.usage_nov

            #we set the new usage
            account_record.usage_nov = float(reading_november) - float(account_record.reading_oct)

            #we generate the bill
            if reading_november != 0:   
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_nov <= rate.minimumreading and reading_november > 0:
                        account_record.bill_jan = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_nov = reading_november
                        account_record.totalbill_nov = account_record.bill_nov + account_record.penalty_nov
                        new_balance = balance + account_record.totalbill_nov
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic = reading_november - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_nov = excess_mincharge +  rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_nov = reading_november
                        account_record.totalbill_nov = account_record.bill_nov + account_record.penalty_nov
                        new_balance = balance + account_record.totalbill_nov
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_nov <= rate.minimumreading and reading_november > 0:
                        account_record.bill_nov = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_nov = reading_november
                        account_record.totalbill_nov = account_record.bill_nov + account_record.penalty_nov
                        new_balance = balance + account_record.totalbill_nov
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic =  account_record.usage_nov - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_nov = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_nov = reading_november
                        account_record.totalbill_nov = account_record.bill_nov + account_record.penalty_nov
                        new_balance = balance + account_record.totalbill_nov
                        account_record.commulative_bill = new_balance
                        account_record.save()

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_nov
                new_nov_balance = brgy_balance_nov + account_record.totalbill_nov                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_november = new_nov_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_nov
                new_nov_balance = year_balance_nov + account_record.totalbill_nov                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_november = new_nov_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_nov
                new_nov_usage = brgy_usage_nov + account_record.usage_nov                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_november = new_nov_usage
                
                new_year_usage = year_usage + account_record.usage_nov
                new_nov_usage = year_usage_nov + account_record.usage_nov                
                brgy_record.total_usage = new_year_usage
                brgy_record.usage_november = new_nov_usage
                #save
                year_record.save()
                brgy_record.save()

                

            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_nov = 0
                account_record.bill_nov = 0
                account_record.totalbill_nov = 0
                account_record.usage_nov = 0
                account_record.penalty_nov = 0
                account_record.save()


        #December
        if float(reading_december) != account_record.reading_dec:
            #minus first the commulative bill from totalbill
            balance = account_record.commulative_bill - account_record.totalbill_dec
            #reports
            brgy_balance = brgy_record.total_due_ytd - account_record.totalbill_dec
            year_balance = year_record.total_due_ytd - account_record.totalbill_dec
            brgy_balance_dec = brgy_record.total_due_december - account_record.totalbill_dec
            year_balance_dec = year_record.total_due_december - account_record.totalbill_dec
            year_usage = year_record.total_usage - account_record.usage_dec
            year_usage_dec = year_record.usage_december - account_record.usage_dec
            brgy_usage = brgy_record.total_usage - account_record.usage_dec
            brgy_usage_dec = brgy_record.usage_december - account_record.usage_dec

            #we setthe new usage
            account_record.usage_dec = float(reading_december) - float(account_record.reading_nov)

            #we generate the bill  
            if reading_december != 0: 
                if rateid == ReqParams.residential:  #residential
                    if account_record.usage_dec <= rate.minimumreading and reading_december > 0:
                        account_record.bill_dec = rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_dec = reading_december
                        account_record.totalbill_dec = account_record.bill_dec + account_record.penalty_dec
                        new_balance = balance + account_record.totalbill_dec
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic = account_record.usage_dec - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_dec = excess_mincharge +  rate.minimumreading_charge 
                        #update the current record
                        account_record.reading_dec = reading_december
                        account_record.totalbill_dec = account_record.bill_dec + account_record.penalty_dec
                        new_balance = balance + account_record.totalbill_dec
                        account_record.commulative_bill = new_balance
                        account_record.save()

                elif rateid == ReqParams.commercial:#commercial
                    if account_record.usage_dec <= rate.minimumreading and reading_december > 0:
                        account_record.bill_dec = rate.minimumreading_charge
                        #update the current record
                        account_record.reading_dec = reading_december
                        account_record.totalbill_dec = account_record.bill_dec + account_record.penalty_dec
                        new_balance = balance + account_record.totalbill_dec
                        account_record.commulative_bill = new_balance
                        account_record.save()

                    else:
                        excess_cubic =  account_record.usage_dec - rate.minimumreading
                        excess_mincharge = excess_cubic * rate.rateafterminimum  #depending on consumer type
                        account_record.bill_dec = excess_mincharge +  rate.minimumreading_charge
                        #update the current record
                        account_record.reading_dec = reading_december
                        account_record.totalbill_dec = account_record.bill_dec + account_record.penalty_dec
                        new_balance = balance + account_record.totalbill_dec
                        account_record.commulative_bill = new_balance
                        account_record.save() 

                #set the updated year and brangay report
                #baragay report
                new_brgy_balance = brgy_balance + account_record.totalbill_dec
                new_dec_balance = brgy_balance_dec + account_record.totalbill_dec                
                brgy_record.total_due_ytd = new_brgy_balance
                brgy_record.total_due_december = new_dec_balance
                
                #year / month report
                new_year_balance = year_balance + account_record.totalbill_dec
                new_dec_balance = year_balance_dec + account_record.totalbill_dec                
                year_record.total_due_ytd = new_year_balance
                year_record.total_due_december = new_dec_balance
                
                #usage report
                new_brgy_usage = brgy_usage + account_record.usage_dec
                new_dec_usage = brgy_usage_dec + account_record.usage_dec                
                brgy_record.total_usage = new_brgy_usage
                brgy_record.usage_december = new_dec_usage
                
                new_year_usage = year_usage + account_record.usage_dec
                new_dec_usage = year_usage_dec + account_record.usage_dec                
                year_record.total_usage = new_year_usage
                year_record.usage_december = new_dec_usage
                #save
                year_record.save()
                brgy_record.save()


            else:
                #update the current record
                account_record.commulative_bill = balance
                account_record.reading_dec = 0
                account_record.bill_dec = 0
                account_record.totalbill_dec = 0
                account_record.usage_dec = 0
                account_record.penalty_dec = 0
                account_record.save()


        pathstr = "/source_access/edit-this-meter-reading=" + id
        return HttpResponseRedirect(pathstr)

    current_date = date.today()
    if current_date.month == 1:
        context["month_of_reading"] = "12"
    else:
        context["month_of_reading"] = str(current_date.month - 1) 

    context["balance"] = str(account_record.commulative_bill)
    context["Fullname"] = account.firstname + " " + account.lastname
    context["Id"] = account.accountinfoid
    context[ReqParams.address] = account.address   

    return render(request,template,{"context":context,"usage":account_record})




