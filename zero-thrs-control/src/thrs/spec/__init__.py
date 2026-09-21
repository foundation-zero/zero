"""The published contract of the THRS control system: its AsyncAPI document
(``asyncapi``), the GraphQL side of it (``extension``, ``naming``) and the
API behaviour both sides implement (``contract``)."""

from thrs.spec.extension import build_thrs_spec

__all__ = ["build_thrs_spec"]
