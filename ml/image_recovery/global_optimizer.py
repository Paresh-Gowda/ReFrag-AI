import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image


# ============================================================
# ReFrag AI
# Global Jigsaw Optimizer
#
# Rotation + permutation + global consistency
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FRAGMENTS_DIR = BASE_DIR / "test" / "fragments"
OUTPUT_DIR = BASE_DIR / "test" / "output"
ARTIFACT_DIR = BASE_DIR / "test" / "artifacts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "reconstructed_global.png"
RESULT_FILE = ARTIFACT_DIR / "global_optimization_result.json"

GRID = 8
TILE = 96

ROTATIONS = (0, 90, 180, 270)

# Number of pixels around a seam.
BAND = 8

# Optimization settings.
RESTARTS = 12
ITERATIONS = 18000

INITIAL_TEMPERATURE = 0.08
FINAL_TEMPERATURE = 0.001

# Every N iterations print progress.
PRINT_EVERY = 1000

RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


# ============================================================
# LOAD FRAGMENTS
# ============================================================

def load_fragments():

    fragments = {}

    files = sorted(
        FRAGMENTS_DIR.glob("F*.png")
    )

    for path in files:

        image = Image.open(
            path
        ).convert("RGB")

        if image.size != (
            TILE,
            TILE
        ):

            image = image.resize(
                (TILE, TILE)
            )

        fragments[path.stem] = np.asarray(
            image,
            dtype=np.float32
        )

    return fragments


# ============================================================
# ROTATIONS
# ============================================================

def build_rotations(fragments):

    rotations = {}

    for name, image in fragments.items():

        rotations[name] = {}

        for rotation in ROTATIONS:

            if rotation == 0:

                rotated = image

            elif rotation == 90:

                rotated = np.rot90(
                    image,
                    1
                )

            elif rotation == 180:

                rotated = np.rot90(
                    image,
                    2
                )

            else:

                rotated = np.rot90(
                    image,
                    3
                )

            rotations[name][rotation] = (
                np.ascontiguousarray(
                    rotated
                )
            )

    return rotations


# ============================================================
# GRAYSCALE
# ============================================================

def gray(image):

    return (
        0.299 * image[:, :, 0]
        + 0.587 * image[:, :, 1]
        + 0.114 * image[:, :, 2]
    )


# ============================================================
# EDGE PROFILE
# ============================================================

def edge_profile(image, side):

    """
    Extract the edge region used for compatibility.
    """

    if side == "L":

        return image[
            :,
            :BAND,
            :
        ]

    if side == "R":

        return image[
            :,
            -BAND:,
            :
        ]

    if side == "T":

        return image[
            :BAND,
            :,
            :
        ]

    if side == "B":

        return image[
            -BAND:,
            :,
            :
        ]

    raise ValueError(side)


# ============================================================
# SEAM COMPATIBILITY
# ============================================================

def seam_cost(
    image_a,
    image_b,
    direction
):

    """
    MGC-style seam compatibility.

    Lower = better.

    RIGHT:
        A is left of B

    DOWN:
        A is above B
    """

    if direction == "RIGHT":

        a_last = image_a[
            :,
            -1,
            :
        ]

        a_prev = image_a[
            :,
            -2,
            :
        ]

        b_first = image_b[
            :,
            0,
            :
        ]

        b_next = image_b[
            :,
            1,
            :
        ]

        # Expected continuation from A.
        predicted_b = (
            2.0 * a_last
            - a_prev
        )

        # Expected continuation backwards from B.
        predicted_a = (
            2.0 * b_first
            - b_next
        )

        forward_error = np.mean(
            np.abs(
                predicted_b
                - b_first
            )
        )

        backward_error = np.mean(
            np.abs(
                predicted_a
                - a_last
            )
        )

        gradient_a = (
            a_last
            - a_prev
        )

        gradient_b = (
            b_next
            - b_first
        )

        gradient_error = np.mean(
            np.abs(
                gradient_a
                - gradient_b
            )
        )

        # Wider-band color continuity.
        band_a = image_a[
            :,
            -BAND:,
            :
        ]

        band_b = image_b[
            :,
            :BAND,
            :
        ]

        color_error = np.mean(
            np.abs(
                band_a[:, -1, :]
                - band_b[:, 0, :]
            )
        )

    else:

        a_last = image_a[
            -1,
            :,
            :
        ]

        a_prev = image_a[
            -2,
            :,
            :
        ]

        b_first = image_b[
            0,
            :,
            :
        ]

        b_next = image_b[
            1,
            :,
            :
        ]

        predicted_b = (
            2.0 * a_last
            - a_prev
        )

        predicted_a = (
            2.0 * b_first
            - b_next
        )

        forward_error = np.mean(
            np.abs(
                predicted_b
                - b_first
            )
        )

        backward_error = np.mean(
            np.abs(
                predicted_a
                - a_last
            )
        )

        gradient_a = (
            a_last
            - a_prev
        )

        gradient_b = (
            b_next
            - b_first
        )

        gradient_error = np.mean(
            np.abs(
                gradient_a
                - gradient_b
            )
        )

        band_a = image_a[
            -BAND:,
            :,
            :
        ]

        band_b = image_b[
            :BAND,
            :,
            :
        ]

        color_error = np.mean(
            np.abs(
                band_a[-1, :, :]
                - band_b[0, :, :]
            )
        )

    # Normalize.
    forward_error /= 255.0
    backward_error /= 255.0
    gradient_error /= 255.0
    color_error /= 255.0

    # Combined MGC-style score.
    cost = (
        0.30 * forward_error
        + 0.25 * backward_error
        + 0.30 * gradient_error
        + 0.15 * color_error
    )

    return float(cost)


