from tscfbench.demo_cases import run_demo

if __name__ == "__main__":
    payload = run_demo("detector-downtime", output_dir="demo_outputs", plot=True)
    print(payload["summary"])
