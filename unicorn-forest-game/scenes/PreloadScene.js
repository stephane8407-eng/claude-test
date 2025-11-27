// PreloadScene.js
// Generates placeholder graphics and prepares the game

class PreloadScene extends Phaser.Scene {
    constructor() {
        super({ key: 'PreloadScene' });
    }

    preload() {
        // Show loading text
        const loadingText = this.add.text(400, 300, 'Loading...', {
            fontSize: '32px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive'
        }).setOrigin(0.5);
    }

    create() {
        // Generate all placeholder textures using Phaser Graphics
        this.createPlaceholderTextures();

        // Start the menu scene
        this.scene.start('MenuScene');
    }

    createPlaceholderTextures() {
        // ========== UNI THE UNICORN (with horn) ==========
        // Pink/purple unicorn represented as a rounded rectangle with a horn
        let graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Body - soft pink
        graphics.fillStyle(0xffb6c1, 1); // Light pink
        graphics.fillRoundedRect(0, 8, 40, 32, 8);

        // Horn - golden/yellow triangle
        graphics.fillStyle(0xffd700, 1);
        graphics.fillTriangle(20, 0, 10, 12, 30, 12);

        // Eye
        graphics.fillStyle(0x000000, 1);
        graphics.fillCircle(28, 20, 4);

        // Cute blush
        graphics.fillStyle(0xff69b4, 0.5);
        graphics.fillCircle(32, 28, 5);

        graphics.generateTexture('uni_horn', 40, 40);
        graphics.destroy();

        // ========== UNI WITHOUT HORN ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Body - slightly dimmer pink (sad unicorn)
        graphics.fillStyle(0xdda0dd, 1); // Plum
        graphics.fillRoundedRect(0, 8, 40, 32, 8);

        // Eye (sad)
        graphics.fillStyle(0x000000, 1);
        graphics.fillCircle(28, 20, 4);

        // Tear drop
        graphics.fillStyle(0x87ceeb, 1);
        graphics.fillCircle(30, 28, 3);

        graphics.generateTexture('uni_no_horn', 40, 40);
        graphics.destroy();

        // ========== MR FOX ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Body - orange
        graphics.fillStyle(0xff6b35, 1);
        graphics.fillRoundedRect(0, 5, 36, 30, 6);

        // Ears
        graphics.fillTriangle(5, 5, 0, 0, 10, 0);
        graphics.fillTriangle(31, 5, 26, 0, 36, 0);

        // Snout - lighter orange
        graphics.fillStyle(0xffa07a, 1);
        graphics.fillRoundedRect(10, 18, 16, 12, 4);

        // Eyes - menacing
        graphics.fillStyle(0x000000, 1);
        graphics.fillCircle(10, 15, 4);
        graphics.fillCircle(26, 15, 4);

        // Evil glint
        graphics.fillStyle(0xffff00, 1);
        graphics.fillCircle(11, 14, 1);
        graphics.fillCircle(27, 14, 1);

        graphics.generateTexture('fox', 36, 35);
        graphics.destroy();

        // ========== MR CHICKEN ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Body - white/cream
        graphics.fillStyle(0xfffacd, 1);
        graphics.fillRoundedRect(0, 10, 32, 25, 8);

        // Comb - red
        graphics.fillStyle(0xff4444, 1);
        graphics.fillCircle(8, 8, 5);
        graphics.fillCircle(16, 5, 5);
        graphics.fillCircle(24, 8, 5);

        // Beak
        graphics.fillStyle(0xffa500, 1);
        graphics.fillTriangle(16, 20, 10, 25, 22, 25);

        // Eyes - dizzy/confused
        graphics.fillStyle(0x000000, 1);
        graphics.fillCircle(10, 18, 3);
        graphics.fillCircle(22, 18, 3);

        graphics.generateTexture('chicken', 32, 35);
        graphics.destroy();

        // ========== MR OWL ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Body - brown
        graphics.fillStyle(0x8b4513, 1);
        graphics.fillRoundedRect(5, 15, 40, 35, 10);

        // Head
        graphics.fillCircle(25, 18, 18);

        // Ear tufts
        graphics.fillTriangle(10, 5, 5, 18, 15, 15);
        graphics.fillTriangle(40, 5, 35, 15, 45, 18);

        // Eye circles - cream
        graphics.fillStyle(0xfff8dc, 1);
        graphics.fillCircle(18, 18, 10);
        graphics.fillCircle(32, 18, 10);

        // Eyes
        graphics.fillStyle(0x000000, 1);
        graphics.fillCircle(18, 18, 5);
        graphics.fillCircle(32, 18, 5);

        // Wise glint
        graphics.fillStyle(0xffffff, 1);
        graphics.fillCircle(20, 16, 2);
        graphics.fillCircle(34, 16, 2);

        // Beak
        graphics.fillStyle(0xffa500, 1);
        graphics.fillTriangle(25, 25, 20, 32, 30, 32);

        graphics.generateTexture('owl', 50, 50);
        graphics.destroy();

        // ========== TREEHOUSE ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Tree trunk
        graphics.fillStyle(0x8b4513, 1);
        graphics.fillRect(35, 50, 30, 50);

        // Tree crown - dark green
        graphics.fillStyle(0x228b22, 1);
        graphics.fillCircle(50, 30, 45);

        // House structure
        graphics.fillStyle(0xdeb887, 1);
        graphics.fillRoundedRect(20, 20, 60, 40, 5);

        // Roof
        graphics.fillStyle(0xa0522d, 1);
        graphics.fillTriangle(50, 0, 10, 25, 90, 25);

        // Door
        graphics.fillStyle(0x8b4513, 1);
        graphics.fillRoundedRect(40, 35, 20, 25, 3);

        // Window
        graphics.fillStyle(0x87ceeb, 1);
        graphics.fillRoundedRect(25, 30, 12, 12, 2);
        graphics.fillRoundedRect(63, 30, 12, 12, 2);

        graphics.generateTexture('treehouse', 100, 100);
        graphics.destroy();

        // ========== BROWN MUSHROOM (SAFE) ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Stem
        graphics.fillStyle(0xf5deb3, 1);
        graphics.fillRect(8, 15, 8, 10);

        // Cap - brown
        graphics.fillStyle(0xcd853f, 1);
        graphics.fillRoundedRect(0, 0, 24, 18, 8);

        // Spots
        graphics.fillStyle(0xdeb887, 1);
        graphics.fillCircle(6, 8, 3);
        graphics.fillCircle(18, 8, 3);
        graphics.fillCircle(12, 5, 2);

        graphics.generateTexture('mushroom_brown', 24, 25);
        graphics.destroy();

        // ========== WHITE MUSHROOM (SAFE) ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Stem
        graphics.fillStyle(0xffffff, 1);
        graphics.fillRect(8, 15, 8, 10);

        // Cap - white/cream
        graphics.fillStyle(0xfffaf0, 1);
        graphics.fillRoundedRect(0, 0, 24, 18, 8);

        // Spots
        graphics.fillStyle(0xfaebd7, 1);
        graphics.fillCircle(6, 8, 3);
        graphics.fillCircle(18, 8, 3);
        graphics.fillCircle(12, 5, 2);

        graphics.generateTexture('mushroom_white', 24, 25);
        graphics.destroy();

        // ========== RED MUSHROOM (POISONOUS) ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Stem
        graphics.fillStyle(0xf5deb3, 1);
        graphics.fillRect(8, 15, 8, 10);

        // Cap - bright red
        graphics.fillStyle(0xff0000, 1);
        graphics.fillRoundedRect(0, 0, 24, 18, 8);

        // White spots (classic toadstool)
        graphics.fillStyle(0xffffff, 1);
        graphics.fillCircle(6, 8, 3);
        graphics.fillCircle(18, 8, 3);
        graphics.fillCircle(12, 5, 3);

        // Skull warning
        graphics.fillStyle(0x000000, 0.3);
        graphics.fillCircle(12, 10, 2);

        graphics.generateTexture('mushroom_red', 24, 25);
        graphics.destroy();

        // ========== MAGIC BOOK ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Book cover - magical purple
        graphics.fillStyle(0x9370db, 1);
        graphics.fillRoundedRect(0, 0, 28, 24, 3);

        // Pages
        graphics.fillStyle(0xfffaf0, 1);
        graphics.fillRect(3, 3, 22, 18);

        // Spine
        graphics.fillStyle(0x6a0dad, 1);
        graphics.fillRect(0, 0, 4, 24);

        // Magic star
        graphics.fillStyle(0xffd700, 1);
        graphics.fillStar(17, 12, 5, 6, 3);

        // Sparkles
        graphics.fillStyle(0xffffff, 1);
        graphics.fillCircle(8, 8, 2);
        graphics.fillCircle(22, 6, 1);
        graphics.fillCircle(10, 16, 1);

        graphics.generateTexture('magic_book', 28, 24);
        graphics.destroy();

        // ========== OBSTACLE (Tree/Rock) ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Tree stump / rock
        graphics.fillStyle(0x556b2f, 1);
        graphics.fillRoundedRect(0, 10, 40, 30, 5);

        // Bush top
        graphics.fillStyle(0x228b22, 1);
        graphics.fillCircle(20, 12, 18);
        graphics.fillCircle(8, 18, 12);
        graphics.fillCircle(32, 18, 12);

        graphics.generateTexture('obstacle', 40, 40);
        graphics.destroy();

        // ========== HEART (for lives) ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        graphics.fillStyle(0xff6b81, 1);
        // Simple heart shape
        graphics.fillCircle(8, 8, 8);
        graphics.fillCircle(22, 8, 8);
        graphics.fillTriangle(0, 10, 30, 10, 15, 28);

        graphics.generateTexture('heart', 30, 28);
        graphics.destroy();

        // ========== EMPTY HEART ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        graphics.lineStyle(2, 0xff6b81, 1);
        graphics.strokeCircle(8, 8, 7);
        graphics.strokeCircle(22, 8, 7);
        graphics.strokeTriangle(1, 10, 29, 10, 15, 27);

        graphics.generateTexture('heart_empty', 30, 28);
        graphics.destroy();

        // ========== BASKET ==========
        graphics = this.make.graphics({ x: 0, y: 0, add: false });

        // Basket body
        graphics.fillStyle(0xcd853f, 1);
        graphics.fillRoundedRect(0, 10, 36, 20, 5);

        // Handle
        graphics.lineStyle(3, 0x8b4513, 1);
        graphics.strokeEllipse(18, 8, 24, 16);

        // Weave pattern
        graphics.lineStyle(1, 0x8b4513, 0.5);
        graphics.lineBetween(5, 15, 5, 28);
        graphics.lineBetween(12, 15, 12, 28);
        graphics.lineBetween(18, 15, 18, 28);
        graphics.lineBetween(24, 15, 24, 28);
        graphics.lineBetween(31, 15, 31, 28);

        graphics.generateTexture('basket', 36, 30);
        graphics.destroy();

        console.log('All placeholder textures created successfully!');
    }
}
