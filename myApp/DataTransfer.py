import csv
from .models import *
from .BillingDB import *
from django.http import HttpResponse


def CSVBill(request):

    bill = getTotalBill()
    with open("myApp/static/website/RevenueUsage.csv", "r") as csv_file:

        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for lines in csv_reader:
            print(lines)
            bill.bill_id = lines['Bill ID']
            bill.con_id = lines['Con ID']
            bill.currentdue = float(lines['Current Due'])
            bill.rateid = lines['Bill Type']
            bill.paid = lines['Paid Flag']
            bill.current_reading = float(lines['Current Reading'])
            bill.previous_reading = float(lines['Previous Reading'])
            bill.reading_date = lines['Reading Date']
            bill.consumption = float(lines['Consumption'])
            bill.save()



    return render(request,"test.html")


def getCurrentReading( list ):
    max = list[ 0 ]
    for a in list:
        if a > max:
            max = a
    return max


def CSV_Consumer(request):

    consumer = consumers_info()
    account = account_info()
    keybasis = Primarykey_Basis.objects.get(pk = "consumerid")
    barangay_name = ReqParams.barangay_list
    barangay_val =  ReqParams.barangay_val

    with open("myApp/static/website/ConsumerCsv.csv", "r") as csv_file:

        csv_reader = csv.DictReader(csv_file, delimiter=',')

        for lines in csv_reader:
            print(lines)
            consumer.firstname = lines['First Name']
            consumer.middlename = lines['Middle Name']
            consumer.lastname = lines['Last Name']
            consumer.barangay = lines['Barangay']
            if lines['Barangay'] in barangay_val:
                consumer.homeaddress = barangay_name[int(lines['Barangay']) - 1] + ",Ginatilan,Cebu"
            else:
                consumer.homeaddress = ""

            consumer.birthday = ""
            consumer.installcount = 1
            consumer.sitio = ""
            consumer.mobilenumber = ""
            consumer.mobilenumber2 = ""
            consumer.emailaddress = ""

            #new consumer id format
            consumerid_len = 10
            lastid = keybasis.lastid_used
            lastid_len = len(str(lastid + 1))
            len_zeros = consumerid_len - lastid_len
            accstr = ""

            while len_zeros != 0:
                accstr += "0"
                len_zeros -= 1

            accstr += str(lastid + 1) #new consumerid
            consumer.consumerid = accstr
            consumer.oldconsumerid = lines['Con ID']
            consumer.save()

            #we set the new Accountinfo
            if len(str(consumer.installcount)) < 2:
                withzero = "0"
            else:
                withzero = ""

            account.accountinfoid = accstr + "-" + withzero + str(consumer.installcount)#we set account
            account.firstname = consumer.firstname
            account.middlename = consumer.middlename
            account.lastname = consumer.lastname
            account.barangay = consumer.barangay
            account.address = consumer.homeaddress
            account.rateid = lines['Rate ID']
            meternum = lines['Meter Number'].replace("MN-","")
            account.meternumber = meternum
            account.initial_meter_reading = -1
            account.consumerid = consumer #Foreign Key

            #we get the previous bill using con_id
            acc = lines['Con ID']
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
            account.initial_meter_reading = -1
            keybasis.lastid_used =  lastid + 1
            keybasis.save()
            account.save()
            consumer.save()

    return render(request,"test.html")



