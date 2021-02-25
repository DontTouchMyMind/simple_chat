const userName = JSON.parse(document.getElementById('username').textContent);
var elParticipants = document.getElementById('participants');
var listParticipants = elParticipants.textContent;
const  chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws'
    + window.location.pathname
);

chatSocket.onopen = function () {
    chatSocket.send(JSON.stringify({
    'event': 'fetch.messages',
    'data': {}
      }));
};

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data)
    if (data['status'] === 'ok' && data['event'] === 'send.message') {
        createMessage(data['data']);
    }
    else if (data['status'] === 'ok' && (data['event'] === 'fetch.messages' || data['event'] === 'list.messages')) {
        var containerParent = document.getElementById('chat-log');
        while (containerParent.firstChild) {
            containerParent.firstChild.remove();
        }
        for (let i=0; i<data['data'].length; i++) {
          createMessage(data['data'][i]);
        }
    }
    else {
        console.log('Error messages');
    }
};

chatSocket.onclose = function (e) {
    console.log('Chat socket closed')
};

document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#chat-message-submit').click();
    }
};

document.querySelector('#chat-message-submit').onclick = function(e) {
    var messageInputDom = document.getElementById('chat-message-input');
    var message = messageInputDom.value;
    chatSocket.send(JSON.stringify({
        'event': 'send.message',
        'data': {
            'message': message
        }
    }));

    messageInputDom.value = '';
};

document.querySelector('#view-history').onclick = function (e) {
    chatSocket.send(JSON.stringify({
        'event': 'list.messages',
        'data': {}
    }));
}

function addUserToGroup() {
    console.log(this.parentNode.id);
    listParticipants += this.parentNode.id;
    chatSocket.send(JSON.stringify({
        'event': 'add.participant',
        'data': {
            'user_id': this.id
        }
    }))
    elParticipants.textContent = listParticipants;
}

function createMessage(data) {
    var author = data['username'];
    var liTag = document.createElement('li');
    var pTagMessage = document.createElement('p');
    var pTagAuthor = document.createElement('p');
    pTagMessage.textContent = data['message'];
    pTagMessage.className = 'text_message';

    if (author === userName) {
        liTag.className = 'sent';
        pTagAuthor.textContent = 'You';
    } else {
        liTag.className = 'replies';
        pTagAuthor.textContent = author;
    }
    liTag.appendChild(pTagAuthor);
    liTag.appendChild(pTagMessage);
    document.querySelector('#chat-log').appendChild(liTag);
}

var elAddUserButton = document.getElementsByClassName('add_user_button');
[].forEach.call(elAddUserButton, function (el) {
    el.addEventListener('click', addUserToGroup, false)
});
