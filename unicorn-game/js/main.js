/**
 * Main Game Entry Point
 * Initializes Phaser and registers all scenes
 */

// Wait for DOM to be ready
window.addEventListener('load', () => {
    // Phaser game configuration
    const config = {
        type: Phaser.AUTO,
        width: GAME_CONFIG.width,
        height: GAME_CONFIG.height,
        parent: 'game',
        backgroundColor: '#228b22',
        physics: {
            default: 'arcade',
            arcade: {
                gravity: { y: 0 }, // Top-down game, no gravity
                debug: false // Set to true for physics debugging
            }
        },
        scene: [
            BootScene,
            MenuScene,
            GameScene,
            UIScene,
            GameOverScene
        ],
        scale: {
            mode: Phaser.Scale.FIT,
            autoCenter: Phaser.Scale.CENTER_BOTH
        }
    };

    // Create the game instance
    const game = new Phaser.Game(config);

    // Handle window focus/blur for pausing
    window.addEventListener('blur', () => {
        if (game.scene.isActive('GameScene')) {
            const gameScene = game.scene.getScene('GameScene');
            if (gameScene && !gameScene.isPaused && !gameScene.isGameOver) {
                gameScene.togglePause();
            }
        }
    });

    // Log game version
    console.log("Uni's Mushroom Adventure v1.0");
    console.log('Built with Phaser 3');
});
