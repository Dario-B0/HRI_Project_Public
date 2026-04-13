// log display function
function append(text) {
  // document.getElementById("websocket_events").insertAdjacentHTML('beforeend', "<li>" + text + ";</li>");
  console.log(text);
} 

// websocket global variable
var websocket = null;

function wsrobot_connected() {
  var connected = false;
  if (websocket!=null)
    console.log("websocket.readyState: "+websocket.readyState)
  if (websocket!=null && websocket.readyState==1) {
    connected = true;
  }
  console.log("connected: "+connected)
  return connected;
}

function wsrobot_init(ip, port) {
    var url = "ws://"+ip+":"+port+"/modimwebsocketserver";
    console.log(url);
    websocket = new WebSocket(url);

    websocket.onmessage = function(event) {
        console.log("message received: "+event.data);
        v = event.data.split('_');
        
        if (v[0]=='display') {
          if (v[1]=='text'){
            if (v[3]=="cycles"){
              if (v[4]=="show"){
                counterElement = document.getElementById('cycle-counter');
                current = v[5];
                total = v[6];
                document.getElementById('current-cycles').textContent = current;
                document.getElementById('total-cycles').textContent = total;
                counterElement.style.visibility = "visible";
              }
              else if (v[4]=="hide"){
                counterElement = document.getElementById('cycle-counter');
                counterElement.style.visibility = "hidden";
              }
            }
            else if (v[3]=="schedule"){

              if (v[4] != "reset"){
                document.getElementById("image_default").style.visibility = "hidden";
                document.getElementById("image_default").src = "";

                const eventsString = v[5];

                // Fix single quotes
                let fixedQuotes = eventsString.replace(/'/g, '"');

                // Optional: Fix invalid times (this part requires custom logic)
                let events = JSON.parse(fixedQuotes).filter(e => e[4] >= 0 && e[4] < 24);
                
                const scheduleEl = document.getElementById("schedule");

                const today = new Date();
                // const targetDay = [today.getFullYear(), today.getMonth(), today.getDate()];
                targetDay = [2025, 4, 10]

                let selectedEvents = 0;
                // Today
              
                if (v[4] == "daily"){
                  selectedEvents = events
                    .filter(([_, y, m, d]) => y === targetDay[0] && m === targetDay[1] && d === targetDay[2])    
                }

                // This week
                else if (v[4] == "weekly") {
                  selectedEvents = events
                    .filter(([_, y, m, d]) => y === targetDay[0] && m === targetDay[1] && d >= targetDay[2] && d < (targetDay[2] + 7))
                }

                // Complete
                else {
                  selectedEvents = events
                }


                selectedEvents.forEach(([name, year, month, day, hour, minute]) => {
                    const timeStr = `${String(year)}/${String(month).padStart(2, '0')}/${String(day).padStart(2, '0')}  ${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
                    const eventEl = document.createElement("div");
                    eventEl.className = "event";
                    eventEl.innerHTML = `<span class="time">${timeStr}</span><span class="name">${name}</span>`;
                    scheduleEl.appendChild(eventEl);
                });

                document.getElementById("schedule").style.visibility = "visible";
              }
              else{
                  document.getElementById("schedule").replaceChildren("");
                  document.getElementById("schedule").style.visibility = "hidden";
              }
            }
            else
              document.getElementById(v[1]+'_'+v[2]).innerHTML = v[3];
          }
          else if (v[1]=='image'){
            p = v[3];
            for (i=4; i<v.length; i++){
                p = p + "_" + v[i];
            }
            console.log("image: " + p);
            
            if (p == "blueScreenBackground"){
              document.body.style.background = 'linear-gradient(to right, #00f, #0ff)';
              document.getElementById(v[1]+'_'+v[2]).style.visibility = "hidden"
            
            }
            else{
              document.getElementById(v[1]+'_'+v[2]).src = p;
              document.getElementById("image_default").style.visibility = "visible";
            }

            }
          else if (v[1]=='button') {
            var b = document.createElement("input");
            //Assign different attributes to the element. 
            p = v[2] 
            for (i=3; i<v.length; i++){
                p = p + "_" + v[i];
            }
            console.log(p);
            vp = p.split('$');

            if (vp[1].substr(0,3)=='img') {
                b.type = "image";
                b.src = vp[1];
            }
            else {
                b.type = "button";
                b.value = vp[1]; 
            }
            
            b.name = vp[0]; 
            b.id = vp[0];
            b.onclick = function(event) { button_fn(event) };
            var bdiv = document.getElementById("buttons");
            bdiv.appendChild(b);
            }
          }
        else if (v[0]=='remove') {
            if (v[1]=='buttons') {
                var bdiv = document.getElementById("buttons");
                var fc = bdiv.firstChild;
                while( fc ) {
                    bdiv.removeChild( fc );
                    fc = bdiv.firstChild;
                }

            }
        }
        else if (v[0]=='url') {
            p = v[1]
            for (i=2; i<v.length; i++){
                p = p + "_" + v[i];
            }
            console.log('load url: '+p)
            window.location.assign(p)
        }
    } 

    websocket.onopen = function(){
      append("connection received");
      document.getElementById("status").innerHTML = "<font color='green'>OK</font>";

    } 

    websocket.onclose = function(){
      append("connection closed");
      document.getElementById("status").innerHTML = "<font color='red'>NOT CONNECTED</font>";
    }

    websocket.onerror = function(){
      append("!!!connection error!!!");
    }

}
 
function wsrobot_quit() {
    websocket.close();
    websocket = null;
}

function wsrobot_send(data) {
  if (websocket!=null)
    websocket.send(data);
}

function button_fn(event) {
  var bsrc = event.srcElement || event.originalTarget
  console.log('websocket button '+bsrc.id)
  wsrobot_send(bsrc.id);
}


// MODIM Code port

ip=window.location.hostname;
if (ip=='')
    ip='127.0.0.1';

// to connect from a remote client, set modim IP here
// ip='10.0.1.200'
codeport = 9010;
codeurl = "ws://"+ip+":"+codeport+"/websocketserver";
console.log(codeurl);
codews = new WebSocket(codeurl);

codews.onopen = function(){
  console.log("codews connection received");
}