# ============================================================
# COMPATIBILITY MATRIX
# ============================================================

def build_compatibility(
    rotations,
    names
):

    print()
    print(
        "Building compatibility matrix..."
    )

    compatibility = {}

    total = (
        len(names)
        * len(names)
        * 16
    )

    completed = 0

    for index_a, name_a in enumerate(
        names
    ):

        compatibility[name_a] = {}

        for rotation_a in ROTATIONS:

            compatibility[
                name_a
            ][rotation_a] = {
                "RIGHT": {},
                "DOWN": {}
            }

            image_a = rotations[
                name_a
            ][rotation_a]

            for name_b in names:

                if name_a == name_b:
                    continue

                for rotation_b in ROTATIONS:

                    image_b = rotations[
                        name_b
                    ][rotation_b]

                    compatibility[
                        name_a
                    ][rotation_a]["RIGHT"][
                        (name_b, rotation_b)
                    ] = seam_cost(
                        image_a,
                        image_b,
                        "RIGHT"
                    )

                    compatibility[
                        name_a
                    ][rotation_a]["DOWN"][
                        (name_b, rotation_b)
                    ] = seam_cost(
                        image_a,
                        image_b,
                        "DOWN"
                    )

                    completed += 2

            if index_a % 8 == 7:

                print(
                    f"  processed "
                    f"{index_a + 1}/"
                    f"{len(names)}"
                )

    print(
        "Compatibility matrix ready."
    )

    return compatibility


# ============================================================
# BEST-BUDDY MAP
# ============================================================

def build_best_buddies(
    compatibility,
    names
):

    print()
    print(
        "Building mutual best-neighbor map..."
    )

    buddies = {}

    for name in names:

        buddies[name] = {}

        for rotation in ROTATIONS:

            for direction in (
                "RIGHT",
                "DOWN"
            ):

                candidates = (
                    compatibility[
                        name
                    ][rotation][direction]
                )

                if not candidates:
                    continue

                best = min(
                    candidates.items(),
                    key=lambda x: x[1]
                )

                buddies[
                    name,
                    rotation,
                    direction
                ] = best[0]

    print(
        "Best-buddy map ready."
    )

    return buddies


# ============================================================
# POSITION HELPERS
# ============================================================

def neighbors(position):

    row = position // GRID
    col = position % GRID

    result = []

    if col > 0:
        result.append(
            (
                position - 1,
                "RIGHT"
            )
        )

    if col < GRID - 1:
        result.append(
            (
                position + 1,
                "RIGHT"
            )
        )

    if row > 0:
        result.append(
            (
                position - GRID,
                "DOWN"
            )
        )

    if row < GRID - 1:
        result.append(
            (
                position + GRID,
                "DOWN"
            )
        )

    return result


# ============================================================
# EDGE COST BETWEEN POSITIONS
# ============================================================

