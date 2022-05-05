'''
Websockets sample for FastAPI
FastAPI handles both Websockets routes (via Starlette wrapper) and HTML responses
'''

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from connections import manager

app = FastAPI()

# FOR LOCAL TESTING ONLY
# Update websockets url to wss://<app-name>.azurewebsites.net/ws
html = """
<h1>Real Time Messaging</h1>
<pre id="messages" style="height: 400px; overflow: scroll"></pre>
<input type="text" id="messageBox" placeholder="Type your message here" style="display: block; width: 100%; margin-bottom: 10px; padding: 10px;" />
<button id="send" title="Send Message!" style="width: 100%; height: 30px;">Send Message</button>

<script>
  (function() {
    const sendBtn = document.querySelector('#send');
    const messages = document.querySelector('#messages');
    const messageBox = document.querySelector('#messageBox');

    let ws;

    function showMessage(message) {
      messages.textContent += `\n\n${message}`;
      messages.scrollTop = messages.scrollHeight;
      messageBox.value = '';
    }

    function init() {
      if (ws) {
        ws.onerror = ws.onopen = ws.onclose = null;
        ws.close();
      }

      ws = new WebSocket('wss://fastapi-websockets-sample.azurewebsites.net/ws');
      ws.onopen = () => {
        console.log('Connection opened!');
      }
      ws.onmessage = ({ data }) => showMessage(data);
      ws.onclose = function() {
        ws = null;
      }
      ws.onerror = function(error) {
        console.log(error);
      }
    }

    sendBtn.onclick = function() {
      if (!ws) {
        showMessage("No WebSocket connection :(");
        return ;
      }

      ws.send(messageBox.value);
    }

    init();
  })();
</script>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print(websocket.url.path)
    print(websocket.url.port)
    print(websocket.url.scheme)

    await manager.connect(websocket)
    while True:
        try:
          data = await websocket.receive_text()
          await manager.broadcast({data})
        except Exception as e:
          print('error: ', e)
          break
        