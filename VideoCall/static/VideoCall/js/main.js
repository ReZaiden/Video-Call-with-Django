// DOM Elements
const localVideo = document.getElementById('local-video');
const remoteVideo = document.getElementById('remote-video');
const callBtn = document.getElementById('call-btn');
const peerIdInput = document.getElementById('peer-id');
const historyList = document.getElementById('history-list');
const incomingModal = document.getElementById('incoming-modal');
const callerName = document.getElementById('caller-name');
const acceptBtn = document.getElementById('accept-btn');
const rejectBtn = document.getElementById('reject-btn');
const callControls = document.getElementById('call-controls');
const muteBtn = document.getElementById('mute-btn');
const videoBtn = document.getElementById('video-btn');
const endCallBtn = document.getElementById('end-call-btn');
const infoText = document.getElementById('info-text');

let localStream = null;
let isMuted = false;
let isVideoOff = false;
let inCall = false;
let PC = null;
let video_call_id = 0;
let is_caller = true;

// STUN configuration
const configuration = {
    iceServers: [{ urls: "stun:stun.l.google.com:19302" }]
};

// WebSocket connection
const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const socket = new WebSocket(protocol + window.location.host + '/ws/video_call/');

socket.onopen = () => console.log("WebSocket connected ✅");

socket.onclose = () => {
    console.log("WebSocket disconnected");
    if (inCall) endCall();
};

socket.onmessage = async (event) => {
    const message = JSON.parse(event.data);

    switch (message.action) {
        case "call_initiated":
            switch (message.status_code) {
                case 404:
                    infoText.innerHTML = message.message;
                    break;
                case 409:
                    infoText.innerHTML = message.message;
                    break;
                case 201:
                    infoText.innerHTML = message.message;
                    video_call_id = message.video_call_id;
                    break;
            }
            break;

        case "incoming_call":
            video_call_id = message.video_call_id;
            callerName.textContent = message.caller_username;
            incomingModal.style.display = 'flex';

            setTimeout(() => {
                if (!inCall) send_message({ action: 'cancel_call' });
            }, 20000);
            break;

        case "call_started":
            infoText.innerHTML = "Connecting...";
            video_call_id = message.video_call_id;
            StartWebRTC();
            break;

        case "call_ended":
        case "disconnected":
            endCall();
            infoText.innerHTML = message.message || "Call ended.";
            break;

        case "call_canceled":
            incomingModal.style.display = 'none';
            infoText.innerHTML = "Call canceled.";
            break;

        case "error":
            infoText.innerHTML = message.message;
            break;

        case "caller_data":
        case "receiver_data":
            if (message.sdp) {
                console.log("📦 Received SDP");
                await PC.setRemoteDescription(new RTCSessionDescription(message.sdp));
                if (message.sdp.type === "offer") {
                    const answer = await PC.createAnswer();
                    await PC.setLocalDescription(answer);
                    send_RTC_message({ sdp: PC.localDescription });
                }
            } else if (message.candidate) {
                console.log("📦 Received ICE Candidate");
                try {
                    await PC.addIceCandidate(new RTCIceCandidate(message.candidate));
                } catch (err) {
                    console.error("Error adding ICE candidate:", err);
                }
            }
            break;
    }
};

// -------------------------------
// Media handling
// -------------------------------
async function getMedia() {
    try {
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            },
            audio: true
        };
        if (!window.isSecureContext) {
            throw new Error('HTTPS required for camera access on mobile!');
        }
        localStream = await navigator.mediaDevices.getUserMedia(constraints);
        localVideo.srcObject = localStream;
        if (PC) {
            localStream.getTracks().forEach(track => PC.addTrack(track, localStream));
        }
        console.log('Camera access granted!');
    } catch (err) {
        console.error("Media access error:", err.name, err.message);
        let userMsg = 'Please allow camera and microphone access!';
        if (err.name === 'NotAllowedError') {
            userMsg = 'Permission denied. Check browser settings.';
        } else if (err.name === 'NotFoundError') {
            userMsg = 'No camera found. Try another device.';
        } else if (err.name === 'NotReadableError') {
            userMsg = 'Camera in use by another app. Close it.';
        }
        alert(userMsg);
        infoText.innerHTML = userMsg;
    }
}

