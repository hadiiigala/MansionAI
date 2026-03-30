const API_BASE_URL = 'http://localhost:5000/api';

// Form elements
const registrationForm = document.getElementById('registrationForm');
const promptForm = document.getElementById('promptForm');
const promptSection = document.getElementById('promptSection');
const historySection = document.getElementById('historySection');
const generateBtn = document.getElementById('generateBtn');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const historyContainer = document.getElementById('historyContainer');
const multiViewContainer = document.getElementById('multiViewContainer');

// Audio elements
const recordPositiveBtn = document.getElementById('recordPositiveBtn');
const speakPositiveBtn = document.getElementById('speakPositiveBtn');
const recordNegativeBtn = document.getElementById('recordNegativeBtn');
const speakNegativeBtn = document.getElementById('speakNegativeBtn');

// Result elements
const promptDisplay = document.getElementById('promptDisplay');
const negativePromptDisplay = document.getElementById('negativePromptDisplay');
const negativePromptText = document.getElementById('negativePromptText');

// Modal elements
const imageModal = document.getElementById('imageModal');
const enlargedImage = document.getElementById('enlargedImage');
const modalCaption = document.getElementById('modalCaption');
const closeModal = document.getElementsByClassName('close')[0];

// User data
let currentUser = null;
let userHistory = [];

// Audio recording state
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentRecordingField = null;

// Web Audio API
const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Initialize on page load
window.addEventListener('load', () => {
    // Initialize audio controls
    initAudioControls();
    
    // Check API health
    fetch(`${API_BASE_URL}/health`)
        .then(response => {
            if (response.ok) {
                console.log('API is ready');
            }
        })
        .catch(error => {
            console.warn('API health check failed:', error);
        });
});

// Handle registration form submission
registrationForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    // Get user info
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const registrationId = document.getElementById('registration').value;
    
    // Store user info
    currentUser = {
        name: name,
        email: email,
        registrationId: registrationId,
        registeredAt: new Date()
    };
    
    // Show success message
    showSuccess(`Welcome, ${name}! You're now registered.`);
    
    // Show the prompt section
    promptSection.style.display = 'block';
    
    // Scroll to prompt section
    promptSection.scrollIntoView({ behavior: 'smooth' });
});

// Handle form submission
promptForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    if (!currentUser) {
        showError('Please register first before generating designs');
        document.getElementById('userInfoForm').scrollIntoView({ behavior: 'smooth' });
        return;
    }
    
    // Get prompts and number of views
    const positivePrompt = document.getElementById('positivePrompt').value;
    const negativePrompt = document.getElementById('negativePrompt').value;
    const numViews = parseInt(document.getElementById('numViews').value);
    
    // Validate
    if (!positivePrompt.trim()) {
        showError('Please enter a positive prompt');
        return;
    }
    
    // Hide previous results and errors
    resultsSection.style.display = 'none';
    errorMessage.style.display = 'none';
    
    // Show loading state
    setLoading(true);
    
    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                userInfo: currentUser,
                positivePrompt,
                negativePrompt,
                numViews
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to generate image');
        }
        
        // Add to history
        addToHistory({
            timestamp: new Date(),
            positivePrompt,
            negativePrompt,
            images: data.images
        });
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'An error occurred while generating the image. Please try again.');
    } finally {
        setLoading(false);
    }
});

