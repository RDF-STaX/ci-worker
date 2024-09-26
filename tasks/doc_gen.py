from pathlib import Path
import re
import sys

from bs4 import BeautifulSoup
import pylode

FORMATS = [
    ('ttl', 'Turtle'),
    ('nt', 'N-Triples'),
    ('jsonld', 'JSON-LD'),
    ('rdf', 'RDF/XML'),
    ('jelly', 'Jelly'),
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

    # Remove the erroneous download link
    html = re.sub(r'<dt>Ontology RDF.*?</dd>', '', html, flags=re.DOTALL)

    # Remove H1
    html = re.sub(r'<h1.*?</h1>', '', html, flags=re.DOTALL)

    # Remove the favicon of pyLODE
    html = re.sub(r'<link rel="icon".+?>', '', html, flags=re.DOTALL)

    # Fix anchor links to match entity names in the ontology
    # Issue: https://github.com/RDF-STaX/rdf-stax.github.io/issues/55
    soup = BeautifulSoup(html, 'html.parser')
    for div_tag in soup.find_all('div', class_='entity'):
        code_tags = div_tag.find_all('code')
        if len(code_tags) == 0:
            continue
        uri = code_tags[0].text.strip()
        if not uri.startswith('https://w3id.org/stax/ontology#'):
            continue
        name = uri.split('#')[1]
        old_id = div_tag['id']
        div_tag['id'] = name
        for anchor_link in soup.find_all('a', href='#' + old_id):
            anchor_link['href'] = '#' + name

    # Save
    with open(output_file, 'w') as f:
        f.write(soup.prettify())

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
