import webcolors

class BaseDronePrinter:
    RESET: str = "\033[0m"
    
    def __init__(self, graph: dict) -> None:
        self.all_color: dict = self.get_zone_color(graph["hubs"])
        self.hex_color: dict = self.color_to_hex(self.all_color)
    
    @staticmethod
    def get_zone_color(hubs: dict) -> dict:
        all_color: dict = {}
        for zone in hubs:
            color_name: str = hubs[zone]['color']
            all_color[zone] = color_name.lower()
        return all_color
    
    @staticmethod
    def color_to_hex(colors: dict) -> dict:
        hex_color: dict = {}
        for zone, color_name in colors.items():
            try:
                hex_color[zone] = webcolors.name_to_hex(color_name)
            except ValueError:
                hex_color[zone] = "#ffffff"
        return hex_color
    
    @staticmethod
    def hex_to_ansi_rgb(hex_color: str) -> str:
        rgb = webcolors.hex_to_rgb(hex_color)
        return f"\033[38;2;{rgb.red};{rgb.green};{rgb.blue}m"
    
    def colorize(self, zone: str, text: str) -> str:
        hex_val: str = self.hex_color.get(zone, "#ffffff")
        ansi: str = self.hex_to_ansi_rgb(hex_val)
        return f"{ansi}{text}{self.RESET}"
    
    def format_move(self, drone_id: int, zone: str) -> str:
        raise NotImplementedError

class RestrictedMovePrinter(BaseDronePrinter):
    def format_move(self, drone_id: int, zone: str) -> str:
        from_zone, to_zone = zone.split("-")

        colored_from = self.colorize(from_zone, from_zone)
        colored_to = self.colorize(to_zone, to_zone)
        return f"D{drone_id}-{colored_from}-{colored_to}"

class SimpleMovePrinter(BaseDronePrinter):
    def format_move(self, drone_id: int, zone: str) -> str:
        colored_to: str = self.colorize(zone, zone)
        return f"D{drone_id}-{colored_to}"



# hubs = {
#     'start': {'color': 'Grey'}, 
#     'end': {'color': 'Mahogany'}, 
#     'a': {'color': 'Coral'}, 
#     'b': {'color': 'red'}, 
#     'c': {'color': 'blue'}, 
#     'j': {'color': 'red'}, 
#     'd': {'color': 'orange'}, 
#     'e': {'color': 'red'}, 
#     'f': {'color': 'reld'}, 
# }


# # Run the code
# if __name__ == "__main__":
#     graph = {"hubs": hubs}
#     printer = RestrictedMovePrinter(graph)
#     printes = SimpleMovePrinter(graph)
    
#     # Test with different moves
#     print(printer.format_move(1, "c-e"))
#     print(printer.format_move(2, "a-d"))
#     print(printes.format_move(3, "end"))
