function insertRow(packet) {
    var div = document.getElementById("table-body");
    var row = `
        <tr>
            <th colspan="21" style="text-align: left;">` + new Date(packet.timestamp * 1000).toLocaleString("es-ES") + `.` + new Date(packet.telemetry.timestamp * 1000).getMilliseconds() + ` // ` +  packet.gs_id + `</th>
        </tr>
        <tr>
            <td>` +  packet.rssi + `</td>
            <td>` +  packet.callsign + `</td>
            <td>` +  packet.functionId + `</td>
            <td>` +  packet.src + `</td>
            <td>` +  packet.dst + `</td>
            <td>` +  new Date(packet.telemetry.timestamp * 1000).toLocaleTimeString("es-ES") + `.` +  new Date(packet.telemetry.timestamp * 1000).getMilliseconds() + `</td>
            <td>` +  packet.telemetry.id + `</td>
            <td>` +  packet.telemetry.batt_v + `</td>
            <td>` +  packet.telemetry.batt_ch_i + `</td>
            <td>` +  packet.telemetry.batt_ch_v + `</td>
            <td>` +  packet.telemetry.boot_counter + `</td>
            <td>` +  packet.telemetry.conf_byte + `</td>
            <td>` +  packet.telemetry.rst_counter + `</td>
            <td>` +  packet.telemetry.cell_a_v + `</td>
            <td>` +  packet.telemetry.cell_b_v + `</td>
            <td>` +  packet.telemetry.cell_c_v + `</td>
            <td>` +  packet.telemetry.batt_temp + `</td>
            <td>` +  packet.telemetry.board_temp + `</td>
            <td>` +  packet.telemetry.mcu_temp + `</td>
            <td>` +  parseFloat(packet.telemetry.latitude).toFixed(3) + `</td>
            <td>` +  parseFloat(packet.telemetry.longitude).toFixed(3) + `</td>
            <td>` +  packet.telemetry.tx_counter + `</td>
            <td>` +  packet.telemetry.rx_counter + `</td>
        </tr>
        <tr>
            <td colspan="21" style="text-align: left;">Route: [` +  packet.route + `]</td>
        </tr>
    `;
    div.innerHTML += row
}

function showNotification(from, align, level, icon, msg){
    $.notify({
      icon: icon,
      message: msg
      },{
      type: level,
      timer: 1000,
      placement: {
          from: from,
          align: align
      }
      });
}

/* Retrieve all the items */
function getAllItems() {
    let all_socket = new WebSocket("wss://gs.jarao.org/all");
    all_socket.onmessage = function(event) {
          console.log(event.data);
          var packet = JSON.parse(event.data);
          insertRow(packet);
    };
    all_socket.onclose = function(event) {

    };
    all_socket.onerror = function(event) {
        console.error("Error all_socket")
    };
}

/* Create websocket */
function createWebSocket() {
    let socket = new WebSocket("wss://gs.jarao.org/sub");
    socket.onmessage = function(event) {
          //alert(`[message] Data received from server: ${event.data}`);
          try{
              console.log(event.data);
            var packet = JSON.parse(event.data)
            insertRow(packet);
            showNotification('top', 'right', 'success', "check_circle", "New packet received");
          } catch(err) {

            showNotification('top', 'right', 'warning', "add_alert", event.data);
          }
    };
    socket.onclose = function(event) {
      if (!event.wasClean) {
        showNotification('top', 'right', 'danger', 'error', "No communication with server. Trying to reconnect with the server...");
        /* Try to reconnect again */
      }
    };
    socket.onerror = function(event) {
        setTimeout(function() {
            createWebSocket();
        }, 5000);
    };
}

createWebSocket();
getAllItems();

