// MiniPupper Web Controller JavaScript
// Handles Web Bluetooth connection and joystick input

const SERVICE_UUID = '0d9be2a0-4757-43d9-83df-704ae274b8df';
const CHARACTERISTIC_UUID = '8116d8c0-d45d-4fdf-998e-33ab8c471d59';

class MiniPupperController {
    constructor() {
        this.device = null;
        this.characteristic = null;
        this.isConnected = false;
        
        // Controller state
        this.state = {
            lx: 0.0,  // Left stick X
            ly: 0.0,  // Left stick Y
            rx: 0.0,  // Right stick X
            ry: 0.0,  // Right stick Y
            dpadx: 0, // D-pad X
            dpady: 0, // D-pad Y
            R1: 0,
            L1: 0,
            x: 0,
            circle: 0,
            triangle: 0,
            message_rate: 50
        };
        
        this.updateInterval = null;
        this.joystickActiveLeft = false;
        this.joystickActiveRight = false;
        
        this.init();
    }
    
    init() {
        // Connect button
        document.getElementById('connectBtn').addEventListener('click', () => this.connect());
        
        // Initialize joysticks
        this.initJoystick('left', document.getElementById('leftJoystick'), document.getElementById('leftStick'));
        this.initJoystick('right', document.getElementById('rightJoystick'), document.getElementById('rightStick'));
        
        // Initialize buttons
        this.initButton('btnL1', 'L1');
        this.initButton('btnR1', 'R1');
        this.initButton('btnX', 'x');
        this.initButton('btnCircle', 'circle');
        this.initButton('btnTriangle', 'triangle');
        
        // Initialize D-pad
        this.initDpad();
    }
    
    async connect() {
        try {
            this.updateStatus('connecting', 'Connecting...');
            document.getElementById('connectBtn').disabled = true;
            
            // Request Bluetooth device
            this.device = await navigator.bluetooth.requestDevice({
                filters: [{ name: 'Minipupper-v2' }],
                optionalServices: [SERVICE_UUID]
            });
            
            console.log('Device selected:', this.device.name);
            
            // Connect to GATT server
            const server = await this.device.gatt.connect();
            console.log('Connected to GATT server');
            
            // Get service
            const service = await server.getPrimaryService(SERVICE_UUID);
            console.log('Got service');
            
            // Get characteristic
            this.characteristic = await service.getCharacteristic(CHARACTERISTIC_UUID);
            console.log('Got characteristic');
            
            // Start notifications
            await this.characteristic.startNotifications();
            this.characteristic.addEventListener('characteristicvaluechanged', (event) => {
                this.handleNotification(event.target.value);
            });
            
            this.isConnected = true;
            this.updateStatus('connected', 'Connected');
            document.getElementById('controls').classList.add('active');
            
            // Start sending updates
            this.startUpdates();
            
            // Handle disconnection
            this.device.addEventListener('gattserverdisconnected', () => {
                this.onDisconnected();
            });
            
        } catch (error) {
            console.error('Connection failed:', error);
            this.updateStatus('disconnected', 'Connection failed');
            document.getElementById('connectBtn').disabled = false;
            alert('Connection failed: ' + error.message);
        }
    }
    
    onDisconnected() {
        console.log('Device disconnected');
        this.isConnected = false;
        this.stopUpdates();
        this.updateStatus('disconnected', 'Disconnected');
        document.getElementById('controls').classList.remove('active');
        document.getElementById('connectBtn').disabled = false;
    }
    
    updateStatus(status, text) {
        const statusEl = document.getElementById('status');
        statusEl.className = 'status ' + status;
        statusEl.textContent = text;
    }
    
