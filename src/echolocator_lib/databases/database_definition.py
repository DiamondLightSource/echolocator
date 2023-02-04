import logging

# Base class for all aiosqlite database objects.
from echolocator_lib.databases.table_definitions import RockmakerImagesTable

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class DatabaseDefinition:
    """
    Class which defines the database tables and revision migration path.
    Used in concert with the normsql class.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self):
        """
        Construct object.  Do not connect to database.
        """

        self.LATEST_REVISION = 2

    # ----------------------------------------------------------------------------------------
    async def apply_revision(self, revision):
        pass

        # from echolocator_api.databases.constants import Tablenames
        # from echolocator_api.databases.constants import ImageFieldnames
        # if revision == 2:
        #     await self.execute(
        #         f"ALTER TABLE {Tablenames.ROCKMAKER_IMAGES} ADD COLUMN {ImageFieldnames.NEWFIELD} TEXT",
        #         why=f"revision 2: add {Tablenames.ROCKMAKER_IMAGES} {ImageFieldnames.NEWFIELD} column",
        #     )
        #     await self.execute(
        #         "CREATE INDEX %s_%s ON %s(%s)"
        #         % (
        #             Tablenames.ROCKMAKER_IMAGES,
        #             ImageFieldnames.NEWFIELD,
        #             Tablenames.ROCKMAKER_IMAGES,
        #             ImageFieldnames.NEWFIELD,
        #         )
        #     )

    # ----------------------------------------------------------------------------------------
    async def add_table_definitions(self):
        """
        Make all the table definitions.
        """

        # Table schemas in our database.
        self.add_table_definition(RockmakerImagesTable())