def directed_cost(
    state,
    position_a,
    position_b,
    direction,
    compatibility
):

    name_a, rot_a = state[
        position_a
    ]

    name_b, rot_b = state[
        position_b
    ]

    if direction == "RIGHT":

        return compatibility[
            name_a
        ][rot_a]["RIGHT"].get(
            (name_b, rot_b),
            1.0
        )

    return compatibility[
        name_a
    ][rot_a]["DOWN"].get(
        (name_b, rot_b),
        1.0
    )


# ============================================================
# TOTAL ENERGY
# ============================================================

def total_energy(
    state,
    compatibility
):

    energy = 0.0

    for position in range(
        GRID * GRID
    ):

        row = position // GRID
        col = position % GRID

        # Right edge.
        if col < GRID - 1:

            energy += directed_cost(
                state,
                position,
                position + 1,
                "RIGHT",
                compatibility
            )

        # Down edge.
        if row < GRID - 1:

            energy += directed_cost(
                state,
                position,
                position + GRID,
                "DOWN",
                compatibility
            )

    return float(energy)


# ============================================================
# LOCAL ENERGY
# ============================================================

def local_energy(
    state,
    position,
    compatibility
):

    total = 0.0

    row = position // GRID
    col = position % GRID

    if col > 0:

        total += directed_cost(
            state,
            position - 1,
            position,
            "RIGHT",
            compatibility
        )

    if col < GRID - 1:

        total += directed_cost(
            state,
            position,
            position + 1,
            "RIGHT",
            compatibility
        )

    if row > 0:

        total += directed_cost(
            state,
            position - GRID,
            position,
            "DOWN",
            compatibility
        )

    if row < GRID - 1:

        total += directed_cost(
            state,
            position,
            position + GRID,
            "DOWN",
            compatibility
        )

    return float(total)


# ============================================================
# AFFECTED POSITIONS
# ============================================================

def affected_positions(
    a,
    b=None
):

    positions = set()

    targets = [a]

    if b is not None:
        targets.append(b)

    for position in targets:

        positions.add(position)

        row = position // GRID
        col = position % GRID

        if col > 0:
            positions.add(
                position - 1
            )

        if col < GRID - 1:
            positions.add(
                position + 1
            )

        if row > 0:
            positions.add(
                position - GRID
            )

        if row < GRID - 1:
            positions.add(
                position + GRID
            )

    return positions


# ============================================================
# ENERGY FOR AFFECTED AREA
# ============================================================

def affected_energy(
    state,
    positions,
    compatibility
):

    total = 0.0

    checked = set()

    for position in positions:

        row = position // GRID
        col = position % GRID

        if col < GRID - 1:

            edge = (
                position,
                position + 1,
                "RIGHT"
            )

            if edge not in checked:

                total += directed_cost(
                    state,
                    position,
                    position + 1,
                    "RIGHT",
                    compatibility
                )

                checked.add(edge)

        if row < GRID - 1:

            edge = (
                position,
                position + GRID,
                "DOWN"
            )

            if edge not in checked:

                total += directed_cost(
                    state,
                    position,
                    position + GRID,
                    "DOWN",
                    compatibility
                )

                checked.add(edge)

    return float(total)


# ============================================================
# INITIAL GREEDY SOLUTION
# ============================================================

def greedy_initial_solution(
    names,
    compatibility
):

    print()
    print(
        "Creating greedy starting solution..."
    )

    # Start from every fragment/orientation
    # and retain the best complete solution.

    best_state = None
    best_score = float("inf")

    trials = min(
        len(names) * 4,
        256
    )

    starts = []

    for name in names:

        for rotation in ROTATIONS:

            starts.append(
                (
                    name,
                    rotation
                )
            )

    random.shuffle(starts)

    starts = starts[
        :trials
    ]

    for start_name, start_rotation in starts:

        state = [
            None
        ] * (
            GRID * GRID
        )

        state[0] = (
            start_name,
            start_rotation
        )

        used = {
            start_name
        }

        for position in range(
            1,
            GRID * GRID
        ):

            row = position // GRID
            col = position % GRID

            candidates = []

            for name in names:

                if name in used:
                    continue

                for rotation in ROTATIONS:

                    score = 0.0
                    count = 0

                    # Left.
                    if col > 0:

                        left = state[
                            position - 1
                        ]

                        if left is not None:

                            ln, lr = left

                            score += compatibility[
                                ln
                            ][lr]["RIGHT"].get(
                                (
                                    name,
                                    rotation
                                ),
                                1.0
                            )

                            count += 1

                    # Top.
                    if row > 0:

                        top = state[
                            position - GRID
                        ]

                        if top is not None:

                            tn, tr = top

                            score += compatibility[
                                tn
                            ][tr]["DOWN"].get(
                                (
                                    name,
                                    rotation
                                ),
                                1.0
                            )

                            count += 1

                    if count:

                        score /= count

                    candidates.append(
                        (
                            score,
                            name,
                            rotation
                        )
                    )

            candidates.sort(
                key=lambda x: x[0]
            )

            _, name, rotation = (
                candidates[0]
            )

            state[position] = (
                name,
                rotation
            )

            used.add(name)

        score = total_energy(
            state,
            compatibility
        )

        if score < best_score:

            best_score = score
            best_state = state.copy()

    print(
        f"Initial energy: "
        f"{best_score:.6f}"
    )

    return best_state, best_score


