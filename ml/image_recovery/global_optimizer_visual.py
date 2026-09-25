import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image


# ============================================================
# ReFrag AI — Visual Global Reconstruction
# Uses foreground-aware visual compatibility
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

FRAGMENTS_DIR = BASE_DIR / "test" / "fragments"
ARTIFACT_DIR = BASE_DIR / "test" / "artifacts"
OUTPUT_DIR = BASE_DIR / "test" / "output"

MATRIX_FILE = (
    ARTIFACT_DIR /
    "visual_compatibility.json"
)

OUTPUT_FILE = (
    OUTPUT_DIR /
    "reconstructed_visual.png"
)

RESULT_FILE = (
    ARTIFACT_DIR /
    "visual_reconstruction_result.json"
)

GRID = 8
TILE = 96

ROTATIONS = (
    0,
    90,
    180,
    270
)

# Optimization
RESTARTS = 8
ITERATIONS = 14000

INITIAL_TEMPERATURE = 0.025
FINAL_TEMPERATURE = 0.0005

PRINT_EVERY = 1000

RANDOM_SEED = 42

random.seed(
    RANDOM_SEED
)

np.random.seed(
    RANDOM_SEED
)


# ============================================================
# LOAD MATRIX
# ============================================================

def load_matrix():

    print()
    print(
        "Loading foreground-aware "
        "compatibility matrix..."
    )

    with open(
        MATRIX_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    matrix = {}

    relationships = data[
        "relationships"
    ]

    for item in relationships:

        name_a = item[
            "fragment_a"
        ]

        rotation_a = int(
            item[
                "rotation_a"
            ]
        )

        name_b = item[
            "fragment_b"
        ]

        rotation_b = int(
            item[
                "rotation_b"
            ]
        )

        direction = item[
            "direction"
        ]

        score = float(
            item[
                "score"
            ]
        )

        matrix.setdefault(
            name_a,
            {}
        )

        matrix[
            name_a
        ].setdefault(
            rotation_a,
            {
                "RIGHT": {},
                "DOWN": {}
            }
        )

        matrix[
            name_a
        ][rotation_a][
            direction
        ][
            (
                name_b,
                rotation_b
            )
        ] = score

    print(
        f"Relationships loaded: "
        f"{len(relationships)}"
    )

    return matrix


# ============================================================
# LOAD FRAGMENTS
# ============================================================

def load_fragments():

    fragments = {}

    for path in sorted(
        FRAGMENTS_DIR.glob(
            "F*.png"
        )
    ):

        image = Image.open(
            path
        ).convert(
            "RGB"
        )

        image = image.resize(
            (
                TILE,
                TILE
            )
        )

        fragments[
            path.stem
        ] = np.asarray(
            image,
            dtype=np.uint8
        )

    return fragments


# ============================================================
# COMPATIBILITY LOOKUP
# ============================================================

def get_cost(
    matrix,
    a,
    b,
    direction
):

    name_a, rotation_a = a
    name_b, rotation_b = b

    try:

        return matrix[
            name_a
        ][rotation_a][
            direction
        ][
            (
                name_b,
                rotation_b
            )
        ]

    except KeyError:

        return 1.0


# ============================================================
# TOTAL ENERGY
# ============================================================

def total_energy(
    state,
    matrix
):

    energy = 0.0

    for position in range(
        GRID * GRID
    ):

        row = (
            position // GRID
        )

        col = (
            position % GRID
        )

        # RIGHT
        if col < GRID - 1:

            energy += get_cost(
                matrix,
                state[position],
                state[
                    position + 1
                ],
                "RIGHT"
            )

        # DOWN
        if row < GRID - 1:

            energy += get_cost(
                matrix,
                state[position],
                state[
                    position + GRID
                ],
                "DOWN"
            )

    return float(
        energy
    )


# ============================================================
# LOCAL ENERGY
# ============================================================

def local_energy(
    state,
    position,
    matrix
):

    total = 0.0

    row = (
        position // GRID
    )

    col = (
        position % GRID
    )

    # LEFT
    if col > 0:

        total += get_cost(
            matrix,
            state[
                position - 1
            ],
            state[position],
            "RIGHT"
        )

    # RIGHT
    if col < GRID - 1:

        total += get_cost(
            matrix,
            state[position],
            state[
                position + 1
            ],
            "RIGHT"
        )

    # TOP
    if row > 0:

        total += get_cost(
            matrix,
            state[
                position - GRID
            ],
            state[position],
            "DOWN"
        )

    # BOTTOM
    if row < GRID - 1:

        total += get_cost(
            matrix,
            state[position],
            state[
                position + GRID
            ],
            "DOWN"
        )

    return float(
        total
    )


# ============================================================
# GREEDY INITIAL SOLUTION
# ============================================================

def greedy_solution(
    names,
    matrix
):

    print()
    print(
        "Creating visual greedy "
        "starting solution..."
    )

    best_state = None
    best_energy = float(
        "inf"
    )

    # Try multiple starting pieces.
    starts = []

    for name in names:

        for rotation in ROTATIONS:

            starts.append(
                (
                    name,
                    rotation
                )
            )

    random.shuffle(
        starts
    )

    starts = starts[:128]

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

            row = (
                position // GRID
            )

            col = (
                position % GRID
            )

            candidates = []

            for name in names:

                if name in used:
                    continue

                for rotation in ROTATIONS:

                    candidate = (
                        name,
                        rotation
                    )

                    cost = 0.0
                    count = 0

                    # LEFT
                    if col > 0:

                        left = state[
                            position - 1
                        ]

                        cost += get_cost(
                            matrix,
                            left,
                            candidate,
                            "RIGHT"
                        )

                        count += 1

                    # TOP
                    if row > 0:

                        top = state[
                            position - GRID
                        ]

                        cost += get_cost(
                            matrix,
                            top,
                            candidate,
                            "DOWN"
                        )

                        count += 1

                    if count:

                        cost /= count

                    candidates.append(
                        (
                            cost,
                            candidate
                        )
                    )

            candidates.sort(
                key=lambda x: x[0]
            )

            _, selected = (
                candidates[0]
            )

            state[
                position
            ] = selected

            used.add(
                selected[0]
            )

        energy = total_energy(
            state,
            matrix
        )

        if energy < best_energy:

            best_energy = energy
            best_state = state.copy()

    print(
        f"Initial visual energy: "
        f"{best_energy:.6f}"
    )

    return (
        best_state,
        best_energy
    )


# ============================================================
# SIMULATED ANNEALING
# ============================================================

def optimize(
    initial_state,
    matrix,
    restart
):

    state = initial_state.copy()

    # Randomize starting state for restart.
    shuffle_count = (
        5 + restart * 2
    )

    for _ in range(
        shuffle_count
    ):

        a = random.randrange(
            GRID * GRID
        )

        b = random.randrange(
            GRID * GRID
        )

        if a != b:

            state[a], state[b] = (
                state[b],
                state[a]
            )

    current_energy = total_energy(
        state,
        matrix
    )

    best_state = state.copy()
    best_energy = current_energy

    for iteration in range(
        ITERATIONS
    ):

        progress = (
            iteration /
            ITERATIONS
        )

        temperature = (
            INITIAL_TEMPERATURE
            * (
                1.0 -
                progress
            )
            +
            FINAL_TEMPERATURE
            * progress
        )

        # ----------------------------------------------------
        # Rotation move
        # ----------------------------------------------------

        if random.random() < 0.40:

            position = random.randrange(
                GRID * GRID
            )

            old_piece = state[
                position
            ]

            name, old_rotation = (
                old_piece
            )

            possible_rotations = [
                r
                for r in ROTATIONS
                if r != old_rotation
            ]

            new_rotation = random.choice(
                possible_rotations
            )

            old_local = local_energy(
                state,
                position,
                matrix
            )

            state[position] = (
                name,
                new_rotation
            )

            new_local = local_energy(
                state,
                position,
                matrix
            )

            delta = (
                new_local -
                old_local
            )

            accept = (
                delta <= 0
                or
                random.random()
                <
                math.exp(
                    -delta /
                    max(
                        temperature,
                        1e-9
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

        # ----------------------------------------------------
        # Swap move
        # ----------------------------------------------------

        else:

            a = random.randrange(
                GRID * GRID
            )

            b = random.randrange(
                GRID * GRID
            )

            if a == b:
                continue

            old_a = local_energy(
                state,
                a,
                matrix
            )

            old_b = local_energy(
                state,
                b,
                matrix
            )

            state[a], state[b] = (
                state[b],
                state[a]
            )

            new_a = local_energy(
                state,
                a,
                matrix
            )

            new_b = local_energy(
                state,
                b,
                matrix
            )

            delta = (
                new_a +
                new_b -
                old_a -
                old_b
            )

            accept = (
                delta <= 0
                or
                random.random()
                <
                math.exp(
                    -delta /
                    max(
                        temperature,
                        1e-9
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

        # ----------------------------------------------------
        # Best solution
        # ----------------------------------------------------

        if current_energy < best_energy:

            best_energy = (
                current_energy
            )

            best_state = (
                state.copy()
            )

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

    return (
        best_state,
        best_energy
    )


# ============================================================
# CONFIDENCE
# ============================================================

def confidence(
    state,
    matrix
):

    total = 0.0
    count = 0

    for position in range(
        GRID * GRID
    ):

        row = (
            position // GRID
        )

        col = (
            position % GRID
        )

        if col < GRID - 1:

            total += get_cost(
                matrix,
                state[position],
                state[
                    position + 1
                ],
                "RIGHT"
            )

            count += 1

        if row < GRID - 1:

            total += get_cost(
                matrix,
                state[position],
                state[
                    position + GRID
                ],
                "DOWN"
            )

            count += 1

    mean_cost = (
        total /
        max(count, 1)
    )

    value = (
        100.0 *
        math.exp(
            -4.0 *
            mean_cost
        )
    )

    return float(
        max(
            0.0,
            min(
                100.0,
                value
            )
        )
    )


# ============================================================
# RENDER
# ============================================================

def render(
    state
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
    ) in enumerate(
        state
    ):

        image = Image.open(
            FRAGMENTS_DIR /
            f"{name}.png"
        ).convert(
            "RGB"
        )

        image = image.resize(
            (
                TILE,
                TILE
            )
        )

        if rotation == 90:

            image = image.rotate(
                90,
                expand=True
            )

        elif rotation == 180:

            image = image.rotate(
                180,
                expand=True
            )

        elif rotation == 270:

            image = image.rotate(
                270,
                expand=True
            )

        image = np.asarray(
            image,
            dtype=np.uint8
        )

        row = (
            position // GRID
        )

        col = (
            position % GRID
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
    score
):

    data = {
        "success": True,
        "algorithm": (
            "foreground_aware_global_optimizer"
        ),
        "grid_size": int(
            GRID
        ),
        "fragment_count": int(
            len(state)
        ),
        "energy": float(
            energy
        ),
        "confidence": float(
            score
        ),
        "fragments": []
    }

    for position, (
        name,
        rotation
    ) in enumerate(
        state
    ):

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
        " ReFrag AI — Visual Global Reconstruction"
    )
    print("=" * 65)

    fragments = load_fragments()

    print()
    print(
        f"Fragments: "
        f"{len(fragments)}"
    )

    if len(fragments) != 64:

        raise RuntimeError(
            "Expected 64 fragments."
        )

    names = list(
        fragments.keys()
    )

    matrix = load_matrix()

    initial_state, initial_energy = (
        greedy_solution(
            names,
            matrix
        )
    )

    global_best_state = (
        initial_state.copy()
    )

    global_best_energy = (
        initial_energy
    )

    print()
    print("=" * 65)
    print(
        " VISUAL GLOBAL OPTIMIZATION"
    )
    print("=" * 65)

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
            matrix,
            restart
        )

        print(
            f"  Restart energy: "
            f"{energy:.6f}"
        )

        if energy < global_best_energy:

            global_best_energy = (
                energy
            )

            global_best_state = (
                state.copy()
            )

            print(
                "  ★ NEW GLOBAL BEST"
            )

    final_confidence = confidence(
        global_best_state,
        matrix
    )

    render(
        global_best_state
    )

    save_result(
        global_best_state,
        global_best_energy,
        final_confidence
    )

    print()
    print("=" * 65)
    print(
        " FINAL VISUAL RECONSTRUCTION"
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
        f"{final_confidence:.2f}%"
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
        " VISUAL RECONSTRUCTION COMPLETE"
    )
    print("=" * 65)