import json
import logging
import subprocess

from echolocator_api.databases.constants import ImageFieldnames, Tablenames

# Object managing datafaces.
from echolocator_api.datafaces.datafaces import echolocator_datafaces_get_default

# Context creator.
from echolocator_lib.contexts.contexts import Contexts

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestTutorial:
    def test_dataface_laptop(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/laptop.yaml"
        TutorialTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TutorialTester(BaseContextTester):
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
                        ImageFieldnames.FILENAME: "1.jpg",
                        ImageFieldnames.TARGET_POSITION_X: 1,
                        ImageFieldnames.TARGET_POSITION_Y: 2,
                    },
                    {
                        ImageFieldnames.FILENAME: "2.jpg",
                        ImageFieldnames.TARGET_POSITION_X: 3,
                        ImageFieldnames.TARGET_POSITION_Y: 4,
                    },
                ],
            )

            # Run the tutorial and capture the output.

            command = ["python", "tests/tutorials/tutorial2.py"]
            process = subprocess.run(command, capture_output=True)
            if process.returncode != 0:
                stderr = process.stderr.decode().replace("\\n", "\n")
                logger.debug(f"stderr is:\n{stderr}")
                assert process.returncode == 0

            stdout = process.stdout.decode().replace("\\n", "\n")
            logger.debug(f"stdout is:\n{stdout}")
            try:
                result = json.loads(stdout)
                assert result["count"] == 1
            except Exception:
                assert False, "stdout is not json"

            # Check the tutorial ran.
            all_sql = f"SELECT * FROM {Tablenames.ROCKMAKER_IMAGES}"
            records = await dataface.query(all_sql)

            assert len(records) == 2
            assert records[0][ImageFieldnames.FILENAME] == "1.jpg"
            assert records[0][ImageFieldnames.TARGET_POSITION_X] == 1
            assert records[0][ImageFieldnames.TARGET_POSITION_Y] == 2
