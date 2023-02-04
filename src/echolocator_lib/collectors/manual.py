import logging

# Base class for collector instances.
from echolocator_lib.collectors.base import Base as CollectorBase

logger = logging.getLogger(__name__)

thing_type = "echolocator_lib.collectors.popener"


# ------------------------------------------------------------------------------------------
class Manual(CollectorBase):
    """
    Object representing a collector which launches a task using popen for onboard execution.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification, predefined_uuid=None):
        CollectorBase.__init__(
            self, thing_type, specification, predefined_uuid=predefined_uuid
        )

    # ----------------------------------------------------------------------------------------
    async def activate(self):
        """"""
        pass

    # ----------------------------------------------------------------------------------------
    async def deactivate(self):
        """"""
        pass

    # ----------------------------------------------------------------------------------------
    async def fire(
        self,
        message,
    ):
        """"""

        await CollectorBase.trigger(
            self,
            message["workflow_filename_classname"],
            **message["workflow_constructor_kwargs"],
        )
