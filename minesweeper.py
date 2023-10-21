import random
import time
import csv
import sys
import game_graphics


# state dictionary keys:
# "field": a 2-dimensional list describing the minefield
# "flags": the coordinates (x, y) of the flags placed on the field
# "opened": number of opened tiles
# "start_time": game start time
# "end": True when the game is over, otherwise False.

state = {

    "field": [],
    "flags": [],
    "opened": 0,
    "start_time": 0.0,
    "end": False,

}

statistics = {

    "date": "",
    "game_time": "",
    "result": "",
    "moves": 0,
    "field_size": "",
    "mine_count": 0

}


gui = game_graphics.MyGUI()


def save_statistics(filename):
    """
    Saves the game data from the statistics dictionary in 
    csv format to the file given as an argument.
    The dictionary keys correspond to the following information:
    "date": game start time in the format "year-month-day hours:minutes"
    "game_time": game duration in "hours:minutes:seconds" format
    "result": "Win" or "Lose"
    "moves:" the number of moves as an integer
    "field_size": field size as a string "widthxheight"
    "mine_count": the number of mines as an integer

    example: 2020-12-08 19:37,00:02:44,Win,26,15x15,15
    """

    data = [statistics["date"], statistics["game_time"], statistics["result"], statistics["moves"],
            statistics["field_size"], statistics["mine_count"]]

    try:
        with open(filename, 'a+', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)

    except IOError:
        print("Failed to open file")


def calculate_duration():
    """
    Calculates the duration of the game and adds it to the
    "statistics" dictionary to key "game_time" in the format "hours:minutes:seconds".
    """

    game_time = round(time.time() - state["start_time"])
    statistics["game_time"] = time.strftime("%H:%M:%S", time.gmtime(game_time))


def read_statistics_file(stats_file):
    """
    Reads the game statistics from the file given as an argument and prints it to the console.
    """

    try:
        with open(stats_file, newline="") as file:
            reader = csv.reader(file)

            for line in reader:
                print_statistics(line)

    except IOError:
        print("Failed to open file")


def print_statistics(line):
    """
    Formats and prints game statistics to the console.
    """

    try:
        date, game_time, win, moves, size, mines = line
        h, m, s = game_time.split(":")

    except ValueError:
        print("Failed to read line")
        return

    print(date + ",", end=" ")

    if h == '00':

        print("Game duration: {m}min {s}s,".format(

            m=m.lstrip("0").zfill(1),
            s=s.lstrip("0").zfill(1)),
            end=" ")
    else:

        print("Game duration: {h}h {m}min {s}s,".format(
            h=h.lstrip("0"),
            m=m.lstrip("0").zfill(1),
            s=s.lstrip("0").zfill(1)),
            end=" ")

    print("{},".format(win), end=" ")

    if moves == "1":
        print("{} move,".format(moves), end=" ")
    else:
        print("{} moves,".format(moves), end=" ")

    print("{} tiles, {} mines".format(size, mines))


def lower_limit(index):
    """
    Returns 0 if the index given as an argument is 0.
    In other cases returns index-1. 
    """

    if index == 0:
        limit = 0
    else:
        limit = index - 1
    return limit


def higher_limit(list_length, index):
    """
    Returns index+1, if the index given as an argument is the last index in the list.
    Otherwise returns index+2.
    """

    if index == (list_length - 1):
        limit = index + 1
    else:
        limit = index + 2
    return limit


def count_mines(x, y, field):
    """
    Counts the mines in the minefield that are diagonal or adjacent to 
    the tile indicated by the x and y coordinates 
    and returns their number.
    """

    mine_count = 0

    try:
        for i in range(lower_limit(y), higher_limit(len(field), y)):

            for j in range(lower_limit(x), higher_limit(len(field[0]), x)):

                if field[i][j] == 'x':

                    mine_count += 1

    except IndexError:
        pass

    return mine_count


