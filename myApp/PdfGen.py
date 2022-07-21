from . createTable import PDF 
from fpdf import FPDF
from io import BytesIO
from django.http import HttpResponse
import pandas as pd

from . BillingDB import *
from datetime import date, datetime
import qrcode
from . models import *
from django_pandas.io import read_frame
import unicodedata

accounts = None
billdf = None

from . createTable import PDF 
from fpdf import FPDF
from io import BytesIO
from django.http import HttpResponse
import pandas as pd

from . BillingDB import *
from datetime import date, datetime
import qrcode
from . models import *
from django_pandas.io import read_frame
import unicodedata





# to add colnames your list should look like the list below
#TABLE_COL_NAMES = [('Accout ID', 'Last name', 'Meter No.', 'Bill')]


TABLE_COL_NAMES = ['Accout ID', 'Fullname', 'Meter No.', 'Bill', 'Address']
#parameters datatypes are data_table = list and PDF_Title = str
pdf_title= 'Usettled bills'
align_header = 'L'
align_col_name = 'C'
align_data = 'C'
data_size = 8
cell_width = 'even'
title_size = 20
screen_orientation = 'P'
paper_size = 'Letter'
table_header = TABLE_COL_NAMES
header_count = 5

COL_NAMES = [('accountinfoid', 'firstname', 'lastname', 'address', 'middlename',
    'barangay', 'meternumber', 'initial meter reading', 'rate id', 'status', 'duedate', 'consumer id')]

