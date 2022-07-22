from django.db import models
from django.shortcuts import render
from datetime import date



class consumers_info(models.Model):
    sex_choices = (
        ('male','Male'),
        ('female','Female'),
    )

    consumerid = models.CharField(primary_key=True,max_length = 50)
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45)
    middlename = models.CharField(max_length=45,default="",null = True)
    birthday = models.CharField(max_length=45,null = True)
    mobilenumber = models.CharField(max_length = 50)
    mobilenumber2 = models.CharField(max_length = 50,null = True)
    emailaddress = models.EmailField(null = True)
    homeaddress = models.CharField(max_length=120,) #complete address
    sex = models.CharField(max_length=20,choices=sex_choices,default='male')
    installcount = models.IntegerField()
    profilepic = models.FileField(default = "ui-admin.jpg")
    barangay = models.CharField(max_length=45,default = "01")
    sitio = models.CharField(max_length=45,null = True)
    oldconsumerid = models.CharField(max_length = 50,default = "")
    deleted_flag = models.CharField(max_length = 50,default = "0")

    def __str__(self):
        return self.consumerid

    class Meta:

        db_table = 'consumerinfo'

class account_info(models.Model):
    accountinfoid = models.CharField(max_length=45, primary_key=True)
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45)
    address = models.CharField(max_length=120)
    middlename = models.CharField(max_length=45,default="")
    barangay = models.CharField(max_length = 50,default = "01")
    meternumber = models.CharField(max_length=45)
    initial_meter_reading = models.FloatField(default = 0)
    rateid = models.CharField(max_length=45,)
    status = models.CharField(max_length=45,default = "1") #1 = active, 0 = inactive/suspended
    stop_meter_flag = models.IntegerField(default = 0)
    deleted_flag = models.CharField(max_length = 50,default = "0")
    duedate = models.CharField(max_length=45,null = True)
    penalty_flag = models.IntegerField(default = 0)
    consumerid = models.ForeignKey(consumers_info,on_delete = models.CASCADE)


    def __str__(self):
        return self.accountinfoid

    class Meta:
        db_table = "accountinfo"

