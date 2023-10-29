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
    ], check=True)

    g = Graph()
    g.parse(input_dir / 'stax.ttl', format='turtle')
    original_size = len(g)

    print('Adding version...')
    g.add((URIRef(STAX_MAIN), OWL.versionInfo, Literal(version)))
    g.add((URIRef(STAX_MAIN), OWL.versionIRI, URIRef(STAX_MAIN.replace('ontology', version + '/ontology'))))
    now_iso = datetime.now(timezone.utc).isoformat()[:19]
    g.add((URIRef(STAX_MAIN), DCTERMS.modified, Literal(now_iso, datatype=XSD.dateTime)))
    # Add the type of the dcterms:modified property (required in OWL 2 DL)
    g.add((URIRef(DCTERMS.modified), RDF.type, OWL.AnnotationProperty))
    g.namespace_manager.bind('stax_ont', None, replace=True)
    g.namespace_manager.bind('schema', SCHEMA, replace=True)

    print('Serializing the OWL 2 DL ontology...')
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        pass
    serialize(g, output_dir, 'dl')

    print("Validating the OWL 2 DL ontology's profile...")
    # We have changed the ontology, so let's revalidate it, just in case
    subprocess.run([
        'java', '-jar', str(parent_dir / 'robot.jar'),
        'validate-profile', '--input', output_dir / 'dl.ttl', '--profile', 'DL',
        '--output', temp_dir / 'dl_validation.txt'
    ], check=True)

    print('Merging...')
    g_inf = Graph()
    g_inf.parse(temp_dir / 'inferred.ttl', format='turtle')

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
    original_size = len(g)

    g.parse(input_dir / 'authors.ttl', format='turtle')
    print(f'Added {len(g) - original_size} triples about authors')
    original_size = len(g)

    g.parse(input_dir / 'alignments.ttl', format='turtle')
    print(f'Added {len(g) - original_size} triples about alignments')

    print('Serializing the merged ontology...')
    serialize(g, output_dir, 'stax')


def serialize(g: Graph, output_dir: Path, filename: str):
    g.serialize(destination=output_dir / f'{filename}.ttl', format='turtle', encoding='utf-8')
    g.serialize(destination=output_dir / f'{filename}.rdf', format='xml', encoding='utf-8')
    g.serialize(destination=output_dir / f'{filename}.jsonld', format='json-ld', encoding='utf-8')
    g.serialize(destination=output_dir / f'{filename}.nt', format='nt', encoding='utf-8')


if __name__ == '__main__':
    main()
