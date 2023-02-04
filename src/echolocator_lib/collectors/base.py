import inspect
import logging

from dls_utilpack.import_class import import_class

# Base class which maps flask tasks to methods.
from echolocator_api.thing import Thing

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------
class Base(Thing):
    """
    Object representing a collector which receives triggers from aiohttp.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, thing_type, specification=None, predefined_uuid=None):
        Thing.__init__(self, thing_type, specification, predefined_uuid=predefined_uuid)

    # ----------------------------------------------------------------------------------------
    async def job_was_deleted(self, news_payload):
        pass

    # ------------------------------------------------------------------------------------------
    async def trigger(self, workflow_filename_classname, **workflow_constructor_kwargs):
        """Handle request to submit task for execution."""

        logger.debug(f"[DMOTF] triggering workflow from {workflow_filename_classname}")

        class_object = import_class(workflow_filename_classname)

        logger.debug("[DMOTF] constructing")

        # Construct the workflow instance.
        workflow = class_object(**workflow_constructor_kwargs)

        logger.debug("[DMOTF] building")

        # Let the workflow build itself.
        if inspect.iscoroutinefunction(workflow.build):
            await workflow.build()
        else:
            workflow.build()

        logger.debug("[DMOTF] starting")

        # Commit workflow to the database and enable it for scheduling.
        await workflow.start()

        logger.debug("[DMOTF] started")
