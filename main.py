#!/usr/bin/env python3
"""
TensorBoard visualization script
Traverse specified folders, read all TensorBoard event files, and generate a combined chart.
"""

import os
import argparse
from pathlib import Path
from collections import defaultdict
import numpy as np
import itertools
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator


def find_tb_files(directories):
    """
    Recursively find all TensorBoard event files in the given directories.

    Args:
        directories: list of directories to search

    Returns:
        list of event file paths
    """
    tb_files = []
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"Warning: directory does not exist: {directory}")
            continue

        # Recursively find all events files
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if file.startswith("events.out.tfevents"):
                    tb_files.append(os.path.join(root, file))

    return tb_files


def load_tb_data(tb_files, base_directories, max_step=None):
    """
    Load TensorBoard data.

    Args:
        tb_files: list of TensorBoard event file paths
        base_directories: base input directories, used to compute relative paths
        max_step: maximum step value to include (data beyond this step will be ignored)

    Returns:
        dict: key is metric name, value is a list of (steps, values, walltimes, run_name)
    """
    data = defaultdict(list)

    # Convert base directories to absolute paths
    base_paths = [Path(d).resolve() for d in base_directories]

    for tb_file in tb_files:
        print(f"Loading: {tb_file}")

        # Parent directory of the event file (usually the log directory)
        tb_file_path = Path(tb_file).resolve()
        log_dir = tb_file_path.parent

        # Find the best matching base directory and compute relative path
        run_name = None
        for base_path in base_paths:
            try:
                # Compute relative path to base directory
                rel_path = log_dir.relative_to(base_path)
                run_name = str(rel_path)
                break
            except ValueError:
                # Not a subdirectory; try the next base directory
                continue

        # If no base directory matches, use the full path
        if run_name is None:
            run_name = str(log_dir)

        try:
            # Create EventAccumulator and load data
            ea = EventAccumulator(tb_file)
            ea.Reload()

            # Get all scalar tags
            scalar_tags = ea.Tags()["scalars"]

            for tag in scalar_tags:
                # Read all events for this tag
                events = ea.Scalars(tag)

                if events:
                    steps = [e.step for e in events]
                    values = [e.value for e in events]
                    walltimes = [e.wall_time for e in events]

                    # Filter data beyond max_step if specified
                    if max_step is not None:
                        filtered_data = [(s, v, w) for s, v, w in zip(steps, values, walltimes) if s <= max_step]
                        if filtered_data:
                            steps, values, walltimes = zip(*filtered_data)
                        else:
                            # Skip this tag if no data remains after filtering
                            continue

                    data[tag].append({
                        "steps": np.array(steps),
                        "values": np.array(values),
                        "walltimes": np.array(walltimes),
                        "run_name": run_name,
                        "file_path": tb_file
                    })

        except Exception as e:
            print(f"Failed to load file {tb_file}: {e}")
            continue

    return data


def smooth_values(values, method="ema", window=10):
    """
    Smooth a 1D array of values.

    Args:
        values: 1D numpy array
        method: "ema" or "ma"
        window: window size (>1)

    Returns:
        smoothed numpy array
    """
    if window is None or window <= 1:
        return values

    if method == "ma":
        kernel = np.ones(int(window), dtype=float) / float(window)
        return np.convolve(values, kernel, mode="same")

    # Exponential moving average (default)
    alpha = 2.0 / (float(window) + 1.0)
    smoothed = np.empty_like(values, dtype=float)
    if values.size == 0:
        return values
    smoothed[0] = values[0]
    for i in range(1, len(values)):
        smoothed[i] = alpha * values[i] + (1.0 - alpha) * smoothed[i - 1]
    return smoothed


