from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect

from myApp.DataTransfer import Payment_History
from .models import *
from django.template import Context
from datetime import date
from django.contrib import messages
from .BillingDB import *
from .BillingUtil import *
from .Payment import *
from .Application import *
import datetime
import time



def Search(request):


    #rendering page
   template = ""
   sessionval = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/Search_account.Payment.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")


   account_list = []
   usage_list = []
   all_list = []

   message = ""
   current_date = date.today()
   year = str(current_date.year)
   all_record = usage_record.objects.filter(year = current_date.year)
   all_accounts = account_info.objects.all()

   index = 0
   maxlen = 0
   if ReqParams.index1 in request.session:
      index = request.session.get(ReqParams.index1)
   else:
      index = 0
   if ReqParams.max_length1 in request.session:
      maxlen = request.session.get(ReqParams.max_length1)
   else:
      maxlen = 25

   table_length = all_accounts.count()

   #first display
   accounts = []
   account_bill = []
   for element in range(index,maxlen):
      accounts.append(all_accounts[element])
      acc = all_accounts[element]
      account_bill.append(usage_record.objects.get(pk = acc.accountinfoid + "-" + str(current_date.year)))

   #zip list
   all_list = zip(accounts,account_bill)

   context = {
      "name":request.session.get(ReqParams.name),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "table_length":table_length,
      "userid":request.session.get(ReqParams.userid)
   }
   context[ReqParams.index] = index
   context[ReqParams.max_length] = maxlen

   search_for = request.POST.get('search_for')
   submitbtn = request.POST.get("Post")

   if request.method == "POST":
      index = 0
      maxlen = 0
      if ReqParams.index1 in request.session:
         index = request.session.get(ReqParams.index1)
      else:
         index = 0
      if ReqParams.max_length1 in request.session:
         maxlen = request.session.get(ReqParams.max_length1)
      else:
         maxlen = 25

      accounts = []
      account_bill = []

      if search_for:
         retval = None
         retval1 = None
         isMatch_for_meternum = account_info.objects.filter(meternumber__icontains=search_for)
         isMatch_for_acc = account_info.objects.filter(accountinfoid__icontains=search_for)
         isMatch_for_name = account_info.objects.filter(firstname__icontains=search_for)
         isMatch_for_lastname = account_info.objects.filter(lastname__icontains=search_for)


         if isMatch_for_meternum:
            retval = isMatch_for_meternum
         elif isMatch_for_acc:
            retval = isMatch_for_acc
         elif isMatch_for_name:
            retval = isMatch_for_name
         elif isMatch_for_lastname:
            retval = isMatch_for_lastname

         if retval:
            for element in retval:
               account_bill.append(usage_record.objects.get(pk = element.accountinfoid + "-" + str(current_date.year)))
            all_list = zip(retval,account_bill)

         return render(request,template,{"ReqParams":ReqParams,'all_list': all_list,"context":context})

      if submitbtn == "Next":
         index = index + 25
         total = maxlen + 25
         if total > table_length:
            maxlen = table_length
         else:
            maxlen = maxlen +  25
         for element in range(index,maxlen):
            accounts.append(all_accounts[element])
            acc = all_accounts[element]
            account_bill.append(usage_record.objects.get(pk = acc.accountinfoid + "-" + str(current_date.year)))
         #zip list
         all_list = zip(accounts,account_bill)

         request.session[ReqParams.index1] = index
         request.session[ReqParams.max_length1] = maxlen
         context[ReqParams.index] = index
         context[ReqParams.max_length] = maxlen
         #return render(request,template,{"ReqParams":ReqParams,'all_list': all_list,"context":context,"message":message})
         return HttpResponseRedirect("/source_access/Payment")

      if submitbtn == "Previous":
         index = index -  25
         maxlen = maxlen - 25
         diff = index - 25

         if index < 0:
            return HttpResponseRedirect("/source_access/Payment")

         for element in range(index,maxlen):
            accounts.append(all_accounts[element])
            acc = all_accounts[element]
            print(acc)
            account_bill.append(usage_record.objects.get(pk = acc.accountinfoid + "-" + str(current_date.year)))

         #zip list
         all_list = zip(accounts,account_bill)

         request.session[ReqParams.index1] = index
         request.session[ReqParams.max_length1] = maxlen
         context[ReqParams.index] = index
         context[ReqParams.max_length] = maxlen

         #return render(request,template,{"ReqParams":ReqParams,'all_list': all_list,"context":context,"message":message})
         return HttpResponseRedirect("/source_access/Payment")



   return render(request,template,{"ReqParams":ReqParams,'all_list': all_list,"context":context,"message":message})



