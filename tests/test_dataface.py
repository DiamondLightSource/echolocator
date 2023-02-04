import logging

from echolocator_api.databases.constants import ImageFieldnames, Tablenames

# Object managing datafaces.
from echolocator_api.datafaces.datafaces import echolocator_datafaces_get_default

# Context creator.
from echolocator_lib.contexts.contexts import Contexts

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDatafaceImage:
    def test_dataface_laptop(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/laptop.yaml"
        DatafaceImageTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DatafaceImageTester(BaseContextTester):
    """
    Class to test the dataface.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        echolocator_configurator = self.get_configurator()

        context_configuration = await echolocator_configurator.load()
        echolocator_context = Contexts().build_object(context_configuration)

        async with echolocator_context:
            dataface = echolocator_datafaces_get_default()

            # Write one record.
            await dataface.insert(
                Tablenames.ROCKMAKER_IMAGES,
                [
                    {
                        ImageFieldnames.FILENAME: "x",
                        ImageFieldnames.TARGET_POSITION_X: "1",
                        ImageFieldnames.TARGET_POSITION_Y: "2",
                    }
                ],
            )

            all_sql = f"SELECT * FROM {Tablenames.ROCKMAKER_IMAGES}"
            records = await dataface.query(all_sql)

            assert len(records) == 1
            assert records[0][ImageFieldnames.FILENAME] == "x"
            assert records[0][ImageFieldnames.TARGET_POSITION_X] == 1
            assert records[0][ImageFieldnames.TARGET_POSITION_Y] == 2

            # ----------------------------------------------------------------
            # Now try an update.
            record = {
                ImageFieldnames.WELL_CENTER_X: 123,
                ImageFieldnames.WELL_CENTER_Y: 456,
            }

            subs = [1]
            result = await dataface.update(
                Tablenames.ROCKMAKER_IMAGES,
                record,
                f"{ImageFieldnames.AUTOID} = ?",
                subs=subs,
                why="test update",
            )

            assert result["count"] == 1
            records = await dataface.query(all_sql)

            assert len(records) == 1
            assert records[0][ImageFieldnames.WELL_CENTER_X] == 123
            assert records[0][ImageFieldnames.WELL_CENTER_Y] == 456