def create_pdf(header_count: int, table_header: str,data_table: list, pdf_title: str, align_header: str, align_data: str, data_size: int,cell_width,title_size: int,screen_orientation: str,paper_size: str,align_col_name: str):
    current_date = date.today()
    date_today = date.today()
    date_today = str(date_today)
    curMonth = str(datetime.now().month)
    strCurMonth = ''
    if curMonth == '1':
        strCurMonth = 'January'
    elif curMonth == '2':
        strCurMonth = 'February'
    elif curMonth == '3':
        strCurMonth ='March'
    elif curMonth == '4':
        strCurMonth == 'April'
    elif curMonth == '5':
        strCurMonth = 'May'
    elif curMonth == '6':
        strCurMonth = 'June'
    elif curMonth == '7':
        strCurMonth = 'July'
    elif curMonth == '8':
        strCurMonth = 'August'
    elif curMonth == '9':
        strCurMonth = 'September'
    elif curMonth == '10':
        strCurMonth = 'October'
    elif curMonth == '11':
        strCurMonth = 'November'
    elif curMonth == '12':
        strCurMonth = 'December'


    

    accounts = account_info.objects.filter(deleted_flag = "0")
    billdf = usage_record.objects.filter(year = current_date.year)   
    dataframe = read_frame(accounts)
    dataframebills = read_frame(billdf)
    db = DB_CREDINTIALS
    #engine = sqlalchemy.create_engine('mysql+pymysql://'+db.USER+':'+db.PASSWORD+'@'+db.HOST+':'+db.PORT+'/'+db.NAME) #accessing database

    #df = pd.read_sql_table('accountinfo', engine) #reading accountinfo table
    #df2 = pd.read_sql_table('accountrecord', engine) #reading accountrecord table
    #df['fullname'] = df['lastname'] + ', ' + df['firstname'] + ' ' + df['middlename'] #combining 3 columns into 1
    dataframe['fullname'] = dataframe['lastname'] + ', ' + dataframe['firstname'] + ' ' + dataframe['middlename'] #combining 3 columns into 1
    bill_data = dataframe[['accountinfoid','fullname','meternumber', 'rateid', 'address']] #making a new dataframe by selecting only the columns that are needed
    totalbills = dataframebills['commulative_bill'].sum().astype(int)
    totalbills = "{:,}".format(totalbills)
    totalbills = str(totalbills)
    bill_data.insert(loc=3,column='bills',value=dataframebills['commulative_bill']) #adding new column from accountrecord table
    bill_data['bills'] = bill_data['bills'].astype(int)
    bill_data.loc[:, "bills"] = bill_data["bills"].map('{:,d}'.format)

    bill_data = bill_data.astype(str)#changing dataframe's data type to str

    dropList = [] #list for rows to be removed 
    unsettledbills_data = bill_data
    unsettledbills_data = unsettledbills_data.drop(['rateid'], axis=1)
    for i in unsettledbills_data.iterrows(): #iterating for every row
        if i[1].bills == '0': #value of bills column in every row compared to 0 in str dtype
            dropList.append(i[0]) #adding rows with 0 value in bills column to the list dropList

    unsettledbills_data = unsettledbills_data.drop(dropList) #droping all the rows with zero bills, note that drop function receives list
    unsettledbills_p = unsettledbills_data.values.tolist() #changing its dtype from dataframe to list

    unsettledbills = []
    for bill in unsettledbills_p:
        insert = []
        fullname =  unicodedata.normalize('NFKD', bill[1]).encode('ASCII', 'ignore')
        acc = unicodedata.normalize('NFKD', bill[0]).encode('ASCII', 'ignore')
        meternum = unicodedata.normalize('NFKD', bill[2]).encode('ASCII', 'ignore')
        address = unicodedata.normalize('NFKD', bill[3]).encode('ASCII', 'ignore')
        commu = unicodedata.normalize('NFKD', bill[4]).encode('ASCII', 'ignore')
        insert.append(acc.decode())
        insert.append(fullname.decode())   
        insert.append(meternum.decode())
        #insert.append(rateid)
        insert.append(address.decode())
        insert.append(commu.decode())
        unsettledbills.append(insert)

    pdf = PDF(screen_orientation, 'mm', paper_size)
    pdf.add_page()
    pdf.set_font("helvetica")
    line_height = pdf.font_size * 2
    col_width = pdf.epw / header_count
    

    def render_table_header():
        pdf.set_font(style='B')
        for col_name in table_header:
            pdf.cell(col_width, line_height, col_name, border=1, align=align_col_name)
        pdf.ln(line_height)
        pdf.set_font(style='')

    def render_title():
        if pdf_title != '':
            pdf.set_font(size=title_size)
            pdf.multi_cell(0, line_height,pdf_title,border=0, align=align_header,ln=3,max_line_height=pdf.font_size)
        pdf.ln(line_height)
        pdf.set_font(size=data_size)

    render_title()
    if totalbills != 0:
        pdf.set_font(style='B')
        pdf.cell(160, line_height,'Total bills: Php '+ totalbills, border=0, align='R')
        pdf.set_font(style='')
    else:
        pdf.ln(line_height)
    pdf.ln(line_height)
    render_table_header()

    for row in data_table:
        if pdf.will_page_break(line_height):
            render_title()
            render_table_header()
        for datum in row:
            pdf.multi_cell(col_width, line_height, datum, border=1, ln=3, max_line_height=pdf.font_size, align=align_data)
            
        pdf.ln(line_height)

    createPDF = pdf.output()
    return createPDF

