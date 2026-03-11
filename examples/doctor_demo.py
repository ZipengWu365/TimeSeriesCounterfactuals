from tscfbench.onramp import doctor_report

if __name__ == '__main__':
    import json
    print(json.dumps(doctor_report(), indent=2))
