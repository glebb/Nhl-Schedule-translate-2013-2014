var update = function() {
  $.getJSON($SCRIPT_ROOT + '/_get_schedule', {
    TARGET_TIMEZONE : $('#timezone').val(),
    START_FROM : $('#start').val(),
    END_BY : $('#end').val(),
    TEAM_FILTER : $('#team').val(),
    FILTER_TIME : $('#time').is(':checked')
  }, function(data) {
      $("#result").empty();
      if(typeof data.games === 'undefined') return;
      for (index = 0; index < data.games.length; ++index) {
        var str = data.games[index].target_time;
          tagline = data.games[index].home_team + ' vs ' + data.games[index].visiting_team;
          str = str + ' ' + tagline
          str = str + ' <a href="_get_ical?tagline=' 
            + tagline + '&time=' + data.games[index].target_time 
            + '&timezone=' + $('#timezone').val() + '">ic</a>'

            listItem = jQuery('<li />', {
            });
            listItem.append(str);
            wd = data.games[index].weekday;
            
            if (!$('#time').is(':checked') && data.games[index].weekend == true) {
              listItem.addClass("weekend")
            }
            
          $("#result").append(listItem);
      }
  });
  return false;
}


$(function() {
  $('button#submit').bind('click', update);
  update();
  $('#time').change(function() {
      $('#start').attr('disabled',! this.checked)
      $('#end').attr('disabled',! this.checked)      
  });
});