    startUpdates() {
        // Send state updates at 20Hz
        this.updateInterval = setInterval(() => {
            this.sendState();
        }, 50); // 20Hz
    }
    
    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }
    
    async sendState() {
        if (!this.isConnected || !this.characteristic) return;
        
        try {
            const message = {
                type: 'joystick',
                data: this.state
            };
            
            const json = JSON.stringify(message);
            const encoder = new TextEncoder();
            const data = encoder.encode(json);
            
            await this.characteristic.writeValue(data);
            
        } catch (error) {
            console.error('Failed to send state:', error);
        }
    }
    
    handleNotification(value) {
        const decoder = new TextDecoder();
        const text = decoder.decode(value);
        console.log('Received:', text);
    }
    
    initJoystick(side, container, stick) {
        const rect = container.getBoundingClientRect();
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        const maxRadius = rect.width / 2 - 30; // Account for stick size
        
        let isDragging = false;
        
        const updateStickPosition = (clientX, clientY) => {
            const rect = container.getBoundingClientRect();
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            let x = clientX - rect.left - centerX;
            let y = clientY - rect.top - centerY;
            
            // Limit to circular boundary
            const distance = Math.sqrt(x * x + y * y);
            if (distance > maxRadius) {
                const angle = Math.atan2(y, x);
                x = Math.cos(angle) * maxRadius;
                y = Math.sin(angle) * maxRadius;
            }
            
            // Update visual position
            stick.style.transform = `translate(calc(-50% + ${x}px), calc(-50% + ${y}px))`;
            
            // Update state (-1.0 to 1.0)
            const normalizedX = x / maxRadius;
            const normalizedY = y / maxRadius;
            
            if (side === 'left') {
                this.state.lx = normalizedX;
                this.state.ly = -normalizedY; // Invert Y
                document.getElementById('infoLeft').textContent = 
                    `X: ${normalizedX.toFixed(2)}, Y: ${(-normalizedY).toFixed(2)}`;
            } else {
                this.state.rx = normalizedX;
                this.state.ry = -normalizedY; // Invert Y
                document.getElementById('infoRight').textContent = 
                    `X: ${normalizedX.toFixed(2)}, Y: ${(-normalizedY).toFixed(2)}`;
            }
        };
        
        const resetStick = () => {
            stick.style.transform = 'translate(-50%, -50%)';
            if (side === 'left') {
                this.state.lx = 0;
                this.state.ly = 0;
                document.getElementById('infoLeft').textContent = 'X: 0.00, Y: 0.00';
            } else {
                this.state.rx = 0;
                this.state.ry = 0;
                document.getElementById('infoRight').textContent = 'X: 0.00, Y: 0.00';
            }
        };
        
        // Mouse events
        stick.addEventListener('mousedown', (e) => {
            isDragging = true;
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (isDragging) {
                updateStickPosition(e.clientX, e.clientY);
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isDragging) {
                isDragging = false;
                resetStick();
            }
        });
        
        // Touch events
        stick.addEventListener('touchstart', (e) => {
            isDragging = true;
            e.preventDefault();
        });
        
        document.addEventListener('touchmove', (e) => {
            if (isDragging && e.touches.length > 0) {
                updateStickPosition(e.touches[0].clientX, e.touches[0].clientY);
            }
        });
        
        document.addEventListener('touchend', () => {
            if (isDragging) {
                isDragging = false;
                resetStick();
            }
        });
    }
    
    initButton(elementId, stateKey) {
        const button = document.getElementById(elementId);
        let isToggle = (stateKey === 'R1' || stateKey === 'L1');
        
        const activate = () => {
            if (isToggle) {
                this.state[stateKey] = this.state[stateKey] ? 0 : 1;
                if (this.state[stateKey]) {
                    button.classList.add('toggle-on');
                } else {
                    button.classList.remove('toggle-on');
                }
            } else {
                this.state[stateKey] = 1;
            }
        };
        
        const deactivate = () => {
            if (!isToggle) {
                this.state[stateKey] = 0;
            }
        };
        
        button.addEventListener('mousedown', activate);
        button.addEventListener('mouseup', deactivate);
        button.addEventListener('mouseleave', deactivate);
        button.addEventListener('touchstart', (e) => {
            e.preventDefault();
            activate();
        });
        button.addEventListener('touchend', (e) => {
            e.preventDefault();
            deactivate();
        });
    }
    
    initDpad() {
        const buttons = document.querySelectorAll('.dpad-btn:not(.empty)');
        
        buttons.forEach(btn => {
            const direction = btn.dataset.dpad;
            
            const activate = () => {
                switch(direction) {
                    case 'up':
                        this.state.dpady = 1;
                        break;
                    case 'down':
                        this.state.dpady = -1;
                        break;
                    case 'left':
                        this.state.dpadx = -1;
                        break;
                    case 'right':
                        this.state.dpadx = 1;
                        break;
                }
                this.updateDpadInfo();
            };
            
            const deactivate = () => {
                switch(direction) {
                    case 'up':
                    case 'down':
                        this.state.dpady = 0;
                        break;
                    case 'left':
                    case 'right':
                        this.state.dpadx = 0;
                        break;
                }
                this.updateDpadInfo();
            };
            
            btn.addEventListener('mousedown', activate);
            btn.addEventListener('mouseup', deactivate);
            btn.addEventListener('mouseleave', deactivate);
            btn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                activate();
            });
            btn.addEventListener('touchend', (e) => {
                e.preventDefault();
                deactivate();
            });
        });
    }
    
    updateDpadInfo() {
        document.getElementById('infoDpad').textContent = 
            `X: ${this.state.dpadx}, Y: ${this.state.dpady}`;
    }
}

// Initialize controller when page loads
let controller;
window.addEventListener('DOMContentLoaded', () => {
    controller = new MiniPupperController();
});
