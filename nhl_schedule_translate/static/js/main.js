var update = function() {
  $.getJSON($SCRIPT_ROOT + '_get_schedule', {
    TARGET_TIMEZONE : $('#timezone').val(),
    START_FROM : $('#start').val(),
    END_BY : $('#end').val(),
    TEAM_FILTER : $('#team').val(),
    FILTER_TIME : $('#time').is(':checked')
  }, function(data) {
      $("#result").empty();
      if(typeof data.games === 'undefined') return;
      for (index = 0; index < data.games.length; ++index) {
        if (data.games[index].inPast && $('#excludePastGames').is(':checked') )
        {
          continue;
        }

        var str = data.games[index].target_time;

        tagline = data.games[index].home_team + ' vs ' + data.games[index].visiting_team;
        str = str + ' ' + tagline
        if (!data.games[index].inPast)
        {
          str = str + ' <a href="_get_ical?tagline=' 
            + tagline + '&time=' + data.games[index].target_time 
            + '&timezone=' + $('#timezone').val() + '">ic</a>'
        }

        listItem = jQuery('<li />', {
        });
        listItem.append(str);
        wd = data.games[index].weekday;
        
        if (data.games[index].weekend) {
          listItem.addClass("weekend")
        }
        
        $("#result").append(listItem);
          
      }
  });
  return false;
}


$(function() {
  if (!$.cookie('excludePastGames')) {
    $.cookie('excludePastGames', "true", { expires: 365 });    
  }
  
  checked = ( $.cookie('excludePastGames')) == "true";
  $( "#excludePastGames" ).attr('checked', checked);
  $('#start').attr('disabled', !$('#time').attr('checked'))
  $('#end').attr('disabled', !$('#time').attr('checked'))
  
  update();

  $('#time').change(function() {
      $('#start').attr('disabled', !this.checked)
      $('#end').attr('disabled', !this.checked)
      update();      
  });

  $( "#excludePastGames" ).change(function() {
    $.cookie('excludePastGames', this.checked, { expires: 365 });
    update();
  });
  
  $('button#submit').bind('click', update);
  $( "#team" ).change(update);
  $( "#timezone" ).change(update);
  $( "#start" ).change(update);
  $( "#end" ).change(update);
});

$(document).ajaxStart(function(){
  $("#result").hide();
  $("#loading").show();
}).ajaxStop(function(){
  $("#loading").hide();
  $("#result").show();
});


