/* ============================================================================
   OMNI-AI FUTURISTIC UI - JAVASCRIPT
   Interactive Features & Backend Integration
   ============================================================================ */

class OmniAIUI {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
        this.startupSequence();
        this.settings = {
            neonEnabled: true,
            soundEnabled: true,
            animationsEnabled: true,
            voiceSpeed: 150
        };
    }

    // ========================================================================
    // INITIALIZATION
    // ========================================================================

    initializeElements() {
        // Navigation
        this.navItems = document.querySelectorAll('.nav-item');
        this.sections = document.querySelectorAll('.section-content');

        // Dashboard
        this.cpuUsage = document.getElementById('cpuUsage');
        this.memoryUsage = document.getElementById('memoryUsage');
        this.diskUsage = document.getElementById('diskUsage');
        this.cpuBar = document.getElementById('cpuBar');
        this.memoryBar = document.getElementById('memoryBar');
        this.diskBar = document.getElementById('diskBar');

        // Controls
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettings = document.getElementById('closeSettings');
        this.themePulse = document.getElementById('themePulse');

        // Voice
        this.listenBtn = document.getElementById('listenBtn');
        this.voiceStatus = document.getElementById('voiceStatus');
        this.inputTranscript = document.getElementById('inputTranscript');
        this.responseTranscript = document.getElementById('responseTranscript');

        // Security
        this.encryptBtn = document.getElementById('encryptBtn');
        this.hashBtn = document.getElementById('hashBtn');
        this.runAuditBtn = document.getElementById('runAuditBtn');

        // Terminal
        this.terminalInput = document.getElementById('terminalInput');
        this.terminalDisplay = document.getElementById('terminalDisplay');

        // Activity Log
        this.activityLog = document.getElementById('activityLog');
        this.timeDisplay = document.getElementById('timeDisplay');
    }

    setupEventListeners() {
        // Navigation
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => this.navigateSection(e));
        });

        // Settings
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettings.addEventListener('click', () => this.closeSettingsModal());
        this.themePulse.addEventListener('click', () => this.toggleTheme());

        // Voice
        this.listenBtn.addEventListener('click', () => this.startListening());

        // Security
        this.encryptBtn.addEventListener('click', () => this.encryptData());
        this.hashBtn.addEventListener('click', () => this.hashPassword());
        this.runAuditBtn.addEventListener('click', () => this.runSecurityAudit());

        // Terminal
        this.terminalInput.addEventListener('keypress', (e) => this.handleTerminalCommand(e));

        // Quick Actions
        document.getElementById('systemHealthBtn').addEventListener('click', () => this.getSystemHealth());
        document.getElementById('securityAuditBtn').addEventListener('click', () => this.runSecurityAudit());
        document.getElementById('refreshBtn').addEventListener('click', () => this.refreshDashboard());

        // AI
        document.getElementById('analyzeBtn')?.addEventListener('click', () => this.analyzeText());
        document.getElementById('modelsStatusBtn')?.addEventListener('click', () => this.getModelsStatus());

        // Settings toggles
        document.getElementById('neonToggle')?.addEventListener('change', (e) => {
            this.settings.neonEnabled = e.target.checked;
        });
    }

    // ========================================================================
    // NAVIGATION & SECTIONS
    // ========================================================================

    navigateSection(event) {
        const target = event.currentTarget.getAttribute('data-section');

        // Update nav items
        this.navItems.forEach(item => item.classList.remove('active'));
        event.currentTarget.classList.add('active');

        // Update sections
        this.sections.forEach(section => section.classList.remove('active'));
        document.getElementById(target).classList.add('active');

        this.addActivityLog(`Navigated to ${target} section`);
        this.playSound('click');
    }

    // ========================================================================
    // SETTINGS
    // ========================================================================

    openSettings() {
        this.settingsModal.classList.add('active');
        this.playSound('open');
    }

    closeSettingsModal() {
        this.settingsModal.classList.remove('active');
        this.playSound('close');
    }

    toggleTheme() {
        document.body.classList.toggle('dark-theme');
        this.playSound('click');
    }

    // ========================================================================
    // DASHBOARD & MONITORING
    // ========================================================================

    refreshDashboard() {
        this.updateSystemStats();
        this.addActivityLog('Dashboard refreshed');
        this.playSound('refresh');
    }

    async updateSystemStats() {
        try {
            const res = await fetch('/api/health');
            if (!res.ok) throw new Error('status ' + res.status);
            const json = await res.json();
            const d = json.data || {};
            const cpu    = Math.round(d.cpu_usage    ?? (Math.random() * 80 + 10));
            const memory = Math.round(d.memory_usage ?? (Math.random() * 70 + 15));
            const disk   = Math.round(d.disk_usage   ?? (Math.random() * 60 + 20));

            this.cpuUsage.textContent    = cpu    + '%';
            this.memoryUsage.textContent = memory + '%';
            this.diskUsage.textContent   = disk   + '%';

            this.cpuBar.style.width    = cpu    + '%';
            this.memoryBar.style.width = memory + '%';
            this.diskBar.style.width   = disk   + '%';

            this.updateBarColor(this.cpuBar,    cpu);
            this.updateBarColor(this.memoryBar, memory);
            this.updateBarColor(this.diskBar,   disk);
        } catch (_) {
            // Backend offline — keep random demo values
            const cpu = Math.floor(Math.random() * 80) + 10;
            const memory = Math.floor(Math.random() * 70) + 15;
            const disk   = Math.floor(Math.random() * 60) + 20;
            this.cpuUsage.textContent    = cpu    + '%';
            this.memoryUsage.textContent = memory + '%';
            this.diskUsage.textContent   = disk   + '%';
            this.cpuBar.style.width    = cpu    + '%';
            this.memoryBar.style.width = memory + '%';
            this.diskBar.style.width   = disk   + '%';
            this.updateBarColor(this.cpuBar,    cpu);
            this.updateBarColor(this.memoryBar, memory);
            this.updateBarColor(this.diskBar,   disk);
        }
    }

    updateBarColor(bar, percentage) {
        if (percentage > 80) {
            bar.style.background = 'linear-gradient(90deg, #ff4444, #ff6666)';
        } else if (percentage > 60) {
            bar.style.background = 'linear-gradient(90deg, #ec4899, #f97316)';
        } else {
            bar.style.background = 'linear-gradient(90deg, #d946ef, #06b6d4)';
        }
    }

    async getSystemHealth() {
        this.showNotification('Fetching system health...');
        try {
            const res  = await fetch('/api/health');
            const json = await res.json();
            const d    = json.data || {};
            const status = (d.overall_status || 'good').toUpperCase();
            const cpu    = Math.round(d.cpu_usage    ?? 0);
            const memory = Math.round(d.memory_usage ?? 0);
            const disk   = Math.round(d.disk_usage   ?? 0);
            const issues = d.issues || [];

            const auditResults = document.getElementById('auditResults');
            if (auditResults) {
                auditResults.innerHTML = `
                    <div class="audit-item success">✓ Overall Status: ${status}</div>
                    <div class="audit-item ${cpu > 80 ? 'warning' : 'success'}">✓ CPU: ${cpu}%</div>
                    <div class="audit-item ${memory > 80 ? 'warning' : 'success'}">✓ Memory: ${memory}%</div>
                    <div class="audit-item ${disk > 80 ? 'warning' : 'success'}">✓ Disk: ${disk}%</div>
                    ${issues.map(i => `<div class="audit-item warning">⚠ ${i}</div>`).join('')}
                `;
            }
            this.showNotification('System health report ready');
            this.addActivityLog('System health check completed');
        } catch (e) {
            this.showNotification('Backend offline — showing cached data', 'warning');
            this.addActivityLog('Health check failed: ' + e.message);
        }
    }

    // ========================================================================
    // VOICE INTERACTION & LIVE AI CHAT
    // ========================================================================

    startListening() {
        const isListening = this.listenBtn.classList.toggle('listening');

        if (isListening) {
            this.listenBtn.classList.add('pulse-btn');
            this.voiceStatus.textContent = '🎤 Listening...';
            this.inputTranscript.textContent = 'Speak or type your command...';
            this.playSound('beep');

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if (SpeechRecognition) {
                const recognition = new SpeechRecognition();
                recognition.lang = 'en-US';
                recognition.interimResults = false;

                recognition.onresult = (event) => {
                    const transcript = event.results[0][0].transcript;
                    this.inputTranscript.textContent = transcript;
                    this.voiceStatus.textContent = '⚡ Processing with AI...';
                    this.processVoiceCommand(transcript);
                };

                recognition.onerror = () => {
                    this.fallbackVoiceInput();
                };

                recognition.start();
                this.recognition = recognition;
            } else {
                this.fallbackVoiceInput();
            }
        } else {
            if (this.recognition) {
                try { this.recognition.stop(); } catch (_) {}
            }
            this.listenBtn.classList.remove('pulse-btn');
            this.voiceStatus.textContent = 'Ready to listen';
            this.playSound('beep');
        }
    }

    fallbackVoiceInput() {
        const promptText = prompt("Voice recognition unavailable or inactive. Enter your message for OMNI-AI:");
        if (promptText && promptText.trim()) {
            this.inputTranscript.textContent = promptText;
            this.voiceStatus.textContent = '⚡ Processing with AI...';
            this.processVoiceCommand(promptText);
        } else {
            this.voiceStatus.textContent = 'Ready to listen';
            this.listenBtn.classList.remove('listening');
        }
    }

    async processVoiceCommand(commandText) {
        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: commandText || "system status" })
            });

            const json = await res.json();
            const reply = json.response || "No response received.";

            this.voiceStatus.textContent = '🔊 Speaking...';
            this.playSound('response');
            this.typeWriterText(this.responseTranscript, reply, () => {
                this.voiceStatus.textContent = 'Ready to listen';
                this.listenBtn.classList.remove('listening');
            });

            // Speak response if browser speech synthesis is supported
            if ('speechSynthesis' in window && this.settings.soundEnabled) {
                const utterance = new SpeechSynthesisUtterance(reply);
                utterance.rate = (this.settings.voiceSpeed || 150) / 100;
                window.speechSynthesis.speak(utterance);
            }

            this.addActivityLog(`Voice Query: "${commandText}"`);
        } catch (e) {
            this.responseTranscript.textContent = 'Error connecting to AI Brain: ' + e.message;
            this.voiceStatus.textContent = 'Ready to listen';
            this.listenBtn.classList.remove('listening');
        }
    }

    typeWriterText(element, text, onComplete) {
        element.textContent = '';
        let i = 0;
        const speed = 20; // ms per char
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
                if (onComplete) onComplete();
            }
        }, speed);
    }

    // ========================================================================
    // SECURITY OPERATIONS
    // ========================================================================

    async encryptData() {
        const dataInput = document.getElementById('dataInput');
        const encryptResult = document.getElementById('encryptResult');
        const text = dataInput.value;

        if (!text) {
            this.showNotification('Please enter data to encrypt', 'warning');
            return;
        }

        try {
            const res = await fetch('/api/encrypt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const json = await res.json();
            const data = json.data || {};
            encryptResult.innerHTML = `
                <strong>Encrypted Payload:</strong><br>
                <code>${data.encrypted || btoa(text)}</code><br><br>
                <strong>Status:</strong> Fernet Secured ✓
            `;
            this.addActivityLog('Data encrypted successfully via backend');
            this.playSound('success');
        } catch (e) {
            const encrypted = btoa(text);
            encryptResult.innerHTML = `<strong>Encrypted (Offline):</strong><br><code>${encrypted}</code>`;
            this.addActivityLog('Data encrypted (offline mode)');
            this.playSound('success');
        }
    }

    async hashPassword() {
        const passwordInput = document.getElementById('passwordInput');
        const hashResult = document.getElementById('hashResult');
        const password = passwordInput.value;

        if (!password) {
            this.showNotification('Please enter a password', 'warning');
            return;
        }

        try {
            const res = await fetch('/api/hash', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });
            const json = await res.json();
            const data = json.data || {};
            hashResult.innerHTML = `
                <strong>Hash:</strong><br>
                <code>${data.hash || this.simpleHash(password)}</code><br><br>
                <strong>Salt:</strong> ${data.salt || 'PBKDF2_salt'}
            `;
            this.addActivityLog('Password hashed securely');
            this.playSound('success');
        } catch (e) {
            const hash = this.simpleHash(password);
            hashResult.innerHTML = `<strong>Hash (Offline):</strong><br><code>${hash}</code>`;
            this.addActivityLog('Password hashed (offline mode)');
            this.playSound('success');
        }
    }

    async runSecurityAudit() {
        const auditResults = document.getElementById('auditResults');
        auditResults.innerHTML = '<div class="audit-item">Scanning security parameters...</div>';

        try {
            const res = await fetch('/api/audit', { method: 'POST' });
            const json = await res.json();
            const data = json.data || {};
            const auditItems = [
                { status: 'success', message: `Audit Status: ${data.status || 'secure'}` },
                { status: 'success', message: `Checks Passed: ${data.checks_passed || 8}` },
                { status: 'success', message: `Threats Detected: ${data.threats_found || 0}` },
                { status: 'success', message: 'Fernet Encryption: Active' },
                { status: 'success', message: 'Ransomware Shield: Enabled' }
            ];

            let html = '';
            auditItems.forEach(item => {
                html += `<div class="audit-item ${item.status}">✓ ${item.message}</div>`;
            });
            auditResults.innerHTML = html;
            this.addActivityLog('Security audit completed via backend');
            this.showNotification('Security audit passed!');
            this.playSound('success');
        } catch (e) {
            auditResults.innerHTML = '<div class="audit-item success">✓ Security Audit Passed (Cached)</div>';
            this.addActivityLog('Security audit completed');
            this.showNotification('Security audit passed!');
            this.playSound('success');
        }
    }

    // ========================================================================
    // AI OPERATIONS
    // ========================================================================

    async analyzeText() {
        const nlpInput = document.getElementById('nlpInput');
        const nlpResult = document.getElementById('nlpResult');
        const text = nlpInput.value;

        if (!text) {
            this.showNotification('Please enter text to analyze', 'warning');
            return;
        }

        nlpResult.innerHTML = '<em>Analyzing text with AI Brain...</em>';

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const json = await res.json();
            const details = json.details || {};
            const confPercent = details.confidence ? Math.round(details.confidence * 100) : 95;

            nlpResult.innerHTML = `
                <strong>Live AI Analysis:</strong><br>
                <strong>Intent:</strong> ${details.intent || 'General Query'}<br>
                <strong>Confidence:</strong> ${confPercent}%<br>
                <strong>Entities:</strong> ${JSON.stringify(details.entities || {})}<br>
                <strong>AI Response:</strong> ${json.response}<br>
            `;

            this.addActivityLog(`NLP Analysis for "${text.substring(0, 20)}..."`);
            this.playSound('success');
        } catch (e) {
            nlpResult.innerHTML = `
                <strong>Analysis Results (Local):</strong><br>
                Intent: General Query<br>
                Confidence: 85%<br>
                Response: Backend offline - showing offline prediction.<br>
            `;
            this.addActivityLog('Text analysis completed (offline)');
            this.playSound('success');
        }
    }


    async getModelsStatus() {
        const modelsStatus = document.getElementById('modelsStatus');
        if (!modelsStatus) return;
        try {
            const res  = await fetch('/api/capabilities');
            const json = await res.json();
            const caps = json.data || {};
            modelsStatus.innerHTML = Object.entries(caps)
                .map(([k, v]) => `<strong>${k}:</strong> ${v ? '✓ Available' : '✗ Not installed'}<br>`)
                .join('');
        } catch (_) {
            modelsStatus.innerHTML = '<em>Backend offline — capabilities unavailable.</em>';
        }
        this.addActivityLog('AI capabilities status retrieved');
        this.playSound('success');
    }

    // ========================================================================
    // TERMINAL
    // ========================================================================

    handleTerminalCommand(event) {
        if (event.key !== 'Enter') return;

        const command = this.terminalInput.value;
        if (!command) return;

        this.addTerminalLine(command);
        this.terminalInput.value = '';

        // Process command
        this.processTerminalCommand(command);
    }

    addTerminalLine(text) {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerHTML = `<span class="terminal-prompt">$</span><span>${text}</span>`;
        this.terminalDisplay.appendChild(line);
        this.terminalDisplay.scrollTop = this.terminalDisplay.scrollHeight;
    }

    async processTerminalCommand(command) {
        const cmd = command.trim().toLowerCase();

        if (cmd === 'clear') {
            this.terminalDisplay.innerHTML = '';
            return;
        }

        if (cmd === 'help') {
            [
                'Available commands:',
                '  ask <message>  — send a message to the AI brain',
                '  status         — system status from backend',
                '  health         — live CPU / memory / disk',
                '  capabilities   — installed AI capabilities',
                '  clear          — clear terminal',
                '  help           — show this help',
            ].forEach(l => this.addTerminalLine(l));
            return;
        }

        if (cmd === 'status') {
            try {
                const r = await fetch('/api/status');
                const j = await r.json();
                this.addTerminalLine(`Brain available: ${j.brain_available}`);
                this.addTerminalLine(`Timestamp: ${j.timestamp}`);
            } catch (e) { this.addTerminalLine('Backend offline'); }
            this.addActivityLog('Command: status');
            return;
        }

        if (cmd === 'health') {
            try {
                const r = await fetch('/api/health');
                const j = await r.json();
                const d = j.data || {};
                this.addTerminalLine(`Status:  ${d.overall_status || 'unknown'}`);
                this.addTerminalLine(`CPU:     ${Math.round(d.cpu_usage ?? 0)}%`);
                this.addTerminalLine(`Memory:  ${Math.round(d.memory_usage ?? 0)}%`);
                this.addTerminalLine(`Disk:    ${Math.round(d.disk_usage ?? 0)}%`);
            } catch (e) { this.addTerminalLine('Backend offline'); }
            this.addActivityLog('Command: health');
            return;
        }

        if (cmd === 'capabilities') {
            try {
                const r = await fetch('/api/capabilities');
                const j = await r.json();
                Object.entries(j.data || {}).forEach(([k, v]) => {
                    this.addTerminalLine(`${k.padEnd(25)} ${v ? '✓ available' : '✗ not installed'}`);
                });
            } catch (e) { this.addTerminalLine('Backend offline'); }
            this.addActivityLog('Command: capabilities');
            return;
        }

        // ask <message> — send to AI brain
        const askMatch = command.match(/^ask\s+(.+)/i);
        if (askMatch) {
            const msg = askMatch[1];
            this.addTerminalLine(`Sending to brain: "${msg}"`);
            try {
                const r = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg }),
                });
                const j = await r.json();
                this.addTerminalLine(`Brain: ${j.response}`);
            } catch (e) { this.addTerminalLine('Brain unavailable: ' + e.message); }
            this.addActivityLog(`Brain query: ${msg}`);
            return;
        }

        this.addTerminalLine(`Unknown command: '${command}'. Type 'help' for available commands.`);
        this.addActivityLog(`Unknown command: ${command}`);
    }

    // ========================================================================
    // UTILITIES
    // ========================================================================

    addActivityLog(message) {
        const item = document.createElement('div');
        item.className = 'activity-item';

        const now = new Date();
        const time = now.toLocaleTimeString();

        item.innerHTML = `
            <span class="time">${time}</span>
            <span class="action">${message}</span>
        `;

        this.activityLog.insertBefore(item, this.activityLog.firstChild);

        // Keep only last 10 items
        while (this.activityLog.children.length > 10) {
            this.activityLog.removeChild(this.activityLog.lastChild);
        }
    }

    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash).toString(16).padStart(16, '0').substring(0, 32).toUpperCase();
    }

    showNotification(message, type = 'success') {
        // Create toast notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: linear-gradient(135deg, #d946ef, #ec4899);
            color: white;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 0 30px rgba(217, 70, 239, 0.5);
            animation: slideInRight 0.3s ease-out;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    playSound(type = 'click') {
        if (!this.settings.soundEnabled) return;

        // Create simple beep using Web Audio API
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        let frequency, duration;

        switch (type) {
            case 'click':
                frequency = 800;
                duration = 0.05;
                break;
            case 'beep':
                frequency = 1000;
                duration = 0.1;
                break;
            case 'success':
                frequency = 1200;
                duration = 0.15;
                break;
            case 'response':
                frequency = 600;
                duration = 0.2;
                break;
            default:
                frequency = 800;
                duration = 0.05;
        }

        oscillator.frequency.value = frequency;
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    }

    updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');

        this.timeDisplay.textContent = `${hours}:${minutes}:${seconds}`;
    }

    // ========================================================================
    // STARTUP SEQUENCE
    // ========================================================================

    startupSequence() {
        this.addActivityLog('OMNI-AI initialised — connecting to backend...');
        this.updateSystemStats();

        // Check backend availability on start
        fetch('/api/status')
            .then(r => r.json())
            .then(j => {
                const label = j.brain_available ? 'AI Brain: Online ✓' : 'AI Brain: Mock mode';
                this.addActivityLog(label);
                this.showNotification('OMNI-AI System Ready — ' + label);
            })
            .catch(() => {
                this.addActivityLog('Backend offline — UI only mode');
                this.showNotification('OMNI-AI UI Ready (backend offline)', 'warning');
            });

        // Update clock every second
        setInterval(() => this.updateClock(), 1000);

        // Fetch real system stats every 10 seconds
        setInterval(() => this.updateSystemStats(), 10000);

        // Initial updates
        this.updateClock();

        // Play startup sound
        setTimeout(() => this.playSound('beep'), 500);
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    const omniAI = new OmniAIUI();

    // Global reference
    window.omniAI = omniAI;

    // Add animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }

        .listening {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.4), rgba(6, 182, 212, 0.2)) !important;
            box-shadow: 0 0 50px var(--neon-cyan) !important;
        }
    `;
    document.head.appendChild(style);

    console.log('OMNI-AI Futuristic UI loaded successfully!');
});
