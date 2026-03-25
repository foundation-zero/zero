import logging
from operator import ge
from pathlib import Path

from zero_data.config import io_lists
from zero_data.io_list import read_io_list, Source
from zero_data.vector_gen.marpower import MarpowerVectorGenerator

logger = logging.getLogger(__name__)

_GENERATORS: dict[Source, type] = {
    "marpower": MarpowerVectorGenerator,
}


def generate_vector():
    """Generate vector resources for all IO lists."""
    vector_path = Path("../vector/")

    for source, file_names in io_lists:
        logger.debug(f"Processing {source} {file_names}")
        paths = [Path(f"io_lists/{file_name}") for file_name in file_names]
        io_result = read_io_list(paths, source)

        vector_generator_class = _GENERATORS.get(source, None)
        if vector_generator_class is None:
            logger.warning(f"No vector generator found for source: {source}")
            continue

        generator = vector_generator_class(vector_path)
        generator.generate(io_result.topics)

    logging.info("Vector generation complete")
