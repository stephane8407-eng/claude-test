/**
 * UI Scene
 * Heads-Up Display showing lives, mushroom count, timer, etc.
 * Runs parallel to the game scene
 */

class UIScene extends Phaser.Scene {
    constructor() {
        super({ key: 'UIScene' });
    }

    create() {
        // HUD background
        this.hudBg = this.add.graphics();
        this.hudBg.fillStyle(0x000000, 0.6);
        this.hudBg.fillRect(0, 0, GAME_CONFIG.width, 50);

        // Level indicator
        this.levelText = this.add.text(20, 15, 'Level: 1', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '18px',
            fill: '#ffd700'
        });

        // Lives display
        this.livesContainer = this.add.container(150, 15);
        this.livesText = this.add.text(0, 0, 'Lives:', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '18px',
            fill: '#ffffff'
        });
        this.livesContainer.add(this.livesText);
        this.hearts = [];
        this.updateLivesDisplay(GameState.lives);

        // Mushroom counter
        this.mushroomText = this.add.text(350, 15, 'Mushrooms: 0 / 10', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '18px',
            fill: '#90EE90'
        });

        // Timer
        this.timerText = this.add.text(580, 15, 'Time: 3:00', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '18px',
            fill: '#ffffff'
        });

        // Horn status indicator
        this.hornIndicator = this.add.graphics();
        this.updateHornIndicator(GameState.hasHorn);
        this.hornText = this.add.text(720, 15, '', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '14px',
            fill: '#ffd700'
        });

        // Freeze overlay (hidden by default)
        this.freezeOverlay = this.add.graphics();
        this.freezeOverlay.setVisible(false);

        // Pause overlay (hidden by default)
        this.pauseOverlay = this.createPauseOverlay();
        this.pauseOverlay.setVisible(false);

        // Message display area
        this.messageText = this.add.text(GAME_CONFIG.width / 2, GAME_CONFIG.height / 2, '', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '32px',
            fill: '#ffd700',
            stroke: '#000000',
            strokeThickness: 4
        }).setOrigin(0.5).setVisible(false);

        // Listen for events from GameScene
        this.setupEventListeners();
    }

    setupEventListeners() {
        const gameScene = this.scene.get('GameScene');

        // Game start
        gameScene.events.on('gameStart', (data) => {
            this.levelText.setText(`Level: ${data.level}`);
            this.updateLivesDisplay(data.lives);
            this.updateMushroomCount(data.mushrooms, data.target);
            this.updateTimer(data.time);
            this.updateHornIndicator(data.hasHorn);
        });

        // Mushroom collected
        gameScene.events.on('mushroomCollected', (data) => {
            this.updateMushroomCount(data.collected, data.target);
            this.showFloatingText('+1', 0x90EE90);
        });

        // Player frozen
        gameScene.events.on('playerFrozen', (data) => {
            this.showFreezeEffect(data.duration);
        });

        // Player unfrozen
        gameScene.events.on('playerUnfrozen', () => {
            this.hideFreezeEffect();
        });

        // Lives changed
        gameScene.events.on('livesChanged', (data) => {
            this.updateLivesDisplay(data.lives);
            this.updateHornIndicator(data.hasHorn);
        });

        // Horn lost
        gameScene.events.on('hornLost', () => {
            this.updateHornIndicator(false);
            this.showFloatingText('Horn Lost!', 0xff0000);
        });

        // Horn restored
        gameScene.events.on('hornRestored', () => {
            this.updateHornIndicator(true);
            this.showFloatingText('Horn Restored!', 0xffd700);
        });

        // Timer update
        gameScene.events.on('timerUpdate', (data) => {
            this.updateTimer(data.time);
        });

        // Time warning
        gameScene.events.on('timeWarning', () => {
            this.timerText.setFill('#ff0000');
            this.tweens.add({
                targets: this.timerText,
                scale: 1.2,
                duration: 200,
                yoyo: true,
                repeat: 5
            });
        });

        // Level complete
        gameScene.events.on('levelComplete', (data) => {
            this.showMessage(`Level ${data.level} Complete!`, 0x00ff00);
        });

        // Game over
        gameScene.events.on('gameOver', (data) => {
            this.showMessage('Game Over!', 0xff0000);
        });

        // Game paused
        gameScene.events.on('gamePaused', () => {
            this.pauseOverlay.setVisible(true);
        });

        // Game resumed
        gameScene.events.on('gameResumed', () => {
            this.pauseOverlay.setVisible(false);
        });
    }

    updateLivesDisplay(lives) {
        // Clear existing hearts
        this.hearts.forEach(heart => heart.destroy());
        this.hearts = [];

        // Draw new hearts
        for (let i = 0; i < lives; i++) {
            const heart = this.add.graphics();
            const x = 60 + i * 25;

            // Draw heart shape
            heart.fillStyle(0xff0000);
            heart.fillCircle(x, 5, 8);
            heart.fillCircle(x + 10, 5, 8);
            heart.fillTriangle(x - 8, 5, x + 18, 5, x + 5, 18);

            this.livesContainer.add(heart);
            this.hearts.push(heart);
        }
    }

    updateMushroomCount(collected, target) {
        this.mushroomText.setText(`Mushrooms: ${collected} / ${target}`);

        // Pulse effect when collecting
        this.tweens.add({
            targets: this.mushroomText,
            scale: 1.2,
            duration: 100,
            yoyo: true
        });
    }

    updateTimer(seconds) {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        const timeString = `${minutes}:${secs.toString().padStart(2, '0')}`;
        this.timerText.setText(`Time: ${timeString}`);
    }

    updateHornIndicator(hasHorn) {
        this.hornIndicator.clear();

        if (hasHorn) {
            // Draw golden horn icon
            this.hornIndicator.fillStyle(0xffd700);
            this.hornIndicator.fillTriangle(710, 35, 700, 15, 720, 15);
            this.hornText.setText('');
        } else {
            // Draw broken horn icon
            this.hornIndicator.fillStyle(0x808080);
            this.hornIndicator.fillTriangle(710, 35, 705, 25, 715, 25);
            this.hornText.setText('Lost!');
            this.hornText.setFill('#ff6b6b');
        }
    }

    showFreezeEffect(duration) {
        // Blue tinted overlay
        this.freezeOverlay.clear();
        this.freezeOverlay.fillStyle(0x87ceeb, 0.3);
        this.freezeOverlay.fillRect(0, 0, GAME_CONFIG.width, GAME_CONFIG.height);
        this.freezeOverlay.setVisible(true);

        // Frozen text
        this.showMessage('FROZEN!', 0x87ceeb);

        // Auto-hide after duration
        this.time.delayedCall(duration, () => {
            this.hideFreezeEffect();
        });
    }

    hideFreezeEffect() {
        this.freezeOverlay.setVisible(false);
        this.messageText.setVisible(false);
    }

    createPauseOverlay() {
        const container = this.add.container(0, 0);

        // Dark overlay
        const overlay = this.add.graphics();
        overlay.fillStyle(0x000000, 0.7);
        overlay.fillRect(0, 0, GAME_CONFIG.width, GAME_CONFIG.height);

        // Pause text
        const pauseText = this.add.text(GAME_CONFIG.width / 2, GAME_CONFIG.height / 2 - 30, 'PAUSED', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '48px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // Instructions
        const instructionText = this.add.text(GAME_CONFIG.width / 2, GAME_CONFIG.height / 2 + 30, 'Press ESC or P to resume', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '20px',
            fill: '#cccccc'
        }).setOrigin(0.5);

        container.add([overlay, pauseText, instructionText]);

        return container;
    }

    showMessage(text, color) {
        this.messageText.setText(text);
        this.messageText.setFill(Phaser.Display.Color.IntegerToColor(color).rgba);
        this.messageText.setVisible(true);

        // Animate in
        this.messageText.setScale(0);
        this.tweens.add({
            targets: this.messageText,
            scale: 1,
            duration: 300,
            ease: 'Back.easeOut'
        });
    }

    showFloatingText(text, color) {
        const floatText = this.add.text(
            GAME_CONFIG.width / 2,
            100,
            text,
            {
                fontFamily: 'Comic Sans MS, cursive',
                fontSize: '24px',
                fill: Phaser.Display.Color.IntegerToColor(color).rgba,
                stroke: '#000000',
                strokeThickness: 2
            }
        ).setOrigin(0.5);

        // Animate up and fade
        this.tweens.add({
            targets: floatText,
            y: floatText.y - 50,
            alpha: 0,
            duration: 1000,
            ease: 'Power2',
            onComplete: () => floatText.destroy()
        });
    }
}
