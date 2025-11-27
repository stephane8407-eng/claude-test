// SoundManager.js
// Generates fun synthesized sound effects using Web Audio API

class SoundManager {
    constructor() {
        this.audioContext = null;
        this.enabled = true;
        this.volume = 0.3;
    }

    init() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Web Audio API not supported');
            this.enabled = false;
        }
    }

    // Resume audio context (needed after user interaction)
    resume() {
        if (this.audioContext && this.audioContext.state === 'suspended') {
            this.audioContext.resume();
        }
    }

    toggle() {
        this.enabled = !this.enabled;
        return this.enabled;
    }

    // Play a simple tone
    playTone(frequency, duration, type = 'sine', volumeMult = 1) {
        if (!this.enabled || !this.audioContext) return;

        this.resume();

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.type = type;
        oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);

        gainNode.gain.setValueAtTime(this.volume * volumeMult, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }

    // Play a sequence of tones (melody)
    playMelody(notes, tempo = 150) {
        if (!this.enabled || !this.audioContext) return;

        notes.forEach((note, index) => {
            setTimeout(() => {
                this.playTone(note.freq, note.duration || 0.15, note.type || 'sine', note.vol || 1);
            }, index * tempo);
        });
    }

    // ========== GAME SOUND EFFECTS ==========

    // Collect safe mushroom - happy "bloop"
    collectMushroom() {
        this.playMelody([
            { freq: 523, duration: 0.08 },  // C5
            { freq: 659, duration: 0.12 }   // E5
        ], 80);
    }

    // Collect magic book - sparkly ascending
    collectBook() {
        this.playMelody([
            { freq: 523, duration: 0.1, type: 'triangle' },  // C5
            { freq: 659, duration: 0.1, type: 'triangle' },  // E5
            { freq: 784, duration: 0.1, type: 'triangle' },  // G5
            { freq: 1047, duration: 0.2, type: 'triangle' }  // C6
        ], 100);
    }

    // Touch poison mushroom - bad buzz
    poison() {
        this.playTone(150, 0.3, 'sawtooth', 0.5);
        setTimeout(() => {
            this.playTone(100, 0.4, 'sawtooth', 0.4);
        }, 100);
    }

    // Lose horn - sad descending
    loseHorn() {
        this.playMelody([
            { freq: 440, duration: 0.15, type: 'triangle' },  // A4
            { freq: 349, duration: 0.15, type: 'triangle' },  // F4
            { freq: 294, duration: 0.25, type: 'triangle' }   // D4
        ], 150);
    }

    // Lose life - dramatic
    loseLife() {
        this.playMelody([
            { freq: 392, duration: 0.2, type: 'sawtooth', vol: 0.6 },  // G4
            { freq: 330, duration: 0.2, type: 'sawtooth', vol: 0.5 },  // E4
            { freq: 262, duration: 0.3, type: 'sawtooth', vol: 0.4 },  // C4
            { freq: 196, duration: 0.4, type: 'sawtooth', vol: 0.3 }   // G3
        ], 200);
    }

    // Use magic - mystical whoosh
    useMagic() {
        if (!this.enabled || !this.audioContext) return;

        this.resume();

        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(300, this.audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(1200, this.audioContext.currentTime + 0.3);

        gainNode.gain.setValueAtTime(this.volume * 0.5, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.4);

        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + 0.4);

        // Add sparkle
        setTimeout(() => {
            this.playMelody([
                { freq: 880, duration: 0.05 },
                { freq: 1100, duration: 0.05 },
                { freq: 1320, duration: 0.1 }
            ], 50);
        }, 200);
    }

    // Fox transforms to chicken - funny "bawk"
    foxToChicken() {
        this.playMelody([
            { freq: 600, duration: 0.1, type: 'square', vol: 0.4 },
            { freq: 800, duration: 0.08, type: 'square', vol: 0.3 },
            { freq: 500, duration: 0.15, type: 'square', vol: 0.4 }
        ], 80);
    }

    // Chicken back to fox - growl
    chickenToFox() {
        this.playTone(200, 0.2, 'sawtooth', 0.4);
        setTimeout(() => {
            this.playTone(150, 0.3, 'sawtooth', 0.5);
        }, 150);
    }

    // Visit Mr Owl - wise hoot sequence
    owlHoot() {
        this.playMelody([
            { freq: 330, duration: 0.3, type: 'sine', vol: 0.6 },  // E4
            { freq: 262, duration: 0.4, type: 'sine', vol: 0.5 }   // C4
        ], 350);
    }

    // Horn restored - magical triumph
    hornRestored() {
        this.playMelody([
            { freq: 523, duration: 0.1, type: 'triangle' },   // C5
            { freq: 659, duration: 0.1, type: 'triangle' },   // E5
            { freq: 784, duration: 0.1, type: 'triangle' },   // G5
            { freq: 1047, duration: 0.15, type: 'triangle' }, // C6
            { freq: 1319, duration: 0.25, type: 'triangle' }  // E6
        ], 120);
    }

    // Level complete - victory fanfare
    levelComplete() {
        this.playMelody([
            { freq: 523, duration: 0.15, type: 'square', vol: 0.5 },  // C5
            { freq: 523, duration: 0.15, type: 'square', vol: 0.5 },  // C5
            { freq: 523, duration: 0.15, type: 'square', vol: 0.5 },  // C5
            { freq: 659, duration: 0.4, type: 'square', vol: 0.6 },   // E5
            { freq: 784, duration: 0.15, type: 'square', vol: 0.5 },  // G5
            { freq: 659, duration: 0.15, type: 'square', vol: 0.5 },  // E5
            { freq: 784, duration: 0.5, type: 'square', vol: 0.6 }    // G5
        ], 150);
    }

    // Game over - sad trombone
    gameOver() {
        this.playMelody([
            { freq: 493, duration: 0.3, type: 'sawtooth', vol: 0.4 },  // B4
            { freq: 466, duration: 0.3, type: 'sawtooth', vol: 0.4 },  // Bb4
            { freq: 440, duration: 0.3, type: 'sawtooth', vol: 0.4 },  // A4
            { freq: 392, duration: 0.6, type: 'sawtooth', vol: 0.5 }   // G4
        ], 300);
    }

    // Victory - triumphant fanfare
    victory() {
        this.playMelody([
            { freq: 523, duration: 0.2, type: 'square', vol: 0.5 },   // C5
            { freq: 659, duration: 0.2, type: 'square', vol: 0.5 },   // E5
            { freq: 784, duration: 0.2, type: 'square', vol: 0.5 },   // G5
            { freq: 1047, duration: 0.4, type: 'square', vol: 0.6 },  // C6
            { freq: 784, duration: 0.15, type: 'square', vol: 0.5 },  // G5
            { freq: 1047, duration: 0.6, type: 'square', vol: 0.7 }   // C6
        ], 180);
    }

    // Button click
    buttonClick() {
        this.playTone(600, 0.08, 'square', 0.3);
    }

    // Timer warning (low time)
    timerWarning() {
        this.playTone(880, 0.1, 'square', 0.3);
    }

    // Time up
    timeUp() {
        this.playMelody([
            { freq: 440, duration: 0.2, type: 'sawtooth', vol: 0.5 },
            { freq: 330, duration: 0.3, type: 'sawtooth', vol: 0.4 }
        ], 200);
    }

    // Footstep (optional - for movement)
    footstep() {
        this.playTone(100 + Math.random() * 50, 0.05, 'triangle', 0.15);
    }
}

// Create global instance
const soundManager = new SoundManager();
