from pathlib import Path
import sys

import pylode


def main():
    if len(sys.argv) != 3:
        print('Generates documentation for the ontology\n'
              'Args:\n'
              '- input .ttl file\n'
              '- output dir')
        exit(1)

    input_file = sys.argv[1]
    output_dir = Path(sys.argv[2])
    output_file = output_dir / 'index.html'

    pylode.MakeDocco(
        input_data_file=input_file,
        outputformat='html',
        profile='ontdoc',
    ).document(str(output_file))


if __name__ == '__main__':
    main()
