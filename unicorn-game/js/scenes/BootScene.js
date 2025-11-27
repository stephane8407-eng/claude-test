/**
 * Boot Scene
 * Initial loading and setup
 */

class BootScene extends Phaser.Scene {
    constructor() {
        super({ key: 'BootScene' });
    }

    preload() {
        // Show loading progress
        const width = this.cameras.main.width;
        const height = this.cameras.main.height;

        // Loading bar background
        const bgBar = this.add.graphics();
        bgBar.fillStyle(0x222222, 1);
        bgBar.fillRect(width / 2 - 150, height / 2 - 15, 300, 30);

        // Loading bar fill
        const progressBar = this.add.graphics();

        // Loading text
        const loadingText = this.add.text(width / 2, height / 2 - 50, 'Loading...', {
            fontFamily: 'Comic Sans MS, cursive',
            fontSize: '24px',
            fill: '#ffffff'
        }).setOrigin(0.5);

        // Update progress bar
        this.load.on('progress', (value) => {
            progressBar.clear();
            progressBar.fillStyle(0x4CAF50, 1);
            progressBar.fillRect(width / 2 - 145, height / 2 - 10, 290 * value, 20);
        });

        this.load.on('complete', () => {
            progressBar.destroy();
            bgBar.destroy();
            loadingText.destroy();
        });

        // Since we're using generated graphics, just add a small delay for effect
        // In a real game, you would load image assets here:
        // this.load.image('unicorn', 'assets/unicorn.png');
        // this.load.image('fox', 'assets/fox.png');
        // this.load.spritesheet('mushroom', 'assets/mushroom.png', { frameWidth: 32, frameHeight: 32 });
        // this.load.audio('collect', 'assets/sounds/collect.wav');
        // etc.
    }

    create() {
        // Initialize game state
        GameState.reset();

        // Proceed to menu
        this.scene.start('MenuScene');
    }
}
