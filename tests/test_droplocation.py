import logging

# API constants.
from dls_servbase_api.constants import Keywords as ProtocoljKeywords
from dls_servbase_lib.datafaces.context import Context as DlsServbaseDatafaceContext

# Utilities.
from dls_utilpack.describe import describe

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel

# Client context creator.
from echolocator_api.guis.context import Context as GuiClientContext

# GUI constants.
from echolocator_lib.guis.constants import Commands, Cookies, Keywords

# Server context creator.
from echolocator_lib.guis.context import Context as GuiServerContext

# Object managing gui
from echolocator_lib.guis.guis import echolocator_guis_get_default

# Base class for the tester.
from tests.base import Base

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDroplocation:
    def test(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/service.yaml"
        DroplocationTester().main(
            constants,
            configuration_file,
            output_directory,
        )


# ----------------------------------------------------------------------------------------
class DroplocationTester(Base):
    """
    Class to test the gui fetch_image endpoint.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        multiconf = self.get_multiconf()
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_dataface_specification = multiconf_dict[
            "xchembku_dataface_specification"
        ]

        # Make the xchembku client context, expected to be direct (no server).
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        servbase_dataface_specification = multiconf_dict[
            "dls_servbase_dataface_specification"
        ]
        servbase_dataface_context = DlsServbaseDatafaceContext(
            servbase_dataface_specification
        )

        gui_specification = multiconf_dict["echolocator_gui_specification"]
        # Make the server context.
        gui_server_context = GuiServerContext(gui_specification)

        # Make the client context.
        gui_client_context = GuiClientContext(gui_specification)

        # Start the client context for the direct access to the xchembku.
        async with xchembku_client_context:
            # Start the dataface the gui uses for cookies.
            async with servbase_dataface_context:
                # Start the gui client context.
                async with gui_client_context:
                    # And the gui server context which starts the coro.
                    async with gui_server_context:
                        await self.__run_the_test(constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_the_test(self, constants, output_directory):
        """ """
        # Reference the xchembku object which the context has set up as the default.
        xchembku = xchembku_datafaces_get_default()

        crystal_wells = []

        # Inject some wells.
        crystal_wells.append(
            await self.inject(xchembku, True, False)
        )  # models index 0, sorted index 2: 01A_1
        crystal_wells.append(
            await self.inject(xchembku, True, False)
        )  # models index 1, sorted index 1: 02A_1
        crystal_wells.append(
            await self.inject(xchembku, True, False)
        )  # models index 2, sorted index 0: 03A_1

        # 0. 03A_1 3 a874afc0-9690-4588-ac6d-4cfff72bf504
        # 1. 02A_1 2 3bce2953-7059-4042-bd36-7042914b47a1
        # 2. 01A_1 1 ea239972-cc00-49ac-8a71-afd6b5af7207

        # Query the list, which set the list cookies, needed for the crystal_well_index scheme to work.
        self.__cookies = {}
        await self.__fetch_image_list()

        # The crystal count increases with each one added, so they are sorted in reverse order of adding.
        await self.__set_confirmed_target_and_advance(xchembku, crystal_wells, 2, 1, 1)
        await self.__set_confirmed_target_and_advance(xchembku, crystal_wells, 1, 2, 0)
        await self.__set_confirmed_target_and_advance(
            xchembku, crystal_wells, 0, None, None
        )

        await self.__set_is_usable_and_dont_advance(xchembku, crystal_wells, 0, False)
        await self.__set_is_usable_and_dont_advance(xchembku, crystal_wells, 0, True)

    # ----------------------------------------------------------------------------------------

    async def __set_confirmed_target_and_advance(
        self, xchembku, crystal_well_models, index1, advance_to_list_index, index2
    ):
        """ """

        x = 100 + index1
        y = 200 + index1
        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.UPDATE,
            Keywords.SHOULD_ADVANCE: True,
            Keywords.CRYSTAL_WELL_INDEX: advance_to_list_index,
            "visit": self.visit,
            "crystal_well_droplocation_model": {
                "crystal_well_uuid": crystal_well_models[index1].uuid,
                "confirmed_target_x": x,
                "confirmed_target_y": y,
                "is_usable": True,
            },
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=self.__cookies
        )

        self.__cookies = response["__cookies"]

        note = f"advance from {index1} to {index2}"
        logger.debug(describe(f"set_target response, {note}", response))

        assert "record" in response, note
        record = response["record"]
        assert "confirmation" in response, note
        assert "has been updated" in response["confirmation"], note
        if index2 is not None:
            assert record is not None, note
            assert record["position"] == crystal_well_models[index2].position, note
            assert "advanced" in response["confirmation"], note
        else:
            assert record is None, note
            assert "reached the end of the list" in response["confirmation"], note

        # Fetch the record which should have been updated.
        fetched_models = await xchembku.fetch_crystal_wells_needing_droplocation(
            CrystalWellFilterModel(anchor=crystal_well_models[index1].uuid)
        )

        assert fetched_models[0].confirmed_target_x == x, note
        assert fetched_models[0].confirmed_target_y == y, note
        assert fetched_models[0].is_usable is True, note

    # ----------------------------------------------------------------------------------------

    async def __set_is_usable_and_dont_advance(
        self,
        xchembku,
        crystal_well_models,
        index1,
        is_usable,
    ):
        """ """

        # Build the request to change only the is_usable field.
        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_EDIT_UX,
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.UPDATE,
            Keywords.SHOULD_ADVANCE: False,
            "crystal_well_droplocation_model": {
                "crystal_well_uuid": crystal_well_models[index1].uuid,
                "is_usable": is_usable,
            },
        }

        # Send the ajax request to the gui.
        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=self.__cookies
        )

        assert "record" not in response
        assert "confirmation" in response
        assert "has been updated" in response["confirmation"]

        # Fetch the record which should have been updated.
        fetched_models = await xchembku.fetch_crystal_wells_needing_droplocation(
            CrystalWellFilterModel(anchor=crystal_well_models[index1].uuid)
        )

        # These should remain changed from when we set them previously in the test.
        x = 100 + index1
        y = 200 + index1

        assert fetched_models[0].confirmed_target_x == x, f"index {index1}"
        assert fetched_models[0].confirmed_target_y == y, f"index {index1}"
        assert fetched_models[0].is_usable is is_usable, f"index {index1}"

    # ----------------------------------------------------------------------------------------

    async def __fetch_image_list(self):
        """
        Query the list, which set the list cookied, needed for the crystal_well_index scheme to work.
        """

        request = {
            ProtocoljKeywords.ENABLE_COOKIES: [
                Cookies.IMAGE_LIST_UX,
            ],
            Keywords.COMMAND: Commands.FETCH_IMAGE_LIST,
            "visit_filter": self.visit,
        }

        response = await echolocator_guis_get_default().client_protocolj(
            request, cookies=self.__cookies
        )

        # Pick up the cookies established by the list query.
        self.__cookies = response["__cookies"]
