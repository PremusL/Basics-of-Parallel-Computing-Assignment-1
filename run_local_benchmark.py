import os
import subprocess

NPROCS = [1, 2, 4, 8, 16, 24, 32]
SIZES = [120, 1030]
PATCH = 24
NREP = 3

def run_experiment(out_file, benchmark):
    with open(out_file, "w") as f:
        f.write("")
        
    for nprocs in NPROCS:
        for size in SIZES:
            for r in range(NREP):
                cmd = ["python3", "julia_par.py", "--nprocs", str(nprocs), "--size", str(size), "--patch", str(PATCH)]
                if benchmark:
                    cmd.append("--benchmark")
                
                print(f"Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                with open(out_file, "a") as f:
                    f.write(result.stdout)

if __name__ == "__main__":
    print("Running cb benchmarks...")
    run_experiment("output_exp22_1.dat", True)
    print("Running cs benchmarks...")
    run_experiment("output_exp22_2.dat", False)
