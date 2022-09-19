from myApp.DataTransfer import prev_reading
from .models import *
from django.shortcuts import render
from django.shortcuts import redirect
from .models import consumers_info,getTotalBill
from django.template import Context
from datetime import date, datetime
from .BillingDB import *
from django.template.loader import get_template, render_to_string
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
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




def create_year_record():

   all_accounts = account_info.objects.all()
   new_usage_record = usage_record()
   current_date = date.today()

   for each_account in all_accounts:
      idstr = each_account.accountinfoid + "-" + str(current_date.year)
      isExist = usage_record.objects.filter(accountid = idstr).exists()
      print("error")
      if isExist == False:
         consumer = consumers_info.objects.get(pk = each_account.consumerid)
         print("check")
         #set a new record
         new_usage_record.accountid = idstr
         new_usage_record.year = current_date.year
         new_usage_record.rateid = each_account.rateid
         new_usage_record.commulative_bill = each_account.commulative_bill
         new_usage_record.accountinfoid = each_account.accountinfoid
         new_usage_record.consumerid = consumer
         new_usage_record.save()




def AutoCreate_NewRecord():
   current_date = date.today()
   month = current_date.month
   accounts = account_info.objects.all()
   prevyear = str(current_date.year - 1)
   yearly_record = Year_Report()
   brgy_record = barangay_report()
   barangay_list = zip(ReqParams.barangay_list,ReqParams.barangay_val)
   # we get the last year record particularly the december records
   record = usage_record.objects.filter(year = current_date.year).exists()
   if month == 1 and record == False: #Create record every january
      #Create Year Record
      yearly_record.year = current_date.year
      yearly_record.save()

      #Create account new Account record
      create_year_record()

      #create barangay record
      for brgyname,barangay_val in barangay_list:
         brgy_record.barangay_val = barangay_val + "-" + str(current_date.year)
         brgy_record.barangay_name = brgyname
         brgy_record.year = current_date.year
         brgy_record.save()



def view_consumerUsage(request,id):
   template = ""
   sessionval = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/consumer_usage.payment.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   account = account_info()
   usage = usage_record()
   current_date = date.today()
   context = []
   usage_list = []
   account_list = []
   getID = account_info.objects.get(accountinfoid = id)
   account_list.append(getID)

   idstr = id + "-" + str(current_date.year)
   pkstr = usage_record.objects.get(accountid = idstr)
   usage_list.append(pkstr)

   context = zip(usage_list,account_list,ReqParams.month_name)

   return render(request,template,{'context':context,"getID":getID})



def getCurrentReading( list ):
    max = list[ 0 ]
    for a in list:
        if a > max:
            max = a
    return max


#driver to get bill and etc
def getTotalBills(request):
   year = str(date.today().year)
   all_bill = getTotalBill.objects.all()
   all_accounts = account_info.objects.all()
   all_consumer = OldCosumerInfo.objects.all()
   new_consumer = consumers_info()
   new_record = usage_record()
   account = account_info()
   totalbill = 0
   accstr = ""

   #set the accountinfoid base on our format
   for consumer in all_consumer:
      # accstr = ""
      # new_consumer.installcount = 1 #we set installcount into 1
      # new_consumer.firstname = consumer.firstname
      # new_consumer.middlename = consumer.middlename
      # new_consumer.lastname = consumer.lastname
      # new_consumer.homeaddress = consumer.address
      #
      # #we create the applicantid base on last id used and barangay codes
      # consumerid_len = 10
      # keybasis = Primarykey_Basis.objects.get(pk = "consumerid")
      # lastid = keybasis.lastid_used
      # lastid_len = len(str(lastid + 1))
      # len_zeros = consumerid_len - lastid_len
      #
      # while len_zeros != 0:
      #    accstr += "0"
      #    len_zeros -= 1
      #
      # accstr += str(lastid + 1) #new consumerid
      # new_consumer.consumerid = accstr
      # new_consumer.oldconsumerid = consumer.con_id
      # keybasis.lastid_used =  lastid + 1
      #
      # #we set the new Accountinfo
      # if len(str(new_consumer.installcount)) < 2:
      #    withzero = "0"
      # else:
      #    withzero = ""
      #
      # account.accountinfoid = accstr + "-" + withzero + str(new_consumer.installcount)#we set account
      # account.firstname = consumer.firstname
      # account.middlename = consumer.middlename
      # account.lastname = consumer.lastname
      # account.address = consumer.address
      # account.rateid = consumer.con_category
      # account.meternumber = consumer.meternumber
      # account.consumerid = new_consumer #Foreign Key

      #we get the previous bill using con_id
      this_consumer = consumers_info.objects.get(oldconsumerid = consumer.con_id)
      this_id = this_consumer.consumerid + "-0" + str(this_consumer.installcount)
      account = account_info.objects.get(pk = this_id)
      acc = consumer.con_id
      getID = getTotalBill.objects.filter(con_id = acc)
      totalbill = 0
      reading_list = [0]

      for bill in getID:
         #we get the bill base on their PAID flag
         # PAID = 1, Not PAID = 0
         if bill.paid == "0":
            totalbill  += bill.currentdue

         #we get all readings
         reading_list.append(bill.current_reading)

      #we get the largest reading. The greatest reading obviously the latest reading
      latest_reading = getCurrentReading(reading_list)
      account.initial_meter_reading = latest_reading #we set the latest reading as initial meter reading


      new_record.accountid = account.accountinfoid + "-" + year #PK Value
      new_record.accountinfoid = account.accountinfoid
      new_record.commulative_bill = totalbill
      new_record.consumerid = new_consumer
      new_record.rateid = account.rateid
      new_record.accountinfoid = account.accountinfoid
      #We save
      new_record.save()
      # new_consumer.save()
      # account.save()
      # keybasis.save()

      #yearly record


   #rates
   residential = rates()
   commercial = rates()
   #set rate for residential
   residential.rateid = "1"
   residential.minimumreading = 20
   residential.rateafterminimum = 3
   residential.minimumreading_charge = 25
   residential.ratepenalty = 0.2
   residential.ratepenaltyfrequency = 3 #months
   residential.paymentchedday = "None"

   commercial.rateid = "2"
   commercial.minimumreading = 20
   commercial.rateafterminimum = 4
   commercial.minimumreading_charge = 30
   commercial.ratepenalty = 0.2
   commercial.ratepenaltyfrequency = 3 #months
   commercial.paymentchedday = "None"

   commercial.save()
   residential.save()

   #revenue code
   revenue = revenuecode()
   revenue.id = "1"
   revenue.save()


   return render(request,"test.html")



