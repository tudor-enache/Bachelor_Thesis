import subprocess
import random
import time
import argparse

def run_command():
    subprocess.run("curl -v 10.10.3.3/file", shell=True)

def exponential(mean):
    return random.expovariate(1 / mean)

def lognormal(mean, sigma):
    return random.lognormvariate(mean, sigma)

def run_command_with_distribution(distribution, params):
    start_time = time.time()
    while time.time() - start_time < 30:
        wait_time = distribution(*params)
        time.sleep(wait_time)
        run_command()

def main():
    parser = argparse.ArgumentParser(description="Run a CLI command with a specified distribution within a 30-second time window.")
    parser.add_argument("distribution", type=str, choices=["exponential", "pareto", "lognormal"], help="Distribution type")
    parser.add_argument("--mean", type=float, help="Mean for exponential or lognormal distribution")
    parser.add_argument("--alpha", type=float, help="Alpha for Pareto distribution")
    parser.add_argument("--sigma", type=float, help="Sigma for lognormal distribution")
    args = parser.parse_args()

    if args.distribution == "exponential":
        if args.mean is None:
            print("Mean must be provided for exponential distribution.")
            return
        run_command_with_distribution(exponential, (args.mean,))
    elif args.distribution == "lognormal":
        if args.mean is None or args.sigma is None:
            print("Mean and sigma must be provided for lognormal distribution.")
            return
        run_command_with_distribution(lognormal, (args.mean, args.sigma))

if __name__ == "__main__":
    main() 