def pay_bill(request,id):

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
   amountpaid = request.POST.get('amount')
   or_number = request.POST.get("or_number")
   postedby = request.session.get("postedby")


   #Totals
   totalpkstr = getID.barangay + "-" + str(current_date.year)
   total_paid_brgy = barangay_report.objects.get(pk = totalpkstr)
   yearly_record = Year_Report.objects.get(pk = current_date.year)

   payment = payment_history()

   if request.method == "POST":

      #month of non payment
      prev_list = UnpaidMonth(id,str(current_date.year - 1))#list of unpaid month previous year
      current_list = UnpaidMonth(id,str(current_date.year))#list of unpaid this year
      ziplist = (prev_list,current_list)

      print(current_list)

      #Payment History
      user = SystemUser.objects.get(pk = request.session.get(ReqParams.userid))
      payment.amount = float(amountpaid)
      payment.date = current_date
      payment.or_number = or_number
      payment.time = time.asctime( time.localtime(time.time()) )
      payment.postedby = user.firstname + " " + user.lastname
      payment.consumer = getID.firstname + " " + getID.lastname
      payment.accountinfoid = getID.accountinfoid
      payment.meternumber = getID.meternumber
      payment.year = current_date.year
      payment.save()

      get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

      postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_history
      get_usageid.postedby_history = postedbystr
      amountpaidstr =  str(amountpaid) + "|" + get_usageid.amountpaid_history
      get_usageid.amountpaid_history = amountpaidstr
      datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_history
      get_usageid.datepaid_history = datestr
      or_numberstr = or_number + "|" + get_usageid.or_number_history
      get_usageid.or_number_history = or_numberstr

      #excess payment and  commulative bill
      if float(amountpaid) > get_usageid.commulative_bill:
         #excess payment
         excesspayment = float(amountpaid) - get_usageid.commulative_bill
         get_usageid.excesspayment = excesspayment
         get_usageid.commulative_bill = 0
         get_usageid.save()
      else:
         get_usageid.commulative_bill = get_usageid.commulative_bill -  float(amountpaid)
         get_usageid.save()

      #january
      if 1 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:

               #saving all amount paid
               tobePosted = 0
               difference = 0
               if get_usageid.totalbill_jan > get_usageid.paidamt_jan:
                  difference = get_usageid.totalbill_jan - get_usageid.paidamt_jan
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_jan += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_jan += tobePosted
                     amountpaid = 0


               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_jan
               get_usageid.postedby_jan = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_jan
               get_usageid.amountpaid_str_jan = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_jan
               get_usageid.ior_jan = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jan
               get_usageid.datepaid_jan = datestr



               #we set total paid per month
               total_paid_brgy.total_paid_january += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                  total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_january < float(tobePosted):
                  total_paid_brgy.total_due_january = 0
               else:
                  total_paid_brgy.total_due_january -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_january += float(tobePosted)
               if yearly_record.total_due_january < float(tobePosted):
                  yearly_record.total_due_january = 0
               else:
                  yearly_record.total_due_january -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()

      if 2 in prev_list and amountpaid != 0:

         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:

               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_feb > get_usageid.paidamt_feb:
                  difference = get_usageid.totalbill_feb - get_usageid.paidamt_feb
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_feb += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_feb += tobePosted
                     amountpaid = 0



               #February
               #saving all amount paid

               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_feb
               get_usageid.postedby_feb = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_feb
               get_usageid.amountpaid_str_feb = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_feb
               get_usageid.ior_feb = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jan
               get_usageid.datepaid_feb = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_february += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_february < float(tobePosted):
                  total_paid_brgy.total_due_february = 0
               else:
                  total_paid_brgy.total_due_february -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_february += float(tobePosted)
               if yearly_record.total_due_february < float(tobePosted):
                  yearly_record.total_due_february = 0
               else:
                  yearly_record.total_due_february -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()
               get_usageid.save()

      #p March
      if 3 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:

               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_mar > get_usageid.paidamt_mar:
                  difference = get_usageid.totalbill_mar - get_usageid.paidamt_mar
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_mar += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_mar += tobePosted
                     amountpaid = 0


               #March
               #saving all amount paid
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_mar
               get_usageid.postedby_mar = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_mar
               get_usageid.amountpaid_str_mar = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_mar
               get_usageid.ior_mar = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_mar
               get_usageid.datepaid_mar = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_march += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_march < float(tobePosted):
                  total_paid_brgy.total_due_march = 0
               else:
                  total_paid_brgy.total_due_march -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_march += float(tobePosted)
               if yearly_record.total_due_march < float(tobePosted):
                  yearly_record.total_due_march = 0
               else:
                  yearly_record.total_due_march -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()

      #April
      if 4 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:

               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_apr > get_usageid.paidamt_apr:
                  difference = get_usageid.totalbill_apr - get_usageid.paidamt_apr
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - get_usageid.totalbill_apr
                     tobePosted = difference
                     get_usageid.paidamt_apr = tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_apr += tobePosted
                     amountpaid = 0



               #April
               #saving all amount paid

               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_apr
               get_usageid.postedby_apr = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_apr
               get_usageid.amountpaid_str_apr = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_apr
               get_usageid.ior_apr = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_apr
               get_usageid.datepaid_apr = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_april += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_april < float(tobePosted):
                  total_paid_brgy.total_due_april = 0
               else:
                  total_paid_brgy.total_due_april -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_april += float(tobePosted)
               if yearly_record.total_due_april < float(tobePosted):
                  yearly_record.total_due_april = 0
               else:
                  yearly_record.total_due_april -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()

      #current May
      if 5 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_may > get_usageid.paidamt_may:
                  difference = get_usageid.totalbill_may - get_usageid.paidamt_may
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_may += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_may += tobePosted
                     amountpaid = 0



               #May
               #saving all amount paid

               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_may
               get_usageid.postedby_may = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_may
               get_usageid.amountpaid_str_may = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_may
               get_usageid.ior_may = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_may
               get_usageid.datepaid_may = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_may += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_may < float(tobePosted):
                  total_paid_brgy.total_due_may = 0
               else:
                  total_paid_brgy.total_due_may -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_may += float(tobePosted)
               if yearly_record.total_due_may < float(tobePosted):
                  yearly_record.total_due_january = 0
               else:
                  yearly_record.total_due_may -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)
               yearly_record.save()


               get_usageid.save()

      #june
      if 6 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_jun > get_usageid.paidamt_jun:
                  difference = get_usageid.totalbill_jun - get_usageid.paidamt_jun
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_jun += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_jun += tobePosted
                     amountpaid = 0



               #June
               #saving all amount paid
               get_usageid.paidamt_jun += float(tobePosted)
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_jun
               get_usageid.postedby_jun = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_jun
               get_usageid.amountpaid_str_jun = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_jun
               get_usageid.ior_jun = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jun
               get_usageid.datepaid_jun = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_june += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_june < float(tobePosted):
                  total_paid_brgy.total_due_june = 0
               else:
                  total_paid_brgy.total_due_june -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_june += float(tobePosted)
               if yearly_record.total_due_june < float(tobePosted):
                  yearly_record.total_due_january = 0
               else:
                  yearly_record.total_due_june -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)
               yearly_record.save()


               get_usageid.save()

      #July
      if 7 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_jul > get_usageid.paidamt_jul:
                  difference = get_usageid.totalbill_jul - get_usageid.paidamt_jul
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_jul += tobePosted

                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_jul += tobePosted
                     amountpaid = 0



               #July
               #saving all amount paid

               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_jul
               get_usageid.postedby_jul = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_jul
               get_usageid.amountpaid_str_jul = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_jul
               get_usageid.ior_jul = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jul
               get_usageid.datepaid_jul = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_july += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_july < float(tobePosted):
                  total_paid_brgy.total_due_july = 0
               else:
                  total_paid_brgy.total_due_july -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_july += float(tobePosted)
               if yearly_record.total_due_july < float(tobePosted):
                  yearly_record.total_due_july = 0
               else:
                  yearly_record.total_due_july -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()
               get_usageid.save()


      if 8 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_aug > get_usageid.paidamt_aug:
                  difference = get_usageid.totalbill_aug - get_usageid.paidamt_aug
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_aug += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_aug += tobePosted
                     amountpaid = 0



               #August
               #saving all amount paid
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_aug
               get_usageid.postedby_aug = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_aug
               get_usageid.amountpaid_str_aug = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_aug
               get_usageid.ior_aug = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_aug
               get_usageid.datepaid_aug = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_august += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_august < float(tobePosted):
                  total_paid_brgy.total_due_august = 0
               else:
                  total_paid_brgy.total_due_august -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_august += float(tobePosted)
               if yearly_record.total_due_august < float(tobePosted):
                  yearly_record.total_due_august = 0
               else:
                  yearly_record.total_due_august -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()


       # September
      if 9 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_sept > get_usageid.paidamt_sept:
                  difference = get_usageid.totalbill_sept - get_usageid.paidamt_sept
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_sept += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_sept += tobePosted
                     amountpaid = 0



               get_usageid.postedby_sept = request.session.get(ReqParams.postedby)
               get_usageid.amountpaid_str_sept += str(tobePosted) + "|" #saving all amount paid
               get_usageid.ior_sept += or_number  + "|"
               get_usageid.datepaid_sept += time.asctime( time.localtime(time.time()) ) + "|"

               #we set total paid per month
               total_paid_brgy.total_paid_september += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_september < float(tobePosted):
                  total_paid_brgy.total_due_september = 0
               else:
                  total_paid_brgy.total_due_september -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_september += float(tobePosted)
               if yearly_record.total_due_september < float(tobePosted):
                  yearly_record.total_due_september = 0
               else:
                  yearly_record.total_due_september -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


            get_usageid.save()

      # October
      if 10 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_oct > get_usageid.paidamt_oct:
                  difference = get_usageid.totalbill_oct - get_usageid.paidamt_oct
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_oct += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_oct += tobePosted
                     amountpaid = 0



               #October
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_oct
               get_usageid.postedby_oct = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_oct
               get_usageid.amountpaid_str_oct = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_oct
               get_usageid.ior_oct = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_oct
               get_usageid.datepaid_oct = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_october += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_october < float(tobePosted):
                  total_paid_brgy.total_due_october = 0
               else:
                  total_paid_brgy.total_due_october -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_july += float(tobePosted)
               if yearly_record.total_due_october < float(tobePosted):
                  yearly_record.total_due_october = 0
               else:
                  yearly_record.total_due_october -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()

      #November
      if 11 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_nov > get_usageid.paidamt_nov:
                  difference = get_usageid.totalbill_nov - get_usageid.paidamt_nov
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted  = difference
                     get_usageid.paidamt_nov += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_nov += tobePosted
                     amountpaid = 0



               #November
               #saving all amount paid
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_nov
               get_usageid.postedby_nov = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_nov
               get_usageid.amountpaid_str_nov = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_nov
               get_usageid.ior_nov = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_nov
               get_usageid.datepaid_nov = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_november += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_july < float(tobePosted):
                  total_paid_brgy.total_due_july = 0
               else:
                  total_paid_brgy.total_due_july -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_july += float(tobePosted)
               if yearly_record.total_due_july < float(tobePosted):
                  yearly_record.total_due_july = 0
               else:
                  yearly_record.total_due_july -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()

      if 12 in prev_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year - 1)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year - 1))
            if amountpaid:
               #December
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_dec > get_usageid.paidamt_dec:
                  difference = get_usageid.totalbill_dec - get_usageid.paidamt_dec
                  if tobePosted >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_dec += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_dec += tobePosted
                     amountpaid = 0


               get_usageid.paidamt_dec += float(tobePosted)
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_dec
               get_usageid.postedby_dec = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_dec
               get_usageid.amountpaid_str_dec = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_dec
               get_usageid.ior_dec = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_dec
               get_usageid.datepaid_dec = datestr


               #we set total paid per month
               total_paid_brgy.total_paid_december += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_december < float(tobePosted):
                  total_paid_brgy.total_due_december = 0
               else:
                  total_paid_brgy.total_due_december -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_december += float(tobePosted)
               if yearly_record.total_due_december < float(tobePosted):
                  yearly_record.total_due_december = 0
               else:
                  yearly_record.total_due_december -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()
               get_usageid.save()


      #current january
      if 1 in current_list and amountpaid != 0:

         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:

               #saving all amount paid
               tobePosted = 0
               difference = 0
               if get_usageid.totalbill_jan > get_usageid.paidamt_jan:
                  difference = get_usageid.totalbill_jan - get_usageid.paidamt_jan
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_jan += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_jan += tobePosted
                     amountpaid = 0


               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_jan
               get_usageid.postedby_jan = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_jan
               get_usageid.amountpaid_str_jan = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_jan
               get_usageid.ior_jan = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jan
               get_usageid.datepaid_jan = datestr


               #we set total paid per month
               total_paid_brgy.total_paid_january += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                  total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_january < float(tobePosted):
                  total_paid_brgy.total_due_january = 0
               else:
                  total_paid_brgy.total_due_january -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_january += float(tobePosted)
               if yearly_record.total_due_january < float(tobePosted):
                  yearly_record.total_due_january = 0
               else:
                  yearly_record.total_due_january -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()



               get_usageid.save()




      #current February
      if 2 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:

               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_feb > get_usageid.paidamt_feb:
                  difference = get_usageid.totalbill_feb - get_usageid.paidamt_feb
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_feb += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_feb += tobePosted
                     amountpaid = 0


               #February
               #saving all amount paid

               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_feb
               get_usageid.postedby_feb = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_feb
               get_usageid.amountpaid_str_feb = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_feb
               get_usageid.ior_feb = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_feb
               get_usageid.datepaid_feb = datestr

               #we set total paid per month
               total_paid_brgy.total_paid_february += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_february < float(tobePosted):
                  total_paid_brgy.total_due_february = 0
               else:
                  total_paid_brgy.total_due_february -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_february += float(tobePosted)
               if yearly_record.total_due_february < float(tobePosted):
                  yearly_record.total_due_february = 0
               else:
                  yearly_record.total_due_february -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()

               get_usageid.save()



      #current march
      if 3 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:

               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_mar > get_usageid.paidamt_mar:
                  difference = get_usageid.totalbill_mar - get_usageid.paidamt_mar
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_mar += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_mar += tobePosted
                     amountpaid = 0
            #March
            #saving all amount paid
            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_mar
            get_usageid.postedby_mar = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_mar
            get_usageid.amountpaid_str_mar = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_mar
            get_usageid.ior_mar = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_mar
            get_usageid.datepaid_mar = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_march += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_march < float(tobePosted):
               total_paid_brgy.total_due_march = 0
            else:
               total_paid_brgy.total_due_march -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_march += float(tobePosted)
            if yearly_record.total_due_march < float(tobePosted):
               yearly_record.total_due_march = 0
            else:
               yearly_record.total_due_march -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)

            yearly_record.save()


            get_usageid.save()



      #previous April
      if 4 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_apr > get_usageid.paidamt_apr:
                  difference = get_usageid.totalbill_apr - get_usageid.paidamt_apr
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - get_usageid.totalbill_apr
                     tobePosted = difference
                     get_usageid.paidamt_apr += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_apr += tobePosted
                     amountpaid = 0

            #April
            #saving all amount paid
            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_apr
            get_usageid.postedby_apr = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_apr
            get_usageid.amountpaid_str_apr = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_apr
            get_usageid.ior_apr = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_apr
            get_usageid.datepaid_apr = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_april += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_april < float(tobePosted):
               total_paid_brgy.total_due_april = 0
            else:
               total_paid_brgy.total_due_april -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_april += float(tobePosted)
            if yearly_record.total_due_april < float(tobePosted):
               yearly_record.total_due_april = 0
            else:
               yearly_record.total_due_april -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)

            yearly_record.save()


            get_usageid.save()





      #previous May
      if 5 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_may > get_usageid.paidamt_may:
                  difference = get_usageid.totalbill_may - get_usageid.paidamt_may
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_may += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_may += tobePosted
                     amountpaid = 0
            #May
            #saving all amount paid

            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_may
            get_usageid.postedby_may = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_may
            get_usageid.amountpaid_str_may = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_may
            get_usageid.ior_may = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_may
            get_usageid.datepaid_may = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_may += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_may < float(tobePosted):
               total_paid_brgy.total_due_may = 0
            else:
               total_paid_brgy.total_due_may -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_may += float(tobePosted)
            if yearly_record.total_due_may < float(tobePosted):
               yearly_record.total_due_january = 0
            else:
               yearly_record.total_due_may -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)
            yearly_record.save()


            get_usageid.save()





      if 6 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_jun > get_usageid.paidamt_jun:
                  difference = get_usageid.totalbill_jun - get_usageid.paidamt_jun
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_jun += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_jun += tobePosted
                     amountpaid = 0

            #June
            #saving all amount paid

            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_jun
            get_usageid.postedby_jun = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_jun
            get_usageid.amountpaid_str_jun = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_jun
            get_usageid.ior_jun = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jun
            get_usageid.datepaid_jun = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_june += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_june < float(tobePosted):
               total_paid_brgy.total_due_june = 0
            else:
               total_paid_brgy.total_due_june -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_june += float(tobePosted)
            if yearly_record.total_due_june < float(tobePosted):
               yearly_record.total_due_january = 0
            else:
               yearly_record.total_due_june -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)
            yearly_record.save()



            get_usageid.save()





      if 7 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_jul > get_usageid.paidamt_jul:
                  difference = get_usageid.totalbill_jul - get_usageid.paidamt_jul
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_jul += tobePosted

                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_jul += tobePosted
                     amountpaid = 0

            #July
            #saving all amount paid

            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_jul
            get_usageid.postedby_jul = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_jul
            get_usageid.amountpaid_str_jul = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_jul
            get_usageid.ior_jul = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_jul
            get_usageid.datepaid_jul = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_july += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_july < float(tobePosted):
               total_paid_brgy.total_due_july = 0
            else:
               total_paid_brgy.total_due_july -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_july += float(tobePosted)
            if yearly_record.total_due_july < float(tobePosted):
               yearly_record.total_due_july = 0
            else:
               yearly_record.total_due_july -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)

            yearly_record.save()



            get_usageid.save()


      if 8 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_aug > get_usageid.paidamt_aug:
                  difference = get_usageid.totalbill_aug - get_usageid.paidamt_aug
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_aug += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_aug += tobePosted
                     amountpaid = 0

            #August
            #saving all amount paid
            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_aug
            get_usageid.postedby_aug = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_aug
            get_usageid.amountpaid_str_aug = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_aug
            get_usageid.ior_aug = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_aug
            get_usageid.datepaid_aug = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_august += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_august < float(tobePosted):
               total_paid_brgy.total_due_august = 0
            else:
               total_paid_brgy.total_due_august -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_august += float(tobePosted)
            if yearly_record.total_due_august < float(tobePosted):
               yearly_record.total_due_august = 0
            else:
               yearly_record.total_due_august -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)

            yearly_record.save()


            get_usageid.save()


      if 9 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_sept > get_usageid.paidamt_sept:
                  difference = get_usageid.totalbill_sept - get_usageid.paidamt_sept
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_sept += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_sept += tobePosted
                     amountpaid = 0


               get_usageid.postedby_sept = request.session.get(ReqParams.postedby)
               get_usageid.amountpaid_str_sept += str(tobePosted) + "|" #saving all amount paid
               get_usageid.ior_sept += or_number  + "|"
               get_usageid.datepaid_sept += time.asctime( time.localtime(time.time()) ) + "|"

               #we set total paid per month
               total_paid_brgy.total_paid_september += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_september < float(tobePosted):
                  total_paid_brgy.total_due_september = 0
               else:
                  total_paid_brgy.total_due_september -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_september += float(tobePosted)
               if yearly_record.total_due_september < float(tobePosted):
                  yearly_record.total_due_september = 0
               else:
                  yearly_record.total_due_september -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()


               get_usageid.save()


      if 10 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_oct > get_usageid.paidamt_oct:
                  difference = get_usageid.totalbill_oct - get_usageid.paidamt_oct
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_oct += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_oct += tobePosted
                     amountpaid = 0

            #October
            #saving all amount paid
            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_oct
            get_usageid.postedby_oct = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_oct
            get_usageid.amountpaid_str_oct = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_oct
            get_usageid.ior_oct = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_oct
            get_usageid.datepaid_oct = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_october += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_october < float(tobePosted):
               total_paid_brgy.total_due_october = 0
            else:
               total_paid_brgy.total_due_october -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_july += float(tobePosted)
            if yearly_record.total_due_october < float(tobePosted):
               yearly_record.total_due_october = 0
            else:
               yearly_record.total_due_october -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)

            yearly_record.save()


            get_usageid.save()


      if 11 in current_list and amountpaid != 0:
         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))

            if amountpaid:
               ##saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_nov > get_usageid.paidamt_nov:
                  difference = get_usageid.totalbill_nov - get_usageid.paidamt_nov
                  if float(amountpaid) >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted  = difference
                     get_usageid.paidamt_nov += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_nov += tobePosted
                     amountpaid = 0

            #November
            #saving all amount paid
            get_usageid.paidamt_nov += float(tobePosted)
            postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_nov
            get_usageid.postedby_nov = postedbystr
            amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_nov
            get_usageid.amountpaid_str_nov = amountpaidstr
            or_numberstr = or_number + "|" + get_usageid.ior_nov
            get_usageid.ior_nov = or_numberstr
            datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_nov
            get_usageid.datepaid_nov = datestr

            #we set total paid per month
            total_paid_brgy.total_paid_november += float(tobePosted)
            if total_paid_brgy.total_due_ytd < float(tobePosted):
                   total_paid_brgy.total_due_ytd = 0
            else:
               total_paid_brgy.total_due_ytd -= float(tobePosted)

            if total_paid_brgy.total_due_july < float(tobePosted):
               total_paid_brgy.total_due_july = 0
            else:
               total_paid_brgy.total_due_july -= float(tobePosted)

            total_paid_brgy.total_paid_ytd += float(tobePosted)
            total_paid_brgy.save()

            yearly_record.total_paid_july += float(tobePosted)
            if yearly_record.total_due_july < float(tobePosted):
               yearly_record.total_due_july = 0
            else:
               yearly_record.total_due_july -= float(tobePosted)

            yearly_record.total_paid_ytd += float(tobePosted)
            if yearly_record.total_due_ytd < float(tobePosted):
               yearly_record.total_due_ytd = 0
            else:
               yearly_record.total_due_ytd -= float(tobePosted)

            yearly_record.save()

            get_usageid.save()


      if 12 in current_list and amountpaid != 0:

         if usage_record.objects.filter(pk = id + "-" + str(current_date.year)).exists():
            get_usageid = usage_record.objects.get(pk = id + "-" + str(current_date.year))
            if amountpaid:
               #December
               #saving all amount paid
               difference = 0
               tobePosted = 0
               if get_usageid.totalbill_dec > get_usageid.paidamt_dec:
                  difference = get_usageid.totalbill_dec - get_usageid.paidamt_dec
                  if tobePosted >= difference:
                     amountpaid = float(amountpaid) - difference
                     tobePosted = difference
                     get_usageid.paidamt_dec += tobePosted
                  else:
                     tobePosted = float(amountpaid)
                     get_usageid.paidamt_dec += tobePosted
                     amountpaid = 0

               get_usageid.paidamt_dec += float(tobePosted)
               postedbystr = request.session.get(ReqParams.postedby) + "|" + get_usageid.postedby_dec
               get_usageid.postedby_dec = postedbystr
               amountpaidstr =  str(tobePosted) + "|" + get_usageid.amountpaid_str_dec
               get_usageid.amountpaid_str_dec = amountpaidstr
               or_numberstr = or_number + "|" + get_usageid.ior_dec
               get_usageid.ior_dec = or_numberstr
               datestr = time.asctime( time.localtime(time.time()) ) + "|" + get_usageid.datepaid_dec
               get_usageid.datepaid_dec = datestr


               #we set total paid per month
               total_paid_brgy.total_paid_december += float(tobePosted)
               if total_paid_brgy.total_due_ytd < float(tobePosted):
                     total_paid_brgy.total_due_ytd = 0
               else:
                  total_paid_brgy.total_due_ytd -= float(tobePosted)

               if total_paid_brgy.total_due_december < float(tobePosted):
                  total_paid_brgy.total_due_december = 0
               else:
                  total_paid_brgy.total_due_december -= float(tobePosted)

               total_paid_brgy.total_paid_ytd += float(tobePosted)
               total_paid_brgy.save()

               yearly_record.total_paid_december += float(tobePosted)
               if yearly_record.total_due_december < float(tobePosted):
                  yearly_record.total_due_december = 0
               else:
                  yearly_record.total_due_december -= float(tobePosted)

               yearly_record.total_paid_ytd += float(tobePosted)
               if yearly_record.total_due_ytd < float(tobePosted):
                  yearly_record.total_due_ytd = 0
               else:
                  yearly_record.total_due_ytd -= float(tobePosted)

               yearly_record.save()

               get_usageid.save()

      pathstr = "/source_access"  + "/Payment=" + id
      return HttpResponseRedirect((pathstr))

   #get the commulative bill
   context["balance"] = str(get_usageid.commulative_bill)
   context["Fullname"] = getID.firstname + " " + getID.lastname
   context["Id"] = getID.accountinfoid
   context["consumerid"] = getID.consumerid
   context[ReqParams.address] = getID.address
   context[ReqParams.userid] =  request.session.get(ReqParams.userid)
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)

   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession:
      if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/consumer_usage.payment.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")


   current_date = date.today()
   year_request = request.POST.get(ReqParams.year)
   defval_year = str(current_date.year)
   year_list = []
   retval_list = []


   account = account_info.objects.get(pk = id)
   accountrecord = payment_history.objects.filter(accountinfoid = id)
   for record in accountrecord:
      #for dropdown values(year)
      if record.year not in year_list:
         year_list.append(record.year)
      #default display, current year
      if record.year == current_date.year:
         retval_list.append(record)


   if year_request:
      accountrecord = payment_history.objects.filter(accountinfoid = id)
      for record in accountrecord:

         #default display, current year
         if record.year == int(year_request):
            retval_list.append(record)
      defval_year = year_request

   return render(request,template,{"account":getID,"usage":pkstr,"context":context,
                                          'defval':defval,'month':month.getMonth,'monthval':month,
                                          'params':ReqParams,"monthval":month,"defval":defval_year,"year_list":year_list,})


