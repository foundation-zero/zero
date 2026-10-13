from thrs.graphql.strawberry import create_app
from thrs.orchestration.config import Config

app = create_app(Config())  # type: ignore
