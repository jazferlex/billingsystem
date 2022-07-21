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
from io import BytesIO,StringIO
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import get_template, render_to_string
from django.views import View
from xhtml2pdf import pisa
from smtplib import SMTPException
from .MeterReadingModification import *



from reportlab.pdfgen import canvas  
from django.http import HttpResponse  
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle


def render_to_pdf(template_src,context={}):
    template = get_template(template_src)
    html  = template.render(context)
    result = StringIO()
    pdf = pisa.pisaDocument(StringIO(html.encode("ISO-8859-1")), result)

    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None
            

def ConsumerPDF(request,id):
    account = account_info.objects.get(pk = id)
    consumerid = consumers_info.objects.get(pk = account.consumerid)
    #we get the previous record using old consumerid
    prev_consumerid = getTotalBill.objects.filter(con_id = consumerid.oldconsumerid)
    context = {}
    btnsubmit = request.POST.get("Submit")
    if request.method == "POST":
        context = {
        "id":id
    }
        if btnsubmit:
            render_to_pdf("ConsumerPDF.html",context)

    return render(request,"ConsumerPDF.html",{"prev_record":prev_consumerid,"context":context})    
    

