function compute_transformation(){
  //Code angepasst von : https://codepen.io/hilotacker/pen/ONZWoX
  listItems = document.querySelectorAll('li');
  var r = 112 //Bestimmt die Größe von dem Kreis

  for (i=0; i < listItems.length; i++) {
    //Die 100 steht für die Anzahl der Listenelemente
    var angle = 450 + (360 / 60) * (i + 1);
    angle = String(angle) + "deg";
    var radian =  (360 / 60) * (Math.PI/180) * (i + 1);
    var x = r * Math.cos(radian);
    x = String(x) + "px";
    var y = r * Math.sin(radian);
    y = String(y) + "px";
    var transformation = "translate(" + x + "," +y+") rotate(" + angle + ")";
    listItems[i].style.transform = transformation;
  }
}

function nameListElements() {
  listItems = document.querySelectorAll('li');
    for (i=0; i < listItems.length; i++) {
      list_item_id = "listitem" + String(i);
      listItems[i].setAttribute('id', list_item_id);
  }
}

compute_transformation();
nameListElements();

//code from: https://stackoverflow.com/questions/5517597/plain-count-up-timer-in-javascript
var minutesLabel = document.getElementById("minutes");
var secondsLabel = document.getElementById("seconds");
var totalSeconds = 0;
var counter = 0;
setInterval(setTime, 1000);

function setTime() {
  ++totalSeconds;
  //console.log(totalSeconds);
  secondsLabel.innerHTML = pad(totalSeconds % 60);
  minutesLabel.innerHTML = pad(parseInt(totalSeconds / 60));
  if (totalSeconds < 61){
    var target_item = document.getElementById('listitem' + String((44 + counter) % 60));
    //console.log(target_item);
    target_item.style.background = "#08DEDE";
    ++counter;
  }
}

function pad(val) {
  var valString = val + "";
  if (valString.length < 2) {
    return "0" + valString;
  } else {
    return valString;
  }
}




/*(function($,doc,win){
  //Variables
  var hour = $('#hr');
  var min = $('#min');
  var sec = $('#sec');
  var liNum = 75;
  var flip = false;
  var intervalCounter = 0;
  //Buttons
  var btnStartStop = $('#btn-start-stop');
  var labelStartStop = $('#label-start-stop');
  var btnReset = $('#btn-reset');
  //Elements for Animations
  var icnClockLine = $('#icn-clock-line');
  var icnClockLineDeg = 180;
  var clockLines = $('.clockline').find('li');
  var clockLines_arr = [];
    for (var i = 0; i < clockLines.length; i++) {
        clockLines_arr.push(clockLines[i]);
    }
  //Time
  var currentTime = 0;
  //States
  var stop = true;
  //Method
  var sWatchMethod ={
    timer: function(){
      var interval = 10;
      time = setInterval(function() {
                intervalCounter +=interval;
                if (!stop) {
                 
                  if((intervalCounter%1000)==0){
                    currentTime += 1000;
                    var appendHour = currentTime / (1000 * 60 * 60) | 0; 
                    var appendMinute = currentTime % (1000 * 60 * 60) / (1000 * 60) | 0;
                    var appendSecond = currentTime  % (1000 * 60) / 1000 | 0;
                  
                    appendHour = appendHour < 10 ? "0" + appendHour : appendHour;
                    appendMinute = appendMinute < 10 ? "0" + appendMinute : appendMinute;
                    appendSecond = appendSecond < 10 ? "0" + appendSecond : appendSecond;
                    hour.html(appendHour);
min.html(appendMinute);
sec.html(appendSecond);
        
                    }
                  
                  //------
                  
                    var target = $('#clockline li').eq(liNum);
          
                    if(!flip){
                    target.css('background','#339dac');
                    }else{
                      target.css('background','#fff');
                    }
                    
                    liNum += 1;
                    if(liNum>100){
                      liNum=0;
                    }
                    if(liNum ==75){
                      flip =!flip;
                    }
                }

            }, 10); 
    },
    startAndStop: function(){

      $('#btn-start-stop .stop-watch').addClass('sw-click');
      setTimeout(function(){
        $('#btn-start-stop .stop-watch').removeClass('sw-click');
      },200);
      stop = !stop;
      if(!stop){
      labelStartStop.html('STOP');
        if(!intervalCounter){
         sWatchMethod.timer();
        }
      }else{ 
     
      labelStartStop.html('START');
      //clearInterval(time);
      //clearInterval(time2);
      }
      
      
      btnReset.css('opacity',1);
      $('.btn-reset .bl-parts').css('transition','transform 0s');
      btnReset.removeClass('br-click');
      setTimeout(function(){
      $('.btn-reset .bl-parts').css('transition','transform 0.5s');
        },200);
    },
    reset: function(){
      if(!stop){
        stop = !stop;
        labelStartStop.html('START');
      }
      clearInterval(time);
      if(intervalCounter){
      currentTime = 0;
      intervalCounter = 0;
      hour.html("00");
      min.html("00");
      sec.html("00");
      liNum = 75;
      flip = false;
      for (var i = 0; i < clockLines.length; i++) {
        $('#clockline li').eq(i).css('background','#fff');
      }
      
      $(this).css('opacity',0.5);
      $(this).addClass('br-click');
      }
    },
    init: function(){
      btnStartStop.on('click',sWatchMethod.startAndStop);
      btnReset.on('click',sWatchMethod.reset); 
    }
  }
  
  $(document).ready(sWatchMethod.init);
  }(jQuery,document,window));*/