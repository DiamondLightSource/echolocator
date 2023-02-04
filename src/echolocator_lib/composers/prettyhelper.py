import json
import logging

import prettytable

logger = logging.getLogger(__name__)


class PrettyHelper:
    """ """

    # ----------------------------------------------------------------------------------------
    def __init__(self):
        pass

    # ----------------------------------------------------------------------------------------
    def compose_health_reports(self, health_reports):
        """"""

        table = prettytable.PrettyTable()
        table.field_names = [
            "service",
            "seconds alive",
            "request count",
            "state",
            "details",
        ]

        rows = []
        for health_report in health_reports:
            row = []
            row.append(health_report["name"])
            row.append(health_report.get("time_alive", "-"))
            row.append(health_report.get("request_count", "-"))
            row.append(health_report["state"])

            details = []
            if "exception" in health_report:
                details.append(health_report["exception"])

            if "details" in health_report:
                details.append(json.dumps(health_report["details"], indent=4))

            details = "\n\n".join(details)
            row.append(f"<xmp>{details}</xmp>")

            rows.append(row)

        table.add_rows(rows)

        table.align = "l"
        table.align["seconds alive"] = "r"
        table.align["request count"] = "r"

        table.title = "Health Reports"
        return table
