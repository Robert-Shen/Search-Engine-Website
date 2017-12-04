<!DOCTYPE html>
<html lang="en">

  <head>
  <title>searchpage</title>
	<meta charset="utf-8">
	<script src="https://ajax.googleapis.com/ajax/libs/jquery/2.1.3/jquery.min.js"></script>
  <script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.11.3/jquery-ui.min.js"></script>
  <script src="autocomplete.js"></script>
  <link rel="stylesheet" type="text/css" href="search.css"/>
  <link rel="stylesheet" type="text/css" href="jquery-ui.css"/>
  </head>
<body>
  <div class="header">
      <form action="/result" method="get">
      <div class="logo">
        <input type="image" src="logo.gif" alt="Supported by BigBroEngine" width="84" height="84" style="outline:None;">
      </div>
      </form>
      <form action="/" method="get">
      <div class="search">
        <input class="textbox" name="keywords" type="text" spellcheck="false" maxlength="2048" placeholder="What are you looking for?" required>
        <input type="hidden" name="page_no" value="1">
        <div class="texts" id="srch-result" style="margin-top: 44px;margin-left: 1px;"></div>
        <input type="image" src="mgf.png" class="mag" width="24" height="24">
      </div>
      </form>
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
 %if keywords != key_sug:
     <div class="sug">
     <p class = "suggest">
      <span class = "spell">Showing result for</span>
      <a class ="spell" href="/?keywords={{"+".join(key_sug.split())}}&page_no=1&origin=1">{{key_sug}}</a>
      <br>
      <span class = "spell_orig">Search instead for</span>
      <a class ="spell_orig" href="/?keywords={{"+".join(keywords.split())}}&page_no=1&origin=1">{{keywords}}</a>     
      <br>
      </p>
      </div>
      %end
 <div class="content">
     %for n in srch:
     <a href={{n[0]}}>{{n[1]}}</a>
     <cite>{{n[0]}}</cite>
     <p class="snippet">{{n[2]}}</p>
     %end
     %if not srch:
     <p style="margin-left:30px;">Oops, nothing is found...</p>
     %end

 </div>
 <div class="index">
     <form action="/" method="get">
         <input type="hidden" name="keywords" value={{key_sug}}>
          <input type="hidden" name="origin" value=1>
         <div class="pagination">
             %if currentpage is not 1:
             <button type="submit" name="page_no" value={{currentpage-1}}>&laquo</button>
             %end
             %for info in pgn:
             <button type="submit" class={{info[0]}} name="page_no" value={{info[1]}}>{{info[1]}}</button>
             %end
             %if currentpage is not maxpage:
             <button type="submit" name="page_no"  value={{currentpage+1}}>&raquo</button>
             %end
         </div>
     </form>
 </div>
 </body>
