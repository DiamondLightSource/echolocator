import logging

# Base class for table definitions.
from dls_normsql.table_definition import TableDefinition

from echolocator_api.databases.constants import ImageFieldnames, Tablenames

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class RockmakerImagesTable(TableDefinition):
    # ----------------------------------------------------------------------------------------
    def __init__(self):
        TableDefinition.__init__(self, Tablenames.ROCKMAKER_IMAGES)

        # All images have a unique autoid field.
        self.fields[ImageFieldnames.AUTOID] = {
            "type": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "index": True,
        }

        self.fields[ImageFieldnames.FILENAME] = {"type": "TEXT", "index": True}
        self.fields[ImageFieldnames.ERROR] = {"type": "TEXT", "index": False}
        self.fields[ImageFieldnames.WIDTH] = {"type": "INTEGER", "index": False}
        self.fields[ImageFieldnames.HEIGHT] = {"type": "INTEGER", "index": False}
        self.fields[ImageFieldnames.WELL_CENTER_X] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[ImageFieldnames.WELL_CENTER_Y] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[ImageFieldnames.TARGET_POSITION_X] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[ImageFieldnames.TARGET_POSITION_Y] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[ImageFieldnames.CRYSTAL_PROBABILITY] = {
            "type": "FLOAT",
            "index": False,
        }
        self.fields[ImageFieldnames.NUMBER_OF_CRYSTALS] = {
            "type": "INTEGER",
            "index": False,
        }
        self.fields[ImageFieldnames.IS_USABLE] = {"type": "BOOLEAN", "index": False}
        self.fields[ImageFieldnames.IS_DROP] = {"type": "BOOLEAN", "index": False}
        self.fields[ImageFieldnames.CREATED_ON] = {"type": "TEXT", "index": False}
