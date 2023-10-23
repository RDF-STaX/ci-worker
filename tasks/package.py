from datetime import datetime, timezone
from pathlib import Path
import re
import os
import subprocess
import sys

from rdflib import Graph, Namespace, Literal, DCTERMS, OWL, RDF, RDFS, SKOS, XSD, URIRef

STAX_PREFIX = 'https://w3id.org/stax/ontology#'
STAX_MAIN = 'https://w3id.org/stax/ontology'
STAX = Namespace(STAX_PREFIX)
SCHEMA = Namespace('http://schema.org/')


def main():
    if len(sys.argv) != 4:
        print('Packages the ontology\n'
              'Args:\n'
              '- input dir (src directory in the repo)\n'
              '- output dir\n'
              '- version tag for the ontology\n'
              '  The version tag can start with "v" – it will be stripped automatically.'
              )
        exit(1)

    parent_dir = Path(__file__).parent.parent
    temp_dir = parent_dir / 'temp'
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    version = sys.argv[3]
    if re.match(r'^v\d+\.\d+\.', version):
        # strip "v" from the start of the version tag
        version = version[1:]

    print('Preparing environment...')
    try:
        os.mkdir(temp_dir)
    except FileExistsError:
        pass

    print('Running inference...')
    subprocess.run([
        'java', '-jar', str(parent_dir / 'robot.jar'),
        'reason', '--input', input_dir / 'stax.ttl', '--reasoner', 'HermiT',
        '--axiom-generators', 'SubClass EquivalentClass DisjointClasses ClassAssertion PropertyAssertion '
                              'EquivalentObjectProperty InverseObjectProperties ObjectPropertyCharacteristic '
                              'SubObjectProperty ObjectPropertyRange ObjectPropertyDomain',
        '--include-indirect', 'true',
        '--output', temp_dir / 'inferred.ttl'
    ])

    print('Merging...')
    g_inf = Graph()
    g_inf.parse(temp_dir / 'inferred.ttl', format='turtle')
    g = Graph()
    g.parse(input_dir / 'stax.ttl', format='turtle')
    original_size = len(g)
    g.parse(input_dir / 'authors.ttl', format='turtle')
    print(f'Added {len(g) - original_size} triples about authors')
    original_size = len(g)

    for s, p, o in g_inf:
        if (s, p, o) in g:
            continue
        if p == RDF.type and str(s).startswith(STAX_PREFIX) and str(o).endswith('Concept'):
            # print(f'Adding inferred class {s} {p} {o}')
            g.add((s, p, o))
        elif p in [RDFS.domain, RDFS.range] and str(s).startswith(STAX_PREFIX):
            # print(f'Adding inferred property {s} {p} {o}')
            g.add((s, p, o))
        elif p in [SKOS.narrower, STAX.canBeFlattenedInto, STAX.canBeGroupedInto, STAX.hasElementType]:
            # print(f'Adding inferred property {s} {p} {o}')
            g.add((s, p, o))

    print(f'Added {len(g) - original_size} inferred triples')

    print('Adding version...')
    g.add((URIRef(STAX_MAIN), OWL.versionInfo, Literal(version)))
    g.add((URIRef(STAX_MAIN), OWL.versionIRI, URIRef(f'{STAX_MAIN}/{version}')))
    now_iso = datetime.now(timezone.utc).isoformat()[:19]
    g.add((URIRef(STAX_MAIN), DCTERMS.issued, Literal(now_iso, datatype=XSD.dateTime)))
    g.namespace_manager.bind('stax_ont', None, replace=True)
    g.namespace_manager.bind('schema', SCHEMA, replace=True)

    print('Serializing...')
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    g.serialize(destination=output_dir / 'stax.ttl', format='turtle', encoding='utf-8')
    g.serialize(destination=output_dir / 'stax.rdf', format='xml', encoding='utf-8')
    g.serialize(destination=output_dir / 'stax.jsonld', format='json-ld', encoding='utf-8')
    g.serialize(destination=output_dir / 'stax.nt', format='nt', encoding='utf-8')


if __name__ == '__main__':
    main()