#making a request to create a pdf
def pdf_maker(request): 
    current_date = date.today()
    date_today = date.today()
    date_today = str(date_today)
    curMonth = str(datetime.now().month)
    strCurMonth = ''
    if curMonth == '1':
        strCurMonth = 'January'
    elif curMonth == '2':
        strCurMonth = 'February'
    elif curMonth == '3':
        strCurMonth ='March'
    elif curMonth == '4':
        strCurMonth == 'April'
    elif curMonth == '5':
        strCurMonth = 'May'
    elif curMonth == '6':
        strCurMonth = 'June'
    elif curMonth == '7':
        strCurMonth = 'July'
    elif curMonth == '8':
        strCurMonth = 'August'
    elif curMonth == '9':
        strCurMonth = 'September'
    elif curMonth == '10':
        strCurMonth = 'October'
    elif curMonth == '11':
        strCurMonth = 'November'
    elif curMonth == '12':
        strCurMonth = 'December'


    TABLE_COL_NAMES = ['Accout ID', 'Fullname', 'Meter No.', 'Bill', 'Address']

    accounts = account_info.objects.filter(deleted_flag = "0")
    billdf = usage_record.objects.filter(year = current_date.year)     
    dataframe = read_frame(accounts)
    dataframebills = read_frame(billdf)
    db = DB_CREDINTIALS
    #engine = sqlalchemy.create_engine('mysql+pymysql://'+db.USER+':'+db.PASSWORD+'@'+db.HOST+':'+db.PORT+'/'+db.NAME) #accessing database

    #df = pd.read_sql_table('accountinfo', engine) #reading accountinfo table
    #df2 = pd.read_sql_table('accountrecord', engine) #reading accountrecord table
    #df['fullname'] = df['lastname'] + ', ' + df['firstname'] + ' ' + df['middlename'] #combining 3 columns into 1
    dataframe['fullname'] = dataframe['lastname'] + ', ' + dataframe['firstname'] + ' ' + dataframe['middlename'] #combining 3 columns into 1
    bill_data = dataframe[['accountinfoid','fullname','meternumber', 'rateid', 'address']] #making a new dataframe by selecting only the columns that are needed
    totalbills = dataframebills['commulative_bill'].sum().astype(int)
    totalbills = "{:,}".format(totalbills)
    totalbills = str(totalbills)
    bill_data.insert(loc=3,column='bills',value=dataframebills['commulative_bill']) #adding new column from accountrecord table
    bill_data['bills'] = bill_data['bills'].astype(int)
    bill_data.loc[:, "bills"] = bill_data["bills"].map('{:,d}'.format)

    bill_data = bill_data.astype(str)#changing dataframe's data type to str

    dropList = [] #list for rows to be removed 
    unsettledbills_data = bill_data
    unsettledbills_data = unsettledbills_data.drop(['rateid'], axis=1)
    for i in unsettledbills_data.iterrows(): #iterating for every row
        if i[1].bills == '0': #value of bills column in every row compared to 0 in str dtype
            dropList.append(i[0]) #adding rows with 0 value in bills column to the list dropList

    unsettledbills_data = unsettledbills_data.drop(dropList) #droping all the rows with zero bills, note that drop function receives list
    unsettledbills_p = unsettledbills_data.values.tolist() #changing its dtype from dataframe to list

    unsettledbills = []
    for bill in unsettledbills_p:
        insert = []
        fullname =  unicodedata.normalize('NFKD', bill[1]).encode('ASCII', 'ignore')
        acc = unicodedata.normalize('NFKD', bill[0]).encode('ASCII', 'ignore')
        meternum = unicodedata.normalize('NFKD', bill[2]).encode('ASCII', 'ignore')
        address = unicodedata.normalize('NFKD', bill[3]).encode('ASCII', 'ignore')
        commu = unicodedata.normalize('NFKD', bill[4]).encode('ASCII', 'ignore')
        insert.append(acc.decode())
        insert.append(fullname.decode())   
        insert.append(meternum.decode())
        #insert.append(rateid)
        insert.append(address.decode())
        insert.append(commu.decode())
        unsettledbills.append(insert)

    pdf = BytesIO(create_pdf(header_count=header_count,table_header=table_header,data_table=unsettledbills,pdf_title=pdf_title, 
    align_data=align_data, align_header=align_header, data_size=data_size, 
    cell_width=cell_width,title_size=title_size, screen_orientation=screen_orientation,
    paper_size=paper_size,align_col_name=align_col_name )) #saving the pdf as BytesIO
    response = HttpResponse(pdf, content_type='application/pdf')
    return response
    