# ============================================================
# SIMULATED ANNEALING
# ============================================================

def optimize(
    initial_state,
    compatibility,
    restart
):

    state = initial_state.copy()

    current_energy = total_energy(
        state,
        compatibility
    )

    best_state = state.copy()
    best_energy = current_energy

    # Random perturbation for restarts.
    perturbations = (
        10 + restart * 3
    )

    for _ in range(
        perturbations
    ):

        a = random.randrange(
            GRID * GRID
        )

        b = random.randrange(
            GRID * GRID
        )

        if a == b:
            continue

        state[a], state[b] = (
            state[b],
            state[a]
        )

    current_energy = total_energy(
        state,
        compatibility
    )

    if current_energy < best_energy:

        best_energy = current_energy
        best_state = state.copy()

    for iteration in range(
        ITERATIONS
    ):

        progress = (
            iteration
            / ITERATIONS
        )

        temperature = (
            INITIAL_TEMPERATURE
            * (
                1.0
                - progress
            )
            + FINAL_TEMPERATURE
            * progress
        )

        move_type = random.random()

        # ====================================================
        # ROTATION MOVE
        # ====================================================

        if move_type < 0.35:

            position = random.randrange(
                GRID * GRID
            )

            affected = affected_positions(
                position
            )

            old_energy = affected_energy(
                state,
                affected,
                compatibility
            )

            name, old_rotation = (
                state[position]
            )

            possible = [
                r
                for r in ROTATIONS
                if r != old_rotation
            ]

            new_rotation = random.choice(
                possible
            )

            state[position] = (
                name,
                new_rotation
            )

            new_energy = affected_energy(
                state,
                affected,
                compatibility
            )

            delta = (
                new_energy
                - old_energy
            )

            accept = (
                delta <= 0
                or random.random()
                < math.exp(
                    -delta
                    / max(
                        temperature,
                        1e-8
                    )
                )
            )

            if accept:

                current_energy += delta

            else:

                state[position] = (
                    name,
                    old_rotation
                )

        # ====================================================
        # SWAP MOVE
        # ====================================================

        else:

            a = random.randrange(
                GRID * GRID
            )

            b = random.randrange(
                GRID * GRID
            )

            if a == b:
                continue

            affected = affected_positions(
                a,
                b
            )

            old_energy = affected_energy(
                state,
                affected,
                compatibility
            )

            state[a], state[b] = (
                state[b],
                state[a]
            )

            new_energy = affected_energy(
                state,
                affected,
                compatibility
            )

            delta = (
                new_energy
                - old_energy
            )

            accept = (
                delta <= 0
                or random.random()
                < math.exp(
                    -delta
                    / max(
                        temperature,
                        1e-8
                    )
                )
            )

            if accept:

                current_energy += delta

            else:

                state[a], state[b] = (
                    state[b],
                    state[a]
                )

        # ====================================================
        # BEST
        # ====================================================

        if current_energy < best_energy:

            best_energy = current_energy
            best_state = state.copy()

        # ====================================================
        # PROGRESS
        # ====================================================

        if (
            iteration + 1
        ) % PRINT_EVERY == 0:

            print(
                f"    "
                f"{iteration + 1:5d}/"
                f"{ITERATIONS}"
                f" | current="
                f"{current_energy:.5f}"
                f" | best="
                f"{best_energy:.5f}"
            )

    return best_state, best_energy


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    state,
    compatibility
):

    total = 0.0
    count = 0

    for position in range(
        GRID * GRID
    ):

        row = position // GRID
        col = position % GRID

        if col < GRID - 1:

            total += directed_cost(
                state,
                position,
                position + 1,
                "RIGHT",
                compatibility
            )

            count += 1

        if row < GRID - 1:

            total += directed_cost(
                state,
                position,
                position + GRID,
                "DOWN",
                compatibility
            )

            count += 1

    if count == 0:
        return 0.0

    mean_cost = (
        total / count
    )

    confidence = (
        100.0
        * math.exp(
            -5.0 * mean_cost
        )
    )

    return float(
        max(
            0.0,
            min(
                100.0,
                confidence
            )
        )
    )


