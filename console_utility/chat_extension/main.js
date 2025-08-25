const ws = new WebSocket('ws://localhost:8080');

formChat.addEventListener('submit', (e) => {
    e.preventDefault();
    ws.send(textField.value);
    textField.value = '';
});

ws.onopen = (e) => {
    console.log('WebSocket подключен');
};

ws.onmessage = (e) => {
    const text = e.data;
    const elMsg = document.createElement('div');
    elMsg.textContent = text;
    subscribe.appendChild(elMsg);
};