def create_visualization(
    data,
    output_path="tensorboard_visualization.png",
    figsize_per_plot=(8, 4),
    max_cols=3,
    show=False,
    smooth_method=None,
    smooth_window=10,
    show_raw_and_smooth=False,
    x_axis="step",
):
    """
    Create a combined visualization figure.

    Args:
        data: data dict returned by load_tb_data
        output_path: output image path
        figsize_per_plot: size of each subplot
        max_cols: maximum subplots per row
        x_axis: x-axis type, "step" or "walltime"
    """
    if not data:
        print("No data to visualize")
        return

    # Compute subplot count and layout
    n_metrics = len(data)
    n_cols = min(n_metrics, max_cols)
    n_rows = (n_metrics + n_cols - 1) // n_cols

    # Create the figure
    fig_width = figsize_per_plot[0] * n_cols
    fig_height = figsize_per_plot[1] * n_rows

    fig = plt.figure(figsize=(fig_width, fig_height))
    gs = GridSpec(n_rows, n_cols, figure=fig, hspace=0.4, wspace=0.3)

    # Build a stable color map per run name
    color_cycle = plt.rcParams.get("axes.prop_cycle", None)
    colors = []
    if color_cycle is not None:
        colors = color_cycle.by_key().get("color", [])
    if not colors:
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    color_iter = itertools.cycle(colors)
    run_color_map = {}

    # Create a subplot for each metric
    for idx, (metric_name, runs_data) in enumerate(sorted(data.items())):
        row = idx // n_cols
        col = idx % n_cols
        ax = fig.add_subplot(gs[row, col])

        # Plot data for each run
        for run_data in runs_data:
            steps = run_data["steps"]
            values = run_data["values"]
            walltimes = run_data["walltimes"]
            run_name = run_data["run_name"]

            # Choose x-axis data based on parameter
            if x_axis == "walltime":
                # Convert walltime to relative time in hours from the first event
                if len(walltimes) > 0:
                    x_data = (walltimes - walltimes[0]) / 3600.0  # Convert to hours
                else:
                    x_data = walltimes
            else:
                x_data = steps

            run_color = run_color_map.get(run_name)
            if run_color is None:
                run_color = next(color_iter)
                run_color_map[run_name] = run_color

            if smooth_method and show_raw_and_smooth:
                raw_line, = ax.plot(
                    x_data,
                    values,
                    label="_nolegend_",
                    color=run_color,
                    alpha=0.35,
                    linewidth=1.0,
                )
                smooth_values_arr = smooth_values(values, method=smooth_method, window=smooth_window)
                ax.plot(
                    x_data,
                    smooth_values_arr,
                    label=run_name,
                    color=raw_line.get_color(),
                    alpha=0.9,
                    linewidth=1.6,
                )
                continue

            if smooth_method:
                values = smooth_values(values, method=smooth_method, window=smooth_window)

            # Draw curve
            ax.plot(x_data, values, label=run_name, color=run_color, alpha=0.8, linewidth=1.5)

        # Set title and labels
        ax.set_title(metric_name, fontsize=10, fontweight="bold")
        x_label = "Wall Time (hours)" if x_axis == "walltime" else "Step"
        ax.set_xlabel(x_label, fontsize=9)
        ax.set_ylabel("Value", fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(labelsize=8)

        # Show legend
        ax.legend(fontsize=7, loc="best", framealpha=0.7)

    # Set overall title
    fig.suptitle("TensorBoard Metrics Visualization", fontsize=16, fontweight="bold", y=0.995)

    # Save image
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nVisualization saved to: {output_path}")
    print(f"Figure size: {fig_width}x{fig_height} inches")
    print(f"Total metrics plotted: {n_metrics}")

    # Optionally show the figure (safe for headless environments)
    if show:
        try:
            plt.show()
        except Exception as e:
            print(f"Warning: failed to show figure: {e}")

    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a combined visualization from TensorBoard logs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python draw_tb.py ./run1 ./run2 ./run3
    python draw_tb.py ./experiments/* -o results.png
    python draw_tb.py ./logs -o output.png --max-cols 4
    python draw_tb.py ./logs --x-axis walltime --smooth ema
        """,
    )

    parser.add_argument("directories", nargs="+", help="Directories containing TensorBoard logs")
    parser.add_argument("-o", "--output", default="tensorboard_visualization.png", help="Output image path (default: tensorboard_visualization.png)")
    parser.add_argument("--width", type=float, default=8, help="Width of each subplot in inches (default: 8)")
    parser.add_argument("--height", type=float, default=4, help="Height of each subplot in inches (default: 4)")
    parser.add_argument("--max-cols", type=int, default=3, help="Maximum number of subplots per row (default: 3)")
    parser.add_argument("--show", action="store_true", help="Show the visualization window if available")
    parser.add_argument("--smooth", choices=["ema", "ma"], default=None, help="Enable curve smoothing: ema (exponential) or ma (moving average)")
    parser.add_argument("--smooth-window", type=int, default=10, help="Smoothing window size (default: 10)")
    parser.add_argument("--show-both", action="store_true", help="Show raw curve and smoothed curve together (requires --smooth)")
    parser.add_argument("--x-axis", choices=["step", "walltime"], default="step", help="X-axis type: step (default) or walltime (in hours)")
    parser.add_argument("--max-step", type=int, default=None, help="Maximum step value to include (data beyond this step will be ignored)")

    args = parser.parse_args()

    print("=" * 60)
    print("TensorBoard Visualization Tool")
    print("=" * 60)
    print(f"Search directories: {args.directories}")
    print()

    # Find all TensorBoard files
    tb_files = find_tb_files(args.directories)

    if not tb_files:
        print("Error: no TensorBoard event files found")
        return

    print(f"\nFound {len(tb_files)} TensorBoard event files")
    print()

    # Load data, passing base directories to compute relative paths
    data = load_tb_data(tb_files, args.directories, max_step=args.max_step)

    if not data:
        print("Error: failed to load any data")
        return

    print(f"\nSuccessfully loaded {len(data)} metrics")
    print()

    # Create visualization
    create_visualization(
        data,
        output_path=args.output,
        figsize_per_plot=(args.width, args.height),
        max_cols=args.max_cols,
        show=args.show,
        smooth_method=args.smooth,
        smooth_window=args.smooth_window,
        show_raw_and_smooth=args.show_both,
        x_axis=args.x_axis,
    )

    print("\nDone!")


if __name__ == "__main__":
    main()