def Usage_Report(request):

   #rendering page
   template = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL):

         template = "html/usage_report.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")
  
   year_request = request.POST.get(ReqParams.year)
   brgycode = request.POST.get(ReqParams.barangay)


   current_date = date.today()

   #default value(year)
   current_date = date.today()
   defval_year = str(current_date.year)

   current_year = current_date.year
   allyear = []
   defval_year = str(current_year)

   report = Year_Report.objects.get(pk = current_date.year)
   if year_request != None:
      defval_year = year_request
      if Year_Report.objects.filter(pk = year_request).exists():
          report = Year_Report.objects.get(pk = year_request)
      else:
          report = None


   # #year dropdown value
   # allyear = Year_Report.objects.all()

   #year to choose,from year 2010 until today
   while current_year >= 2018:
      allyear.append(current_year)
      current_year = current_year - 1
   current_year = 2011
   while current_year >= 2010:
      allyear.append(current_year)
      current_year = current_year - 1


   brgy_report = barangay_report.objects.all()
   brgy_due = []
   brgy_paid = []
   brgy_usage = []
   totalbrgy_usage = 0
   totaldue = 0
   totalpaid = 0
   context = {
      "userid":request.session.get(ReqParams.userid),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "name":request.session.get(ReqParams.name)
   }

   #usage per baranggay
   year_brgy = 0
   if year_request != None:
      year_brgy = year_request
   else:
      year_brgy = current_date.year

   for brgy in brgy_report:
      totaldue = 0
      totalpaid = 0
      totalbrgy_usage = 0

      if brgy.year == int(year_brgy):
         totaldue = brgy.total_due_ytd
         totalpaid = brgy.total_paid_ytd
         totalbrgy_usage = brgy.total_usage
         brgy_usage.append(totalbrgy_usage)
         brgy_due.append(totaldue)
         brgy_paid.append(totalpaid)

   #get monthly report in in Every Barangay
   #default value(brgycode)
   anao_record = None
   cagsing_record = None
   calabawan_record = None
   cambagte_record = None
   campisong_record = None
   cañorong_record = None
   guiwanon_record = None
   looc_record = None
   malatbo_record = None
   mangaco_record = None
   palanas_record = None
   poblacion_record = None
   salamanca_record = None
   sanroque_record = None

   if barangay_report.objects.filter(pk = "1-" + str(year_brgy)).exists():
      anao_record = barangay_report.objects.get(pk = "1-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "2-" + str(year_brgy)).exists():
      cagsing_record = barangay_report.objects.get(pk = "2-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "3-" + str(year_brgy)).exists():
      calabawan_record = barangay_report.objects.get(pk = "3-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "4-" + str(year_brgy)).exists():
      cambagte_record = barangay_report.objects.get(pk = "4-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "5-" + str(year_brgy)).exists():
      campisong_record = barangay_report.objects.get(pk = "5-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "6-" + str(year_brgy)).exists():
      cañorong_record = barangay_report.objects.get(pk = "6-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "7-" + str(year_brgy)).exists():
      guiwanon_record = barangay_report.objects.get(pk = "7-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "8-" + str(year_brgy)).exists():
      looc_record = barangay_report.objects.get(pk = "8-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "9-" + str(year_brgy)).exists():
      malatbo_record = barangay_report.objects.get(pk = "9-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "10-" + str(year_brgy)).exists():
      mangaco_record = barangay_report.objects.get(pk = "10-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "11-" + str(year_brgy)).exists():
      palanas_record = barangay_report.objects.get(pk = "11-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "12-" + str(year_brgy)).exists():
      poblacion_record = barangay_report.objects.get(pk = "12-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "13-" + str(year_brgy)).exists():
      salamanca_record = barangay_report.objects.get(pk = "13-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "14-" + str(year_brgy)).exists():
      sanroque_record = barangay_report.objects.get(pk = "14-" + str(year_brgy))



   return render(request,template,{"report":report,"brgy_due":brgy_due,"brgy_paid":brgy_paid,
                                    "context":context,"brgy_report":brgy_report,
                                    "brgy_usage":brgy_usage,"allyear":allyear,"ReqParams":ReqParams,
                                    "defval":defval_year,
                                    "brgycode":brgycode,
                                    "brgy":brgy,
                                    "anao_record":anao_record,"cagsing_record":cagsing_record,"calabawan_record":calabawan_record,"campisong_record":campisong_record,"cañorong_record":cañorong_record,"cambagte_record":cambagte_record,
                                    "guiwanon_record":guiwanon_record,"looc_record":looc_record,"malatbo_record":malatbo_record,"mangaco_record":mangaco_record,
                                    "palanas_record":palanas_record,"poblacion_record":poblacion_record,"salamanca_record":salamanca_record,"sanroque_record":sanroque_record})

def Barangay_Monthly_Report(request):
   #rendering page
   template = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL):

         template = "html/barangay_monthly_report.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   year_request = request.POST.get(ReqParams.year)
   brgycode = request.POST.get(ReqParams.barangay)


   current_date = date.today()

   #default value(year)
   current_date = date.today()
   defval_year = str(current_date.year)

   current_year = current_date.year
   allyear = []
   defval_year = str(current_year)

   report = Year_Report.objects.get(pk = current_date.year)
   if year_request != None:
      defval_year = year_request
      if Year_Report.objects.filter(pk = year_request).exists():
          report = Year_Report.objects.get(pk = year_request)
      else:
          report = None


   # #year dropdown value
   # allyear = Year_Report.objects.all()

   #year to choose,from year 2010 until today
   while current_year >= 2018:
      allyear.append(current_year)
      current_year = current_year - 1
   current_year = 2011
   while current_year >= 2010:
      allyear.append(current_year)
      current_year = current_year - 1


   brgy_report = barangay_report.objects.all()
   brgy_due = []
   brgy_paid = []
   brgy_usage = []
   brgy_rate = []
   totalbrgy_usage = 0
   totaldue = 0
   totalpaid = 0
   rate = 0
   context = {
      "userid":request.session.get(ReqParams.userid),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "name":request.session.get(ReqParams.name)
   }

   #usage per baranggay
   year_brgy = 0
   if year_request != None:
      year_brgy = year_request
   else:
      year_brgy = current_date.year

   for brgy in brgy_report:
      totaldue = 0
      totalpaid = 0
      totalbrgy_usage = 0
      rate = 0

      if brgy.year == int(year_brgy):
         totaldue = brgy.total_due_ytd
         totalpaid = brgy.total_paid_ytd
         totalbrgy_usage = brgy.total_usage
         brgy_usage.append(totalbrgy_usage)
         brgy_due.append(totaldue)
         brgy_paid.append(totalpaid)

   #get monthly report in in Every Barangay
   #default value(brgycode)
   anao_record = None
   cagsing_record = None
   calabawan_record = None
   cambagte_record = None
   campisong_record = None
   cañorong_record = None
   guiwanon_record = None
   looc_record = None
   malatbo_record = None
   mangaco_record = None
   palanas_record = None
   poblacion_record = None
   salamanca_record = None
   sanroque_record = None

   if barangay_report.objects.filter(pk = "1-" + str(year_brgy)).exists():
      anao_record = barangay_report.objects.get(pk = "1-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "2-" + str(year_brgy)).exists():
      cagsing_record = barangay_report.objects.get(pk = "2-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "3-" + str(year_brgy)).exists():
      calabawan_record = barangay_report.objects.get(pk = "3-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "4-" + str(year_brgy)).exists():
      cambagte_record = barangay_report.objects.get(pk = "4-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "5-" + str(year_brgy)).exists():
      campisong_record = barangay_report.objects.get(pk = "5-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "6-" + str(year_brgy)).exists():
      cañorong_record = barangay_report.objects.get(pk = "6-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "7-" + str(year_brgy)).exists():
      guiwanon_record = barangay_report.objects.get(pk = "7-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "8-" + str(year_brgy)).exists():
      looc_record = barangay_report.objects.get(pk = "8-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "9-" + str(year_brgy)).exists():
      malatbo_record = barangay_report.objects.get(pk = "9-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "10-" + str(year_brgy)).exists():
      mangaco_record = barangay_report.objects.get(pk = "10-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "11-" + str(year_brgy)).exists():
      palanas_record = barangay_report.objects.get(pk = "11-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "12-" + str(year_brgy)).exists():
      poblacion_record = barangay_report.objects.get(pk = "12-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "13-" + str(year_brgy)).exists():
      salamanca_record = barangay_report.objects.get(pk = "13-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "14-" + str(year_brgy)).exists():
      sanroque_record = barangay_report.objects.get(pk = "14-" + str(year_brgy))
   


   return render(request,template,{"report":report,"brgy_due":brgy_due,"brgy_paid":brgy_paid,"rate":rate,
                                    "context":context,"brgy_report":brgy_report,
                                    "brgy_usage":brgy_usage,"allyear":allyear,"ReqParams":ReqParams,
                                    "defval":defval_year,
                                    "brgycode":brgycode,
                                    "brgy":brgy,
                                    "anao_record":anao_record,"cagsing_record":cagsing_record,"calabawan_record":calabawan_record,"campisong_record":campisong_record,"cañorong_record":cañorong_record,"cambagte_record":cambagte_record,
                                    "guiwanon_record":guiwanon_record,"looc_record":looc_record,"malatbo_record":malatbo_record,"mangaco_record":mangaco_record,
                                    "palanas_record":palanas_record,"poblacion_record":poblacion_record,"salamanca_record":salamanca_record,"sanroque_record":sanroque_record})

def Barangay_Monthly_Record(request,year,id):
   #rendering page
   template = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL):

         template = "html/barangay_monthly_record.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")


   brgycode = id

   current_date = date.today()

   #default value(year)
   current_date = date.today()
   defval = str(year)

   current_year = current_date.year
   allyear = []
   defval = str(current_year)

   #default value(year)
   current_date = date.today()
   year_brgy = year
   defval = year_brgy
   if request.method == 'POST':
      year_request = request.POST.get(ReqParams.year)
      defval = year_request
      year_brgy = year_request
      if Year_Report.objects.filter(pk = year_request).exists():
         report = Year_Report.objects.get(pk = year_request)
      else:
         report = None
   else:
      report = Year_Report.objects.get(pk = defval)

   # #year dropdown value
   # allyear = Year_Report.objects.all()

   #year to choose,from year 2010 until today
   while current_year >= 2018:
      allyear.append(current_year)
      current_year = current_year - 1
   current_year = 2011
   while current_year >= 2010:
      allyear.append(current_year)
      current_year = current_year - 1


   brgy_report = barangay_report.objects.all()
   brgy_due = []
   brgy_paid = []
   brgy_usage = []
   totalbrgy_usage = 0
   totaldue = 0
   totalpaid = 0
   context = {
      "userid":request.session.get(ReqParams.userid),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "name":request.session.get(ReqParams.name)
   }


   for brgy in brgy_report:
      totaldue = 0
      totalpaid = 0
      totalbrgy_usage = 0

      if brgy.year == int(year_brgy):
         totaldue = brgy.total_due_ytd
         totalpaid = brgy.total_paid_ytd
         totalbrgy_usage = brgy.total_usage
         brgy_usage.append(totalbrgy_usage)
         brgy_due.append(totaldue)
         brgy_paid.append(totalpaid)

   #get monthly report in in Every Barangay
   #default value(brgycode)
   anao_record = None
   cagsing_record = None
   calabawan_record = None
   cambagte_record = None
   campisong_record = None
   cañorong_record = None
   guiwanon_record = None
   looc_record = None
   malatbo_record = None
   mangaco_record = None
   palanas_record = None
   poblacion_record = None
   salamanca_record = None
   sanroque_record = None

   if barangay_report.objects.filter(pk = "1-" + str(year_brgy)).exists():
      anao_record = barangay_report.objects.get(pk = "1-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "2-" + str(year_brgy)).exists():
      cagsing_record = barangay_report.objects.get(pk = "2-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "3-" + str(year_brgy)).exists():
      calabawan_record = barangay_report.objects.get(pk = "3-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "4-" + str(year_brgy)).exists():
      cambagte_record = barangay_report.objects.get(pk = "4-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "5-" + str(year_brgy)).exists():
      campisong_record = barangay_report.objects.get(pk = "5-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "6-" + str(year_brgy)).exists():
      cañorong_record = barangay_report.objects.get(pk = "6-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "7-" + str(year_brgy)).exists():
      guiwanon_record = barangay_report.objects.get(pk = "7-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "8-" + str(year_brgy)).exists():
      looc_record = barangay_report.objects.get(pk = "8-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "9-" + str(year_brgy)).exists():
      malatbo_record = barangay_report.objects.get(pk = "9-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "10-" + str(year_brgy)).exists():
      mangaco_record = barangay_report.objects.get(pk = "10-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "11-" + str(year_brgy)).exists():
      palanas_record = barangay_report.objects.get(pk = "11-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "12-" + str(year_brgy)).exists():
      poblacion_record = barangay_report.objects.get(pk = "12-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "13-" + str(year_brgy)).exists():
      salamanca_record = barangay_report.objects.get(pk = "13-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "14-" + str(year_brgy)).exists():
      sanroque_record = barangay_report.objects.get(pk = "14-" + str(year_brgy))
   barangay_name = ReqParams.barangay_list
   if brgycode != None or brgycode != "" or brgycode != '':
      defval_brgycode = brgycode
      defval_brgyname = barangay_name[int(defval_brgycode) - 1]
      if brgycode == "1":
         brgy = anao_record
      if brgycode == "2":
         brgy = cagsing_record
      if brgycode == "3":
         brgy = calabawan_record
      if brgycode == "4":
         brgy = cambagte_record
      if brgycode == "5":
         brgy = campisong_record
      if brgycode == "6":
         brgy = cañorong_record
      if brgycode == "7":
         brgy = guiwanon_record
      if brgycode == "8":
         brgy = looc_record
      if brgycode == "9":
         brgy = malatbo_record
      if brgycode == "10":
         brgy = mangaco_record
      if brgycode == "11":
         brgy = palanas_record
      if brgycode == "12":
         brgy = poblacion_record
      if brgycode == "13":
         brgy = salamanca_record
      if brgycode == "14":
         brgy = sanroque_record
   else:
      defval_brgycode = "14"
      brgycode = "14"
      defval_brgyname = barangay_name[int(defval_brgycode) - 1]

   records = []
   for n in range(current_date.year, 2017, -1):
      new_record1 =  barangay_report.objects.get(pk = (brgycode + "-" + str(n)))
      records.append(new_record1)
   for n in range(2011, 2009, -1):
      new_record1 =  barangay_report.objects.get(pk = (brgycode + "-" + str(n)))
      records.append(new_record1)
   

   return render(request,template,{"report":report,"brgy_due":brgy_due,"brgy_paid":brgy_paid,
                                    "context":context,"brgy_report":brgy_report,
                                    "brgy_usage":brgy_usage,"allyear":allyear,"ReqParams":ReqParams,
                                    "defval":defval,
                                    "brgycode":brgycode,
                                    "brgy":brgy,"records":records,
                                    "defval_brgyname":defval_brgyname,
                                    "anao_record":anao_record,"cagsing_record":cagsing_record,"calabawan_record":calabawan_record,"campisong_record":campisong_record,"cañorong_record":cañorong_record,"cambagte_record":cambagte_record,
                                    "guiwanon_record":guiwanon_record,"looc_record":looc_record,"malatbo_record":malatbo_record,"mangaco_record":mangaco_record,
                                    "palanas_record":palanas_record,"poblacion_record":poblacion_record,"salamanca_record":salamanca_record,"sanroque_record":sanroque_record})




def Revenue_Report(request):
   #rendering page
   template = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL):

         template = "html/revenue_report.html"
      else:
         template = "html/unavailable.html"
   else:
      LogInSession

   year_request = request.POST.get(ReqParams.year)
   brgy_code = request.POST.get(ReqParams.barangay)
   current_date = date.today()

   current_date = date.today()

   #default value(year)
   current_date = date.today()
   defval_year = str(current_date.year)

   current_year = current_date.year
   allyear = []
   defval_year = str(current_year)

   report = Year_Report.objects.get(pk = current_date.year)
   if year_request != None:
      defval_year = year_request
      if Year_Report.objects.filter(pk = year_request).exists():
          report = Year_Report.objects.get(pk = year_request)
      else:
          report = None


   # #year dropdown value
   # allyear = Year_Report.objects.all()

   #year to choose,from year 2010 until today
   while current_year >= 2018:
      allyear.append(current_year)
      current_year = current_year - 1
   current_year = 2011
   while current_year >= 2010:
      allyear.append(current_year)
      current_year = current_year - 1



   brgy_report = barangay_report.objects.all()
   brgy_due = []
   brgy_paid = []
   brgy_usage = []
   totalbrgy_usage = 0
   totaldue = 0
   totalpaid = 0
   context = {
      "userid":request.session.get(ReqParams.userid),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "name":request.session.get(ReqParams.name)
   }
   context["UserType"] = request.session.get(ReqParams.LOGIN_SESSION)
   #monthly revenue and usage per barangay
   year_brgy = 0
   if year_request != None:
      year_brgy = year_request
   else:
      year_brgy = current_date.year

   for brgy in brgy_report:
      totaldue = 0
      totalpaid = 0
      totalbrgy_usage = 0

      if brgy.year == int(year_brgy):
         totaldue = brgy.total_due_ytd
         totalpaid = brgy.total_paid_ytd
         totalbrgy_usage = brgy.total_usage
         brgy_usage.append(totalbrgy_usage)
         brgy_due.append(totaldue)
         brgy_paid.append(totalpaid)

   #get monthly report in in Every Barangay
   #default value(brgycode)
   anao_record = None
   cagsing_record = None
   calabawan_record = None
   cambagte_record = None
   campisong_record = None
   cañorong_record = None
   guiwanon_record = None
   looc_record = None
   malatbo_record = None
   mangaco_record = None
   palanas_record = None
   poblacion_record = None
   salamanca_record = None
   sanroque_record = None

   if barangay_report.objects.filter(pk = "1-" + str(year_brgy)).exists():
      anao_record = barangay_report.objects.get(pk = "1-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "2-" + str(year_brgy)).exists():
      cagsing_record = barangay_report.objects.get(pk = "2-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "3-" + str(year_brgy)).exists():
      calabawan_record = barangay_report.objects.get(pk = "3-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "4-" + str(year_brgy)).exists():
      cambagte_record = barangay_report.objects.get(pk = "4-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "5-" + str(year_brgy)).exists():
      campisong_record = barangay_report.objects.get(pk = "5-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "6-" + str(year_brgy)).exists():
      cañorong_record = barangay_report.objects.get(pk = "6-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "7-" + str(year_brgy)).exists():
      guiwanon_record = barangay_report.objects.get(pk = "7-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "8-" + str(year_brgy)).exists():
      looc_record = barangay_report.objects.get(pk = "8-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "9-" + str(year_brgy)).exists():
      malatbo_record = barangay_report.objects.get(pk = "9-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "10-" + str(year_brgy)).exists():
      mangaco_record = barangay_report.objects.get(pk = "10-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "11-" + str(year_brgy)).exists():
      palanas_record = barangay_report.objects.get(pk = "11-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "12-" + str(year_brgy)).exists():
      poblacion_record = barangay_report.objects.get(pk = "12-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "13-" + str(year_brgy)).exists():
      salamanca_record = barangay_report.objects.get(pk = "13-" + str(year_brgy))

   if barangay_report.objects.filter(pk = "14-" + str(year_brgy)).exists():
      sanroque_record = barangay_report.objects.get(pk = "14-" + str(year_brgy))

   #unuse next line of code
   #monthname = ReqParams.barangay_list
   #defval_brgycode = "12"
   #defval_brgyname = monthname[int(defval_brgycode) - 1]
   #brgycode = barangay_report.objects.get(pk = defval_brgycode + "-" + defval_year)
   #if brgy_code != None:
      #brgycode = barangay_report.objects.get(pk = brgy_code + "-" + year_request)
      #defval_brgycode = brgy_code
      #defval_brgyname = monthname[int(defval_brgycode) - 1]


   return render(request,template,{"report":report,"brgy_due":brgy_due,"brgy_paid":brgy_paid,
                                    "context":context,"brgy_report":brgy_report,"allyear":allyear,
                                    "ReqParams":ReqParams,"defval":defval_year,
                                    "brgy_code":brgy_code,
                                    "anao_record":anao_record,"cagsing_record":cagsing_record,"calabawan_record":calabawan_record,"campisong_record":campisong_record,"cañorong_record":cañorong_record,"cambagte_record":cambagte_record,
                                    "guiwanon_record":guiwanon_record,"looc_record":looc_record,"malatbo_record":malatbo_record,"mangaco_record":mangaco_record,
                                    "palanas_record":palanas_record,"poblacion_record":poblacion_record,"salamanca_record":salamanca_record,"sanroque_record":sanroque_record})






def pending_bills(request):
   #rendering page
   template = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL) or LogInSession.__contains__(ReqParams.MANAGER_LOGIN_VAL):

         template = "html/pending_bills.html"
      else:
         template = "html/unavailable.html"
   else:
      return redirect("/")

   current_date = date.today()

   all_account = account_info.objects.all()
   bills = []
   credentials = []
   retvalobj = []

   context = {
      "name":request.session.get(ReqParams.name),
      "UserType":request.session.get(ReqParams.LOGIN_SESSION),
      "userid":request.session.get(ReqParams.userid)
   }

   #for account in all_account:
     # accountidstr = account.accountinfoid + "-" + str(current_date.year)
      #if usage_record.objects.filter(pk = accountidstr).exists():
         #record = usage_record.objects.order_by('commulative_bill')
         #if record.commulative_bill != 0:
            #bills.append(record)
            #names.append(account)

   order_by_bill = usage_record.objects.filter(year = current_date.year)#descending order
   totalbill = 0

   for record in order_by_bill:
      if record.commulative_bill != 0:
         totalbill += record.commulative_bill
         if account_info.objects.filter(pk = record.accountinfoid).exists():
            account = account_info.objects.get(accountinfoid = record.accountinfoid)
            bills.append(record)
            credentials.append(account)

   formatted_float = "Php:{:,.2f}".format(totalbill)
   print(formatted_float)
   context["total_str"] = "Total Uncollected: " + str(formatted_float)
   context["pendingbills"] = formatted_float


   retvalobj = zip(bills,credentials)
   retvalobj1 = zip(bills,credentials)

   

   return render(request,template,{"retval":retvalobj,"retval1":retvalobj1,"context":context})




def OldSystemRecordDisplay(request,id):

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
   template = ""
   LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
   if LogInSession:
      if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/OldSystemRecordDisplay.html"
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
   retvall_list = []
   defval_year = str(current_year)
   prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
   readingdate = usage_record.objects.get(pk = accountidstr)
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

   # #year to choose,from year 2010 until today
   # while current_year >= 2018:
   #    year_list.append(current_year)
   #    current_year = current_year - 1

   # current_year = 2011
   # while current_year >= 2010:
   #    year_list.append(current_year)
   #    current_year = current_year - 1

   account = account_info.objects.get(pk = id)
   accountrecord = payment_history.objects.filter(accountinfoid = id)
   for record in accountrecord:
      #for dropdown values(year)
      if record.year not in year_list:
         year_list.append(record.year)
      #default display, current year
      if record.year == current_date.year:
         retvall_list.append(record)

   # accountrecord = payment_history.objects.filter(accountinfoid = id)
   # if year_request:
   #    accountrecord = payment_history.objects.filter(accountinfoid = id)
   #    for record in accountrecord:

   #       #default display, current year
   #       if record.year == int(year_request):
   #          retvall_list.append(record)
   #    defval_year = year_request


   # if request.method == "POST":
   #    retval_list = []
   #    index = 0
   #    if year_request:
   #       prev_record = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
   #       defval_year = year_request
   #       for record in  prev_record:
   #          if record.reading_date.__contains__(str(year_request)):
   #             retval_list.append(record)
   #             index = index + 1

   #       #for record that has been updated/posted on this new System
   #       if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(defval_year)).exists():
   #          new_record =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(defval_year))
   

   newrecord = []
   for n in range(current_date.year, 2009, -1):
      if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(n)).exists():
         new_record1 =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(n))
         newrecord.append(new_record1)
   for n in range(2011, 2009, -1):
      if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(n)).exists():
         new_record1 =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(n))
         newrecord.append(new_record1)


         
   return render(request,template,{"year_list":year_list,"retval":retval_list,"retvall":retvall_list,
                                    "consumer":consumer,"ErrorMessagePass":ErrorMessagePass,"context":context,
                                     "PaidStatus":PaidStatus,"ReqParams":ReqParams,"defval_year":defval_year,
                                     "oldcon":oldconsumer,"account":account,"accountrecord":accountrecord,
                                     "new_record":new_record, "index":index,"commulative_bill":commulative_bill,
                                     "newrecord":newrecord,"account":getID,"usage":pkstr,"context":context,
                                    "defval":defval,"month":month.getMonth,"monthval":month,
                                    "params":ReqParams,"monthval":month,"defval":defval_year,"year_list":year_list,})

   



def getUsageRevenue(request):#we get only the record for 2021
   context = {}
   current_date = date.today()
   current_year = current_date.year
   year_record = None
   brgy_record = None
   year_report = Year_Report()
   current_year = current_date.year

   while current_year >= 2018:
      record = Year_Report.objects.filter(pk = str(current_year)).exists()
      if record == False:
         year_report.year = current_year
         year_report.save()
   current_year = 2011
   while current_year >= 2010:
      record = Year_Report.objects.filter(pk = str(current_year)).exists()
      if record == False:
         year_report.year = current_year
         year_report.save()


      year_record = Year_Report.objects.get(pk = current_year)
      #bills and usage for january
      record_jan = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-02").exists():
         record_jan = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-02")
         for record in record_jan:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_january += record.currentdue

            year_record.total_due_january += record.currentdue
            year_record.total_due_ytd += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_january +=  record.consumption
            year_record.save()

      #bills and usage for february
      record_feb = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-03").exists():
         record_feb = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-03")
         for record in record_feb:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_february += record.currentdue

            year_record.total_due_february += record.currentdue
            year_record.total_due_ytd += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_february +=  record.consumption
            year_record.save()

      #bills and usage for March
      record_mar = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-04").exists():
         record_mar = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-04")
         for record in record_mar:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_march += record.currentdue

            year_record.total_due_march += record.currentdue
            year_record.total_due_ytd += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_march +=  record.consumption
            year_record.save()

      #bills and usage for April
      record_apr = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-05").exists():
         record_apr = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-05")
         for record in record_apr:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_april += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_april += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_april +=  record.consumption
            year_record.save()

      #bills and usage for May
      record_may = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-06").exists():
         record_may = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-06")
         for record in record_may:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_may += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_may += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_may +=  record.consumption
            year_record.save()

      #bills and usage for June
      record_jun = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-07").exists():
         record_jun = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-07")
         for record in record_jun:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_june = record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_june += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_june +=  record.consumption
            year_record.save()

      #bills and usage for July
      record_jul = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-08").exists():
         record_jul = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-08")
         for record in record_jul:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_july += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_july += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_july +=  record.consumption
            year_record.save()

      #bills and usage for August
      record_aug = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-09").exists():
         record_aug = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-09")
         for record in record_aug:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_august += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_august += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_august +=  record.consumption
            year_record.save()

      #bills and usage for September
      record_sept = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-10").exists():
         record_sept = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-10")
         for record in record_sept:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_september += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_september += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_september +=  record.consumption
            year_record.save()

      #bills and usage for October
      record_oct = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-11").exists():
         record_oct = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-11")
         for record in record_oct:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_october += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_october += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_october +=  record.consumption
            year_record.save()

      #bills and usage for November
      record_mov = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-12").exists():
         record_nov = getTotalBill.objects.filter(reading_date__contains = str(current_year) + "-12")
         for record in record_nov:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_november += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_november += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_november +=  record.consumption
            year_record.save()

      #bills and usage for November
      record_mov = None
      if getTotalBill.objects.filter(reading_date__contains = str(current_year + 1) + "-01").exists():
         record_dec = getTotalBill.objects.filter(reading_date__contains = str(current_year + 1) + "-01")
         for record in record_dec:
            if record.paid == "1":
               year_record.total_paid_ytd += record.currentdue
               year_record.total_paid_december += record.currentdue

            year_record.total_due_ytd += record.currentdue
            year_record.total_due_december += record.currentdue
            year_record.total_usage += record.consumption
            year_record.usage_december +=  record.consumption
            year_record.save()

      #decrement
      current_year = current_year - 1

   return render(request,"test.html")

def accountrecord(request):
   accounts = account_info.objects.all()
   current_date = date.today()


   #create year


   year_list = []
   year_list.append(2020)
   year_list.append(2021)
   this_year = 2010
   while this_year <= current_date.year:
      billmonth = 0
      if current_date.month == 1:
         billmonth = 12
      else:
         billmonth = current_date.month - 1

      current_year = this_year
      for account in accounts:
         record = usage_record()
         consumer = consumers_info.objects.get(pk = account.consumerid)
         #record_check = usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_year)).exists()
         #if record_check == False:
            #record.accountid =  account.accountinfoid + "-" + str(current_year)
            #record.accountinfoid = account.accountinfoid
            #record.rateid = account.rateid
            #record.consumerid = consumer
            #record.year = current_year
            #record.save()

         if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_year)).exists():
            pass
         else:
            new_record = usage_record()
            new_record.accountid = account.accountinfoid + "-" + str(current_year) #PK Value
            new_record.accountinfoid = account.accountinfoid
            new_record.commulative_bill = 0
            new_record.consumerid = consumer
            new_record.rateid = account.rateid
            new_record.accountinfoid = account.accountinfoid
            new_record.year = int(current_year)
            #We save
            new_record.save()

         account_record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_year))
         account_record.commulative_bill = 0
         account_record.save()

         prev_record = None
         #adding the previous balance
         #if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(current_year - 1)):
            #prev_record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_year - 1))
            #account_record.commulative_bill += prev_record.commulative_bill
            #account_record.save()

         #bills and usage for january
         record_jan = None
         consumer = consumers_info.objects.get(pk = account.consumerid)
         oldcon = getTotalBill.objects.filter(con_id = consumer.oldconsumerid)
         # if billmonth == 1:
         for con in oldcon:
            reading = con.reading_date
            commulative_bill = 0
            paid_amount = 0
            if reading.__contains__(str(current_year) + "-02"):
               account_record.reading_jan = con.current_reading
               account_record.reading_date_jan = con.reading_date
               account_record.usage_jan =  con.consumption
               if account_record.usage_jan < 20 and account_record.usage_jan > 0:
                  account_record.bill_jan = 25
                  account_record.totalbill_jan = 25
                  
               else:
                  account_record.bill_jan = con.currentdue
                  account_record.totalbill_jan = con.currentdue

               commulative_bill += account_record.totalbill_jan
               if con.paid == "1":
                  account_record.paidamt_jan = commulative_bill

            if reading.__contains__(str(current_year) + "-03"):
               account_record.reading_feb = con.current_reading
               account_record.reading_date_feb = con.reading_date
               account_record.usage_feb =  con.consumption
               if account_record.usage_feb < 20 and account_record.usage_feb > 0:
                  account_record.bill_feb = 25
                  account_record.totalbill_feb = 25
               else:
                  account_record.bill_feb = con.currentdue
                  account_record.totalbill_feb = con.currentdue

               commulative_bill += account_record.totalbill_feb
               if con.paid == "1":
                  account_record.paidamt_feb = commulative_bill

            if reading.__contains__(str(current_year) + "-04"):
               account_record.reading_mar = con.current_reading
               account_record.reading_date_mar = con.reading_date
               account_record.usage_mar =  con.consumption
               if account_record.usage_mar < 20 and account_record.usage_mar > 0:
                  account_record.bill_mar = 25
                  account_record.totalbill_mar = 25
               else:
                  account_record.bill_mar = con.currentdue
                  account_record.totalbill_mar = con.currentdue

               commulative_bill += account_record.totalbill_mar
               if con.paid == "1":
                  account_record.paidamt_mar = commulative_bill

            if reading.__contains__(str(current_year) + "-05"):
               account_record.reading_apr = con.current_reading
               account_record.reading_date_apr = con.reading_date
               account_record.usage_apr =  con.consumption
               if account_record.usage_apr < 20 and account_record.usage_apr > 0:
                  account_record.bill_apr = 25
                  account_record.totalbill_apr = 25
               else:
                  account_record.bill_apr = con.currentdue
                  account_record.totalbill_apr = con.currentdue

               commulative_bill += account_record.totalbill_apr
               if con.paid == "1":
                  account_record.paidamt_apr = commulative_bill

            if reading.__contains__(str(current_year) + "-06"):
               account_record.reading_may = con.current_reading
               account_record.reading_date_may = con.reading_date
               account_record.usage_may =  con.consumption
               if account_record.usage_may < 20 and account_record.usage_may > 0:
                  account_record.bill_may = 25
                  account_record.totalbill_may = 25
               else:
                  account_record.bill_may = con.currentdue
                  account_record.totalbill_may = con.currentdue

               commulative_bill += account_record.totalbill_may
               if con.paid == "1":
                  account_record.paidamt_may = commulative_bill

            if reading.__contains__(str(current_year) + "-07"):
               account_record.reading_jun = con.current_reading
               account_record.reading_date_jun = con.reading_date
               account_record.usage_jun =  con.consumption
               if account_record.usage_jun < 20 and account_record.usage_jun > 0:
                  account_record.bill_jun = 25
                  account_record.totalbill_jun = 25
               else:
                  account_record.bill_jun = con.currentdue
                  account_record.totalbill_jun = con.currentdue

               commulative_bill += account_record.totalbill_jun
               if con.paid == "1":
                  account_record.paidamt_june = commulative_bill

            if reading.__contains__(str(current_year) + "-08"):
               account_record.reading_jul = con.current_reading
               account_record.reading_date_jul = con.reading_date
               account_record.usage_jul =  con.consumption
               if account_record.usage_jul < 20 and account_record.usage_jul > 0:
                  account_record.bill_jul = 25
                  account_record.totalbill_jul = 25
               else:
                  account_record.bill_jul = con.currentdue
                  account_record.totalbill_jul = con.currentdue

               commulative_bill += account_record.totalbill_jul
               if con.paid == "1":
                  account_record.paidamt_jul = commulative_bill

            if reading.__contains__(str(current_year) + "-09"):
               account_record.reading_aug = con.current_reading
               account_record.reading_date_aug = con.reading_date
               account_record.usage_aug =  con.consumption
               if account_record.usage_aug < 20 and account_record.usage_aug > 0:
                  account_record.bill_aug = 25
                  account_record.totalbill_aug = 25
               else:
                  account_record.bill_aug = con.currentdue
                  account_record.totalbill_aug = con.currentdue

               commulative_bill += account_record.totalbill_aug
               if con.paid == "1":
                  account_record.paidamt_aug = commulative_bill

            if reading.__contains__(str(current_year) + "-10"):
               account_record.reading_sept = con.current_reading
               account_record.reading_date_sept = con.reading_date
               account_record.usage_sept =  con.consumption
               if account_record.usage_sept < 20 and account_record.usage_sept > 0:
                  account_record.bill_sept = 25
                  account_record.totalbill_sept = 25
               else:
                  account_record.bill_sept = con.currentdue
                  account_record.totalbill_sept = con.currentdue

               commulative_bill += account_record.totalbill_sept
               if con.paid == "1":
                  account_record.paidamt_sept = commulative_bill

            if reading.__contains__(str(current_year) + "-11"):
               account_record.reading_oct = con.current_reading
               account_record.reading_date_oct = con.reading_date
               account_record.usage_oct =  con.consumption
               if account_record.usage_oct < 20 and account_record.usage_oct > 0:
                  account_record.bill_oct = 25
                  account_record.totalbill_oct = 25
               else:
                  account_record.bill_oct = con.currentdue
                  account_record.totalbill_oct = con.currentdue

               commulative_bill += account_record.totalbill_oct
               if con.paid == "1":
                  account_record.paidamt_oct = commulative_bill

            if reading.__contains__(str(current_year) + "-12"):
               account_record.reading_nov = con.current_reading
               account_record.reading_date_nov = con.reading_date
               account_record.usage_nov =  con.consumption
               if account_record.usage_nov < 20 and account_record.usage_nov > 0:
                  account_record.bill_nov = 25
                  account_record.totalbill_nov = 25
               else:
                  account_record.bill_nov = con.currentdue
                  account_record.totalbill_nov = con.currentdue

               commulative_bill += account_record.totalbill_nov
               if con.paid == "1":
                  account_record.paidamt_nov = commulative_bill

            if reading.__contains__(str(current_year + 1) + "-01"):
               account_record.reading_dec = con.current_reading
               account_record.reading_date_dec = con.reading_date
               account_record.usage_dec =  con.consumption
               if account_record.usage_dec < 20 and account_record.usage_dec > 0:
                  account_record.bill_dec = 25
                  account_record.totalbill_dec = 25
               else:
                  account_record.bill_dec = con.currentdue
                  account_record.totalbill_dec = con.currentdue

               commulative_bill += account_record.totalbill_dec
               if con.paid == "1":
                  account_record.paidamt_dec = commulative_bill
               

               # account_record.save()
            if con.paid != "1":
               account_record.commulative_bill += commulative_bill
            account_record.save()          

         prev_year = int(current_year) - 1         
         if usage_record.objects.filter(accountinfoid = account.accountinfoid,year = prev_year).exists():
            prev_record = usage_record.objects.get(accountinfoid = account.accountinfoid,year = prev_year)     
            account_record.commulative_bill += prev_record.commulative_bill
            account_record.save()  
      this_year = this_year + 1







   return render(request,"test.html")

def meternumber(request):
   return render(request,"test.html")

def testyear(request):
   all_account = usage_record.objects.all()
   for account in all_account:
      this_year = ""
      this_len = len(account.accountid) -4
      this_id = account.accountid
      while len(this_year) != 4:
         this_year += this_id[this_len]
         this_len = this_len + 1
      account.year = int(this_year)
      account.save()   
   return render(request,"test.html")
