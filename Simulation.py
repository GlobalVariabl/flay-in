from typing import Any, Optional
from Drone import Drone
from Color import RestrictedMovePrinter, SimpleMovePrinter


class Simulation:
    """
    Manages turn-by-turn simulation of all drones.

    Drives the main simulation loop: each turn, every drone
    attempts to move toward the goal following the gradient field,
    subject to zone capacity and connection capacity constraints,
    until every drone has been delivered.

    Attributes
    ----------
    graph : dict[str, Any]
        Shared reference to the full simulation graph.
    turn : int
        Current turn number.
    goal : str
        Name of the end zone.
    track_drone : list[Drone]
        All drones participating in the simulation.
    """

    def __init__(self, graph: dict[str, Any]) -> None:
        """
        Initialize and immediately run the simulation.

        Parameters
        ----------
        graph : dict[str, Any]
            The fully assembled graph from Json_file, including
            hubs, adjacency list, and Dijkstra distances.
        """
        self.graph: dict[str, Any] = graph
        self.turn: int = 0
        self.goal: str = graph["end_zone"]
        self.track_drone: list[Drone] = []
        self.printer: RestrictedMovePrinter = RestrictedMovePrinter(graph)
        self.printes: SimpleMovePrinter = SimpleMovePrinter(graph)
        self.run()

    def all_delivered(self) -> bool:
        """
        Check whether every drone has reached the goal.

        Returns
        -------
        bool
            True if all drones have status "DELIVERED", False
            otherwise.
        """
        return all(drone.statue == "DELIVERED" for drone in self.track_drone)

    def run(self) -> None:
        """
        Run the simulation loop until all drones are delivered.

        Creates one Drone per unit in drones_number, then repeats
        the turn logic (move each drone, resolve zone/connection
        capacity, reset per-turn connection state, print progress)
        until all_delivered() is True.
        """

        for drone_id in range(1, self.graph["drones_number"] + 1):
            drone: Drone = Drone(drone_id, self.graph)
            paths: list[str] = self.graph.get("launch_paths", [])
            if paths:
                drone.forced_first = paths[(drone_id - 1) % len(paths)]
            else:
                drone.forced_first = ""
            self.track_drone.append(drone)

        while not self.all_delivered():

            move_track: list[tuple[int, str]] = []
            connection_idx: Optional[int] = None
            capacity_link: Optional[int] = None
            holde_link: Optional[int] = None

            for drone in self.track_drone:

                if drone.wait_turns > 0:
                    drone.wait_turns -= 1
                    drone.move_to_next_zone(drone.rest_zone_landing)
                    move_track.append(
                        (drone.drones_id, drone.rest_zone_landing)
                    )
                    continue

                if drone.statue == "DELIVERED":
                    continue

                zone: Optional[str] = drone.get_next_bast_zone()
                if zone is None:
                    continue

                zone_data: dict[str, Any] = self.graph["hubs"][zone]

                if zone_data.get("zone") == "blocked":
                    continue

                current_hold: int = zone_data.get("holde", 0)
                max_drones: int = zone_data.get("max_drones", 1)

                for idx, connection in enumerate(
                    self.graph["graph"][drone.location]
                ):
                    if connection["to"] == zone:
                        connection_idx = idx
                        capacity_link = connection["capacity"]
                        holde_link = connection["holde"]
                        break

                if capacity_link == holde_link:
                    continue

                if current_hold < max_drones:
                    leaving: str = drone.location
                    landing: str = zone
                else:
                    continue

                if leaving != self.graph["start_zone"]:
                    self.graph["hubs"][leaving]["holde"] -= 1

                self.graph["hubs"][landing]["holde"] += 1

                if connection_idx is not None:
                    self.graph["graph"][drone.location][connection_idx][
                        "holde"
                    ] += 1

                if zone_data.get("zone") == "restricted":
                    drone.wait_turns = 1
                    drone.rest_zone_landing = landing
                    drone.rest_zone_leaving = leaving
                    move_track.append(
                        (drone.drones_id, f"{leaving}-{landing}")
                    )
                else:
                    drone.move_to_next_zone(landing)
                    move_track.append((drone.drones_id, landing))

            for connection_zone in self.graph["graph"]:
                for holde in self.graph["graph"][connection_zone]:
                    holde["holde"] = 0
            if move_track:
                output: str = " ".join(
                    "  " + self.printer.format_move(did, zone) if "-" in zone
                    else "  " + self.printes.format_move(did, zone)
                    for did, zone in move_track
                )
                print(f"Turn {self.turn + 1}: {output}")

            self.turn += 1

        print(f"\nTotal turns: {self.turn}")
