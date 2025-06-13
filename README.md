# Gerson Sim

Gerson Sim is a reflex-based bullet-hell mini-game inspired by Undertale's mechanics. Defend the soul using a directional shield as arrows fly in from all sides. The arrows vary in speed, but all arrive at a steady rhythm—can you keep up?

## 🎮 Gameplay

- Use **arrow keys** to rotate your shield and block incoming arrows.
- If an arrow hits your soul and the shield is not aligned, you take damage.
- As the game progresses, arrow patterns speed up and get more complex.
- Score points by successfully blocking arrows.

## 🕹️ Features

- Dynamic arrow speeds with timing compensation.
- Octagon shield upgrade for increased difficulty.
- Real-time audio effects for block, hit, and game over.
- Background music with seamless loop.
- Scaling difficulty over time with faster arrow rates.

## 🔧 Controls

| Key        | Action                      |
|------------|-----------------------------|
| Arrow Keys | Rotate shield               |
| R          | Restart after game over     |
| Any Key    | Start game from splash menu |

## 📁 Project Structure

```
project/
├── assets/
│   ├── arrow_*.png          # Standard arrow images (per direction)
│   ├── red_arrow_*.png      # Highlighted arrows
│   ├── soul.png             # The player's soul
│   ├── block.wav            # Block sound effect
│   ├── hurt.wav             # Hit sound effect
│   ├── game_over.wav        # Game over sound
│   └── music.ogg            # Background music
├── main.py                  # Game logic
└── README.md
```

## 🚀 Run the Game

Download the release (on the right of your screen under 'Releases'), unzip, and start the game!

## 📈 Scoring & Difficulty

- You start with 3 HP.
- Game gets harder over time: arrows per second gradually increase.
- Shield upgrades from square to octagon after 12 seconds.
- Arrows are dynamically queued based on speed to maintain a constant rhythm.

## 📜 Credits

Created by **LennyTheSniper**

Inspired by Undertale and Deltarune’s combat mini-games.

---

Enjoy the fight, and protect your soul!
