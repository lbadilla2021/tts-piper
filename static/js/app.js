// Variables globales
const textInput = document.getElementById('text-input');
const genderSelect = document.getElementById('gender-select');
const voiceSelect = document.getElementById('voice-select');
const speedSlider = document.getElementById('speed-slider');
const speedValue = document.getElementById('speed-value');
const charCount = document.getElementById('char-count');
const generateBtn = document.getElementById('generate-btn');
const clearBtn = document.getElementById('clear-btn');
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const progressContainer = document.getElementById('progress-container');
const resultContainer = document.getElementById('result-container');
const audioPlayer = document.getElementById('audio-player');
const downloadBtn = document.getElementById('download-btn');

let voices = { male: [], female: [] };
let currentAudioUrl = null;
let currentFilename = null;

// Cargar voces disponibles
async function loadVoices() {
    try {
        const response = await fetch('/api/voices');
        voices = await response.json();
    } catch (error) {
        console.error('Error cargando voces:', error);
    }
}

// Actualizar contador de caracteres
textInput.addEventListener('input', () => {
    const count = textInput.value.length;
    charCount.textContent = count;
    
    if (count > 9000) {
        charCount.style.color = '#ef4444';
    } else if (count > 7000) {
        charCount.style.color = '#f59e0b';
    } else {
        charCount.style.color = '#64748b';
    }
    
    updateGenerateButton();
});

// Actualizar selector de voz cuando cambia el género
genderSelect.addEventListener('change', () => {
    const selectedGender = genderSelect.value;
    
    voiceSelect.innerHTML = '';
    voiceSelect.disabled = !selectedGender;
    
    if (selectedGender) {
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = 'Seleccionar voz';
        voiceSelect.appendChild(defaultOption);
        
        const genderVoices = voices[selectedGender] || [];
        genderVoices.forEach(voice => {
            const option = document.createElement('option');
            option.value = voice.id;
            option.textContent = `${voice.name} - ${voice.accent} (${voice.quality})`;
            voiceSelect.appendChild(option);
        });
    } else {
        const option = document.createElement('option');
        option.value = '';
        option.textContent = 'Primero selecciona un género';
        voiceSelect.appendChild(option);
    }
    
    updateGenerateButton();
});

// Actualizar selección de voz
voiceSelect.addEventListener('change', updateGenerateButton);

// Actualizar velocidad
speedSlider.addEventListener('input', () => {
    const speed = parseFloat(speedSlider.value);
    let speedText = `${speed.toFixed(1)}x`;
    
    if (speed === 1.0) {
        speedText += ' (Normal)';
    } else if (speed < 1.0) {
        speedText += ' (Lento)';
    } else {
        speedText += ' (Rápido)';
    }
    
    speedValue.textContent = speedText;
});

// Actualizar botón de generar
function updateGenerateButton() {
    const hasText = textInput.value.trim().length > 0;
    const hasVoice = voiceSelect.value !== '';
    
    generateBtn.disabled = !(hasText && hasVoice);
}

// Manejo de archivos - drag and drop
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', async (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        await handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', async (e) => {
    if (e.target.files.length > 0) {
        await handleFileUpload(e.target.files[0]);
    }
});

// Procesar archivo subido
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showNotification('Cargando archivo...', 'info');
        
        const response = await fetch('/api/upload-file', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            textInput.value = data.text;
            textInput.dispatchEvent(new Event('input'));
            showNotification(`Archivo "${data.filename}" cargado exitosamente`, 'success');
        } else {
            showNotification(data.error || 'Error al cargar el archivo', 'error');
        }
    } catch (error) {
        showNotification('Error al procesar el archivo', 'error');
        console.error('Error:', error);
    }
}

// Generar audio
generateBtn.addEventListener('click', async () => {
    const text = textInput.value.trim();
    const voice = voiceSelect.value;
    const speed = parseFloat(speedSlider.value);
    
    if (!text || !voice) return;
    
    // Ocultar resultado anterior
    resultContainer.style.display = 'none';
    
    // Mostrar progreso
    progressContainer.style.display = 'block';
    generateBtn.disabled = true;
    
    try {
        const response = await fetch('/api/synthesize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text, voice, speed })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Guardar información del audio
            currentFilename = data.filename;
            currentAudioUrl = data.download_url;
            
            // Mostrar resultado
            progressContainer.style.display = 'none';
            resultContainer.style.display = 'block';
            
            // Actualizar información
            document.getElementById('result-voice-info').textContent = 
                `Voz: ${data.voice} | Velocidad: ${speed.toFixed(1)}x`;
            
            // Configurar reproductor de audio
            audioPlayer.src = currentAudioUrl;
            
            showNotification('Audio generado exitosamente', 'success');
        } else {
            throw new Error(data.error || 'Error al generar audio');
        }
    } catch (error) {
        showNotification(error.message || 'Error al generar el audio', 'error');
        console.error('Error:', error);
    } finally {
        progressContainer.style.display = 'none';
        generateBtn.disabled = false;
    }
});

// Descargar audio
downloadBtn.addEventListener('click', () => {
    if (currentAudioUrl) {
        const link = document.createElement('a');
        link.href = currentAudioUrl;
        link.download = currentFilename;
        link.click();
    }
});

// Limpiar formulario
clearBtn.addEventListener('click', () => {
    textInput.value = '';
    genderSelect.value = '';
    voiceSelect.value = '';
    voiceSelect.disabled = true;
    speedSlider.value = 1.0;
    charCount.textContent = '0';
    speedValue.textContent = '1.0x (Normal)';
    resultContainer.style.display = 'none';
    progressContainer.style.display = 'none';
    
    // Limpiar opciones de voz
    voiceSelect.innerHTML = '<option value="">Primero selecciona un género</option>';
    
    updateGenerateButton();
    
    showNotification('Formulario limpiado', 'info');
});

// Sistema de notificaciones
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '16px 24px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease-out',
        maxWidth: '400px'
    });
    
    // Colores según tipo
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#6366f1'
    };
    
    notification.style.background = colors[type] || colors.info;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Remover después de 4 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 4000);
}

// Agregar estilos de animación
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Cargar estadísticas
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('male-count').textContent = stats.male_voices;
        document.getElementById('female-count').textContent = stats.female_voices;
    } catch (error) {
        console.error('Error cargando estadísticas:', error);
    }
}

// Inicialización
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Aplicación TTS inicializada');
    await loadVoices();
    await loadStats();
    updateGenerateButton();
});

// Prevenir pérdida de datos
window.addEventListener('beforeunload', (e) => {
    if (textInput.value.trim().length > 100) {
        e.preventDefault();
        e.returnValue = '';
    }
});