def paymenthistory(request,id):

   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession:
      if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/payment-history.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   context = {
      "name":request.session.get(ReqParams.name),
   }
   current_date = date.today()
   year_request = request.POST.get(ReqParams.year)
   defval_year = str(current_date.year)
   year_list = []
   retval_list = []

  

   account = account_info.objects.get(pk = id)
   # history = getTotalBill.objects.get(pk = id)
   accountrecord = payment_history.objects.filter(accountinfoid = id)
   for record in accountrecord:
      #for dropdown values(year)
      if record.year not in year_list:
         year_list.append(record.year)
      #default display, current year
      if record.year == current_date.year:
         retval_list.append(record)

   accountrecord = payment_history.objects.filter(accountinfoid = id)
   if year_request:
      accountrecord = payment_history.objects.filter(accountinfoid = id)
      for record in accountrecord:

         #default display, current year
         if record.year == int(year_request):
            retval_list.append(record)
      defval_year = year_request

   return render(request,template,{"retval":retval_list,"account":account,"accoutrecord":accountrecord,"context":context,"defval":defval_year,"year_list":year_list,"ReqParams":ReqParams,"accountrecord":accountrecord})

def history(request,id):

   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession:
      if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/history.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   context = {
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "name":request.session.get(ReqParams.name),
      "0":"Not Paid",
      "1":"Paid"
   }
   PaidStatus = ["Not Paid","Paid"]
   ErrorMessagePass = ""
   index = 0
   commulative_bill = 0
   current_date = date.today()
   year_request = request.POST.get(ReqParams.year)
   account = account_info.objects.get(pk = id)
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
   retval_list = []
   defval_year = str(current_year)
   prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
   readingdate = ""
   for record in  prev_record:
      if record.reading_date.__contains__(str(defval_year)):
         retval_list.append(record)
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
   while current_year >= 2018:
      year_list.append(current_year)
      current_year = current_year - 1

   current_year = 2011
   while current_year >= 2010:
      year_list.append(current_year)
      current_year = current_year - 1

   account = account_info.objects.get(pk = id)
   accountrecord = payment_history.objects.filter(accountinfoid = id)
   for record in accountrecord:
      #for dropdown values(year)
      if record.year not in year_list:
         year_list.append(record.year)
      #default display, current year
      if record.year == current_date.year:
         retval_list.append(record)

   accountrecord = payment_history.objects.filter(accountinfoid = id)
   if year_request:
      accountrecord = payment_history.objects.filter(accountinfoid = id)
      for record in accountrecord:

         #default display, current year
         if record.year == int(year_request):
            retval_list.append(record)
      defval_year = year_request


   if request.method == "POST":
      retval_list = []
      index = 0
      if year_request:
         prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
         defval_year = year_request
         for record in  prev_record:
            if record.reading_date.__contains__(str(year_request)):
               retval_list.append(record)
               index = index + 1

         #for record that has been updated/posted on this new System
         if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(defval_year)).exists():
            new_record =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(defval_year))
   

   newrecord = []
   for n in range(current_date.year, 2017, -1):
      if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(n)).exists():
         new_record1 =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(n))
         newrecord.append(new_record1)
   for n in range(2011, 2009, -1):
      if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(n)).exists():
         new_record1 =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(n))
         newrecord.append(new_record1)

         
   return render(request,template,{"year_list":year_list,"retval":retval_list,
                                    "consumer":consumer,"ErrorMessagePass":ErrorMessagePass,"context":context,
                                     "PaidStatus":PaidStatus,"ReqParams":ReqParams,"defval_year":defval_year,
                                     "oldcon":oldconsumer,"account":account,"accountrecord":accountrecord,
                                     "new_record":new_record, "index":index,"commulative_bill":commulative_bill,
                                     "newrecord":newrecord })
                                    


