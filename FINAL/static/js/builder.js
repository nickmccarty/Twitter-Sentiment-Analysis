$(document).ready(function() {

     $('button[name=formSubmit]').click(function() {
        var form_button = document.getElementById('spinner');
        form_button.innerHTML =  '<div id="mapSpin" style="margin:14em" class="text-center"><div class="spinner-grow text-light" role="status"><span class="sr-only">Loading...</span></div></div>';
  });
}); // end document.ready
