

class month:
    January = "1"
    February = "2"
    March = "3"
    April = "4"
    May = "5"
    June = "6"
    July = "7"
    August = "8"
    September = "9"
    October = "10"
    November = "11"
    December = "12"

    def getMonth():
        Month_val = {}

        Month_val["jan"] = "January"
        Month_val["feb"] = "February"
        Month_val["mar"] = "March"
        Month_val["apr"] = "April"
        Month_val["may"] = "May"
        Month_val["jun"] = "June"
        Month_val["jul"] = "July"
        Month_val["aug"] = "August"
        Month_val["sept"] = "September"
        Month_val["oct"] = "October"
        Month_val["nov"] = "November"
        Month_val["dec"] = "December"

        return Month_val

class ReqParams():
    sample = {}
    pk = "consumerid"
    fname = "firstname"
    mname = "middlename"
    lname = "lastname"
    add = "homeaddress"
    barangay = "barangay"
    barangay_installation = "barangay_installation"
    sitio = "sitio"
    sex = "sex"
    profilepic = "profilepic"
    installcount = "installcount"
    mobile1 = "mobilenumber"
    mobile2 = "mobilenumber2"
    birthday = "birthday"
    email = "emailaddress"
    PASS = "password"
    usertype = "usertype"

    accid = "accountinfoid"
    address = "address"
    meter_num = "meternumber"
    initialreading = "initial_meter_reading"
    status = "status"
    rateid = "rateid"
    duedate = "duedate"
    meter_reading = "meter_reading"
    image = "required_image"
    file = "required_files"
    DashBoard_url = "DashBoard_url"

    reading = "reading"
    month = "month"

    year = "year"
    month ="month"
    day = "day"

    maleval = "Male"
    femaleval = "Female"

    index = "index"
    max_length = "max_length"
    index1 = "index1"
    max_length1 = "max_length1"
    Next = "Next"
    Previous = "Previous"
    search_for = "search_for"
    

    residential = "1"
    commercial = "2"
    industrial = "3"
    government = "4"

    rateid_name = {
        "1":"Residential",
        "2":"Commercial",
        "3":"Industrial",
        "4":"Government"
    }

    approverflag_level1 = "1"
    approverflag_level2 = "2"
    approverflag_level3 = "3"
    can_approve = "can_approve"

    status_active_val = "1"
    status_inactive_val = "0"

    #table name

    revenue_table = "revenuecode"
    consumers_table = "consumserinfo"
    account_table = "accountinfo"
    accountrecord_table = "accountrecord"

    #list of baranagay
    barangay_list = ['Anao','Cagsing','Calabawan','Cambagte','Campisong','Cañorong',
                     'Guiwanon','Looc','Malatbo','Mangaco','Palanas','Poblacion',
                     'Salamanca','San Roque'
    ]
    barangay_val = [ '1','2','3','4','5','6',
                     '7','8','9','10','11','12',
                     '13','14'

    ]
    month_name = [ 'January','February','March','April','May','June',
                     'July','August','September','October','November','December',

    ]
    user_roles = ["Admin","Teller","Supervisor","Manager","Meter Reader"]

    #revenue code attributes
    application_fee = "application_fee"
    mayors_permit = "mayors_permit"
    gravel_excavation = "gravel_excavation"
    asphalted_road = "asphalted_road"
    cemented_road = "cemented_road"
    residential_service = "residential_service"
    commercial_service = "commercial_service"
    residential_excess_fee = "residential_excess_fee"
    commercial_excess_fee = "commercial_excess_fee"
    drilling_from_mainline = "drilling_from_mainline"
    reinstallation_fee = "reinstallation_fee"
    tapping_fee = "tapping_fee"
    transfer_fee = "transfer_fee"
    repair_fee = "repair_fee"
    three_month_penalty = "three_month_penalty"
    additionalfee_pipe_of_20_lineal_feet = "additionalfee_pipe_of_20_lineal_feet"
    disconnection_after = "disconnection_after"
    disconnection_notice_after = "disconnetion_notice_after"
    penalty_after = "penalty_after"
    percentage = "percentage"
    fix_amount = "fix_amount"
    penaltybasis = "penaltybasis"
    percentage_value = "percentage_value"
    fix_amount_value = "fix_amount_value"

    #session attribute
    template = "template"
    postedby = "postedby"
    reading_postedby = "reading_postedby"
    userid = "userid"
    LOGIN_SESSION = "LogInSession"
    TELLER_LOGIN_VAL = "2"
    ADMIN_LOGIN_VAL = "1"
    SUPERVISOR_LOGIN_VAL = "3"
    INPUTREADER_LOGIN_VAL = "5"
    MANAGER_LOGIN_VAL = "4"
    name = "name"
    verification_code = "verification_code"
    remember_me = "remember_me"
    ACCOUNTID_VAL = "accountinfoidval"
    vcode_expiry = "vcode_expiry"

    #users role
    ADMIN = "1"
    TELLER = "2"
    SUPERVISOR = "3"
    MANAGER = "4"
    INPUT_READER = "5"
    admin = "admin"
    teller = "teller"
    supervisor = "supervisor"
    manager = "manager"
    input_reader = "input_reader"
    reading = "reading"

    Checker_Email = "ceazarjohn.bautista@ctu.edu.ph"
    Engineer_Email = "ceazarjohn.bautista@ctu.edu.ph"
    Mayor_Email = "ceazarjohn.bautista@ctu.edu.ph"
    Teller_Email = "ceazarjohn.bautista@ctu.edu.ph"
    Supervisor_Email = "ceazarjohn.bautista@ctu.edu.ph"

    #Email Credentials
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_USE_TLS = True
    EMAIL_PORT = 587
    EMAIL_HOST_USER = "ginatilancebuwater@gmail.com"
    EMAIL_HOST_PASSWORD = "yjh434ctuG@-@"

class DB_CREDINTIALS():
    ENGINE = "django.db.backends.mysql"
    NAME = "lgu_ginatilan_db"
    USER = "root"
    PASSWORD = "database2021"
    HOST = "localhost"
    PORT = "3306"


class Secret_Secret():
    Secret_key = 'bdji1+*1d!*l3s0r5l2^&r$)nb1%*1*gj1pe@n94d8^fhdumsz'
