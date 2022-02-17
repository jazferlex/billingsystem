function show(usertype){
    //usertype = "{{ context.UserType }}";

    document.getElementById("rates").style.display = 'none';
    document.getElementById("usermanagement").style.display = 'none';
    document.getElementById("backupdatabase").style.display = 'none';
    document.getElementById("manage_account").style.display = 'none';
    document.getElementById("input_reading").style.display = 'none';
    document.getElementById("application").style.display = 'none';
    document.getElementById("reports").style.display = 'none';
    document.getElementById("billspayment").style.display = 'none';
    document.getElementById("usercreation").style.display = 'none';
    document.getElementById("modification").style.display = 'none';

    //admin
    if(usertype.includes("1") === true){
        document.getElementById("usermanagement").style.display = 'block';
        document.getElementById("backupdatabase").style.display = 'block';
        document.getElementById("usercreation").style.display = 'block'
    }
    //Teller
    if(usertype.includes("2") === true){
        document.getElementById("manage_account").style.display = 'block';
        document.getElementById("reports").style.display = 'block';
        document.getElementById("input_reading").style.display = 'block';
        document.getElementById("application").style.display = 'block';
        document.getElementById("billspayment").style.display = 'block'
        document.getElementById("approve_app").style.display = 'none'
        document.getElementById("modification").style.display = 'block'

    }
    //Supervisor
    if(usertype.includes("3") === true){
          document.getElementById("manage_account").style.display = 'block';
          document.getElementById("reports").style.display = 'block';
          document.getElementById("input_reading").style.display = 'block';
          document.getElementById("application").style.display = 'block';
          document.getElementById("billspayment").style.display = 'block'
          document.getElementById("rates").style.display = 'block';
          document.getElementById("modification").style.display = 'block';
      
      }
    //Manager
    if(usertype.includes("4") === true){
        document.getElementById("rates").style.display = 'block';
        document.getElementById("application").style.display = 'block';
        document.getElementById("reports").style.display = 'block';
    }

    //meter reader
    if(usertype.includes("5") === true){
        document.getElementById("input_reading").style.display = 'block';
    }



};
function hide_buttons(reading_jan,reading_feb,reading_mar,reading_apr,reading_may,reading_jun,reading_jul,reading_aug,reading_sept,reading_oct,reading_nov,reading_dec){
    var current_date = new Date();
    var month = current_date.getMonth();
    document.getElementById("mod_jan").style.display = 'none';
    document.getElementById("mod_feb").style.display = 'none';
    document.getElementById("mod_mar").style.display = 'none';
    document.getElementById("mod_apr").style.display = 'none';
    document.getElementById("mod_may").style.display = 'none';
    document.getElementById("mod_jun").style.display = 'none';
    document.getElementById("mod_jul").style.display = 'none';
    document.getElementById("mod_aug").style.display = 'none';
    document.getElementById("mod_sept").style.display = 'none';
    document.getElementById("mod_oct").style.display = 'none';
    document.getElementById("mod_nov").style.display = 'none';
    document.getElementById("mod_dec").style.display = 'none';

    document.getElementById("sub_jan").style.display = 'none';
    document.getElementById("sub_feb").style.display = 'none';
    document.getElementById("sub_mar").style.display = 'none';
    document.getElementById("sub_apr").style.display = 'none';
    document.getElementById("sub_may").style.display = 'none';
    document.getElementById("sub_jun").style.display = 'none';
    document.getElementById("sub_jul").style.display = 'none';
    document.getElementById("sub_aug").style.display = 'none';
    document.getElementById("sub_sept").style.display = 'none';
    document.getElementById("sub_oct").style.display = 'none';
    document.getElementById("sub_nov").style.display = 'none';
    document.getElementById("sub_dec").style.display = 'none';

    document.getElementById("reading_jan").style.display = 'none';
    document.getElementById("reading_feb").style.display = 'none';
    document.getElementById("reading_mar").style.display = 'none';
    document.getElementById("reading_apr").style.display = 'none';
    document.getElementById("reading_may").style.display = 'none';
    document.getElementById("reading_jun").style.display = 'none';
    document.getElementById("reading_jul").style.display = 'none';
    document.getElementById("reading_aug").style.display = 'none';
    document.getElementById("reading_sept").style.display = 'none';
    document.getElementById("reading_oct").style.display = 'none';
    document.getElementById("reading_nov").style.display = 'none';
    document.getElementById("reading_dec").style.display = 'none';
    
    

    
        //fields
    if(reading_jan != 0 || month == 1){
        document.getElementById("reading_jan").style.display = 'block';
        if(reading_jan != 0){
            document.getElementById("mod_jan").style.display = 'block';
        }else{
            document.getElementById("sub_jan").style.display = 'block';
        }
        
    }
    if(reading_feb != 0 || month == 2){
        document.getElementById("reading_jan").style.display = 'block';
        document.getElementById("reading_feb").style.display = 'block';
        if(reading_feb != 0){
            document.getElementById("mod_feb").style.display = 'block';
        }else{    
            document.getElementById("sub_feb").style.display = 'block';
        }
    }

    if(reading_mar != 0 || month == 3){   
        document.getElementById("reading_feb").style.display = 'block';      
        document.getElementById("reading_mar").style.display = 'block';
        if(reading_mar != 0){
            document.getElementById("mod_mar").style.display = 'block';
        }else{    
            document.getElementById("sub_mar").style.display = 'block';
        }
    }

    if(reading_apr != 0 || month == 4){        
        document.getElementById("reading_mar").style.display = 'block';           
        document.getElementById("reading_apr").style.display = 'block';
        if(reading_apr != 0){
            document.getElementById("mod_apr").style.display = 'block';
        }else{    
            document.getElementById("sub_apr").style.display = 'block';
        }
    }

    if(reading_may != 0  || month == 5){    
        document.getElementById("reading_apr").style.display = 'block';
        document.getElementById("reading_may").style.display = 'block'; 
        if(reading_may != 0){
            document.getElementById("mod_may").style.display = 'block';
        }else{    
            document.getElementById("sub_may").style.display = 'block';
        }
    }

    if(reading_jun != 0 || month == 6){      
        document.getElementById("reading_may").style.display = 'block';  
        document.getElementById("reading_jun").style.display = 'block';  
        if(reading_jun != 0){
            document.getElementById("mod_jun").style.display = 'block';
        }else{    
            document.getElementById("sub_jun").style.display = 'block';
        }
    }

    if(reading_jul != 0 || month == 7){
        document.getElementById("reading_jun").style.display = 'block';
        document.getElementById("reading_jul").style.display = 'block'; 
        if(reading_jul != 0){
            document.getElementById("mod_jul").style.display = 'block';
        }else{    
            document.getElementById("sub_jul").style.display = 'block';
        }
    }

    if(reading_aug != 0 || month == 8){   
        document.getElementById("reading_jul").style.display = 'block';                
        document.getElementById("reading_aug").style.display = 'block';
        if(reading_aug != 0){
            document.getElementById("mod_aug").style.display = 'block';
        }else{    
            document.getElementById("sub_aug").style.display = 'block';
        }
    }

    if(reading_sept != 0 || month == 9){
        document.getElementById("reading_aug").style.display = 'block';
        document.getElementById("reading_sept").style.display = 'block';
        if(reading_sept != 0){
            document.getElementById("mod_sept").style.display = 'block';
        }else{    
            document.getElementById("sub_sept").style.display = 'block';
        }
    }

    if(reading_oct != 0 || month == 10){
        document.getElementById("reading_sept").style.display = 'block';
        document.getElementById("reading_oct").style.display = 'block';    
        if(reading_oct != 0){
            document.getElementById("mod_oct").style.display = 'block';
        }else{    
            document.getElementById("sub_oct").style.display = 'block';
        }
    }

    if(reading_nov != 0 || month == 11){
        document.getElementById("reading_oct").style.display = 'block';
        document.getElementById("reading_nov").style.display = 'block'; 
        if(reading_nov != 0){
            document.getElementById("mod_nov").style.display = 'block';
        }else{    
            document.getElementById("sub_nov").style.display = 'block';
        }
    }

    if(reading_dec != 0 || month == 0){
        document.getElementById("reading_nov").style.display = 'block';
        document.getElementById("reading_dec").style.display = 'block';
        if(reading_dec != 0){
            document.getElementById("mod_dec").style.display = 'block';
        }else{
            document.getElementById("sub_dec").style.display = 'block';
        
    }
        
    }
   
};

