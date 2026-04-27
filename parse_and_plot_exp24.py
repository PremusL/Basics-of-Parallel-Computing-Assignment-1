import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import glob
import os
import csv

def parse_dat_file_24(filename):
    print(f"Parsing {filename}...")
    data = defaultdict(list)
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            if len(parts) == 4:
                size   = int(parts[0])
                patch  = int(parts[1])
                nprocs = int(parts[2])
                rtime  = float(parts[3])
                data[patch].append(rtime)

    means = {patch: np.mean(times) for patch, times in data.items()}
    return means

def print_table_24(means):
    print("\n### Exercise 2.4 - Finding the Best Patch Size")
    print("| size | p | patch | mean runtime (s) |")
    print("|---|---|---|---|")
    for patch, mean_time in sorted(means.items()):
        print(f"| 900 | 20 | {patch} | {mean_time:.4f} |")

def save_csv_24(means, filename):
    print(f"Saving to {filename}...")
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['size', 'p', 'patch', 'mean_runtime'])
        for patch, mean_time in sorted(means.items()):
            writer.writerow([900, 20, patch, f"{mean_time:.4f}"])

def plot_24(means):
    os.makedirs('./figs', exist_ok=True)
    patches = sorted(means.keys())
    times   = [means[p] for p in patches]

    # find best patch
    best_patch = min(means, key=means.get)
    best_time  = means[best_patch]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(patches, times, marker='o', color='steelblue')

    # highlight the best patch
    ax.axvline(x=best_patch, color='red', linestyle='--', label=f'Best patch={best_patch}')
    ax.annotate(f'min={best_time:.4f}s\npatch={best_patch}',
                xy=(best_patch, best_time),
                xytext=(best_patch + 1, best_time + 0.05),
                color='red')

    ax.set_xlabel('Patch Size')
    ax.set_ylabel('Mean Runtime (s)')
    ax.set_title('Finding the Best Patch Size (size=900, nprocs=20, cs)')
    ax.set_xticks(patches)
    ax.set_xticklabels(patches, rotation=45, ha='right')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.savefig('./figs/exp24_best_patch.png')
    plt.close(fig)
    print(f"Saved plot to ./figs/exp24_best_patch.png")
    print(f"Best patch size: {best_patch} with mean runtime {best_time:.4f}s")

if __name__ == "__main__":
    dat_files = sorted(glob.glob("output_exp24*.dat"))

    if not dat_files:
        print("No output_exp24*.dat files found.")
    else:
        for dat_file in dat_files:
            print(f"{'='*60}")
            means = parse_dat_file_24(dat_file)
            print_table_24(means)
            save_csv_24(means, "results_exp24.csv")
            plot_24(means)