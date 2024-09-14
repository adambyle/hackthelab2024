import requests, json

SANDBOX_KEY = "AE5A38575AAC40D8"

def get(request, body=None):
    response = requests.get(
        f"http://api.milabs.xyz/v1/{request}",
        json=body,
        headers={"X-API-KEY": SANDBOX_KEY})
    return response.json()

def post(request, body=None):
    response = requests.post(
        f"http://api.milabs.xyz/v1/{request}",
        json=body,
        headers={"X-API-KEY": SANDBOX_KEY})
    return response.json()

def solve_maze(maze_id):

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

    def smell():
        body = {
            "mazeId": maze_id
        }
        response = post("/rat/smell", body)
        print("SMELL:", response)
        return response["distance"]
    
    def surroundings():
        response = get(f"/rat/{maze_id}/surroundings")
        print("SURROUNDINGS:", response)
        return response
    
    reset()

    map = Map(surroundings())

    eat_mode = False
    cheese_gotten = False
    cheeses = []

    while not map.exhausted():
        moved = False
        for direction, neighbor in map.at.neighbors.items():
            if not neighbor.visited:
                data = move(direction)["cell"]
                map.move_to(direction, data)
                moved = True
                if eat_mode:
                    if map.at.kind == "cheese":
                        if cheese_gotten:
                            eat()
                        else:
                            cheese_gotten = True
                            map.at.kind = "open"
                            grab()
                else:
                    if cheese_gotten:
                        cheeses.append(map.at)
                    else:
                        cheese_gotten = True
                        map.at.kind = "open"
                        grab()
                break
        if not moved:
            unvisited_paths = [
                map.a_star(map.at, cell)
                for cell in map.cells
                if not cell.visited
            ]
            path = min(unvisited_paths, key=lambda path: len(path))
            steps = path_to_directions(list(path))
            for direction in steps:
                data = move(direction)["cell"]
                map.move_to(direction, data)
    
    end = next(cell for cell in map.cells if cell.kind == "exit")
    
    if eat_mode:
        path_to_end = map.a_star(map.at, end)
        steps = path_to_directions(list(path_to_end))

        for direction in steps:
            data = move(direction)["cell"]
            map.move_to(direction, data)
            if map.at.kind == "cheese":
                if cheese_gotten:
                    eat()
                else:
                    cheese_gotten = True
                    map.at.kind = "open"
                    grab()
        if cheese_gotten:
            drop()

        exit()
    else:
        if cheese_gotten:
            end = next(cell for cell in map.cells if cell.kind == "exit")
            path_to_end = map.a_star(map.at, end)
            steps = path_to_directions(list(path_to_end))
            drop()

        print("END FOUND")
        input()
        
        cheese_paths = [
            map.a_star(map.at, cheese)
            for cheese in cheeses
        ]
        viable_paths = [
            path for path in cheese_paths
            if len(path) * 3 * 2 < 2500
        ]

        for path in viable_paths:
            print("FINDING CHEESE")
            input()
            steps = list(path_to_directions(path))
            for direction in steps:
                data = move(direction)["cell"]
                map.move_to(direction, data)
            grab()

            print("CHEESE GOTTEN")
            input()

            path_to_end = map.a_star(map.at, end)
            steps = path_to_directions(list(path_to_end))
            for direction in steps:
                data = move(direction)["cell"]
                map.move_to(direction, data)
            drop()

            print("CHEESE DROPPED")
            input()
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
    
    def backtrack(self):
        direction = self.traveled.pop()
        normal_directions = ["north", "east", "south", "west"]
        reverse_directions = ["south", "west", "north", "east"]
        index = normal_directions.index(direction)
        reverse_direction = reverse_directions[index]
        self.at = self.neighbor(self.at.y, self.at.x, reverse_direction)
        return reverse_direction

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


mazes = get("/mazes")
test_maze = mazes[6]["id"]
solve_maze(test_maze)