// -------------------------------
// Call control functions
// -------------------------------
function ShowHistory(displayName, duration, datetime) {
            const div = document.createElement('div');
            div.className = 'history-item';
            historyList.prepend(div);
            var initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
            div.innerHTML = `
                        <div class="history-avatar">${initials}</div>
                        <div class="history-info">
                            <h6>${displayName}</h6>
                            <p>Video call • ${duration} • ${datetime}</p>
                        </div>
                    `;
            div.onclick = () => peerIdInput.value = displayName;
        }

function endCall() {
    if (PC) {
        PC.close();
        PC = null;
    }
    remoteVideo.srcObject = null;
    inCall = false;
    callControls.classList.remove('active');
    infoText.innerHTML = "Call ended.";

    video_call_id = 0;
    is_caller = true;
}


// -------------------------------
// Button event handlers
// -------------------------------
callBtn.onclick = () => {
    const id = peerIdInput.value.trim();
    if (id && !inCall) {
        ShowHistory(peerIdInput.value, "00:00:00", "Just Now")
        peerIdInput.value = '';
        send_message({ action: 'initiate_call', receiver_username: id });
    }
};

acceptBtn.onclick = () => {
    incomingModal.style.display = 'none';
    ShowHistory(callerName.textContent, "00:00:00", "Just Now")
    send_message({ action: 'start_call' });
    is_caller = false;
    StartWebRTC();
};

rejectBtn.onclick = () => {
    incomingModal.style.display = 'none';
    send_message({ action: 'cancel_call' });
};

muteBtn.onclick = () => {
    if (!localStream) return;
    isMuted = !isMuted;
    localStream.getAudioTracks()[0].enabled = !isMuted;
    muteBtn.classList.toggle('active', isMuted);
};

videoBtn.onclick = () => {
    if (!localStream) return;
    isVideoOff = !isVideoOff;
    localStream.getVideoTracks()[0].enabled = !isVideoOff;
    videoBtn.classList.toggle('active', isVideoOff);
};

endCallBtn.onclick = () => {
    if (inCall) {
        send_message({ action: 'end_call' });
        endCall();
    }
};

incomingModal.onclick = (e) => {
    if (e.target === incomingModal) incomingModal.style.display = 'none';
};

// -------------------------------
// WebRTC functions
// -------------------------------
async function StartWebRTC() {
    PC = new RTCPeerConnection(configuration);

    // Ice candidates
    PC.onicecandidate = (e) => {
        if (e.candidate) {
            send_RTC_message({ candidate: e.candidate });
        }
    };

    // Remote stream
    PC.ontrack = (event) => {
        console.log("🎥 Remote stream received");
        remoteVideo.srcObject = event.streams[0];
        inCall = true;
        callControls.classList.add('active');
    };

    // مدیریت وضعیت اتصال
    PC.oniceconnectionstatechange = () => {
        console.log('ICE state:', PC.iceConnectionState);
        if (PC.iceConnectionState === 'failed' || PC.iceConnectionState === 'disconnected') {
            endCall();
        }
    };

    await getMedia();

    if (is_caller) {
        const offer = await PC.createOffer();
        await PC.setLocalDescription(offer);
        send_RTC_message({ sdp: PC.localDescription });
    }
}

// -------------------------------
// WebSocket message helpers
// -------------------------------
function send_message(msg) {
    msg.video_call_id = video_call_id;
    socket.send(JSON.stringify(msg));
}

function send_RTC_message(msg) {
    msg.action = is_caller ? "caller_data" : "receiver_data";
    msg.video_call_id = video_call_id;
    socket.send(JSON.stringify(msg));
}