#'Name','Account ID','Meter No.','Consumer Type','Bill'  //header

def create_invoice(table_header: str,screen_orientation: str, paper_size: str, align_col_name: str, align_header: str, align_data: str, title_size: int, data_table: list, data_size: int, pdf_title: str ):
    current_date = date.today()
    date_today = date.today()
    date_today = str(date_today)
    curMonth = str(datetime.now().month)
    strCurMonth = ''
    if curMonth == '1':
        strCurMonth = 'January'
    elif curMonth == '2':
        strCurMonth = 'February'
    elif curMonth == '3':
        strCurMonth ='March'
    elif curMonth == '4':
        strCurMonth == 'April'
    elif curMonth == '5':
        strCurMonth = 'May'
    elif curMonth == '6':
        strCurMonth = 'June'
    elif curMonth == '7':
        strCurMonth = 'July'
    elif curMonth == '8':
        strCurMonth = 'August'
    elif curMonth == '9':
        strCurMonth = 'September'
    elif curMonth == '10':
        strCurMonth = 'October'
    elif curMonth == '11':
        strCurMonth = 'November'
    elif curMonth == '12':
        strCurMonth = 'December'


    TABLE_COL_NAMES = ['Accout ID', 'Fullname', 'Meter No.', 'Bill', 'Address']

    accounts = account_info.objects.filter(deleted_flag = "0")
    billdf = usage_record.objects.filter(year = current_date.year)     
    dataframe = read_frame(accounts)
    dataframebills = read_frame(billdf)
    db = DB_CREDINTIALS
    #engine = sqlalchemy.create_engine('mysql+pymysql://'+db.USER+':'+db.PASSWORD+'@'+db.HOST+':'+db.PORT+'/'+db.NAME) #accessing database

    #df = pd.read_sql_table('accountinfo', engine) #reading accountinfo table
    #df2 = pd.read_sql_table('accountrecord', engine) #reading accountrecord table
    #df['fullname'] = df['lastname'] + ', ' + df['firstname'] + ' ' + df['middlename'] #combining 3 columns into 1
    dataframe['fullname'] = dataframe['lastname'] + ', ' + dataframe['firstname'] + ' ' + dataframe['middlename'] #combining 3 columns into 1
    bill_data = dataframe[['accountinfoid','fullname','meternumber', 'rateid', 'address']] #making a new dataframe by selecting only the columns that are needed
    totalbills = dataframebills['commulative_bill'].sum().astype(int)
    totalbills = "{:,}".format(totalbills)
    totalbills = str(totalbills)
    bill_data.insert(loc=3,column='bills',value=dataframebills['commulative_bill']) #adding new column from accountrecord table
    bill_data['bills'] = bill_data['bills'].astype(int)
    bill_data.loc[:, "bills"] = bill_data["bills"].map('{:,d}'.format)

    bill_data = bill_data.astype(str)#changing dataframe's data type to str

    dropList = [] #list for rows to be removed 
    unsettledbills_data = bill_data
    unsettledbills_data = unsettledbills_data.drop(['rateid'], axis=1)
    for i in unsettledbills_data.iterrows(): #iterating for every row
        if i[1].bills == '0': #value of bills column in every row compared to 0 in str dtype
            dropList.append(i[0]) #adding rows with 0 value in bills column to the list dropList

    unsettledbills_data = unsettledbills_data.drop(dropList) #droping all the rows with zero bills, note that drop function receives list
    unsettledbills_p = unsettledbills_data.values.tolist() #changing its dtype from dataframe to list

    unsettledbills = []
    for bill in unsettledbills_p:
        insert = []
        fullname =  unicodedata.normalize('NFKD', bill[1]).encode('ASCII', 'ignore')
        acc = unicodedata.normalize('NFKD', bill[0]).encode('ASCII', 'ignore')
        meternum = unicodedata.normalize('NFKD', bill[2]).encode('ASCII', 'ignore')
        address = unicodedata.normalize('NFKD', bill[3]).encode('ASCII', 'ignore')
        commu = unicodedata.normalize('NFKD', bill[4]).encode('ASCII', 'ignore')
        insert.append(acc.decode())
        insert.append(fullname.decode())   
        insert.append(meternum.decode())
        #insert.append(rateid)
        insert.append(address.decode())
        insert.append(commu.decode())
        unsettledbills.append(insert)

    pdf = PDF('L', 'mm', 'A5')
    pdf.add_page()
    pdf.set_font("helvetica", size=8)
    pdf.set_auto_page_break(True,45)
    line_height = pdf.font_size * 2
    col_width = pdf.epw/2

    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=2.5,
    border=4,
    )
    qr.add_data('https://www.youtube.com/watch?v=dQw4w9WgXcQ')#this should be a link for the user's billing information
    qr.make(fit=True)

    img = qr.make_image(fill_color="green", back_color="white")
    connType = ''

    
    for i in range(len(bill_data)):
        fullname = unicodedata.normalize('NFKD', bill_data.loc[i,"fullname"]).encode('ASCII', 'ignore').decode()
        accountinfoid = unicodedata.normalize('NFKD', bill_data.loc[i,"accountinfoid"]).encode('ASCII', 'ignore').decode()
        meternumber = unicodedata.normalize('NFKD', bill_data.loc[i,"meternumber"]).encode('ASCII', 'ignore').decode()
        bills = unicodedata.normalize('NFKD', bill_data.loc[i,"bills"]).encode('ASCII', 'ignore').decode()
        if bill_data.loc[i,'rateid'] == '1':
            connType = 'Residential'
        else:
            connType = 'Commercial'
        INVOICE_HTML = f"""
                        <table border="1">
                            <thead>
                                <tr>
                                    <th width="35%">Name</th>
                                    <th width="25%">Account ID</th>
                                    <th width="15%">Meter No.</th>>
                                    <th width="25%">Bill</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{fullname}</td>
                                    <td>{accountinfoid}</td>
                                    <td>{meternumber}</td>
                                    <td>{bill_data.loc[i, "bills"]}</td>
                                </tr>
                            </tbody>
                        </table>
                        <table border="1">
                            <thead>
                                <tr>
                                    <th width="50%">Month</th>
                                    <th width="50%">Connection Type</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>{strCurMonth}</td>
                                    <td>{connType}</td>
                                </tr>
                            </tbody>
                        </table>
                        """
        pdf.cell(col_width,line_height,'Date: '+ date_today, align='L', ln=True)#dateProduced
        pdf.cell(col_width,line_height, 'Ginatilan Waters', align='L', ln=True)#CompanyName
        pdf.cell(col_width,line_height, 'Ginatilan Municipal Hall', align='L', ln=True)#Name of the building/address
        pdf.cell(col_width,line_height, 'Poblacion, Ginatilan, Cebu', align='L', ln=True)#address
        pdf.cell(col_width,line_height, '', align='L', ln=True)
        pdf.write_html(INVOICE_HTML,table_line_separators=True,)
        pdf.cell(col_width,line_height, '', align='L', ln=True)
        pdf.image(img.get_image(), x=150, y=30)
    
    
    createPDF = pdf.output()
    return createPDF

