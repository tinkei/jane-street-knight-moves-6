import time

import streamlit as st

from knight_moves_6.calculation.constant import GRID
from knight_moves_6.calculation.coordinate_map import string_to_path
from knight_moves_6.model.database import Session, top_n
from knight_moves_6.visualization.plot_grid import visualize_grid


# Cache the top solutions function to avoid constant re-fetching.
@st.cache_data(ttl=29)
def get_top_solutions(n=6):
    # Query the top N solutions
    with Session() as session:
        return top_n(n)


# Periodically poll and display the top solutions.
def display_top_solutions():
    top_solutions = get_top_solutions()
    if not top_solutions:
        st.write("No solutions available. Please wait for new solutions to be added.")
    else:
        for i, solution in enumerate(top_solutions):
            A = solution.A
            B = solution.B
            C = solution.C
            path1 = solution.path1
            path2 = solution.path2
            score1 = solution.score1
            score2 = solution.score2
            st.subheader(f"Solution {i + 1}: Sum of A+B+C = {solution.sum_abc} (A={A}, B={B}, C={C})")
            st.text(f"Path1: {path1} Score1: {score1}")
            st.text(f"Path2: {path2} Score2: {score2}")

            # Visualize the grid for each solution.
            st.plotly_chart(
                visualize_grid(GRID, string_to_path(path1), string_to_path(path2), A, B, C), key=f"Chart {i+1}"
            )


if __name__ == "__main__":

    # Initialize the Streamlit app.
    st.title("Knight Moves 6 Puzzle - Top Solutions")

    # Display the top solutions on page load.
    display_top_solutions()

    # Set up auto-refresh for the Streamlit app.
    # st.write("Auto-refreshing every 30 seconds to display the latest top solutions.")
    # time.sleep(30)
    # st.rerun()
