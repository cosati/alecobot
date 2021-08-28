// Receiving data from Raspberry
let lightauto = false

function requestData() {
  var requests = $.get('/data_feed');
  var tm = requests.done(function (result) {
    console.log("JSON", result);

    // Initializing
    $('#information').html(result.init == 1 ? "Calibrating..." : "")

    // IR Rear Status
    $('#rear').html(result.rear == 1 ? "-" : "Stop!").removeClass(result.rear == 1 ? "redalert" : "").addClass(result.rear == 1 ? "" : "redalert");

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

});