def barangayRecord(request):
    accounts = account_info.objects.all()
    current_date = date.today()


    #barangay report
    brgyreport = barangay_report()
    barangay_list = zip(ReqParams.barangay_list,ReqParams.barangay_val)
    year_list = []
    year_list.append("2010")
    year_list.append("2011")
    year_list.append("2018")
    year_list.append("2019")
    year_list.append("2020")
    year_list.append("2021")
    

    for x in year_list:
        print(x)

    i = 0
    yearlen = 6
    for x in year_list:
        current_year = x
        brgyreport = barangay_report()
        barangay_list = zip(ReqParams.barangay_list,ReqParams.barangay_val)
        for brgyname,barangay_val in barangay_list:
            brgyreport.barangay_val = barangay_val + "-" + str(current_year)
            brgyreport.barangay_name = brgyname
            brgyreport.year = current_year
            brgyreport.save()
        
        
    for x in year_list:
        current_year = x
        for acc in accounts:
            brgy_record = None
            account = account_info.objects.get(pk = acc.accountinfoid)
            accountrecord = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_year))
            if barangay_report.objects.filter(pk = account.barangay + "-" + str(current_year)).exists():
                brgy_record = barangay_report.objects.get(pk = account.barangay + "-" + str(current_year))
                #January
                #usage
                brgy_record.total_usage += accountrecord.usage_jan
                brgy_record.usage_january += accountrecord.usage_jan
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_jan
                brgy_record.total_paid_ytd += accountrecord.paidamt_jan
                brgy_record.total_due_january += accountrecord.totalbill_jan
                brgy_record.total_paid_january += accountrecord.paidamt_jan

                #February
                #usage
                brgy_record.total_usage += accountrecord.usage_feb
                brgy_record.usage_february += accountrecord.usage_feb
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_feb
                brgy_record.total_paid_ytd += accountrecord.paidamt_feb
                brgy_record.total_due_february += accountrecord.totalbill_feb
                brgy_record.total_paid_february += accountrecord.paidamt_feb

                #March
                #usage
                brgy_record.total_usage += accountrecord.usage_mar
                brgy_record.usage_march += accountrecord.usage_mar
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_mar
                brgy_record.total_paid_ytd += accountrecord.paidamt_mar
                brgy_record.total_due_march += accountrecord.totalbill_mar
                brgy_record.total_paid_march += accountrecord.paidamt_mar

                #April
                #usage
                brgy_record.total_usage += accountrecord.usage_apr
                brgy_record.usage_april += accountrecord.usage_apr
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_apr
                brgy_record.total_paid_ytd += accountrecord.paidamt_apr
                brgy_record.total_due_april += accountrecord.totalbill_apr
                brgy_record.total_paid_april += accountrecord.paidamt_apr

                #May
                #usage
                brgy_record.total_usage += accountrecord.usage_may
                brgy_record.usage_may += accountrecord.usage_may
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_may
                brgy_record.total_paid_ytd += accountrecord.paidamt_may
                brgy_record.total_due_may += accountrecord.totalbill_may
                brgy_record.total_paid_may += accountrecord.paidamt_may

                #June
                #usage
                brgy_record.total_usage += accountrecord.usage_jun
                brgy_record.usage_june += accountrecord.usage_jun
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_jun
                brgy_record.total_paid_ytd += accountrecord.paidamt_jun
                brgy_record.total_due_june += accountrecord.totalbill_jun
                brgy_record.total_paid_june += accountrecord.paidamt_jun

                #July
                #usage
                brgy_record.total_usage += accountrecord.usage_jul
                brgy_record.usage_july += accountrecord.usage_jul
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_jul
                brgy_record.total_paid_ytd += accountrecord.paidamt_jul
                brgy_record.total_due_july += accountrecord.totalbill_jul
                brgy_record.total_paid_july += accountrecord.paidamt_jul

                #August
                #usage
                brgy_record.total_usage += accountrecord.usage_aug
                brgy_record.usage_august += accountrecord.usage_aug
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_aug
                brgy_record.total_paid_ytd += accountrecord.paidamt_aug
                brgy_record.total_due_august += accountrecord.totalbill_aug
                brgy_record.total_paid_august += accountrecord.paidamt_aug

                #September
                #usage
                brgy_record.total_usage += accountrecord.usage_sept
                brgy_record.usage_september += accountrecord.usage_sept
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_sept
                brgy_record.total_paid_ytd += accountrecord.paidamt_sept
                brgy_record.total_due_september += accountrecord.totalbill_sept
                brgy_record.total_paid_september += accountrecord.paidamt_sept

                #October
                #usage
                brgy_record.total_usage += accountrecord.usage_oct
                brgy_record.usage_october += accountrecord.usage_oct
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_oct
                brgy_record.total_paid_ytd += accountrecord.paidamt_oct
                brgy_record.total_due_october += accountrecord.totalbill_oct
                brgy_record.total_paid_october += accountrecord.paidamt_oct

                #November
                #usage
                brgy_record.total_usage += accountrecord.usage_nov
                brgy_record.usage_november += accountrecord.usage_nov
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_nov
                brgy_record.total_paid_ytd += accountrecord.paidamt_nov
                brgy_record.total_due_november += accountrecord.totalbill_nov
                brgy_record.total_paid_november += accountrecord.paidamt_nov

                #December
                #usage
                brgy_record.total_usage += accountrecord.usage_dec
                brgy_record.usage_december += accountrecord.usage_dec
                #revenue
                brgy_record.total_due_ytd += accountrecord.totalbill_dec
                brgy_record.total_paid_ytd += accountrecord.paidamt_dec
                brgy_record.total_due_december += accountrecord.totalbill_dec
                brgy_record.total_paid_december += accountrecord.paidamt_dec

                brgy_record.save()

        


    return render(request,"test.html")


