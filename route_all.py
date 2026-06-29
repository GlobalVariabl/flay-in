
if __name__ == "__main__":
    from Read_file import Read_file
    from RegEx_line import RegEx_line
    from Json_file import Json_file
    try:
        reader = Read_file("test.txt")
        parser = RegEx_line(reader.get_data())
        Json_file(parser.get_data())
        json_file = Json_file(parser.get_data())
        database = json_file.grouping_in_graph()
        # print(database)
        if database is None:
            exit()
        from Simulation import Simulation as Air_Traffic_Control
        run = Air_Traffic_Control(database)
    except Exception as e:
        print(f"Error: {e}")
