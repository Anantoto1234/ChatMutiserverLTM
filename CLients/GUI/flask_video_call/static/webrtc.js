const socket = io.connect();
let localStream;
let peers = {}; // Đối tượng chứa tất cả kết nối WebRTC của từng user
const configuration = {
    iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
};

let room;
let username;
let isCameraOn = true; // Trạng thái của camera

async function joinRoom() {
    username = document.getElementById("username").value.trim();
    room = document.getElementById("room").value.trim();
    
    if (!username || !room) {
        alert("Please enter both your name and a room code to join.");
        return;
    }

    // Truy cập video và audio của người dùng
    localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    const localVideo = document.createElement("video");
    localVideo.srcObject = localStream;
    localVideo.autoplay = true;
    localVideo.muted = true; // Tắt tiếng của bản thân
    localVideo.id = 'localVideo';
    document.getElementById("videos").appendChild(localVideo);

    // Tham gia phòng trên server
    socket.emit('join', { room, username });

    socket.on('user_joined', (data) => {
        if (data.user_id !== socket.id) {
            createOffer(data.user_id);
        }
    });

    socket.on('offer', async (data) => {
        if (data.sender_id !== socket.id && !peers[data.sender_id]) {
            await createAnswer(data.sender_id, data.offer);
        }
    });

    socket.on('answer', async (data) => {
        const peerConnection = peers[data.sender_id];
        if (peerConnection) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer));
        }
    });

    socket.on('ice-candidate', async (data) => {
        const peerConnection = peers[data.sender_id];
        if (peerConnection) {
            await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    });

    socket.on('notification', (data) => {
        const notification = document.createElement("div");
        notification.innerText = data.message;
        document.getElementById("notifications").appendChild(notification);
    });
}
// Tạo kết nối: RTCPeerConnection
async function createOffer(user_id) {
    const peerConnection = new RTCPeerConnection(configuration);
    peers[user_id] = peerConnection;
// Thêm luồng video/audio của local (localStream):
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    peerConnection.ontrack = (event) => {
        if (!document.getElementById(`video-${user_id}`)) {
            const remoteVideo = document.createElement("video");
            remoteVideo.srcObject = event.streams[0];
            remoteVideo.autoplay = true;
            remoteVideo.id = `video-${user_id}`;
            document.getElementById("videos").appendChild(remoteVideo);
        }
    };

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('ice-candidate', { candidate: event.candidate, sender_id: socket.id, room });
        }
    };
//Tạo offer và gửi qua signaling server:
    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);
    socket.emit('offer', { offer, sender_id: socket.id, room });
}

async function createAnswer(user_id, offer) {
    const peerConnection = new RTCPeerConnection(configuration);
    peers[user_id] = peerConnection;

    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    peerConnection.ontrack = (event) => {
        if (!document.getElementById(`video-${user_id}`)) {
            const remoteVideo = document.createElement("video");
            remoteVideo.srcObject = event.streams[0];
            remoteVideo.autoplay = true;
            remoteVideo.id = `video-${user_id}`;
            document.getElementById("videos").appendChild(remoteVideo);
        }
    };

    peerConnection.onicecandidate = (event) => {
        if (event.candidate) {
            socket.emit('ice-candidate', { candidate: event.candidate, sender_id: socket.id, room });
        }
    };

    await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
    const answer = await peerConnection.createAnswer();
    await peerConnection.setLocalDescription(answer);
    socket.emit('answer', { answer, sender_id: socket.id, room });
}

// Hàm để bật/tắt camera
function toggleCamera() {
    isCameraOn = !isCameraOn;
    localStream.getVideoTracks()[0].enabled = isCameraOn;
    document.getElementById('localVideo').style.display = isCameraOn ? 'block' : 'none';
}

function endCall() {
    localStream.getTracks().forEach(track => track.stop());
    document.getElementById("videos").innerHTML = '';

    for (let userId in peers) {
        peers[userId].close();
        delete peers[userId];
    }

    socket.emit('leave', { room });
}

window.addEventListener('beforeunload', () => {
    endCall();
});
