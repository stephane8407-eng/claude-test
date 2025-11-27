/**
 * Game Over Scene
 * Shows results and allows replay or continue to next level
 */

class GameOverScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameOverScene' });
    }

    init(data) {
        this.won = data.won || false;
        this.reason = data.reason || '';
        this.level = data.level || 1;
        this.score = data.score || 0;
        this.canContinue = data.canContinue || false;
    }

    create() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        // Background
        const bg = this.add.graphics();
        if (this.won) {
            bg.fillGradientStyle(0x1a5c1a, 0x1a5c1a, 0x2d8a2d, 0x2d8a2d, 1);
        } else {
            bg.fillGradientStyle(0x5c1a1a, 0x5c1a1a, 0x8a2d2d, 0x8a2d2d, 1);
        }
        bg.fillRect(0, 0, width, height);

        // Add decorative elements
        this.createDecorations();

        // Title
        const titleText = this.won ? 'Level Complete!' : 'Game Over';
        const titleColor = this.won ? '#ffd700' : '#ff6b6b';

        this.add.text(width / 2, 80, titleText, {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '48px',
            fill: titleColor,
            stroke: '#000000',
            strokeThickness: 6
        }).setOrigin(0.5);

        // Show character reaction
        if (this.won) {
            this.createHappyUni(width / 2, 200);
        } else {
            this.createSadUni(width / 2 - 80, 200);
            this.createHappyFox(width / 2 + 80, 200);
        }

        // Results panel
        this.createResultsPanel(width / 2, 350);

        // Buttons
        if (this.won && this.canContinue) {
            // Continue to next level
            this.createButton(width / 2, 480, 'Next Level', () => {
                this.scene.start('GameScene');
                this.scene.start('UIScene');
            });

            this.createButton(width / 2, 540, 'Main Menu', () => {
                GameState.reset();
                this.scene.start('MenuScene');
            });
        } else {
            // Try again or menu
            this.createButton(width / 2, 480, 'Try Again', () => {
                if (!this.won) {
                    // Reset for retry
                    GameState.lives = GAME_CONFIG.player.startLives;
                    GameState.hasHorn = true;
                }
                this.scene.start('GameScene');
                this.scene.start('UIScene');
            });

            this.createButton(width / 2, 540, 'Main Menu', () => {
                GameState.reset();
                this.scene.start('MenuScene');
            });
        }

        // Show reason if lost
        if (!this.won && this.reason) {
            this.add.text(width / 2, height - 30, this.reason, {
                fontFamily: 'Comic Sans MS, cursive',
                fontSize: '16px',
                fill: '#ff9999'
            }).setOrigin(0.5);
        }
    }

    createDecorations() {
        // Floating particles
        for (let i = 0; i < 20; i++) {
            const particle = this.add.graphics();
            const color = this.won ? 0xffd700 : 0xff6b6b;
            particle.fillStyle(color, 0.5);
            particle.fillCircle(0, 0, 3 + Math.random() * 5);

            particle.x = Math.random() * GAME_CONFIG.width;
            particle.y = Math.random() * GAME_CONFIG.height;

            // Floating animation
            this.tweens.add({
                targets: particle,
                y: particle.y - 50 - Math.random() * 50,
                alpha: 0,
                duration: 2000 + Math.random() * 2000,
                repeat: -1,
                delay: Math.random() * 2000
            });
        }
    }

    createHappyUni(x, y) {
        const uni = this.add.graphics();

        // Body
        uni.fillStyle(GAME_CONFIG.colors.unicornBody);
        uni.fillEllipse(x, y, 60, 40);

        // Mane
        uni.fillStyle(GAME_CONFIG.colors.unicornMane);
        uni.fillEllipse(x - 22, y - 12, 22, 30);

        // Horn with sparkle
        uni.fillStyle(GAME_CONFIG.colors.unicornHorn);
        uni.fillTriangle(x + 22, y - 25, x + 15, y - 10, x + 29, y - 10);

        // Happy eyes (closed arcs)
        uni.lineStyle(3, 0x000000);
        uni.beginPath();
        uni.arc(x + 12, y - 8, 6, 0.2, Math.PI - 0.2);
        uni.strokePath();

        // Smile
        uni.beginPath();
        uni.arc(x + 15, y + 5, 8, 0.2, Math.PI - 0.2);
        uni.strokePath();

        // Sparkles around
        this.createSparkles(x, y - 30);

        // Bouncing animation
        this.tweens.add({
            targets: uni,
            y: y - 10,
            duration: 500,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }

    createSadUni(x, y) {
        const uni = this.add.graphics();

        // Body (slightly gray - sad)
        uni.fillStyle(0xdddddd);
        uni.fillEllipse(x, y, 50, 35);

        // Mane (droopy)
        uni.fillStyle(0xffb6c1);
        uni.fillEllipse(x - 18, y - 5, 18, 22);

        // No horn (lost)
        // Just a small stub
        uni.fillStyle(0xcccccc);
        uni.fillTriangle(x + 15, y - 12, x + 12, y - 5, x + 18, y - 5);

        // Sad eyes
        uni.fillStyle(0x000000);
        uni.fillCircle(x + 12, y - 5, 5);

        // Tear
        uni.fillStyle(0x87ceeb);
        uni.fillEllipse(x + 18, y + 2, 3, 5);

        // Frown
        uni.lineStyle(2, 0x000000);
        uni.beginPath();
        uni.arc(x + 15, y + 12, 6, Math.PI + 0.3, -0.3);
        uni.strokePath();
    }

    createHappyFox(x, y) {
        const fox = this.add.graphics();

        // Body
        fox.fillStyle(GAME_CONFIG.colors.foxBody);
        fox.fillEllipse(x, y, 45, 30);

        // Head
        fox.fillCircle(x + 18, y - 6, 15);

        // Ears
        fox.fillTriangle(x + 12, y - 22, x + 10, y - 10, x + 18, y - 12);
        fox.fillTriangle(x + 24, y - 22, x + 18, y - 10, x + 26, y - 12);

        // Happy eyes (closed)
        fox.lineStyle(3, 0x000000);
        fox.beginPath();
        fox.arc(x + 14, y - 10, 4, 0.2, Math.PI - 0.2);
        fox.strokePath();
        fox.beginPath();
        fox.arc(x + 22, y - 10, 4, 0.2, Math.PI - 0.2);
        fox.strokePath();

        // Big grin
        fox.fillStyle(0xffffff);
        fox.fillEllipse(x + 28, y - 2, 12, 8);
        fox.lineStyle(2, 0x000000);
        fox.beginPath();
        fox.arc(x + 28, y - 4, 6, 0.2, Math.PI - 0.2);
        fox.strokePath();

        // Tail wagging
        const tail = this.add.graphics();
        tail.fillStyle(GAME_CONFIG.colors.foxBody);
        tail.fillEllipse(x - 25, y + 5, 25, 10);
        tail.fillStyle(0xffffff);
        tail.fillCircle(x - 35, y + 5, 6);

        this.tweens.add({
            targets: tail,
            angle: 15,
            duration: 200,
            yoyo: true,
            repeat: -1
        });
    }

    createSparkles(x, y) {
        for (let i = 0; i < 5; i++) {
            const sparkle = this.add.graphics();
            const sx = x - 30 + Math.random() * 60;
            const sy = y - 20 + Math.random() * 40;

            sparkle.fillStyle(0xffd700);
            sparkle.fillStar(sx, sy, 4, 8, 4);

            this.tweens.add({
                targets: sparkle,
                alpha: 0,
                scale: 0,
                duration: 500 + Math.random() * 500,
                repeat: -1,
                yoyo: true,
                delay: Math.random() * 500
            });
        }
    }

    createResultsPanel(x, y) {
        // Panel background
        const panel = this.add.graphics();
        panel.fillStyle(0x000000, 0.5);
        panel.fillRoundedRect(x - 150, y - 60, 300, 120, 15);
        panel.lineStyle(3, this.won ? 0xffd700 : 0xff6b6b);
        panel.strokeRoundedRect(x - 150, y - 60, 300, 120, 15);

        // Level
        this.add.text(x, y - 40, `Level: ${this.level}`, {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '20px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // Score
        this.add.text(x, y, `Score: ${this.score}`, {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '24px',
            fill: '#ffd700'
        }).setOrigin(0.5);

        // Status message
        const statusText = this.won
            ? (this.canContinue ? 'Ready for the next challenge?' : 'You completed all levels!')
            : 'Better luck next time!';

        this.add.text(x, y + 40, statusText, {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '16px',
            fill: '#cccccc'
        }).setOrigin(0.5);
    }

    createButton(x, y, text, callback) {
        // Button background
        const button = this.add.graphics();
        const buttonColor = this.won ? 0x4CAF50 : 0x2196F3;
        const hoverColor = this.won ? 0x66BB6A : 0x42A5F5;

        button.fillStyle(buttonColor);
        button.fillRoundedRect(x - 100, y - 22, 200, 44, 10);
        button.lineStyle(2, 0xffffff, 0.3);
        button.strokeRoundedRect(x - 100, y - 22, 200, 44, 10);

        // Button text
        const buttonText = this.add.text(x, y, text, {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '20px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // Hit area
        const hitArea = this.add.rectangle(x, y, 200, 44, 0x000000, 0);
        hitArea.setInteractive({ useHandCursor: true });

        hitArea.on('pointerover', () => {
            button.clear();
            button.fillStyle(hoverColor);
            button.fillRoundedRect(x - 100, y - 22, 200, 44, 10);
            button.lineStyle(2, 0xffffff, 0.5);
            button.strokeRoundedRect(x - 100, y - 22, 200, 44, 10);
            buttonText.setScale(1.05);
        });

        hitArea.on('pointerout', () => {
            button.clear();
            button.fillStyle(buttonColor);
            button.fillRoundedRect(x - 100, y - 22, 200, 44, 10);
            button.lineStyle(2, 0xffffff, 0.3);
            button.strokeRoundedRect(x - 100, y - 22, 200, 44, 10);
            buttonText.setScale(1);
        });

        hitArea.on('pointerdown', callback);
    }
}
