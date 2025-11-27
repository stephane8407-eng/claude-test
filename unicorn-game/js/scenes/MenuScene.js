/**
 * Menu Scene
 * Main menu with title and start button
 */

class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
    }

    create() {
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        // Create forest background
        this.createBackground();

        // Title
        const titleText = this.add.text(width / 2, 100, "Uni's Mushroom Adventure", {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '42px',
            fill: '#ffd700',
            stroke: '#2d5a27',
            strokeThickness: 6
        }).setOrigin(0.5);

        // Subtitle
        this.add.text(width / 2, 150, 'Help Uni collect mushrooms in the forest!', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '18px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // Draw Uni preview
        this.createUniPreview(width / 2 - 80, height / 2);

        // Draw Fox preview
        this.createFoxPreview(width / 2 + 80, height / 2);

        // VS text
        this.add.text(width / 2, height / 2, 'VS', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '28px',
            fill: '#ff0000',
            stroke: '#000000',
            strokeThickness: 3
        }).setOrigin(0.5);

        // Start button
        const startButton = this.createButton(width / 2, height / 2 + 120, 'START GAME', () => {
            this.scene.start('GameScene');
            this.scene.start('UIScene');
        });

        // Instructions
        const instructionsBg = this.add.graphics();
        instructionsBg.fillStyle(0x000000, 0.5);
        instructionsBg.fillRoundedRect(width / 2 - 200, height - 120, 400, 100, 10);

        this.add.text(width / 2, height - 95, 'How to Play:', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '18px',
            fill: '#ffd700'
        }).setOrigin(0.5);

        this.add.text(width / 2, height - 65, 'Use Arrow Keys or WASD to move Uni', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '14px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        this.add.text(width / 2, height - 45, 'Collect 10 brown mushrooms to win!', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '14px',
            fill: '#90EE90'
        }).setOrigin(0.5);

        this.add.text(width / 2, height - 25, 'Avoid Mr Fox and red mushrooms!', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '14px',
            fill: '#ff6b6b'
        }).setOrigin(0.5);

        // Animate title
        this.tweens.add({
            targets: titleText,
            y: 105,
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }

    createBackground() {
        // Gradient green background
        const bg = this.add.graphics();
        bg.fillGradientStyle(0x1a472a, 0x1a472a, 0x2d5a3f, 0x2d5a3f, 1);
        bg.fillRect(0, 0, GAME_CONFIG.width, GAME_CONFIG.height);

        // Add some decorative trees
        for (let i = 0; i < 8; i++) {
            this.createTree(
                50 + Math.random() * (GAME_CONFIG.width - 100),
                200 + Math.random() * (GAME_CONFIG.height - 300)
            );
        }

        // Add some grass patches
        for (let i = 0; i < 20; i++) {
            const grass = this.add.graphics();
            grass.fillStyle(0x32cd32, 0.6);
            const x = Math.random() * GAME_CONFIG.width;
            const y = Math.random() * GAME_CONFIG.height;
            grass.fillEllipse(x, y, 20 + Math.random() * 30, 10 + Math.random() * 15);
        }
    }

    createTree(x, y) {
        const tree = this.add.graphics();

        // Trunk
        tree.fillStyle(0x8b4513);
        tree.fillRect(x - 8, y, 16, 40);

        // Foliage (multiple circles)
        tree.fillStyle(GAME_CONFIG.colors.tree, 0.8);
        tree.fillCircle(x, y - 15, 25);
        tree.fillCircle(x - 15, y, 20);
        tree.fillCircle(x + 15, y, 20);
        tree.fillCircle(x, y + 5, 18);
    }

    createUniPreview(x, y) {
        const uni = this.add.graphics();

        // Body
        uni.fillStyle(GAME_CONFIG.colors.unicornBody);
        uni.fillEllipse(x, y, 50, 35);

        // Mane
        uni.fillStyle(GAME_CONFIG.colors.unicornMane);
        uni.fillEllipse(x - 18, y - 10, 18, 25);

        // Horn
        uni.fillStyle(GAME_CONFIG.colors.unicornHorn);
        uni.fillTriangle(x + 18, y - 20, x + 12, y - 8, x + 24, y - 8);

        // Eye
        uni.fillStyle(0x000000);
        uni.fillCircle(x + 15, y - 6, 5);

        // Label
        this.add.text(x, y + 45, 'Uni', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '20px',
            fill: '#ffffff',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);

        // Floating animation
        this.tweens.add({
            targets: { y: y },
            y: y - 10,
            duration: 800,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut',
            onUpdate: (tween) => {
                uni.clear();
                const newY = y - 10 + (10 * (1 - tween.progress));

                // Redraw at new position
                uni.fillStyle(GAME_CONFIG.colors.unicornBody);
                uni.fillEllipse(x, newY, 50, 35);
                uni.fillStyle(GAME_CONFIG.colors.unicornMane);
                uni.fillEllipse(x - 18, newY - 10, 18, 25);
                uni.fillStyle(GAME_CONFIG.colors.unicornHorn);
                uni.fillTriangle(x + 18, newY - 20, x + 12, newY - 8, x + 24, newY - 8);
                uni.fillStyle(0x000000);
                uni.fillCircle(x + 15, newY - 6, 5);
            }
        });
    }

    createFoxPreview(x, y) {
        const fox = this.add.graphics();

        // Body
        fox.fillStyle(GAME_CONFIG.colors.foxBody);
        fox.fillEllipse(x, y, 45, 30);

        // Head
        fox.fillCircle(x + 18, y - 6, 15);

        // Ears
        fox.fillTriangle(x + 12, y - 22, x + 10, y - 10, x + 18, y - 12);
        fox.fillTriangle(x + 24, y - 22, x + 18, y - 10, x + 26, y - 12);

        // Snout
        fox.fillStyle(0xffffff);
        fox.fillEllipse(x + 28, y - 4, 10, 8);

        // Nose
        fox.fillStyle(0x000000);
        fox.fillCircle(x + 32, y - 5, 3);

        // Eyes
        fox.fillStyle(0xffff00);
        fox.fillCircle(x + 14, y - 10, 4);
        fox.fillCircle(x + 22, y - 10, 4);

        // Tail
        fox.fillStyle(GAME_CONFIG.colors.foxBody);
        fox.fillEllipse(x - 25, y + 5, 25, 10);
        fox.fillStyle(0xffffff);
        fox.fillCircle(x - 35, y + 5, 6);

        // Label
        this.add.text(x, y + 45, 'Mr Fox', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '20px',
            fill: '#ff6600',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);
    }

    createButton(x, y, text, callback) {
        // Button background
        const button = this.add.graphics();
        button.fillStyle(0x4CAF50);
        button.fillRoundedRect(x - 100, y - 25, 200, 50, 10);
        button.lineStyle(3, 0x2E7D32);
        button.strokeRoundedRect(x - 100, y - 25, 200, 50, 10);

        // Button text
        const buttonText = this.add.text(x, y, text, {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '24px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // Make interactive
        const hitArea = this.add.rectangle(x, y, 200, 50, 0x000000, 0);
        hitArea.setInteractive({ useHandCursor: true });

        hitArea.on('pointerover', () => {
            button.clear();
            button.fillStyle(0x66BB6A);
            button.fillRoundedRect(x - 100, y - 25, 200, 50, 10);
            button.lineStyle(3, 0x2E7D32);
            button.strokeRoundedRect(x - 100, y - 25, 200, 50, 10);
        });

        hitArea.on('pointerout', () => {
            button.clear();
            button.fillStyle(0x4CAF50);
            button.fillRoundedRect(x - 100, y - 25, 200, 50, 10);
            button.lineStyle(3, 0x2E7D32);
            button.strokeRoundedRect(x - 100, y - 25, 200, 50, 10);
        });

        hitArea.on('pointerdown', callback);

        return { button, buttonText, hitArea };
    }
}
