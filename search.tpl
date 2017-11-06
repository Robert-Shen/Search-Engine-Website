<!DOCTYPE html>
<html lang="en">

  <head>
  <title>searchpage</title>
	<meta charset="utf-8">
	<link rel="stylesheet" type="text/css" href="search.css"/>
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
 <div class="content">
     %for n in srch:
     <a href={{n[0]}}>{{n[1]}}</a>
     <cite>{{n[0]}}</cite>
     %end
     %if not srch:
     <p>Oops, nothing is found...</p>
     %end
 <div class="index">
     <form action="/" method="get">
         <input type="hidden" name="keywords" value={{keywords}}>
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
 </div>

 </body>

