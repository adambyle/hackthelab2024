# HackTheLab 2024 winning algorithm

This maze-solving algorithm (codename **Ransack**) won the HackTheLab hackathon in September 2024 at Michigan Software Labs in Ada, Michigan. It beat the second-place submission by nearly 10 times the points.

Each of ten mazes has a start and an end cell and may contain many "pieces of cheese" scattered throughout the maze. A rat is making its way through each maze. The rat may only see its own cell and any adjacent cells, including whether the adjacent cells are the start, are the end, or contain a piece of cheese. The rat may eat any piece of cheese it encounters. It may also carry at most one piece of cheese with it and deposit it at the exit cell, or eat a piece of cheese it is carrying with it. The rat may also "smell" for nearby pieces of cheese. Our solution did not use the sense of smell.

Points are awarded or spent for performing certain actions:

- Moving from one cell to another costs 3 points.
- Performing the "exit" action on the exit cell is worth 5000 points.
- Eating a piece of cheese is worth 1000 points.
- Dropping a piece of cheese off at the exit cell is worth 2500 points.

Our algorithm performs a near-exhaustive traversal of the maze in search of the exit cell and every piece of cheese (the number of cheese pieces is known at the beginning). Once the exit cell and all pieces of cheese have been located, the rat carries each piece of cheese one-by-one to the exit cell, exiting the maze once it has finished. We determined that every piece of cheese would likely be worth the cost of the trip made to reach it, although we included a case in our program to ignore cheese pieces that are not worth reaching.

The algorithm works in this order:

1. The rat traverses the maze until the exit cell and all cheese pieces are located. It chooses to turn left first, but if it sees adjacent cheese it will move toward the cheese instead.
2. The rat will pick up any cheese it finds if it is emptyhanded (remember it may only carry one at a time).
3. Anytime the exit cell is touched by the rat, the rat deposits the cheese.
4. If a rat encounters cheese while its hands are full, it remembers the location of the cheese. If the location of the exit is known, the rat may decide to eat the cheese if the 1000 points gained from eating it outweigh the points gained by making a two-way trip to retrieve it from the exit cell (the rat will have to visit the exit cell to free its hands before coming back for the newly encountered cheese).
5. Once the exit cell and all cheese pieces have been located, the rat moves to the exit to deposit cheese if it is carrying any.
6. Then, the rat retrieves and deposits each remaining piece of cheese.
7. Once the rat has deposited the last piece of cheese, it is already at the exit cell, so it exits the maze.

Our algorithm leverages the A* pathfinding algorithm in a number of scenarios:

1. When the rat encounters a dead end, it pathfinds to the nearest unvisited cell. We found this to be slightly faster than backtracking.
2. The rat uses pathfinding to reach the exit and to reach known pieces of cheese.

The file [`main.py`](main.py) contains the code we used during the hour the "competition API" was open. The sandbox API, open for the whole time, provided an online visual of the maze to track the rat's progress. No such visual existed for the competition submission, and the rat's position in each maze could only be reset through the sandbox API.

A file with annotations will come soon.
