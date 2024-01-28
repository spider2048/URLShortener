import base64
import hashlib
import logging
import datetime
from typing import List, Optional, Union, Dict
from urllib.parse import ParseResult, quote, unquote, urlparse

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from constants import *
from models import Base, URLRefs, URLTable, URLStats

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("URLShortener")


class ShortURLManager:
    def __init__(self, database: str) -> None:
        self.engine = self._setup_database(database)
        self.session = sessionmaker(bind=self.engine)()

    def _add_hash(self, hash: str, url: str) -> None:
        logger.info("Adding hash %s - %s", hash, url)
        self.session.add(URLTable(hash=hash, url=url))
        self.session.commit()

    def _increase_count(self, hash: str) -> None:
        logger.info("Increasing click count for hash: %s", hash)
        self.session.query(URLStats).filter(URLStats.hash == hash) \
                                    .update({'times': URLStats.times + 1})
        self.session.commit()


    def get_url(self, hash: str) -> Union[str, bool]:
        logger.info("Getting from hash %s", hash)
        query: Optional[URLTable | None] = (
            self.session.query(URLTable).filter(URLTable.hash == hash).first()
        )
        if query:
            return str(query.url)
        return False

    def _get_hash(self, url: str) -> Union[str, bool]:
        query = self.session.query(URLTable).filter(URLTable.url == url).first()
        if query:
            return str(query.hash)
        return False

    def _setup_database(self, path: str) -> Engine:
        engine: Engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(bind=engine)
        return engine

    def _validate_url(self, url: str) -> None:
        parse_result: ParseResult = urlparse(url)
        assert parse_result.scheme, "The scheme of the URL cannot be null"
        assert parse_result.netloc, "The location of the URL cannot be null"

    def shorten(self, url: str) -> str:
        # Validate & Encode URL
        self._validate_url(url)
        url = quote(url, safe="")

        # Check for duplicates
        res: Optional[str | bool] = self._get_hash(url)
        if isinstance(res, str):
            return res

        # Hash the URL
        by: List[int] = [PRINTABLE.index(ch) for ch in url]
        for times in range(MAX_TIMES):
            prepend: bytes = SALT * times
            digest: bytes = hashlib.sha256(prepend + bytearray(by)).digest()
            hash: str = base64.urlsafe_b64encode(digest).decode()[:MIN_BYTES]
            if self.get_url(hash) is False:
                self._add_hash(hash, url)
                return hash

            times += 1
            logger.error("collission %s %s (times: %d)", hash, url, times)

        logger.error("Failed to add %s", url)
        raise Exception(f'Failed to add "{url}"')

    def get_hash_count(self, hash) -> int:
        logger.info("Getting count for hash: %s", hash)
        result = self.session.query(URLStats) \
                           .filter(URLStats.hash == hash) \
                           .first()
        if result:
            return result.times
        return 0

    def get_hash_stats(self, hash) -> List[Dict]:
        logger.info("Getting all statistics from hash: %s", hash)
        stats = []

        for q in reversed(self.session.query(URLRefs).filter(URLRefs.hash == hash).all()):
            stats.append(dict(
                hash=str(q.hash), 
                referer=str(q.referer),
                ip=str(q.ip),
                time=str(q.time)
            ))
        return stats

    def add_stats(self, hash: str, referer: str, ip: str, time: str):
        # Add ref stats (per click)
        logger.info('Adding referer:%s to hash:%s from ip:%s', referer, hash, ip)
        self.session.add(URLRefs(hash=hash, referer=referer, ip=ip, time=time))
        self.session.commit()

        # Add click stats
        self._increase_count(hash)

    def unshorten(self, hash: str) -> Optional[str]:
        result = self.get_url(hash)
        if isinstance(result, str):
            return unquote(result)
        else:
            logger.error("hash `%s` doesn't exist", hash)
            return None
