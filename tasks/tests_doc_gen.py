import yaml
from pathlib import Path

import sys
import textwrap


def main():
    if len(sys.argv) != 4:
        print('Generates the docs for competency question tests\n'
              'Args:\n'
              '- test_dir: directory containing the test files\n'
              '- output_path: the file to write the docs to (will be truncated)\n'
              '- ref: branch or tag name')
        sys.exit(1)

    test_dir = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    ref = sys.argv[3]

    out_f = open(output_path, 'wt')

    # check all files in direct subdirectories of test_dir
    for uc_dir in sorted(test_dir.iterdir()):
        if not uc_dir.is_dir():
            continue
        write_use_case(uc_dir, out_f)

        for test_file in sorted(uc_dir.iterdir()):
            if not test_file.is_file() or test_file.suffix != '.yaml':
                continue
            write_test(test_file, out_f, ref)

    print('Done.')


def write_use_case(uc_dir, out_file):
    uc_num = uc_dir.stem.replace('uc', '')
    print(f'Generating use case {uc_num}')
    out_file.write(f'## Use case {uc_num}\n\n')
    with open(uc_dir / 'index.md', 'r') as f:
        out_file.write(f.read())
    out_file.write('\n')


def write_test(test_file, out_file, ref):
    with open(test_file, 'r') as f:
        test = yaml.safe_load(f)

    with open(test_file.with_suffix('.rq'), 'r') as f:
        query = f.read()

    def_link = f"https://github.com/RDF-STaX/rdf-stax.github.io/blob/{ref}/tests/uc{test['useCase']}/{test_file.name}"
    out_file.write(f"### Test CQ{test['useCase']}.{test['testNumber']} ([definition]({def_link}))\n\n")
    out_file.write(f"**Question:** {test['text']}\n\n")
    out_file.write(f"**Expectation:** ")
    if test['expectation'] == 'nonEmpty':
        out_file.write('query results are not empty')
    elif test['expectation'] == 'empty':
        out_file.write('query results are empty')
    else:
        c = test['expectation']['resultsCount']
        if c == 1:
            out_file.write(f'there is 1 query result')
        else:
            out_file.write(f'there are {c} query results')

    out_file.write('\n\n??? example "SPARQL query of the test"\n\n')
    out_file.write('    ```sparql\n')
    out_file.write(textwrap.indent(query.strip(), 4 * ' '))
    out_file.write('\n    ```\n\n')


if __name__ == '__main__':
    main()