def UnpaidMonth(id,year):
   month_list = []
   record = None
   if usage_record.objects.filter(pk = id + "-" + year).exists():
      record = usage_record.objects.get(pk = id + "-" + year)
      #we check unpaid or unsettled month
      if record.totalbill_jan != 0:
         if  record.totalbill_jan > record.paidamt_jan:
            month_list.append(1)
         else:
            pass
      if record.totalbill_feb != 0:
         if  record.totalbill_feb > record.paidamt_feb:
            month_list.append(2)
         else:
            pass
      if record.totalbill_mar != 0:
         if  record.totalbill_mar > record.paidamt_mar:
            month_list.append(3)
         else:
            pass
      if record.totalbill_apr != 0:
         if  record.totalbill_apr > record.paidamt_apr:
            month_list.append(4)
         else:
            pass
      if record.totalbill_may != 0:
         if  record.totalbill_may > record.paidamt_may:
            month_list.append(5)
         else:
            pass
      if record.totalbill_jun != 0:
         if  record.totalbill_jun > record.paidamt_jun:
            month_list.append(6)
         else:
            pass
      if record.totalbill_jul != 0:
         if  record.totalbill_jul > record.paidamt_jul:
            month_list.append(7)
         else:
            pass
      if record.totalbill_aug != 0:
         if  record.totalbill_aug > record.paidamt_aug:
            month_list.append(8)
         else:
            pass
      if record.totalbill_sept != 0:
         if  record.totalbill_sept > record.paidamt_sept:
            month_list.append(9)
         else:
            pass
      if record.totalbill_oct != 0:
         if  record.totalbill_oct > record.paidamt_oct:
            month_list.append(10)
         else:
            pass
      if record.totalbill_nov != 0:
         if  record.totalbill_nov > record.paidamt_nov:
            month_list.append(11)
         else:
            pass
      if record.totalbill_dec != 0:
         if  record.totalbill_dec > record.paidamt_dec:
            month_list.append(12)
         else:
            pass

   return month_list

