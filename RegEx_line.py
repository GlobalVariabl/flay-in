import re
from typing import Any, Optional


class RegEx_line:
    """
    Parse and validate drone simulation file lines.

    Takes the raw line groups produced by Read_file and converts
    each one into structured data using regular expressions,
    validating format, zone types, metadata, and connection rules
    along the way.

    Attributes
    ----------
    hubs : list[dict[str, Any]]
        Parsed hub records (name, coordinate, zone, color,
        max_drones) accumulated across all RegEx_line instances.
    connections : list[dict[str, Any]]
        Parsed connection records (from, to, max_link_capacity)
        accumulated across all RegEx_line instances.
    """

    hubs: list[dict[str, Any]] = []
    connections: list[dict[str, Any]] = []

    def __init__(self, read_file_dict: dict[str, Any]) -> None:
        """
        Initialize with parsed dictionary from Read_file.

        Parameters
        ----------
        read_file_dict : dict[str, Any]
            Dictionary from Read_file.get_data() containing the raw
            parsed lines for drones_number, start_zone, end_zone,
            hub, and connection.
        """
        self.drones_number: Any = read_file_dict["drones_number"]
        self.start_zone: list[Any] = read_file_dict["start_zone"]
        self.end_zone: list[Any] = read_file_dict["end_zone"]
        self.hub: list[Any] = read_file_dict["hub"]
        self.connection: list[Any] = read_file_dict["connection"]
        self.parsed_alls: list[Any] = []
        self.validit_all()

    def validit_all(self) -> None:
        """
        Validate and parse all sections.

        Populates parsed_alls, the start/end zone dicts, the class
        level hubs and connections lists, and validates that all
        connections reference defined zones and that the end zone
        is reachable.

        Raises
        ------
        ValueError
            If any line is invalid, a zone is blocked when it
            should not be, or the connection graph is malformed.
        """

        self.drones_number = RegEx_line.validit_drones(
            self.drones_number[0], self.drones_number[1] + 1
        )
        self.parsed_alls.append({"drones_number": self.drones_number})

        self.start_zone[0] = RegEx_line.validit_hub_sd(
            self.start_zone[0].split(":", 1)[1].strip(),
            True, self.start_zone[1] + 1
        )
        self.parsed_alls.append(self.start_zone)

        self.end_zone[0] = RegEx_line.validit_hub_sd(
            self.end_zone[0].split(":", 1)[1].strip(),
            True, self.end_zone[1] + 1
        )
        self.parsed_alls.append(self.end_zone)

        if self.start_zone[0]["zone"] == "blocked":
            raise ValueError(
                f"The start zone: {self.start_zone[0]['name']}"
                f" is Inaccessible zone ,line {self.start_zone[1] + 1}"
            )
        if self.end_zone[0]["zone"] == "blocked":
            raise ValueError(
                f"The End zone: {self.end_zone[0]['name']}"
                f" is Inaccessible zone ,line {self.start_zone[1] + 1}"
            )
        for idx, line in enumerate(self.hub):
            self.hub[idx][0] = RegEx_line.validit_hub_sd(
                line[0].split(":", 1)[1], False, line[1] + 1
            )
            self.parsed_alls.append(self.hub[idx])
            RegEx_line.hubs.append(self.hub[idx][0])
        for idx, line in enumerate(self.connection):
            self.connection[idx][0] = RegEx_line.validate_connection(
                line[0].split(":", 1)[1].strip(), line[1] + 1
            )
            self.parsed_alls.append(self.connection[idx])
            RegEx_line.connections.append(self.connection[idx][0])

        RegEx_line.validate_connection_link(self.parsed_alls[1:])

    def get_data(self) -> dict[str, Any]:
        """
        Return parsed data as a dictionary.

        Returns
        -------
        dict[str, Any]
            A dictionary with keys "drones_number", "start_zone",
            "end_zone", "hub", and "connection", ready to be passed
            to Json_file.
        """
        return {
            "drones_number": self.drones_number,
            "start_zone": self.start_zone[0],
            "end_zone": self.end_zone[0],
            "hub": self.hubs,
            "connection": self.connections,
        }

    @staticmethod
    def validit_drones(line: str, indx: int) -> int:
        """
        Parse and validate the nb_drones line.

        Parameters
        ----------
        line : str
            The raw nb_drones line, e.g. "nb_drones: 5".

        Returns
        -------
        int
            The validated number of drones.

        Raises
        ------
        ValueError
            If the line does not match the expected format or the
            value is less than 1.
        """
        drones: Optional[int] = None
        patten = re.match(r"^nb_drones\s*:\s*(\d+)\s*$", line.strip())
        if not patten:
            raise ValueError(f"Invalid line nb_drones : {line},"
                             f"line at {indx}")
        drones = int(patten.group(1))
        if drones < 1:
            raise ValueError("nb_drones must be greater than 0")
        return drones

    @staticmethod
    def validit_hub_sd(line: str,
                       ist_special: bool, indx: int) -> dict[str, Any]:
        """
        Parse and validate a hub/start_hub/end_hub line.

        Extracts name, coordinates, and optional metadata
        (zone, color, max_drones) from the line.

        Parameters
        ----------
        line : str
            The hub line content after the keyword, e.g.
            "start 0 3 [color=green max_drones=4]".
        ist_special : bool
            True if this is a start_hub or end_hub line, which
            changes the default max_drones value.

        Returns
        -------
        dict[str, Any]
            A dictionary with keys "name", "coordinate", "zone",
            "color", and "max_drones".

        Raises
        ------
        ValueError
            If the line format is invalid, the zone name contains
            a dash, metadata keys/values are invalid or duplicated,
            or there is unexpected trailing text in the metadata.
        """
        pattern = re.compile(
            r"^(?P<name>[^\s\-]+)\s+"
            r"(?P<x>-?\d+)\s+"
            r"(?P<y>-?\d+)"
            r"(?:\s*\[(?P<metadata>[^\]]*)\])?$"
        )
        meta_pattern = re.compile(r"(zone|color|max_drones)=([^\s]+)")
        valid_zones: set[str] = {"normal", "blocked", "restricted", "priority"}
        valid_keys: set[str] = {"zone", "color", "max_drones"}
        defaults: dict[str, Any] = {
            "zone": "normal",
            "color": None,
            "max_drones": float("inf") if ist_special else 1,
        }
        match = pattern.match(line.strip())
        if not match:
            raise ValueError(
                f"Invalid hub line format: '{line.strip()}' line at {indx}"
            )

        data: dict[str, Any] = match.groupdict()
        name: str = data["name"]
        if "-" in name:
            raise ValueError(
                f"Zone name '{name}' cannot contain dashes. "
                f"Dashes are reserved for connection syntax, line at {indx}"
            )
        metadata: Optional[str] = data.get("metadata")
        if metadata is not None:

            metadata = metadata.strip()
            key_value_pattern = re.compile(r"(\w+)=([^\s\]]+)")
            all_pairs: list[tuple[str, str]] = (
                key_value_pattern.findall(metadata)
            )
            valid_key_repet: dict[str, str] = dict()
            cleaned: str = metadata
            for key, value in all_pairs:
                if key not in valid_keys:
                    raise ValueError(
                        f"Invalid metadata key '{key}' in line: '{line}'."
                        f" line at {indx}"
                    )
                if key in valid_key_repet:
                    raise ValueError(
                        f"Duplicate metadata key '{key}' in line: '{line}'."
                        f" line at {indx}"
                    )

                if key == "max_drones":
                    if not re.match(r"^[0-9][0-9]*$", value):
                        raise ValueError(
                            f"Invalid max_drones value '{value}'"
                            f" in line: '{line}'."
                            f" Must be a positive integer, line at {indx}"
                        )
                else:
                    if not re.match(r"^[a-zA-Z\-]+$", value):
                        raise ValueError(
                            f"Invalid value '{value}' for key"
                            f" '{key}' in line: '{line}'. , line at {indx}"
                        )
                valid_key_repet[key] = value
                cleaned = cleaned.replace(f"{key}={value}", "")

            if cleaned:
                cleaned = " ".join(cleaned.split())
                if cleaned:
                    raise ValueError(
                        f"Invalid metadata format: '{metadata}'"
                        f" in line: '{line.strip()}'. "
                        f"Unexpected text: '{cleaned}', line at {indx}"
                    )

            for key, value in meta_pattern.findall(metadata):
                if key == "zone":
                    if value not in valid_zones:
                        raise ValueError(
                            f"Invalid zone type '{value}'"
                            f" in line: '{line}'., line at {indx}"
                        )
                    defaults["zone"] = value
                if key == "color":
                    defaults["color"] = value
                if key == "max_drones":
                    if ist_special:
                        continue
                    if not value.isdigit() or int(value) <= 0:
                        raise ValueError(
                            f"Invalid max_drones '{value}' , line at {indx}"
                            f" '{line}'. Must be positive integer"
                        )
                    defaults["max_drones"] = int(value)

        result: dict[str, Any] = {
            "name": data["name"],
            "coordinate": (int(data["x"]), int(data["y"])),
            "zone": defaults["zone"],
            "color": defaults["color"],
            "max_drones": defaults["max_drones"],
        }
        return result

    @staticmethod
    def validate_connection(line: str, indx: int) -> dict[str, Any]:
        """
        Parse and validate a connection line.

        Extracts from_hub, to_hub, and the optional
        max_link_capacity from a connection line.

        Parameters
        ----------
        line : str
            The connection line content after the keyword, e.g.
            "start-A [max_link_capacity=2]".

        Returns
        -------
        dict[str, Any]
            A dictionary with keys "from", "to", and
            "max_link_capacity".

        Raises
        ------
        ValueError
            If the line format is invalid, either zone name is
            empty, the zone connects to itself, or capacity is not
            a positive integer.
        """
        connection_pattern = re.compile(
            r"^(?P<from_hub>[^\s\-]+)"
            r"-"
            r"(?P<to_hub>[^\s\-]+)"
            r"(?:\s*\[\s*(?:max_link_capacity\s*=\s*"
            r"(?P<capacity>\d+))?\s*\])?\s*$"
        )
        defaults: dict[str, int] = {"max_link_capacity": 1}
        connections = connection_pattern.match(line.strip())
        if not connections:
            raise ValueError(
                f"Invalid connections line format: '{line}'"
                f" Expected '<from>-<to> [max_link_capacity=N]',"
                f"line at {indx}"
            )
        data: dict[str, Any] = connections.groupdict()
        from_hub: str = data["from_hub"]
        to_hub: str = data["to_hub"]
        capacity: Optional[str] = data["capacity"]

        if not from_hub or not to_hub:
            raise ValueError(f"Empty zone name in connection: '{line}',"
                             f"line at {indx}")
        if from_hub == to_hub:
            raise ValueError(
                f"Zone cannot connect to itself: '{line}', line at {indx} !?"
            )

        if capacity:
            capacity_int: int = int(capacity)
            if capacity_int <= 0:
                raise ValueError(
                    f"max_link_capacity must be positive,"
                    f" got {capacity_int} in: '{line}', line at {indx}"
                )
            defaults["max_link_capacity"] = capacity_int

        result: dict[str, Any] = {
            "from": from_hub,
            "to": to_hub,
            "max_link_capacity": defaults["max_link_capacity"],
        }
        return result

    @staticmethod
    def validate_connection_link(list_line: list[Any]) -> None:
        """
        Validate the connection graph as a whole.

        Checks for duplicate zone names/coordinates, connections
        referencing undefined zones, duplicate connections, and
        that the goal zone is reachable through at least one
        connection.

        Parameters
        ----------
        list_line : list[Any]
            All parsed zone and connection entries (excluding
            drones_number), each as [data_dict, line_index].

        Raises
        ------
        ValueError
            If a zone name or coordinate is repeated, a connection
            references an undefined zone, a connection is
            duplicated, or the goal zone has no connection.
        """
        goal: str = list_line[1][0]["name"]
        goal_connected: bool = False
        list_line.sort(key=lambda x: x[1])
        set_name: set[str] = set()
        set_coordinate: set[tuple[int, int]] = set()
        set_connection: set[tuple[str, str]] = set()
        for lines in list_line:
            line: dict[str, Any] = lines[0]
            if "name" in line:
                if line["name"] not in set_name:
                    set_name.add(line["name"])
                else:
                    raise ValueError(
                        f"the {line['name']} is repetition"
                        f" in line {lines[1]+1}"
                    )
                if line["coordinate"] not in set_coordinate:
                    set_coordinate.add(line["coordinate"])
                else:
                    raise ValueError(
                        f"the {line['coordinate']} is repetition"
                        f"  in line {lines[1]+1}"
                    )
            elif "from" in line:
                if line["from"] not in set_name:
                    raise ValueError(
                        f"the '{line['from']}' is not defined,"
                        f" Connections must link only previously"
                        f" defined zones  in line {lines[1]+1} ??"
                    )
                if line["to"] not in set_name:
                    raise ValueError(
                        f"the '{line['to']}' is not defined,"
                        f" Connections must link only previously"
                        f" defined zones  in line {lines[1]+1} ??"
                    )
                else:
                    connection: tuple[str, str] = tuple(
                        sorted([line["from"], line["to"]])
                    )
                    if connection not in set_connection:
                        set_connection.add(connection)
                    else:
                        raise ValueError(
                            f"The same connection must not appear"
                            f" more than once {connection} is"
                            f" repetition  in line {lines[1]+1}"
                        )

        for connection in set_connection:
            if goal in connection:
                goal_connected = True
        if not goal_connected:
            raise ValueError(
                f"The is no {goal} in connection so connection"
                f" is not full connect to end zone '{goal}'"
            )