def make_invoice(request):
    current_date = date.today()
    date_today = date.today()
    date_today = str(date_today)
    curMonth = str(datetime.now().month)
    strCurMonth = ''
    if curMonth == '1':
        strCurMonth = 'January'
    elif curMonth == '2':
        strCurMonth = 'February'
    elif curMonth == '3':
        strCurMonth ='March'
    elif curMonth == '4':
        strCurMonth == 'April'
    elif curMonth == '5':
        strCurMonth = 'May'
    elif curMonth == '6':
        strCurMonth = 'June'
    elif curMonth == '7':
        strCurMonth = 'July'
    elif curMonth == '8':
        strCurMonth = 'August'
    elif curMonth == '9':
        strCurMonth = 'September'
    elif curMonth == '10':
        strCurMonth = 'October'
    elif curMonth == '11':
        strCurMonth = 'November'
    elif curMonth == '12':
        strCurMonth = 'December'


    TABLE_COL_NAMES = ['Accout ID', 'Fullname', 'Meter No.', 'Bill', 'Address']

    accounts = account_info.objects.filter(deleted_flag = "0")
    billdf = usage_record.objects.filter(year = current_date.year)     
    dataframe = read_frame(accounts)
    dataframebills = read_frame(billdf)
    db = DB_CREDINTIALS
    #engine = sqlalchemy.create_engine('mysql+pymysql://'+db.USER+':'+db.PASSWORD+'@'+db.HOST+':'+db.PORT+'/'+db.NAME) #accessing database

    #df = pd.read_sql_table('accountinfo', engine) #reading accountinfo table
    #df2 = pd.read_sql_table('accountrecord', engine) #reading accountrecord table
    #df['fullname'] = df['lastname'] + ', ' + df['firstname'] + ' ' + df['middlename'] #combining 3 columns into 1
    dataframe['fullname'] = dataframe['lastname'] + ', ' + dataframe['firstname'] + ' ' + dataframe['middlename'] #combining 3 columns into 1
    bill_data = dataframe[['accountinfoid','fullname','meternumber', 'rateid', 'address']] #making a new dataframe by selecting only the columns that are needed
    totalbills = dataframebills['commulative_bill'].sum().astype(int)
    totalbills = "{:,}".format(totalbills)
    totalbills = str(totalbills)
    bill_data.insert(loc=3,column='bills',value=dataframebills['commulative_bill']) #adding new column from accountrecord table
    bill_data['bills'] = bill_data['bills'].astype(int)
    bill_data.loc[:, "bills"] = bill_data["bills"].map('{:,d}'.format)

    bill_data = bill_data.astype(str)#changing dataframe's data type to str

    dropList = [] #list for rows to be removed 
    unsettledbills_data = bill_data
    unsettledbills_data = unsettledbills_data.drop(['rateid'], axis=1)
    for i in unsettledbills_data.iterrows(): #iterating for every row
        if i[1].bills == '0': #value of bills column in every row compared to 0 in str dtype
            dropList.append(i[0]) #adding rows with 0 value in bills column to the list dropList

    unsettledbills_data = unsettledbills_data.drop(dropList) #droping all the rows with zero bills, note that drop function receives list
    unsettledbills_p = unsettledbills_data.values.tolist() #changing its dtype from dataframe to list

    unsettledbills = []
    for bill in unsettledbills_p:
        insert = []
        fullname =  unicodedata.normalize('NFKD', bill[1]).encode('ASCII', 'ignore')
        acc = unicodedata.normalize('NFKD', bill[0]).encode('ASCII', 'ignore')
        meternum = unicodedata.normalize('NFKD', bill[2]).encode('ASCII', 'ignore')
        address = unicodedata.normalize('NFKD', bill[3]).encode('ASCII', 'ignore')
        commu = unicodedata.normalize('NFKD', bill[4]).encode('ASCII', 'ignore')
        insert.append(acc.decode())
        insert.append(fullname.decode())   
        insert.append(meternum.decode())
        #insert.append(rateid)
        insert.append(address.decode())
        insert.append(commu.decode())
        unsettledbills.append(insert)

    pdf = BytesIO(create_invoice(table_header=table_header, screen_orientation=screen_orientation, paper_size=paper_size,
        align_col_name=align_col_name, align_header=align_header, align_data=align_data, title_size=title_size, 
        data_size=data_size, data_table=unsettledbills_data, pdf_title=pdf_title))
    response = HttpResponse(pdf, content_type='application/pdf')
    return response


