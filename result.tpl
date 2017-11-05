<html>
<head>
    <style>
      .login {
      position: absolute;
      top: 10px;
      right: 12px;
      font-size: 20px;
      }
      .profile {
        position: absolute;
        top: 10px;
        right: 12px;
        text-align: center;
        vertical-align: middle
      }
      #profileImg {
        width: 46px;
        height: 44px;   
      }
      .profile img font {
        display: inline;
        float: none;
      }
    </style>
  </head>
<body>

  <form action="/result">
    <input type="submit" value="Go to home page" />
  </form>

  <p>Search for "{{searchedKeywords}}"</p>

  <table id=”results”>
    <tr>
      <td><b>Word</b></td>
      <td><b>Count</b></td>
    </tr>

    %i = 0
    %for word in localKeywords:
    <tr>
      <td>{{word}}</td>
      <td>{{localCount[i]}}</td>
      %i = i+1
    </tr>
    %end
  </table>

  %if loggin:
    <div class="profile">
        <img src={{userInfo["picture"]}} id="profileImg"/>
        <br>
        <font size='3'>{{userInfo["name"]}}</font>

        <form action="\logout">
          <input type="submit" value="Logout">
        </form>
      </div>
    %end
</body>

</html>
