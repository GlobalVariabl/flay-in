from typing import Any, Optional


class Drone:
    """
    Represents a single drone moving through the zone graph.

    Each drone tracks its own location, and decides its
    next move each turn by following the precomputed Dijkstra
    gradient field stored in the shared graph.

    Attributes
    ----------
    graph : dict[str, Any]
        Shared reference to the full simulation graph.
    drones_id : int
        Unique identifier for this drone.
    location : str
        Name of the zone the drone currently occupies.
    statue : str
        Current status: "waiting", "moving", or "DELIVERED".
    wait_turns : int
        Number of additional turns the drone must wait (used for
        restricted zone crossings).
    rest_zone_landing : str
        Zone the drone will land in once wait_turns reaches zero.
    visit_zone : set[str]
        Set of zone names this drone has already passed through,
        used to prevent backtracking into previously visited zones.
    """

    def __init__(self, drones_id: int, graph: dict[str, Any]) -> None:
        """
        Initialize a drone at the start zone.

        Parameters
        ----------
        drones_id : int
            Unique identifier for this drone.
        graph : dict[str, Any]
            Shared reference to the full simulation graph.
        """
        self.graph: dict[str, Any] = graph
        self.drones_id: int = drones_id
        self.location: str = graph["start_zone"]
        self.statue: str = "waiting"
        self.visit_zone: set[str] = {self.location}

        self.wait_turns: int = 0
        self.rest_zone_landing: str = ""
        self.rest_zone_leaving: str = ""

        self.forced_first: str = ""

    def get_next_bast_zone(self) -> Optional[str]:
        """
        Find the best next zone for this drone to move to.

        Looks at every neighbor of the current location, skips
        zones already visited, zones with equal or higher gradient
        cost, and zones already at capacity, then picks the
        neighbor with the lowest cost.

        Returns
        -------
        Optional[str]
            The name of the best neighboring zone to move to, or
            None if no valid move is currently available.
        """
        location: str = self.location
        best_zone: Optional[str] = None
        all_zones: list[Any] = self.graph["graph"][location]
        location_cost: float = self.graph["distances"][location][0]
        best_cost: float = float("inf")
        best_load: float = float("inf")
        if self.forced_first:
            zone: str = self.forced_first
            self.forced_first = ""
            return zone
        for edge in all_zones:
            next_zone: str = edge["to"]
            capacity_link: Optional[int] = None
            holde_link: Optional[int] = None
            for connection in self.graph["graph"][location]:
                if connection["to"] == next_zone:
                    capacity_link = connection["capacity"]
                    holde_link = connection["holde"]

            next_cost: float = self.graph["distances"][next_zone][0]

            zont_type = self.graph["distances"][next_zone][1]
            if zont_type == self.graph["start_zone"]:
                continue

            cost_comparison: bool = float(next_cost) > float(location_cost)
            if cost_comparison or next_zone in self.visit_zone:
                continue

            next_zone_data: dict[str, Any] = (
                self.graph["hubs"].get(next_zone, {})
            )

            current: int = next_zone_data.get("holde", 0)
            maximum: int = next_zone_data.get("max_drones", 1)
            zone_type: str = next_zone_data.get("zone", "normal")
            if current >= maximum:
                continue

            if capacity_link == holde_link:
                continue

            if next_cost < best_cost:
                best_cost = next_cost
                best_zone = next_zone
                best_load = current

            elif next_cost == best_cost:
                if current < best_load:
                    best_zone = next_zone
                elif current == best_load and zone_type == "priority":
                    best_zone = next_zone
        return best_zone

    def move_to_next_zone(self, next_zone: str) -> None:
        """
        Move this drone to the given zone.

        Updates the drone's location, records the new zone in
        visited to prevent future backtracking, and marks the
        drone as delivered if the new zone is the end zone.

        Parameters
        ----------
        next_zone : str
            The zone to move into.
        """
        self.location = next_zone
        self.visit_zone.add(next_zone)
        if next_zone == self.graph["end_zone"]:
            self.statue = "DELIVERED"
