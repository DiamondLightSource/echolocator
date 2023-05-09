import html
import logging
from pathlib import Path
from typing import List, Optional, Sequence, Union

import numpy as np

# Base class for generic things.
from dls_utilpack.thing import Thing

# Models which we can compose.
from xchembku_api.models.crystal_plate_report_model import CrystalPlateReportModel
from xchembku_api.models.crystal_well_needing_droplocation_model import (
    CrystalWellNeedingDroplocationModel,
)

# Class to do the work using prettytable.
from echolocator_lib.composers.prettyhelper import PrettyHelper

logger = logging.getLogger(__name__)

thing_type = "echolocator_lib.echolocator_composers.html"
# TODO: Move these constants outside this file and allow adjustment according to imager used
MICRONS_PER_PIXEL_X = 2.837
MICRONS_PER_PIXEL_Y = 2.837
SCALE_FACTORS = [MICRONS_PER_PIXEL_Y, MICRONS_PER_PIXEL_X]


class Html(Thing):
    """
    Class which composes various things as html.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None):
        Thing.__init__(self, thing_type, specification)

        self.__prettyhelper = PrettyHelper()

        self.__indent = 0

    # ----------------------------------------------------------------------------------------
    def compose_image_list(self, models: List[CrystalWellNeedingDroplocationModel]):
        """
        Compose the image list as an html table.
        """

        field_names = [
            {"text": "uuid", "class": "T_uuid"},
            {"text": "well", "class": "T_well"},
            {"text": "#Crystals", "class": "T_number_of_crystals"},
            {"text": "Offset x (\u03BCm)", "class": "T_real_space_target_x"},
            {"text": "Offset y (\u03BCm)", "class": "T_real_space_target_y"},
            {"text": "drop", "class": "T_is_drop"},
            {"text": "well centroid x,y", "class": "T_well_centroid_x_y"},
            {"text": "auto x,y", "class": "T_auto_target_x_y"},
            {"text": "confirmed x,y", "class": "T_confirmed_target_x_y"},
            {"text": "echo coordinate x,y", "class": "T_confirmed_microns_x_y"},
            {"text": "use", "class": "T_is_usable"},
            {"text": "error", "class": "T_error"},
        ]

        html_lines = []

        html_lines.append("<table>")
        html_lines.append("<thead>")
        html_lines.append("<tr>")
        for field_name in field_names:
            if isinstance(field_name, dict):
                html_lines.append(
                    f"<th class='{field_name['class']}'>{field_name['text']}</th>"
                )
            else:
                html_lines.append(f"<th>{field_name}</th>")
        html_lines.append("</tr>")
        html_lines.append("</thead>")

        html_lines.append("<tbody>")

        # Traverse all the given records.
        for model in models:
            uuid = model.uuid
            error = model.error
            if error is None:
                error = "-"
            html_lines.append(f"<tr crystal_well_uuid='{uuid}'>")
            html_lines.append(f"<td class='T_uuid'>{uuid}</td>")

            # Extract derived info from filename
            filestem = Path(model.filename).stem

            html_lines.append(
                f"<td class='T_filename' title='{html.escape(model.filename)}'>{html.escape(filestem)}</td>"
            )

            t = model.number_of_crystals
            if t is None:
                t = "-"
            html_lines.append("<td id='number_of_crystals'>" + str(t) + "</td>")

            target_x = model.auto_target_x
            target_y = model.auto_target_y
            well_centre_x = model.well_centroid_x
            well_centre_y = model.well_centroid_y
            t = self.calculate_realspace_offset(
                [target_y, target_x],
                [well_centre_y, well_centre_x],
                SCALE_FACTORS,
            )
            if t is None:
                t = ["-", "-"]
            html_lines.append(
                "<td class='T_real_space_target_x' id='real_space_target_x'>"
                + str(t[1])
                + "</td>"
            )
            html_lines.append(
                "<td class='T_real_space_target_y' id='real_space_target_y'>"
                + str(t[0])
                + "</td>"
            )

            t = model.drop_detected
            if t is None:
                t = "-"
            elif t:
                t = "yes"
            else:
                t = "no"
            html_lines.append("<td class='T_is_drop'>" + str(t) + "</td>")

            if model.well_centroid_x is None or model.well_centroid_y is None:
                t = "-"
            else:
                t = f"{model.well_centroid_x}, {model.well_centroid_y}"
            html_lines.append("<td class='T_well_centroid_x_y'>" + t + "</td>")

            if model.auto_target_x is None or model.auto_target_y is None:
                t = "-"
            else:
                t = f"{model.auto_target_x}, {model.auto_target_y}"
            html_lines.append("<td class='T_auto_target_x_y'>" + t + "</td>")

            if model.confirmed_target_x is None or model.confirmed_target_y is None:
                t = "-"
            else:
                t = f"{model.confirmed_target_x}, {model.confirmed_target_y}"
            html_lines.append("<td class='T_confirmed_target_x_y'>" + t + "</td>")

            if model.confirmed_microns_x is None or model.confirmed_microns_y is None:
                t = "-"
            else:
                t = f"{model.confirmed_microns_x}, {model.confirmed_microns_y}"
            html_lines.append("<td class='T_confirmed_microns_x_y'>" + t + "</td>")

            t = model.is_usable
            if t is None:
                t = "-"
            elif t:
                t = "yes"
            else:
                t = "no"
            html_lines.append("<td class='T_is_usable'>" + str(t) + "</td>")

            html_lines.append("<td class='T_error'>" + html.escape(error) + "</td>")

            html_lines.append("</td>")

            html_lines.append("</tr>")

        html_lines.append("</tbody>")

        html_lines.append("</table>")

        return "\n".join(html_lines)

    # ----------------------------------------------------------------------------------------
    def compose_crystal_plate_report(self, models: List[CrystalPlateReportModel]):
        """
        Compose the crystal plates as an html table.
        """

        field_names = [
            {"text": "uuid", "class": "T_uuid"},
            {"text": "formulatrix plate id", "class": "T_formulatrix__plate__id"},
            {
                "text": "formulatrix experiment name",
                "class": "T_formulatrix__experiment__name",
            },
            {"text": "rockminer collected stem", "class": "T_rockminer_collected_stem"},
            {"text": "barcode", "class": "T_barcode"},
            {"text": "visit", "class": "T_visit"},
            {"text": "collected from Luigi", "class": "T_collected_count T_count"},
            {"text": "chimp processed", "class": "T_chimped_count T_count"},
            {"text": "undecided", "class": "T_undecided_count T_count"},
            {
                "text": "undecided with crystals",
                "class": "T_undecided_crystals_count T_count",
            },
            {"text": "decided", "class": "T_decided_count T_count"},
            {"text": "usable", "class": "T_decided_usable_count T_count"},
            {
                "text": "unusable",
                "class": "T_decided_unusable_count T_count",
            },
            {"text": "exported", "class": "T_exported_count T_count"},
            {
                "text": "ready to export",
                "class": "T_usable_unexported_count T_count",
            },
        ]

        html_lines = []

        html_lines.append("<table>")
        html_lines.append("<thead>")
        html_lines.append("<tr>")
        for field_name in field_names:
            if isinstance(field_name, dict):
                html_lines.append(
                    f"<th class='{field_name['class']}'>{field_name['text']}</th>"
                )
            else:
                html_lines.append(f"<th>{field_name}</th>")
        html_lines.append("</tr>")
        html_lines.append("</thead>")

        html_lines.append("<tbody>")

        # Traverse all the given records.
        for model in models:
            uuid = model.uuid
            html_lines.append(f"<tr crystal_plate_uuid='{uuid}'>")
            html_lines.append(f"<td class='T_uuid'>{uuid}</td>")
            html_lines.append(
                f"<td class='T_formulatrix__plate__id'>{model.formulatrix__plate__id}</td>"
            )
            html_lines.append(
                f"<td class='T_formulatrix__experiment__name'>{model.formulatrix__experiment__name}</td>"
            )
            html_lines.append(
                f"<td class='T_rockminer_collected_stem'>{model.rockminer_collected_stem}</td>"
            )
            html_lines.append(f"<td class='T_barcode'>{model.barcode}</td>")
            html_lines.append(f"<td class='T_visit'>{model.visit}</td>")
            html_lines.append(
                f"<td class='T_collected_count T_count'>{model.collected_count}</td>"
            )
            html_lines.append(
                f"<td class='T_chimped_count T_count'>{model.chimped_count}</td>"
            )
            html_lines.append(
                f"<td class='T_undecided_count T_count'>{model.undecided_count}</td>"
            )
            html_lines.append(
                f"<td class='T_undecided_crystals_count T_count'>{model.undecided_crystals_count}</td>"
            )
            html_lines.append(
                f"<td class='T_decided_count T_count'>{model.decided_count}</td>"
            )
            html_lines.append(
                f"<td class='T_decided_usable_count T_count'>{model.decided_usable_count}</td>"
            )
            html_lines.append(
                f"<td class='T_decided_unusable_count T_count'>{model.decided_unusable_count}</td>"
            )
            html_lines.append(
                f"<td class='T_exported_count T_count'>{model.exported_count}</td>"
            )
            html_lines.append(
                f"<td class='T_usable_unexported_count T_count'>{model.usable_unexported_count}</td>"
            )

            html_lines.append("</tr>")

        html_lines.append("</tbody>")

        html_lines.append("</table>")

        return "\n".join(html_lines)

    # ----------------------------------------------------------------------------------------
    def calculate_realspace_offset(
        self,
        confirmed_target: Sequence[int],
        well_centre: Sequence[int],
        scale_factor: Sequence[float],
    ) -> Optional[int]:
        if self.list_has_none(confirmed_target) or self.list_has_none(well_centre):
            return None
        return np.rint(
            (np.array(confirmed_target) - np.array(well_centre))
            * np.array(scale_factor)
        ).astype(int)

    # ----------------------------------------------------------------------------------------
    def list_has_none(self, input_list: Sequence[Union[int, None]]) -> bool:
        return any(x is None for x in input_list)

    # ----------------------------------------------------------------------------------------
    def compose_lines(self, lines):
        """
        Compose a list of strings as a div with css class T_echolocator_composer_lines.
        Each line will also be a div with class T_echolocator_composer_line.
        """
        html_string = []

        html_string.append("<div class='T_echolocator_composer_lines'>")
        for line in lines:
            html_string.append(
                f"<div class='T_echolocator_composer_line'>{html.escape(line)}</div>"
            )
        html_string.append("</div><!-- T_echolocator_composer_lines -->")

        return "\n".join(html_string)

    # ----------------------------------------------------------------------------------------
    def compose_tree(self, contents):
        """
        Compose the contents dict into a tree of sub-branches.
        """
        self.__lines = []
        self._compose_tree_branch("", contents)

        return "\n".join(self.__lines)

    # ----------------------------------------------------------------------------------------
    def _compose_tree_branch(self, key, contents):
        """
        Compose an HTML div, recursive.
        """
        prefix = " " * self.__indent
        self.__lines.append(f"{prefix}<div class='T_section'>")
        self.__indent += 2
        prefix = " " * self.__indent

        self.__lines.append(f"{prefix}<div class='T_title'>{html.escape(key)}</div>")
        self.__lines.append(f"{prefix}<div class='T_body'>")

        for key, content in contents.items():
            if isinstance(content, dict):
                self.__indent += 2
                self._compose_tree_branch(key, content)
                self.__indent -= 2
            else:
                self._compose_tree_leaf(key, content)

        self.__lines.append(f"{prefix}</div><!-- T_body -->")

        self.__indent -= 2
        prefix = " " * self.__indent
        self.__lines.append(f"{prefix}</div><!-- T_section -->")

    # ----------------------------------------------------------------------------------------
    def _compose_tree_leaf(self, key, value):
        """
        Componse the final non-dict element as a leaf of the tree.
        """
        self.__indent += 2
        prefix1 = " " * self.__indent
        prefix2 = " " * (self.__indent + 2)
        self.__lines.append(f"{prefix1}<div class='T_item'>")
        self.__lines.append(f"{prefix2}<div class='T_prompt'>{html.escape(key)}</div>")
        if isinstance(value, list):
            value = self.compose_lines(value)
        else:
            value = html.escape(str(value))
        self.__lines.append(f"{prefix2}<div class='T_value'>{value}</div>")
        self.__lines.append(f"{prefix1}</div>")
        self.__indent -= 2
