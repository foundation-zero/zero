from itertools import groupby
import logging

from zero_data.io_list.types import IOTopic

logger = logging.getLogger(__name__)

def detect_same_format(
    topics: list[IOTopic],
) -> tuple[list[IOTopic], list[IOTopic], list[IOTopic]]:
    """Detect topics with the same format and group them into a wildcard."""
    nested_topics = [topic for topic in topics if len(topic.topic.split("/")) >= 3]
    unnested_topics = [topic for topic in topics if len(topic.topic.split("/")) < 3]

    def _nesting(topic: IOTopic):
        """Extract the nesting from the topic."""
        return topic.topic.split("/")[1:-1]

    sorted_topics = sorted(nested_topics, key=_nesting)
    grouped = groupby(sorted_topics, key=_nesting)
    squashed_topics = []
    unsquashed_topics: list[IOTopic] = []
    for nest, group in grouped:
        list_of_group = list(group)
        if len(list_of_group) > 1:
            # Check if all topics in the group have the same format
            if all(topic.fields == list_of_group[0].fields for topic in list_of_group):
                logger.info(f"Generating single table for nesting: {nest}")
                squashed_topics.append(
                    IOTopic(
                        topic="/".join(["marpower", *nest, "#"]),
                        fields=list_of_group[0].fields,
                    )
                )
            else:
                logger.warning(
                    f"Different formats found in nesting: {nest}, generating separate tables."
                )
                unsquashed_topics.extend(list_of_group)
        else:
            unsquashed_topics.append(list_of_group[0])
    return unnested_topics, squashed_topics, unsquashed_topics
