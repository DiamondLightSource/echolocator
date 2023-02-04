import copy
import logging

from dls_utilpack.require import require

from echolocator_api.databases.constants import ImageFieldnames, Tablenames

# Base class for generic things.
from echolocator_api.thing import Thing

# Database manager.
from echolocator_lib.databases.databases import Databases

logger = logging.getLogger(__name__)

thing_type = "echolocator_lib.echolocator_datafaces.aiosqlite"


class Aiosqlite(Thing):
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

        self.__database = None

    # ----------------------------------------------------------------------------------------
    async def start(self):
        # Connect to the database to create the schemas if they don't exist already.
        await self.establish_database_connection()

    # ----------------------------------------------------------------------------------------
    async def disconnect(self):
        if self.__database is not None:
            await self.__database.disconnect()
            self.__database = None

    # ----------------------------------------------------------------------------------------
    async def establish_database_connection(self):

        if self.__database is None:
            self.__database = Databases().build_object(self.specification()["database"])
            await self.__database.connect()

    # ----------------------------------------------------------------------------------------
    async def reinstance(self):
        """"""
        if self.__database is None:
            return

        self.__database = self.__database.reinstance()

    # ----------------------------------------------------------------------------------------
    async def backup(self):
        """"""
        await self.establish_database_connection()

        return await self.__database.backup()

    # ----------------------------------------------------------------------------------------
    async def restore(self, nth):
        """"""
        await self.establish_database_connection()

        return await self.__database.restore(nth)

    # ----------------------------------------------------------------------------------------
    async def query(self, sql, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        records = await self.__database.query(sql, subs=subs, why=why)

        return records

    # ----------------------------------------------------------------------------------------
    async def execute(self, sql, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        return await self.__database.execute(sql, subs=subs, why=why)

    # ----------------------------------------------------------------------------------------
    async def insert(self, table_name, records, why=None):
        """"""
        await self.establish_database_connection()

        return await self.__database.insert(table_name, records, why=why)

    # ----------------------------------------------------------------------------------------
    async def update(self, table_name, record, where, subs=None, why=None):
        """"""
        await self.establish_database_connection()

        if why is None:
            why = f"update {table_name} record"

        # This returns the count of records changed by the update.
        return {
            "count": await self.__database.update(
                table_name, record, where, subs=subs, why=why
            )
        }

    # ----------------------------------------------------------------------------------------
    async def update_image(self, record, why=None):
        """
        Caller provides the image record with the fields to be updated.
        The filename field is used to uniquely select the database record.
        """

        table_name = Tablenames.ROCKMAKER_IMAGES

        filename = require("image record", record, ImageFieldnames.FILENAME)
        record = copy.deepcopy(record)
        record.pop(ImageFieldnames.FILENAME)

        result = await self.update(
            table_name,
            record,
            f"({ImageFieldnames.FILENAME} REGEXP ?)",
            subs=[f"{filename}$"],
            why=why,
        )

        return result

    # ----------------------------------------------------------------------------------------
    async def report_health(self):
        """"""

        report = {}

        report["alive"] = True

        return report
