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

let localStream = null;
let isMuted = false;
let isVideoOff = false;
let inCall = false;

// Get user media
async function getMedia() {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
        localVideo.srcObject = localStream;
        return localStream;
    } catch (err) {
        console.error('Media access error:', err);
        alert('Camera and microphone access required!');
    }
}

// Start local video
getMedia();

// Simulate remote video
function startRemoteVideo() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            remoteVideo.srcObject = stream;
            inCall = true;
            callControls.classList.add('active');
        });
}

// End call
function endCall() {
    if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
    }
    remoteVideo.srcObject = null;
    localVideo.srcObject = null;
    inCall = false;
    callControls.classList.remove('active');
    getMedia(); // Restart local camera
}

// Add to history
function addToHistory(id, name = null) {
    const displayName = name || `User ${id}`;
    const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

    const div = document.createElement('div');
    div.className = 'history-item';
    div.innerHTML = `
        <div class="history-avatar">${initials}</div>
        <div class="history-info">
            <h6>${displayName}</h6>
            <p>Video call • Just now</p>
        </div>
    `;
    div.onclick = () => {
        peerIdInput.value = id;
    };
    historyList.prepend(div);
}

// Outgoing call
callBtn.onclick = () => {
    const id = peerIdInput.value.trim();
    if (id && !inCall) {
        addToHistory(id);
        startRemoteVideo();
        peerIdInput.value = '';
    }
};

// Simulate incoming call
setTimeout(() => {
    callerName.textContent = 'Sarah Connor';
    incomingModal.style.display = 'flex';
}, 6000);

// Accept call
acceptBtn.onclick = () => {
    incomingModal.style.display = 'none';
    startRemoteVideo();
    addToHistory('sarah_c', 'Sarah Connor');
};

// Reject call
rejectBtn.onclick = () => {
    incomingModal.style.display = 'none';
};

// Mute/Unmute
muteBtn.onclick = () => {
    if (!localStream) return;
    isMuted = !isMuted;
    localStream.getAudioTracks()[0].enabled = !isMuted;
    muteBtn.classList.toggle('active', isMuted);
    muteBtn.title = isMuted ? 'Unmute' : 'Mute';
};

// Toggle video
videoBtn.onclick = () => {
    if (!localStream) return;
    isVideoOff = !isVideoOff;
    localStream.getVideoTracks()[0].enabled = !isVideoOff;
    videoBtn.classList.toggle('active', isVideoOff);
    videoBtn.title = isVideoOff ? 'Camera On' : 'Camera Off';
};

// End call
endCallBtn.onclick = () => {
    if (inCall) {
        endCall();
    }
};

// Close modal on outside click
incomingModal.onclick = (e) => {
    if (e.target === incomingModal) {
        incomingModal.style.display = 'none';
    }
};