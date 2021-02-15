const  chatSocket = new WebSocket(
          'ws://'
          + window.location.host
          + '/ws/groups/'
      );

window.onload = function () {
    chatSocket.send(JSON.stringify({
        'event': 'group.list',
        'data': {}
    }));
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly')
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data);
    var group_list = data.data;
    if (group_list.length === 0) {
        $('.created_rooms').html(
          '<p>You are not connected to any of the existing groups.</p>' +
                '<p>Create a new room and invite users to chat.</p>'
        )
    }
    for (var i=0; i<=group_list.length-1; i++) {
        var group_name = group_list[i]['name'];
        var $link = '/chat/' + group_list[i]['id'] + '/';

        $('#created_rooms_display').append(
            '<tr>' +
            '<th>' + group_name + '</th>' +
            '<th><button onclick="window.location.pathname = \''+ $link + '\'" type="button">Connect</button></th>' +
            '</tr>'
        );
    }
};

document.querySelector('#room-name-input').focus();
document.querySelector('#room-name-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#room-name-submit').click();
    }
};

document.querySelector('#room-name-submit').onclick = function(e) {
    var roomName = document.querySelector('#room-name-input').value;

    window.location.pathname = '/chat/' + roomName + '/';
};