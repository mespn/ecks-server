function setUp () {
  // this is a closure, gets variables
  // from method it is in
  function loadedEventCallback () {
    if (oReq.status == 401) {
      showLoginPage ();
    } else {
      var theDiv = document.getElementById ('fill-here');
      theDiv.innerHTML = oReq.responseText;
    }
  }

  // basis from
  // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Using_XMLHttpRequest
  // probably will not work from localhost!
  var oReq = new XMLHttpRequest ();
  oReq.addEventListener ('load', loadedEventCallback);
  oReq.open ('GET', '/tweets.html');
  oReq.send ();
}

function loadTweets () {
  console.log ('Loading tweets');
  var tweetsReq = new XMLHttpRequest ();

  tweetsReq.addEventListener ('load', showTweets);

  tweetsReq.open ('GET', '/api/tweet');
  tweetsReq.send ();

  function showTweets () {
    var postBox = document.getElementById ('new-tweet');
    postBox.value = '';
    var tweetDiv = document.getElementById ('results');
    if (tweetsReq.status == 401) showLoginPage ();
    else if (tweetsReq.status == 200) {
      var tweetList = JSON.parse (tweetsReq.responseText);

      function tweet_item (id, tweet_object) {
        auth = tweet_object.author;
        cont = tweet_object.content;

        gen_div = `<li class = "tweet" id = ${id}> <div class="tweet-item">
        <div class="tweet-info tweet-element">
        <div class= "tweet-author">${auth}</div> 
        
        <div class = "tweet-content"><input class="tweet-txtbx" value = "${cont}"></div> 
        </div>
        ${updater_button ()}
        </div>
        </li>`;
        return gen_div;
      }

      function updater_button () {
        return `<div class = "tweet-element" ><button class="updater" onclick=update_tweet(this.parentNode.getAttribute("id"))>
        Update
        </button></div>`;
      }

      tweetDiv.innerHTML = '<h2> Tweets </h2>';

      if (Object.keys (tweetList).length == 0) {
        tweetDiv.innerHTML +=
          '<p>There are no tweets here.</p> <p>Post the very first tweet!</p>';
      } else {
        tweetDiv.innerHTML += '<ul>';

        for (i in tweetList) {
          tweetDiv.innerHTML += tweet_item (i, tweetList[i]);
        }

        tweetDiv.innerHTML += '</ul>';
      }
    } else {
      tweetDiv.innerText = 'Could not get tweets';
    }
  }
}

function showLoginPage () {
  console.log ('Showing login page...');
  var loginReq = new XMLHttpRequest ();
  loginReq.addEventListener ('load', () => {
    var theDiv = document.getElementById ('fill-here');
    theDiv.innerHTML = loginReq.responseText;
  });

  loginReq.open ('GET', '/login.html');
  loginReq.send ();
}

function login () {
  var loginReq = new XMLHttpRequest ();
  var tbox = document.getElementById ('username-textbox');

  loginReq.addEventListener ('load', setUp);
  loginReq.open ('POST', '/api/login');
  loginReq.send ('username=' + tbox.value);
}

function post_tweet () {
  var tweet_poster = new XMLHttpRequest ();

  function confirm_posting () {
    textbox.value = '';
    if (tweet_poster.status == 401) {
      showLoginPage ();
    } else {
      if (JSON.parse (tweet_poster.responseText).success) {
        console.log ('Tweet Posted');
        loadTweets ();
      } else {
        console.log ("Couldn't post tweet");
      }
    }
  }

  tweet_poster.addEventListener ('load', confirm_posting);

  tweet_poster.open ('POST', 'api/tweet');
  console.log ('Sent POST request');
  textbox = document.getElementById ('new-tweet');
  tweet = {Content: textbox.value};
  tweet_poster.send (JSON.stringify (tweet));
}

function update_tweet (id) {
  console.log ('updating tweet ', id);
  var update_req = new XMLHttpRequest ();

  update_req.addEventListener ('load', () => {
    console.log ('update_req status is', update_req.status);
    if (update_req.status == 401) {
      showLoginPage ();
    } else if (update_req.status == 200) {
      console.log ('update successful');
      loadTweets ();
    } else {
      console.log ('Something went wrong while updating tweet');
    }
  });

  new_val = {
    Content: document
      .getElementById (id)
      .getElementsByClassName ('tweet-content')[0].firstChild.value,
  };

  update_req.open ('PUT', `/api/tweet/${id}`);
  console.log ('New_val=', new_val);
  update_req.send (JSON.stringify (new_val));
}
