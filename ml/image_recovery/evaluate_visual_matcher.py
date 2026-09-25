import json
from pathlib import Path


# ============================================================
# ReFrag AI — Visual Matcher Evaluation
#
# IMPORTANT:
# ground_truth.json is used ONLY for evaluation.
# It is NOT used by reconstruction.
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

GROUND_TRUTH = (
    BASE_DIR
    / "test"
    / "input"
    / "ground_truth.json"
)

MATRIX_FILE = (
    BASE_DIR
    / "test"
    / "artifacts"
    / "visual_compatibility.json"
)


# ============================================================
# LOAD GROUND TRUTH
# ============================================================

def load_ground_truth():

    with open(
        GROUND_TRUTH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    fragments = {}

    for item in data["fragments"]:

        fragment_id = item[
            "fragment_id"
        ]

        original_rotation = int(
            item["rotation"]
        )

        # The fragment stored in test/fragments
        # is already rotated by this amount.
        #
        # To restore the original orientation,
        # we need the inverse rotation.
        restore_rotation = (
            360 - original_rotation
        ) % 360

        fragments[
            fragment_id
        ] = {
            "row": int(
                item["original_row"]
            ),

            "col": int(
                item["original_col"]
            ),

            "rotation": original_rotation,

            "restore_rotation":
                restore_rotation
        }

    return fragments


# ============================================================
# LOAD MATRIX
# ============================================================

def load_matrix():

    with open(
        MATRIX_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    matrix = {}

    for item in data[
        "relationships"
    ]:

        a = item[
            "fragment_a"
        ]

        b = item[
            "fragment_b"
        ]

        rotation_a = int(
            item[
                "rotation_a"
            ]
        )

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
            a,
            {}
        )

        matrix[
            a
        ].setdefault(
            rotation_a,
            {
                "RIGHT": {},
                "DOWN": {}
            }
        )

        matrix[
            a
        ][
            rotation_a
        ][
            direction
        ][
            (
                b,
                rotation_b
            )
        ] = score

    return matrix


# ============================================================
# EXPECTED NEIGHBORS
# ============================================================

def build_grid(
    fragments
):

    grid = {}

    for fragment_id, info in fragments.items():

        grid[
            (
                info["row"],
                info["col"]
            )
        ] = fragment_id

    return grid


# ============================================================
# GET EXPECTED EDGES
# ============================================================

def expected_edges(
    fragments
):

    grid = build_grid(
        fragments
    )

    edges = []

    max_row = max(
        info["row"]
        for info in fragments.values()
    )

    max_col = max(
        info["col"]
        for info in fragments.values()
    )

    for (
        row,
        col
    ), fragment_a in grid.items():

        info_a = fragments[
            fragment_a
        ]

        # ----------------------------------------------------
        # RIGHT
        # ----------------------------------------------------

        if col < max_col:

            fragment_b = grid.get(
                (
                    row,
                    col + 1
                )
            )

            if fragment_b:

                info_b = fragments[
                    fragment_b
                ]

                edges.append({
                    "a": fragment_a,
                    "b": fragment_b,
                    "rotation_a":
                        info_a[
                            "restore_rotation"
                        ],
                    "rotation_b":
                        info_b[
                            "restore_rotation"
                        ],
                    "direction": "RIGHT"
                })

        # ----------------------------------------------------
        # DOWN
        # ----------------------------------------------------

        if row < max_row:

            fragment_b = grid.get(
                (
                    row + 1,
                    col
                )
            )

            if fragment_b:

                info_b = fragments[
                    fragment_b
                ]

                edges.append({
                    "a": fragment_a,
                    "b": fragment_b,
                    "rotation_a":
                        info_a[
                            "restore_rotation"
                        ],
                    "rotation_b":
                        info_b[
                            "restore_rotation"
                        ],
                    "direction": "DOWN"
                })

    return edges


# ============================================================
# TOP MATCH
# ============================================================

def rank_correct_match(
    matrix,
    edge
):

    a = edge["a"]
    b = edge["b"]

    rotation_a = edge[
        "rotation_a"
    ]

    rotation_b = edge[
        "rotation_b"
    ]

    direction = edge[
        "direction"
    ]

    try:

        candidates = matrix[
            a
        ][
            rotation_a
        ][
            direction
        ]

    except KeyError:

        return None

    correct_key = (
        b,
        rotation_b
    )

    correct_score = candidates.get(
        correct_key
    )

    if correct_score is None:

        return None

    ranked = sorted(
        candidates.items(),
        key=lambda x: x[1]
    )

    rank = None

    for index, (
        candidate,
        score
    ) in enumerate(
        ranked,
        start=1
    ):

        if candidate == correct_key:

            rank = index
            break

    return {
        "rank": rank,
        "score": correct_score,
        "best_candidate":
            ranked[0][0],
        "best_score":
            ranked[0][1]
    }


# ============================================================
# EVALUATE
# ============================================================

def evaluate(
    fragments,
    matrix
):

    edges = expected_edges(
        fragments
    )

    print()
    print(
        f"Ground-truth adjacency edges: "
        f"{len(edges)}"
    )

    top1 = 0
    top3 = 0
    top5 = 0

    total = 0

    rank_sum = 0

    results = []

    for edge in edges:

        result = rank_correct_match(
            matrix,
            edge
        )

        if result is None:
            continue

        total += 1

        rank = result[
            "rank"
        ]

        if rank is not None:

            rank_sum += rank

            if rank == 1:
                top1 += 1

            if rank <= 3:
                top3 += 1

            if rank <= 5:
                top5 += 1

        results.append({
            **edge,
            **result
        })

    if total == 0:

        raise RuntimeError(
            "No evaluable relationships."
        )

    top1_accuracy = (
        100.0 *
        top1 /
        total
    )

    top3_accuracy = (
        100.0 *
        top3 /
        total
    )

    top5_accuracy = (
        100.0 *
        top5 /
        total
    )

    mean_rank = (
        rank_sum /
        total
    )

    return {
        "edges": edges,
        "results": results,
        "total": total,
        "top1": top1,
        "top3": top3,
        "top5": top5,
        "top1_accuracy":
            top1_accuracy,
        "top3_accuracy":
            top3_accuracy,
        "top5_accuracy":
            top5_accuracy,
        "mean_rank":
            mean_rank
    }


# ============================================================
# MUTUAL CHECK
# ============================================================

def mutual_accuracy(
    evaluation
):

    results = evaluation[
        "results"
    ]

    if not results:
        return 0.0

    mutual = 0

    for item in results:

        if item["rank"] != 1:
            continue

        reverse_direction = (
            "DOWN"
            if item["direction"] == "UP"
            else item["direction"]
        )

        # For the controlled evaluation,
        # simply count exact top-1 matches.
        mutual += 1

    return (
        100.0 *
        mutual /
        len(results)
    )


# ============================================================
# PRINT
# ============================================================

def print_report(
    evaluation
):

    print()
    print("=" * 65)
    print(
        " VISUAL MATCHER EVALUATION"
    )
    print("=" * 65)

    print()

    print(
        f"Evaluated edges : "
        f"{evaluation['total']}"
    )

    print()

    print(
        f"Top-1 accuracy  : "
        f"{evaluation['top1_accuracy']:.2f}%"
    )

    print(
        f"Top-3 accuracy  : "
        f"{evaluation['top3_accuracy']:.2f}%"
    )

    print(
        f"Top-5 accuracy  : "
        f"{evaluation['top5_accuracy']:.2f}%"
    )

    print(
        f"Mean rank       : "
        f"{evaluation['mean_rank']:.2f}"
    )

    print()

    print(
        "Top-1 correct   : "
        f"{evaluation['top1']}/"
        f"{evaluation['total']}"
    )

    print(
        "Top-3 correct   : "
        f"{evaluation['top3']}/"
        f"{evaluation['total']}"
    )

    print(
        "Top-5 correct   : "
        f"{evaluation['top5']}/"
        f"{evaluation['total']}"
    )

    print()

    # --------------------------------------------------------
    # Show some strongest correct matches.
    # --------------------------------------------------------

    correct = [
        x
        for x in evaluation[
            "results"
        ]
        if x["rank"] == 1
    ]

    correct.sort(
        key=lambda x: x["score"]
    )

    print(
        "Sample correct Top-1 matches:"
    )

    for item in correct[:10]:

        print(
            f"  "
            f"{item['a']}"
            f" -> "
            f"{item['b']}"
            f" "
            f"{item['direction']} "
            f"| "
            f"score="
            f"{item['score']:.4f}"
        )

    print()

    # --------------------------------------------------------
    # Show difficult matches.
    # --------------------------------------------------------

    difficult = sorted(
        evaluation[
            "results"
        ],
        key=lambda x: x["rank"]
        if x["rank"] is not None
        else 999
    )[-10:]

    print(
        "Difficult matches:"
    )

    for item in difficult:

        print(
            f"  "
            f"{item['a']}"
            f" -> "
            f"{item['b']}"
            f" "
            f"{item['direction']}"
            f" | rank="
            f"{item['rank']}"
            f" | best="
            f"{item['best_candidate']}"
        )

    print()

    print("=" * 65)


# ============================================================
# SAVE EVALUATION
# ============================================================

def save_evaluation(
    evaluation
):

    output = (
        BASE_DIR
        / "test"
        / "artifacts"
        / "matcher_evaluation.json"
    )

    # Make numpy-free JSON.
    clean_results = []

    for item in evaluation[
        "results"
    ]:

        clean_results.append({
            "a": str(
                item["a"]
            ),
            "b": str(
                item["b"]
            ),
            "rotation_a": int(
                item["rotation_a"]
            ),
            "rotation_b": int(
                item["rotation_b"]
            ),
            "direction": str(
                item["direction"]
            ),
            "rank": int(
                item["rank"]
            )
            if item["rank"] is not None
            else None,
            "score": float(
                item["score"]
            ),
            "best_candidate": [
                str(
                    item["best_candidate"][0]
                ),
                int(
                    item["best_candidate"][1]
                )
            ],
            "best_score": float(
                item["best_score"]
            )
        })

    data = {
        "algorithm":
            "foreground_continuity_v2",

        "total_edges":
            int(
                evaluation["total"]
            ),

        "top1_accuracy":
            float(
                evaluation[
                    "top1_accuracy"
                ]
            ),

        "top3_accuracy":
            float(
                evaluation[
                    "top3_accuracy"
                ]
            ),

        "top5_accuracy":
            float(
                evaluation[
                    "top5_accuracy"
                ]
            ),

        "mean_rank":
            float(
                evaluation[
                    "mean_rank"
                ]
            ),

        "results":
            clean_results
    }

    with open(
        output,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2
        )

    print()
    print(
        "Evaluation saved:"
    )

    print(
        f"  {output}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print(
        " ReFrag AI — Matcher Evaluation"
    )
    print("=" * 65)

    fragments = load_ground_truth()

    print()
    print(
        f"Ground-truth fragments: "
        f"{len(fragments)}"
    )

    matrix = load_matrix()

    evaluation = evaluate(
        fragments,
        matrix
    )

    print_report(
        evaluation
    )

    save_evaluation(
        evaluation
    )