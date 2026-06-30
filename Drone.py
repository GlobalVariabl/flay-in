from typing import Any, Optional


class Drone:
    """Represents a single drone."""

    def __init__(self, drones_id: int, graph: dict[str, Any]) -> None:
        """Initialize drone at start zone."""
        self.graph: dict[str, Any] = graph
        self.drones_id: int = drones_id
        self.location: str = graph["start_zone"]
        self.statue: str = "waiting"
        self.visit_zone: tuple = {self.location}

        self.wait_turns: int = 0
        self.rest_zone_landing: str = ""
        self.rest_zone_leaving: str = ""

    def get_next_bast_zone(self) -> Optional[str]:
        """
        Find the best next zone for a drone to move to.
        Returns the zone ID of the best move, or None if no move is available.
        """
        location: str = self.location
        best_zone: Optional[str] = None
        all_zones: list[Any] = self.graph["graph"][location]
        location_cost: float = self.graph["distances"][location][0]
        best_cost: float = float("inf")

        for edge in all_zones:
            next_zone: str = edge["to"]

            capacity_link = None
            holde_link = None
            for connection in self.graph["graph"][location]:
                if connection["to"] == next_zone:
                    capacity_link = connection["capacity"]
                    holde_link = connection["holde"]

            next_cost: float = self.graph["distances"][next_zone][0]

            if float(next_cost) > float(location_cost) or next_zone in self.visit_zone:
                continue

            next_zone_data: dict[str, Any] = self.graph["hubs"].get(
                next_zone, {}
            )

            current: int = next_zone_data.get("holde", 0)
            maximum: float = next_zone_data.get("max_drones", 1)
            zone_type = next_zone_data.get("zone", "normal")
            if current >= maximum:
                continue

            if capacity_link == holde_link:
                continue

            if next_cost < best_cost and zone_type == "priority":
                best_cost = next_cost
                best_zone = next_zone
            elif next_cost < best_cost and zone_type == "normal":
                best_cost = next_cost
                best_zone = next_zone
            elif next_cost < best_cost:
                best_cost = next_cost
                best_zone = next_zone

        return best_zone

    def move_to_next_zone(self, next_zone: str) -> None:
        """Move drone to next zone."""
        self.location = next_zone
        self.visit_zone.add(next_zone)
        if next_zone == self.graph["end_zone"]:
            self.statue = "DELIVERED"

    def get_state(self) -> dict[str, Any]:
        """Return current drone state."""
        return {
            "drones_id": self.drones_id,
            "statue": self.statue,
            "location": self.location,
        }
