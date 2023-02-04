import logging

# Base class for the aiosqlite database object.
from dls_normsql.aiosqlite import Aiosqlite as NormsqlAiosqlite

# Base class for our database definition.
from echolocator_lib.databases.database_definition import DatabaseDefinition

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class Aiosqlite(DatabaseDefinition, NormsqlAiosqlite):
    """
    Class with coroutines for creating and querying a sqlite database.
    We use dls-normsql to do the heavy lifting.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        """
        Construct object.  Do not connect to database.
        """

        # Constructor for the database definition.
        DatabaseDefinition.__init__(self)

        # Constructor for the database implementation.
        NormsqlAiosqlite.__init__(self, specification)

    # ----------------------------------------------------------------------------------------
    def reinstance(self):
        """
        Clone database instance.
        This is needed if a process inherits an instance, but needs its own connection.
        """

        return Aiosqlite(self.__filename)

    # ----------------------------------------------------------------------------------------
    async def add_table_definitions(self):
        """
        Make all the table definitions.
        """

        # Add tables common in all implementations.
        await NormsqlAiosqlite.add_table_definitions(self)

        # Add tables from our definition.
        await DatabaseDefinition.add_table_definitions(self)
