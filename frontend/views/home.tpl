<!DOCTYPE html>
<html lang="en">

  <head>
  <title>homepage</title>
	<meta charset="utf-8"> 
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.3/jquery-ui.min.js"></script>
  <script src="autocomplete.js"></script>    
	<link rel="stylesheet" type="text/css" href="home.css"/>
  <link rel="stylesheet" type="text/css" href="jquery-ui.css"/>
  </head>

  <body>
    <div class="header">

      %if not loggin:
      <div class="header2">
      <form action="/login">
          <input class="login" type="submit" value="Login">
      </form>
      </div>
      %end
       %if loggin:
      <div class="header1">
        <img src={{userInfo['picture']}} width="46px" height="44px">
      </div>
       <div class="header2">
      <form action="/logout">
          <input class="login" type="submit" value="Logout">
      </form>
      </div>
      <div class="header3">
        <p>{{userInfo['user']}}</p>
      </div>
    %end
    </div>
    <div class="content">
        <div class="img">
        <img src="https://media.giphy.com/media/goCaAHqHS0lDW/giphy.gif" alt="Supported by BigBroEngine" width="256" height="256">
        </div>
    <form action="/" method="get">
        <div class="search">
            <input class="textbox" name="keywords" type="text" spellcheck="false" maxlength="2048" placeholder="What are you looking for?" required>
            <input type="hidden" name="page_no" value="1">
            <input class="button" type="submit" value="Search">
        </div>
       <div class="texts" id="srch-result"></div>

    </form>
    </div>
    
    %if popularKeywords is not None:
      %listLength = len(popularKeywords)
      <table id=”history”>
        <tr>
          <td><b>Word</b></td>
          <td><b>Count</b></td>
        </tr>

        %for i in range(0,20):
          %if i >= listLength:
            %break
          %end

          <tr>
            <td>{{popularKeywords[i][0]}}</td>
            <td>{{popularKeywords[i][1]}}</td>
          </tr>
        %end
      </table>
    %end

  </body>

</html>