def prev_reading(request):
    accounts = account_info.objects.all()
    current_date = date.today()
    latest_bill = current_date.month - 1 #month  

    for account in accounts:
        acc = account.accountinfoid + "-" + str(current_date.year)
        accountrecord = usage_record.objects.get(pk = acc)
        if latest_bill == 1:
            accountrecord.previous_reading = accountrecord.reading_jan
        elif latest_bill == 2:
            accountrecord.previous_reading = accountrecord.reading_feb
        elif latest_bill == 3:
            accountrecord.previous_reading = accountrecord.reading_mar
        elif latest_bill == 4:
            accountrecord.previous_reading = accountrecord.reading_apr
        elif latest_bill == 5:
            accountrecord.previous_reading = accountrecord.reading_may
        elif latest_bill == 6:
            accountrecord.previous_reading = accountrecord.reading_jun   
        elif latest_bill == 7:
            accountrecord.previous_reading = accountrecord.reading_jul
        elif latest_bill == 8:
            accountrecord.previous_reading = accountrecord.reading_aug
        elif latest_bill == 9:
            accountrecord.previous_reading = accountrecord.reading_sept
        elif latest_bill == 10:
            accountrecord.previous_reading = accountrecord.reading_oct      
        elif latest_bill == 11:
            accountrecord.previous_reading = accountrecord.reading_nov
        elif latest_bill == 12:
            accountrecord.previous_reading = accountrecord.reading_dec
        accountrecord.save()  


    return render(request,"test.html")    


def write_consumercsv(request):
    accounts = account_info.objects.all()
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="consumerlist.csv"'
    writer = csv.writer(response)
    writer.writerow(["accountinfoid","meternumber","firstname","middlename","lastname","address",])

    for account in accounts:
        writer.writerow([account.accountinfoid,account.meternumber,account.firstname,account.middlename,account.lastname,account.address])

    return response


def write_billcsv(request):
    current_date = date.today()
    current_year = current_date.year
    accounts = account_info.objects.all()
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="bill.csv"'
    writer = csv.writer(response)
    writer.writerow(["accountid","year","commulative_bill","reading_jan","usage_jan","bill_jan","penalty_jan","totalbill_jan","reading_feb","usage_feb","bill_feb","penalty_feb","totalbill_feb","reading_mar","usage_mar","bill_mar","penalty_mar","totalbill_mar",
    "reading_apr","usage_apr","bill_apr","penalty_apr","totalbill_apr","reading_may","usage_may","bill_may","penalty_may","totalbill_may",
    "reading_jun","usage_jun","bill_jun","penalty_jun","totalbill_jun","reading_jul","usage_jul","bill_jul","penalty_jul","totalbill_jul",
    "reading_aug","usage_aug","bill_aug","penalty_aug","totalbill_aug","reading_sept","usage_sept","bill_sept","penalty_sept","totalbill_sept",
    "reading_oct","usage_oct","bill_oct","penalty_oct","totalbill_oct","reading_nov","usage_nov","bill_nov","penalty_nov","totalbill_nov",
    "reading_dec","usage_dec","bill_dec","penalty_dec","totalbill_dec",])


    accounts = usage_record.objects.filter(year = current_year)
    for account in accounts:
        writer.writerow([account.accountid,account.year,account.commulative_bill,account.reading_jan,account.usage_jan,account.bill_jan,account.penalty_jan,account.totalbill_jan,account.reading_feb,account.usage_feb,account.bill_feb,account.penalty_feb,account.totalbill_feb,account.reading_mar,account.usage_mar,account.bill_mar,account.penalty_mar,account.totalbill_mar,
        account.reading_apr,account.usage_apr,account.bill_apr,account.penalty_apr,account.totalbill_apr,account.reading_may,account.usage_may,account.bill_may,account.penalty_may,account.totalbill_may,
        account.reading_jun,account.usage_jun,account.bill_jun,account.penalty_jun,account.totalbill_jun,account.reading_jul,account.usage_jul,account.bill_jul,account.penalty_jul,account.totalbill_jul,
        account.reading_aug,account.usage_aug,account.bill_aug,account.penalty_aug,account.totalbill_aug,account.reading_sept,account.usage_sept,account.bill_sept,account.penalty_sept,account.totalbill_sept,
        account.reading_oct,account.usage_oct,account.bill_oct,account.penalty_oct,account.totalbill_oct,account.reading_nov,account.usage_nov,account.bill_nov,account.penalty_nov,account.totalbill_nov,
        account.reading_dec,account.usage_dec,account.bill_dec,account.penalty_dec,account.totalbill_dec,])

    return response    


