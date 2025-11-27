// GameScene.js
// Main gameplay scene with all game logic

class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }

    // Level configurations - 10 levels with increasing difficulty
    static LEVELS = [
        { timeLimit: 180, targetMushrooms: 8,  foxSpeed: 70,  numObstacles: 4,  numPoison: 2, numBooks: 2, numSafe: 12 },
        { timeLimit: 170, targetMushrooms: 10, foxSpeed: 80,  numObstacles: 5,  numPoison: 3, numBooks: 2, numSafe: 14 },
        { timeLimit: 160, targetMushrooms: 12, foxSpeed: 90,  numObstacles: 6,  numPoison: 4, numBooks: 2, numSafe: 16 },
        { timeLimit: 150, targetMushrooms: 14, foxSpeed: 100, numObstacles: 7,  numPoison: 5, numBooks: 3, numSafe: 18 },
        { timeLimit: 140, targetMushrooms: 16, foxSpeed: 110, numObstacles: 8,  numPoison: 6, numBooks: 3, numSafe: 20 },
        { timeLimit: 130, targetMushrooms: 18, foxSpeed: 120, numObstacles: 9,  numPoison: 7, numBooks: 3, numSafe: 22 },
        { timeLimit: 120, targetMushrooms: 20, foxSpeed: 130, numObstacles: 10, numPoison: 8, numBooks: 4, numSafe: 24 },
        { timeLimit: 110, targetMushrooms: 22, foxSpeed: 140, numObstacles: 11, numPoison: 9, numBooks: 4, numSafe: 26 },
        { timeLimit: 100, targetMushrooms: 24, foxSpeed: 150, numObstacles: 12, numPoison: 10, numBooks: 4, numSafe: 28 },
        { timeLimit: 90,  targetMushrooms: 26, foxSpeed: 160, numObstacles: 13, numPoison: 11, numBooks: 5, numSafe: 30 }
    ];

    init() {
        // Get current level from global data
        this.currentLevelIndex = this.game.globalData.currentLevel - 1;
        this.levelConfig = GameScene.LEVELS[this.currentLevelIndex];

        // Player state
        this.hasHorn = true;
        this.magicCharges = 0;
        this.collectedMushrooms = 0;
        this.isFrozen = false;
        this.isPaused = false;

        // Fox state
        this.foxIsChicken = false;
        this.chickenTimer = null;

        // Timer
        this.timeRemaining = this.levelConfig.timeLimit;
    }

    create() {
        const { width, height } = this.cameras.main;

        // Initialize sound manager
        soundManager.init();
        soundManager.resume();

        // Create the forest background
        this.createBackground();

        // Create game groups
        this.obstacles = this.physics.add.staticGroup();
        this.safeMushrooms = this.physics.add.group();
        this.poisonMushrooms = this.physics.add.group();
        this.magicBooks = this.physics.add.group();

        // Create Mr Owl's treehouse (fixed position in top-right)
        this.createTreehouse();

        // Spawn obstacles
        this.spawnObstacles();

        // Spawn mushrooms
        this.spawnMushrooms();

        // Spawn magic books
        this.spawnMagicBooks();

        // Create Uni the Unicorn (player)
        this.createUni();

        // Create Mr Fox
        this.createFox();

        // Set up physics collisions
        this.setupCollisions();

        // Set up input
        this.setupInput();

        // Start the timer
        this.startTimer();

        // Notify UI scene
        this.updateUI();

        // Show level start message
        this.showMessage(`Level ${this.game.globalData.currentLevel}`, 2000);
    }

    createBackground() {
        const { width, height } = this.cameras.main;

        // Base grass
        this.add.rectangle(width / 2, height / 2, width, height, 0x7ec850);

        // Add some grass patches for variation
        for (let i = 0; i < 20; i++) {
            const x = Phaser.Math.Between(0, width);
            const y = Phaser.Math.Between(0, height);
            const shade = Phaser.Math.RND.pick([0x6db33f, 0x8fd14f, 0x9de24f]);
            const size = Phaser.Math.Between(20, 60);
            this.add.circle(x, y, size, shade, 0.3);
        }

        // Add path/trail
        const graphics = this.add.graphics();
        graphics.fillStyle(0xc4a35a, 0.4);
        graphics.fillRoundedRect(50, height / 2 - 20, width - 100, 40, 20);
    }

    createTreehouse() {
        const { width } = this.cameras.main;

        // Treehouse position (top-right area)
        this.treehouseX = width - 80;
        this.treehouseY = 80;

        // Treehouse sprite
        this.treehouse = this.add.image(this.treehouseX, this.treehouseY, 'treehouse');
        this.treehouse.setScale(1);

        // Mr Owl on the treehouse
        this.owl = this.add.image(this.treehouseX, this.treehouseY - 10, 'owl');
        this.owl.setScale(0.8);

        // Add a gentle bobbing animation to Mr Owl
        this.tweens.add({
            targets: this.owl,
            y: this.treehouseY - 5,
            duration: 2000,
            yoyo: true,
            repeat: -1,
            ease: 'Sine.easeInOut'
        });

        // Create owl interaction zone (physics body for collision)
        this.owlZone = this.physics.add.sprite(this.treehouseX, this.treehouseY + 30, null);
        this.owlZone.setVisible(false);
        this.owlZone.body.setSize(80, 60);
        this.owlZone.body.setAllowGravity(false);
        this.owlZone.body.setImmovable(true);

        // Label
        this.add.text(this.treehouseX, this.treehouseY + 60, "Mr Owl's House", {
            fontSize: '12px',
            fill: '#ffffff',
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#2d5016',
            strokeThickness: 2
        }).setOrigin(0.5);
    }

    spawnObstacles() {
        const { width, height } = this.cameras.main;
        const safeZones = [
            { x: 100, y: height - 100, r: 80 }, // Uni spawn area
            { x: this.treehouseX, y: this.treehouseY, r: 120 } // Treehouse area
        ];

        for (let i = 0; i < this.levelConfig.numObstacles; i++) {
            let x, y, valid;
            let attempts = 0;

            do {
                x = Phaser.Math.Between(60, width - 60);
                y = Phaser.Math.Between(100, height - 60);
                valid = true;

                // Check safe zones
                for (const zone of safeZones) {
                    const dist = Phaser.Math.Distance.Between(x, y, zone.x, zone.y);
                    if (dist < zone.r) {
                        valid = false;
                        break;
                    }
                }

                attempts++;
            } while (!valid && attempts < 50);

            if (valid) {
                const obstacle = this.obstacles.create(x, y, 'obstacle');
                obstacle.setScale(Phaser.Math.FloatBetween(0.8, 1.2));
                obstacle.refreshBody();
            }
        }
    }

    spawnMushrooms() {
        const { width, height } = this.cameras.main;

        // Spawn safe mushrooms (brown and white)
        for (let i = 0; i < this.levelConfig.numSafe; i++) {
            const pos = this.getValidSpawnPosition(width, height);
            const type = Phaser.Math.RND.pick(['mushroom_brown', 'mushroom_white']);
            const mushroom = this.safeMushrooms.create(pos.x, pos.y, type);
            mushroom.setScale(1.2);
            mushroom.body.setSize(20, 20);

            // Add slight bobbing
            this.tweens.add({
                targets: mushroom,
                y: pos.y - 3,
                duration: Phaser.Math.Between(1000, 1500),
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut',
                delay: Phaser.Math.Between(0, 500)
            });
        }

        // Spawn poison mushrooms (red)
        for (let i = 0; i < this.levelConfig.numPoison; i++) {
            const pos = this.getValidSpawnPosition(width, height);
            const mushroom = this.poisonMushrooms.create(pos.x, pos.y, 'mushroom_red');
            mushroom.setScale(1.2);
            mushroom.body.setSize(20, 20);

            // Add pulsing effect to make them look dangerous
            this.tweens.add({
                targets: mushroom,
                scale: 1.4,
                duration: 500,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
    }

    spawnMagicBooks() {
        const { width, height } = this.cameras.main;

        for (let i = 0; i < this.levelConfig.numBooks; i++) {
            const pos = this.getValidSpawnPosition(width, height);
            const book = this.magicBooks.create(pos.x, pos.y, 'magic_book');
            book.setScale(1.3);
            book.body.setSize(24, 20);

            // Add sparkle/float effect
            this.tweens.add({
                targets: book,
                y: pos.y - 8,
                angle: 5,
                duration: 1200,
                yoyo: true,
                repeat: -1,
                ease: 'Sine.easeInOut'
            });
        }
    }

    getValidSpawnPosition(width, height) {
        const safeZones = [
            { x: 100, y: height - 100, r: 60 },
            { x: this.treehouseX, y: this.treehouseY, r: 100 }
        ];

        let x, y, valid;
        let attempts = 0;

        do {
            x = Phaser.Math.Between(50, width - 50);
            y = Phaser.Math.Between(80, height - 50);
            valid = true;

            for (const zone of safeZones) {
                if (Phaser.Math.Distance.Between(x, y, zone.x, zone.y) < zone.r) {
                    valid = false;
                    break;
                }
            }

            // Check distance from obstacles
            this.obstacles.children.iterate((obstacle) => {
                if (obstacle && Phaser.Math.Distance.Between(x, y, obstacle.x, obstacle.y) < 50) {
                    valid = false;
                }
            });

            attempts++;
        } while (!valid && attempts < 50);

        return { x, y };
    }

    createUni() {
        const { height } = this.cameras.main;

        // Spawn Uni in bottom-left area
        this.uni = this.physics.add.sprite(100, height - 100, 'uni_horn');
        this.uni.setScale(1.5);
        this.uni.setCollideWorldBounds(true);
        this.uni.body.setSize(30, 30);
        this.uni.setDepth(10);

        // Player speed
        this.uniSpeed = 180;
    }

    createFox() {
        const { width } = this.cameras.main;

        // Spawn Fox on the opposite side
        this.fox = this.physics.add.sprite(width - 100, 200, 'fox');
        this.fox.setScale(1.5);
        this.fox.setCollideWorldBounds(true);
        this.fox.body.setSize(30, 28);
        this.fox.setDepth(10);

        // Fox label
        this.foxLabel = this.add.text(this.fox.x, this.fox.y - 30, 'Mr Fox', {
            fontSize: '12px',
            fill: '#ff6b35',
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#ffffff',
            strokeThickness: 2
        }).setOrigin(0.5).setDepth(11);
    }

    setupCollisions() {
        // Uni collides with obstacles
        this.physics.add.collider(this.uni, this.obstacles);

        // Fox collides with obstacles
        this.physics.add.collider(this.fox, this.obstacles);

        // Uni collects safe mushrooms
        this.physics.add.overlap(this.uni, this.safeMushrooms, this.collectSafeMushroom, null, this);

        // Uni touches poison mushrooms
        this.physics.add.overlap(this.uni, this.poisonMushrooms, this.touchPoisonMushroom, null, this);

        // Uni collects magic books
        this.physics.add.overlap(this.uni, this.magicBooks, this.collectMagicBook, null, this);

        // Fox catches Uni
        this.physics.add.overlap(this.uni, this.fox, this.foxCatchesUni, null, this);

        // Uni visits Mr Owl
        this.physics.add.overlap(this.uni, this.owlZone, this.visitOwl, null, this);
    }

    setupInput() {
        // Arrow keys
        this.cursors = this.input.keyboard.createCursorKeys();

        // WASD keys
        this.wasd = {
            up: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.W),
            down: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.S),
            left: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.A),
            right: this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.D)
        };

        // Space for magic (transform Fox to Chicken)
        this.spaceKey = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);
        this.spaceKey.on('down', () => this.useMagic());
    }

    startTimer() {
        this.timerEvent = this.time.addEvent({
            delay: 1000,
            callback: this.tickTimer,
            callbackScope: this,
            loop: true
        });
    }

    tickTimer() {
        if (this.isPaused) return;

        this.timeRemaining--;
        this.updateUI();

        // Play warning sound when time is low
        if (this.timeRemaining <= 10 && this.timeRemaining > 0) {
            soundManager.timerWarning();
        }

        if (this.timeRemaining <= 0) {
            this.timeUp();
        }
    }

    update() {
        if (this.isPaused) return;

        // Handle Uni movement
        this.handleUniMovement();

        // Handle Fox AI
        this.handleFoxAI();

        // Update fox label position
        if (this.foxLabel && this.fox) {
            this.foxLabel.setPosition(this.fox.x, this.fox.y - 30);
        }
    }

    handleUniMovement() {
        if (this.isFrozen) {
            this.uni.setVelocity(0, 0);
            return;
        }

        let vx = 0;
        let vy = 0;

        // Check arrow keys and WASD
        if (this.cursors.left.isDown || this.wasd.left.isDown) {
            vx = -this.uniSpeed;
        } else if (this.cursors.right.isDown || this.wasd.right.isDown) {
            vx = this.uniSpeed;
        }

        if (this.cursors.up.isDown || this.wasd.up.isDown) {
            vy = -this.uniSpeed;
        } else if (this.cursors.down.isDown || this.wasd.down.isDown) {
            vy = this.uniSpeed;
        }

        // Normalize diagonal movement
        if (vx !== 0 && vy !== 0) {
            vx *= 0.707;
            vy *= 0.707;
        }

        this.uni.setVelocity(vx, vy);

        // Flip sprite based on direction
        if (vx < 0) {
            this.uni.setFlipX(true);
        } else if (vx > 0) {
            this.uni.setFlipX(false);
        }
    }

    handleFoxAI() {
        if (!this.fox || !this.uni) return;

        let speed = this.foxIsChicken ? this.levelConfig.foxSpeed * 0.3 : this.levelConfig.foxSpeed;

        if (this.foxIsChicken) {
            // Chicken wanders randomly
            if (!this.chickenWanderTarget || Phaser.Math.Distance.Between(
                this.fox.x, this.fox.y,
                this.chickenWanderTarget.x, this.chickenWanderTarget.y
            ) < 20) {
                this.chickenWanderTarget = {
                    x: Phaser.Math.Between(50, this.cameras.main.width - 50),
                    y: Phaser.Math.Between(50, this.cameras.main.height - 50)
                };
            }

            this.physics.moveToObject(this.fox, this.chickenWanderTarget, speed);
        } else {
            // Fox chases Uni
            this.physics.moveToObject(this.fox, this.uni, speed);
        }

        // Flip sprite based on velocity
        if (this.fox.body.velocity.x < 0) {
            this.fox.setFlipX(true);
        } else if (this.fox.body.velocity.x > 0) {
            this.fox.setFlipX(false);
        }
    }

    collectSafeMushroom(uni, mushroom) {
        // Remove mushroom
        mushroom.destroy();

        // Play sound
        soundManager.collectMushroom();

        // Increment count
        this.collectedMushrooms++;

        // Show collect effect
        this.showCollectEffect(mushroom.x, mushroom.y, '+1 🍄', '#8b4513');

        // Update UI
        this.updateUI();

        // Check level completion
        if (this.collectedMushrooms >= this.levelConfig.targetMushrooms) {
            this.levelComplete();
        }
    }

    touchPoisonMushroom(uni, mushroom) {
        if (this.isFrozen) return; // Already frozen

        // Remove mushroom
        mushroom.destroy();

        // Play poison sound
        soundManager.poison();

        // Freeze Uni
        this.isFrozen = true;
        this.uni.setTint(0x9932cc); // Purple tint to show poisoned

        // Show message
        this.showMessage('Poisoned! Frozen for 3 seconds!', 2000);
        this.showCollectEffect(mushroom.x, mushroom.y, '☠️ POISON!', '#ff0000');

        // Unfreeze after 3 seconds
        this.time.delayedCall(3000, () => {
            this.isFrozen = false;
            this.uni.clearTint();
        });
    }

    collectMagicBook(uni, book) {
        // Remove book
        book.destroy();

        // Play magic book sound
        soundManager.collectBook();

        // Add magic charge
        this.magicCharges++;

        // Show effect
        this.showCollectEffect(book.x, book.y, '✨ MAGIC +1', '#9370db');
        this.showMessage('Magic book collected! Press SPACE to use.', 2000);

        // Update UI
        this.updateUI();
    }

    useMagic() {
        if (this.magicCharges <= 0) {
            this.showMessage('No magic books!', 1000);
            return;
        }

        if (this.foxIsChicken) {
            this.showMessage('Fox is already a chicken!', 1000);
            return;
        }

        // Use magic charge
        this.magicCharges--;

        // Transform fox to chicken
        this.transformToChicken();

        // Update UI
        this.updateUI();
    }

    transformToChicken() {
        // Play magic and chicken sounds
        soundManager.useMagic();
        setTimeout(() => soundManager.foxToChicken(), 300);

        this.foxIsChicken = true;
        this.fox.setTexture('chicken');
        this.foxLabel.setText('Mr Chicken');
        this.foxLabel.setColor('#ffa500');

        // Show message
        this.showMessage('🐔 Mr Fox became Mr Chicken for 10 seconds!', 2000);

        // Visual effect
        this.tweens.add({
            targets: this.fox,
            scale: 1.8,
            duration: 200,
            yoyo: true
        });

        // Clear any existing timer
        if (this.chickenTimer) {
            this.chickenTimer.remove();
        }

        // Transform back after 10 seconds
        this.chickenTimer = this.time.delayedCall(10000, () => {
            this.transformToFox();
        });
    }

    transformToFox() {
        // Play fox return sound
        soundManager.chickenToFox();

        this.foxIsChicken = false;
        this.fox.setTexture('fox');
        this.foxLabel.setText('Mr Fox');
        this.foxLabel.setColor('#ff6b35');
        this.chickenWanderTarget = null;

        // Show warning
        this.showMessage('🦊 Mr Fox is back! Watch out!', 2000);

        // Visual effect
        this.tweens.add({
            targets: this.fox,
            scale: 1.8,
            duration: 200,
            yoyo: true
        });
    }

    foxCatchesUni(uni, fox) {
        if (this.foxIsChicken) return; // Chicken is harmless

        // Prevent multiple hits in quick succession
        if (this.hitCooldown) return;
        this.hitCooldown = true;
        this.time.delayedCall(1000, () => { this.hitCooldown = false; });

        if (this.hasHorn) {
            // Lose horn first
            this.loseHorn();
        } else {
            // Already without horn, lose a life
            this.loseLife();
        }
    }

    loseHorn() {
        // Play lose horn sound
        soundManager.loseHorn();

        this.hasHorn = false;
        this.uni.setTexture('uni_no_horn');

        // Knock back Uni
        const angle = Phaser.Math.Angle.Between(this.fox.x, this.fox.y, this.uni.x, this.uni.y);
        this.uni.setVelocity(Math.cos(angle) * 300, Math.sin(angle) * 300);

        // Show effect
        this.showCollectEffect(this.uni.x, this.uni.y - 20, '🦄➡️🐴', '#ff69b4');
        this.showMessage('Uni lost her horn! Visit Mr Owl!', 3000);

        // Flash effect
        this.tweens.add({
            targets: this.uni,
            alpha: 0.3,
            duration: 100,
            yoyo: true,
            repeat: 5
        });

        // Update UI
        this.updateUI();
    }

    loseLife() {
        // Play lose life sound
        soundManager.loseLife();

        this.game.globalData.lives--;

        // Knock back and flash
        const angle = Phaser.Math.Angle.Between(this.fox.x, this.fox.y, this.uni.x, this.uni.y);
        this.uni.setVelocity(Math.cos(angle) * 300, Math.sin(angle) * 300);

        this.tweens.add({
            targets: this.uni,
            alpha: 0.3,
            duration: 100,
            yoyo: true,
            repeat: 5
        });

        this.showCollectEffect(this.uni.x, this.uni.y - 20, '💔 -1 LIFE', '#ff0000');

        // Update UI
        this.updateUI();

        if (this.game.globalData.lives <= 0) {
            this.gameOver();
        } else {
            // Respawn near treehouse with horn restored
            this.showMessage('Ouch! Respawning near Mr Owl...', 2000);
            this.time.delayedCall(1000, () => {
                this.respawnUni();
            });
        }
    }

    respawnUni() {
        // Move Uni near treehouse
        this.uni.setPosition(this.treehouseX - 80, this.treehouseY + 60);
        this.uni.setVelocity(0, 0);

        // Restore horn
        this.hasHorn = true;
        this.uni.setTexture('uni_horn');

        // Brief invincibility
        this.uni.setAlpha(0.5);
        this.time.delayedCall(2000, () => {
            this.uni.setAlpha(1);
        });

        this.updateUI();
    }

    visitOwl(uni, owlZone) {
        // Only trigger if Uni doesn't have her horn
        if (this.hasHorn) return;

        // Prevent multiple triggers
        if (this.visitingOwl) return;
        this.visitingOwl = true;

        // Stop Uni briefly
        this.uni.setVelocity(0, 0);
        this.isFrozen = true;

        // Show the magical sequence
        this.showOwlMagicSequence();
    }

    showOwlMagicSequence() {
        // Play owl hoot
        soundManager.owlHoot();

        const messages = [
            { text: 'Mr Owl finds the right book...', delay: 0 },
            { text: '📖 "Hornus Restorus!"', delay: 1500 },
            { text: 'Uni says: "Abracadabra!"', delay: 3000 },
            { text: '✨ Her horn appears again! ✨', delay: 4500 }
        ];

        // Show messages sequentially
        messages.forEach((msg) => {
            this.time.delayedCall(msg.delay, () => {
                this.showMessage(msg.text, 1400);
            });
        });

        // Create sparkle effect around Uni
        this.time.delayedCall(4000, () => {
            this.createSparkleEffect(this.uni.x, this.uni.y);
        });

        // Restore horn after sequence
        this.time.delayedCall(5500, () => {
            // Play horn restored sound
            soundManager.hornRestored();

            this.hasHorn = true;
            this.uni.setTexture('uni_horn');
            this.isFrozen = false;
            this.visitingOwl = false;
            this.updateUI();

            // Celebration effect
            this.tweens.add({
                targets: this.uni,
                scale: 2,
                duration: 200,
                yoyo: true
            });
        });
    }

    createSparkleEffect(x, y) {
        const colors = [0xffd700, 0xff69b4, 0x87ceeb, 0xffffff];

        for (let i = 0; i < 12; i++) {
            const sparkle = this.add.circle(x, y, 5, Phaser.Math.RND.pick(colors));
            const angle = (i / 12) * Math.PI * 2;
            const distance = 50;

            this.tweens.add({
                targets: sparkle,
                x: x + Math.cos(angle) * distance,
                y: y + Math.sin(angle) * distance,
                alpha: 0,
                scale: 0,
                duration: 800,
                ease: 'Power2',
                onComplete: () => sparkle.destroy()
            });
        }
    }

    showCollectEffect(x, y, text, color) {
        const effect = this.add.text(x, y, text, {
            fontSize: '18px',
            fill: color,
            fontFamily: 'Comic Sans MS, cursive',
            stroke: '#ffffff',
            strokeThickness: 3
        }).setOrigin(0.5).setDepth(100);

        this.tweens.add({
            targets: effect,
            y: y - 50,
            alpha: 0,
            duration: 1000,
            ease: 'Power2',
            onComplete: () => effect.destroy()
        });
    }

    showMessage(text, duration) {
        // Get UIScene and show message there
        const uiScene = this.scene.get('UIScene');
        if (uiScene && uiScene.showMessage) {
            uiScene.showMessage(text, duration);
        }
    }

    updateUI() {
        // Emit event to UIScene with all game data
        const uiScene = this.scene.get('UIScene');
        if (uiScene) {
            uiScene.events.emit('updateHUD', {
                lives: this.game.globalData.lives,
                hasHorn: this.hasHorn,
                magicCharges: this.magicCharges,
                collectedMushrooms: this.collectedMushrooms,
                targetMushrooms: this.levelConfig.targetMushrooms,
                timeRemaining: this.timeRemaining,
                currentLevel: this.game.globalData.currentLevel
            });
        }
    }

    timeUp() {
        this.isPaused = true;
        this.timerEvent.remove();

        // Play time up sound
        soundManager.timeUp();

        this.showMessage('⏰ Time\'s up!', 2000);

        this.time.delayedCall(2000, () => {
            this.game.globalData.lives--;
            this.updateUI();

            if (this.game.globalData.lives <= 0) {
                this.gameOver();
            } else {
                // Restart current level
                this.showMessage('Try again!', 1500);
                this.time.delayedCall(1500, () => {
                    this.scene.restart();
                });
            }
        });
    }

    levelComplete() {
        this.isPaused = true;
        if (this.timerEvent) this.timerEvent.remove();

        // Play level complete sound
        soundManager.levelComplete();

        // Show completion in UI
        const uiScene = this.scene.get('UIScene');
        if (uiScene && uiScene.showLevelComplete) {
            uiScene.showLevelComplete(this.game.globalData.currentLevel, () => {
                // Check if there are more levels
                if (this.game.globalData.currentLevel >= 10) {
                    this.youWin();
                } else {
                    this.game.globalData.currentLevel++;
                    this.scene.restart();
                }
            });
        }
    }

    gameOver() {
        this.isPaused = true;
        if (this.timerEvent) this.timerEvent.remove();

        // Play game over sound
        soundManager.gameOver();

        // Show game over in UI
        const uiScene = this.scene.get('UIScene');
        if (uiScene && uiScene.showGameOver) {
            uiScene.showGameOver(() => {
                // Return to menu
                this.scene.stop('UIScene');
                this.scene.start('MenuScene');
            });
        }
    }

    youWin() {
        this.isPaused = true;
        if (this.timerEvent) this.timerEvent.remove();

        // Play victory sound
        soundManager.victory();

        // Show victory in UI
        const uiScene = this.scene.get('UIScene');
        if (uiScene && uiScene.showVictory) {
            uiScene.showVictory(() => {
                // Return to menu
                this.scene.stop('UIScene');
                this.scene.start('MenuScene');
            });
        }
    }
}