# ============================================================
# RENDER
# ============================================================

def render(
    state,
    rotations
):

    canvas = np.zeros(
        (
            GRID * TILE,
            GRID * TILE,
            3
        ),
        dtype=np.uint8
    )

    for position, (
        name,
        rotation
    ) in enumerate(state):

        row = position // GRID
        col = position % GRID

        image = rotations[
            name
        ][rotation]

        image = np.clip(
            image,
            0,
            255
        ).astype(
            np.uint8
        )

        y = row * TILE
        x = col * TILE

        canvas[
            y:y + TILE,
            x:x + TILE
        ] = image

    Image.fromarray(
        canvas
    ).save(
        OUTPUT_FILE
    )


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
    state,
    energy,
    confidence
):

    data = {
        "success": True,
        "algorithm": (
            "global_simulated_annealing"
        ),
        "grid_size": int(GRID),
        "fragment_count": int(
            len(state)
        ),
        "global_energy": float(
            energy
        ),
        "confidence": float(
            confidence
        ),
        "fragments": []
    }

    for position, (
        name,
        rotation
    ) in enumerate(state):

        data[
            "fragments"
        ].append({

            "position": int(
                position
            ),

            "row": int(
                position // GRID
            ),

            "column": int(
                position % GRID
            ),

            "fragment": str(
                name
            ),

            "rotation": int(
                rotation
            )
        })

    with open(
        RESULT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print(
        " ReFrag AI — Global Jigsaw Optimizer"
    )
    print("=" * 65)

    fragments = load_fragments()

    print()
    print(
        f"Fragments loaded: "
        f"{len(fragments)}"
    )

    if len(fragments) != 64:

        raise RuntimeError(
            "Expected exactly 64 fragments."
        )

    names = list(
        fragments.keys()
    )

    rotations = build_rotations(
        fragments
    )

    compatibility = build_compatibility(
        rotations,
        names
    )

    buddies = build_best_buddies(
        compatibility,
        names
    )

    # Keep variable intentionally available
    # for future evidence reporting.
    _ = buddies

    initial_state, initial_energy = (
        greedy_initial_solution(
            names,
            compatibility
        )
    )

    global_best_state = (
        initial_state.copy()
    )

    global_best_energy = (
        initial_energy
    )

    print()
    print(
        "=" * 65
    )

    print(
        " GLOBAL OPTIMIZATION"
    )

    print(
        "=" * 65
    )

    for restart in range(
        RESTARTS
    ):

        print()
        print(
            f"Restart "
            f"{restart + 1}/"
            f"{RESTARTS}"
        )

        state, energy = optimize(
            initial_state,
            compatibility,
            restart
        )

        print(
            f"  Restart energy: "
            f"{energy:.6f}"
        )

        if energy < global_best_energy:

            global_best_energy = energy

            global_best_state = (
                state.copy()
            )

            print(
                "  ★ New global best"
            )

    confidence = calculate_confidence(
        global_best_state,
        compatibility
    )

    render(
        global_best_state,
        rotations
    )

    save_result(
        global_best_state,
        global_best_energy,
        confidence
    )

    print()
    print("=" * 65)
    print(
        " FINAL RECONSTRUCTION"
    )
    print("=" * 65)

    print(
        f"Fragments : "
        f"{len(global_best_state)}/64"
    )

    print(
        f"Energy    : "
        f"{global_best_energy:.6f}"
    )

    print(
        f"Confidence: "
        f"{confidence:.2f}%"
    )

    print()
    print(
        "Output:"
    )

    print(
        f"  {OUTPUT_FILE}"
    )

    print()
    print(
        "Result:"
    )

    print(
        f"  {RESULT_FILE}"
    )

    print()
    print("=" * 65)
    print(
        " GLOBAL OPTIMIZATION COMPLETE"
    )
    print("=" * 65)