def search_payment_history(request):
   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession:
      if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/search(payment_history).html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   context = {}
   context[ReqParams.userid] =  request.session.get(ReqParams.userid)
   context[ReqParams.name] = request.session.get(ReqParams.name)
   context[ReqParams.DashBoard_url] = request.session.get(ReqParams.DashBoard_url)
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)

   payments = payment_history.objects.all()
   getall = request.POST.get("get_all")
   date_from = request.POST.get("date_from")
   date_to = request.POST.get("date_to")
   retval = None

   if request.method == "POST":
      if getall:
         retval = payment_history.objects.all()
         context["report_type"] = ""
         return render(request,"html/payment_history(report).html",{"context":context,"retval":retval,})

      if date_from != None and date_to != None:
         if date_from >= date_to:
            pass
         else:
            retval = []
            context["report_type"] =  "From " + date_from + " to " + date_to
            for x in payments:
               if str(x.date) >= date_from and str(x.date) <= date_to:
                  retval.append(x)
            return render(request,"html/payment_history(report).html",{"context":context,"retval":retval,})

   return render(request,template,{"context":context})

def view_all_payment(request):
   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession:
      if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/payment_history(report).html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   retval = payment_history.objects.all()

   return render(request,"html/payment_history(report).html",{"retval":retval})