def floodfill(x, y):
    """
    Reveals unopened tiles in the minefield using a flood-fill algorithmn.
    Filling starts from the given x, y point.
    Filling is stopped when the first tile with at least 1 surrounding mine is reached.
    """

    points = [(x, y)]
    field = state["field"]

    if field[y][x] == ' ':

        if count_mines(x, y, field) != 0:

            field[y][x] = str(count_mines(x, y, field))
            state["opened"] += 1
            return
        else:

            while points:

                try:
                    for n in range(lower_limit(y), higher_limit(len(field), y)):

                        for m in range(lower_limit(x), higher_limit(len(field[0]), x)):

                            if field[n][m] == ' ' and (m, n) not in state["flags"]:
                                state["opened"] += 1

                                if count_mines(m, n, field) == 0:
                                    field[n][m] = str(count_mines(m, n, field))
                                    points.append((m, n))
                                else:
                                    field[n][m] = str(count_mines(m, n, field))

                except IndexError:
                    pass
                else:
                    x = points[-1][0]
                    y = points[-1][1]
                    points.pop()


def handle_mouse(x, y, mouse_button, buttons):
    """
    This function is called when the user clicks the application window with the mouse. 
    Left clicking on the mouse opens a tile in the minefield. The right mouse button sets or removes a flag on the tile which the player has the mouse pointer on.
    """

    x = x // 40
    y = y // 40

    try:
        if not state["end"]:
            if mouse_button == gui.MOUSE_LEFT and (x, y) not in state["flags"]:

                if state["field"][y][x] == 'x':

                    statistics["moves"] += 1
                    calculate_duration()
                    statistics["result"] = "Lose"
                    state["end"] = True
                    save_statistics(file_name)  # pylint: disable=E0601

                elif state["field"][y][x] == ' ':
                    statistics["moves"] += 1
                    floodfill(x, y)

                    if (len(state["field"][0]) * len(state["field"])) - state["opened"] - statistics["mine_count"] == 0:
                        calculate_duration()
                        statistics["result"] = "Win"
                        state["end"] = True
                        save_statistics(file_name)

            elif mouse_button == gui.MOUSE_RIGHT:

                if state["field"][y][x] == 'x' or state["field"][y][x] == ' ':

                    if (x, y) not in state["flags"]:
                        state["flags"].append((x, y))
                    else:
                        state["flags"].remove((x, y))

        elif state["end"]:

            if mouse_button == gui.MOUSE_LEFT:
                gui.end()

    except IndexError:
        pass


def draw_field():
    """
    A handler function which draws the tiles for the minefield 
    onto the game window. 
    This function is called every time the game engine requests an update of the screen view.
    """

    gui.clear_window()

    for m, y in enumerate(state["field"]):

        for n, _ in enumerate(y):

            if (n, m) in state["flags"]:

                if state["end"] and state["field"][m][n] == "x":
                    gui.add_tile("x", n * 40, m * 40)
                else:
                    gui.add_tile("f", n * 40, m * 40)

            elif state["field"][m][n] == "x":

                if state["end"]:
                    gui.add_tile("x", n * 40, m * 40)
                else:
                    gui.add_tile(" ", n * 40, m * 40)

            elif state["field"][m][n] == " ":
                gui.add_tile(" ", n * 40, m * 40)
            else:
                gui.add_tile(state["field"][m][n], n * 40, m * 40)


    gui.draw_grid()

    gui.draw_text(("Mines left: {}".format(statistics["mine_count"] - len(state["flags"]))),

                 0, 40 * len(state["field"]), (0, 90, 210, 255), size=20)

    if state["end"]:
        if statistics["result"] == "Win":
            gui.draw_text(
                "You win!", 0, (40 * len(state["field"])) + 40, (0, 160, 100, 255), size=20)
        else:
            gui.draw_text("You hit a mine!", 0, (40 *
                                               len(state["field"])) + 40, (200, 0, 100, 255), size=20)

        gui.draw_text("Click anywhere to return to the menu",
                     0, 0, (20, 0, 100, 255), size=14)


