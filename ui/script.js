/* ============================================================================
   OMNI-AI FUTURISTIC UI - JAVASCRIPT
   Interactive Features & Backend Integration
   ============================================================================ */

class OmniAIUI {
    constructor() {
        this.settings = {
            neonEnabled: true,
            soundEnabled: true,
            animationsEnabled: true,
            voiceSpeed: 150
        };
        this.initializeElements();
        this.setupEventListeners();
        this.startupSequence();
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
        this.voiceTextInput = document.getElementById('voiceTextInput');

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
        this.systemOnlineStatus = document.getElementById('systemOnlineStatus');
        this.networkStatus = document.getElementById('networkStatus');
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
        this.settingsModal.addEventListener('click', (event) => {
            if (event.target === this.settingsModal) this.closeSettingsModal();
        });
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape' && this.settingsModal.classList.contains('active')) {
                this.closeSettingsModal();
            }
        });

        // Voice
        this.listenBtn.addEventListener('click', () => this.startListening());
        document.getElementById('speakBtn').addEventListener('click', () => this.speakResponse());
        document.getElementById('voiceSendBtn').addEventListener('click', () => this.sendTypedMessage());
        this.voiceTextInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') this.sendTypedMessage();
        });

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
            document.body.classList.toggle('reduced-glow', !e.target.checked);
        });
        document.getElementById('soundToggle')?.addEventListener('change', (e) => {
            this.settings.soundEnabled = e.target.checked;
        });
        document.getElementById('animToggle')?.addEventListener('change', (e) => {
            this.settings.animationsEnabled = e.target.checked;
            document.body.classList.toggle('reduced-motion', !e.target.checked);
        });
        document.getElementById('voiceSpeedSlider')?.addEventListener('input', (e) => {
            this.settings.voiceSpeed = Number(e.target.value);
        });
    }

    // ========================================================================
    // NAVIGATION & SECTIONS
    // ========================================================================

    navigateSection(event) {
        const target = event.currentTarget.getAttribute('data-section');
        const targetSection = document.getElementById(target);
        if (!targetSection) return;

        // Update nav items
        this.navItems.forEach(item => {
            item.classList.remove('active');
            item.setAttribute('aria-current', 'false');
        });
        event.currentTarget.classList.add('active');
        event.currentTarget.setAttribute('aria-current', 'page');

        // Update sections
        this.sections.forEach(section => section.classList.remove('active'));
        targetSection.classList.add('active');

        this.addActivityLog(`Navigated to ${target} section`);
        if (target === 'monitor') this.updateSystemMonitor();
        this.playSound('click');
    }

    // ========================================================================
    // SETTINGS
    // ========================================================================

    openSettings() {
        this.settingsModal.classList.add('active');
        this.settingsModal.setAttribute('aria-hidden', 'false');
        this.closeSettings.focus();
        this.playSound('open');
    }

    closeSettingsModal() {
        this.settingsModal.classList.remove('active');
        this.settingsModal.setAttribute('aria-hidden', 'true');
        this.settingsBtn.focus();
        this.playSound('close');
    }

    toggleTheme() {
        const lightTheme = document.body.classList.toggle('light-theme');
        this.themePulse.setAttribute('aria-label', lightTheme ? 'Switch to dark theme' : 'Switch to light theme');
        this.playSound('click');
    }

    // ========================================================================
    // DASHBOARD & MONITORING
    // ========================================================================

    refreshDashboard() {
        this.updateSystemStats();
        this.updateSystemMonitor();
        this.addActivityLog('Dashboard refreshed');
        this.playSound('refresh');
    }

    async updateSystemStats() {
        try {
            const json = await this.requestJson('/api/health');
            const d = json.data;
            this.setStat(this.cpuUsage, this.cpuBar, d.cpu_usage);
            this.setStat(this.memoryUsage, this.memoryBar, d.memory_usage);
            this.setStat(this.diskUsage, this.diskBar, d.disk_usage);
            this.networkStatus.textContent = 'Connected';
            this.systemOnlineStatus.textContent = 'System connected';
        } catch (error) {
            [this.cpuUsage, this.memoryUsage, this.diskUsage].forEach((value) => {
                value.textContent = 'Unavailable';
            });
            [this.cpuBar, this.memoryBar, this.diskBar].forEach((bar) => {
                bar.style.width = '0%';
            });
            this.networkStatus.textContent = 'Offline';
            this.systemOnlineStatus.textContent = 'Backend offline';
        }
    }

    setStat(value, bar, rawValue) {
        const percentage = Number(rawValue);
        if (!Number.isFinite(percentage)) {
            value.textContent = 'Unavailable';
            bar.style.width = '0%';
            return;
        }
        const safePercentage = Math.min(100, Math.max(0, percentage));
        value.textContent = `${Math.round(safePercentage)}%`;
        bar.style.width = `${safePercentage}%`;
        this.updateBarColor(bar, safePercentage);
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
            const json = await this.requestJson('/api/health');
            const d = json.data;

            const auditResults = document.getElementById('auditResults');
            if (auditResults) {
                const metrics = [
                    ['System status', d.overall_status],
                    ['CPU', `${Math.round(d.cpu_usage)}%`],
                    ['Memory', `${Math.round(d.memory_usage)}%`],
                    ['Disk', `${Math.round(d.disk_usage)}%`],
                ];
                auditResults.replaceChildren();
                metrics.forEach(([label, value]) => {
                    const item = document.createElement('div');
                    item.className = 'audit-item';
                    item.textContent = `${label}: ${value}`;
                    auditResults.appendChild(item);
                });
            }
            this.showNotification('System health report ready');
            this.addActivityLog('System health check completed');
        } catch (error) {
            this.showNotification(error.message, 'error');
            this.addActivityLog(`Health check failed: ${error.message}`);
        }
    }

    async updateSystemMonitor() {
        try {
            const json = await this.requestJson('/api/monitor');
            const data = json.data;
            const health = await this.requestJson('/api/health');
            this.setStat(
                document.getElementById('monitorCpuValue'),
                document.getElementById('monitorCpuBar'),
                health.data.cpu_usage,
            );
            this.setStat(
                document.getElementById('monitorMemoryValue'),
                document.getElementById('monitorMemoryBar'),
                health.data.memory_usage,
            );
            document.getElementById('uptimeValue').textContent =
                this.formatDuration(data.uptime_seconds);

            const processOverview = document.getElementById('processOverview');
            processOverview.replaceChildren();
            const count = document.createElement('p');
            count.textContent = `${data.process_count} processes running`;
            processOverview.appendChild(count);
            data.processes.forEach((process) => {
                const row = document.createElement('div');
                row.className = 'process-item';
                row.textContent = `${process.name} · PID ${process.pid} · ${Number(process.memory_percent).toFixed(1)}% memory`;
                processOverview.appendChild(row);
            });

            const systemHealth = document.getElementById('systemHealth');
            systemHealth.replaceChildren();
            const healthStatus = document.createElement('div');
            healthStatus.className = 'health-item';
            healthStatus.textContent = `System status: ${health.data.overall_status}`;
            systemHealth.appendChild(healthStatus);
        } catch (error) {
            document.getElementById('uptimeValue').textContent = 'Unavailable';
            document.getElementById('processOverview').textContent =
                `Monitoring unavailable: ${error.message}`;
            document.getElementById('systemHealth').textContent = 'Monitoring unavailable';
        }
    }

    formatDuration(rawSeconds) {
        const totalSeconds = Math.max(0, Math.floor(Number(rawSeconds) || 0));
        const days = Math.floor(totalSeconds / 86400);
        const hours = Math.floor((totalSeconds % 86400) / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        const time = `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        return days ? `${days}d ${time}` : time;
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
        this.voiceStatus.textContent = 'Voice recognition unavailable. Type your message below.';
        this.listenBtn.classList.remove('listening', 'pulse-btn');
        this.voiceTextInput.focus();
        this.showNotification('Voice recognition is unavailable. You can type instead.', 'warning');
    }

    sendTypedMessage() {
        const message = this.voiceTextInput.value.trim();
        if (!message) {
            this.showNotification('Enter a message first', 'warning');
            this.voiceTextInput.focus();
            return;
        }
        this.voiceTextInput.value = '';
        this.inputTranscript.textContent = message;
        this.voiceStatus.textContent = 'Processing…';
        this.processVoiceCommand(message);
    }

    async processVoiceCommand(commandText) {
        try {
            const json = await this.requestJson('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: commandText || "system status" })
            });
            const reply = json.response;

            this.voiceStatus.textContent = '🔊 Speaking...';
            this.playSound('response');
            this.typeWriterText(this.responseTranscript, reply, () => {
                this.voiceStatus.textContent = 'Ready to listen';
                this.listenBtn.classList.remove('listening');
            });
            this.speakResponse(reply);

            this.addActivityLog(`Voice Query: "${commandText}"`);
        } catch (error) {
            this.responseTranscript.textContent = `Unable to reach the AI service: ${error.message}`;
            this.voiceStatus.textContent = 'Ready to listen';
            this.listenBtn.classList.remove('listening');
        }
    }

    speakResponse(text = this.responseTranscript.textContent) {
        if (!('speechSynthesis' in window) || !text) {
            this.showNotification('Speech output is not available in this browser', 'warning');
            return;
        }
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = this.settings.voiceSpeed / 100;
        window.speechSynthesis.speak(utterance);
    }

    typeWriterText(element, text, onComplete) {
        element.textContent = '';
        text = String(text || '');
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

        if (!text.trim()) {
            this.showNotification('Please enter data to encrypt', 'warning');
            return;
        }

        try {
            const json = await this.requestJson('/api/encrypt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = json.data;
            this.renderResult(encryptResult, [
                ['Encrypted payload', data.encrypted],
                ['Recovery key (store separately)', data.key],
                ['Algorithm', data.algorithm],
                ['Important', data.key_warning],
            ]);
            this.addActivityLog('Data encrypted successfully via backend');
            this.playSound('success');
            this.showNotification('Data encrypted. Save the recovery key separately.');
        } catch (error) {
            encryptResult.textContent = `Encryption failed: ${error.message}`;
            this.addActivityLog(`Encryption failed: ${error.message}`);
            this.showNotification(error.message, 'error');
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
            const json = await this.requestJson('/api/hash', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password })
            });
            const data = json.data;
            this.renderResult(hashResult, [
                ['Hash', data.hash],
                ['Salt', data.salt],
                ['Algorithm', data.algorithm],
                ['Iterations', data.iterations],
            ]);
            passwordInput.value = '';
            this.addActivityLog('Password hashed securely');
            this.playSound('success');
        } catch (error) {
            hashResult.textContent = `Password hashing failed: ${error.message}`;
            this.addActivityLog(`Password hashing failed: ${error.message}`);
            this.showNotification(error.message, 'error');
        }
    }

    async runSecurityAudit() {
        const auditResults = document.getElementById('auditResults');
        auditResults.textContent = 'Checking local application configuration…';

        try {
            const json = await this.requestJson('/api/audit', { method: 'POST' });
            const data = json.data;
            auditResults.replaceChildren();
            data.checks.forEach((check) => {
                const item = document.createElement('div');
                item.className = `audit-item ${check.status === 'passed' ? 'success' : 'warning'}`;
                item.textContent = `${check.status === 'passed' ? '✓' : '⚠'} ${check.name}: ${check.detail}`;
                auditResults.appendChild(item);
            });
            const scope = document.createElement('p');
            scope.className = 'audit-scope';
            scope.textContent = data.scope;
            auditResults.appendChild(scope);
            this.addActivityLog(`Local configuration checks: ${data.status}`);
            this.showNotification(`Configuration checks ${data.status}`, data.status === 'passed' ? 'success' : 'warning');
        } catch (error) {
            auditResults.textContent = `Configuration checks failed: ${error.message}`;
            this.addActivityLog(`Configuration checks failed: ${error.message}`);
            this.showNotification(error.message, 'error');
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
            const json = await this.requestJson('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });
            const details = json.details || {};
            const result = [
                ['Intent', details.intent || 'General query'],
                ['Confidence', Number.isFinite(details.confidence) ? `${Math.round(details.confidence * 100)}%` : 'Not reported'],
                ['Entities', JSON.stringify(details.entities || {})],
                ['AI response', json.response],
            ];
            this.renderResult(nlpResult, result);

            this.addActivityLog(`NLP Analysis for "${text.substring(0, 20)}..."`);
            this.playSound('success');
        } catch (error) {
            nlpResult.textContent = `Analysis unavailable: ${error.message}`;
            this.addActivityLog(`Text analysis failed: ${error.message}`);
            this.showNotification(error.message, 'error');
        }
    }


    async getModelsStatus() {
        const modelsStatus = document.getElementById('modelsStatus');
        if (!modelsStatus) return;
        try {
            const json = await this.requestJson('/api/capabilities');
            const caps = json.data;
            this.renderResult(modelsStatus, Object.entries(caps).map(([name, installed]) => [
                name,
                installed ? 'Available' : 'Not installed',
            ]));
            this.setCapabilityBadge('tensorflowStatus', caps.tensorflow);
            this.setCapabilityBadge('pytorchStatus', caps.pytorch);
            this.setCapabilityBadge('encryptionStatus', caps.encryption);
            this.setCapabilityBadge('monitorStatus', caps.system_monitoring);
            this.setCapabilityBadge(
                'voiceEngineStatus',
                caps.speech_recognition || caps.text_to_speech,
            );
        } catch (error) {
            modelsStatus.textContent = `Capabilities unavailable: ${error.message}`;
        }
        this.addActivityLog('AI capabilities status retrieved');
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
        const prompt = document.createElement('span');
        prompt.className = 'terminal-prompt';
        prompt.textContent = '$';
        const content = document.createElement('span');
        content.textContent = String(text);
        line.append(prompt, content);
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
                const j = await this.requestJson('/api/status');
                this.addTerminalLine(`Brain available: ${j.brain_available}`);
                this.addTerminalLine(`Timestamp: ${j.timestamp}`);
            } catch (error) { this.addTerminalLine(`Backend unavailable: ${error.message}`); }
            this.addActivityLog('Command: status');
            return;
        }

        if (cmd === 'health') {
            try {
                const j = await this.requestJson('/api/health');
                const d = j.data || {};
                this.addTerminalLine(`Status:  ${d.overall_status || 'unknown'}`);
                this.addTerminalLine(`CPU:     ${Math.round(d.cpu_usage ?? 0)}%`);
                this.addTerminalLine(`Memory:  ${Math.round(d.memory_usage ?? 0)}%`);
                this.addTerminalLine(`Disk:    ${Math.round(d.disk_usage ?? 0)}%`);
            } catch (error) { this.addTerminalLine(`Backend unavailable: ${error.message}`); }
            this.addActivityLog('Command: health');
            return;
        }

        if (cmd === 'capabilities') {
            try {
                const j = await this.requestJson('/api/capabilities');
                Object.entries(j.data || {}).forEach(([k, v]) => {
                    this.addTerminalLine(`${k.padEnd(25)} ${v ? '✓ available' : '✗ not installed'}`);
                });
            } catch (error) { this.addTerminalLine(`Backend unavailable: ${error.message}`); }
            this.addActivityLog('Command: capabilities');
            return;
        }

        // ask <message> — send to AI brain
        const askMatch = command.match(/^ask\s+(.+)/i);
        if (askMatch) {
            const msg = askMatch[1];
            this.addTerminalLine(`Sending to brain: "${msg}"`);
            try {
                const j = await this.requestJson('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: msg }),
                });
                this.addTerminalLine(`Brain: ${j.response}`);
            } catch (error) { this.addTerminalLine(`Brain unavailable: ${error.message}`); }
            this.addActivityLog(`Brain query: ${msg}`);
            return;
        }

        this.addTerminalLine(`Unknown command: '${command}'. Type 'help' for available commands.`);
        this.addActivityLog(`Unknown command: ${command}`);
    }

    // ========================================================================
    // UTILITIES
    // ========================================================================

    async requestJson(url, options = {}) {
        const response = await fetch(url, options);
        let payload;
        try {
            payload = await response.json();
        } catch {
            throw new Error(`The server returned an invalid response (${response.status})`);
        }
        if (!response.ok || payload.success === false) {
            throw new Error(payload.error || `Request failed (${response.status})`);
        }
        return payload;
    }

    renderResult(container, entries) {
        container.replaceChildren();
        entries.forEach(([label, value]) => {
            const row = document.createElement('div');
            const heading = document.createElement('strong');
            heading.textContent = `${label}: `;
            const content = document.createElement('span');
            content.textContent = String(value ?? 'Not reported');
            row.append(heading, content);
            container.appendChild(row);
        });
    }

    setCapabilityBadge(id, available) {
        const badge = document.getElementById(id);
        if (!badge) return;
        const isAvailable = Boolean(available);
        badge.textContent = isAvailable ? 'Available' : 'Not installed';
        badge.classList.toggle('unavailable', !isAvailable);
    }

    addActivityLog(message) {
        const item = document.createElement('div');
        item.className = 'activity-item';

        const now = new Date();
        const time = now.toLocaleTimeString();

        const timeLabel = document.createElement('span');
        timeLabel.className = 'time';
        timeLabel.textContent = time;
        const action = document.createElement('span');
        action.className = 'action';
        action.textContent = String(message);
        item.append(timeLabel, action);

        this.activityLog.insertBefore(item, this.activityLog.firstChild);

        // Keep only last 10 items
        while (this.activityLog.children.length > 10) {
            this.activityLog.removeChild(this.activityLog.lastChild);
        }
    }

    showNotification(message, type = 'success') {
        // Create toast notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'error' ? '#b42318' : type === 'warning' ? '#9a6700' : 'linear-gradient(135deg, #d946ef, #ec4899)'};
            color: white;
            border-radius: 10px;
            z-index: 10000;
            box-shadow: 0 0 30px rgba(217, 70, 239, 0.5);
            animation: slideInRight 0.3s ease-out;
        `;
        notification.setAttribute('role', type === 'error' ? 'alert' : 'status');
        notification.textContent = String(message);
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    playSound(type = 'click') {
        if (!this.settings.soundEnabled) return;

        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;

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

        try {
            const audioContext = this.audioContext || (this.audioContext = new AudioContext());
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            oscillator.frequency.value = frequency;
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration);
        } catch (error) {
            console.warn('Sound effects are unavailable:', error.message);
        }
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
        this.getModelsStatus();

        // Check backend availability on start
        this.requestJson('/api/status')
            .then((j) => {
                const label = j.brain_available ? 'AI brain ready' : 'AI running in mock mode';
                document.getElementById('brainStatus').textContent = j.brain_available ? 'Ready' : 'Mock mode';
                this.systemOnlineStatus.textContent = 'System connected';
                this.addActivityLog(label);
                this.showNotification('OMNI-AI System Ready — ' + label);
            })
            .catch((error) => {
                document.getElementById('brainStatus').textContent = 'Unavailable';
                this.systemOnlineStatus.textContent = 'Backend offline';
                this.addActivityLog('Backend offline — UI only mode');
                this.showNotification(`Backend unavailable: ${error.message}`, 'warning');
            });

        // Update clock every second
        setInterval(() => this.updateClock(), 1000);

        // Fetch real system stats every 10 seconds
        setInterval(() => {
            this.updateSystemStats();
            this.updateSystemMonitor();
        }, 10000);

        // Initial updates
        this.updateClock();
        this.updateSystemMonitor();

        // Play startup sound
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
