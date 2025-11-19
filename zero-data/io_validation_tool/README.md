# IO List validation tool

## How to run 
There are two folders that will be mounted in the docker container:
- io_lists: This folder should contain the IO list files to be validated. It is possible to add more io lists to this folder, and they will be validated as well.
- notebooks: This folder will contain the validation Jupyter notebooks.

To run the tool, execute the following commands:
```bash
cd io_validation_tool
docker compose up -d
```
After that, navigate to `http://localhost:8888` in your web browser to access the Jupyter notebooks. Find and open the validate_io_lists.ipynb notebook in the file browser on the left panel.
Running it should validate all the IO lists present in the io_lists folder. Each validation check will display validation results as output.

## UV
This part of the project uses [UV as a package & project manager](https://docs.astral.sh/uv).
To run the project locally without docker, install uv and run:

```bash
uv run jupyter notebook
```

This will start a Jupyter notebook server and automatically open the notebook in your default web browser.

To add a new dependency to the project, use:

```bash
uv add <package-name>
```