function setLoading(loading) {
    const btnText = generateBtn.querySelector('.btn-text');
    const btnLoader = generateBtn.querySelector('.btn-loader');
    
    if (loading) {
        generateBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
    } else {
        generateBtn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

function displayResults(data) {
    // Set prompts
    promptDisplay.textContent = data.prompt;
    
    if (data.negativePrompt) {
        negativePromptText.textContent = data.negativePrompt;
        negativePromptDisplay.style.display = 'block';
    } else {
        negativePromptDisplay.style.display = 'none';
    }
    
    // Display multi-view images
    displayMultiViewImages(data.images);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function displayMultiViewImages(images) {
    // Clear previous images
    multiViewContainer.innerHTML = '';
    
    // Create image cards for each view
    images.forEach((imageData, index) => {
        const viewCard = document.createElement('div');
        viewCard.className = 'view-card';
        
        const img = document.createElement('img');
        img.src = imageData.image;
        img.alt = `Generated Interior Design - View ${imageData.viewNumber}`;
        img.className = 'view-image';
        img.dataset.viewNumber = imageData.viewNumber;
        
        const viewInfo = document.createElement('div');
        viewInfo.className = 'view-info';
        viewInfo.innerHTML = `View <span class="view-number">${imageData.viewNumber}</span>`;
        
        viewCard.appendChild(img);
        viewCard.appendChild(viewInfo);
        multiViewContainer.appendChild(viewCard);
        
        // Add click event to open modal
        img.addEventListener('click', () => openModal(imageData.image, `View ${imageData.viewNumber}`));
    });
}

function addToHistory(entry) {
    userHistory.unshift(entry); // Add to beginning of array
    
    // Keep only the last 10 entries
    if (userHistory.length > 10) {
        userHistory = userHistory.slice(0, 10);
    }
    
    // Update history display
    updateHistoryDisplay();
}

function updateHistoryDisplay() {
    if (userHistory.length === 0) {
        historyContainer.innerHTML = '<p>No history available. Generate some designs to see them here.</p>';
        return;
    }
    
    let historyHTML = '<div class="history-list">';
    
    userHistory.forEach((entry, index) => {
        const timestamp = new Date(entry.timestamp).toLocaleString();
        historyHTML += `
            <div class="history-item">
                <div class="history-header">
                    <span class="history-number">#${userHistory.length - index}</span>
                    <span class="history-timestamp">${timestamp}</span>
                </div>
                <div class="history-prompts">
                    <div class="prompt-positive">
                        <strong>Positive:</strong> ${entry.positivePrompt}
                    </div>
                    ${entry.negativePrompt ? `<div class="prompt-negative">
                        <strong>Negative:</strong> ${entry.negativePrompt}
                    </div>` : ''}
                </div>
                <div class="history-image-preview">
        `;
        
        // Display thumbnails for all views
        if (entry.images && entry.images.length > 0) {
            entry.images.forEach(imageData => {
                historyHTML += `<img src="${imageData.image}" alt="Generated design - View ${imageData.viewNumber}" />`;
            });
        }
        
        historyHTML += `
                </div>
            </div>
        `;
    });
    
    historyHTML += '</div>';
    historyContainer.innerHTML = historyHTML;
}

// Show history when clicking on Profile link
document.querySelector('a[href="#userInfoForm"]').addEventListener('click', (e) => {
    e.preventDefault();
    if (currentUser) {
        historySection.style.display = 'block';
        historySection.scrollIntoView({ behavior: 'smooth' });
    } else {
        document.getElementById('userInfoForm').scrollIntoView({ behavior: 'smooth' });
    }
});

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showSuccess(message) {
    const tempMessage = document.createElement('div');
    tempMessage.textContent = message;
    tempMessage.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 1000;
        animation: slideIn 0.3s ease-in-out;
    `;
    document.body.appendChild(tempMessage);
    setTimeout(() => tempMessage.remove(), 3000);
}

// Audio functions
function initAudioControls() {
    // Positive Prompt Audio Buttons
    recordPositiveBtn.addEventListener('click', () => startRecording('positivePrompt', recordPositiveBtn));
    speakPositiveBtn.addEventListener('click', () => speakText('positivePrompt'));
    
    // Negative Prompt Audio Buttons
    recordNegativeBtn.addEventListener('click', () => startRecording('negativePrompt', recordNegativeBtn));
    speakNegativeBtn.addEventListener('click', () => speakText('negativePrompt'));
    
    // Close modal
    if (closeModal) {
        closeModal.onclick = function() {
            imageModal.style.display = "none";
        }
    }
    
    // Close modal when clicking outside the image
    window.onclick = function(event) {
        if (imageModal && event.target == imageModal) {
            imageModal.style.display = "none";
        }
    }
}

// Open modal with enlarged image
function openModal(imageSrc, caption) {
    if (enlargedImage) {
        enlargedImage.src = imageSrc;
        if (modalCaption) {
            modalCaption.innerHTML = caption || "Generated Interior Design";
        }
        if (imageModal) {
            imageModal.style.display = "block";
        }
    }
}

// Start recording audio
async function startRecording(fieldId, button) {
    if (isRecording && currentRecordingField === fieldId) {
        // Stop recording
        stopRecording(fieldId, button);
        return;
    }
    
    try {
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }

        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
            ? 'audio/webm;codecs=opus'
            : undefined;
        mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
        audioChunks = [];
        isRecording = true;
        currentRecordingField = fieldId;
        
        // Update button appearance
        button.textContent = '⏹️ Stop Recording';
        button.classList.add('recording');
        
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };
        
        mediaRecorder.onstop = async () => {
            const recordedType = mediaRecorder.mimeType || 'audio/webm';
            const audioBlob = new Blob(audioChunks, { type: recordedType });
            await convertSpeechToText(audioBlob, fieldId);
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
    } catch (error) {
        showError('Microphone access denied. Please allow microphone access and try again.');
        console.error('Microphone error:', error);
    }
}

// Stop recording audio
function stopRecording(fieldId, button) {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        // Reset button appearance
        button.textContent = fieldId === 'positivePrompt' ? '🎤 Record' : '🎤 Record';
        button.classList.remove('recording');
    }
}

// Convert speech to text using backend API
async function convertSpeechToText(audioBlob, fieldId) {
    try {
        // Show loading state
        const button = fieldId === 'positivePrompt' ? recordPositiveBtn : recordNegativeBtn;
        button.disabled = true;
        button.textContent = '⏳ Processing...';
        
        // Convert blob to wav base64 to avoid ffmpeg dependency server-side
        const base64Audio = await convertBlobToWavBase64(audioBlob);
        
        try {
            const response = await fetch(`${API_BASE_URL}/speech-to-text`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    audio: base64Audio,
                    language: 'en-US'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                document.getElementById(fieldId).value = data.text;
                showSuccess(`Successfully transcribed: "${data.text}"`);
            } else {
                showError(`Speech to text failed: ${data.error}`);
            }
        } catch (error) {
            showError('Failed to process speech: ' + error.message);
        } finally {
            button.disabled = false;
            button.textContent = fieldId === 'positivePrompt' ? '🎤 Record' : '🎤 Record';
        }
    } catch (error) {
        showError('Error processing audio: ' + error.message);
    }
}

async function convertBlobToWavBase64(blob) {
    const arrayBuffer = await blob.arrayBuffer();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer.slice(0));
    const wavBuffer = audioBufferToWav(audioBuffer);
    const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });

    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(wavBlob);
    });
}

function audioBufferToWav(buffer) {
    const numOfChan = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const format = 1; // PCM
    const bitDepth = 16;
    const bytesPerSample = bitDepth / 8;
    const blockAlign = numOfChan * bytesPerSample;
    const samples = buffer.length * numOfChan;
    const bufferLength = 44 + samples * bytesPerSample;
    const arrayBuffer = new ArrayBuffer(bufferLength);
    const view = new DataView(arrayBuffer);
    let offset = 0;

    function writeString(str) {
        for (let i = 0; i < str.length; i += 1) {
            view.setUint8(offset, str.charCodeAt(i));
            offset += 1;
        }
    }

    // RIFF chunk descriptor
    writeString('RIFF');
    view.setUint32(offset, bufferLength - 8, true); offset += 4;
    writeString('WAVE');

    // FMT sub-chunk
    writeString('fmt ');
    view.setUint32(offset, 16, true); offset += 4; // Subchunk1Size (16 for PCM)
    view.setUint16(offset, format, true); offset += 2; // Audio format (1 = PCM)
    view.setUint16(offset, numOfChan, true); offset += 2;
    view.setUint32(offset, sampleRate, true); offset += 4;
    view.setUint32(offset, sampleRate * blockAlign, true); offset += 4; // Byte rate
    view.setUint16(offset, blockAlign, true); offset += 2;
    view.setUint16(offset, bitDepth, true); offset += 2;

    // Data sub-chunk
    writeString('data');
    view.setUint32(offset, samples * bytesPerSample, true); offset += 4;

    // Write PCM samples
    const channelData = [];
    for (let channel = 0; channel < numOfChan; channel += 1) {
        channelData.push(buffer.getChannelData(channel));
    }

    for (let i = 0; i < buffer.length; i += 1) {
        for (let channel = 0; channel < numOfChan; channel += 1) {
            let sample = channelData[channel][i];
            sample = Math.max(-1, Math.min(1, sample));
            view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
            offset += 2;
        }
    }

    return arrayBuffer;
}

// Speak text using backend API
async function speakText(fieldId) {
    const text = document.getElementById(fieldId).value;
    
    if (!text.trim()) {
        showError('Please enter text before speaking');
        return;
    }
    
    try {
        const button = fieldId === 'positivePrompt' ? speakPositiveBtn : speakNegativeBtn;
        button.disabled = true;
        button.textContent = '⏳ Generating...';
        
        const response = await fetch(`${API_BASE_URL}/text-to-speech`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                text: text,
                rate: 150,
                volume: 0.9
            })
        });
        
        const data = await response.json();
        
        if (data.success && data.audio) {
            // Play the audio
            const audio = new Audio(data.audio);
            audio.play();
        } else {
            showError(`Text to speech failed: ${data.error}`);
        }
    } catch (error) {
        showError('Error generating speech: ' + error.message);
    } finally {
        const button = fieldId === 'positivePrompt' ? speakPositiveBtn : speakNegativeBtn;
        button.disabled = false;
        button.textContent = fieldId === 'positivePrompt' ? '🔊 Speak' : '🔊 Speak';
    }
}