def Payment_History(request):
    payment = payment_history()

    with open("myApp/static/website/Payment_History.csv", "r") as csv_file:
        
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        x = 1
        for lines in csv_reader:
            
            payment.id = x
            payment.amount = lines['Amount']
            payment.date = lines['Date']
            payment.or_number = lines['OrNumber']
            payment.time = " "
            payment.postedby = lines['PostedBy']
            payment.consumer = lines["Consumer"]
            consumer = None

            if consumers_info.objects.filter(oldconsumerid = lines['MeterNumber']).exists():
                consumer = consumers_info.objects.get(oldconsumerid = lines['MeterNumber'])
                account = account_info.objects.get(consumerid = consumer.consumerid)
                payment.accountinfoid = account.accountinfoid
                payment.meternumber = account.meternumber
            getyear = lines["Date"]
            year = ""
            i = 0
            for element in getyear:
                if i < 4:
                    year += element
                    i = i + 1
                else:
                    break
            payment.year = int(year)
            print(year)
            payment.save()
            x = x + 1

    return render(request,"test.html")


def getcommu(request):
    current_Date = date.today()
    all_2021 = usage_record.objects.filter(year = 2021)
    all_account = usage_record.objects.all()

    # for record in all_2021:
    #     accountid_str = record.accountinfoid + "-" + str(current_Date.year)
    #     account = usage_record.objects.get(pk = accountid_str)
    #     account.commulative_bill = record.commulative_bill
    #     account.save()
    # for account in all_account:
    #     record = usage_record.objects.get(pk = account.accountinfoid + "-" + str(current_Date.year))
    #     consumer = consumers_info.objects.get(pk = account.consumerid)
    #     record.accountinfoid = account.accountinfoid
    #     record.consumerid = consumer
    #     record.save()
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename="NovDec.csv"'
    writer = csv.writer(response)
    writer.writerow(["accountid","reading_nov","usage_nov","bill_nov","penalty_nov","totalbill_nov",
                    "reading_dec","usage_dec","bill_dec","penalty_dec","totalbill_dec",])
    for account in all_account:
        writer.writerow([account.accountid,
        account.reading_nov,account.usage_nov,account.bill_nov,account.penalty_nov,account.totalbill_nov,
        account.reading_dec,account.usage_dec,account.bill_dec,account.penalty_dec,account.totalbill_dec])

    return response          
    #return render(request,"test.html")    

def writebill(request):
    current_date = date.today()
    with open("myApp/static/website/NovDec.csv", "r") as csv_file:
        
        csv_reader = csv.DictReader(csv_file, delimiter=',')
        for lines in csv_reader:
            
            account_2021 = usage_record.objects.get(pk = lines["accountid"])
            account_2022 =  usage_record.objects.get(pk = account_2021.accountinfoid + "-" + str(current_date.year))
            account_2021.reading_nov = lines["reading_nov"]
            account_2021.usage_nov = lines["usage_nov"] 
            account_2021.bill_nov = lines["bill_nov"]
            account_2021.totalbill_nov = lines["totalbill_nov"]

            account_2021.reading_dec = lines["reading_dec"]
            account_2021.usage_dec = lines["usage_dec"] 
            account_2021.bill_dec = lines["bill_dec"]
            account_2021.totalbill_dec = lines["totalbill_dec"]
            tobeAdd = float(lines["totalbill_nov"]) + float(lines["totalbill_dec"])
            account_2021.commulative_bill += tobeAdd
            account_2021.save()
            account_2022.commulative_bill = account_2021.commulative_bill
            account_2022.save()

    return render(request,"test.html")  

