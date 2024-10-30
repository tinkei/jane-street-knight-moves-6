from enum import Enum, auto

import plotly.graph_objects as go

from knight_moves_6.calculation.calculate_score import (
    calculate_path_score,
    calculate_path_score_cumulative,
    calculate_path_score_marginal,
)
from knight_moves_6.calculation.coordinate_map import coord_to_index, path_to_solution_string, path_to_string


class ShowPath(Enum):
    A1 = auto()
    A6 = auto()
    BOTH = auto()


def visualize_grid(
    grid: list[list[str]],
    path1: list[str],
    path2: list[str],
    A: int,
    B: int,
    C: int,
    show_path: ShowPath = ShowPath.BOTH,
) -> go.Figure:
    """
    Visualize the grid with accumulated scores along a knight's path.

    Args:
        grid (list of list of str): 2D grid with "A", "B", "C" values.
        path1 (list of str): List of coordinates representing the knight's path from "a1" to "f6".
        path2 (list of str): List of coordinates representing the knight's path from "a6" to "f1".
        A (int): The positive integer value for "A" in the grid.
        B (int): The positive integer value for "B" in the grid.
        C (int): The positive integer value for "C" in the grid.
        show_path (ShowPath): Whether to display only one of the two paths, or both.

    Returns:
        The visualization plot.
    """
    # Mapping grid values to their corresponding integers
    symbol_map = {"A": A, "B": B, "C": C}

    # Calculate cumulative and marginal scores along the path
    path1_cumulative_scores = calculate_path_score_cumulative(grid, path1, A, B, C)
    path2_cumulative_scores = calculate_path_score_cumulative(grid, path2, A, B, C)
    path1_marginal_scores = calculate_path_score_marginal(grid, path1, A, B, C)
    path2_marginal_scores = calculate_path_score_marginal(grid, path2, A, B, C)

    # Convert path to indices.
    path1_row_col = [coord_to_index(coord) for coord in path1]
    path2_row_col = [coord_to_index(coord) for coord in path2]

    # Initialize accumulated score grid and text annotations for cells.
    cumulative_scores = [[None] * 6 for _ in range(6)]
    cell_text = [[""] * 6 for _ in range(6)]
    arrows_1 = []
    arrows_2 = []

    # TODO: Don't duplicate the accumulation logic.
    #  The code is duplicated because we wish to display the operators +/x,
    #  which is information not found in `calculate_path_score_cumulative()`.
    # Start accumulating score along Path 1.
    if show_path in (ShowPath.BOTH, ShowPath.A1):
        prev_row, prev_col = path1_row_col[0]
        prev_symbol = grid[prev_row][prev_col]
        score = symbol_map[prev_symbol]
        for i, (row, col) in enumerate(path1_row_col):
            curr_symbol = grid[row][col]
            score_change = symbol_map[curr_symbol]
            operator = "+"

            # Apply the scoring rule based on the path 1.
            if i > 0:
                if curr_symbol == prev_symbol:
                    # Same value, add.
                    score += score_change
                    operator = "+"
                else:
                    # Different value, multiply.
                    score *= score_change
                    operator = "x"

                # Calculate start and end positions centered on cells for plotting arrows.
                arrows_1.append(
                    {
                        "start_x": prev_col,
                        "start_y": prev_row,
                        "end_x": col,
                        "end_y": row,
                    }
                )
                prev_row, prev_col = row, col
                prev_symbol = curr_symbol

            # This isn't really the accumulated value, but a hack to display similar colors along the same path.
            cumulative_scores[row][col] = (i + 1) / len(path2) + 1  # score == path1_cumulative_scores[i]
            if score != path1_cumulative_scores[i]:
                raise ValueError("Score calculation mismatch.")

            # Generate cell text (e.g., "A (x2): 4" for original value, marginal increase, and accumulated value).
            cell_text[row][col] = f"Path 1 Step {i+1}:<br>{curr_symbol} ({operator}{score_change}): {score}"

    # Start accumulating score along Path 2.
    if show_path in (ShowPath.BOTH, ShowPath.A6):
        prev_row, prev_col = path2_row_col[0]
        prev_symbol = grid[prev_row][prev_col]
        score = symbol_map[prev_symbol]
        for i, (row, col) in enumerate(path2_row_col):
            curr_symbol = grid[row][col]
            score_change = symbol_map[curr_symbol]
            operator = "+"

            # Apply the scoring rule based on the path.
            if i > 0:
                if curr_symbol == prev_symbol:
                    # Same value, add.
                    score += score_change
                    operator = "+"
                else:
                    # Different value, multiply.
                    score *= score_change
                    operator = "x"

                # Store start and end positions centered on cells for plotting arrows.
                arrows_2.append(
                    {
                        "start_x": prev_col,
                        "start_y": prev_row,
                        "end_x": col,
                        "end_y": row,
                    }
                )
                prev_row, prev_col = row, col
                prev_symbol = curr_symbol

            # Since this is the second path, multiply by -1 to give it a different color on the heatmap.
            # This isn't really the accumulated value, but a hack to display similar colors along the same path.
            if cumulative_scores[row][col] is not None:
                cumulative_scores[row][col] += -(i + 1) / len(path2) - 1  # - score
            else:
                cumulative_scores[row][col] = -(i + 1) / len(path2) - 1  # - score
            if score != path2_cumulative_scores[i]:
                raise ValueError("Score calculation mismatch.")

            # Generate cell text (e.g., "A (x2): 4" for original value, marginal increase, and accumulated value).
            if cell_text[row][col] == "":
                cell_text[row][col] += f"Path 2 Step {i+1}:<br>{curr_symbol} ({operator}{score_change}): {score}"
            else:
                cell_text[row][
                    col
                ] += f"<br><br>Path 2 Step {i+1}:<br>{curr_symbol} ({operator}{score_change}): {score}"

    # Set up the plot title and subtitle.
    title = f"Sum = {A + B + C} (A={A}, B={B}, C={C})"
    if show_path == ShowPath.BOTH:
        subtitle = f"Solution string: {path_to_solution_string(A, B, C, path1, path2)}"
    elif show_path == ShowPath.A1:
        subtitle = f"Solution path: {path_to_string(path1)}"
    elif show_path == ShowPath.A6:
        subtitle = f"Solution path: {path_to_string(path2)}"

    # Create the grid using heatmap.
    fig = go.Figure(
        data=go.Heatmap(
            z=cumulative_scores,
            text=cell_text,
            texttemplate="%{text}",
            # textfont={"size": 30},
            colorscale="Viridis",
            # colorbar=dict(title="Accumulated Score"),
            colorbar=dict(title="Step"),
        )
    )

    # Add a semi-transparent arrow shape pointing out each step along the path.
    for coordinates in arrows_1:
        start_x = coordinates["start_x"]
        start_y = coordinates["start_y"]
        end_x = coordinates["end_x"]
        end_y = coordinates["end_y"]
        fig.add_annotation(
            x=end_x,
            y=end_y,
            ax=start_x,
            ay=start_y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            # arrowhead=3,
            # arrowsize=3,
            # arrowwidth=8,
            arrowcolor="rgba(255, 0, 0, 0.5)",
        )
    for coordinates in arrows_2:
        start_x = coordinates["start_x"]
        start_y = coordinates["start_y"]
        end_x = coordinates["end_x"]
        end_y = coordinates["end_y"]
        fig.add_annotation(
            x=end_x,
            y=end_y,
            ax=start_x,
            ay=start_y,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            # arrowhead=3,
            # arrowsize=3,
            # arrowwidth=8,
            arrowcolor="rgba(135, 206, 235, 0.5)",
        )

    # Add text annotations "A, B, C" to each cell.
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            fig.add_annotation(
                x=col - 0.4,
                y=row + 0.3,
                xref="x",
                yref="y",
                text=grid[row][col],
                showarrow=False,
                # font_size=80,
                font_color="rgba(200, 200, 200, 0.8)",
            )

    # Configure figure settings.
    fig.update_layout(
        font=dict(
            # family="Courier New, monospace",
            # size=28,
            # color="RebeccaPurple",
            # variant="small-caps",
        ),
        title={
            "text": f"{title}<br><sup>{subtitle}</sup>",
            "x": 0.5,
            "xanchor": "center",
            # "font": 30,
        },
        xaxis=dict(
            title="Column",
            tickvals=list(range(6)),
            ticktext=["a", "b", "c", "d", "e", "f"],
            ticks="outside",
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
        yaxis=dict(
            title="Row",
            tickvals=list(range(6)),
            ticktext=list(range(1, 7)),
            ticks="outside",
            showgrid=False,
            showline=False,
            zeroline=False,
        ),
    )

    return fig


if __name__ == "__main__":

    # Test the function with an example grid, path, and values.
    from knight_moves_6.calculation.constant import GRID, MY_SOLUTION, SAMPLE_SOLUTION
    from knight_moves_6.calculation.coordinate_map import solution_string_to_coordinate_list

    solution_string = SAMPLE_SOLUTION
    solution_string = MY_SOLUTION
    A, B, C, path1, path2 = solution_string_to_coordinate_list(solution_string)
    print(A, B, C)
    print(path1)
    print(path2)
    # path1 = ["a1", "b3", "c5", "d3", "f4", "d5", "f6"]
    # path2 = ["a6", "c5", "a4", "b2", "c4", "d2", "f1"]
    path1_score = calculate_path_score(GRID, path1, A, B, C)
    path2_score = calculate_path_score(GRID, path2, A, B, C)
    print(path1_score)
    print(path2_score)

    # Visualize the grid and path.
    fig = visualize_grid(GRID, path1, path2, A, B, C)
    fig.show()
