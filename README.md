# ci-worker

CI worker for processing the RDF Stream Taxonomy (RDF-STaX).

## Usage

Use the provided Docker image. In the container you can invoke the commands:

```bash
$ python /app/tasks/package.py <input dir> <output dir> <version tag>
$ python /app/tasks/doc_gen.py <input file> <output dir>
$ java -jar /app/robot.jar <command>
```

## Contributing

Please see **[the main repository of RDF-STaX](https://github.com/RDF-STaX/rdf-stax.github.io)** and its [issue tracker](https://github.com/RDF-STaX/rdf-stax.github.io/issues) for more information.

## License

This work is licensed under the Apache License, Version 2.0. See `LICENSE` for details.
