import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import glob
import os
import csv

def parse_dat_file_23(filename):
    print(f"Parsing {filename}...")
    data = defaultdict(list)
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if len(parts) == 4:
                size  = int(parts[0])
                patch = int(parts[1])
                nprocs = int(parts[2])
                rtime = float(parts[3])
                data[patch].append(rtime)
    
    means = {patch: np.mean(times) for patch, times in data.items()}
    return means

def print_table_23(means):
    print("\n### Exercise 2.3 - Influence of Patch Size")
    print("| size | p | patch | mean runtime (s) |")
    print("|---|---|---|---|")
    for patch, mean_time in sorted(means.items()):
        print(f"| 880 | 32 | {patch} | {mean_time:.4f} |")

def save_csv_23(means, filename):
    print(f"Saving to {filename}...")
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['size', 'p', 'patch', 'mean_runtime'])
        for patch, mean_time in sorted(means.items()):
            writer.writerow([880, 32, patch, f"{mean_time:.4f}"])

def plot_23(means):
    os.makedirs('./figs', exist_ok=True)
    patches = sorted(means.keys())
    times   = [means[p] for p in patches]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(patches, times, marker='o', color='steelblue')
    ax.set_xlabel('Patch Size')
    ax.set_ylabel('Mean Runtime (s)')
    ax.set_title('Influence of Patch Size (size=880, nprocs=32, cs)')
    ax.set_xticks(patches)
    ax.grid(True)
    plt.tight_layout()
    plt.savefig('./figs/exp23_patch_size.png')
    plt.close(fig)
    print("Saved plot to ./figs/exp23_patch_size.png")

if __name__ == "__main__":
    dat_files = sorted(glob.glob("output_exp23*.dat"))

    if not dat_files:
        print("No output_exp23*.dat files found.")
    else:
        for dat_file in dat_files:
            print(f"{'='*60}")
            means = parse_dat_file_23(dat_file)
            print_table_23(means)
            save_csv_23(means, f"results_exp23.csv")
            plot_23(means)