class usage_record(models.Model):
    #generate date
    current_date =  date.today()

    accountid = models.CharField(max_length=45,primary_key=True)
    rateid = models.CharField(max_length=45,default= " ")
    prevyeardue = models.FloatField(default = 0)
    excesspayment = models.FloatField(default = 0)
    commulative_bill = models.FloatField(default = 0)
    year = models.BigIntegerField(default=current_date.year)
    consumerid = models.ForeignKey(consumers_info,on_delete = models.CASCADE,default="")
    accountinfoid = models.CharField(max_length = 50,default = "")
    amountpaid_history = models.TextField(default = "")
    datepaid_history = models.TextField(default = "")
    postedby_history = models.TextField(default = "")
    or_number_history = models.TextField(default = "")
    previous_reading = models.FloatField(default = 0)
    reading_date_formatted = models.BooleanField(default=False)



    #january
    reading_jan = models.FloatField(default = 0)
    reading_date_jan = models.CharField(max_length=45,default = " ")
    reading_postedby_jan = models.CharField(max_length=45,default = " ")
    usage_jan = models.FloatField(default = 0)
    penalty_jan = models.FloatField(default = 0)
    bill_jan = models.FloatField(default = 0)
    totalbill_jan = models.FloatField(default = 0)
    paidamt_jan = models.FloatField(default = 0)
    datepaid_jan = models.TextField(default = " ")
    dateposted_jan = models.CharField(max_length=45,default = " ")
    postedby_jan = models.TextField(default = " ")
    txrefnum_jan = models.CharField(max_length=45,default = " ")
    ior_jan = models.CharField(max_length=50,default=" ")
    amountpaid_str_jan = models.TextField(default="")
    #february
    reading_feb = models.FloatField(default = 0)
    reading_date_feb = models.CharField(max_length=45)
    reading_postedby_feb = models.CharField(max_length=45)
    usage_feb = models.FloatField(default = 0)
    penalty_feb = models.FloatField(default = 0)
    bill_feb = models.FloatField(default = 0)
    totalbill_feb = models.FloatField(default = 0)
    paidamt_feb = models.FloatField(default = 0)
    datepaid_feb = models.TextField(default = " ")
    dateposted_feb = models.CharField(max_length=45,default = " ")
    postedby_feb = models.TextField(default=" ")
    txrefnum_feb = models.CharField(max_length=45,default = " ")
    ior_feb = models.CharField(max_length=50,default=" ")
    amountpaid_str_feb = models.TextField(default="")
    #march
    reading_mar = models.FloatField(default = 0)
    reading_date_mar = models.CharField(max_length=45)
    reading_postedby_mar = models.CharField(max_length=45)
    usage_mar = models.FloatField(default = 0)
    penalty_mar = models.FloatField(default = 0)
    bill_mar = models.FloatField(default = 0)
    totalbill_mar = models.FloatField(default = 0)
    paidamt_mar = models.FloatField(default = 0)
    datepaid_mar = models.TextField(default = " ")
    dateposted_mar = models.TextField(default = " ")
    postedby_mar = models.TextField(default=" ")
    txrefnum_mar = models.CharField(max_length=45,default = " ")
    ior_mar = models.CharField(max_length=50,default=" ")
    amountpaid_str_mar = models.TextField(default ="")
    #april
    reading_apr = models.FloatField(default = 0)
    reading_date_apr = models.CharField(max_length=45)
    reading_postedby_apr = models.CharField(max_length=45)
    usage_apr = models.FloatField(default = 0)
    penalty_apr = models.FloatField(default = 0)
    bill_apr = models.FloatField(default = 0)
    totalbill_apr = models.FloatField(default = 0)
    paidamt_apr = models.FloatField(default = 0)
    datepaid_apr = models.TextField(default = " ")
    dateposted_apr = models.CharField(max_length=45,default = " ")
    postedby_apr = models.TextField(default=" ")
    txrefnum_apr = models.CharField(max_length=45,default = " ")
    ior_apr = models.CharField(max_length=50,default=" ")
    amountpaid_str_apr = models.TextField(default="")
    #may
    reading_may = models.FloatField(default = 0)
    reading_date_may = models.CharField(max_length=45)
    reading_postedby_may = models.CharField(max_length=45)
    usage_may = models.FloatField(default = 0)
    penalty_may = models.FloatField(default = 0)
    bill_may = models.FloatField(default = 0)
    totalbill_may = models.FloatField(default = 0)
    paidamt_may = models.FloatField(default = 0)
    datepaid_may = models.TextField(default = " ")
    dateposted_may = models.CharField(max_length=45,default = " ")
    postedby_may = models.TextField(default=" ")
    txrefnum_may = models.CharField(max_length=45,default = " ")
    ior_may = models.CharField(max_length=50,default=" ")
    amountpaid_str_may = models.TextField(default="")
    #june
    reading_jun = models.FloatField(default = 0)
    reading_date_jun = models.CharField(max_length=45)
    reading_postedby_jun = models.CharField(max_length=45)
    usage_jun = models.FloatField(default = 0)
    penalty_jun = models.FloatField(default = 0)
    bill_jun = models.FloatField(default = 0)
    totalbill_jun = models.FloatField(default = 0)
    paidamt_jun = models.FloatField(default = 0)
    datepaid_jun = models.TextField(default = " ")
    dateposted_jun = models.CharField(max_length=45,default = " ")
    postedby_jun = models.TextField(default=" ")
    txrefnum_jun = models.CharField(max_length=45,default = " ")
    ior_jun = models.CharField(max_length=50,default=" ")
    amountpaid_str_jun = models.TextField(default="")
    #july
    reading_jul = models.FloatField(default = 0)
    reading_date_jul = models.CharField(max_length=45)
    reading_postedby_jul = models.CharField(max_length=45)
    usage_jul = models.FloatField(default = 0)
    penalty_jul = models.FloatField(default = 0)
    bill_jul = models.FloatField(default = 0)
    totalbill_jul = models.FloatField(default = 0)
    paidamt_jul = models.FloatField(default = 0)
    datepaid_jul = models.TextField(default = " ")
    dateposted_jul = models.CharField(max_length=45,default = " ")
    postedby_jul = models.TextField(default=" ")
    txrefnum_jul = models.CharField(max_length=45,default = " ")
    ior_jul = models.CharField(max_length=50,default=" ")
    amountpaid_str_jul = models.TextField(default="")
    #august
    reading_aug = models.FloatField(default = 0)
    reading_date_aug = models.CharField(max_length=45)
    reading_postedby_aug = models.CharField(max_length=45)
    usage_aug = models.FloatField(default = 0)
    penalty_aug = models.FloatField(default = 0)
    bill_aug = models.FloatField(default = 0)
    totalbill_aug = models.FloatField(default = 0)
    paidamt_aug = models.FloatField(default = 0)
    datepaid_aug = models.TextField(default = " ")
    dateposted_aug = models.CharField(max_length=45,default = " ")
    postedby_aug = models.TextField(default=" ")
    txrefnum_aug = models.CharField(max_length=45,default = " ")
    ior_aug = models.CharField(max_length=50,default=" ")
    amountpaid_str_aug = models.TextField(default="")
    #september
    reading_sept = models.FloatField(default = 0)
    reading_date_sept = models.CharField(max_length=45)
    reading_postedby_sept = models.CharField(max_length=45)
    usage_sept = models.FloatField(default = 0)
    penalty_sept = models.FloatField(default = 0)
    bill_sept = models.FloatField(default = 0)
    totalbill_sept = models.FloatField(default = 0)
    paidamt_sept = models.FloatField(default = 0)
    datepaid_sept = models.TextField(default = " ")
    dateposted_sept = models.CharField(max_length=45,default = " ")
    postedby_sept = models.TextField(default=" ")
    txrefnum_sept = models.CharField(max_length=45,default = " ")
    ior_sept = models.CharField(max_length=50,default=" ")
    amountpaid_str_sept = models.TextField(default="")
    #october
    reading_oct = models.FloatField(default = 0)
    reading_date_oct = models.CharField(max_length=45)
    reading_postedby_oct = models.CharField(max_length=45)
    usage_oct = models.FloatField(default = 0)
    penalty_oct = models.FloatField(default = 0)
    bill_oct = models.FloatField(default = 0)
    totalbill_oct = models.FloatField(default = 0)
    paidamt_oct = models.FloatField(default = 0)
    datepaid_oct = models.TextField(default = " ")
    dateposted_oct = models.CharField(max_length=45,default = " ")
    postedby_oct = models.TextField(default=" ")
    txrefnum_oct = models.TextField(default = " ")
    ior_oct = models.CharField(max_length=50,default=" ")
    amountpaid_str_oct = models.TextField(default="")
    #november
    reading_nov = models.FloatField(default = 0)
    reading_date_nov = models.CharField(max_length=45)
    reading_postedby_nov = models.CharField(max_length=45)
    usage_nov = models.FloatField(default = 0)
    penalty_nov = models.FloatField(default = 0)
    bill_nov = models.FloatField(default = 0)
    totalbill_nov = models.FloatField(default = 0)
    paidamt_nov = models.FloatField(default = 0)
    datepaid_nov = models.TextField(default = " ")
    dateposted_nov = models.CharField(max_length=45,default = " ")
    postedby_nov = models.TextField(default=" ")
    txrefnum_nov = models.CharField(max_length=45,default = " ")
    ior_nov = models.CharField(max_length=50,default=" ")
    amountpaid_str_nov = models.TextField(default="")
    #december
    reading_dec = models.FloatField(default = 0)
    reading_date_dec = models.CharField(max_length=45)
    reading_postedby_dec = models.CharField(max_length=45)
    usage_dec = models.FloatField(default = 0)
    penalty_dec = models.FloatField(default = 0)
    bill_dec = models.FloatField(default = 0)
    totalbill_dec = models.FloatField(default = 0)
    paidamt_dec = models.FloatField(default = 0)
    datepaid_dec = models.TextField(default = " ")
    dateposted_dec = models.CharField(max_length=45,default = " ")
    postedby_dec = models.TextField(default=" ")
    txrefnum_dec = models.CharField(max_length=45,default = " ")
    ior_dec = models.CharField(max_length=50,default=" ")
    amountpaid_str_dec = models.TextField(default="")

    class Meta:
        db_table = "accountrecord"

