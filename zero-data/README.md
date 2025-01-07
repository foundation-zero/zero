# IO processing

This folder contains the scripts to process the IO lists supplied by various parties into the SQL
needed to process the values published by those parties.


## Commands
```bash
poetry install
```

```bash
poetry run datamodel-codegen --input-file-type jsonschema --input components.schema.json --output src/io_processing/generated_components.py --class-name Description
```

```bash
poetry run python -m io_processing --help
```