def initialize_values():
    """
    Sets the initial values of the dictionaries used to save the game state and statistics.
    """

    statistics["date"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    statistics["moves"] = 0
    statistics["result"] = ""
    state["flags"].clear()
    state["opened"] = 0
    state["end"] = False
    state["start_time"] = time.time()


def add_mines(field, blank_tiles, mine_count):
    """
    Places mines on the field in random places.
    Arguments:
    field = 2-dimensional list
    free_boxes = elements of a 2-dimensional list as tuples (x, y)
    mine_count = the number of mines as an integer
    """

    mines = random.sample(blank_tiles, mine_count)

    for x_column, y_row in mines:

        field[y_row][x_column] = 'x'


def create_field():
    """
    Asks the user to input the width and height of the field and the number of mines. 
    Creates a minefield and stores it in the key "field" of the global dictionary "state".
    """

    field = []
    width = request_number("Minefield width: ", 3, 30)
    height = request_number("Minefield height: ", 3, 30)
    statistics["field_size"] = str(width) + "x" + str(height)

    while True:
        statistics["mine_count"] = request_number("Number of mines: ", 1, width * height)
        if statistics["mine_count"] > width * height:
            print("That's too many mines - there are {} tiles on the field".format(width * height))
        else:
            break

    for _ in range(height):

        field.append([])

        for _ in range(width):
            field[-1].append(" ")

    tiles = []

    for x in range(width):
        for y in range(height):

            tiles.append((x, y))

    add_mines(field, tiles, statistics["mine_count"])

    state["field"] = field


def request_number(question, min_number=1, max_number=sys.maxsize):
    """
    Asks the user the question given as an argument and returns the positive integer entered by the user.
    """

    while True:

        try:
            number = int(input(question))

            if number < min_number:
                print(f"The smallest number allowed is {min_number}")
                continue

            elif number > max_number:
                print(f"The largest number allowed is {max_number}")
                continue

        except ValueError:
            print(f"Please enter an integer between {min_number} and {max_number}")
        else:
            return number


def read_arguments(arguments):
    """
    Reads the command-line arguments and returns the latter of them.
    """

    if len(arguments) == 2:

        filename = arguments[1]

        return filename
    else:

        return None


def start_game():
    """
    Creates the game window including the game field, and sets a drawing handler in the game window. 
    Sets the initial values of the dictionaries used to save the game state and collect statistics.
    """

    global gui
    gui = game_graphics.MyGUI()

    create_field()

    gui.create_window((40 * len(state["field"][0])),
                     (40 * len(state["field"]))+80)

    gui.set_draw_handler(draw_field)
    gui.set_mouse_handler(handle_mouse)

    initialize_values()

    gui.start()


def main():
    """
    Prints the menu and reads the user's selection.
    """
    print("Minesweeper")

    while True:

        print("(N)ew game\n(S)tatistics\n(H)elp\n(Q)uit")

        selection = input("Enter your selection > ").strip().lower()

        if selection == "n":

            start_game()

        elif selection == "s":

            read_statistics_file(file_name)

        elif selection == "h":

            print("Instructions:\n"

                  "The goal of the game is to open all safe tiles and avoid mines.\n"
                  "Open a tile with the left mouse button.\n"
                  "Set or remove a flag with the right mouse button.\n"
                  "The number in the tile indicates the number of mines adjacent or diagonal to the tile.\n")

        elif selection == "q":

            break
        


if __name__ == "__main__":

    file_name = read_arguments(sys.argv)

    if file_name:

        try:

            gui.load_images("sprites")
            main()

        except KeyboardInterrupt:

            print("Program was interrupted")
    else:

        print("Start the game from the command line:")
        print("python minesweeper.py gamedata.txt")
