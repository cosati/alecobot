// Receiving data from Raspberry
let lightauto = false
var keys = {
  'w': false,
}

function requestData() {
  var requests = $.get('/data_feed');
  var tm = requests.done(function (result) {
    console.log("JSON", result);

    // Initializing
    switch(result.init) {
      case -1:
        console.log("No data from arduino");
        $('#information').html("No data...");
        $('#information').removeClass().addClass("nosignal")
        break;
      case 1:
        console.log("Calibrating ESCs");
        $('#information').html("Calibrating...");
        $('#information').removeClass().removeClass("nosignal");
        break;
      default:
        console.log("Ok");
        $('#information').html("Ok");
        $('#information').removeClass().removeClass("nosignal");
    }
    $('#information').html(result.init == 1 ? "Calibrating..." : "")

    // Updating Sensors status
    $('#rear').html(result.rear == 1 ? "-" : "Stop!").removeClass().addClass(result.rear == 1 ? "" : "redalert");
    $('#front').html(result.front == 0 ? "Go" : "Stop!").removeClass().addClass(result.front == 0 ? "" : "redalert");
    $('#distance').html(result.distance == -1 ? "No data" : result.distance + "cm").removeClass().addClass(result.distance == -1 ? "nosignal" : "");
    $('#light').html(result.light == -1 ? "No data" : result.light + '%').removeClass().addClass(result.light == -1 ? "nosignal" : "");
    $('#leftmotor').html(result.lm == -1 ? "No data" : result.lm + '%').removeClass();
    $('#rightmotor').html(result.rm == -1 ? "No data" : result.rm + '%').removeClass();

    // Sliders value
    if (lightauto) {
      $('#redslider').val(result.autolight);
      $('#greenslider').val(result.autolight);
      $('#blueslider').val(result.autolight);
    } 

    setTimeout(requestData, 500);
  });
}

$(document).ready(function() {
  requestData();

  //Lights auto or manual
  $('#lightmode').on('click', function(){  ///ledsmode/<value>          
    if($(this).is(':checked')){
      $('#redslider').attr('disabled', true);
      $('#greenslider').attr('disabled', true);
      $('#blueslider').attr('disabled', true);
      $.get('/ledsmode/auto');
      lightauto = true
    } else {
      $('#redslider').attr('disabled', false);
      $('#greenslider').attr('disabled', false);
      $('#blueslider').attr('disabled', false);
      $.get('/ledsmode/man');
      lightauto = false
    }
  });

  // Pilot mode | auto, manual, stop
  $('input[type=radio][name=mode]').change(function() {
    if (this.value == 1) { // Manual
      console.log("Changed to manual");
      $.get('/pilot/manual');
    }
    else if (this.value == 2) { // Auto
      console.log("Changed to autopilot");
      $.get('/pilot/auto');
    }
    else { // Stop
      console.log("Stopped");
      $.get('/pilot/stop');
    }
  });

  // Setting leds intensity
  $('.rgbslider').on('change', function() {
    if (!lightauto) {
      let s = $(this).attr('id');
      let v = $(this).val();
      let p = '/' + s + '/' + v;
      console.log(p);
      $.get(p);
    };
  });

});

document.addEventListener("keydown", function(e) {
  let k = e.key;

  if (!keys[k]) {
    keys[k] = true;
    let p = '/keydown/' + k;
    console.log(p);
    $.get(p);
  }

});

document.addEventListener("keyup", function(e) {
  let k = e.key;

  keys[k] = false;
  let p = '/keyup/' + k;
  console.log(p);
  $.get(p);

});