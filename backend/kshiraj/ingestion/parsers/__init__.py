"""
kshiraj/ingestion/parsers/__init__.py

Portal-specific parsers for Indian Government websites and document formats.
"""

from kshiraj.ingestion.parsers.base_parser import BasePortalParser
from kshiraj.ingestion.parsers.bis_parser import BisPortalParser
from kshiraj.ingestion.parsers.cppp_parser import CpppPortalParser
from kshiraj.ingestion.parsers.dpiit_parser import DpiitPortalParser
from kshiraj.ingestion.parsers.egazette_parser import EgazettePortalParser

__all__ = [
    "BasePortalParser",
    "BisPortalParser",
    "CpppPortalParser",
    "DpiitPortalParser",
    "EgazettePortalParser",
]