class rates(models.Model):
    rateid = models.CharField(max_length=45,primary_key= True)
    minimumreading = models.FloatField()#20 cubic meter
    minimumreading_charge = models.FloatField()
    rateafterminimum = models.FloatField()
    ratepenalty = models.FloatField()
    ratepenaltyfrequency = models.BigIntegerField()
    paymentchedday = models.CharField(max_length=45,default="")


    class Meta:
        db_table = "ratestable"

class SystemUser(models.Model):
    userid = models.CharField(max_length=45,primary_key = True)
    password = models.BinaryField(max_length=450)
    firstname = models.CharField(max_length=45)
    middlename = models.CharField(max_length=45,default="")
    mobilenumber = models.CharField(max_length=45,default="")
    lastname = models.CharField(max_length=45)
    emailaddress = models.EmailField(null = True)
    usertype = models.CharField(max_length=45)
    profilepic = models.FileField(default = "ui-admin.jpg")
    approver_flag = models.CharField(max_length = 50,default="0")

    class Meta:
        db_table = "systemuser"

class barangay_report(models.Model):
    barangay_val = models.CharField(max_length = 50,primary_key = True)
    barangay_name = models.CharField(max_length = 50,default="")
    year = models.BigIntegerField()
    total_due_ytd = models.FloatField(default = 0)
    total_paid_ytd = models.FloatField(default = 0)
    total_usage = models.FloatField(default = 0)
    total_due_january = models.FloatField(default = 0)
    total_paid_january = models.FloatField(default = 0)
    usage_january = models.FloatField(default = 0)
    total_due_february = models.FloatField(default = 0)
    total_paid_february = models.FloatField(default = 0)
    usage_february = models.FloatField(default = 0)
    total_due_march = models.FloatField(default = 0)
    total_paid_march = models.FloatField(default = 0)
    usage_march = models.FloatField(default = 0)
    total_due_april = models.FloatField(default = 0)
    total_paid_april = models.FloatField(default = 0)
    usage_april = models.FloatField(default = 0)
    total_due_may = models.FloatField(default = 0)
    total_paid_may = models.FloatField(default = 0)
    usage_may = models.FloatField(default = 0)
    total_due_june = models.FloatField(default = 0)
    total_paid_june = models.FloatField(default = 0)
    usage_june = models.FloatField(default = 0)
    total_due_july = models.FloatField(default = 0)
    total_paid_july = models.FloatField(default = 0)
    usage_july = models.FloatField(default = 0)
    total_due_august = models.FloatField(default = 0)
    total_paid_august = models.FloatField(default = 0)
    usage_august = models.FloatField(default = 0)
    total_due_september = models.FloatField(default = 0)
    total_paid_september = models.FloatField(default = 0)
    usage_september = models.FloatField(default = 0)
    total_due_october = models.FloatField(default = 0)
    total_paid_october = models.FloatField(default = 0)
    usage_october = models.FloatField(default = 0)
    total_due_november = models.FloatField(default = 0)
    total_paid_november = models.FloatField(default = 0)
    usage_november = models.FloatField(default = 0)
    total_due_december = models.FloatField(default = 0)
    total_paid_december = models.FloatField(default = 0)
    usage_december = models.FloatField(default = 0)

    class Meta:
        db_table = "barangay_record"

