import requests

# The first two keys are "sandbox" keys. The third is the "competition" key.
# Sandbox mazes could be reset and viewed online while the rat made its way
# through the maze. We had to solve competition mazes blindly, and we got only
# one try.
# API_KEY = "AE5A38575AAC40D8"
# API_KEY = "B2206439EF744BB9"
API_KEY = "E890A820F8EE4708"

CHEESE_DROP_VALUE = 2500
CHEESE_EAT_VALUE = 1000

def get(request, body=None):
    response = requests.get(
        f"http://api.milabs.xyz/v1/{request}",
        json=body,
        headers={"X-API-KEY": API_KEY})
    return response.json()

def post(request, body=None):
    response = requests.post(
        f"http://api.milabs.xyz/v1/{request}",
        json=body,
        headers={"X-API-KEY": API_KEY})
    return response.json()

def solve_maze(maze_id, cheese_count):

    def reset():
        body = {
            "mazeId": maze_id,
        }
        response = post("/rat/reset", body)
        print("RESET:", response)
        return response

    def drop():
        body = {
            "mazeId": maze_id
        }
        response = post("/rat/drop", body)
        print("DROP:", response)
        return response
    
    def eat():
        body = {
            "mazeId": maze_id
        }
        response = post("/rat/eat", body)
        print("EAT:", response)
        return response
    
    def exit():
        body = {
            "mazeId": maze_id
        }
        response = post("/rat/exit", body)
        print("EXIT:", response)
        return response
    
    def grab():
        body = {
            "mazeId": maze_id
        }
        response = post("/rat/grab", body)
        print("GRAB:", response)
        return response

    def move(direction):
        body = {
            "mazeId": maze_id,
            "direction": direction
        }
        response = post("/rat/move", body)
        print("MOVE:", response)
        return response
    
    # Moves will occur with two lines of code.
    # data = move(direction)["cell"]
    # map.move_to(direction, data)
    # This performs the move through the API, gets the data of the
    # destination cell, and updates the local map object with thew
    # new cell's data.
    
    def surroundings():
        response = get(f"/rat/{maze_id}/surroundings")
        print("SURROUNDINGS:", response)
        return response
    
    # The reset function may only be called on sandbox mazes.
    # reset()

    # Construct a map of the maze.
    # The starting information includes only the rat's starting cell
    # and its adjacent cells.
    map = Map(surroundings())

    # The rat traverses the maze until it encounters all cheese, but it
    # may only carry one cheese at a time.
    # This is not used in the cheese-retrieval phase.
    holding_cheese = False

    # Keep track of which cheeses were left behind to be collected later.
    cheeses = []

    # The number of cheeses that have been located. Compare to cheese_count.
    found_cheeses = 0

    # Whether the exit has been located.
    # This should have been a cell that is the exit, or None, since a search
    # for the exit is performed quite often.
    exit_found = False

    # The first phase of the traversal continues indefinitely until
    # one of the following conditions is met:
    # 1. All cells have been explored.
    # 2. The exit and all cheeses have been found.
    # Realistically, the second condition should be met first every time.
    while (not map.exhausted()) and not (found_cheeses == cheese_count and exit_found):
        unvisited_adjacent = False

        # These checks are performed every time the rat moves to a new cell
        # during this phase of the traversal.
        def spot_handler():
            nonlocal found_cheeses, holding_cheese, exit_found, cheeses

            if map.at.kind == "cheese":
                if holding_cheese:
                    # The rat encountered cheese but is already holding cheese.
                    # The rat must decide whether to eat the cheese.
                    eaten = False

                    # We're going to measure the distance from the cheese to the exit.
                    # Forget it if we haven't found the exit yet.
                    if any(cell.kind == "exit" for cell in map.cells):
                        end = next(cell for cell in map.cells if cell.kind == "exit")
                        distance = len(map.a_star(map.at, end))

                        # If the cheese is too far from the exit, it may be
                        # worthwhile to eat it now rather than come back
                        # for it later.
                        travel_cost = distance * 2 * 3
                        if travel_cost > CHEESE_DROP_VALUE - CHEESE_EAT_VALUE:
                            eaten = True
                            eat()
                    
                    # If we didn't eat the cheese, keep track of where it was.
                    if not eaten:
                        cheeses.append(map.at)
                else:
                    # We are not holding a cheese. Pick this one up; we'll drop
                    # it off when we find the exit.
                    holding_cheese = True
                    grab()

                # We don't want to try to interact with this cheese again,
                # at least not until we start making return trips.
                # We made a mistake here: the rat should be able to pick up
                # cheeses on its rounds if it managed to deposit it at an
                # exit (see below), but that is impossible because of this
                # line of code.
                map.at.kind = "open"
                found_cheeses += 1
            
            elif map.at.kind == "exit":
                # We found the exit. Drop the cheese if we're holding one.
                if holding_cheese:
                    holding_cheese = False
                    drop()
                exit_found = True

        # Whether an adjacent cell was found that has cheese. In
        # hindsight, we should have also checked for the exit cell.
        cheese_adjacent = False
        for direction, neighbor in map.at.neighbors.items():
            if neighbor.kind == "cheese" and not neighbor.visited:
                data = move(direction)["cell"]
                map.move_to(direction, data)
                unvisited_adjacent = True
                cheese_adjacent = True
                spot_handler()
                break
        
        # If we did not find an adjacent cheese cell, move to the
        # first unvisited adjacent cell.
        if not cheese_adjacent:
            for direction, neighbor in map.at.neighbors.items():
                if not neighbor.visited:
                    data = move(direction)["cell"]
                    map.move_to(direction, data)
                    unvisited_adjacent = True
                    spot_handler()
                    break
        
        # If there are no unvisited adjacent cells, we need to backtrack.
        if not unvisited_adjacent:
            # Find paths to unvisited cells and choose to follow the shortest one.
            unvisited_paths = [
                map.a_star(map.at, cell)
                for cell in map.cells
                if not cell.visited
            ]
            cheese_path = min(unvisited_paths, key=len)
            steps = path_to_directions(list(cheese_path))
            for direction in steps:
                data = move(direction)["cell"]
                map.move_to(direction, data)
                spot_handler()

    
    # Now that the locations of the exit cell and all the cheeses are known,
    # find the path to the exit. This is most efficient when the rat is
    # carrying a cheese (it almost always should be). Otherwise, this is
    # inefficient.
    end = next(cell for cell in map.cells if cell.kind == "exit")
    path_to_end = map.a_star(map.at, end)
    steps = path_to_directions(list(path_to_end))
    for direction in steps:
        data = move(direction)["cell"]
        map.move_to(direction, data)
    if holding_cheese:
        drop()

    # The rat must retrieve the cheeses. Only go after cheeses that
    # would net positive points.
    cheese_paths = [
        map.a_star(map.at, cheese)
        for cheese in cheeses
    ]
    travel_cost = lambda path: len(path) * 3 * 2
    viable_paths = [
        path for path in cheese_paths
        if travel_cost(path) < CHEESE_DROP_VALUE
    ]

    for cheese_path in viable_paths:
        steps = list(path_to_directions(cheese_path))
        for direction in steps:
            data = move(direction)["cell"]
            map.move_to(direction, data)
        grab()

        path_to_end = map.a_star(map.at, end)
        steps = path_to_directions(list(path_to_end))
        for direction in steps:
            data = move(direction)["cell"]
            map.move_to(direction, data)
        drop()

    exit()

