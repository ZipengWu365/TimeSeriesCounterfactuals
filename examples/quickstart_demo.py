from pprint import pprint

from tscfbench import run_demo


if __name__ == "__main__":
    result = run_demo("city-traffic", output_dir="tscfbench_quickstart_demo")
    pprint(result["summary"])
