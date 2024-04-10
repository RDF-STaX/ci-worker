import yaml
from pathlib import Path
from rdflib import Graph

import json
import sys


def main():
    if len(sys.argv) != 3:
        print('Runs the competency question tests\n'
              'Args:\n'
              '- in_file: input RDF file\n'
              '- test_dir: directory containing the test files')
        sys.exit(1)

    in_file = Path(sys.argv[1])
    test_dir = Path(sys.argv[2])

    g = Graph()
    g.parse(in_file, format="turtle")

    test_results = []

    for uc_dir in sorted(test_dir.iterdir()):
        if not uc_dir.is_dir():
            continue
        for test_file in sorted(uc_dir.iterdir()):
            if not test_file.is_file() or test_file.suffix != '.yaml':
                continue
            test_results.append(run_test(test_file, g))

    print(f'Ran {len(test_results)} competency question tests')
    print(f'{sum(test_results)} successful, {len(test_results) - sum(test_results)} failed')

    if sum(test_results) != len(test_results):
        sys.exit(1)


def run_test(test_file: Path, g: Graph) -> bool:
    with open(test_file, "r") as f:
        test = yaml.safe_load(f)

    with open(test_file.with_suffix('.rq'), 'r') as f:
        query = f.read()

    print(f"***** Running use case {test['useCase']} test {test['testNumber']} *****")
    print(f"  Question: {test['text']}")
    print(f"  Expectation: {test['expectation']}")

    results = len(g.query(query))
    print(f"  Got {results} result(s)")

    success = False
    if test['expectation'] == 'empty':
        success = results == 0
    elif test['expectation'] == 'nonEmpty':
        success = results > 0
    elif test['expectation']['resultsCount'] == results:
        success = True

    if success:
        print("***** PASSED *****")
    else:
        print("***** FAILED *****")

    print()
    return success


if __name__ == '__main__':
    main()
