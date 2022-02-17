from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from .models import *
from .Serializer import *
from django.template import Context
from datetime import date
from django.contrib import messages
from .BillingDB import *
from .BillingUtil import *
from .Payment import *
import datetime


def Search(request):

   #rendering page
   template = "html/Search_account.Payment.html"
   sessionval = ""
   if request.session.get(ReqParams.LOGIN_SESSION) == ReqParams.TELLER_LOGIN_VAL:
      sessionval = ReqParams.TELLER_LOGIN_VAL
   elif request.session.get(ReqParams.LOGIN_SESSION) == ReqParams.SUPERVISOR_LOGIN_VAL:
      sessionval =  ReqParams.SUPERVISOR_LOGIN_VAL

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

def pay_bill(request,id,month):
   account = account_info()
   usage = usage_record()
   current_date = date.today()
   context = {}
   defval = {}
   all_list = []
   usage_list = []
   account_list = []
   getID = account_info.objects.get(accountinfoid = id)
   account_list.append(getID)
   
   idstr = id + "-" + str(current_date.year)
   pkstr = usage_record.objects.get(accountid = idstr)
   usage_list.append(pkstr)

   all_list = zip(usage_list,account_list)

   #set selected value       
   defmonthval = current_date.month - 1
   #get the month name
   month_obj = datetime.datetime.strptime(str(defmonthval),"%M")
   month_name = month_obj.strftime("%B")
   defval["selectmonth"] = str(defmonthval)
   defval["selectyear"] = str(current_date.year) 
   defval["monthval"]  = month_name
   getID = account_info.objects.get(accountinfoid = id)
   account_list.append(getID)
   
   idstr = id + "-" + str(current_date.year)
   pkstr = usage_record.objects.get(accountid = idstr)
   usage_list.append(pkstr)
   context["balance"] = pkstr.commulative_bill
   
   yearstr = str(current_date.year)
   context = {}
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)  
   
   accstr = id + "-" + yearstr
   get_usageid = usage_record.objects.get(accountid = accstr)
   #amount paid
   amountpaid_jan = request.POST.get('amountpaid_jan')
   amountpaid_feb = request.POST.get('amountpaid_feb')
   amountpaid_mar= request.POST.get('amountpaid_mar')
   amountpaid_apr = request.POST.get('amountpaid_apr')
   amountpaid_may = request.POST.get('amountpaid_may')
   amountpaid_jun = request.POST.get('amountpaid_jun')
   amountpaid_jul = request.POST.get('amountpaid_jul')
   amountpaid_aug = request.POST.get('amountpaid_aug')
   amountpaid_sept = request.POST.get('amountpaid_sept')
   amountpaid_oct = request.POST.get('amountpaid_oct')
   amountpaid_nov = request.POST.get('amountpaid_nov')
   amountpaid_dec = request.POST.get('amountpaid_dec')
   
   or_number = request.POST.get("or_number")
   or_number1 = request.POST.get("or_number1")
   postedby = request.session.get(ReqParams.name)
   

   #Totals
   totalpkstr = getID.barangay + "-" + str(current_date.year)
   total_paid_brgy = barangay_report.objects.get(pk = totalpkstr)
   yearly_record = Year_Report.objects.get(pk = current_date.year)

   if request.method == "POST":
      
      if amountpaid_jan != None:
         if amountpaid_jan != "":
            get_usageid.paidamt_jan += float(amountpaid_jan)
            get_usageid.ior_jan += or_number1 + ":php" + amountpaid_jan + "||"
            get_usageid.datepaid_jan = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_january += float(amountpaid_jan)
            total_paid_brgy.total_due_ytd -= float(amountpaid_jan)
            total_paid_brgy.total_due_january -= float(amountpaid_jan)
            total_paid_brgy.total_paid_ytd += float(amountpaid_jan)      
            total_paid_brgy.save()
            yearly_record.total_paid_january += float(amountpaid_jan)
            yearly_record.total_due_january -= float(amountpaid_jan)
            yearly_record.total_paid_ytd += float(amountpaid_jan)
            yearly_record.total_due_ytd -= float(amountpaid_jan)
            yearly_record.save()

            

            #we generate excess payment
            if float(amountpaid_jan) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_jan) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_jan)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save() 
         
         
      if amountpaid_feb != None:
         if amountpaid_feb != "":
            #February     
            get_usageid.paidamt_feb += float(amountpaid_feb)
            get_usageid.ior_feb = or_number1  + ":php" + amountpaid_feb + "||"
            get_usageid.datepaid_feb = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_february += float(amountpaid_feb)
            total_paid_brgy.total_due_ytd -= float(amountpaid_feb) 
            total_paid_brgy.total_due_february -= float(amountpaid_feb)
            total_paid_brgy.total_paid_ytd += float(amountpaid_feb)     
            total_paid_brgy.save()
            yearly_record.total_paid_february += float(amountpaid_feb)
            yearly_record.total_paid_ytd += float(amountpaid_feb)
            yearly_record.total_due_ytd -= float(amountpaid_feb)
            yearly_record.total_due_february -= float(amountpaid_feb)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_feb) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_feb) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_feb)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
      
         
      if amountpaid_mar != None:
         if amountpaid_mar != "":
            #March
            get_usageid.paidamt_mar += float(amountpaid_mar)
            get_usageid.ior_mar = or_number1  + ":php" + amountpaid_mar + "||"
            get_usageid.datepaid_mar = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_march += float(amountpaid_mar)
            total_paid_brgy.total_due_ytd -= float(amountpaid_mar)
            total_paid_brgy.total_due_march -= float(amountpaid_mar)
            total_paid_brgy.total_paid_ytd += float(amountpaid_mar)    
            total_paid_brgy.save()
            yearly_record.total_paid_march += float(amountpaid_mar)
            yearly_record.total_paid_ytd += float(amountpaid_mar)
            yearly_record.total_due_ytd += float(amountpaid_mar)
            yearly_record.total_due_march -= float(amountpaid_mar)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_mar) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_mar) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_mar)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
              

      if amountpaid_apr != None:      
         if amountpaid_apr != "":     
            #April
            get_usageid.paidamt_apr += float(amountpaid_apr)
            get_usageid.ior_apr = or_number1  + ":php" + amountpaid_apr + "||"
            get_usageid.datepaid_apr = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_april += float(amountpaid_apr)
            total_paid_brgy.total_due_ytd -= float(amountpaid_apr)
            total_paid_brgy.total_due_april -= float(amountpaid_apr)
            total_paid_brgy.total_paid_ytd += float(amountpaid_apr)     
            total_paid_brgy.save()
            yearly_record.total_paid_april += float(amountpaid_apr)
            yearly_record.total_paid_ytd += float(amountpaid_apr)
            yearly_record.total_due_ytd -= float(amountpaid_apr)
            yearly_record.total_due_april -= float(amountpaid_apr)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_apr) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_apr) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_apr)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
      
         
      if amountpaid_may !=None:
         if amountpaid_may != "":
            #May
            get_usageid.paidamt_may += float(amountpaid_may)
            get_usageid.ior_may = or_number1  + ":php" + amountpaid_may + "||"
            get_usageid.datepaid_may = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_may += float(amountpaid_may)
            total_paid_brgy.total_due_ytd -= float(amountpaid_may)
            total_paid_brgy.total_due_may -= float(amountpaid_may)
            total_paid_brgy.total_paid_ytd += float(amountpaid_may)    
            total_paid_brgy.save()
            yearly_record.total_paid_may += float(amountpaid_may)
            yearly_record.total_paid_ytd += float(amountpaid_may)
            yearly_record.total_due_ytd -= float(amountpaid_may)
            yearly_record.total_due_may -= float(amountpaid_may)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_may) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_may) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_may)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
      
         
      if amountpaid_jun != None: 
         if amountpaid_jun != "":       
            #June
            get_usageid.paidamt_jun += float(amountpaid_jun)
            get_usageid.ior_jun = or_number1  + ":php" + amountpaid_jun + "||"
            get_usageid.datepaid_jun = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_june += float(amountpaid_jun)
            total_paid_brgy.total_due_ytd -= float(amountpaid_jun) 
            total_paid_brgy.total_due_june -= float(amountpaid_jun)
            total_paid_brgy.total_paid_ytd += float(amountpaid_jun)   
            total_paid_brgy.save()
            yearly_record.total_paid_june += float(amountpaid_jun)
            yearly_record.total_paid_ytd += float(amountpaid_jun)
            yearly_record.total_due_ytd -= float(amountpaid_jun)
            yearly_record.total_due_june -= float(amountpaid_jun)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_jun) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_jun) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_jun)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
      
          
      if amountpaid_jul != None:
         if amountpaid_jul != "":
            #July
            get_usageid.paidamt_jul += float(amountpaid_jul)
            get_usageid.ior_jul = or_number1  + ":php" + amountpaid_jul + "||"
            get_usageid.datepaid_jul = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_july += float(amountpaid_jul)
            total_paid_brgy.total_due_ytd -= float(amountpaid_jul)
            total_paid_brgy.total_due_july -= float(amountpaid_jul)
            total_paid_brgy.total_paid_ytd += float(amountpaid_jul)    
            total_paid_brgy.save()
            yearly_record.total_paid_july += float(amountpaid_jul)
            yearly_record.total_paid_ytd += float(amountpaid_jul)
            yearly_record.total_due_ytd -= float(amountpaid_jul)
            yearly_record.total_due_july -= float(amountpaid_jul)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_jul) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_jul) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_jul)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()

         

      if amountpaid_aug != None:
         if amountpaid_aug != "":
            #August    
            get_usageid.paidamt_aug += float(amountpaid_aug)
            get_usageid.ior_aug = or_number1  + ":php" + amountpaid_aug + "||"
            get_usageid.datepaid_aug = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_august += float(amountpaid_aug)
            total_paid_brgy.total_due_ytd -= float(amountpaid_aug)
            total_paid_brgy.total_due_august -= float(amountpaid_aug)
            total_paid_brgy.total_paid_ytd += float(amountpaid_aug)    
            total_paid_brgy.save()
            yearly_record.total_paid_august += float(amountpaid_aug)
            yearly_record.total_paid_ytd += float(amountpaid_aug)
            yearly_record.total_due_ytd -= float(amountpaid_aug)
            yearly_record.total_due_august -= float(amountpaid_aug)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_aug) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_aug) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_aug)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
      
         

      if amountpaid_sept != None:
         if amountpaid_sept != "":
            
            get_usageid.paidamt_sept += float(amountpaid_sept)
            get_usageid.ior_sept = or_number1  + ":php" + amountpaid_sept + "||"
            get_usageid.datepaid_sept = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_september += float(amountpaid_sept)
            total_paid_brgy.total_due_ytd -= float(amountpaid_sept)
            total_paid_brgy.total_due_september -= float(amountpaid_sept)
            total_paid_brgy.total_paid_ytd += float(amountpaid_sept)    
            total_paid_brgy.save()
            yearly_record.total_paid_september += float(amountpaid_sept)
            yearly_record.total_paid_ytd += float(amountpaid_sept)
            yearly_record.total_due_ytd -= float(amountpaid_sept)
            yearly_record.total_due_september -= float(amountpaid_sept)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_sept) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_sept) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_sept)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
         
         
      if amountpaid_oct != None:
         if amountpaid_oct != "":
            #October
            get_usageid.paidamt_oct += float(amountpaid_oct)
            get_usageid.ior_oct = or_number1  + ":php" + amountpaid_oct + "||"
            get_usageid.datepaid_oct = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_october += float(amountpaid_oct)
            total_paid_brgy.total_due_ytd -= float(amountpaid_oct) 
            total_paid_brgy.total_due_october -= float(amountpaid_oct)
            total_paid_brgy.total_paid_ytd += float(amountpaid_oct)   
            total_paid_brgy.save()
            yearly_record.total_paid_oct += float(amountpaid_oct)
            yearly_record.total_paid_ytd += float(amountpaid_oct)
            yearly_record.total_due_ytd -= float(amountpaid_oct)
            yearly_record.total_due_october -= float(amountpaid_oct)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_oct) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_oct) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_oct)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
     
         
      if amountpaid_nov != None:
         if amountpaid_nov != "":
            #November
            get_usageid.paidamt_nov += float(amountpaid_nov)
            get_usageid.ior_nov = or_number1  + ":php" + amountpaid_nov + "||"
            get_usageid.datepaid_nov = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_november += float(amountpaid_nov)
            total_paid_brgy.total_due_ytd -= float(amountpaid_nov)
            total_paid_brgy.total_due_november -= float(amountpaid_nov)
            total_paid_brgy.total_paid_ytd += float(amountpaid_nov)    
            total_paid_brgy.save()
            yearly_record.total_paid_november += float(amountpaid_nov)
            yearly_record.total_paid_ytd += float(amountpaid_nov)
            yearly_record.total_due_ytd -= float(amountpaid_nov)
            yearly_record.total_due_november -= float(amountpaid_nov)
            yearly_record.save()

            #we generate excess payment
            if float(amountpaid_nov) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_nov) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_nov)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()
      
         
      if amountpaid_dec != None:
         if amountpaid_dec != "":
            #December
            get_usageid.paidamt_dec += float(amountpaid_dec)
            get_usageid.ior_dec = or_number1  + ":php" + amountpaid_dec + "||"
            get_usageid.datepaid_dec = current_date

            #we set total paid per month
            total_paid_brgy.total_paid_december += float(amountpaid_dec)
            total_paid_brgy.total_due_ytd -= float(amountpaid_dec)
            total_paid_brgy.total_due_december -= float(amountpaid_dec)
            total_paid_brgy.total_paid_ytd += float(amountpaid_dec)    
            total_paid_brgy.save()
            yearly_record.total_paid_december += float(amountpaid_dec)
            yearly_record.total_paid_ytd += float(amountpaid_dec)
            yearly_record.total_due_ytd -= float(amountpaid_dec)
            yearly_record.total_due_december -= float(amountpaid_dec)
            yearly_record.save()

            
               
            #we generate excess payment
            if float(amountpaid_dec) > get_usageid.commulative_bill:
               balance = get_usageid.commulative_bill
               excess = float(amountpaid_dec) - balance 
               get_usageid.excesspayment = excess 
               get_usageid.commulative_bill = 0
               get_usageid.save()
            else:
               amountexcess = get_usageid.excesspayment + float(amountpaid_dec)
               get_usageid.commulative_bill -= amountexcess
               get_usageid.save()

      

      if or_number != None: 
         if or_number != "":                    
            #we call the clear bill method or non installment method
            clear_bill(request,getID.accountinfoid,or_number)
      else:
         pathstr = "/source_access"  + "/Payment=" + id
         return HttpResponseRedirect((pathstr))
         
      pathstr = "/source_access"  + "/Payment=" + id
      return HttpResponseRedirect((pathstr))

   


   #get the commulative bill  
   context["balance"] = str(get_usageid.commulative_bill)
   context["Fullname"] = getID.firstname + " " + getID.lastname
   context["Id"] = getID.accountinfoid
   context[ReqParams.address] = getID.address
   context[ReqParams.userid] =  request.session.get(ReqParams.userid)
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)

   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
      template = "html/consumer_usage.payment.html"
   else:
      template = "html/unavailable.html"   

   return render(request,template,{"account":getID,"usage":pkstr,"context":context,
                                          'defval':defval,'month':month.getMonth,'monthval':month,
                                          'params':ReqParams,"monthval":month})      



