// Uni the Unicorn - Forest Adventure
// Main Game Configuration

const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-container',
    backgroundColor: '#7ec850', // Forest green background
    physics: {
        default: 'arcade',
        arcade: {
            gravity: { y: 0 }, // Top-down view, no gravity
            debug: false
        }
    },
    scene: [PreloadScene, MenuScene, GameScene, UIScene],
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH
    }
};

// Create the game instance
const game = new Phaser.Game(config);

// Global game data that persists across scenes
game.globalData = {
    lives: 3,
    currentLevel: 1,
    maxLevels: 10
};
