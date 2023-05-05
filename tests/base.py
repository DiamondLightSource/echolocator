import asyncio
import logging
import multiprocessing
import os

import pytest
from dls_multiconf_lib.constants import ThingTypes as MulticonfThingTypes

# Configurator.
from dls_multiconf_lib.multiconfs import Multiconfs, multiconfs_set_default

# Types which the CrystalPlateObjects factory can use to build an instance.
from xchembku_api.crystal_plate_objects.constants import (
    ThingTypes as CrystalPlateObjectThingTypes,
)
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class Base:
    """
    This is a base class for tests which use Context.
    """

    def __init__(self):
        self.tasks_execution_outputs = {}
        self.residuals = ["stdout.txt", "stderr.txt", "main.log"]

        self.injected_count = 0
        self.visit = "cm00001-1"
        self.__barcode_template = "98a%d"
        self.crystal_plate_uuid = None
        self.__rockminer_collected_stem_template = "98a%d_2021-09-14_RI1000-0276-3drop"

        self.crystal_plate_models = []

        self.__formulatrix_plate_id = 0

    def main(self, constants, configuration_file, output_directory):
        """
        This is the main program which calls the test using asyncio.
        """

        # Save these for when the configuration is loaded.
        self.__configuration_file = configuration_file
        self.__output_directory = output_directory

        multiprocessing.current_process().name = "main"

        # self.__blocked_event = asyncio.Event()

        failure_message = None
        try:
            # Run main test in asyncio event loop.
            asyncio.run(self._main_coroutine(constants, output_directory))

        except Exception as exception:
            logger.exception(
                "unexpected exception in the test method", exc_info=exception
            )
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)

    # ----------------------------------------------------------------------------------------
    def get_multiconf(self):

        rockingest_multiconf = Multiconfs().build_object(
            {
                "type": MulticonfThingTypes.YAML,
                "type_specific_tbd": {"filename": self.__configuration_file},
            }
        )

        # For convenience, always do these replacement.
        rockingest_multiconf.substitute({"output_directory": self.__output_directory})

        # Add various things from the environment into the multiconf.
        rockingest_multiconf.substitute(
            {
                "CWD": os.getcwd(),
                "PYTHONPATH": os.environ.get("PYTHONPATH", "PYTHONPATH"),
            }
        )

        # Set the global value of our multiconf which might be used in other modules.
        multiconfs_set_default(rockingest_multiconf)

        return rockingest_multiconf

    # ----------------------------------------------------------------------------------------

    async def inject_plate(self, xchembku):
        """ """

        self.__formulatrix_plate_id += 1
        self.barcode = self.__barcode_template % (self.__formulatrix_plate_id)
        rockminer_collected_stem = self.__rockminer_collected_stem_template % (
            self.__formulatrix_plate_id
        )

        # Make the plate on which the wells reside.
        crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=self.__formulatrix_plate_id,
            barcode=self.barcode,
            rockminer_collected_stem=rockminer_collected_stem,
            visit=self.visit,
            thing_type=CrystalPlateObjectThingTypes.SWISS3,
        )

        await xchembku.upsert_crystal_plates([crystal_plate_model])
        self.crystal_plate_uuid = crystal_plate_model.uuid

        self.crystal_plate_models.append(crystal_plate_model)

    # ----------------------------------------------------------------------------------------

    async def inject(self, xchembku, autolocation: bool, droplocation: bool):
        """ """

        if self.crystal_plate_uuid is None:
            await self.inject_plate(xchembku)

        self.injected_count += 1

        filename = "/tmp/%03d.jpg" % (self.injected_count)

        # Write well record.
        m = CrystalWellModel(
            position="%02dA_1" % (self.injected_count),
            filename=filename,
            crystal_plate_uuid=self.crystal_plate_uuid,
        )

        await xchembku.upsert_crystal_wells([m])

        if autolocation:
            # Add a crystal well autolocation.
            t = CrystalWellAutolocationModel(
                crystal_well_uuid=m.uuid,
                number_of_crystals=self.injected_count,
                well_centroid_x=400,
                well_centroid_y=500,
                auto_target_x=self.injected_count * 10 + 0,
                auto_target_y=self.injected_count * 10 + 1,
            )

            await xchembku.originate_crystal_well_autolocations([t])

        if droplocation:
            # Add a crystal well droplocation.
            t = CrystalWellDroplocationModel(
                crystal_well_uuid=m.uuid,
                confirmed_target_x=self.injected_count * 100 + 2,
                confirmed_target_y=self.injected_count * 100 + 3,
                is_usable=True,
            )

            await xchembku.upsert_crystal_well_droplocations([t])

        return m
