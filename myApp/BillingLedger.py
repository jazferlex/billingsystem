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
from operator import attrgetter
from django.db import models
from collections import OrderedDict
 
# billingledger_list = []
# BillingLedger_dict = {}
 
BILL_TX_CODE = 1
PAYMENT_TX_CODE = 2
 
def GenerateBillingLedger(request,id, billingledgerdict):
    template = ""
    LogInSession = request.session.get(ReqParams.LOGIN_SESSION)
    if LogInSession:
        if LogInSession.__contains__(ReqParams.TELLER_LOGIN_VAL) or LogInSession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/billing-ledger.html"
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
            retvall_list.append(record)
   
 
    newrecord = []
    for n in range(current_date.year, 2017, -1):
        if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(n)).exists():
            new_record1 =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(n))
            newrecord.append(new_record1)
 
            #for january
            if len(new_record1.reading_date_jan) > 0:
                ledgerjan = BillingLedger()
                ledgerjan.trans_datetime = new_record1.reading_date_jan
                ManualDateConverter(ledgerjan.trans_datetime)
                ledgerjan.meternumber = ""
                ledgerjan.account_number = new_record1.accountinfoid
                ledgerjan.prev_reading = 0
                ledgerjan.cur_reading = new_record1.reading_jan
                ledgerjan.cu_meter = new_record1.usage_jan
                ledgerjan.amt_billed= new_record1.totalbill_jan
                ledgerjan.amt_paid = ""
                ledgerjan.processed_by = ""
                ledgerjan.or_number = ""
                ledgerjan.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerjan.record_flag = BILL_TX_CODE
 
                # dateobj = datetime.strptime(ledgerjan.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%m-%d-%Y")
                # billingledgerdict[dateobjstr] = ledgerjan
                billingledgerdict[ledgerjan.trans_datetime] = ledgerjan
 
            #for february
            if len(new_record1.reading_date_feb) > 0:
                ledgerfeb = BillingLedger()
                #try:
                #    ledgerfeb.trans_datetime = datetime.strptime(new_record1.reading_date_feb, '%d-%m-%Y')
                #except ValueError:
                #    print('result of February Value Error')
               
                ledgerfeb.trans_datetime = new_record1.reading_date_feb
                ledgerfeb.meternumber = ""
                ledgerfeb.account_number = new_record1.accountinfoid
                ledgerfeb.prev_reading = 0
                ledgerfeb.cur_reading = new_record1.reading_feb
                ledgerfeb.cu_meter = new_record1.usage_feb
                ledgerfeb.amt_billed= new_record1.totalbill_feb
                ledgerfeb.amt_paid = " "
                ledgerfeb.processed_by = ""
                ledgerfeb.or_number = ""
                ledgerfeb.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerfeb.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerfeb.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%m-%d-%Y")
                # billingledgerdict[dateobjstr]= ledgerfeb
                billingledgerdict[ledgerfeb.trans_datetime] = ledgerfeb
 
            #for march
            if len(new_record1.reading_date_mar) > 0:
                ledgermar = BillingLedger()
                #ledgermar.trans_datetime = datetime.strptime(new_record1.reading_date_mar, '%d-%m-%Y')
                ledgermar.trans_datetime = new_record1.reading_date_mar
                ledgermar.meternumber = ""
                ledgermar.account_number = new_record1.accountinfoid
                ledgermar.prev_reading = 0
                ledgermar.cur_reading = new_record1.reading_mar
                ledgermar.cu_meter = new_record1.usage_mar
                ledgermar.amt_billed= new_record1.totalbill_mar
                ledgermar.amt_paid = " "
                ledgermar.processed_by = ""
                ledgermar.or_number = ""
                ledgermar.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgermar.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgermar.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgermar
                billingledgerdict[ledgermar.trans_datetime] = ledgermar
 
            #for april
            if len(new_record1.reading_date_apr) > 0:
                ledgerapr = BillingLedger()
                #ledgerapr.trans_datetime = datetime.strptime(new_record1.reading_date_apr, '%d-%m-%Y')
                ledgerapr.trans_datetime = new_record1.reading_date_apr
                ledgerapr.meternumber = ""
                ledgerapr.account_number = new_record1.accountinfoid
                ledgerapr.prev_reading = 0
                ledgerapr.cur_reading = new_record1.reading_apr
                ledgerapr.cu_meter = new_record1.usage_apr
                ledgerapr.amt_billed= new_record1.totalbill_apr
                ledgerapr.amt_paid = " "
                ledgerapr.processed_by = ""
                ledgerapr.or_number = ""
                ledgerapr.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerapr.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerapr.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerapr
 
                billingledgerdict[ledgerapr.trans_datetime] = ledgerapr
 
            #for may
            if len(new_record1.reading_date_may) > 0:
                ledgermay = BillingLedger()
                #ledgermay.trans_datetime = datetime.strptime(new_record1.reading_date_may, '%d-%m-%Y')
                ledgermay.trans_datetime = new_record1.reading_date_may
                ledgermay.meternumber = ""
                ledgermay.account_number = new_record1.accountinfoid
                ledgermay.prev_reading = 0
                ledgermay.cur_reading = new_record1.reading_may
                ledgermay.cu_meter = new_record1.usage_may
                ledgermay.amt_billed= new_record1.totalbill_may
                ledgermay.amt_paid = " "
                ledgermay.processed_by = ""
                ledgermay.or_number = ""
                ledgermay.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgermay.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgermay.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgermay
 
                billingledgerdict[ledgermay.trans_datetime] = ledgermay
 
            #for june
            if len(new_record1.reading_date_jun) > 0:
                ledgerjun = BillingLedger()
                #ledgerjun.trans_datetime = datetime.strptime(new_record1.reading_date_jun, '%d-%m-%Y')
                ledgerjun.trans_datetime = new_record1.reading_date_jun
                ledgerjun.meternumber = ""
                ledgerjun.account_number = new_record1.accountinfoid
                ledgerjun.prev_reading = 0
                ledgerjun.cur_reading = new_record1.reading_jun
                ledgerjun.cu_meter = new_record1.usage_jun
                ledgerjun.amt_billed= new_record1.totalbill_jun
                ledgerjun.amt_paid = " "
                ledgerjun.processed_by = ""
                ledgerjun.or_number = ""
                ledgerjun.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerjun.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerjun.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerjun
 
                billingledgerdict[ledgerjun.trans_datetime] = ledgerjun
 
            #for july
            if len(new_record1.reading_date_jul) > 0:
                ledgerjul = BillingLedger()
                #ledgerjul.trans_datetime = datetime.strptime(new_record1.reading_date_jul, '%d-%m-%Y')
                ledgerjul.trans_datetime = new_record1.reading_date_jul
                ledgerjul.meternumber = ""
                ledgerjul.account_number = new_record1.accountinfoid
                ledgerjul.prev_reading = 0
                ledgerjul.cur_reading = new_record1.reading_jul
                ledgerjul.cu_meter = new_record1.usage_jul
                ledgerjul.amt_billed= new_record1.totalbill_jul
                ledgerjul.amt_paid = " "
                ledgerjul.processed_by = ""
                ledgerjul.or_number = ""
                ledgerjul.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerjul.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerjul.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerjul
 
                billingledgerdict[ledgerjul.trans_datetime] = ledgerjul
 
            #for august
            if len(new_record1.reading_date_aug) > 0:
                ledgeraug = BillingLedger()
                #ledgeraug.trans_datetime = datetime.strptime(new_record1.reading_date_aug, '%d-%m-%Y')
                ledgeraug.trans_datetime = new_record1.reading_date_aug
                ledgeraug.meternumber = ""
                ledgeraug.account_number = new_record1.accountinfoid
                ledgeraug.prev_reading = 0
                ledgeraug.cur_reading = new_record1.reading_aug
                ledgeraug.cu_meter = new_record1.usage_aug
                ledgeraug.amt_billed= new_record1.totalbill_aug
                ledgeraug.amt_paid = " "
                ledgeraug.processed_by = ""
                ledgeraug.or_number = ""
                ledgeraug.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgeraug.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgeraug.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgeraug
 
                billingledgerdict[ledgeraug.trans_datetime] = ledgeraug
 
            #for September
            if len(new_record1.reading_date_sept) > 0:
                ledgersept = BillingLedger()
                #ledgersept.trans_datetime = datetime.strptime(new_record1.reading_date_sept, '%d-%m-%Y')
                ledgersept.trans_datetime = new_record1.reading_date_sept
                ledgersept.meternumber = ""
                ledgersept.account_number = new_record1.accountinfoid
                ledgersept.prev_reading = 0
                ledgersept.cur_reading = new_record1.reading_sept
                ledgersept.cu_meter = new_record1.usage_sept
                ledgersept.amt_billed= new_record1.totalbill_sept
                ledgersept.amt_paid = " "
                ledgersept.processed_by = ""
                ledgersept.or_number = ""
                ledgersept.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgersept.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgersept.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgersept
 
                billingledgerdict[ledgersept.trans_datetime] = ledgersept
 
            #for october
            if len(new_record1.reading_date_oct) > 0:
                ledgeroct = BillingLedger()
                #ledgeroct.trans_datetime = datetime.strptime(new_record1.reading_date_oct, '%d-%m-%Y')
                ledgeroct.trans_datetime = new_record1.reading_date_oct
                ledgeroct.meternumber = ""
                ledgeroct.meternumber = ""
                ledgeroct.account_number = new_record1.accountinfoid
                ledgeroct.prev_reading = 0
                ledgeroct.cur_reading = new_record1.reading_oct
                ledgeroct.cu_meter = new_record1.usage_oct
                ledgeroct.amt_billed= new_record1.totalbill_oct
                ledgeroct.amt_paid = " "
                ledgeroct.processed_by = ""
                ledgeroct.or_number = ""
                ledgeroct.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgeroct.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgeroct.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgeroct
 
                billingledgerdict[ledgeroct.trans_datetime] = ledgeroct
 
            #for November
            if len(new_record1.reading_date_nov) > 0:
                ledgernov = BillingLedger()
                #ledgernov.trans_datetime = datetime.strptime(new_record1.reading_date_nov, '%d-%m-%Y')
                ledgernov.trans_datetime = new_record1.reading_date_nov
                ledgernov.meternumber = ""
                ledgernov.account_number = new_record1.accountinfoid
                ledgernov.prev_reading = 0
                ledgernov.cur_reading = new_record1.reading_nov
                ledgernov.cu_meter = new_record1.usage_nov
                ledgernov.amt_billed= new_record1.totalbill_nov
                ledgernov.amt_paid = " "
                ledgernov.processed_by = ""
                ledgernov.or_number = ""
                ledgernov.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgernov.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgernov.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgernov
 
                billingledgerdict[ledgernov.trans_datetime] = ledgernov
 
            #for december
            if len(new_record1.reading_date_dec) > 0:
                ledgerdec = BillingLedger()
                #ledgerdec.trans_datetime = datetime.strptime(new_record1.reading_date_dec, '%d-%m-%Y')
                ledgerdec.trans_datetime = new_record1.reading_date_dec
                ledgerdec.meternumber = ""
                ledgerdec.account_number = new_record1.accountinfoid
                ledgerdec.prev_reading = 0
                ledgerdec.cur_reading = new_record1.reading_dec
                ledgerdec.cu_meter = new_record1.usage_dec
                ledgerdec.amt_billed= new_record1.totalbill_dec
                ledgerdec.amt_paid = " "
                ledgerdec.processed_by = ""
                ledgerdec.or_number = ""
                ledgerdec.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerdec.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerdec.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerdec
 
                billingledgerdict[ledgerdec.trans_datetime] = ledgerdec
 
 
    for n in range(2011, 2009, -1):
        if usage_record.objects.filter(pk = account.accountinfoid + "-" + str(n)).exists():
            new_record1 =  usage_record.objects.get(pk = account.accountinfoid + "-" + str(n))
            newrecord.append(new_record1)
 
           #for january
            if len(new_record1.reading_date_jan) > 0:
                ledgerjan = BillingLedger()
                #rint(new_record1.reading_date_jan)
                #try:
                #    ledgerjan.trans_datetime = datetime.strptime(new_record1.reading_date_jan, "%m-%d-%Y")
                #except ValueError:
                #    print('result of January Value Error')
                #print('2017 January')
                #print(ledgerjan.trans_datetime)
                ledgerjan.trans_datetime = new_record1.reading_date_jan
                # print('2017 January')
                # print(ledgerjan.trans_datetime)
                # print('Type of variable from DB')
                # print(type(new_record1.reading_date_jan))
                # print('Type of our var')
                # print(type(ledgerjan.trans_datetime))
                ledgerjan.meternumber = ""
                ledgerjan.account_number = new_record1.accountinfoid
                ledgerjan.prev_reading = 0
                ledgerjan.cur_reading = new_record1.reading_jan
                ledgerjan.cu_meter = new_record1.usage_jan
                ledgerjan.amt_billed= new_record1.totalbill_jan
                ledgerjan.amt_paid = " "
                ledgerjan.processed_by = ""
                ledgerjan.or_number = ""
                ledgerjan.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerjan.record_flag = BILL_TX_CODE
 
                # dateobj = datetime.strptime(ledgerjan.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%m-%d-%Y")
                # billingledgerdict[dateobjstr] = ledgerjan
                billingledgerdict[ledgerjan.trans_datetime] = ledgerjan
 
            #for february
            if len(new_record1.reading_date_feb) > 0:
                ledgerfeb = BillingLedger()
                #try:
                #    ledgerfeb.trans_datetime = datetime.strptime(new_record1.reading_date_feb, '%d-%m-%Y')
                #except ValueError:
                #    print('result of February Value Error')
               
                ledgerfeb.trans_datetime = new_record1.reading_date_feb
                print('2017 Februray')
                print(ledgerfeb.trans_datetime)
                print('Type of variable from DB')
                print(type(new_record1.reading_date_feb))
                print('Type of our var')
                print(type(ledgerfeb.trans_datetime))
                ledgerfeb.meternumber = ""
                ledgerfeb.account_number = new_record1.accountinfoid
                ledgerfeb.prev_reading = 0
                ledgerfeb.cur_reading = new_record1.reading_feb
                ledgerfeb.cu_meter = new_record1.usage_feb
                ledgerfeb.amt_billed= new_record1.totalbill_feb
                ledgerfeb.amt_paid = " "
                ledgerfeb.processed_by = ""
                ledgerfeb.or_number = ""
                ledgerfeb.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerfeb.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerfeb.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%m-%d-%Y")
                # billingledgerdict[dateobjstr]= ledgerfeb
                billingledgerdict[ledgerfeb.trans_datetime] = ledgerfeb
 
            #for march
            if len(new_record1.reading_date_mar) > 0:
                ledgermar = BillingLedger()
                #ledgermar.trans_datetime = datetime.strptime(new_record1.reading_date_mar, '%d-%m-%Y')
                ledgermar.trans_datetime = new_record1.reading_date_mar
                ledgermar.meternumber = ""
                ledgermar.account_number = new_record1.accountinfoid
                ledgermar.prev_reading = 0
                ledgermar.cur_reading = new_record1.reading_mar
                ledgermar.cu_meter = new_record1.usage_mar
                ledgermar.amt_billed= new_record1.totalbill_mar
                ledgermar.amt_paid = " "
                ledgermar.processed_by = ""
                ledgermar.or_number = ""
                ledgermar.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgermar.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgermar.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgermar
                billingledgerdict[ledgermar.trans_datetime] = ledgermar
 
            #for april
            if len(new_record1.reading_date_apr) > 0:
                ledgerapr = BillingLedger()
                #ledgerapr.trans_datetime = datetime.strptime(new_record1.reading_date_apr, '%d-%m-%Y')
                ledgerapr.trans_datetime = new_record1.reading_date_apr
                ledgerapr.meternumber = ""
                ledgerapr.account_number = new_record1.accountinfoid
                ledgerapr.prev_reading = 0
                ledgerapr.cur_reading = new_record1.reading_apr
                ledgerapr.cu_meter = new_record1.usage_apr
                ledgerapr.amt_billed= new_record1.totalbill_apr
                ledgerapr.amt_paid = " "
                ledgerapr.processed_by = ""
                ledgerapr.or_number = ""
                ledgerapr.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerapr.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerapr.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerapr
 
                billingledgerdict[ledgerapr.trans_datetime] = ledgerapr
 
            #for may
            if len(new_record1.reading_date_may) > 0:
                ledgermay = BillingLedger()
                #ledgermay.trans_datetime = datetime.strptime(new_record1.reading_date_may, '%d-%m-%Y')
                ledgermay.trans_datetime = new_record1.reading_date_may
                ledgermay.meternumber = ""
                ledgermay.account_number = new_record1.accountinfoid
                ledgermay.prev_reading = 0
                ledgermay.cur_reading = new_record1.reading_may
                ledgermay.cu_meter = new_record1.usage_may
                ledgermay.amt_billed= new_record1.totalbill_may
                ledgermay.amt_paid = " "
                ledgermay.processed_by = ""
                ledgermay.or_number = ""
                ledgermay.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgermay.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgermay.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgermay
 
                billingledgerdict[ledgermay.trans_datetime] = ledgermay
 
            #for june
            if len(new_record1.reading_date_jun) > 0:
                ledgerjun = BillingLedger()
                #ledgerjun.trans_datetime = datetime.strptime(new_record1.reading_date_jun, '%d-%m-%Y')
                ledgerjun.trans_datetime = new_record1.reading_date_jun
                ledgerjun.meternumber = ""
                ledgerjun.account_number = new_record1.accountinfoid
                ledgerjun.prev_reading = 0
                ledgerjun.cur_reading = new_record1.reading_jun
                ledgerjun.cu_meter = new_record1.usage_jun
                ledgerjun.amt_billed= new_record1.totalbill_jun
                ledgerjun.amt_paid = " "
                ledgerjun.processed_by = ""
                ledgerjun.or_number = ""
                ledgerjun.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerjun.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerjun.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerjun
 
                billingledgerdict[ledgerjun.trans_datetime] = ledgerjun
 
            #for july
            if len(new_record1.reading_date_jul) > 0:
                ledgerjul = BillingLedger()
                #ledgerjul.trans_datetime = datetime.strptime(new_record1.reading_date_jul, '%d-%m-%Y')
                ledgerjul.trans_datetime = new_record1.reading_date_jul
                ledgerjul.meternumber = ""
                ledgerjul.account_number = new_record1.accountinfoid
                ledgerjul.prev_reading = 0
                ledgerjul.cur_reading = new_record1.reading_jul
                ledgerjul.cu_meter = new_record1.usage_jul
                ledgerjul.amt_billed= new_record1.totalbill_jul
                ledgerjul.amt_paid = " "
                ledgerjul.processed_by = ""
                ledgerjul.or_number = ""
                ledgerjul.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerjul.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerjul.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerjul
 
                billingledgerdict[ledgerjul.trans_datetime] = ledgerjul
 
            #for august
            if len(new_record1.reading_date_aug) > 0:
                ledgeraug = BillingLedger()
                #ledgeraug.trans_datetime = datetime.strptime(new_record1.reading_date_aug, '%d-%m-%Y')
                ledgeraug.trans_datetime = new_record1.reading_date_aug
                ledgeraug.meternumber = ""
                ledgeraug.account_number = new_record1.accountinfoid
                ledgeraug.prev_reading = 0
                ledgeraug.cur_reading = new_record1.reading_aug
                ledgeraug.cu_meter = new_record1.usage_aug
                ledgeraug.amt_billed= new_record1.totalbill_aug
                ledgeraug.amt_paid = " "
                ledgeraug.processed_by = ""
                ledgeraug.or_number = ""
                ledgeraug.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgeraug.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgeraug.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgeraug
 
                billingledgerdict[ledgeraug.trans_datetime] = ledgeraug
 
            #for September
            if len(new_record1.reading_date_sept) > 0:
                ledgersept = BillingLedger()
                #ledgersept.trans_datetime = datetime.strptime(new_record1.reading_date_sept, '%d-%m-%Y')
                ledgersept.trans_datetime = new_record1.reading_date_sept
                ledgersept.meternumber = ""
                ledgersept.account_number = new_record1.accountinfoid
                ledgersept.prev_reading = 0
                ledgersept.cur_reading = new_record1.reading_sept
                ledgersept.cu_meter = new_record1.usage_sept
                ledgersept.amt_billed= new_record1.totalbill_sept
                ledgersept.amt_paid = " "
                ledgersept.processed_by = ""
                ledgersept.or_number = ""
                ledgersept.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgersept.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgersept.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgersept
 
                billingledgerdict[ledgersept.trans_datetime] = ledgersept
 
            #for october
            if len(new_record1.reading_date_oct) > 0:
                ledgeroct = BillingLedger()
                #ledgeroct.trans_datetime = datetime.strptime(new_record1.reading_date_oct, '%d-%m-%Y')
                ledgeroct.trans_datetime = new_record1.reading_date_oct
                ledgeroct.meternumber = ""
                ledgeroct.meternumber = ""
                ledgeroct.account_number = new_record1.accountinfoid
                ledgeroct.prev_reading = 0
                ledgeroct.cur_reading = new_record1.reading_oct
                ledgeroct.cu_meter = new_record1.usage_oct
                ledgeroct.amt_billed= new_record1.totalbill_oct
                ledgeroct.amt_paid = " "
                ledgeroct.processed_by = ""
                ledgeroct.or_number = ""
                ledgeroct.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgeroct.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgeroct.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgeroct
 
                billingledgerdict[ledgeroct.trans_datetime] = ledgeroct
 
            #for November
            if len(new_record1.reading_date_nov) > 0:
                ledgernov = BillingLedger()
                #ledgernov.trans_datetime = datetime.strptime(new_record1.reading_date_nov, '%d-%m-%Y')
                ledgernov.trans_datetime = new_record1.reading_date_nov
                ledgernov.meternumber = ""
                ledgernov.account_number = new_record1.accountinfoid
                ledgernov.prev_reading = 0
                ledgernov.cur_reading = new_record1.reading_nov
                ledgernov.cu_meter = new_record1.usage_nov
                ledgernov.amt_billed= new_record1.totalbill_nov
                ledgernov.amt_paid = " "
                ledgernov.processed_by = ""
                ledgernov.or_number = ""
                ledgernov.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgernov.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgernov.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgernov
 
                billingledgerdict[ledgernov.trans_datetime] = ledgernov
 
            #for december
            if len(new_record1.reading_date_dec) > 0:
                ledgerdec = BillingLedger()
                #ledgerdec.trans_datetime = datetime.strptime(new_record1.reading_date_dec, '%d-%m-%Y')
                ledgerdec.trans_datetime = new_record1.reading_date_dec
                ledgerdec.meternumber = ""
                ledgerdec.account_number = new_record1.accountinfoid
                ledgerdec.prev_reading = 0
                ledgerdec.cur_reading = new_record1.reading_dec
                ledgerdec.cu_meter = new_record1.usage_dec
                ledgerdec.amt_billed= new_record1.totalbill_dec
                ledgerdec.amt_paid = " "
                ledgerdec.processed_by = ""
                ledgerdec.or_number = ""
                ledgerdec.current_balance = 0.0
                # set to 1 if bill, 2 if payment
                ledgerdec.record_flag = BILL_TX_CODE
                # dateobj = datetime.strptime(ledgerdec.trans_datetime, "%Y-%d-%m")
                # dateobjstr = dateobj.strftime("%Y-%m-%d")
                # billingledgerdict[dateobjstr]= ledgerdec
 
                billingledgerdict[ledgerdec.trans_datetime] = ledgerdec
 
    # return render(request,template,{"year_list":year_list,"retval":retval_list,"retvall":retvall_list,
    #                                     "consumer":consumer,"ErrorMessagePass":ErrorMessagePass,"context":context,
    #                                     "PaidStatus":PaidStatus,"ReqParams":ReqParams,"defval_year":defval_year,
    #                                     "oldcon":oldconsumer,"account":account,"accountrecord":accountrecord,
    #                                     "new_record":new_record, "index":index,"commulative_bill":commulative_bill,
    #                                     "newrecord":newrecord })
 
 
