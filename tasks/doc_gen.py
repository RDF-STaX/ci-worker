from pathlib import Path
import re
import sys

import pylode

FORMATS = [
    ('ttl', 'Turtle'),
    ('nt', 'N-Triples'),
    ('jsonld', 'JSON-LD'),
    ('rdf', 'RDF/XML'),
]
BASE_LINK = 'https://w3id.org/stax'


def main():
    if len(sys.argv) != 4:
        print('Generates documentation for the ontology\n'
              'Args:\n'
              '- input .ttl file\n'
              '- output dir\n'
              '- version tag for the ontology\n')
        exit(1)

    input_file = sys.argv[1]
    output_dir = Path(sys.argv[2])
    output_file = output_dir / 'docs.html'
    version_tag = sys.argv[3]
    if re.match(r'^v\d+\.\d+\.', version_tag):
        # strip "v" from the start of the version tag
        version_tag = version_tag[1:]

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
    img = f'<img src="/{version_tag}/assets/ontology.png" alt="Ontology diagram" >'
    html = re.sub(r'<div.*?Pictures.*?</div>', img, html)
    # Save
    with open(output_file, 'w') as f:
        f.write(html)

    print('Writing download links...')
    with open(output_dir / 'links.md', 'w') as f:
        f.write('!!! info\n\n')
        f.write('    Download the ontology in RDF: ')
        for (ext, fmt) in FORMATS:
            f.write(f'**[{fmt}]({BASE_LINK}/{version_tag}/ontology.{ext})**')
            if ext != 'rdf':
                f.write(', ')
        f.write('.\n')


if __name__ == '__main__':
    main()
