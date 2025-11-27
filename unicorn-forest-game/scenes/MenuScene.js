// MenuScene.js
// Main menu with play button and instructions

class MenuScene extends Phaser.Scene {
    constructor() {
        super({ key: 'MenuScene' });
    }

    create() {
        const { width, height } = this.cameras.main;

        // Background gradient effect with rectangles
        this.add.rectangle(width / 2, height / 2, width, height, 0x7ec850);

        // Add some decorative elements
        this.createDecorations();

        // Title
        const titleShadow = this.add.text(width / 2 + 3, 83, 'Uni the Unicorn', {
            fontSize: '48px',
            fill: '#2d5016',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        const title = this.add.text(width / 2, 80, 'Uni the Unicorn', {
            fontSize: '48px',
            fill: '#ff69b4',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold',
            stroke: '#ffffff',
            strokeThickness: 4
        }).setOrigin(0.5);

        // Subtitle
        this.add.text(width / 2, 130, '🌲 Forest Adventure 🍄', {
            fontSize: '28px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#228b22',
            strokeThickness: 3
        }).setOrigin(0.5);

        // Uni preview
        const uniPreview = this.add.image(width / 2, 200, 'uni_horn').setScale(3);
        this.tweens.add({
            targets: uniPreview,
            y: 210,
            duration: 1000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Instructions panel
        const panelY = 340;
        const panel = this.add.rectangle(width / 2, panelY, 500, 180, 0xffffff, 0.9);
        panel.setStrokeStyle(4, 0xffb6c1);

        // Instructions text
        const instructions = [
            '🎮 Arrow Keys or WASD to move',
            '🍄 Collect brown & white mushrooms',
            '☠️ Avoid red mushrooms (they freeze you!)',
            '🦊 Watch out for Mr Fox!',
            '📚 Find magic books to turn Fox into Chicken',
            '🦉 Visit Mr Owl to get your horn back!'
        ];

        instructions.forEach((text, index) => {
            this.add.text(width / 2, panelY - 70 + index * 25, text, {
                fontSize: '16px',
                fill: '#333333',
                fontFamily: 'Comic Sans MS, cursive'
            }).setOrigin(0.5);
        });

        // Play button
        const playButton = this.add.rectangle(width / 2, 480, 200, 60, 0xff69b4)
            .setStrokeStyle(4, 0xff1493)
            .setInteractive({ useHandCursor: true });

        const playText = this.add.text(width / 2, 480, '▶ PLAY', {
            fontSize: '32px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            fontStyle: 'bold'
        }).setOrigin(0.5);

        // Button hover effects
        playButton.on('pointerover', () => {
            playButton.setFillStyle(0xff1493);
            playButton.setScale(1.1);
            playText.setScale(1.1);
        });

        playButton.on('pointerout', () => {
            playButton.setFillStyle(0xff69b4);
            playButton.setScale(1);
            playText.setScale(1);
        });

        playButton.on('pointerdown', () => {
            // Reset game data
            this.game.globalData.lives = 3;
            this.game.globalData.currentLevel = 1;

            // Start game
            this.scene.start('GameScene');
            this.scene.launch('UIScene');
        });

        // Credits
        this.add.text(width / 2, height - 30, 'Help Uni collect mushrooms for her pie! 🥧', {
            fontSize: '16px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#228b22',
            strokeThickness: 2
        }).setOrigin(0.5);

        // Keyboard shortcut to start
        this.input.keyboard.once('keydown-SPACE', () => {
            this.game.globalData.lives = 3;
            this.game.globalData.currentLevel = 1;
            this.scene.start('GameScene');
            this.scene.launch('UIScene');
        });

        this.add.text(width / 2, height - 10, 'Press SPACE to start', {
            fontSize: '12px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive'
        }).setOrigin(0.5);
    }

    createDecorations() {
        const { width, height } = this.cameras.main;

        // Scatter some mushrooms and trees in the background
        for (let i = 0; i < 8; i++) {
            const x = Phaser.Math.Between(50, width - 50);
            const y = Phaser.Math.Between(height - 100, height - 20);
            const mushroomType = Phaser.Math.RND.pick(['mushroom_brown', 'mushroom_white']);
            this.add.image(x, y, mushroomType).setScale(1.5).setAlpha(0.6);
        }

        // Add some trees/obstacles in corners
        this.add.image(50, height - 50, 'obstacle').setScale(1.5).setAlpha(0.5);
        this.add.image(width - 50, height - 50, 'obstacle').setScale(1.5).setAlpha(0.5);

        // Add treehouse
        this.add.image(width - 80, 60, 'treehouse').setScale(0.8).setAlpha(0.7);

        // Add Mr Fox lurking
        const fox = this.add.image(100, 150, 'fox').setScale(2).setAlpha(0.7);
        this.tweens.add({
            targets: fox,
            x: 130,
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });
    }
}
