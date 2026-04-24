import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import os

def parse_dat_file(filename):
    # data structure: dict of (size, nprocs) -> list of times
    data = defaultdict(list)
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return None

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
    
    # Calculate means
    means = {}
    for k, times in data.items():
        means[k] = np.mean(times)
    
    return means

def generate_table(means, sizes, nprocs_list, title):
    print(f"\n### {title}")
    print("| Size | Cores | Mean Runtime (s) | Speed-up | Parallel Efficiency |")
    print("|---|---|---|---|---|")
    
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
                print(f"| {size} | {p} | {tp:.4f} | {speedup:.2f} | {efficiency:.2f} |")
    
    return results

def plot_metrics(results, sizes, nprocs_list, suffix, c_type):
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Absolute Runtime
    ax = axes[0]
    for size in sizes:
        times = [results[(size, p)][0] for p in nprocs_list if (size, p) in results]
        valid_procs = [p for p in nprocs_list if (size, p) in results]
        ax.plot(valid_procs, times, marker='o', label=f'size={size}')
    ax.set_xlabel('Number of Cores')
    ax.set_ylabel('Running Time (s)')
    ax.set_title(f'Absolute Running Time ({c_type})')
    ax.legend()
    ax.grid(True)
    
    # Relative Speed-up
    ax = axes[1]
    for size in sizes:
        speedups = [results[(size, p)][1] for p in nprocs_list if (size, p) in results]
        valid_procs = [p for p in nprocs_list if (size, p) in results]
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
        efficiencies = [results[(size, p)][2] for p in nprocs_list if (size, p) in results]
        valid_procs = [p for p in nprocs_list if (size, p) in results]
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

if __name__ == "__main__":
    nprocs_list = [1, 2, 4, 8, 16, 24, 32]
    sizes = [120, 1030]
    
    means_cb = parse_dat_file("output_exp22_1.dat")
    if means_cb:
        res_cb = generate_table(means_cb, sizes, nprocs_list, "Table for c = c_b")
        plot_metrics(res_cb, sizes, nprocs_list, "cb", "c_b")
        
    means_cs = parse_dat_file("output_exp22_2.dat")
    if means_cs:
        res_cs = generate_table(means_cs, sizes, nprocs_list, "Table for c = c_s")
        plot_metrics(res_cs, sizes, nprocs_list, "cs", "c_s")
