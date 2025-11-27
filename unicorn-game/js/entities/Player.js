/**
 * Player Entity - Uni the Unicorn
 * Handles player movement, states, and appearance
 */

class Player extends Phaser.GameObjects.Container {
    constructor(scene, x, y) {
        super(scene, x, y);

        this.scene = scene;
        this.speed = GAME_CONFIG.player.speed;
        this.hasHorn = GameState.hasHorn;
        this.isFrozen = false;
        this.isInvincible = false;

        // Create the unicorn graphics
        this.createGraphics();

        // Add to scene and enable physics
        scene.add.existing(this);
        scene.physics.add.existing(this);

        // Set up physics body
        this.body.setSize(40, 40);
        this.body.setCollideWorldBounds(true);

        // Set up controls
        this.cursors = scene.input.keyboard.createCursorKeys();
        this.wasd = {
            up: scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W),
            down: scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S),
            left: scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A),
            right: scene.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D)
        };
    }

    createGraphics() {
        // Body (oval shape)
        this.bodyGraphics = this.scene.add.graphics();
        this.bodyGraphics.fillStyle(GAME_CONFIG.colors.unicornBody);
        this.bodyGraphics.fillEllipse(0, 0, 40, 30);

        // Mane (flowing hair)
        this.maneGraphics = this.scene.add.graphics();
        this.maneGraphics.fillStyle(GAME_CONFIG.colors.unicornMane);
        this.maneGraphics.fillEllipse(-15, -8, 15, 20);

        // Horn (triangle on top)
        this.hornGraphics = this.scene.add.graphics();
        this.updateHornGraphics();

        // Eyes
        this.eyeGraphics = this.scene.add.graphics();
        this.eyeGraphics.fillStyle(0x000000);
        this.eyeGraphics.fillCircle(12, -5, 4);

        // Legs (4 small rectangles)
        this.legsGraphics = this.scene.add.graphics();
        this.legsGraphics.fillStyle(GAME_CONFIG.colors.unicornBody);
        this.legsGraphics.fillRect(-15, 10, 6, 10);
        this.legsGraphics.fillRect(-5, 10, 6, 10);
        this.legsGraphics.fillRect(5, 10, 6, 10);
        this.legsGraphics.fillRect(15, 10, 6, 10);

        // Add all graphics to container
        this.add([
            this.legsGraphics,
            this.bodyGraphics,
            this.maneGraphics,
            this.hornGraphics,
            this.eyeGraphics
        ]);
    }

    updateHornGraphics() {
        this.hornGraphics.clear();
        if (this.hasHorn) {
            this.hornGraphics.fillStyle(GAME_CONFIG.colors.unicornHorn);
            this.hornGraphics.fillTriangle(15, -15, 10, -5, 20, -5);
            // Add sparkle effect
            this.hornGraphics.fillStyle(0xffffcc);
            this.hornGraphics.fillCircle(15, -12, 2);
        }
    }

    loseHorn() {
        if (this.hasHorn && !this.isInvincible) {
            this.hasHorn = false;
            GameState.hasHorn = false;
            this.updateHornGraphics();

            // Change body color to indicate damage
            this.bodyGraphics.clear();
            this.bodyGraphics.fillStyle(GAME_CONFIG.colors.unicornNoHorn);
            this.bodyGraphics.fillEllipse(0, 0, 40, 30);

            // Start invincibility period
            this.startInvincibility();

            // Emit event for UI update
            this.scene.events.emit('hornLost');

            return true; // Horn was lost
        }
        return false; // Already lost horn or invincible
    }

    restoreHorn() {
        if (!this.hasHorn) {
            this.hasHorn = true;
            GameState.hasHorn = true;
            this.updateHornGraphics();

            // Restore body color
            this.bodyGraphics.clear();
            this.bodyGraphics.fillStyle(GAME_CONFIG.colors.unicornBody);
            this.bodyGraphics.fillEllipse(0, 0, 40, 30);

            // Emit event for UI update
            this.scene.events.emit('hornRestored');
        }
    }

    startInvincibility() {
        this.isInvincible = true;

        // Flashing effect
        this.flashTween = this.scene.tweens.add({
            targets: this,
            alpha: 0.3,
            duration: 100,
            yoyo: true,
            repeat: GAME_CONFIG.player.invincibilityDuration / 200
        });

        // End invincibility after duration
        this.scene.time.delayedCall(GAME_CONFIG.player.invincibilityDuration, () => {
            this.isInvincible = false;
            this.alpha = 1;
        });
    }

    freeze() {
        if (!this.isFrozen) {
            this.isFrozen = true;

            // Visual feedback - turn slightly blue
            this.bodyGraphics.clear();
            this.bodyGraphics.fillStyle(0xadd8e6); // Light blue
            this.bodyGraphics.fillEllipse(0, 0, 40, 30);

            // Add ice crystals effect
            this.iceEffect = this.scene.add.graphics();
            this.iceEffect.fillStyle(0x87ceeb, 0.5);
            this.iceEffect.fillCircle(this.x, this.y, 30);

            // Emit event
            this.scene.events.emit('playerFrozen');

            // Unfreeze after duration
            this.scene.time.delayedCall(GAME_CONFIG.player.freezeDuration, () => {
                this.unfreeze();
            });
        }
    }

    unfreeze() {
        this.isFrozen = false;

        // Restore color
        this.bodyGraphics.clear();
        const color = this.hasHorn ? GAME_CONFIG.colors.unicornBody : GAME_CONFIG.colors.unicornNoHorn;
        this.bodyGraphics.fillStyle(color);
        this.bodyGraphics.fillEllipse(0, 0, 40, 30);

        // Remove ice effect
        if (this.iceEffect) {
            this.iceEffect.destroy();
            this.iceEffect = null;
        }

        // Emit event
        this.scene.events.emit('playerUnfrozen');
    }

    update() {
        if (this.isFrozen) {
            this.body.setVelocity(0, 0);
            // Update ice effect position
            if (this.iceEffect) {
                this.iceEffect.clear();
                this.iceEffect.fillStyle(0x87ceeb, 0.5);
                this.iceEffect.fillCircle(this.x, this.y, 30);
            }
            return;
        }

        // Handle movement
        let velocityX = 0;
        let velocityY = 0;

        // Check arrow keys and WASD
        if (this.cursors.left.isDown || this.wasd.left.isDown) {
            velocityX = -this.speed;
            this.scaleX = -1; // Face left
        } else if (this.cursors.right.isDown || this.wasd.right.isDown) {
            velocityX = this.speed;
            this.scaleX = 1; // Face right
        }

        if (this.cursors.up.isDown || this.wasd.up.isDown) {
            velocityY = -this.speed;
        } else if (this.cursors.down.isDown || this.wasd.down.isDown) {
            velocityY = this.speed;
        }

        // Normalize diagonal movement
        if (velocityX !== 0 && velocityY !== 0) {
            velocityX *= 0.707; // 1/sqrt(2)
            velocityY *= 0.707;
        }

        this.body.setVelocity(velocityX, velocityY);
    }

    // Clean up method
    destroy() {
        if (this.iceEffect) {
            this.iceEffect.destroy();
        }
        if (this.flashTween) {
            this.flashTween.stop();
        }
        super.destroy();
    }
}
