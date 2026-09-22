# Team Organization & Management Report

## 1. Team Allocation & Individual Contributions

Work was divided between core algorithmic backend architecture and the graphical interface/rendering pipelines.

### Saad Ksioui (`sksioui`)

* **Core Physics & Movement:** Designed the initial `Position`, `_Entity`, `_Pacman`, and `_Ghost` class hierarchies. Developed continuous pixel-movement math, keyboard vector handling, and velocity management.


* **AI Pathfinding & Behaviors:** Implemented BFS pathfinding algorithms. Structured specific ghost chase targeting formulas (including Blinky vector calculation and Inky pivot geometry).


* **State Machine & Gameplay Logic:** Built out the ghost state transitions (Chase, Frightened, Eaten) and respawn path routing. Handled entity collision resolution, player lives counters, and power pellet integration.


* **Developer Tooling & Cheats:** Implemented the evaluator cheat toolkit (Invincibility, Level Skip, Ghost Freeze, Speed Boost, Extra Lives). Authored project build automation, including the root `Makefile` configured for execution, debugging (`pdb`), and linting (`flake8`, `mypy`).



### Salah Mahraz (`smahraz`)

* **UI & Menu Systems:** Created the initial menu hierarchy and screen flow (Main Menu, Leaderboard, Score Saving, Pause Menu). Migrated UI interactions from cursor-based mouse coordinates to keyboard-focused navigation.


* **Rendering & Graphics Engine:** Built Pyray rendering routines for the maze wall geometry, sprite sheet animation states, Pacman direction masks, and HUD lives indicators.


* **Configuration & Validation:** Implemented initial JSON comment-stripping mechanisms and schema validation fallback routines.


* **Score Persistence & Polish:** Structured highscore JSON writing and parsing. Handled sprite color refinements, UI asset scaling, and output stream silencing for Pyray logs.



---

## 2. Decision-Making Process

* **Separation of Concerns (UI vs. Physics):** An early decision split the application into `paclib/menus.py` (navigation, user inputs, campaign loops) and `paclib/engine.py` (collision detection, delta-time math, pathfinding). This eliminated circular dependencies and prevented UI components from interfering with physics updates.
* **Continuous Delta-Time vs. Grid Snapping:** While grid-based systems simplify intersection detection, moving entities via `get_frame_time()` continuous pixel velocity was selected to ensure authentic arcade fluidity.
* **Frightened Ghost AI (Arcade Panic vs. Fixed Corners):** Rather than routing frightened ghosts to static corners (which caused them to run toward Pac-Man if he stood in their path), a pseudo-random turn algorithm filtering out direct 180° reversals was chosen.
* **Data Validation Strategy:** Pydantic models with robust exception handling (`ValidationError`, `JSONDecodeError`) were chosen over manual schema parsing to enforce strict type checking and fallback safety when reading configuration files.

---

## 3. Issue Tracking & Problem Resolution

```
+-----------------------------------+-----------------------------------+-----------------------------------+
| Issue Encountered                 | Root Cause                        | Engineering Resolution            |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Ghost Wall Tunneling              | Single-sided floating-point       | Replaced remainder logic with a   |
|                                   | modulo in `is_close_cellcenter`   | dual-sided window (`dx < 0.15` or |
|                                   | failed on leftward/upward delta   | `dx > 0.85`) to catch movement in |
|                                   | steps where remainder wrapped.    | all directions.                   |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Frightened Ghost Stutter / Freeze | Ghosts recalculated random turns  | Added `last_pos` tracking to the  |
|                                   | across consecutive frames while   | `_Ghost` class to restrict AI     |
|                                   | remaining within the cell center. | decisions to a single run per     |
|                                   |                                   | tile intersection.                |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Menu Selection Loop Trigger       | `KEY_ENTER` events persisted      | Added `skip_click` debouncing and |
|                                   | across loop iterations,           | an input-drain loop to flush key  |
|                                   | instantly re-selecting menus.     | presses before changing screens.  |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Circular Import Deadlock          | `engine.py` attempted to load UI  | Decoupled components completely:  |
|                                   | elements directly from            | engine returns state/score tuples |
|                                   | `menus.py`.                       | back to `GamePage` controllers.   |
+-----------------------------------+-----------------------------------+-----------------------------------+
| Target Out-of-Bounds Crash        | Offset target vectors (e.g.,      | Clamped calculated targets to the |
|                                   | Pinky's 4-tile lead) generated    | inner boundaries of the matrix    |
|                                   | coordinates outside maze array.   | prior to passing them to the BFS. |
+-----------------------------------+-----------------------------------+-----------------------------------+

```

---

## 4. Development Workflow & Milestones

The project was executed in three chronological milestones tracked via Git commit history:

```
Jul 21 - Aug 8              Aug 10 - Sep 14             Sep 16 - Sep 22
[ M1: Foundations ] ------> [ M2: Core Loop ] --------> [ M3: Polish & Tooling ]
* Architecture Setup        * Dynamic AI Personalities  * Cheat Engine (F1-F5)
* Maze Matrix Rendering     * UI/Menus & Navigation     * Collision Bugfixes
* Entity Classes            * Score & Config Loading    * Flake8/MyPy Validation

```

* **M1: Foundations (Late July – Early August):** Base classes established, Raylib window initialization configured, and bitmask maze wall decoding built.


* **M2: Core Gameplay Loop (Mid August – Mid September):** Ghost BFS chase personalities added, super pacgum timers connected, and UI state routing built.


* **M3: Polish & Tooling (Mid September):** Anti-tunneling physics resolved, evaluation cheat hooks integrated, and Makefile build tooling set up.