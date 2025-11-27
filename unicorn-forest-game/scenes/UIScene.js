// UIScene.js
// HUD overlay showing lives, horn status, magic books, mushrooms, and timer

class UIScene extends Phaser.Scene {
    constructor() {
        super({ key: 'UIScene' });
    }

    create() {
        const { width, height } = this.cameras.main;

        // Create HUD panel at top
        this.createHUDPanel();

        // Create message display area
        this.createMessageArea();

        // Listen for updates from GameScene
        this.events.on('updateHUD', this.updateHUD, this);

        // Initialize with default values
        this.updateHUD({
            lives: 3,
            hasHorn: true,
            magicCharges: 0,
            collectedMushrooms: 0,
            targetMushrooms: 10,
            timeRemaining: 180,
            currentLevel: 1
        });
    }

    createHUDPanel() {
        const { width } = this.cameras.main;

        // Background panel
        this.hudPanel = this.add.rectangle(width / 2, 30, width - 20, 50, 0x000000, 0.6);
        this.hudPanel.setStrokeStyle(3, 0xffffff);

        // Level indicator
        this.levelText = this.add.text(20, 18, 'Level 1', {
            fontSize: '20px',
            fill: '#ffd700',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        });

        // Lives (hearts)
        this.heartsContainer = this.add.container(120, 30);
        this.hearts = [];
        for (let i = 0; i < 3; i++) {
            const heart = this.add.image(i * 35, 0, 'heart').setScale(0.8);
            this.hearts.push(heart);
            this.heartsContainer.add(heart);
        }

        // Horn status
        this.hornText = this.add.text(230, 18, '🦄 Horn: ON', {
            fontSize: '16px',
            fill: '#90ee90',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        });

        // Magic books count
        this.magicText = this.add.text(360, 18, '📚 Magic: 0', {
            fontSize: '16px',
            fill: '#dda0dd',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        });

        // Mushroom count
        this.mushroomText = this.add.text(490, 18, '🍄 0 / 10', {
            fontSize: '16px',
            fill: '#cd853f',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        });

        // Timer
        this.timerText = this.add.text(620, 18, '⏱️ 3:00', {
            fontSize: '16px',
            fill: '#87ceeb',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        });

        // Controls hint (bottom)
        this.add.text(width / 2, this.cameras.main.height - 15, 'Arrow Keys / WASD: Move | SPACE: Use Magic', {
            fontSize: '12px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);
    }

    createMessageArea() {
        const { width } = this.cameras.main;

        // Message text (centered, below HUD)
        this.messageText = this.add.text(width / 2, 80, '', {
            fontSize: '22px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#000000',
            strokeThickness: 4,
            align: 'center'
        }).setOrigin(0.5).setDepth(100);

        // Message background
        this.messageBg = this.add.rectangle(width / 2, 80, 1, 1, 0x000000, 0.7);
        this.messageBg.setVisible(false);
    }

    updateHUD(data) {
        // Update level
        this.levelText.setText(`Level ${data.currentLevel}`);

        // Update hearts
        for (let i = 0; i < 3; i++) {
            if (i < data.lives) {
                this.hearts[i].setTexture('heart');
                this.hearts[i].setAlpha(1);
            } else {
                this.hearts[i].setTexture('heart_empty');
                this.hearts[i].setAlpha(0.5);
            }
        }

        // Update horn status
        if (data.hasHorn) {
            this.hornText.setText('🦄 Horn: ON');
            this.hornText.setColor('#90ee90');
        } else {
            this.hornText.setText('🐴 Horn: OFF');
            this.hornText.setColor('#ff6b6b');

            // Flash effect when horn is lost
            this.tweens.add({
                targets: this.hornText,
                alpha: 0.3,
                duration: 200,
                yoyo: true,
                repeat: 2
            });
        }

        // Update magic charges
        this.magicText.setText(`📚 Magic: ${data.magicCharges}`);
        if (data.magicCharges > 0) {
            this.magicText.setColor('#ffd700');
        } else {
            this.magicText.setColor('#dda0dd');
        }

        // Update mushroom count
        this.mushroomText.setText(`🍄 ${data.collectedMushrooms} / ${data.targetMushrooms}`);

        // Change color based on progress
        const progress = data.collectedMushrooms / data.targetMushrooms;
        if (progress >= 1) {
            this.mushroomText.setColor('#90ee90');
        } else if (progress >= 0.5) {
            this.mushroomText.setColor('#ffd700');
        } else {
            this.mushroomText.setColor('#cd853f');
        }

        // Update timer
        const minutes = Math.floor(data.timeRemaining / 60);
        const seconds = data.timeRemaining % 60;
        const timeStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        this.timerText.setText(`⏱️ ${timeStr}`);

        // Change timer color when low
        if (data.timeRemaining <= 30) {
            this.timerText.setColor('#ff6b6b');
            // Flash effect
            if (data.timeRemaining <= 10) {
                this.tweens.add({
                    targets: this.timerText,
                    scale: 1.2,
                    duration: 200,
                    yoyo: true
                });
            }
        } else if (data.timeRemaining <= 60) {
            this.timerText.setColor('#ffd700');
        } else {
            this.timerText.setColor('#87ceeb');
        }
    }

    showMessage(text, duration = 2000) {
        const { width } = this.cameras.main;

        // Update message text
        this.messageText.setText(text);

        // Update background size
        const padding = 20;
        this.messageBg.setSize(this.messageText.width + padding * 2, this.messageText.height + padding);
        this.messageBg.setPosition(width / 2, 80);
        this.messageBg.setVisible(true);

        // Animate in
        this.messageText.setAlpha(0);
        this.messageBg.setAlpha(0);

        this.tweens.add({
            targets: [this.messageText, this.messageBg],
            alpha: 1,
            duration: 200
        });

        // Clear any existing timer
        if (this.messageTimer) {
            this.messageTimer.remove();
        }

        // Hide after duration
        this.messageTimer = this.time.delayedCall(duration, () => {
            this.tweens.add({
                targets: [this.messageText, this.messageBg],
                alpha: 0,
                duration: 200,
                onComplete: () => {
                    this.messageBg.setVisible(false);
                }
            });
        });
    }

    showLevelComplete(level, callback) {
        const { width, height } = this.cameras.main;

        // Create overlay
        const overlay = this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.8);
        overlay.setDepth(200);

        // Victory container
        const container = this.add.container(width / 2, height / 2).setDepth(201);

        // Background panel
        const panel = this.add.rectangle(0, 0, 400, 300, 0x228b22, 1);
        panel.setStrokeStyle(6, 0xffd700);
        container.add(panel);

        // Title
        const title = this.add.text(0, -100, '🎉 Level Complete! 🎉', {
            fontSize: '32px',
            fill: '#ffd700',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 4
        }).setOrigin(0.5);
        container.add(title);

        // Level number
        const levelText = this.add.text(0, -40, `Level ${level} Cleared!`, {
            fontSize: '24px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive'
        }).setOrigin(0.5);
        container.add(levelText);

        // Uni celebration
        const uni = this.add.image(0, 20, 'uni_horn').setScale(3);
        container.add(uni);

        // Bounce animation
        this.tweens.add({
            targets: uni,
            y: 10,
            duration: 300,
            yoyo: true,
            repeat: -1
        });

        // Next level button
        const button = this.add.rectangle(0, 100, 180, 50, 0xff69b4);
        button.setStrokeStyle(3, 0xff1493);
        button.setInteractive({ useHandCursor: true });
        container.add(button);

        const buttonText = this.add.text(0, 100, 'Next Level ▶', {
            fontSize: '22px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        container.add(buttonText);

        // Button hover
        button.on('pointerover', () => {
            button.setFillStyle(0xff1493);
        });
        button.on('pointerout', () => {
            button.setFillStyle(0xff69b4);
        });
        button.on('pointerdown', () => {
            container.destroy();
            overlay.destroy();
            if (callback) callback();
        });

        // Animate in
        container.setScale(0);
        this.tweens.add({
            targets: container,
            scale: 1,
            duration: 400,
            ease: 'Back.easeOut'
        });
    }

    showGameOver(callback) {
        const { width, height } = this.cameras.main;

        // Create overlay
        const overlay = this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.85);
        overlay.setDepth(200);

        // Container
        const container = this.add.container(width / 2, height / 2).setDepth(201);

        // Background panel
        const panel = this.add.rectangle(0, 0, 400, 320, 0x8b0000, 1);
        panel.setStrokeStyle(6, 0xff6b6b);
        container.add(panel);

        // Title
        const title = this.add.text(0, -110, '💔 Game Over 💔', {
            fontSize: '36px',
            fill: '#ff6b6b',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 4
        }).setOrigin(0.5);
        container.add(title);

        // Sad Uni
        const uni = this.add.image(0, -20, 'uni_no_horn').setScale(3);
        container.add(uni);

        // Sad animation
        this.tweens.add({
            targets: uni,
            angle: -5,
            duration: 500,
            yoyo: true,
            repeat: -1
        });

        // Message
        const msg = this.add.text(0, 50, 'Mr Fox caught Uni...', {
            fontSize: '20px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive'
        }).setOrigin(0.5);
        container.add(msg);

        // Restart button
        const button = this.add.rectangle(0, 110, 180, 50, 0xff69b4);
        button.setStrokeStyle(3, 0xff1493);
        button.setInteractive({ useHandCursor: true });
        container.add(button);

        const buttonText = this.add.text(0, 110, '🔄 Try Again', {
            fontSize: '22px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        container.add(buttonText);

        // Button hover
        button.on('pointerover', () => {
            button.setFillStyle(0xff1493);
        });
        button.on('pointerout', () => {
            button.setFillStyle(0xff69b4);
        });
        button.on('pointerdown', () => {
            container.destroy();
            overlay.destroy();
            if (callback) callback();
        });

        // Animate in
        container.setScale(0);
        this.tweens.add({
            targets: container,
            scale: 1,
            duration: 400,
            ease: 'Back.easeOut'
        });
    }

    showVictory(callback) {
        const { width, height } = this.cameras.main;

        // Create overlay
        const overlay = this.add.rectangle(width / 2, height / 2, width, height, 0x000000, 0.8);
        overlay.setDepth(200);

        // Container
        const container = this.add.container(width / 2, height / 2).setDepth(201);

        // Background panel - golden
        const panel = this.add.rectangle(0, 0, 450, 350, 0x4a0080, 1);
        panel.setStrokeStyle(8, 0xffd700);
        container.add(panel);

        // Title
        const title = this.add.text(0, -130, '🏆 YOU WIN! 🏆', {
            fontSize: '42px',
            fill: '#ffd700',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold',
            stroke: '#000000',
            strokeThickness: 5
        }).setOrigin(0.5);
        container.add(title);

        // Victory message
        const msg1 = this.add.text(0, -70, 'Uni is the', {
            fontSize: '22px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive'
        }).setOrigin(0.5);
        container.add(msg1);

        const msg2 = this.add.text(0, -40, '🥧 Mushroom Pie Champion! 🥧', {
            fontSize: '26px',
            fill: '#ffd700',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        container.add(msg2);

        // Happy Uni
        const uni = this.add.image(0, 40, 'uni_horn').setScale(4);
        container.add(uni);

        // Celebration animation
        this.tweens.add({
            targets: uni,
            y: 30,
            angle: 10,
            duration: 400,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Create sparkles
        for (let i = 0; i < 20; i++) {
            const sparkle = this.add.circle(
                Phaser.Math.Between(-200, 200),
                Phaser.Math.Between(-150, 120),
                Phaser.Math.Between(3, 8),
                Phaser.Math.RND.pick([0xffd700, 0xff69b4, 0x87ceeb, 0xffffff])
            );
            container.add(sparkle);

            this.tweens.add({
                targets: sparkle,
                alpha: 0.3,
                scale: 0.5,
                duration: Phaser.Math.Between(400, 800),
                yoyo: true,
                repeat: -1
            });
        }

        // Play again button
        const button = this.add.rectangle(0, 130, 200, 55, 0xff69b4);
        button.setStrokeStyle(4, 0xff1493);
        button.setInteractive({ useHandCursor: true });
        container.add(button);

        const buttonText = this.add.text(0, 130, '🎮 Play Again', {
            fontSize: '24px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        }).setOrigin(0.5);
        container.add(buttonText);

        // Button hover
        button.on('pointerover', () => {
            button.setFillStyle(0xff1493);
        });
        button.on('pointerout', () => {
            button.setFillStyle(0xff69b4);
        });
        button.on('pointerdown', () => {
            container.destroy();
            overlay.destroy();
            if (callback) callback();
        });

        // Animate in
        container.setScale(0);
        this.tweens.add({
            targets: container,
            scale: 1,
            duration: 500,
            ease: 'Back.easeOut'
        });
    }
}
