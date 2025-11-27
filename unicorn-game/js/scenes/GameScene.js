/**
 * Game Scene
 * Main gameplay scene with all game logic
 */

class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }

    init() {
        // Get level settings
        this.levelConfig = GAME_CONFIG.levels[GameState.currentLevel] || GAME_CONFIG.levels[1];

        // Game state
        this.mushroomsCollected = 0;
        this.targetMushrooms = this.levelConfig.targetMushrooms;
        this.timeRemaining = this.levelConfig.timeLimit;
        this.isGameOver = false;
        this.isPaused = false;
    }

    create() {
        // Create the forest background
        this.createBackground();

        // Create player (Uni)
        this.player = new Player(this, 100, 300);

        // Create enemy (Mr Fox)
        this.fox = new Enemy(this, 600, 400);
        this.fox.setTarget(this.player);
        this.fox.setSpeed(this.levelConfig.foxSpeed);

        // Create mushroom manager and spawn mushrooms
        this.mushroomManager = new MushroomManager(this);
        this.mushroomManager.spawnMushrooms(
            GAME_CONFIG.mushrooms.safeMushrooms,
            this.levelConfig.redMushroomCount
        );

        // Set up collisions
        this.setupCollisions();

        // Set up game timer
        this.gameTimer = this.time.addEvent({
            delay: 1000,
            callback: this.updateTimer,
            callbackScope: this,
            loop: true
        });

        // Listen for events from other scenes
        this.setupEventListeners();

        // Tell UI scene to update
        this.events.emit('gameStart', {
            lives: GameState.lives,
            mushrooms: this.mushroomsCollected,
            target: this.targetMushrooms,
            time: this.timeRemaining,
            level: GameState.currentLevel,
            hasHorn: GameState.hasHorn
        });
    }

    createBackground() {
        // Base grass color
        const bg = this.add.graphics();
        bg.fillStyle(0x228b22);
        bg.fillRect(0, 0, GAME_CONFIG.width, GAME_CONFIG.height);

        // Add grass texture variation
        for (let i = 0; i < 100; i++) {
            const grassPatch = this.add.graphics();
            const shade = 0x228b22 + Math.floor(Math.random() * 0x222222);
            grassPatch.fillStyle(shade, 0.5);
            grassPatch.fillEllipse(
                Math.random() * GAME_CONFIG.width,
                Math.random() * GAME_CONFIG.height,
                10 + Math.random() * 30,
                5 + Math.random() * 15
            );
        }

        // Add some trees around the edges
        this.createForestBorder();

        // Add some flowers for decoration
        this.createFlowers();
    }

    createForestBorder() {
        const treePositions = [
            // Top edge
            { x: 50, y: 30 }, { x: 150, y: 25 }, { x: 280, y: 35 },
            { x: 420, y: 28 }, { x: 550, y: 32 }, { x: 680, y: 25 }, { x: 770, y: 35 },
            // Bottom edge
            { x: 40, y: 580 }, { x: 180, y: 575 }, { x: 320, y: 582 },
            { x: 480, y: 578 }, { x: 620, y: 585 }, { x: 760, y: 575 },
            // Left edge
            { x: 25, y: 150 }, { x: 30, y: 300 }, { x: 25, y: 450 },
            // Right edge
            { x: 775, y: 150 }, { x: 770, y: 300 }, { x: 775, y: 450 }
        ];

        treePositions.forEach(pos => {
            this.createTree(pos.x, pos.y, 0.6 + Math.random() * 0.4);
        });
    }

    createTree(x, y, scale = 1) {
        const tree = this.add.graphics();

        // Trunk
        tree.fillStyle(0x8b4513);
        tree.fillRect(x - 6 * scale, y, 12 * scale, 30 * scale);

        // Foliage layers
        tree.fillStyle(GAME_CONFIG.colors.tree);
        tree.fillCircle(x, y - 10 * scale, 20 * scale);
        tree.fillCircle(x - 12 * scale, y + 5 * scale, 15 * scale);
        tree.fillCircle(x + 12 * scale, y + 5 * scale, 15 * scale);

        // Darker highlights
        tree.fillStyle(0x1a4d1a, 0.5);
        tree.fillCircle(x + 5 * scale, y - 5 * scale, 8 * scale);
    }

    createFlowers() {
        const flowerColors = [0xff69b4, 0xffff00, 0xff6347, 0x9370db, 0x00ced1];

        for (let i = 0; i < 25; i++) {
            const flower = this.add.graphics();
            const color = flowerColors[Math.floor(Math.random() * flowerColors.length)];
            const x = 60 + Math.random() * (GAME_CONFIG.width - 120);
            const y = 80 + Math.random() * (GAME_CONFIG.height - 160);

            // Petals
            flower.fillStyle(color, 0.8);
            for (let j = 0; j < 5; j++) {
                const angle = (j / 5) * Math.PI * 2;
                flower.fillCircle(
                    x + Math.cos(angle) * 4,
                    y + Math.sin(angle) * 4,
                    4
                );
            }

            // Center
            flower.fillStyle(0xffff00);
            flower.fillCircle(x, y, 3);
        }
    }

    setupCollisions() {
        // Player collects safe mushrooms
        this.physics.add.overlap(
            this.player,
            this.mushroomManager.getSafeMushroomsGroup(),
            this.collectSafeMushroom,
            null,
            this
        );

        // Player hits red mushrooms
        this.physics.add.overlap(
            this.player,
            this.mushroomManager.getRedMushroomsGroup(),
            this.hitRedMushroom,
            null,
            this
        );

        // Fox catches player
        this.physics.add.overlap(
            this.player,
            this.fox,
            this.foxCatchesPlayer,
            null,
            this
        );
    }

    collectSafeMushroom(player, mushroom) {
        if (mushroom.isCollected) return;

        const result = mushroom.collect();
        if (result === true) {
            this.mushroomsCollected++;

            // Emit event for UI
            this.events.emit('mushroomCollected', {
                collected: this.mushroomsCollected,
                target: this.targetMushrooms
            });

            // Check win condition
            if (this.mushroomsCollected >= this.targetMushrooms) {
                this.levelComplete();
            }

            // Schedule respawn (for endless mode potential)
            // this.mushroomManager.scheduleRespawn(mushroom);
        }
    }

    hitRedMushroom(player, mushroom) {
        if (mushroom.isCollected || player.isFrozen) return;

        mushroom.collect();
        player.freeze();

        // Visual feedback
        this.cameras.main.shake(200, 0.01);

        // Emit event for UI
        this.events.emit('playerFrozen', {
            duration: GAME_CONFIG.player.freezeDuration
        });
    }

    foxCatchesPlayer(player, fox) {
        if (player.isInvincible || fox.isChicken) return;

        const lostHorn = player.loseHorn();

        if (lostHorn) {
            // Lose a life
            GameState.lives--;

            // Visual feedback
            this.cameras.main.shake(300, 0.02);
            this.cameras.main.flash(200, 255, 0, 0);

            // Emit event for UI
            this.events.emit('livesChanged', {
                lives: GameState.lives,
                hasHorn: GameState.hasHorn
            });

            // Check game over
            if (GameState.lives <= 0) {
                this.gameOver('Mr Fox caught Uni too many times!');
            }
        }
    }

    updateTimer() {
        if (this.isGameOver || this.isPaused) return;

        this.timeRemaining--;

        // Emit event for UI
        this.events.emit('timerUpdate', {
            time: this.timeRemaining
        });

        // Check time's up
        if (this.timeRemaining <= 0) {
            this.gameOver('Time ran out!');
        }

        // Warning when time is low
        if (this.timeRemaining === 30) {
            this.events.emit('timeWarning');
        }
    }

    levelComplete() {
        if (this.isGameOver) return;

        this.isGameOver = true;
        this.gameTimer.remove();

        // Calculate bonus points
        const timeBonus = this.timeRemaining * 10;
        const lifeBonus = GameState.lives * 100;
        GameState.totalScore += this.mushroomsCollected * 50 + timeBonus + lifeBonus;

        // Emit level complete event
        this.events.emit('levelComplete', {
            level: GameState.currentLevel,
            mushrooms: this.mushroomsCollected,
            timeRemaining: this.timeRemaining,
            timeBonus: timeBonus,
            lifeBonus: lifeBonus,
            totalScore: GameState.totalScore
        });

        // Transition to game over scene with win state
        this.time.delayedCall(1500, () => {
            this.scene.stop('UIScene');
            this.scene.start('GameOverScene', {
                won: true,
                level: GameState.currentLevel,
                score: GameState.totalScore,
                canContinue: GameState.nextLevel()
            });
        });
    }

    gameOver(reason) {
        if (this.isGameOver) return;

        this.isGameOver = true;
        this.gameTimer.remove();

        // Emit game over event
        this.events.emit('gameOver', {
            reason: reason,
            level: GameState.currentLevel,
            mushrooms: this.mushroomsCollected
        });

        // Transition to game over scene
        this.time.delayedCall(1500, () => {
            this.scene.stop('UIScene');
            this.scene.start('GameOverScene', {
                won: false,
                reason: reason,
                level: GameState.currentLevel,
                score: GameState.totalScore
            });
        });
    }

    setupEventListeners() {
        // Listen for pause toggle
        this.input.keyboard.on('keydown-ESC', () => {
            this.togglePause();
        });

        this.input.keyboard.on('keydown-P', () => {
            this.togglePause();
        });
    }

    togglePause() {
        this.isPaused = !this.isPaused;

        if (this.isPaused) {
            this.physics.pause();
            this.events.emit('gamePaused');
        } else {
            this.physics.resume();
            this.events.emit('gameResumed');
        }
    }

    update(time, delta) {
        if (this.isGameOver || this.isPaused) return;

        // Update player
        this.player.update();

        // Update fox AI
        this.fox.update(time, delta);
    }

    shutdown() {
        // Clean up
        if (this.gameTimer) {
            this.gameTimer.remove();
        }
        if (this.mushroomManager) {
            this.mushroomManager.destroy();
        }
    }
}
