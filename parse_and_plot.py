import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import os
import glob
import csv

def find_latest_file(pattern):
    """Find the most recently modified file matching the pattern."""
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def parse_dat_file(filename):
    if not filename or not os.path.exists(filename):
        print(f"File {filename} not found.")
        return None

    print(f"Parsing {filename}...")
    data = defaultdict(list)
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if len(parts) == 4:
                size = int(parts[0])
                patch = int(parts[1])
                nprocs = int(parts[2])
                rtime = float(parts[3])
                data[(size, nprocs)].append(rtime)
    
    means = {}
    for k, times in data.items():
        means[k] = np.mean(times)
    
    return means

def calculate_metrics(means, sizes, nprocs_list):
    results = {}
    for size in sizes:
        # Base time for 1 proc
        t1 = means.get((size, 1), None)
        for p in nprocs_list:
            tp = means.get((size, p), None)
            if t1 is not None and tp is not None:
                speedup = t1 / tp
                efficiency = speedup / p
                results[(size, p)] = (tp, speedup, efficiency)
    return results

def save_to_csv(results, sizes, nprocs_list, filename):
    """Saves the results to a CSV file for LaTeX import."""
    print(f"Saving results to {filename}...")
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Header matching the user request: size p mean runtime (s) speed-up par. eff.
        writer.writerow(['size', 'p', 'runtime', 'speedup', 'efficiency'])
        for size in sizes:
            for p in nprocs_list:
                if (size, p) in results:
                    tp, speedup, efficiency = results[(size, p)]
                    writer.writerow([size, p, f"{tp:.4f}", f"{speedup:.2f}", f"{efficiency:.2f}"])

def generate_markdown_table(results, sizes, nprocs_list, title):
    print(f"\n### {title}")
    print("| Size | Cores | Mean Runtime (s) | Speed-up | Parallel Efficiency |")
    print("|---|---|---|---|---|")
    for size in sizes:
        for p in nprocs_list:
            if (size, p) in results:
                tp, speedup, efficiency = results[(size, p)]
                print(f"| {size} | {p} | {tp:.4f} | {speedup:.2f} | {efficiency:.2f} |")

def plot_metrics(results, sizes, nprocs_list, suffix, c_type):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Absolute Runtime
    ax = axes[0]
    for size in sizes:
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        times = [results[(size, p)][0] for p in valid_procs]
        ax.plot(valid_procs, times, marker='o', label=f'size={size}')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Running Time (s)')
    ax.set_title(f'Absolute Running Time ({c_type})')
    ax.legend()
    ax.grid(True)
    
    # Relative Speed-up
    ax = axes[1]
    for size in sizes:
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        speedups = [results[(size, p)][1] for p in valid_procs]
        ax.plot(valid_procs, speedups, marker='o', label=f'size={size}')
    # Add ideal speedup line
    ax.plot(nprocs_list, nprocs_list, 'k--', label='Ideal Speed-up')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Relative Speed-up')
    ax.set_title(f'Relative Speed-up ({c_type})')
    ax.legend()
    ax.grid(True)
    
    # Parallel Efficiency
    ax = axes[2]
    for size in sizes:
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        efficiencies = [results[(size, p)][2] for p in valid_procs]
        ax.plot(valid_procs, efficiencies, marker='o', label=f'size={size}')
    # Add ideal efficiency line
    ax.axhline(y=1.0, color='k', linestyle='--', label='Ideal Efficiency')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Parallel Efficiency')
    ax.set_title(f'Parallel Efficiency ({c_type})')
    ax.legend()
    ax.grid(True)
    
    plt.tight_layout()
    plot_file = f'benchmark_plots_{suffix}.png'
    plt.savefig(plot_file)
    print(f"Saved plot to {plot_file}")

def process_dat_file(dat_file, nprocs_list, sizes):
    """Parse a .dat file, compute metrics, save CSV, print table, and generate plots."""
    means = parse_dat_file(dat_file)
    if means is None:
        return

    found_sizes = sorted(set(s for s, _ in means.keys()))
    found_nprocs = sorted(set(p for _, p in means.keys()))

    results = calculate_metrics(means, found_sizes, found_nprocs)

    basename = os.path.splitext(os.path.basename(dat_file))[0]
    suffix = basename.replace("output_", "")
    csv_file = f"results_{suffix}.csv"
    plot_file_suffix = suffix

    generate_markdown_table(results, found_sizes, found_nprocs, f"Table for {basename}")
    save_to_csv(results, found_sizes, found_nprocs, csv_file)
    plot_metrics(results, found_sizes, found_nprocs, plot_file_suffix, basename)


if __name__ == "__main__":
    nprocs_list = [1, 2, 4, 8, 16, 24, 32]
    sizes = [120, 1030]

    dat_files = sorted(glob.glob("output_exp22*.dat"))

    if not dat_files:
        print("No output_exp22*.dat files found in the current directory.")
    else:
        print(f"Found {len(dat_files)} data file(s): {dat_files}\n")
        for dat_file in dat_files:
            print(f"{'='*60}")
            process_dat_file(dat_file, nprocs_list, sizes)
            print()


# uv run --with matplotlib --with numpy python3 parse_and_plot.py
