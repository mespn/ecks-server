function doneBeenClicked () {
  // this is a closure, gets variables
  // from method it is in
  function loadedEventCallback () {
    var ip = oReq.responseText;
    var asObj = JSON.parse (ip);
    var theDiv = document.getElementById ('fillHere');
    ipAddresses.push (asObj['REMOTE_ADDR']);
    //theDiv.innerText = "You are " + asObj['REMOTE_ADDR'];
    var output = '<table>\n';
    for (let i = 0; i < ipAddresses.length; i++) {
      output += '<tr><td>' + ipAddresses[i] + '</td></tr>\n';
    }
    output += '</table>\n';
    theDiv.innerHTML = output;

    var otherDiv = document.getElementById ('topData');
    otherDiv.innerText = '';
  }

  function loadedEventCallback2 () {
    var theDiv = document.getElementById ('fillHere');
    theDiv.innerText = 'I was done clicked';
  }

  // basis from
  // https://developer.mozilla.org/en-US/docs/Web/API/XMLHttpRequest/Using_XMLHttpRequest
  // probably will not work from localhost!
  var oReq = new XMLHttpRequest ();
  oReq.addEventListener ('load', loadedEventCallback);
  // We want to get the IP address, but I don't want to talk too much about CORS!
  oReq.open ('GET', '/~robg/cgi-bin/3010/get_ip.cgi');
  // hey, we can do this, but don't have to (in this case)
  oReq.setRequestHeader ('Accept', 'application/json');
  oReq.send ();
}
