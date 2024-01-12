import hashlib
import base64
from typing import Optional
from urllib.parse import quote, unquote, urlparse
import logging

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker

from constants import *
from models import Base, URLTable

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("URLShortener")


class ShortURLManager:
    def __init__(self, database) -> None:
        self.engine = self._setup_database(database)
        self.session = sessionmaker(bind=self.engine)()

    def _add_hash(self, hash: str, url: str) -> None:
        logger.info("Adding hash %s - %s", hash, url)
        self.session.add(URLTable(hash=hash, url=url))
        self.session.commit()

    def _get_url(self, hash: str) -> Optional[str | bool]:
        logger.info("Getting from hash %s", hash)
        query = self.session.query(URLTable).filter(URLTable.hash == hash).first()
        if query:
            return str(query.url)
        return False

    def _get_hash(self, url: str):
        query = self.session.query(URLTable).filter(URLTable.url == url).first()
        if query:
            return str(query.hash)
        return False

    def _check_url_exists(self, url: str) -> Optional[str | bool]:
        result = self._get_hash(url)
        if isinstance(result, str):
            return result
        return False

    def _setup_database(self, path) -> Engine:
        engine = create_engine(f"sqlite:///{path}")
        Base.metadata.create_all(bind=engine)
        return engine

    def _validate_url(self, url: str) -> Optional[None | str]:
        try:
            parse_result = urlparse(url)
            assert parse_result.scheme, "The scheme of the URL cannot be null"
            assert parse_result.netloc, "The location of the URL cannot be null"
        except Exception as err:
            return f"Failed to validate URL with: {err}"

    def shorten(self, url: str):
        # Validate URL
        err = self._validate_url(url)
        if isinstance(err, str):
            raise Exception(err)

        url = quote(url, safe="")

        # Check for duplicates
        res = self._check_url_exists(url)
        if isinstance(res, str):
            return res

        # Hash the URL
        by = [PRINTABLE.index(ch) for ch in url]
        for times in range(MAX_TIMES):
            prepend = SALT * times
            digest = hashlib.sha256(prepend + bytearray(by)).digest()
            hash = base64.urlsafe_b64encode(digest).decode()[:MIN_BYTES]
            if self._get_url(hash) is False:
                self._add_hash(hash, url)
                return hash

            times += 1
            logger.error("collission %s %s (times: %d)", hash, url, times)

        logger.error("Failed to add %s", url)
        raise Exception(f'Failed to add "{url}"')

    def unshorten(self, hash: str) -> Optional[str | None]:
        result = self._get_url(hash)
        if isinstance(result, str):
            return unquote(result)
        else:
            logger.error("hash `%s` doesn't exist", hash)
