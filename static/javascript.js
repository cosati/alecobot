/*$(function(){
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
});*/
let rearIR = 1


function requestData() {
  var requests = $.get('/data_feed');
  var tm = requests.done(function (result) {
    console.log("REAR", result.rear);
    
    // if (rearIR != result.rear) {
    //   rearIR = result.rear // updates variable with new value
    //   // Update HTML
    //   $('#rear').html(rearIR = 1 ? "-" : "Stop!");
    // }
    $('#rear').html(result.rear = 1 ? "-" : "Stop!");

    setTimeout(requestData, 500);
  });
}

$(document).ready(function() {
  requestData();
});

/*var slider = document.getElementById("myRange");
var output = document.getElementById("demo");
output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
  output.innerHTML = this.value;
}*/