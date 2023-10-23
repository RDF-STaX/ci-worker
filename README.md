# ci-worker

CI worker for processing the RDF Stream Taxonomy (RDF-STaX).

## Usage

Use the provided Docker image. In the container you can invoke the commands:

```bash
$ python tasks/package.py <input dir> <output dir> <version tag>
$ python tasks/doc_gen.py <input file> <output dir>
$ java -jar robot.jar <command>
```

## License

This work is licensed under the Apache License, Version 2.0. See `LICENSE` for details.