def GenerateGeneralLedger(request,id):
 
    loginsession = request.session.get(ReqParams.LOGIN_SESSION)
    template = ""
    if loginsession:
        if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
            template = "html/billing-ledger.html"
        else:
            template = "html/unavailable.html"
    else:
        return redirect("/")
 
 
    index = 0
    current_date = date.today()
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
    readingdate = usage_record.objects.get(pk = accountidstr)
    for record in  prev_record:
        if record.reading_date.__contains__(str(defval_year)):
            retval_list.append(record)
            index = index + 1
    new_record = None
 
    BillingLedger_dict = {}
    LedgerOutput = []
 
    GenerateBillingLedger(request, id, BillingLedger_dict)
    GeneratePaymentsLedger(request,id, BillingLedger_dict)
 
    # billingledger_list.sort(key=lambda x: x.trans_datetime)
 
    # billingledger_list.sort(key=datetime.strptime(attrgetter('trans_datetime'), '%m/%d/%y %H:%M:%S'))
    # datetime.strptime(attrgetter('trans_datetime'), '%m/%d/%y %H:%M:%S')
    # billingledger_list.sort_values(by='trans_datetime')
 
    runningbalance = 0
    prevreading = 0
    start = True
 
    #sorteddict = sorted(BillingLedger_dict.items(), key = lambda x: datetime.strptime(x[0], '%Y-%m-%d'))
    #for ledgerkey in sorted(BillingLedger_dict.keys()):
    #for ledgerkey in sorteddict.keys():
    #display = "%s  %s"%(billledger.meternumber, billledger.account_number)
    print('Payment History')
    #print(display)
    sorteditems = OrderedDict(sorted(BillingLedger_dict.items()))
    for ledgerkey in sorteditems.keys():
        #billledger = BillingLedger_dict[ledgerkey]
 
        #runningbalance = billledger.adjustbalance(runningbalance)
        runningbalance = BillingLedger_dict[ledgerkey].adjustbalance(runningbalance)
        if start == False:
            #billledger.setprev_reading(prev_reading)
            BillingLedger_dict[ledgerkey].setprev_reading(prev_reading)
 
        #prev_reading = billledger.cur_reading
        if BillingLedger_dict[ledgerkey].record_flag == BILL_TX_CODE:
            #we update previous reading, no changes
            prev_reading = BillingLedger_dict[ledgerkey].cur_reading
       
        #append to our output list
        LedgerOutput.append(BillingLedger_dict[ledgerkey])
       
        #for display only
        billledger = BillingLedger_dict[ledgerkey]
        start = False
        display = "%s  %s  %s  %s  %s   %s  %s   %s  %s"%(billledger.trans_datetime, billledger.prev_reading, billledger.cur_reading, billledger.cu_meter,
                                                          billledger.amt_billed, billledger.amt_paid, billledger.processed_by, billledger.or_number,
                                                          billledger.current_balance)
 
        print(display)
 
 
        # print(ledger.account_number)
        # print(ledger.cu_meter)
        # print(ledger.or_number)
        # print(ledger.processed_by)
        # print(ledger.trans_datetime)
 
 
    return render(request,template,{ "ledger":LedgerOutput,"account":account, "consumer":consumer,"oldcon":oldconsumer} )
 
