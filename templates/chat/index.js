const chat_id = "12"
const messages = []
document.querySelector("#ws-id").textContent = chat_id;
const ws = new WebSocket(`ws://localhost:8000/chat/ws/${chat_id}`);
ws.onmessage = function (event) {
    console.log(event.data)
    const message = document.createElement('li')
    message.appendChild(document.createTextNode(event.data))
    ul.append(message)
};

function sendMessage(event) {
    event.preventDefault();
    const message = document.getElementById("messageText").value
    const name = localStorage.getItem('name')
    ws.send(JSON.stringify({chat_id, name, message}))
}

function connect(event) {
    event.preventDefault();
    const name = localStorage.getItem('name')
    ws.send(JSON.stringify({chat_id, name}))
}

window.onload = function() {
        const token = localStorage.getItem("access")
        fetch('http://localhost:8000/auth/user', {
            method: 'GET',
            headers: {
                'Content-type': 'application/json; charset=UTF-8',
                'Authorization': `Selezenka ${token}`
            },
        })
            .then((response) => response.json())
            .then((data) => {
                const name = data.first_name + " " + data.last_name
                console.log(name)
                localStorage.setItem('name', name)
            })
}
