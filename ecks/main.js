function setUp () {
  // this is a closure, gets variables
  // from method it is in
  function loadedEventCallback () {
    if (oReq.status == 401) {
      var loginReq = new XMLHttpRequest ();
      loginReq.addEventListener ('load', () => {
        var theDiv = document.getElementById ('fill-here');
        theDiv.innerHTML = loginReq.responseText;
      });

      loginReq.open ('GET', '/login.html');
      loginReq.send ();
    } else {
      console.log ('trying to get tweets');
      var mainPageReq = new XMLHttpRequest ();

      mainPageReq.addEventListener ('load', () => {
        var theDiv = document.getElementById ('fill-here');

        theDiv.innerHTML = mainPageReq.responseText;

        var tweetsReq = new XMLHttpRequest ();

        tweetsReq.addEventListener ('load', showTweets);

        tweetsReq.open ('GET', '/api/tweet');
        tweetsReq.setRequestHeader ('Accept', 'application/json');
        tweetsReq.send ();

        function showTweets () {
          var tweetList = JSON.parse (tweetsReq.responseText);
          var tweetDiv = getElementById ('results');
          tweetDiv.innerHTML = '<ul>';

          tweetList.forEach (tweet => {
            tweetDiv.innerHTML +=
              '<li>' + tweet.author + ' said ' + tweet.content + '<li>';
          });

          tweetDiv.innerHTML += '</ul>';
        }
      });
    }

    mainPageReq.open ('GET', '/tweets.html');
    mainPageReq.send ();
  }

  // basis from
  // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Using_XMLHttpRequest
  // probably will not work from localhost!
  var oReq = new XMLHttpRequest ();
  oReq.addEventListener ('load', loadedEventCallback);
  oReq.open ('GET', '/api/tweets');
  oReq.send ();
}

function login () {
  var loginReq = new XMLHttpRequest ();
  var tbox = document.getElementById ('username-textbox');

  loginReq.addEventListener ('load', setUp);
  loginReq.open ('POST', '/api/login');
  loginReq.send ('username=' + tbox.value);
}

function post_tweet () {
  console.log ('Posting tweet: \n');
  t_content = document.getElementById ('new-tweet').value;
  console.log (t_content);
}
