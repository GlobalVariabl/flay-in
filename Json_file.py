import heapq
from typing import Any


class Json_file:
    graph: dict[str, Any] = dict()
    distances: dict[str, Any] = dict()

    def __init__(self, clean_data: dict[str, Any]) -> None:
        self.drones_number: int = clean_data["drones_number"]
        self.start_zone: dict[str, Any] = clean_data["start_zone"]
        self.end_zone: dict[str, Any] = clean_data["end_zone"]
        self.hub: list[dict[str, Any]] = clean_data["hub"]
        self.connection: list[dict[str, Any]] = clean_data["connection"]

    def grouping_in_graph(self) -> dict[str, Any]:
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
            # "state": "empty",
            "holde": self.drones_number,
        }
        Json_file.graph["hubs"][self.end_zone["name"]] = {
            "coordinate": self.end_zone["coordinate"],
            "zone": self.end_zone["zone"],
            "color": self.end_zone["color"],
            "max_drones": self.drones_number,
            # "state": "empty",
            "holde": 0,
        }
        for item in self.hub:
            Json_file.graph["hubs"][item["name"]] = {
                "coordinate": item["coordinate"],
                "zone": item["zone"],
                "color": item["color"],
                "max_drones": item["max_drones"],
                # "state": "empty",
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
                    # "state": "empty",
                    "holde": 0,
                }
            )
            Json_file.graph["graph"][items["to"]].append(
                {
                    "to": items["from"],
                    "capacity": items["max_link_capacity"],
                    # "state": "empty",
                    "holde": 0,
                }
            )

        Json_file.graph["distances"] = Json_file.distances_cost(
            Json_file.graph
        )
        return Json_file.graph

    @staticmethod
    def get_cost(zone_name: str) -> int:
        costs: dict[str, int] = {
            "normal": 1,
            "priority": 1,
            "restricted": 2,
            "blocked": 151,
        }
        return costs[zone_name]

    @staticmethod
    def distances_cost(graph: dict[str, Any]) -> dict[str, Any]:
        distances: dict[str, Any] = {
            zone: [float("inf"), zone] if zone != graph["end_zone"]
            else [0, zone]
            for zone in graph["hubs"]
        }
        goale: str = graph["end_zone"]
        heap_list: list[Any] = [distances[goale]]
        heapq.heapify(heap_list)
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

        is_valid_path: list[str] = []
        start: str = Json_file.graph["start_zone"]
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
            )

        return distances

    def get_data(self) -> dict[str, Any]:
        """Return parsed data as a dictionary."""
        return Json_file.graph
