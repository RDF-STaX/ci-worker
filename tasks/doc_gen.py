from pathlib import Path
import re
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
    output_file = output_dir / 'docs.html'

    print('Generating documentation...')
    pylode.MakeDocco(
        input_data_file=input_file,
        outputformat='html',
        profile='ontdoc',
    ).document(str(output_file))

    print('Post-processing...')
    with open(output_file, 'r') as f:
        html = f.read()
    # Replace the <style> tag with new content
    with open(Path(__file__).parent / 'res' / 'pylode.css', 'r') as f:
        css = f.read()
    html = re.sub(r'<style>.*</style>', f'<style>{css}</style>', html, flags=re.DOTALL)
    # Save
    with open(output_file, 'w') as f:
        f.write(html)


if __name__ == '__main__':
    main()
