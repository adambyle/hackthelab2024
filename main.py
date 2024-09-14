import requests

# API_KEY = "AE5A38575AAC40D8"
# API_KEY = "B2206439EF744BB9"
API_KEY = "E890A820F8EE4708"

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
    
    def surroundings():
        response = get(f"/rat/{maze_id}/surroundings")
        print("SURROUNDINGS:", response)
        return response
    
    # reset()

    map = Map(surroundings())

    cheese_gotten = False
    cheeses = []
    found_cheeses = 0
    exit_found = False

    while (not map.exhausted()) and not (found_cheeses == cheese_count and exit_found):
        moved = False

        def spot_handler():
            nonlocal found_cheeses, cheese_gotten, exit_found, cheeses
            if map.at.kind == "cheese":
                if cheese_gotten:
                    eaten = False
                    if any(cell.kind == "exit" for cell in map.cells):
                        end = next(cell for cell in map.cells if cell.kind == "exit")
                        distance = len(map.a_star(map.at, end))
                        if distance * 2 * 3 > 1500:
                            eaten = True
                            eat()
                    if not eaten:
                        cheeses.append(map.at)
                    map.at.kind = "open"
                else:
                    cheese_gotten = True
                    map.at.kind = "open"
                    grab()
                found_cheeses += 1
            elif map.at.kind == "exit":
                if cheese_gotten:
                    cheese_gotten = False
                    drop()
                exit_found = True

        cheese_direction = False
        for direction, neighbor in map.at.neighbors.items():
            if neighbor.kind == "cheese" and not neighbor.visited:
                data = move(direction)["cell"]
                map.move_to(direction, data)
                moved = True
                cheese_direction = True
                spot_handler()
                break
        
        if not cheese_direction:
            for direction, neighbor in map.at.neighbors.items():
                if not neighbor.visited:
                    data = move(direction)["cell"]
                    map.move_to(direction, data)
                    moved = True
                    spot_handler()
                    break
        
        if not moved:
            unvisited_paths = [
                map.a_star(map.at, cell)
                for cell in map.cells
                if not cell.visited
            ]
            path = min(unvisited_paths, key=len)
            steps = path_to_directions(list(path))
            for direction in steps:
                data = move(direction)["cell"]
                map.move_to(direction, data)
                spot_handler()

    
    end = next(cell for cell in map.cells if cell.kind == "exit")

    path_to_end = map.a_star(map.at, end)
    steps = path_to_directions(list(path_to_end))
    for direction in steps:
        data = move(direction)["cell"]
        map.move_to(direction, data)
    
    if cheese_gotten:
        drop()

    print("END FOUND")
    
    cheese_paths = [
        map.a_star(map.at, cheese)
        for cheese in cheeses
    ]
    viable_paths = [
        path for path in cheese_paths
        if len(path) * 3 * 2 < 2500
    ]

    print(len(cheeses), "Cheeses")
    print(len(cheese_paths), "Cheese Paths")
    print(len(viable_paths), "Viable Paths")

    for path in viable_paths:
        print("FINDING CHEESE")
        steps = list(path_to_directions(path))
        for direction in steps:
            data = move(direction)["cell"]
            map.move_to(direction, data)
        grab()

        print("CHEESE GOTTEN")

        path_to_end = map.a_star(map.at, end)
        steps = path_to_directions(list(path_to_end))
        for direction in steps:
            data = move(direction)["cell"]
            map.move_to(direction, data)
        drop()

        print("CHEESE DROPPED")
    exit()

class Cell:
    
    def __init__(self, y, x, kind):
        self.y = y
        self.x = x
        self.visited = False
        self.kind = kind
        self.neighbors = {}
    
    def __repr__(self):
        return f"Cell({self.y}, {self.x}, {self.kind}, {self.visited}, {self.neighbors})"

class Map:

    def __init__(self, data):
        self.traveled = []
        self.cells = []
        self.at = self.add_cell(0, 0, data)
        self.at.visited = True

    def __repr__(self):
        return f"Map({self.cells}, {self.at})"

    def exhausted(self):
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
        cell = self.cell(y, x)
        if cell is None:
            cell = Cell(y, x, data["type"].lower())
        self.cells.append(cell)

        directions = ["north", "east", "south", "west"]
        facing = self.traveled[-1] if len(self.traveled) else "north"
        facing_index = directions.index(facing)
        direction_data = [
            ("north", -1, 0),
            ("east", 0, 1),
            ("south", 1, 0),
            ("west", 0, -1),
        ]
        
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
        self.add_cell(self.at.y, self.at.x, data)
        self.traveled.append(direction)

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

index = 0

mazes = get("/mazes")
print(mazes)
maze = mazes[index]
maze_id = maze["id"]
cheese_count = maze["numberOfCheese"]
test_maze = mazes[index]["id"]
solve_maze(test_maze, cheese_count)
