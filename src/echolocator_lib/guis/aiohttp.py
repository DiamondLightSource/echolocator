import csv
import logging
import multiprocessing
import threading
from pathlib import Path
from typing import List

from dls_servbase_api.constants import Keywords as ProtocoljKeywords

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Basic things.
from dls_utilpack.thing import Thing
from dls_utilpack.visit import get_xchem_directory

# The model which describes the crystal wells to be injected into soakdb3.
from soakdb3_api.models.crystal_well_model import (
    CrystalWellModel as Soakdb3CrystalWellModel,
)

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.models.crystal_plate_filter_model import CrystalPlateFilterModel
from xchembku_api.models.crystal_well_droplocation_model import (
    CrystalWellDroplocationModel,
)
from xchembku_api.models.crystal_well_filter_model import (
    CrystalWellFilterModel,
    CrystalWellFilterSortbyEnum,
)
from xchembku_api.models.crystal_well_needing_droplocation_model import (
    CrystalWellNeedingDroplocationModel,
)

# Base class for an aiohttp server.
from echolocator_lib.base_aiohttp import BaseAiohttp

# Object managing echolocator_composers.
from echolocator_lib.composers.composers import (
    Composers,
    echolocator_composers_get_default,
    echolocator_composers_has_default,
    echolocator_composers_set_default,
)

# Gui protocolj things (must agree with javascript).
from echolocator_lib.guis.constants import Commands, Cookies, Keywords

logger = logging.getLogger(__name__)

thing_type = "echolocator_lib.echolocator_guis.aiohttp"


