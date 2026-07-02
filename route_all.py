import sys


if __name__ == "__main__":
    from Read_file import Read_file
    from RegEx_line import RegEx_line
    from Json_file import Json_file
    try:
        if len(sys.argv) != 2:
            print("Usage: python route_all.py ./diractory/<map.txt>")
        else:
            map_txt: str = sys.argv[1]
            reader: Read_file = Read_file(map_txt)
            parser: RegEx_line = RegEx_line(reader.get_data())
            Json_file(parser.get_data())
            json_file: Json_file = Json_file(parser.get_data())
            database: dict = json_file.grouping_in_graph()
            if database is None:
                exit()
            from Simulation import Simulation as Air_Traffic_Control
            Air_Traffic_Control(database)
    except Exception as e:
        print(f"Error: {e}")
