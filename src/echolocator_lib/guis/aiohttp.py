import logging
import multiprocessing
import threading

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Global managers.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel

# Direct database queries (need to be deprecated).
from echolocator_api.databases.constants import ImageFieldnames, Tablenames

# Basic things.
from echolocator_api.thing import Thing

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

        except Exception:
            raise RuntimeError(f"unable to start {callsign(self)} server coro")

    # ----------------------------------------------------------------------------------------
    async def direct_shutdown(self):
        """"""

        # Let the base class stop the server looping.
        await self.base_direct_shutdown()

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict, opaque):
        """"""

        command = require("request json", request_dict, Keywords.COMMAND)

        if command == Commands.LOAD_TABS:
            return await self._load_tabs(opaque, request_dict)

        if command == Commands.SELECT_TAB:
            return await self._select_tab(opaque, request_dict)

        if command == Commands.FETCH_IMAGE:
            return await self._fetch_image(opaque, request_dict)

        elif command == Commands.FETCH_IMAGE_LIST:
            return await self._fetch_image_list(opaque, request_dict)

        elif command == Commands.SET_TARGET_POSITION:
            return await self._set_target_position(opaque, request_dict)

        elif command == Commands.SET_IMAGE_IS_USABLE:
            return await self._set_image_is_usable(opaque, request_dict)

        else:
            raise RuntimeError("invalid command %s" % (command))

    # ----------------------------------------------------------------------------------------
    async def _load_tabs(self, opaque, request_dict):

        tab_id = await self.get_cookie_content(
            opaque, Cookies.TABS_MANAGER, Keywords.TAB_ID
        )
        logger.debug(f"[GUITABS] tab_id from cookie content is {tab_id}")

        # Reply with tabs.
        response = {Keywords.TAB_ID: tab_id}

        return response

    # ----------------------------------------------------------------------------------------
    async def _select_tab(self, opaque, request_dict):
        tab_id = require("request json", request_dict, Keywords.TAB_ID)

        logger.debug(f"[GUITABS] tab_id in request is {tab_id}")

        # Put the tab_id into the cookie.
        self.set_cookie_content(opaque, Cookies.TABS_MANAGER, Keywords.TAB_ID, tab_id)

        response = {}

        return response

    # ----------------------------------------------------------------------------------------
    async def _fetch_image(self, opaque, request_dict):

        # Get uuid from the cookie if it's not being posted here.
        uuid = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_EDIT_UX,
            "uuid",
            request_dict.get("uuid"),
            "",
        )

        # Not able to get an image from posted value or cookie?
        # Usually first time visiting Image Details tab when no image picked from list.
        if uuid == "":
            response = {"record": None}
            return response

        # Start a filter where we anchor on the given image.
        filter = CrystalWellFilterModel(anchor=uuid)

        # Image previous or next?
        direction = request_dict.get("direction", 0)
        if direction != 0:
            filter.direction = direction

        crystal_well_models = await xchembku_datafaces_get_default().fetch_crystal_wells_needing_droplocation(
            filter
        )

        if len(crystal_well_models) == 0:
            response = {"record": None}
            return response

        record = crystal_well_models[0].dict()
        record["filename"] = "filestore" + record["filename"]
        response = {"record": record}

        return response

    # ----------------------------------------------------------------------------------------
    async def _fetch_image_records(self, opaque):

        name_pattern = await self.get_cookie_content(
            opaque, Cookies.IMAGE_LIST_UX, "name_pattern", default=""
        )
        should_show_only_undecided = await self.get_cookie_content(
            opaque, Cookies.IMAGE_LIST_UX, "should_show_only_undecided", default=""
        )

        where_and_sqls = []
        where_and_subs = []
        if name_pattern != "":
            where_and_sqls.append("filename GLOB ?")
            where_and_subs.append(name_pattern)
        if should_show_only_undecided:
            where_and_sqls.append(f"{ImageFieldnames.IS_USABLE} IS NULL")

        if len(where_and_sqls) > 0:
            where = " WHERE " + " AND ".join(where_and_sqls)
        else:
            where = ""

        records = await xchembku_datafaces_get_default().query(
            f"SELECT * FROM {Tablenames.ROCKMAKER_IMAGES}"
            + where
            + f" ORDER BY {ImageFieldnames.CREATED_ON} DESC",
            subs=where_and_subs,
        )

        return records

    # ----------------------------------------------------------------------------------------
    async def _fetch_image_list(self, opaque, request_dict):

        # Remember last posted value for auto_update_enabled.
        auto_update_enabled = await self._handle_auto_update(
            opaque, request_dict, Cookies.IMAGE_LIST_UX
        )

        name_pattern = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_LIST_UX,
            "name_pattern",
            request_dict.get("name_pattern"),
            "",
        )
        should_show_only_undecided = await self.set_or_get_cookie_content(
            opaque,
            Cookies.IMAGE_LIST_UX,
            "should_show_only_undecided",
            request_dict.get("should_show_only_undecided"),
            False,
        )

        logger.debug(
            f"fetching image records, name_pattern is '{name_pattern}', should_show_only_undecided is '{should_show_only_undecided}'"
        )

        where_and_sqls = []
        where_and_subs = []
        if name_pattern != "":
            where_and_sqls.append("filename GLOB ?")
            where_and_subs.append(name_pattern)
        if should_show_only_undecided:
            where_and_sqls.append(f"{ImageFieldnames.IS_USABLE} IS NULL")

        if len(where_and_sqls) > 0:
            where = " WHERE " + " AND ".join(where_and_sqls)
        else:
            where = ""
        records = await xchembku_datafaces_get_default().query(
            f"SELECT * FROM {Tablenames.ROCKMAKER_IMAGES}"
            + where
            + f" ORDER BY {ImageFieldnames.CREATED_ON} DESC",
            subs=where_and_subs,
        )
        html = echolocator_composers_get_default().compose_image_list(records)
        filters = {
            "name_pattern": name_pattern,
            "should_show_only_undecided": should_show_only_undecided,
        }
        response = {
            "html": html,
            "filters": filters,
            "auto_update_enabled": auto_update_enabled,
        }

        return response

    # ----------------------------------------------------------------------------------------
    async def _set_target_position(self, opaque, request_dict):

        sql = (
            f"UPDATE {Tablenames.ROCKMAKER_IMAGES}"
            f" SET {ImageFieldnames.TARGET_POSITION_X} = ?,"
            f" {ImageFieldnames.TARGET_POSITION_Y} = ?"
            f" WHERE {ImageFieldnames.AUTOID} = ?"
        )

        subs = []
        target_position = require("ajax request", request_dict, "target_position")
        subs.append(require("ajax request target_position", target_position, "x"))
        subs.append(require("ajax request target_position", target_position, "y"))
        subs.append(require("ajax request", request_dict, "autoid"))

        await xchembku_datafaces_get_default().execute(sql, subs)

        response = {"status": "ok"}

        return response

    # ----------------------------------------------------------------------------------------
    async def _set_image_is_usable(self, opaque, request_dict):
        """
        Set the is_usable flag on the image given its autoid.
        """

        sql = (
            f"UPDATE {Tablenames.ROCKMAKER_IMAGES}"
            f" SET {ImageFieldnames.IS_USABLE} = ?"
            f" WHERE {ImageFieldnames.AUTOID} = ?"
        )

        subs = []
        subs.append(require("ajax request", request_dict, "is_usable"))
        subs.append(require("ajax request", request_dict, "autoid"))

        await xchembku_datafaces_get_default().execute(sql, subs)

        # Fetch the next image record after the update.
        request_dict["direction"] = 1
        response = await self._fetch_image(opaque, request_dict)

        return response

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