class Year_Report(models.Model):
    year = models.IntegerField(primary_key = True)
    total_due_ytd = models.FloatField(default = 0)
    total_paid_ytd = models.FloatField(default = 0)
    total_usage = models.FloatField(default = 0)
    total_due_january = models.FloatField(default = 0)
    total_paid_january = models.FloatField(default = 0)
    usage_january = models.FloatField(default = 0)
    total_due_february = models.FloatField(default = 0)
    total_paid_february = models.FloatField(default = 0)
    usage_february = models.FloatField(default = 0)
    total_due_march = models.FloatField(default = 0)
    total_paid_march = models.FloatField(default = 0)
    usage_march = models.FloatField(default = 0)
    total_due_april = models.FloatField(default = 0)
    total_paid_april = models.FloatField(default = 0)
    usage_april = models.FloatField(default = 0)
    total_due_may = models.FloatField(default = 0)
    total_paid_may = models.FloatField(default = 0)
    usage_may = models.FloatField(default = 0)
    total_due_june = models.FloatField(default = 0)
    total_paid_june = models.FloatField(default = 0)
    usage_june = models.FloatField(default = 0)
    total_due_july = models.FloatField(default = 0)
    total_paid_july = models.FloatField(default = 0)
    usage_july = models.FloatField(default = 0)
    total_due_august = models.FloatField(default = 0)
    total_paid_august = models.FloatField(default = 0)
    usage_august = models.FloatField(default = 0)
    total_due_september = models.FloatField(default = 0)
    total_paid_september = models.FloatField(default = 0)
    usage_september = models.FloatField(default = 0)
    total_due_october = models.FloatField(default = 0)
    total_paid_october = models.FloatField(default = 0)
    usage_october = models.FloatField(default = 0)
    total_due_november = models.FloatField(default = 0)
    total_paid_november = models.FloatField(default = 0)
    usage_november = models.FloatField(default = 0)
    total_due_december = models.FloatField(default = 0)
    total_paid_december = models.FloatField(default = 0)
    usage_december = models.FloatField(default = 0)


    class Meta:
        db_table = "yearly_records"