meternumber = ""
 
def GeneratePaymentsLedger(request,id, billingledgerdict):
 
   loginsession = request.session.get(ReqParams.LOGIN_SESSION)
   template = ""
   if loginsession:
      if loginsession.__contains__(ReqParams.TELLER_LOGIN_VAL) or loginsession.__contains__(ReqParams.SUPERVISOR_LOGIN_VAL):
         template = "html/billing-ledger.html"
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
 
   
   accountrecord = payment_history.objects.filter(accountinfoid = id)
   for record in accountrecord:
 
    #create a billing ledger object
    # set the item
    ledger = BillingLedger()
    #we must convert to string since this is a DateTimeField object
    ledger.trans_datetime = (record.date).strftime("%m-%d-%Y")
    ledger.meternumber = record.meternumber
    #we copy meter number
    meternumber = ledger.meternumber
    ledger.account_number = record.accountinfoid
    ledger.prev_reading = " "
    ledger.cur_reading = " "
    ledger.cu_meter = " "
    ledger.amt_billed= " "
    ledger.amt_paid = record.amount
    ledger.processed_by = record.postedby
    ledger.or_number = record.or_number
    ledger.current_balance = 0
    # set to 1 if bill, 2 if payment
    ledger.record_flag = PAYMENT_TX_CODE  
 
    # billingledger_list.append(ledger)
 
    #we convert to date object
    dateobj = datetime.strptime(ledger.trans_datetime, "%m-%d-%Y")
    dateobjstr = dateobj.strftime("%Y-%m-%d")
    #billingledgerdict[ledger.trans_datetime] = ledger
    billingledgerdict[dateobjstr] = ledger
 
    #return render(request,template,{"retval":retval_list,"account":account,"accoutrecord":accountrecord,
    #                                "context":context,"defval":defval_year,"year_list":year_list,
    #                                "ReqParams":ReqParams,"accountrecord":accountrecord})
 
def ManualDateConverter(datestr):
    print('ManualDateConverter')
    print(datestr)
    if len(datestr) > 0:
        words = datestr.split('-')
        print(words)
 
class BillingLedger:
   trans_datetime = ""
   meternumber = ""
   account_number = ""
   prev_reading = " "
   cur_reading = " "
   cu_meter = " "
   amt_billed = " "
   amt_paid = " "
   processed_by = ""
   or_number = ""
   current_balance = 0.0
   # set to 1 if bill, 2 if payment
   record_flag = BILL_TX_CODE
 
 
   def adjustbalance(self, runningbalance):
    if(self.record_flag == BILL_TX_CODE):
        self.current_balance = runningbalance + self.amt_billed
        # print('hellobilled')
    elif(self.record_flag == PAYMENT_TX_CODE):
        self.current_balance = runningbalance - self.amt_paid
        # print('hellopaid')
    return self.current_balance
   
 
   def setprev_reading(self, previousreading):
    if self.record_flag == BILL_TX_CODE:
        self.prev_reading = previousreading
       
 
 
 

