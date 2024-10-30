from knight_moves_6.solver.generate_paths import generate_and_store_paths_a6

if __name__ == "__main__":

    # Run the path generation and storage process
    all_paths = generate_and_store_paths_a6()
    print(f"Identified {len(all_paths)} paths.")

    # Uncomment to test read_paths
    # read_paths()
