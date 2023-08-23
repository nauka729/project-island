document.getElementById('start').onclick = function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const currentTab = tabs[0];
      chrome.runtime.sendMessage({action: "start", tabId: currentTab.id});
    });
  }
  
  document.getElementById('stop').onclick = function() {
    chrome.runtime.sendMessage({action: "stop"});
  }
  