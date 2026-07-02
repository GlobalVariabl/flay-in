from typing import Optional, Any


class Read_file:
    """
    Read and validate a drone simulation input file.

    Parses a raw text file line by line, validates its structure
    against the expected format (nb_drones, start_hub, end_hub, hub,
    connection sections), and exposes the parsed raw lines through
    class attributes and get_data().

    Attributes
    ----------
    n_drones : list[str | int]
        Parsed nb_drones line as [text, line_index].
    s_zone : list[str | int]
        Parsed start_hub line as [text, line_index].
    e_zone : list[str | int]
        Parsed end_hub line as [text, line_index].
    hub : list[list[str | int]]
        List of parsed hub lines, each as [text, line_index].
    connection : list[list[str | int]]
        List of parsed connection lines, each as [text, line_index].
    """

    n_drones: list[str | int] = []
    s_zone: list[str | int] = []
    e_zone: list[str | int] = []
    hub: list[list[str | int]] = []
    connection: list[list[str | int]] = []

    def __init__(self, file_name: str) -> None:
        """
        Initialize the reader and immediately parse the file.

        Parameters
        ----------
        file_name : str
            Path to the input file to read and validate.
        """
        self.file_name: str = file_name
        self.read_lines()

    def read_lines(self) -> None:
        """
        Read the file and validate/store each required section.

        Opens self.file_name, validates the overall line structure,
        then validates and stores each section (nb_drones, start_hub,
        end_hub, hub, connection) into the corresponding class
        attribute.

        Raises
        ------
        FileNotFoundError
            If self.file_name does not exist.
        ValueError
            If the file structure is invalid.
        """
        list_lines: list[str] = []

        with open(self.file_name, "r") as file:
            list_lines = file.readlines()
        Read_file.valid_garbage_line(list_lines)
        Read_file.valid_line_dron(list_lines)
        Read_file.valid_special_zone(list_lines, "start_hub")
        Read_file.valid_special_zone(list_lines, "end_hub")
        Read_file.valid_more_lines(list_lines, "hub")
        Read_file.valid_more_lines(list_lines, "connection")

        Read_file.n_drones = Read_file.valid_line_dron(list_lines)
        Read_file.s_zone = Read_file.valid_special_zone(
            list_lines, "start_hub"
        )
        Read_file.e_zone = Read_file.valid_special_zone(
            list_lines, "end_hub"
        )
        Read_file.hub = Read_file.valid_more_lines(list_lines, "hub")
        Read_file.connection = Read_file.valid_more_lines(
            list_lines, "connection"
        )

    @staticmethod
    def valid_line_dron(list_lines: list[str]) -> list[str | int]:
        """
        Validate the nb_drones line.

        Checks that nb_drones appears exactly once and that it is
        the first non-comment, non-empty line in the file.

        Parameters
        ----------
        list_lines : list[str]
            All raw lines read from the input file.

        Returns
        -------
        list[str | int]
            A two-item list [line_text, line_index] where line_text
            is the nb_drones line with any trailing comment removed,
            and line_index is its zero-based position in list_lines.

        Raises
        ------
        ValueError
            If the file has no non-comment lines, if nb_drones is
            missing, repeated, or not on the first non-comment line.
        """
        first_non_comment_line_index: Optional[int] = None
        line_dron: Optional[int] = None
        repet_dron: int = 0
        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            first_non_comment_line_index = idx
            break
        for idx, line in enumerate(list_lines):
            stripped = line.strip()
            if stripped.startswith("nb_drones"):
                repet_dron += 1
                line_dron = idx

        if first_non_comment_line_index is None:
            raise ValueError("The file contains no lines other "
                             "than comments, or it was empty.")
        if repet_dron == 0:
            raise ValueError("nb_drones was no in file")
        if line_dron is None:
            raise ValueError(f"{line_dron} was not found in file")
        if repet_dron >= 2:
            raise ValueError(
                f"nb_drones was repet {repet_dron} time,"
                f" last at line {line_dron + 1}"
            )
        if first_non_comment_line_index != line_dron:
            raise ValueError(
                f"nb_drones must be on the first non-comment line."
                f"Found at line {line_dron + 1}, but first non-comment"
                f" line is {first_non_comment_line_index + 1}"
            )
        raw_line: str = list_lines[line_dron].rstrip("\n")
        if "#" in raw_line:
            line_whith_comm: str = raw_line[raw_line.index("#"):]
            line_whith_no_comm: str = raw_line.replace(line_whith_comm, "")
        else:
            line_whith_no_comm = raw_line
        return [line_whith_no_comm, line_dron]

    @staticmethod
    def valid_special_zone(
        list_lines: list[str], special_zone: str
    ) -> list[str | int]:
        """
        Validate a unique section keyword (start_hub or end_hub).

        Checks that the given keyword (e.g. "start_hub", "end_hub")
        appears exactly once in the file.

        Parameters
        ----------
        list_lines : list[str]
            All raw lines read from the input file.
        special_zone : str
            The keyword to search for, e.g. "start_hub" or
            "end_hub".

        Returns
        -------
        list[str | int]
            A two-item list [line_text, line_index] where line_text
            is the matching line with any trailing comment removed,
            and line_index is its zero-based position in list_lines.

        Raises
        ------
        ValueError
            If special_zone is missing or appears more than once.
        """
        repet_time: int = 0
        line_idx: Optional[int] = None

        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith(special_zone):
                repet_time += 1
                line_idx = idx

        if repet_time == 0:
            raise ValueError(f"{special_zone} was not found in file")
        if line_idx is None:
            raise ValueError(f"{special_zone} was not found in file")
        if repet_time != 1:
            raise ValueError(
                f"{special_zone} was repet {repet_time} time,"
                f" last at line {line_idx + 1}"
            )

        raw_line: str = list_lines[line_idx].rstrip("\n")
        if "#" in raw_line:
            line_whith_comm: str = raw_line[raw_line.index("#"):]
            line_whith_no_comm: str = raw_line.replace(line_whith_comm, "")
        else:
            line_whith_no_comm = raw_line

        return [line_whith_no_comm, line_idx]

    @staticmethod
    def valid_more_lines(
        list_lines: list[str], line_word: str
    ) -> list[list[str | int]]:
        """
        Validate and collect all lines starting with a keyword.

        Used for repeatable sections like "hub" and "connection",
        where zero or more lines may share the same prefix.

        Parameters
        ----------
        list_lines : list[str]
            All raw lines read from the input file.
        line_word : str
            The keyword prefix to match, e.g. "hub" or "connection".

        Returns
        -------
        list[list[str | int]]
            A list of [line_text, line_index] pairs for every
            matching line, in file order. line_text has any
            trailing comment removed.

        Raises
        ------
        ValueError
            If no matching line is found and line_word is not
            "hub:" (hub sections may be empty).
        """
        repet_time: int = 0
        lists_word: list[list[str | int]] = []
        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith(line_word):
                raw_line: str = line.rstrip("\n")
                if "#" in raw_line:
                    line_whith_comm: str = raw_line[raw_line.index("#"):]
                    line_whith_no_comm: str = raw_line.replace(
                        line_whith_comm, ""
                    )
                else:
                    line_whith_no_comm = raw_line
                lists_word.append([line_whith_no_comm, idx])
                repet_time += 1
        if repet_time == 0 and line_word != "hub:":
            raise ValueError(f"No '{line_word}' found in file")

        return lists_word

    @staticmethod
    def valid_garbage_line(list_lines: list[str]) -> None:
        """
        Validate that every line starts with a known keyword.

        Every non-comment, non-empty line must begin with one of:
        nb_drones, start_hub, end_hub, hub, connection, and must
        contain a colon separating the keyword from its value.

        Parameters
        ----------
        list_lines : list[str]
            All raw lines read from the input file.

        Raises
        ------
        ValueError
            If a line is missing a colon, or starts with a keyword
            that is not one of the valid keywords.
        """
        valid_keywords: set[str] = {
            "nb_drones", "start_hub", "end_hub", "hub", "connection"
        }
        for idx, line in enumerate(list_lines):
            stripped: str = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if ":" not in stripped:
                raise ValueError(
                    f"Line {idx + 1}: Missing keyword ."
                    f" Expected format 'keyword: value'"
                )
            parts: list[str] = stripped.split(":")
            keyword: str = parts[0].strip() if parts else ""
            if keyword not in valid_keywords:
                raise ValueError(
                    f"The keyword: {keyword} is Invalid keyword"
                    f" for this file, Line {idx + 1}"
                )

    def get_data(self) -> dict[str, Any]:
        """
        Return all parsed file sections as a single dictionary.

        Returns
        -------
        dict[str, object]
            A dictionary with keys "drones_number", "start_zone",
            "end_zone", "hub", and "connection", mapping to the
            corresponding parsed class attributes.
        """
        return {
            "drones_number": self.n_drones,
            "start_zone": self.s_zone,
            "end_zone": self.e_zone,
            "hub": self.hub,
            "connection": self.connection,
        }
