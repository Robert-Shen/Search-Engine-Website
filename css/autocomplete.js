$(function() { last_req = "";
$( ".textbox" ).autocomplete({
  minLength: 3,
  delay: 50,
  appendTo: '#srch-result',
  select: function(event, ui) {
      $( ".textbox" ).val(ui.item.value);
  },
  source: function( request, response ) {
      $.ajax({ dataType: "json", type : 'Get',
      url: 'https://api.datamuse.com/sug?s=' + encodeURIComponent(request.term),
        success: function(data) { response( $.map( data, function(item) { return item["word"]; })) }, });
      last_req = request.term; }
  }); });