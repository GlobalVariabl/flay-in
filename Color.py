from webcolors import name_to_hex, hex_to_rgb
from typing import Any, Dict


class BaseDronePrinter:
    """
    Base class for drone movement printing with color support.

    Provides core functionality for colorizing zone names using RGB/ANSI
    color codes. Subclasses should implement specific move formatting.

    Attributes
    ----------
    RESET : str
        ANSI escape code to reset terminal text formatting.
    all_color : dict
        Mapping of zone names to color names.
    hex_color : dict
        Mapping of zone names to hexadecimal color codes.
    """
    RESET: str = "\033[0m"

    def __init__(self, graph: Dict[str, Any]) -> None:
        """
        Initialize the drone printer with graph data.

        Parameters
        ----------
        graph : Dict[str, Any]
        Graph configuration containing 'hubs' with zone color information.
        """
        self.all_color: Dict[str, str] = self.get_zone_color(graph["hubs"])
        self.hex_color: Dict[str, str] = self.color_to_hex(self.all_color)

    @staticmethod
    def get_zone_color(hubs: Dict[str, Any]) -> dict[str, str]:
        """
        Extract color information for each zone from hubs data.

        Parameters
        ----------
        hubs : dict
            Dictionary containing zone configuration with color attributes.

        Returns
        -------
        Dict[str, str]
            Mapping of zone names to color names. Defaults to '#ffffff'
            for zones without color information.
        """
        all_color: Dict[str, str] = {}
        for zone in hubs:
            color_name: str = hubs[zone]["color"]
            if not color_name:
                all_color[zone] = "#ffffff"
            else:
                all_color[zone] = color_name.lower()
        return all_color

    @staticmethod
    def color_to_hex(colors: dict[str, str]) -> dict[str, str]:
        """
        Convert color names to hexadecimal color codes.

        Parameters
        ----------
        colors : dict
            Mapping of zone names to color names or hex values.

        Returns
        -------
        Dict[str, str]
            Mapping of zone names to hexadecimal color codes.
            Invalid colors default to '#ffffff'.

        """
        hex_color: Dict[str, str] = {}
        for zone, color_name in colors.items():
            try:
                hex_color[zone] = name_to_hex(color_name)
            except ValueError:
                hex_color[zone] = "#ffffff"
        return hex_color

    @staticmethod
    def hex_to_ansi_rgb(hex_color: str) -> str:
        """
        Convert hexadecimal color to ANSI RGB escape sequence.

        Parameters
        ----------
        hex_color : str
            Hexadecimal color code (e.g., '#ff0000').

        Returns
        -------
        str
            ANSI escape sequence for RGB foreground color.
        """
        rgb = hex_to_rgb(hex_color)
        return f"\033[38;2;{rgb.red};{rgb.green};{rgb.blue}m"

    def colorize(self, zone: str, text: str) -> str:
        """
        Apply color formatting to text based on zone color.

        Parameters
        ----------
        zone : str
            Zone name used to look up color configuration.
        text : str
            Text to be colorized.

        Returns
        -------
        str
            Text wrapped with ANSI color codes and reset sequence.
            Defaults to white (#ffffff) if zone color is not found.
        """
        hex_val: str = self.hex_color.get(zone, "#ffffff")
        ansi: str = self.hex_to_ansi_rgb(hex_val)
        return f"{ansi}{text}{self.RESET}"


class RestrictedMovePrinter(BaseDronePrinter):
    """
    Printer for restricted drone moves showing source and destination zones.

    Formats moves as 'D{id}-{from_zone}-{to_zone}' with both zones colorized
    according to their respective zone configurations.

    """
    def format_move(self, drone_id: int, zone: str) -> str:
        """
        Format a restricted move with both source and destination zones.

        Parameters
        ----------
        drone_id : int
            Unique identifier for the drone.
        zone : str
            Move string in format 'source-destination' (e.g., 'A-B').

        Returns
        -------
        str
            Formatted move string with colorized zone names.
        """
        from_zone, to_zone = zone.split("-")

        colored_from = self.colorize(from_zone, from_zone)
        colored_to = self.colorize(to_zone, to_zone)
        return f"D{drone_id}-{colored_from}-{colored_to}"


class SimpleMovePrinter(BaseDronePrinter):
    """
    Printer for simple drone moves showing only the destination zone.

    Formats moves as 'D{id}-{zone}' with the zone name colorized according
    to its configuration.

    """
    def format_move(self, drone_id: int, zone: str) -> str:
        """
        Format a simple move with only the destination zone.

        Parameters
        ----------
        drone_id : int
            Unique identifier for the drone.
        zone : str
            Destination zone name.

        Returns
        -------
        str
            Formatted move string with colorized zone name.
        """
        colored_to: str = self.colorize(zone, zone)
        return f"D{drone_id}-{colored_to}"
