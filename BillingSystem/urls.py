"""my_django_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from myApp import Payment_Installment, views,AddMeterReading, Payment, ReportGenerator,BillingUtil,update_account,RevenueCode,MeterReadingModification,Application,Utility,DataTransfer,PdfGen,ImportData



urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.login),
    path('source_access/add-new-consumer',views.add_consumer),
    path('source_access/view-consumer-list',views.view_consumer_list),
    path('source_access/add_new_authorized_personel',BillingUtil.add_new_authorized_personel),
    path('source_access/view-system-user',BillingUtil.view_user),
    path('source_access/edit_systemuser=<str:id>',BillingUtil.edit_user),
    path('source_access/add-meter-reading',AddMeterReading.search),
    path('source_access/add-meter-reading/<str:id>',AddMeterReading.add_meter_reading,name="add_meter_reading"),
    path('source-create-new-year-record',ReportGenerator.create_year_record),
    path('source_access/search',views.search_to_update_account),
    path('source_access/update-this-consumer=<str:id>',update_account.update_consumer),
    path('source_access/update-this-account=<str:id>',update_account.update_account),
    path('source_access/Payment',Payment.Search),
    path('source_access/Payment=<str:id>',Payment.pay_bill),
    path('PaymentPaid=<str:id>',Payment.pay_bill),
    path("logout",views.logout),
    path("manual",views.manual),
    path("admin",views.admin),
    path("metereader",views.metereader),
    path("mayor",views.mayor),
    path("teller",views.teller),
    path("checkers",views.checkers),
    path("engineer",views.engineer),
    path("source_access/list-applicants",BillingUtil.view_list_applicants),
    path("delete-this-consumer=<str:id>",views.destroy),
    path("delete-this-account=<str:id>",views.delete_account),
    path("delete-this-system-user=<str:id>",views.delete_user),
    path("change_password",BillingUtil.change_password),
    path('source_access',views.source_access),
    path('suspend_account=<str:id>',views.suspend_account),
    path('source_access/add-account=<str:id>',update_account.add_account),
    path("data_transfer",ReportGenerator.getTotalBills),
    path("data_transfer_reports",ReportGenerator.getUsageRevenue),
    path("source_access/usage-report-data",ReportGenerator.Usage_Report),
    path("source_access/revenue-report-data",ReportGenerator.Revenue_Report),
    path("source_access/view-suspended-account",BillingUtil.view_suspended_account),
    path("reactivate_account<str:id>",BillingUtil.reactivate_account),
    path("suspend_account<str:id>",BillingUtil.suspend_account),
    path("source_access/update-revenue-code",RevenueCode.Update_Revenue),
    path("source_access/view-consumer-list",views.view_consumer_list),
    path("source_access/pending_bills",ReportGenerator.pending_bills),
    path("costumer-service",views.view_account),
    path("view-account=<str:id>",views.consumer_view),
    path("application=<str:id>",Application.application_old_consumer),
    path("view-application-status=<str:id>",Application.view_application_status),
    path("source_access/view-applicants-request=<str:id>",Application.view_applicants),
    path("application",Application.application_new_consumer),
    path("approved_application=<str:id>",Application.approve_applicants),
    path("source_access/view-approved-applicants",Application.view_approved_applicants),
    path("source_access/add-this-applicant=<str:id>",Application.add_this_applicant),
    path("update-this-application=<str:id>",Application.update_this_application),
    path("delete-this-file=<str:id>/<str:filename>",Application.delete_files),
    path("delete-this-image=<str:id>/<str:filename>",Application.delete_images),
    path("delete-this-account=<str:id>",views.delete_account),
    path("source_access/payment-history=<str:id>",Payment.paymenthistory),
    path("source_access/pending_bills=<str:id>",BillingUtil.Deliquent),
    path("get_csv",views.get_csv),
    path("send_bill_via_email",AddMeterReading.send_bill),
    path("source_access/Modify_Reading_Request",MeterReadingModification.Modify_Reading_Request),
    path("Confirm_Modification_Request/<str:id>",MeterReadingModification.Confirm_Modification_Request),
    path("source_access/confirmed-meter-reading",AddMeterReading.add_meter_reading),
    path("source_access/prev-record=<str:id>",ReportGenerator.OldSystemRecordDisplay),
    path("account_record",ReportGenerator.accountrecord),
    path("source_access/Send-Bill",BillingUtil.SendBill),
    path("bill_csv",DataTransfer.CSVBill),
    path("prev_reading",DataTransfer.prev_reading),
    path("consumer_csv",DataTransfer.CSV_Consumer),
    path("barangay_record",DataTransfer.barangayRecord),
    path("source_access/My-Account=<str:id>",BillingUtil.MyAccount),
    path("account-recovery",views.forgot_password),
    path("send_vcode=<str:id>",BillingUtil.send_code),
    path("account-recovery=<str:id>/change-pass",BillingUtil.change_pass),
    path("account-recovery=<str:id>/verification_code",BillingUtil.verification_code),
    path('pdfcreate/', PdfGen.pdf_maker, name='pdfcreate'),
    path('pdfbill/', PdfGen.make_invoice, name='pdfbill'),
    path('source_access/search-payment-history', Payment.search_payment_history),
    path('account=<str:id>', Application.view_account),
    path('change_password/<str:id>>', BillingUtil.change_password),
    path('my-bill=<str:id>', views.Mybill),
    path('credits-CTU-G-Developers', views.Developers),
    path('consumerCsv', DataTransfer.write_consumercsv),
    path('payment_history', DataTransfer.writebill),
    path('stop_meter/<str:id>', BillingUtil.stop_meter),
    path('post_month_bill', Payment_Installment.pay_per_month),
    path('source_access/import_data', ImportData.import_data),
    path('source_access/bulk_input_reading', ImportData.bulkreading),
    

    


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from django.contrib import messages
from django.shortcuts import render
from django.shortcuts import redirect,HttpResponseRedirect
from datetime import datetime
import requests

#import pycountry


scheduler = BackgroundScheduler()
#scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

  
    
@register_job(scheduler, "cron", hour=5, minute=10, id='test_job2', year='*', month=1, day=1 ,replace_existing=True,misfire_grace_time=None)
def test_job2():
    print("running task!")
    ReportGenerator.AutoCreate_NewRecord()

@register_job(scheduler, "cron", hour=5, minute=17, id='test_job3', year='*', month=1, day=2 ,replace_existing=True,misfire_grace_time=None)
def test_job3():
    print("running task!")  
    ReportGenerator.AutoCreate_NewRecord()


@register_job(scheduler, "cron", hour=5, minute=17, id='test_job4', year='*', month=1, day=3 ,replace_existing=True,misfire_grace_time=None)
def test_job4():
    print("running task!")
    ReportGenerator.AutoCreate_NewRecord()


register_events(scheduler)
scheduler.start()