$(document).ready(function() {
    $('#btn1').click(function() {
        var disabled = $("#reading_jan").prop('disabled');
        if (disabled) {
            $("#reading_jan").prop('disabled', false);
            document.getElementById("div_jan").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_jan").prop('disabled', true);   
            document.getElementById("div_jan").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn2').click(function() {
        var disabled = $("#reading_feb").prop('disabled');
        if (disabled) {
            $("#reading_feb").prop('disabled', false);
            document.getElementById("div_feb").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_feb").prop('disabled', true);   
            document.getElementById("div_feb").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn3').click(function() {
        var disabled = $("#reading_mar").prop('disabled');
        if (disabled) {
            $("#reading_mar").prop('disabled', false);
            document.getElementById("div_mar").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_mar").prop('disabled', true);   
            document.getElementById("div_mar").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn4').click(function() {
        var disabled = $("#reading_apr").prop('disabled');
        if (disabled) {
            $("#reading_apr").prop('disabled', false);
            document.getElementById("div_apr").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_apr").prop('disabled', true);   
            document.getElementById("div_apr").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn5').click(function() {
        var disabled = $("#reading_may").prop('disabled');
        if (disabled) {
            $("#reading_may").prop('disabled', false);
            document.getElementById("div_may").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_may").prop('disabled', true);   
            document.getElementById("div_may").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn6').click(function() {
        var disabled = $("#reading_jun").prop('disabled');
        if (disabled) {
            $("#reading_jun").prop('disabled', false);
            document.getElementById("div_jun").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_jun").prop('disabled', true);   
            document.getElementById("div_jun").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn7').click(function() {
        var disabled = $("#reading_jul").prop('disabled');
        if (disabled) {
            $("#reading_jul").prop('disabled', false);
            document.getElementById("div_jul").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_jul").prop('disabled', true);   
            document.getElementById("div_jul").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn8').click(function() {
        var disabled = $("#reading_aug").prop('disabled');
        if (disabled) {
            $("#reading_aug").prop('disabled', false);
            document.getElementById("div_aug").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_aug").prop('disabled', true);   
            document.getElementById("div_aug").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn9').click(function() {
        var disabled = $("#reading_sept").prop('disabled');
        if (disabled) {
            $("#reading_sept").prop('disabled', false);
            document.getElementById("div_sept").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_sept").prop('disabled', true);   
            document.getElementById("div_sept").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn10').click(function() {
        var disabled = $("#reading_oct").prop('disabled');
        if (disabled) {
            $("#reading_oct").prop('disabled', false);
            document.getElementById("div_oct").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_oct").prop('disabled', true);   
            document.getElementById("div_oct").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn11').click(function() {
        var disabled = $("#reading_nov").prop('disabled');
        if (disabled) {
            $("#reading_nov").prop('disabled', false);
            document.getElementById("div_nov").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_nov").prop('disabled', true);   
            document.getElementById("div_nov").style.display = 'none';     // if enabled, disable
        }
    })
});
$(document).ready(function() {
    $('#btn12').click(function() {
        var disabled = $("#reading_dec").prop('disabled');
        if (disabled) {
            $("#reading_dec").prop('disabled', false);
            document.getElementById("div_dec").style.display = 'block';     // if disabled, enable
        }
        else {
            $("#reading_dec").prop('disabled', true);   
            document.getElementById("div_dec").style.display = 'none';     // if enabled, disable
        }
    })
});
function hide_div(reading_jan,reading_feb,reading_mar,reading_apr,reading_may,reading_jun,reading_jul,reading_aug,reading_sept,reading_oct,reading_nov,reading_dec){
    var current_date = new Date();
    var month = current_date.getMonth();
    document.getElementById("div_jan").style.display = 'none';
    document.getElementById("div_feb").style.display = 'none';
    document.getElementById("div_mar").style.display = 'none';
    document.getElementById("div_apr").style.display = 'none';
    document.getElementById("div_may").style.display = 'none';
    document.getElementById("div_jun").style.display = 'none';
    document.getElementById("div_jul").style.display = 'none';
    document.getElementById("div_aug").style.display = 'none';
    document.getElementById("div_sept").style.display = 'none';
    document.getElementById("div_oct").style.display = 'none';
    document.getElementById("div_nov").style.display = 'none';
    document.getElementById("div_dec").style.display = 'none';

    document.getElementById("mod_jan").style.display = 'none';
    document.getElementById("mod_feb").style.display = 'none';
    document.getElementById("mod_mar").style.display = 'none';
    document.getElementById("mod_apr").style.display = 'none';
    document.getElementById("mod_may").style.display = 'none';
    document.getElementById("mod_jun").style.display = 'none';
    document.getElementById("mod_jul").style.display = 'none';
    document.getElementById("mod_aug").style.display = 'none';
    document.getElementById("mod_sept").style.display = 'none';
    document.getElementById("mod_oct").style.display = 'none';
    document.getElementById("mod_nov").style.display = 'none';
    document.getElementById("mod_dec").style.display = 'none';

    document.getElementById("sub_jan").style.display = 'none';
    document.getElementById("sub_feb").style.display = 'none';
    document.getElementById("sub_mar").style.display = 'none';
    document.getElementById("sub_apr").style.display = 'none';
    document.getElementById("sub_may").style.display = 'none';
    document.getElementById("sub_jun").style.display = 'none';
    document.getElementById("sub_jul").style.display = 'none';
    document.getElementById("sub_aug").style.display = 'none';
    document.getElementById("sub_sept").style.display = 'none';
    document.getElementById("sub_oct").style.display = 'none';
    document.getElementById("sub_nov").style.display = 'none';
    document.getElementById("sub_dec").style.display = 'none';

    
  
       
        if(reading_jan != 0){
            document.getElementById("mod_jan").style.display = 'block';
        }else{
            document.getElementById("sub_jan").style.display = 'block';
        }
        
    
        if(reading_feb != 0){
            document.getElementById("mod_feb").style.display = 'block';
        }else{    
            document.getElementById("sub_feb").style.display = 'block';
        }
    

      
  
        if(reading_mar != 0){
            document.getElementById("mod_mar").style.display = 'block';
        }else{    
            document.getElementById("sub_mar").style.display = 'block';
        }
    

         
        
        if(reading_apr != 0){
            document.getElementById("mod_apr").style.display = 'block';
        }else{    
            document.getElementById("sub_apr").style.display = 'block';
        }
    

      
        if(reading_may != 0){
            document.getElementById("mod_may").style.display = 'block';
        }else{    
            document.getElementById("sub_may").style.display = 'block';
        }
    

         
     
        if(reading_jun != 0){
            document.getElementById("mod_jun").style.display = 'block';
        }else{    
            document.getElementById("sub_jun").style.display = 'block';
        }
    

    
        if(reading_jul != 0){
            document.getElementById("mod_jul").style.display = 'block';
        }else{    
            document.getElementById("sub_jul").style.display = 'block';
        }
    

      
        if(reading_aug != 0){
            document.getElementById("mod_aug").style.display = 'block';
        }else{    
            document.getElementById("sub_aug").style.display = 'block';
        }
    

    
        if(reading_sept != 0){
            document.getElementById("mod_sept").style.display = 'block';
        }else{    
            document.getElementById("sub_sept").style.display = 'block';
        }
    

      
        if(reading_oct != 0){
            document.getElementById("mod_oct").style.display = 'block';
        }else{    
            document.getElementById("sub_oct").style.display = 'block';
        }
    

   
       
        if(reading_nov != 0){
            document.getElementById("mod_nov").style.display = 'block';
        }else{    
            document.getElementById("sub_nov").style.display = 'block';
        }
    

   
        if(reading_dec != 0){
            document.getElementById("mod_dec").style.display = 'block';
        }else{
            document.getElementById("sub_dec").style.display = 'block';
        
    
    //displaying fields before month of reading
    // month_val = month;
    // if(month == 0){
    //     month_val = 12
    // }
    // var jan = 1;                                                                   
    // if(jan <= month_val){
    //     document.getElementById("reading_jan").style.display = 'block';
    // }
    // var feb = 2;
    // if(feb <= month_val){
    //     document.getElementById("reading_feb").style.display = 'block';
    // }
    // var mar = 3;
    // if(mar <= month_val){
    //     document.getElementById("reading_mar").style.display = 'block';
    // }
    // var apr = 4;
    // if(apr <= month_val){
    //     document.getElementById("reading_apr").style.display = 'block';
    // }
    // var may = 5;
    // if(may <= month_val){
    //     document.getElementById("reading_may").style.display = 'block';
    // }
    // var jun = 6;
    // if(jun <= month_val){
    //     document.getElementById("reading_jun").style.display = 'block';
    // }
    // var jul = 7;                                                                   
    // if(jul <= month_val){
    //     document.getElementById("reading_jul").style.display = 'block';
    // }
    // var aug = 8;
    // if(aug <= month_val){
    //     document.getElementById("reading_aug").style.display = 'block'; 
    // }
    // var sept = 9;
    // if(sept <= month_val){
    //     document.getElementById("reading_sept").style.display = 'block';
    // }
    // var oct = 10;
    // if(oct <= month_val){
    //     document.getElementById("reading_oct").style.display = 'block'; 
    // }
    // var nov = 11;
    // if(nov <= month_val){
    //     document.getElementById("reading_nov").style.display = 'block'; 
    // }
    // var dec = 12;
    // if(dec <= month_val){
    //     document.getElementById("reading_dec").style.display = 'block'; 
    // }


    // //buttons
    // if(month == 1){
    // document.getElementById("div_jan").style.display = 'block';  
        
    // }
    // if(month == 2){
    //     document.getElementById("div_jan").style.display = 'block';  
    //     document.getElementById("div_feb").style.display = 'block';
    //     if(reading_jan != 0){
    //         document.getElementById("mod_jan").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_jan").style.display = 'block';
    //     }
    // }
    // if(month == 3){
    //     document.getElementById("div_mar").style.display = 'block';  
    //     document.getElementById("div_feb").style.display = 'block';
    //     if(reading_feb != 0){
    //         document.getElementById("mod_feb").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_feb").style.display = 'block';
    //     }
    // }
    // if(month == 4){
    //     document.getElementById("div_mar").style.display = 'block';  
    //     document.getElementById("div_apr").style.display = 'block';
    //     if(reading_mar != 0){
    //         document.getElementById("mod_mar").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_mar").style.display = 'block';
    //     }
    // }
    // if(month == 5){
    //     document.getElementById("div_may").style.display = 'block';  
    //     document.getElementById("div_apr").style.display = 'block';
    //     if(reading_apr != 0){
    //         document.getElementById("mod_apr").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_apr").style.display = 'block';
    //     }
    // }
    // if(month == 6){
    //     document.getElementById("div_may").style.display = 'block';  
    //     document.getElementById("div_jun").style.display = 'block';
    //     if(reading_may != 0){
    //         document.getElementById("mod_may").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_may").style.display = 'block';
    //     }
    // }
    // if(month == 7){
    //     document.getElementById("div_jun").style.display = 'block';  
    //     document.getElementById("div_jul").style.display = 'block';
    //     if(reading_jun != 0){
    //         document.getElementById("mod_jun").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_jun").style.display = 'block';
    //     }
    // }
    // if(month == 8){
    //     document.getElementById("div_aug").style.display = 'block';  
    //     document.getElementById("div_jul").style.display = 'block';
    //     if(reading_jul != 0){
    //         document.getElementById("mod_jul").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_jul").style.display = 'block';
    //     }
    // }
    // if(month == 9){
    //     document.getElementById("div_aug").style.display = 'block';  
    //     document.getElementById("div_sept").style.display = 'block';
    //     if(reading_aug != 0){
    //         document.getElementById("mod_aug").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_aug").style.display = 'block';
    //     }
    // }
    // if(month == 10){
    //     document.getElementById("div_oct").style.display = 'block';  
    //     document.getElementById("div_sept").style.display = 'block';
    //     if(reading_sept != 0){
    //         document.getElementById("mod_sept").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_sept").style.display = 'block';
    //     }
    // }
    // if(month == 11){
    //     document.getElementById("div_oct").style.display = 'block';  
    //     document.getElementById("div_nov").style.display = 'block';
    //     if(reading_oct != 0){
    //         document.getElementById("mod_oct").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_oct").style.display = 'block';
    //     }
    // }
    // if(month == 0){
    //     document.getElementById("div_nov").style.display = 'block';  
    //     document.getElementById("div_dec").style.display = 'block';
    //     if(reading_nov != 0){
    //         document.getElementById("mod_nov").style.display = 'block';
    //     }else{    
    //         document.getElementById("sub_nov").style.display = 'block';
    //     }
    // }
    

}

function set_account(){
    var nxtbtn = document.getElementById("postbtn");
    var fname = document.getElementById("Fname").value;
    var mname = document.getElementById("Mname").value;
    var lname = document.getElementById("Lname").value;
    var email = document.getElementById("email").value;
    //var installcount = document.getElementById("installcount").value;
    var profilepic = document.getElementById("profilepic").value;
    var mobile1 = document.getElementById("mobile1").value;
    var mobile2 = document.getElementById("mobile2").value;
    var birthday = document.getElementById("birthday").value;
    var sitio = document.getElementById("sitio").value;

    var regex = /((^(\+)(\d){12}$)|(^\d{11}$))/;
    var mobile1Result = regex.test(mobile1);
    var mobile2Result = regex.test(mobile2);

    if (fname != "" && mname != "" && lname != ""  &&
        email != "" && mobile1 != "" &&
        mobile2 != "" && birthday != "" && sitio != ""  && mobile1Result == true
        && mobile2Result == true){

        nxtbtn.disabled = false;
    } else {
      nxtbtn.disabled = true;
    }
    if(mobile1Result == false && mobile1 != ""){
      document.getElementById("mobile1_error").innerHTML = "Invalid!"
    }else{
      document.getElementById("mobile1_error").innerHTML = ""
    }

    if(mobile2Result == false && mobile2 != ""){
      document.getElementById("mobile2_error").innerHTML = "Invalid!"
    }else{
      document.getElementById("mobile2_error").innerHTML = ""
    }
    }

function addconsumer(){

    var postbtn = document.getElementById("postbtn");
    var initial = document.getElementById("initialmeterreading").value;
    var meternum = document.getElementById("meternum").value;

    if( initial != "" && meternum != ""){
        postbtn.disabled = false;
    }else{
        postbtn.disabled = true;
    }
    }   

function load_role(approverflag){

    if( approverflag.includes("1")){
      document.getElementById("admin").checked = true;
    }
    if( approverflag.includes("2")){
      document.getElementById("teller").checked = true;
    } 
     if( approverflag.includes("3")){
      document.getElementById("supervisor").checked = true;
    }
    if( approverflag.includes("4")){
      document.getElementById("manager").checked = true;
    }
     if( approverflag.includes("5")){
      document.getElementById("reader").checked = true;
    }    
}

function loadchecker(checker,engineer,mayor){
    document.getElementById("checker").checked = false;
    document.getElementById("engineer").checked = false;
    document.getElementById("mayor").checked = false;
  

      if(checker == 1){
          document.getElementById("checker").checked = true;
      }
      if(engineer == 1){
        document.getElementById("engineer").checked = true;
      }
      if(mayor == 1){
        document.getElementById("mayor").checked = true;
      }
  }


function comment_table(checkercomment,engineercomment,mayorcomment){
    document.getElementById("checkercomment").style.display = "none";
    document.getElementById("engineercomment").style.display = "none";
    document.getElementById("mayorcomment").style.display = "none";

    if( checkercomment != ""){
        document.getElementById("checkercomment").style.display = "block";
        }
    if(engineercomment != ""){
    document.getElementById("engineercomment").style.display = "block";
    }
    if(mayorcomment != ""){
    document.getElementById("mayorcomment").style.display = "block";
    }
}  

function generate(duration) {  
    var doc = new jsPDF('p', 'pt', 'letter');  
    var htmlstring = '';  
    var tempVarToCheckPageHeight = 0;  
    var pageHeight = 0;  
    
    pageHeight = doc.internal.pageSize.height;  
    specialElementHandlers = {  
        // element with id of "bypass" - jQuery style selector  
        '#bypassme': function(element, renderer) {  
            // true = "handled elsewhere, bypass text extraction"  
            return true  
        }  
    };  
    margins = {  
        top: 150,  
        bottom: 60,  
        left: 40,  
        right: 40,  
        width: 600  
    };  
    var y = 20; 
    var x = 20; 
    doc.setLineWidth(2);
    doc.setFontSize(14);  
    doc.text(250, y = y + 30,  "Payment History"); 
    doc.text(200, x = x + 50, duration);                         
    
    doc.autoTable({  
        html: '#tablePagination',  
        startY: 100,  
        theme: 'grid',  
        columnStyles: {  
            0: {  
                cellWidth: 70,  
            },  
            1: {  
                cellWidth: 70,  
            },  
            2: {  
                cellWidth: 70,  
            }  
        },  
        styles: {  
            minCellHeight: 50
        
        }  
    })  
    doc.save('Payment History.pdf');  
}  

function getPDF(){

    var HTML_Width = $(".content").width();
    var HTML_Height = $(".content").height();
    var top_left_margin = 15;
    var PDF_Width = HTML_Width+(top_left_margin*2);
    var PDF_Height = (PDF_Width*1.5)+(top_left_margin*2);
    var canvas_image_width = HTML_Width;
    var canvas_image_height = HTML_Height;

    var totalPDFPages = Math.ceil(HTML_Height/PDF_Height)-1;


    html2canvas($(".content")[0],{allowTaint:true}).then(function(canvas) {
        canvas.getContext('2d');
        
        console.log(canvas.height+"  "+canvas.width);
        
        
        var imgData = canvas.toDataURL("image/jpeg", 1.0);
        var pdf = new jsPDF('p', 'pt',  [PDF_Width, PDF_Height]);
        pdf.addImage(imgData, 'PNG', top_left_margin, top_left_margin,canvas_image_width,canvas_image_height);
        
        
        for (var i = 1; i <= totalPDFPages; i++) { 
            pdf.addPage(PDF_Width, PDF_Height);
            pdf.addImage(imgData, 'PNG', top_left_margin, -(PDF_Height*i)+(top_left_margin*4),canvas_image_width,canvas_image_height);
        }
        
        pdf.save("MyBill.pdf");
    });
    };

    function hidebutton(msg){      
        document.getElementById("btnbtn").style.display = "none";
        if(msg === ""){
            document.getElementById("btnbtn").style.display = "block";
        }
    }

    function Disable_PrevBtn(value){
        var prevbtn = document.getElementById("prevbtn");

        if(value == 0){
            prevbtn.disabled = true;
        }else{
            prevbtn.disabled = false;
        }
    }

    function Disable_NextBtn(value1,maxvalue){
        var nextbtn = document.getElementById("nextbtn");
        total = value1 + maxvalue;
        if(value1 < maxvalue){
            nextbtn.disabled = true;
        }else{
            nextbtn.disabled = false;
        }
    }


    function PendingBills(val) {  
        var doc = new jsPDF('p', 'pt', 'letter');  
        var htmlstring = '';  
        var tempVarToCheckPageHeight = 0;  
        var pageHeight = 0;  
        
        pageHeight = doc.internal.pageSize.height;  
        specialElementHandlers = {  
            // element with id of "bypass" - jQuery style selector  
            '#bypassme': function(element, renderer) {  
                // true = "handled elsewhere, bypass text extraction"  
                return true  
            }  
        };  
        margins = {  
            top: 150,  
            bottom: 60,  
            left: 40,  
            right: 40,  
            width: 600  
        };  
        const formatter = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'Php',
            minimumFractionDigits: 2
        })

        var y = 20; 
        var x = 20; 
        
        doc.setLineWidth(2);
        doc.setFontSize(14);  
        doc.text(250, y = y + 30,  "Unsettled Bills"); 
        doc.text(200, x = x + 50, val);                         
        
        doc.autoTable({  
            html: '#tablePagination',  
            startY: 100,  
            theme: 'grid',  
            columnStyles: {  
                0: {  
                    cellWidth: 70,  
                },  
                1: {  
                    cellWidth: 70,  
                },  
                2: {  
                    cellWidth: 70,  
                }  
            },  
            styles: {  
                minCellHeight: 50
            
            }  
        })  
        doc.save('Unsettled Bills.pdf');  
    }  
    
}
function toggleEnable(id) {
    var textbox = document.getElementById(id);
    
    if (textbox.disabled == true) {
        // If disabled, do this 
        document.getElementById(id).disabled = false;
    } else {
    // Enter code here
        document.getElementById(id).disabled = true;
    }
}


function paymonth(id,month){
    sessionStorage.setItem("accountid",id)
    sessionStorage.setItem("month",month)
    
}
function postmonthbill(token){
    sessionStorage.getItem("accountid")
    sessionStorage.getItem("month")
    console.log(sessionStorage.getItem("accountid"))
    console.log(sessionStorage.getItem("month"))
    var OR = document.getElementById("or_number")
    $.ajax({
        url:"/post_month_bill",
        type:"POST",
        data:{csrfmiddlewaretoken: token, id:sessionStorage.getItem("accountid"),month:sessionStorage.getItem("month"),or_number:OR.value},
        success: function() {
            location.reload(true);
          }
    });
    
}