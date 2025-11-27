/**
 * Enemy Entity - Mr Fox
 * Chases the player around the forest
 * Future: Can be transformed into a chicken by magic books
 */

class Enemy extends Phaser.GameObjects.Container {
    constructor(scene, x, y) {
        super(scene, x, y);

        this.scene = scene;
        this.speed = GAME_CONFIG.enemy.speed;
        this.chaseDistance = GAME_CONFIG.enemy.chaseDistance;
        this.isChicken = false; // Future feature: transformation
        this.target = null;

        // Create the fox graphics
        this.createFoxGraphics();

        // Add to scene and enable physics
        scene.add.existing(this);
        scene.physics.add.existing(this);

        // Set up physics body
        this.body.setSize(35, 35);
        this.body.setCollideWorldBounds(true);

        // Movement AI state
        this.wanderTimer = 0;
        this.wanderDirection = { x: 0, y: 0 };
    }

    createFoxGraphics() {
        // Body (oval)
        this.bodyGraphics = this.scene.add.graphics();
        this.bodyGraphics.fillStyle(GAME_CONFIG.colors.foxBody);
        this.bodyGraphics.fillEllipse(0, 0, 35, 25);

        // Head (circle)
        this.headGraphics = this.scene.add.graphics();
        this.headGraphics.fillStyle(GAME_CONFIG.colors.foxBody);
        this.headGraphics.fillCircle(15, -5, 12);

        // Ears (triangles)
        this.earsGraphics = this.scene.add.graphics();
        this.earsGraphics.fillStyle(GAME_CONFIG.colors.foxBody);
        this.earsGraphics.fillTriangle(10, -18, 8, -8, 15, -10);
        this.earsGraphics.fillTriangle(20, -18, 15, -8, 22, -10);
        // Inner ears
        this.earsGraphics.fillStyle(0xffcccc);
        this.earsGraphics.fillTriangle(11, -15, 10, -10, 14, -11);
        this.earsGraphics.fillTriangle(19, -15, 16, -10, 20, -11);

        // Snout
        this.snoutGraphics = this.scene.add.graphics();
        this.snoutGraphics.fillStyle(0xffffff);
        this.snoutGraphics.fillEllipse(22, -2, 8, 6);
        // Nose
        this.snoutGraphics.fillStyle(0x000000);
        this.snoutGraphics.fillCircle(25, -3, 3);

        // Eyes (menacing)
        this.eyeGraphics = this.scene.add.graphics();
        this.eyeGraphics.fillStyle(0xffff00); // Yellow eyes
        this.eyeGraphics.fillCircle(12, -8, 4);
        this.eyeGraphics.fillCircle(18, -8, 4);
        // Pupils
        this.eyeGraphics.fillStyle(0x000000);
        this.eyeGraphics.fillCircle(13, -8, 2);
        this.eyeGraphics.fillCircle(19, -8, 2);

        // Tail (with white tip)
        this.tailGraphics = this.scene.add.graphics();
        this.tailGraphics.fillStyle(GAME_CONFIG.colors.foxBody);
        this.tailGraphics.fillEllipse(-20, 5, 20, 8);
        this.tailGraphics.fillStyle(GAME_CONFIG.colors.foxTail);
        this.tailGraphics.fillCircle(-28, 5, 5);

        // Legs
        this.legsGraphics = this.scene.add.graphics();
        this.legsGraphics.fillStyle(GAME_CONFIG.colors.foxBody);
        this.legsGraphics.fillRect(-10, 8, 5, 10);
        this.legsGraphics.fillRect(0, 8, 5, 10);
        this.legsGraphics.fillRect(8, 8, 5, 10);

        // Add all graphics to container
        this.add([
            this.tailGraphics,
            this.legsGraphics,
            this.bodyGraphics,
            this.headGraphics,
            this.earsGraphics,
            this.snoutGraphics,
            this.eyeGraphics
        ]);
    }

    setTarget(target) {
        this.target = target;
    }

    setSpeed(speed) {
        this.speed = speed;
    }

    // Future feature: Transform into chicken
    transformToChicken() {
        if (!this.isChicken) {
            this.isChicken = true;
            this.previousSpeed = this.speed;
            this.speed = this.speed * 0.3; // Much slower as chicken

            // Change appearance
            this.clearGraphics();
            this.createChickenGraphics();

            // Emit event
            this.scene.events.emit('foxTransformed');
        }
    }

    // Future feature: Transform back to fox
    transformToFox() {
        if (this.isChicken) {
            this.isChicken = false;
            this.speed = this.previousSpeed;

            // Restore appearance
            this.clearGraphics();
            this.createFoxGraphics();

            // Emit event
            this.scene.events.emit('foxRestored');
        }
    }

    clearGraphics() {
        this.removeAll(true);
    }

    // Future feature: Chicken graphics
    createChickenGraphics() {
        // Simple chicken placeholder
        const chicken = this.scene.add.graphics();
        // Body
        chicken.fillStyle(0xffff00); // Yellow
        chicken.fillCircle(0, 0, 15);
        // Head
        chicken.fillCircle(10, -10, 10);
        // Beak
        chicken.fillStyle(0xff6600);
        chicken.fillTriangle(20, -10, 15, -12, 15, -8);
        // Comb
        chicken.fillStyle(0xff0000);
        chicken.fillCircle(8, -18, 4);
        chicken.fillCircle(12, -18, 4);
        // Eye
        chicken.fillStyle(0x000000);
        chicken.fillCircle(12, -12, 2);

        this.add(chicken);
    }

    update(time, delta) {
        if (!this.target) return;

        const distance = Phaser.Math.Distance.Between(
            this.x, this.y,
            this.target.x, this.target.y
        );

        // If chicken, just wander randomly (harmless)
        if (this.isChicken) {
            this.wander(time, delta);
            return;
        }

        // Chase if within range, otherwise wander
        if (distance < this.chaseDistance) {
            this.chase();
        } else {
            this.wander(time, delta);
        }
    }

    chase() {
        if (!this.target) return;

        // Calculate direction to player
        const angle = Phaser.Math.Angle.Between(
            this.x, this.y,
            this.target.x, this.target.y
        );

        // Set velocity towards player
        this.body.setVelocity(
            Math.cos(angle) * this.speed,
            Math.sin(angle) * this.speed
        );

        // Face the direction of movement
        this.scaleX = this.body.velocity.x < 0 ? -1 : 1;
    }

    wander(time, delta) {
        // Change direction periodically
        this.wanderTimer -= delta;

        if (this.wanderTimer <= 0) {
            // Pick a new random direction
            const angle = Math.random() * Math.PI * 2;
            this.wanderDirection.x = Math.cos(angle);
            this.wanderDirection.y = Math.sin(angle);

            // Random time until next direction change
            this.wanderTimer = 1000 + Math.random() * 2000;
        }

        // Move in wander direction at reduced speed
        const wanderSpeed = this.speed * 0.5;
        this.body.setVelocity(
            this.wanderDirection.x * wanderSpeed,
            this.wanderDirection.y * wanderSpeed
        );

        // Face the direction of movement
        if (Math.abs(this.body.velocity.x) > 1) {
            this.scaleX = this.body.velocity.x < 0 ? -1 : 1;
        }
    }
}