def pay_per_month(request):
   current_date = date.today()
   id = request.POST["id"]
   month = request.POST["month"]
   or_number = request.POST["or_number"]
   paymenthistory = payment_history()
   if request.method == "POST":
      usage = usage_record.objects.get(pk = id)
      account = account_info.objects.get(pk = usage.accountinfoid)
      yearly_record = Year_Report.objects.get(pk = usage.year)  
      
      total_paid_brgy = barangay_report.objects.get(pk = account.barangay + "-" + str(usage.year))
      if month == "1":
         diff = usage.totalbill_jan - usage.paidamt_jan
         usage.paidamt_jan += diff
         usage.commulative_bill -= diff
         usage.ior_jan = or_number 
         usage.datepaid_jan = current_date
         usage.save()

         total_paid_brgy.total_paid_january += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_january  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_january  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_january -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()

         

      if month == "2":
         diff = usage.totalbill_feb - usage.paidamt_feb
         usage.paidamt_feb += diff
         usage.commulative_bill -= diff
         usage.ior_feb = or_number 
         usage.datepaid_feb = current_date
         usage.save()

         total_paid_brgy.total_paid_february += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_february  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_february  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_february -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()

         

      if month == "3":
         diff = usage.totalbill_mar - usage.paidamt_mar
         usage.paidamt_mar += diff
         usage.commulative_bill -= diff
         usage.ior_mar = or_number 
         usage.datepaid_mar = current_date
         usage.save()

         total_paid_brgy.total_paid_march += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_march  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_march  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_march -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()

         

      if month == "4":
         diff = usage.totalbill_apr - usage.paidamt_apr
         usage.paidamt_apr += diff
         usage.commulative_bill -= diff
         usage.ior_apr = or_number 
         usage.datepaid_apr = current_date
         usage.save()

         total_paid_brgy.total_paid_april += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_april  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_april  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_april -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()

         

      if month == "5":
         diff = usage.totalbill_may - usage.paidamt_may
         usage.paidamt_may += diff
         usage.commulative_bill -= diff
         usage.ior_may = or_number 
         usage.datepaid_may = current_date
         usage.save()

         total_paid_brgy.total_paid_may += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_may  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_may  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_may -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()

         

      if month == "6":
         diff = usage.totalbill_jun - usage.paidamt_jun
         usage.paidamt_jun += diff
         usage.commulative_bill -= diff
         usage.ior_jun = or_number 
         usage.datepaid_jun = current_date
         usage.save()

         total_paid_brgy.total_paid_june += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_june  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_june  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_june-= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()   

         

      if month == "7":
         diff = usage.totalbill_jul - usage.paidamt_jul
         usage.paidamt_jul += diff
         usage.commulative_bill -= diff
         usage.ior_jul = or_number 
         usage.datepaid_jul = current_date
         usage.save()

         total_paid_brgy.total_paid_july += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_july  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_july  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_july -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()   

           

      if month == "8":
         diff = usage.totalbill_aug - usage.paidamt_aug
         usage.paidamt_aug += diff
         usage.commulative_bill -= diff
         usage.ior_aug = or_number 
         usage.datepaid_aug = current_date
         usage.save()

         total_paid_brgy.total_paid_august += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_august  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_august  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_august -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()  

          

      if month == "9":
         diff = usage.totalbill_sept - usage.paidamt_sept
         usage.paidamt_sept += diff
         usage.commulative_bill -= diff
         usage.ior_sept = or_number 
         usage.datepaid_sept = current_date
         usage.save()

         total_paid_brgy.total_paid_september += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_september  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_september  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_september -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save() 

          

      if month == "10":
         diff = usage.totalbill_oct - usage.paidamt_oct
         usage.paidamt_oct += diff
         usage.commulative_bill -= diff
         usage.ior_oct = or_number 
         usage.datepaid_oct = current_date
         usage.save()

         total_paid_brgy.total_paid_october += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_october  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_october  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_october -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()   

         

      if month == "11":
         diff = usage.totalbill_nov - usage.paidamt_nov
         usage.paidamt_nov += diff
         usage.commulative_bill -= diff
         usage.ior_nov = or_number 
         usage.datepaid_nov = current_date
         usage.save()

         total_paid_brgy.total_paid_november += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_november  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_november  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_november -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save() 

         
      if month == "12":
         diff = usage.totalbill_dec - usage.paidamt_dec
         usage.paidamt_dec += diff
         usage.commulative_bill -= diff
         usage.ior_dec = or_number 
         usage.datepaid_dec = current_date
         usage.save()

         total_paid_brgy.total_paid_december += float(diff)
         total_paid_brgy.total_due_ytd -= float(diff)
         total_paid_brgy.total_due_december  -= float(diff)
         total_paid_brgy.total_paid_ytd += float(diff)    
         total_paid_brgy.save()
         yearly_record.total_paid_december  += float(diff)
         yearly_record.total_paid_ytd += float(diff)
         yearly_record.total_due_ytd -= float(diff)
         yearly_record.total_due_december -= float(diff)
         yearly_record.save()

         paymenthistory.date = current_date
         paymenthistory.or_number = or_number
         paymenthistory.postedby = request.session.get(ReqParams.name)
         paymenthistory.consumer = account.firstname + " " + account.lastname
         paymenthistory.meternumber = account.meternumber
         paymenthistory.year = current_date.year
         paymenthistory.accountinfoid = account.accountinfoid
         paymenthistory.amount = diff
         paymenthistory.time = time.asctime( time.localtime(time.time()) )
         paymenthistory.save()   

         

   return HttpResponse(json.dumps({"success": True}), "application/json")      