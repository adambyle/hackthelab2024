# HackTheLab 2024 winning algorithm

This maze-solving algorithm (codename **Ransack**) won the HackTheLab hackathon in September 2024 at Michigan Software Labs in Ada, Michigan. It beat the second-place submission by nearly 10 times the points.

I would like to thank [Nick Roberts](https://github.com/nickneilroberts) for participating as my partner. Please see our [takeaways](#activity-takeaways) below for our development and learning experience.

## Challenge

Each of ten mazes has a start and an end cell and may contain many "pieces of cheese" scattered throughout the maze. A rat is making its way through each maze. The rat may only see its own cell and any adjacent cells, including whether the adjacent cells are the start, are the end, or contain a piece of cheese. The rat may eat any piece of cheese it encounters. It may also carry at most one piece of cheese with it and deposit it at the exit cell, or eat a piece of cheese it is carrying with it. The rat may also "smell" for nearby pieces of cheese. Our solution did not use the sense of smell.

Points are awarded or spent for performing certain actions:

- Moving from one cell to another costs 3 points.
- Performing the "exit" action on the exit cell is worth 5000 points.
- Eating a piece of cheese is worth 1000 points.
- Dropping a piece of cheese off at the exit cell is worth 2500 points.

## Solution

Our algorithm performs a near-exhaustive traversal of the maze in search of the exit cell and every piece of cheese (the number of cheese pieces is known at the beginning). Once the exit cell and all pieces of cheese have been located, the rat carries each piece of cheese one-by-one to the exit cell, exiting the maze once it has finished. We determined that every piece of cheese would likely be worth the cost of the trip made to reach it, although we included a case in our program to ignore cheese pieces that are not worth reaching.

The algorithm works in this order:

1. The rat traverses the maze until the exit cell and all cheese pieces are located. It chooses to turn left first, but if it sees adjacent cheese it will move toward the cheese instead.
2. The rat will pick up any cheese it finds if it is emptyhanded (remember it may only carry one at a time).
3. Anytime the rat touches the exit cell, it deposits the cheese.
4. If a rat encounters cheese while its hands are full, it remembers the location of the cheese. If the location of the exit is known, the rat may decide to eat the cheese if the 1000 points gained from eating it outweigh the points gained by making a two-way trip to retrieve it from the exit cell (the rat will have to visit the exit cell to free its hands before coming back for the newly encountered cheese).
5. Once the exit cell and all cheese pieces have been located, the rat moves to the exit to deposit cheese if it is carrying any.
6. Then, the rat retrieves and deposits each remaining piece of cheese.
7. Once the rat has deposited the last piece of cheese, it is already at the exit cell, so it exits the maze.

Our algorithm leverages the A* pathfinding algorithm in a couple of scenarios:

1. When the rat encounters a dead end, it pathfinds to the nearest unvisited cell. We found this to usually be faster than backtracking, especially when the maze has "loops".
2. The rat uses pathfinding to reach the exit and to reach known pieces of cheese.

## Code

The file [`main.py`](main.py) contains the code we used during the hour the "competition API" was open. The sandbox API, open for the whole time, provided an online visual of the maze to track the rat's progress. No such visual existed for the competition submission, and the rat's position in each maze could only be reset through the sandbox API.

[`annotated.py`](annotated.py) contains explanations of our choices.

Michigan Software Labs has said they will open-source the server-side code. I will link to it here once I find it.

## Activity takeaways

This challenge tested our knowledge of web API usage and of different maze-solving tactics and pathfinding algorithms. Although I had experience using web APIs in past projects, this was the first time I was able to practically apply pathfinding algorithms. I learned about balancing efficiency against thoroughness: in trying to maximize our score, we also had to be mindful of how many moves the rat was making, as each one cost us more. A single maze could also take up to three minutes to solve, mostly due to network bottlenecks, but this put pressure on us in the final minutes of the hackathon before the web server shut down. (The average maze took from 800 to 1500 "steps" to solve.)

Our initial solution, developed in about half of our allotted time, brute-forced the entire maze in order to locate the exit and all cheese pieces, in order to use A* to collect each one. In the following couple hours, we found a couple ways to avoid traversing the entire maze. For one, we could use the number of cheeses, provided at the beginning, to stop searching when the last one was found. We also gave the rat logic to recover as much cheese as possible *before* all the points of interest are discovered. Finally, we made the rat choose cheese corridors over the usual left-first path: a very trivial change, but one that made a difference of up to 500 points on some mazes.

It was surprising how volatile some of our optimizations could be. One surprising discovery was that, by stopping short on its traversal of the entire maze, the rat would sometimes miss "shortcuts" from each cheese to the exit that would have ultimately saved moves during pathfinding. We decided based on outcomes on the test mazes that it was more often than not worthwhile to stop traversing the maze once all cheeses were found, even though this was sometimes not the case.

One of our earliest cheese-collection algorithms involved picking up the first cheese the rat encountered but eating all the rest. The rat would still search until it found every cheese, but it would only ever bring back one of them. This method generated a higher score than the "fetch every cheese" method on *only one* of our practice mazes. This unique case encouraged us to investigate scenarios where the rat may want to eat the cheese instead of bringing it back, which added a couple special cases to our final solution. We don't think these cases were utilized often, but they improved scores marginally on some practice mazes.
