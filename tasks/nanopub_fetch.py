from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
import sys

from rdflib import Dataset
from nanopub import NanopubClient
import requests


BASE_LINK = 'https://w3id.org/stax'


def main():
    if len(sys.argv) != 4:
        print('Fetches RDF-STaX nanopubs and packages them\n'
              'Args:\n'
              '- nanopub cache directory\n'
              '- output dir\n'
              '- version tag for the ontology\n')
        exit(1)

    parent_dir = Path(__file__).parent.parent
    cache_dir = sys.argv[1]
    output_dir = sys.argv[2]
    version_tag = sys.argv[3]

    print('Fetching nanopubs...')
    client = NanopubClient()
    client.grlc_urls = [
        "http://grlc.nanopubs.lod.labs.vu.nl/api/local/local/",
        "http://130.60.24.146:7881/api/local/local/",
        # Doesn't seem to work
        # "https://openphacts.cs.man.ac.uk/nanopub/grlc/api/local/local/",
        "http://grlc.np.dumontierlab.com/api/local/local/"
    ]
    results = client.find_nanopubs_with_pattern(
        pred='http://purl.org/nanopub/x/hasNanopubType',
        obj='https://w3id.org/stax/ontology#RdfStreamTypeUsage',
    )
    source_files = []
    for r in results:
        h = hashlib.md5(r['np'].encode()).hexdigest()
        source_file = h + '.trig'
        source_files.append(source_file)
        cache_path = Path(cache_dir, source_file)
        if not cache_path.exists() or cache_path.stat().st_size == 0:
            print(f'Fetching {r["np"]}...')
            rq = requests.get(
                r['np'],
                allow_redirects=True,
                headers={'Accept': 'application/trig'},
            )
            rq.raise_for_status()
            with open(cache_path, 'wb') as f:
                f.write(rq.content)

    # Delete files that are no longer needed
    print('Deleting cached files that are no longer needed...')
    for f in Path(cache_dir).glob('*'):
        if f.name not in source_files:
            print(f'Deleting {f.name}...')
            f.unlink()

    # Package
    print(f'Packaging {len(source_files)} nanopubs...')
    d = Dataset()
    for source_file in source_files:
        d.parse(Path(cache_dir, source_file), format='trig')
    d.serialize(Path(output_dir, 'nanopubs.trig'), format='trig')
    d.serialize(Path(output_dir, 'nanopubs.nq'), format='nquads')
    d.serialize(Path(output_dir, 'nanopubs.jelly'), format='jelly')

    print(f'Writing download links...')
    short_version_tag = version_tag[1:] if version_tag.startswith('v') else version_tag
    with open(Path(output_dir, 'nanopub_links.md'), 'w') as f:
        f.write('!!! info\n\n')
        f.write('    Download the RDF-STaX nanopublication dump in RDF: ')
        f.write(f'**[TriG]({BASE_LINK}/{short_version_tag}/nanopubs.trig)**')
        f.write(', ')
        f.write(f'**[N-Quads]({BASE_LINK}/{short_version_tag}/nanopubs.nq)**')
        f.write(', ')
        f.write(f'**[Jelly]({BASE_LINK}/{short_version_tag}/nanopubs.jelly)**')
        f.write('.<br>*[:material-help-circle: What is Jelly?](https://w3id.org/jelly)*\n\n')
        f.write(f'    The dump includes {len(source_files)} nanopublications. ')
        f.write(f'Created at: {datetime.now(timezone.utc).isoformat()[:19]} UTC.\n')


if __name__ == '__main__':
    main()
