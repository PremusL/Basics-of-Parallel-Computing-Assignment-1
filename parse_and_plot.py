import os
import glob
import csv
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
matplotlib.use('Agg') # Using Anti-Grain Geometry

def find_latest_file(pattern):
    """Find the most recently modified file matching the pattern."""
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def parse_calc_means(filename):
    if not filename or not os.path.exists(filename):
        print(f"File {filename} not found.")
        return None

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
        writer.writerow(['size', 'p', 'runtime', 'speedup', 'efficiency'])
        for size in sizes:
            for p in nprocs_list:
                if (size, p) in results:
                    tp, speedup, efficiency = results[(size, p)]
                    writer.writerow([size, p, f"{tp:.4f}", f"{speedup:.2f}", f"{efficiency:.2f}"])

def save_plot(fig, filename):
    base_path = './figs/'
    plt.tight_layout()
    plt.savefig(base_path + filename)
    plt.close(fig)
    print(f"Saved plot to {filename}")

def plot_metrics(results, sizes, nprocs_list, suffix, c_type):
    benchmark_bool = "benchmark" in c_type
    # Absolute Runtime
    fig, ax = plt.subplots(figsize=(7, 5))
    for size in sizes:
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        times = [results[(size, p)][0] for p in valid_procs]
        ax.plot(valid_procs, times, marker='o', label=f'size={size}')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Running Time (s)')
    if (benchmark_bool):
        ax.set_title(f'Absolute Running Time (c_b)')
    else: 
        ax.set_title(f'Absolute Running Time (c_s)')
    
    ax.legend()
    ax.grid(True)
    ax.set_xticks(nprocs_list)
    save_plot(fig, f'benchmark_plots_{suffix}_runtime.png')

    # Relative Speed-up
    fig, ax = plt.subplots(figsize=(7, 5))
    for size in sizes:
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        speedups = [results[(size, p)][1] for p in valid_procs]
        ax.plot(valid_procs, speedups, marker='o', label=f'size={size}')
    ax.plot(nprocs_list, nprocs_list, 'k--', label='Ideal Speed-up')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Relative Speed-up')
    if (benchmark_bool):
        ax.set_title(f'Relative Speed-up (c_b)')
    else: 
        ax.set_title(f'Relative Speed-up (c_s)')

    ax.legend()
    ax.grid(True)
    ax.set_xticks(nprocs_list)
    
    save_plot(fig, f'benchmark_plots_{suffix}_speedup.png')

    # Parallel Efficiency
    fig, ax = plt.subplots(figsize=(7, 5))
    for size in sizes:
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        efficiencies = [results[(size, p)][2] for p in valid_procs]
        ax.plot(valid_procs, efficiencies, marker='o', label=f'size={size}')
    ax.axhline(y=1.0, color='k', linestyle='--', label='Ideal Efficiency')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Parallel Efficiency')
    if (benchmark_bool):
        ax.set_title(f'Parallel Efficiency (c_b)')
    else: 
        ax.set_title(f'Parallel Efficiency (c_s)')

    ax.legend()
    ax.grid(True)
    ax.set_xticks(nprocs_list)
    
    save_plot(fig, f'benchmark_plots_{suffix}_efficiency.png')


def process_dat_file(dat_file):
    """Parse a .dat file, compute metrics, save CSV, print table, and generate plots."""
    means = parse_calc_means(dat_file)
    if means is None:
        return

    found_sizes = sorted(set(s for s, p in means.keys()))
    found_nprocs = sorted(set(p for s, p in means.keys()))

    results = calculate_metrics(means, found_sizes, found_nprocs)

    basename = os.path.splitext(os.path.basename(dat_file))[0]
    suffix = basename.replace("output_", "")
    csv_file = f"results_{suffix}.csv"
    plot_file_suffix = suffix

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
            process_dat_file(dat_file)
            print()

