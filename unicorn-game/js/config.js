/**
 * Game Configuration
 * Central place for all game settings - easy to modify for different levels
 */

const GAME_CONFIG = {
    // Display settings
    width: 800,
    height: 600,

    // Player settings
    player: {
        speed: 200,
        startLives: 3,
        freezeDuration: 3000, // milliseconds
        invincibilityDuration: 2000 // after being hit
    },

    // Enemy settings (Mr Fox)
    enemy: {
        speed: 100, // Base speed - increases with levels
        chaseDistance: 400 // How close before fox starts chasing
    },

    // Mushroom settings
    mushrooms: {
        safeMushrooms: 15, // Number of safe mushrooms to spawn
        redMushrooms: 5, // Number of red (bad) mushrooms
        respawnDelay: 3000 // Time before mushroom respawns after collection
    },

    // Level settings
    levels: {
        1: {
            targetMushrooms: 10,
            timeLimit: 180, // seconds
            foxSpeed: 100,
            redMushroomCount: 5
        },
        2: {
            targetMushrooms: 15,
            timeLimit: 150,
            foxSpeed: 130,
            redMushroomCount: 7
        },
        3: {
            targetMushrooms: 20,
            timeLimit: 120,
            foxSpeed: 160,
            redMushroomCount: 10
        }
    },

    // Colors for placeholder graphics
    colors: {
        unicornBody: 0xffffff,       // White
        unicornHorn: 0xffd700,       // Gold
        unicornMane: 0xff69b4,       // Pink
        unicornNoHorn: 0xcccccc,     // Gray (when horn is lost)
        foxBody: 0xff6600,           // Orange
        foxTail: 0xffffff,           // White tail tip
        safeMushroom: 0x8b4513,      // Brown cap
        safeMushroomSpots: 0xffffff, // White spots
        redMushroom: 0xff0000,       // Red cap
        redMushroomSpots: 0xffffff,  // White spots
        grass: 0x228b22,             // Forest green
        tree: 0x2d5a27              // Dark green
    }
};

// Game state that persists between scenes
const GameState = {
    currentLevel: 1,
    totalScore: 0,
    lives: GAME_CONFIG.player.startLives,
    hasHorn: true,

    // Reset for new game
    reset() {
        this.currentLevel = 1;
        this.totalScore = 0;
        this.lives = GAME_CONFIG.player.startLives;
        this.hasHorn = true;
    },

    // Level up
    nextLevel() {
        this.currentLevel++;
        this.hasHorn = true; // Restore horn at start of new level
        return this.currentLevel <= Object.keys(GAME_CONFIG.levels).length;
    }
};