class Cell:
    
    def __init__(self, y, x, kind):
        self.y = y
        self.x = x
        self.visited = False

        # One of "start", "end", "wall", "open", or "cheese".
        self.kind = kind
        
        # A mapping of cardinal directions to Cell objects.
        self.neighbors = {}
    
    def __repr__(self):
        return f"Cell({self.y}, {self.x}, {self.kind}, {self.visited}, {self.neighbors})"

class Map:

    def __init__(self, data):
        # A list of Cell objects from the start of the maze.
        # This used to be a stack, to enable backtracking when a dead end
        # was reached. This was replaced with pathfinding later.
        self.traveled = []

        # An ordered list of all Cells in the maze.
        self.cells = []

        # The Cell the rat is at.
        self.at = self.add_cell(0, 0, data)
        self.at.visited = True

    def __repr__(self):
        return f"Map({self.cells}, {self.at})"

    def exhausted(self):
        # If there are no unvisited cells, we've exhausted the maze.
        return not any(not cell.visited for cell in self.cells)
    
    def cell(self, y, x):
        try:
            return next(cell for cell in self.cells if cell.x == x and cell.y == y)
        except StopIteration:
            return None
    
    def neighbor(self, y, x, direction):
        delta = {
            "north": (-1, 0),
            "east": (0, 1),
            "south": (1, 0),
            "west": (0, -1),
        }
        y_delta, x_delta = delta[direction]
        return self.cell(y + y_delta, x + x_delta)
    
    def add_cell(self, y, x, data):
        # Allow for redundant calls of add_cell. Update the existing cell
        # if possible.
        cell = self.cell(y, x)
        if cell is None:
            cell = Cell(y, x, data["type"].lower())
        self.cells.append(cell)

        # Get the direction the rat is currently facing using the backtracking stack.
        directions = ["north", "east", "south", "west"]
        facing = self.traveled[-1] if len(self.traveled) else "north"
        facing_index = directions.index(facing)
        direction_data = [
            ("north", -1, 0),
            ("east", 0, 1),
            ("south", 1, 0),
            ("west", 0, -1),
        ]
        
        # For each direction, starting to the left of face, get info for the
        # neighboring cell.
        for i in range(4):
            index = (i + facing_index - 1) % 4
            direction, y_delta, x_delta = direction_data[index]

            neighbor_kind = data["surroundings"][direction].lower()
            if neighbor_kind == "wall":
                continue

            new_y = y + y_delta
            new_x = x + x_delta
            neighbor = self.cell(new_y, new_x)
            if neighbor is None:
                neighbor = Cell(new_y, new_x, neighbor_kind)
                self.cells.append(neighbor)
            cell.neighbors[direction] = neighbor

        return cell
    
    def move_to(self, direction, data):
        self.at = self.neighbor(self.at.y, self.at.x, direction)
        self.at.visited = True

        # Even though the Cell exists in the Map structure, we need to get
        # data on its neighbors.
        self.add_cell(self.at.y, self.at.x, data)
        self.traveled.append(direction)

    # Implementation of A* from https://en.wikipedia.org/wiki/A*_search_algorithm
    # using only the cells that have been discovered by the rat.
    def a_star(self, start: Cell, end: Cell):

        def path(came_from, current):
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        def heuristic(a: Cell, b: Cell):
            return abs(a.x - b.x) + abs(a.y - b.y)
        
        open_set = [start]
        came_from = {}
        g_score = {cell: float("inf") for cell in self.cells}
        g_score[start] = 0
        f_score = {cell: float("inf") for cell in self.cells}
        f_score[start] = heuristic(start, end)

        while len(open_set):
            current = min(open_set, key=lambda cell: f_score[cell])

            if current == end:
                return path(came_from, current)
            
            open_set.remove(current)

            for neighbor in current.neighbors.values():
                tentative_g_score = g_score[current] + 1

                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    if neighbor not in open_set:
                        open_set.append(neighbor)
        
        raise ValueError("No path found")

# Converts a list of cells to a list of cardinal directions
# that will order the rat from the first cell to the last one.
def path_to_directions(cells: list[Cell]):
    for i in range(len(cells) - 1):
        start = cells[i]
        end = cells[i + 1]

        y_delta, x_delta = end.y - start.y, end.x - start.x
        if y_delta < 0:
            yield "north"
        elif y_delta > 0:
            yield "south"
        elif x_delta > 0:
            yield "east"
        elif x_delta < 0:
            yield "west"

# This index is updated to any number 0-9 by hand to run the respective maze.
# We wanted to monitor each run instead of run all at once.
index = 0

mazes = get("/mazes")
maze = mazes[index]
maze_id = maze["id"]
cheese_count = maze["numberOfCheese"]
test_maze = mazes[index]["id"]
solve_maze(test_maze, cheese_count)
