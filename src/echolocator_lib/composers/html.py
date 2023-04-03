import html
import logging
import re
from pathlib import Path
from typing import Optional, Sequence, Union

import numpy as np

# Base class for generic things.
from dls_utilpack.thing import Thing
from xchembku_api.models.crystal_well_needing_droplocation_model import (
    CrystalWellNeedingDroplocationModel,
)

# Database record field names coming from database fields.
from echolocator_api.databases.constants import ImageFieldnames

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
    def compose_image_list(self, models: [CrystalWellNeedingDroplocationModel]):
        """
        Compose the image list as an html table.
        """

        field_names = [
            {"text": "uuid", "class": "T_uuid"},
            {"text": "filename", "class": "T_filename"},
            {"text": "Barcode", "class": "T_barcode"},
            {"text": "Subwell", "class": "T_plate_position"},
            {"text": "#Crystals", "class": "T_number_of_crystals"},
            {"text": "Offset x (\u03BCm)", "class": "T_real_space_target_x"},
            {"text": "Offset y (\u03BCm)", "class": "T_real_space_target_y"},
            {"text": "drop?", "class": "T_is_drop"},
            {"text": "use?", "class": "T_is_usable"},
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
            html_lines.append(f"<td>{uuid}</td>")
            html_lines.append(
                f"<td class='T_filename'>{html.escape(model.filename)}</td>"
            )

            # Extract derived info from filename
            filename = Path(model.filename).name
            barcode, plate_position = self.extract_plate_info_from_filename(
                str(filename)
            )

            html_lines.append(f"<td>{barcode}</td>")

            html_lines.append(f"<td>{plate_position}</td>")

            t = model.number_of_crystals
            if t is None:
                t = "-"
            html_lines.append("<td id='number_of_crystals'>" + str(t) + "</td>")

            target_x = model.auto_target_position_x
            target_y = model.auto_target_position_y
            well_centre_x = model.well_centroid_x
            well_centre_y = model.well_centroid_y
            t = self.calculate_realspace_offset(
                [target_y, target_x],
                [well_centre_y, well_centre_x],
                SCALE_FACTORS,
            )
            if t is None:
                t = ["-", "-"]
            html_lines.append("<td id='real_space_target_x'>" + str(t[1]) + "</td>")
            html_lines.append("<td id='real_space_target_y'>" + str(t[0]) + "</td>")

            t = model.drop_detected
            if t is None:
                t = "-"
            elif t:
                t = "yes"
            else:
                t = "no"
            html_lines.append("<td id='is_drop'>" + str(t) + "</td>")

            t = model.is_valid
            if t is None:
                t = "-"
            elif t:
                t = "yes"
            else:
                t = "no"
            html_lines.append("<td id='is_usable'>" + str(t) + "</td>")

            html_lines.append("<td id='error'>" + html.escape(error) + "</td>")

            html_lines.append("</td>")

            html_lines.append("</tr>")

        html_lines.append("</tbody>")

        html_lines.append("</table>")

        return "\n".join(html_lines)

    # ----------------------------------------------------------------------------------------
    def extract_plate_info_from_filename(self, filename: str) -> tuple[str, str]:
        barcode = None
        position = None
        subwell = None
        pattern = re.compile(r"(\w{4})_(\w{3})_(\d).jpg")
        match = re.findall(pattern, filename)
        if match:
            barcode, position, subwell = match[0]
            position = f"{position[-1]}{position[:2]}_{subwell}"
            return barcode, position
        else:
            logging.error("Unable to get barcode and position from filename!")
            return "X", "X"

    # ----------------------------------------------------------------------------------------
    def calculate_realspace_offset(
        self,
        target_position: Sequence[int],
        well_centre: Sequence[int],
        scale_factor: Sequence[float],
    ) -> Optional[int]:
        if self.list_has_none(target_position) or self.list_has_none(well_centre):
            return None
        return np.rint(
            (np.array(target_position) - np.array(well_centre)) * np.array(scale_factor)
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
