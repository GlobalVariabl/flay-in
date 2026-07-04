import heapq
from typing import Any


class Json_file:
    """
    Build the simulation graph and compute the Dijkstra gradient.

    Converts the parsed zone and connection data from RegEx_line
    into an adjacency-list graph annotated with state (holde,
    capacity, etc.), then runs a reverse Dijkstra from the end zone
    to compute every zone's distance to the goal.

    Attributes
    ----------
    graph : dict[str, Any]
        The full graph structure: drones_number, start_zone,
        end_zone, hubs, graph (adjacency list), and distances.
    distances : dict[str, Any]
        The Dijkstra distance table, mapping each zone name to
        [cost, next_hop_toward_goal].
    """
    graph: dict[str, Any] = dict()
    distances: dict[str, Any] = dict()

    def __init__(self, clean_data: dict[str, Any]) -> None:
        """
        Initialize with parsed data from RegEx_line.

        Parameters
        ----------
        clean_data : dict[str, Any]
            Dictionary from RegEx_line.get_data() containing
            drones_number, start_zone, end_zone, hub, and
            connection.
        """
        self.drones_number: int = clean_data["drones_number"]
        self.start_zone: dict[str, Any] = clean_data["start_zone"]
        self.end_zone: dict[str, Any] = clean_data["end_zone"]
        self.hub: list[dict[str, Any]] = clean_data["hub"]
        self.connection: list[dict[str, Any]] = clean_data["connection"]

    def grouping_in_graph(self) -> dict[str, Any]:
        """
        Build the adjacency-list graph from parsed zones/connections.

        Populates Json_file.graph with hubs (per-zone state) and
        graph (per-edge state), then computes the Dijkstra distance
        table via distances_cost.

        Returns
        -------
        dict[str, Any]
            The fully assembled graph, ready for Simulation.
        """
        Json_file.graph["drones_number"] = self.drones_number
        Json_file.graph["start_zone"] = self.start_zone["name"]
        Json_file.graph["end_zone"] = self.end_zone["name"]
        Json_file.graph["hubs"] = {}
        Json_file.graph["graph"] = {}
        Json_file.graph["distances"] = {}

        Json_file.graph["hubs"][self.start_zone["name"]] = {
            "coordinate": self.start_zone["coordinate"],
            "zone": self.start_zone["zone"],
            "color": self.start_zone["color"],
            "max_drones": self.start_zone["max_drones"],
            "holde": self.drones_number,
        }
        Json_file.graph["hubs"][self.end_zone["name"]] = {
            "coordinate": self.end_zone["coordinate"],
            "zone": self.end_zone["zone"],
            "color": self.end_zone["color"],
            "max_drones": self.drones_number,
            "holde": 0,
        }
        for item in self.hub:
            Json_file.graph["hubs"][item["name"]] = {
                "coordinate": item["coordinate"],
                "zone": item["zone"],
                "color": item["color"],
                "max_drones": item["max_drones"],
                "holde": 0,
            }

        for items in self.connection:
            if items["from"] not in Json_file.graph["graph"]:
                Json_file.graph["graph"][items["from"]] = []
            if items["to"] not in Json_file.graph["graph"]:
                Json_file.graph["graph"][items["to"]] = []

            Json_file.graph["graph"][items["from"]].append(
                {
                    "to": items["to"],
                    "capacity": items["max_link_capacity"],
                    "holde": 0,
                }
            )
            Json_file.graph["graph"][items["to"]].append(
                {
                    "to": items["from"],
                    "capacity": items["max_link_capacity"],
                    "holde": 0,
                }
            )

        Json_file.graph["distances"] = Json_file.distances_cost(
            Json_file.graph
        )
        return Json_file.graph

    @staticmethod
    def get_cost(zone_name: str) -> int:
        """
        Return the movement cost of a given zone type.

        Parameters
        ----------
        zone_name : str
            One of "normal", "priority", "restricted", or
            "blocked".

        Returns
        -------
        int
            The fixed cost associated with entering that zone
            type. Priority is cheapest, blocked is effectively
            impassable.
        """
        costs: dict[str, int] = {
            "normal": 1,
            "priority": 1,
            "restricted": 2,
            "blocked": 151,
        }
        return costs[zone_name]

    @staticmethod
    def distances_cost(graph: dict[str, Any]) -> dict[str, Any]:
        """
        Run a reverse Dijkstra from the end zone to build a
        gradient field.

        Every zone is assigned a cost representing the cheapest
        path to the end zone, plus the next hop on that path.
        Blocked zones are skipped entirely.

        Parameters
        ----------
        graph : dict[str, Any]
            The graph being built, must already contain "hubs",
            "graph", "start_zone", and "end_zone".

        Returns
        -------
        dict[str, Any]
            A dictionary mapping each zone name to
            [cost, next_hop_toward_goal].

        Raises
        ------
        ValueError
            If no path exists from the start zone to the end zone
            (e.g. all routes are cut off by blocked zones).
        """
        distances: dict[str, Any] = {
            zone: [float("inf"), zone] if zone != graph["end_zone"]
            else [0, zone]
            for zone in graph["hubs"]
        }
        goale: str = graph["end_zone"]
        heap_list: list[Any] = [distances[goale]]
        heapq.heapify(heap_list)
        max_num:  list[tuple[int, str]] = []
        while heap_list:
            current_cost, current = heapq.heappop(heap_list)
            for edge in graph["graph"][current]:
                neighbor: str = edge["to"]
                if Json_file.graph["hubs"][neighbor]["zone"] == "blocked":
                    continue
                zone_cost: int = Json_file.get_cost(
                    Json_file.graph["hubs"][neighbor]["zone"]
                )
                new_cost: int = zone_cost + current_cost
                if new_cost < distances[neighbor][0]:
                    distances[neighbor][0] = new_cost
                    distances[neighbor][1] = current
                    heapq.heappush(heap_list, (new_cost, neighbor))
                if neighbor == graph["start_zone"]:
                    max_num.append((new_cost, current))

        is_valid_path: list[str] = []
        start: str = Json_file.graph["start_zone"]
        max_num = [
            item for item in max_num
            if distances[item[1]][1] != start
        ]
        max_num.sort(key=lambda x: x[0], reverse=True)
        if max_num:
            distances[start][0] = max_num[0][0]
            distances[start][1] = max_num[0][1]
        max_num.sort(
            key=lambda x: Json_file.sort_path(graph["hubs"][x[1]]["zone"])
        )
        graph["launch_paths"] = [item[1] for item in max_num]
        while start != Json_file.graph["end_zone"]:
            if start != distances[start][1]:
                is_valid_path.append(distances[start][1])
                start = distances[start][1]
            else:
                break
        if Json_file.graph["end_zone"] not in is_valid_path:
            raise ValueError(
                f"No Path Found from {start} to {goale}"
                f" Check for: All blocked zones cutting all routes"
                f" OR unconnected graph"
            )
        return distances

    @staticmethod
    def sort_path(keys: str) -> int:
        """
        Return the movement cost of a given zone type.

        Parameters
        ----------
        keys : str
            One of "normal", "priority", "restricted", or
            "blocked".

        Returns
        -------
        int
            The fixed cost associated with entering that zone
            type. Priority is cheapest, blocked is effectively
            impassable.
        """
        zone_cost = {
            "normal": 2,
            "priority": 1,
            "restricted": 3,
            "blocked": 4,
        }
        return zone_cost[keys]
