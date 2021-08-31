// Receiving data from Raspberry
let lightauto = false

function requestData() {
  var requests = $.get('/data_feed');
  var tm = requests.done(function (result) {
    console.log("JSON", result);

    // Initializing
    switch(result.init) {
      case -1:
        console.log("No data from arduino");
        $('#information').html("No data...");
        $('#information').removeClass("redalert").addClass("nosignal")
      case 1:
        console.log("Calibrating ESCs");
        $('#information').html("Calibrating...");
        $('#information').removeClass("redalert").removeClass("nosignal");
      default:
        console.log("Ok");
        $('#information').html("Ok");
        $('#information').removeClass("redalert").removeClass("nosignal");
    }
    $('#information').html(result.init == 1 ? "Calibrating..." : "")

    // Updating Sensors status
    $('#rear').html(result.rear == 1 ? "-" : "Stop!").removeClass(result.rear == 1 ? "redalert" : "").addClass(result.rear == 1 ? "" : "redalert");
    $('#front').html(result.front == 0 ? "Go" : "Stop!").removeClass(result.front == 0 ? "redalert" : "").addClass(result.front == 0 ? "" : "redalert");
    $('#distance').html(result.distance == -1 ? "No data" : result.distance + "cm").removeClass(result.distance != -1 ? "nosignal" : "").addClass(result.distance == -1 ? "" : "nosignal");
    $('#light').html(result.light == -1 ? "No data" : result.light + '%').removeClass(result.light != -1 ? "nosignal" : "").addClass(result.light == -1 ? "" : "nosignal");

    // Sliders value
    if (lightauto) {
      $('#redslider').val(result.sliderr);
      $('#greenslider').val(result.sliderg);
      $('#blueslider').val(result.sliderb);
    }

    setTimeout(requestData, 500);
  });
}

$(document).ready(function() {
  requestData();

  //Lights auto or manual
  $('#lightmode').on('click', function(){           
    if($(this).is(':checked')){
      $('#redslider').attr('disabled', true);
      $('#greenslider').attr('disabled', true);
      $('#blueslider').attr('disabled', true);
      lightauto = true
    } else {
      $('#redslider').attr('disabled', false);
      $('#greenslider').attr('disabled', false);
      $('#blueslider').attr('disabled', false);
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