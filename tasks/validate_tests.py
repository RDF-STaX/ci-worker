from jsonschema import validate
import yaml
from pathlib import Path

import json
import sys


def main():
    if len(sys.argv) != 3:
        print('Validates the competency question test files\n'
              'Args:\n'
              '- test_dir: directory containing the test files\n'
              '- schema_path: path to the JSON Schema of the tests')
        sys.exit(1)

    test_dir = Path(sys.argv[1])
    schema_path = Path(sys.argv[2])

    # load the JSON Schema
    with open(schema_path, 'r') as f:
        schema = json.load(f)

    validation_results = []

    # check all files in direct subdirectories of test_dir
    for uc_dir in test_dir.iterdir():
        if not uc_dir.is_dir():
            continue
        for test_file in uc_dir.iterdir():
            if not test_file.is_file() or test_file.suffix != '.yaml':
                continue
            validation_results.append(validate_test(test_file, schema))

    print(f'Checked {len(validation_results)} test files')
    print(f'{sum(validation_results)} valid, {len(validation_results) - sum(validation_results)} invalid')


def validate_test(test_file: Path, schema: dict) -> bool:
    with open(test_file, 'r') as f:
        test = yaml.safe_load(f)

    # check if the test file is valid
    try:
        validate(test, schema)
    except Exception as e:
        print(f'ERROR: Test file {test_file} is not valid: {e}')
        return False

    # check if the query file exists
    query_file = test_file.with_suffix('.rq')
    if not query_file.is_file():
        print(f'ERROR: Query file {query_file} not found')
        return False

    return True


if __name__ == '__main__':
    main()
