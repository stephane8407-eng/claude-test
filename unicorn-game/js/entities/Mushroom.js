/**
 * Mushroom Entity
 * Collectible items - safe mushrooms add to score, red mushrooms freeze player
 */

class Mushroom extends Phaser.GameObjects.Container {
    constructor(scene, x, y, isSafe = true) {
        super(scene, x, y);

        this.scene = scene;
        this.isSafe = isSafe;
        this.isCollected = false;

        // Create mushroom graphics
        this.createGraphics();

        // Add to scene and enable physics
        scene.add.existing(this);
        scene.physics.add.existing(this);

        // Set up physics body (static - mushrooms don't move)
        this.body.setSize(25, 25);
        this.body.setImmovable(true);
    }

    createGraphics() {
        // Stem
        this.stemGraphics = this.scene.add.graphics();
        this.stemGraphics.fillStyle(0xf5f5dc); // Beige
        this.stemGraphics.fillRect(-5, 0, 10, 12);

        // Cap
        this.capGraphics = this.scene.add.graphics();
        const capColor = this.isSafe ? GAME_CONFIG.colors.safeMushroom : GAME_CONFIG.colors.redMushroom;
        this.capGraphics.fillStyle(capColor);
        this.capGraphics.fillEllipse(0, -5, 25, 18);

        // Spots on cap
        this.spotsGraphics = this.scene.add.graphics();
        this.spotsGraphics.fillStyle(GAME_CONFIG.colors.safeMushroomSpots);
        this.spotsGraphics.fillCircle(-6, -6, 3);
        this.spotsGraphics.fillCircle(5, -4, 2);
        this.spotsGraphics.fillCircle(-2, -10, 2);
        this.spotsGraphics.fillCircle(7, -8, 2);

        // Add slight glow for red mushrooms to indicate danger
        if (!this.isSafe) {
            this.glowGraphics = this.scene.add.graphics();
            this.glowGraphics.fillStyle(0xff0000, 0.2);
            this.glowGraphics.fillCircle(0, 0, 20);
            this.add(this.glowGraphics);

            // Pulsing animation for danger
            this.scene.tweens.add({
                targets: this.glowGraphics,
                alpha: 0.1,
                duration: 500,
                yoyo: true,
                repeat: -1
            });
        }

        // Add graphics to container
        this.add([this.stemGraphics, this.capGraphics, this.spotsGraphics]);
    }

    collect() {
        if (this.isCollected) return null;

        this.isCollected = true;

        // Collection animation
        this.scene.tweens.add({
            targets: this,
            y: this.y - 30,
            alpha: 0,
            scale: 1.5,
            duration: 300,
            ease: 'Power2',
            onComplete: () => {
                this.setActive(false);
                this.setVisible(false);
            }
        });

        // Play sound effect (placeholder - would add actual sounds later)
        // this.scene.sound.play(this.isSafe ? 'collect' : 'freeze');

        return this.isSafe;
    }

    // Respawn mushroom at a new position
    respawn(x, y) {
        this.x = x;
        this.y = y;
        this.isCollected = false;
        this.alpha = 1;
        this.scale = 1;
        this.setActive(true);
        this.setVisible(true);

        // Spawn animation
        this.scene.tweens.add({
            targets: this,
            scale: { from: 0, to: 1 },
            alpha: { from: 0, to: 1 },
            duration: 300,
            ease: 'Back.easeOut'
        });
    }

    // Static method to get random spawn position
    static getRandomPosition(scene, margin = 50) {
        return {
            x: margin + Math.random() * (GAME_CONFIG.width - margin * 2),
            y: margin + 60 + Math.random() * (GAME_CONFIG.height - margin * 2 - 60) // Account for HUD
        };
    }
}

/**
 * Mushroom Manager
 * Handles spawning and tracking mushrooms
 */
class MushroomManager {
    constructor(scene) {
        this.scene = scene;
        this.safeMushrooms = [];
        this.redMushrooms = [];
    }

    spawnMushrooms(safeCount, redCount) {
        // Spawn safe mushrooms
        for (let i = 0; i < safeCount; i++) {
            const pos = Mushroom.getRandomPosition(this.scene);
            const mushroom = new Mushroom(this.scene, pos.x, pos.y, true);
            this.safeMushrooms.push(mushroom);
        }

        // Spawn red mushrooms
        for (let i = 0; i < redCount; i++) {
            const pos = Mushroom.getRandomPosition(this.scene);
            const mushroom = new Mushroom(this.scene, pos.x, pos.y, false);
            this.redMushrooms.push(mushroom);
        }
    }

    getSafeMushrooms() {
        return this.safeMushrooms.filter(m => !m.isCollected);
    }

    getRedMushrooms() {
        return this.redMushrooms.filter(m => !m.isCollected);
    }

    getAllMushrooms() {
        return [...this.safeMushrooms, ...this.redMushrooms];
    }

    // Respawn a collected mushroom after delay
    scheduleRespawn(mushroom) {
        this.scene.time.delayedCall(GAME_CONFIG.mushrooms.respawnDelay, () => {
            if (mushroom && mushroom.scene) {
                const pos = Mushroom.getRandomPosition(this.scene);
                mushroom.respawn(pos.x, pos.y);
            }
        });
    }

    destroy() {
        this.safeMushrooms.forEach(m => m.destroy());
        this.redMushrooms.forEach(m => m.destroy());
        this.safeMushrooms = [];
        this.redMushrooms = [];
    }
}
