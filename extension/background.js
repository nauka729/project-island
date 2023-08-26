let attachedTabId;

chrome.runtime.onMessage.addListener(function(message, sender, sendResponse) {
  if (message.action === 'start' && message.tabId) {
    attachedTabId = message.tabId;
    chrome.debugger.attach({tabId: attachedTabId}, '1.2', function() {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError);
        return;
      }
      chrome.debugger.sendCommand({tabId: attachedTabId}, "Network.enable");
      chrome.debugger.onEvent.addListener(debuggerEventHandler);
    });
  } else if (message.action === 'stop' && attachedTabId) {
    chrome.debugger.detach({tabId: attachedTabId});
  }
});




function debuggerEventHandler(debuggeeId, message, params) {
    if (attachedTabId !== debuggeeId.tabId) {
      return;
    }
  
    if (message === 'Network.webSocketFrameReceived') {
      const data = params.response.payloadData;
      if (data.startsWith('{"auctions":{"show":{"offers":')) {
        if (data.startsWith('{"auctions":{"show":{"offers":[]')) {
            // miss the first message  
          }
        else{
            console.log('WebSocket Frame:', data);}
            fetch('http://island.com/api/v1/send_items_json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                    // using different content type, as this was initially set up to handle "form" request.
                },
                // it was sending the "message" the whole time, not the data "variable"
                body: `jsonInput=${encodeURIComponent(data)}`
            })
            .then(response => response.text())
            .then(result => {
                console.log("Response from Flask:", result);
            })
            .catch(error => {
                console.error("Error sending message:", error);
            });
        
      }
    }
  }
  
