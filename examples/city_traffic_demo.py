from pprint import pprint

from tscfbench import run_demo


if __name__ == "__main__":
    result = run_demo("city-traffic", output_dir="demo_outputs", plot=True)
    pprint(result["summary"])
    print(result["generated_files"]["report_md"])