# ------------------------------------------------------------------------------------------
class Aiohttp(Thing, BaseAiohttp):
    """
    Object implementing remote procedure calls for echolocator_gui methods.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)
        BaseAiohttp.__init__(
            self,
            specification["type_specific_tbd"]["aiohttp_specification"],
            calling_file=__file__,
        )

        self.__xchembku_client_context = None
        self.__xchembku = None

    # ----------------------------------------------------------------------------------------
    def callsign(self):
        """"""
        return "%s %s" % ("Gui.Aiohttp", BaseAiohttp.callsign(self))

    # ----------------------------------------------------------------------------------------
    def activate_process(self):
        """"""

        try:
            multiprocessing.current_process().name = "gui"

            self.activate_process_base()

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} process", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    def activate_thread(self, loop):
        """
        Called from inside a newly created thread.
        """

        try:
            threading.current_thread().name = "gui"

            self.activate_thread_base(loop)

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} thread", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    async def activate_coro(self):
        """"""
        try:
            # No special routes, we will use protocolj dispathcing only
            route_tuples = []

            # Start the actual coro to listen for incoming http requests.
            await self.activate_coro_base(route_tuples)

            # No default composer is set up yet?
            if not echolocator_composers_has_default():
                # The echolocator_composer to use.
                echolocator_composer_specification = {
                    "type": "echolocator_lib.echolocator_composers.html"
                }

                # Set up the default echolocator_composer.
                echolocator_composer = Composers().build_object(
                    echolocator_composer_specification
                )
                echolocator_composers_set_default(echolocator_composer)

            # Make the xchembku client context.
            s = require(
                f"{callsign(self)} specification",
                self.specification(),
                "type_specific_tbd",
            )
            s = require(
                f"{callsign(self)} type_specific_tbd",
                s,
                "xchembku_dataface_specification",
            )
            self.__xchembku_client_context = XchembkuDatafaceClientContext(s)

            # Activate the context.
            await self.__xchembku_client_context.aenter()

            # Get a reference to the xchembku interface provided by the context.
            self.__xchembku = self.__xchembku_client_context.get_interface()

            self.__export_directory = require(
                f"{callsign(self)} specification",
                self.specification(),
                "export_directory",
            )
            self.__export_subdirectory = require(
                f"{callsign(self)} specification",
                self.specification(),
                "export_subdirectory",
            )

        except Exception:
            raise RuntimeError(f"unable to start {callsign(self)} server coro")

    # ----------------------------------------------------------------------------------------
    async def direct_shutdown(self):
        """"""
        logger.debug(f"[ECHDON] {callsign(self)} in direct_shutdown")

        # Forget we have an xchembku client reference.
        self.__xchembku = None

        if self.__xchembku_client_context is not None:
            logger.debug(f"[ECHDON] {callsign(self)} exiting __xchembku_client_context")
            await self.__xchembku_client_context.aexit()
            logger.debug(f"[ECHDON] {callsign(self)} exited __xchembku_client_context")
            self.__xchembku_client_context = None

        # Let the base class stop the server event looping.
        await self.base_direct_shutdown()

        logger.debug(f"[ECHDON] {callsign(self)} called base_direct_shutdown")

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict, opaque):
        """"""

        command = require("request json", request_dict, Keywords.COMMAND)

        # Having no xchembku client reference means we must be shutting down.
        if self.__xchembku is None:
            raise RuntimeError(
                "refusing to execute command %s because server is shutting down"
                % (command)
            )

        if command == Commands.LOAD_TABS:
            return await self.__load_tabs(opaque, request_dict)

        if command == Commands.SELECT_TAB:
            return await self.__select_tab(opaque, request_dict)

        if command == Commands.FETCH_IMAGE:
            return await self.__fetch_image(opaque, request_dict)

        elif command == Commands.FETCH_IMAGE_LIST:
            return await self.__fetch_image_list(opaque, request_dict)

        elif command == Commands.EXPORT_TO_SOAKDB3:
            return await self.__export_to_soakdb3(opaque, request_dict)

        elif command == Commands.EXPORT_TO_CSV:
            return await self.__export_to_csv(opaque, request_dict)

        elif command == Commands.UPDATE:
            return await self.__update(opaque, request_dict)

        else:
            raise RuntimeError("invalid command %s" % (command))

    # ----------------------------------------------------------------------------------------
    async def __load_tabs(self, opaque, request_dict):

        tab_id = await self.get_cookie_content(
            opaque, Cookies.TABS_MANAGER, Keywords.TAB_ID
        )
        logger.debug(f"[GUITABS] tab_id from cookie content is {tab_id}")

        # Reply with tabs.
        response = {Keywords.TAB_ID: tab_id}

        return response

    # ----------------------------------------------------------------------------------------
    async def __select_tab(self, opaque, request_dict):
        tab_id = require("request json", request_dict, Keywords.TAB_ID)

        logger.debug(f"[GUITABS] tab_id in request is {tab_id}")

        # Put the tab_id into the cookie.
        self.set_cookie_content(opaque, Cookies.TABS_MANAGER, Keywords.TAB_ID, tab_id)

        response = {}

        return response

    # ----------------------------------------------------------------------------------------
    async def __fetch_image(self, opaque, request_dict):

        # Get uuid from the cookie if it's not being posted here.
        crystal_well_uuid = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_EDIT_UX,
            "crystal_well_uuid",
            request_dict.get("crystal_well_uuid"),
            "",
        )

        logger.info(
            f"fetching image from crystal_well_uuid {crystal_well_uuid}"
            f" direction {request_dict.get('direction')}"
        )

        # Not able to get an image from posted value or cookie?
        # Usually first time visiting Image Details tab when no image picked from list.
        if crystal_well_uuid == "":
            response = {"record": None}
            return response

        # Start a filter where we anchor on the given well.
        filter = CrystalWellFilterModel(
            anchor=crystal_well_uuid,
            limit=1,
            sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
        )

        # Caller is providing visit?
        visit = request_dict.get("visit")
        if visit is not None:
            filter.visit = visit

        # Image previous or next?
        direction = request_dict.get("direction", 0)
        if direction != 0:
            filter.direction = direction

        should_show_only_undecided = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_LIST_UX,
            "should_show_only_undecided",
            request_dict.get("should_show_only_undecided"),
            False,
        )
        if should_show_only_undecided:
            filter.is_decided = False

        crystal_well_models = (
            await self.__xchembku.fetch_crystal_wells_needing_droplocation(filter)
        )

        if len(crystal_well_models) == 0:
            response = {"record": None}
            if direction != 0:
                response["confirmation"] = "there are no more images in this direction"
            return response

        # Presumably there is only one image of interest.
        record = crystal_well_models[0].dict()
        record["filename"] = "filestore" + record["filename"]
        response = {"record": record}

        return response

    # ----------------------------------------------------------------------------------------
    async def __fetch_image_list(self, opaque, request_dict):

        # Remember last posted value for auto_update_enabled.
        auto_update_enabled = await self._handle_auto_update(
            opaque, request_dict, Cookies.IMAGE_LIST_UX
        )

        visit_filter = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_LIST_UX,
            "visit_filter",
            request_dict.get("visit_filter"),
            None,
        )

        should_show_only_undecided = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_LIST_UX,
            "should_show_only_undecided",
            request_dict.get("should_show_only_undecided"),
            False,
        )

        if visit_filter is None:
            visit_filter = ""
        visit_filter = visit_filter.strip()

        filters = {
            "visit_filter": visit_filter,
            "should_show_only_undecided": should_show_only_undecided,
        }

        if visit_filter == "":
            html = "please enter a visit"

        else:
            logger.debug(
                f"fetching image records, visit_filter is '{visit_filter}' and "
                f" should_show_only_undecided is '{should_show_only_undecided}'"
            )

            # Start a filter where we anchor on the given image.
            filter = CrystalWellFilterModel(
                visit=visit_filter,
                sortby=CrystalWellFilterSortbyEnum.NUMBER_OF_CRYSTALS,
            )

            should_show_only_undecided = await self.set_or_get_cookie_content(
                opaque,
                Cookies.IMAGE_LIST_UX,
                "should_show_only_undecided",
                request_dict.get("should_show_only_undecided"),
                False,
            )
            if should_show_only_undecided:
                filter.is_decided = False

            # Fetch the list from the xchembku.
            crystal_well_models = (
                await self.__xchembku.fetch_crystal_wells_needing_droplocation(filter)
            )

            html = echolocator_composers_get_default().compose_image_list(
                crystal_well_models
            )

        response = {
            "html": html,
            "filters": filters,
            "auto_update_enabled": auto_update_enabled,
        }

        return response

    # ----------------------------------------------------------------------------------------
    async def __update(self, opaque, request_dict):

        t = require("ajax request", request_dict, "crystal_well_droplocation_model")

        # Wrap a model around the posted fields.
        crystal_well_droplocation_model = CrystalWellDroplocationModel(**t)

        # Update the database record.
        await self.__xchembku.upsert_crystal_well_droplocations(
            [crystal_well_droplocation_model],
            only_fields=list(t.keys()),
        )

        # Caller wants to select the next image automatically?
        if request_dict.get(Keywords.SHOULD_ADVANCE, False):

            # Caller must provide a visit in order to automatically advance.
            visit = request_dict.get("visit")
            if visit is None:
                raise RuntimeError(
                    "programming error: visit not submitted with request to advance after update"
                )

            # Advance by fetching the next image record after the update.
            next_request_dict = {
                ProtocoljKeywords.ENABLE_COOKIES: [
                    Cookies.IMAGE_EDIT_UX,
                    Cookies.IMAGE_LIST_UX,
                ],
                Keywords.COMMAND: Commands.FETCH_IMAGE,
                "crystal_well_uuid": crystal_well_droplocation_model.crystal_well_uuid,
                "direction": 1,
                "visit": visit,
            }
            response = await self.__fetch_image(opaque, next_request_dict)

            if response.get("record") is not None:
                response[
                    "confirmation"
                ] = "drop location has been updated and view advanced to next image"
            else:
                response[
                    "confirmation"
                ] = "drop location has been updated and there are no more images in the list"
        else:
            response = {"confirmation": "drop location has been updated"}

        return response

    # ----------------------------------------------------------------------------------------
    async def __export_to_soakdb3(self, opaque, request_dict):

        # Caller must provide a visit.
        visit_filter = request_dict.get("visit_filter")
        if visit_filter is None:
            raise RuntimeError("programming error: visit not submitted with request")

        # Visit must not be blank.
        visit_filter = visit_filter.strip()
        if visit_filter == "":
            response = {"error": "blank visit was given"}
            return response

        # Get a filter for wells we want to export.
        crystal_well_filter = CrystalWellFilterModel(
            visit=visit_filter,
            is_decided=True,
            is_usable=True,
            sortby=CrystalWellFilterSortbyEnum.POSITION,
        )

        # Fetch the list of wells according to the filter.
        crystal_well_models: List[
            CrystalWellNeedingDroplocationModel
        ] = await self.__xchembku.fetch_crystal_wells_needing_droplocation(
            crystal_well_filter
        )

        # Export the crystal wells to the appropriate soakdb3 visit.
        await self.__export_to_soakdb3_visit(visit_filter, crystal_well_models)

        response = {
            "confirmation": f"exported {len(crystal_well_models)} rows to soakdb3 visit {visit_filter}"
        }

        return response

    # ----------------------------------------------------------------------------------------
    async def __export_to_soakdb3_visit(
        self,
        visit,
        crystal_well_models: List[CrystalWellNeedingDroplocationModel],
    ) -> None:

        # Fetch the plate record for visit.
        crystal_plate_filter = CrystalPlateFilterModel(visit=visit)
        crystal_plate_models = await self.__xchembku.fetch_crystal_plates(
            crystal_plate_filter
        )

        if len(crystal_plate_models) == 0:
            raise RuntimeError(
                f'database integrity error: no crystal plate for visit "{visit}"'
            )
        crystal_plate_model = crystal_plate_models[0]

        soakdb3_crystal_well_models = []
        for m in crystal_well_models:
            soakdb3_crystal_well_models.append(
                Soakdb3CrystalWellModel(
                    LabVisit=visit,
                    CrystalPlate=crystal_plate_model.rockminer_collected_stem,
                    CrystalWell=m.position,
                    EchoX=m.confirmed_microns_x,
                    EchoY=m.confirmed_microns_y,
                )
            )

        visit_directory = Path(get_xchem_directory(self.__export_directory, visit))

        logger.debug(
            f"exporting {len(soakdb3_crystal_well_models)} to {str(visit_directory)}"
        )
        # Append well records to soakdb3 database.
        # Soakdb3 wants the "/processing" to be on the end of the visitid.
        await self.__xchembku.inject_soakdb3_crystal_wells(
            str(visit_directory / "processing"), soakdb3_crystal_well_models
        )

    # ----------------------------------------------------------------------------------------
    async def __export_to_csv(self, opaque, request_dict):

        # Caller must provide a visit.
        visit_filter = request_dict.get("visit_filter")
        if visit_filter is None:
            raise RuntimeError("visit not submitted with request (programming error)")

        # Visit must not be blank.
        visit_filter = visit_filter.strip()
        if visit_filter == "":
            response = {"error": "blank visit was given"}
            return response

        # Get a filter for wells we want to export.
        crystal_well_filter = CrystalWellFilterModel(
            visit=visit_filter,
            is_decided=True,
            is_usable=True,
            sortby=CrystalWellFilterSortbyEnum.POSITION,
        )

        # Fetch the list of wells according to the filter.
        crystal_well_models: List[
            CrystalWellNeedingDroplocationModel
        ] = await self.__xchembku.fetch_crystal_wells_needing_droplocation(
            crystal_well_filter
        )

        # Group the wells by the plate they belong to.
        plates_crystal_well_models = {}
        for crystal_well_model in crystal_well_models:
            crystal_plate_uuid = crystal_well_model.crystal_plate_uuid
            if crystal_plate_uuid not in plates_crystal_well_models:
                plates_crystal_well_models[crystal_plate_uuid] = []
            plates_crystal_well_models[crystal_plate_uuid].append(crystal_well_model)

        # Keep a list of the confirmations we will get from exporting the plates.
        confirmations = []

        # Go through each plate separately.
        for (
            crystal_plate_uuid,
            plate_crystal_well_models,
        ) in plates_crystal_well_models.items():
            # Export the crystal wells for this plate to the appropriate csv file named for the plate.
            filename = await self.__export_to_csv_plate(
                visit_filter, crystal_plate_uuid, plate_crystal_well_models
            )

            confirmations.append(
                f"exported {len(plate_crystal_well_models)} rows to {filename}"
            )

        response = {"confirmation": "\n".join(confirmations)}

        return response

    # ----------------------------------------------------------------------------------------
    async def __export_to_csv_plate(
        self,
        visit,
        crystal_plate_uuid,
        crystal_well_models: List[CrystalWellNeedingDroplocationModel],
    ):

        # Fetch the plate record for visit.
        crystal_plate_filter = CrystalPlateFilterModel(uuid=crystal_plate_uuid)
        crystal_plate_models = await self.__xchembku.fetch_crystal_plates(
            crystal_plate_filter
        )

        if len(crystal_plate_models) == 0:
            raise RuntimeError(
                f'database integrity error: no crystal plate for uuid "{crystal_plate_uuid}"'
            )
        crystal_plate_model = crystal_plate_models[0]

        # Use the stem from the rockmaker Luigi pipeline to form the csv filename.
        visit_directory = Path(get_xchem_directory(self.__export_directory, visit))
        targets_directory = visit_directory / self.__export_subdirectory

        filename = (
            targets_directory
            / f"{crystal_plate_model.rockminer_collected_stem}_targets.csv"
        )

        if not filename.parent.is_dir():
            raise RuntimeError(f"the directory does not exist: {str(filename.parent)}")

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)

            for m in crystal_well_models:
                row = []
                row.append(m.position)
                row.append(m.confirmed_microns_x or "")
                row.append(m.confirmed_microns_y or "")
                writer.writerow(row)

        return filename

    # ----------------------------------------------------------------------------------------
    async def _handle_auto_update(self, opaque, request_dict, cookie_name):

        # Remember last posted value for auto_update_enabled.
        auto_update_enabled = request_dict.get("auto_update_enabled")
        # logger.debug(
        #     describe(
        #         f"[AUTOUP] request_dict auto_update_enabled for cookie {cookie_name}",
        #         auto_update_enabled,
        #     )
        # )
        auto_update_enabled = await self.set_or_get_cookie_content(
            opaque,
            cookie_name,
            "auto_update_enabled",
            auto_update_enabled,
            False,
        )
        # logger.debug(
        #     describe(
        #         f"[AUTOUP] request_set_or_get_cookie_content auto_update_enabled",
        #         auto_update_enabled,
        #     )
        # )

        return auto_update_enabled
