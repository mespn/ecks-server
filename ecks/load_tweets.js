console.log ('Loading tweets');
var tweetsReq = new XMLHttpRequest ();

tweetsReq.addEventListener ('load', showTweets);

tweetsReq.open ('GET', '/api/tweet');
tweetsReq.setRequestHeader ('Accept', 'application/json');
tweetsReq.send ();

function showTweets () {
  console.log (tweetsReq.responseText);
  var tweetList = JSON.parse (tweetsReq.responseText);
  var tweetDiv = getElementById ('results');
  tweetDiv.innerHTML = '<ul>';

  tweetList.forEach (tweet => {
    tweetDiv.innerHTML +=
      '<li>' + tweet.author + ' said ' + tweet.content + '<li>';
  });

  tweetDiv.innerHTML += '</ul>';
}