class revenuecode(models.Model):
    id = models.CharField(max_length = 50,primary_key = True)
    application_fee = models.FloatField(default = 0)
    mayors_permit = models.FloatField(default = 0)
    gravel_excavation = models.FloatField(default = 0)
    asphalted_road = models.FloatField(default = 0)
    cemented_road = models.FloatField(default = 0)
    additionalfee_pipe_of_20_lineal_feet = models.FloatField(default = 0)
    residentialservice_per_month = models.FloatField(default = 0)
    commercialservice_per_month = models.FloatField(default = 0)
    residentialservice_excess_per_cubicmeter = models.FloatField(default = 0)
    commercialservice_excess_per_cubicmeter = models.FloatField(default = 0)
    drilling_from_mainline = models.FloatField(default = 0)
    reinstallation_fee = models.FloatField(default = 0)
    tapping_fee = models.FloatField(default = 0)
    repair_fee = models.FloatField(default = 0)
    transfer_fee = models.FloatField(default = 0)
    three_month_penalty = models.FloatField(default = 0)
    send_disconnection_notice_after = models.IntegerField(default = 0)#months
    disconnection_after = models.IntegerField(default = 0)#months
    penalty_after = models.IntegerField(default = 0)#months
    fix_amount_penalty = models.FloatField(default = 0)
    percentage_penalty = models.FloatField(default = 0)

    class Meta:
        db_table = "revenuecode"



