$(function(){
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