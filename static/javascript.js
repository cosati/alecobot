// Receiving data from Raspberry
function requestData() {
  var requests = $.get('/data_feed');
  var tm = requests.done(function (result) {
    console.log("JSON", result);

    // IR Rear Status
    $('#rear').html(result.rear == 1 ? "-" : "Stop!").removeClass(result.rear == 1 ? "redalert" : "").addClass(result.rear == 1 ? "" : "redalert");

    // Sliders value
    $('#redslider').val(result.sliderr);
    $('#redslideg').val(result.sliderg);
    $('#redslideb').val(result.sliderb);

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
    } else {
        $('#redslider').attr('disabled', false);
        $('#greenslider').attr('disabled', false);
        $('#blueslider').attr('disabled', false);
    }
  });

});

/*var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
}*/