class Applicants_info(models.Model):

    applicantid = models.CharField(primary_key=True,max_length = 50)
    firstname = models.CharField(max_length=45)
    lastname = models.CharField(max_length=45)
    middlename = models.CharField(max_length=45)
    birthday = models.CharField(max_length=45)
    mobilenumber = models.CharField(max_length = 50)
    mobilenumber2 = models.CharField(max_length = 50)
    emailaddress = models.EmailField()
    homeaddress = models.CharField(max_length=45) #complete address
    sex = models.CharField(max_length=20)
    installcount = models.CharField(max_length=45)
    profilepic = models.FileField(default = "ui-admin.jpg")
    barangay_residence = models.CharField(max_length=45)
    barangay_installation = models.CharField(max_length=45)
    address_installation = models.CharField(max_length = 50,default="")
    sitio = models.CharField(max_length=45)
    mayor_approval = models.BigIntegerField(default = 0)
    date_mayorapproval = models.CharField(max_length = 50)
    mayor_comment = models.TextField(default="")
    engineer_approval = models.BigIntegerField(default = 0)
    date_ingeneerapproval = models.CharField(max_length = 50)
    engineer_comment = models.TextField(default="")
    checker_approval = models.BigIntegerField(default = 0)
    date_checkerapproval = models.CharField(max_length = 50)
    checker_comment = models.TextField(default="")
    required_image = models.TextField(default = "")
    required_files = models.TextField(default="")
    consumerid = models.CharField(max_length = 50,default = "")
    date_checkercommented = models.TextField(default = "")
    date_engineercommented = models.TextField(default = "")
    date_mayorcommented = models.TextField(default = "")

    class Meta:
        db_table = "applicants_table"





#tempoary table
class getTotalBill(models.Model):
    bill_id = models.CharField(max_length = 50,primary_key = True)
    con_id = models.CharField(max_length = 50,)
    currentdue = models.FloatField(default = 0)
    rateid = models.CharField(max_length = 50,default = " ")
    paid = models.CharField(max_length = 50,default = " ")
    current_reading = models.FloatField(default = 0)
    previous_reading = models.FloatField(default = 0)
    reading_date = models.CharField(max_length = 50,default="")
    consumption = models.FloatField(default = 0)

    class Meta:
        db_table = "gettotalbill"



class OldCosumerInfo(models.Model):
    con_id = models.CharField(max_length = 50, primary_key = True)
    firstname = models.CharField(max_length = 50)
    middlename = models.CharField(max_length = 50)
    lastname = models.CharField(max_length = 50)
    con_category = models.CharField(max_length = 50)
    meternumber = models.CharField(max_length = 50)
    address = models.CharField(max_length = 50, default = "")

    class Meta:
        db_table = "oldconsumerinfo"



class Primarykey_Basis(models.Model):
    classification = models.CharField(max_length = 50,primary_key = True)
    lastid_used = models.BigIntegerField()

    class Meta:
        db_table = "primarykey_basis"

class MeterReadingModification(models.Model):
    id = models.AutoField(primary_key = True)
    accountinfoid = models.CharField(max_length = 50,default = "")
    reading = models.FloatField()
    year = models.IntegerField(default=0)
    month = models.IntegerField()
    date = models.CharField(max_length = 50)
    meternumber = models.CharField(max_length = 50)
    name = models.CharField(max_length = 50)
    postedby = models.CharField(max_length = 50,default = "")

    class Meta:
        db_table = "meterreadingmodification_table"

class payment_history(models.Model):
   id = models.AutoField(primary_key = True)
   amount = models.FloatField(default = 0)
   date = models.DateTimeField()
   or_number = models.CharField(max_length = 45)
   time = models.CharField(max_length = 45)
   postedby = models.CharField(max_length = 45)
   consumer = models.CharField(max_length = 120)
   accountinfoid = models.CharField(max_length = 45)
   meternumber = models.CharField(max_length = 45)
   year = models.IntegerField(default = 0 )

   class Meta:
       db_table = "payment_history"
