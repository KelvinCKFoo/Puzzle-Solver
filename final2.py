import pygame
import sys
import heapq
import time
import tracemalloc
from collections import deque

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
BLOCK_SIZE = 100
FPS = 60
BACKGROUND_COLOR = (240, 240, 240)
TARGET_COLOR = (220, 70, 70)
FRAME_COLOR = (0, 0, 0)
FRAME_THICKNESS = 5
TARGET_RECT = pygame.Rect(100, 300, 200, 200)
BLOCK_COLORS = [
    (70, 70, 220),  # Blue
    (220, 220, 70),  # Yellow
    (70, 220, 70),  # Green
    (220, 70, 220),  # Magenta
    (70, 220, 220),  # Cyan
    (220, 140, 70),  # Orange
    (140, 70, 220),  # Purple
    (220, 70, 140),  # Pink
    (70, 140, 220),  # Sky Blue
    (140, 220, 70),  # Lime
    (70, 70, 70),  # Dark Gray
    (255, 165, 0),  # Bright Orange
]


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Klotski Game")
clock = pygame.time.Clock()


# Block class
class Block:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.dragging = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

    def move(self, x, y):
        self.rect.x = x
        self.rect.y = y


# blocks configuration

Standard_Klotski = [
    Block(100, 0, 200, 200, TARGET_COLOR),  # Target block
    Block(0, 0, 100, 200, BLOCK_COLORS[0]),
    Block(300, 0, 100, 200, BLOCK_COLORS[1]),
    Block(100, 200, 100, 100, BLOCK_COLORS[2]),
    Block(200, 200, 100, 100, BLOCK_COLORS[3]),
    Block(0, 200, 100, 100, BLOCK_COLORS[4]),
    Block(300, 200, 100, 100, BLOCK_COLORS[5]),
    Block(0, 300, 100, 200, BLOCK_COLORS[6]),
    Block(300, 300, 100, 200, BLOCK_COLORS[7]),
    Block(100, 400, 100, 100, BLOCK_COLORS[8]),
    Block(200, 400, 100, 100, BLOCK_COLORS[9])
]

Variant_Klotski = [
    Block(100, 0, 200, 200, TARGET_COLOR),    # Target block
    Block(0, 0, 100, 200, BLOCK_COLORS[0]),
    Block(300, 0, 100, 200, BLOCK_COLORS[1]),
    Block(0, 200, 100, 100, BLOCK_COLORS[2]),
    Block(300, 200, 100, 100, BLOCK_COLORS[3]),
    Block(100, 200, 100, 100, BLOCK_COLORS[4]),
    Block(200, 200, 100, 100, BLOCK_COLORS[5]),
    Block(0, 300, 100, 200, BLOCK_COLORS[6]),
    Block(300, 300, 100, 200, BLOCK_COLORS[7]),
    Block(100, 400, 100, 100, BLOCK_COLORS[8]),
    Block(200, 400, 100, 100, BLOCK_COLORS[9])
]

#change puzzle variant here- Variant_Klotski/Standard_Klotski

blocks = Standard_Klotski

def draw_grid(surface):

    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, (200, 200, 200), (0, y), (SCREEN_WIDTH, y))


def draw_target_frame(surface):

    pygame.draw.rect(surface, FRAME_COLOR, TARGET_RECT, FRAME_THICKNESS)


def check_win(block):
    win = block.rect.x == 100 and block.rect.y == 300

    return win


def check_collision(state, moving_index):
# create tile with same size as the moving tile, to simulate moves to the new location
    moving_rect = pygame.Rect(
        state[moving_index][0], #x position of the moving tile
        state[moving_index][1],#y position
        blocks[moving_index].rect.width,#width
        blocks[moving_index].rect.height#height
    )
#loop via every tiles and create rect with their position and size, to check overlap after the moving tile moves
    for i, (x, y) in enumerate(state):
        if i != moving_index:
            rect = pygame.Rect(x, y, blocks[i].rect.width, blocks[i].rect.height)
            if moving_rect.colliderect(rect):

                return True


    return False


def heuristic(state):
    #Manhattan Distance Heuristic
    target_x, target_y = state[0]
    h = abs(target_x - 100) + abs(target_y - 300)

    return h


def get_neighbors(state):
    #loop via every tiles and try to create new state by moving the each in four directions(left,right,up,down) by
    #adding or minusing the block size which is same as 1 move. See line 10
    #the new state only append to the neighbors list if the tile didn't move pass the window boundries and no collision with other tiles
    neighbors = []
    for i, (x, y) in enumerate(state):
        block_width = blocks[i].rect.width
        block_height = blocks[i].rect.height
        for dx, dy in [(-BLOCK_SIZE, 0), (BLOCK_SIZE, 0), (0, -BLOCK_SIZE), (0, BLOCK_SIZE)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT:
                if new_x + block_width <= SCREEN_WIDTH and new_y + block_height <= SCREEN_HEIGHT:
                    new_state = list(state)
                    new_state[i] = (new_x, new_y)
                    if not check_collision(new_state, i):
                        neighbors.append(tuple(new_state))

    return neighbors


def bfs_solver(initial_state):
    #Explores all possible state of the puzzle level by level, uses get_neighbors to create new state to explore, until game wins
    #it pops the queue from the left, therefore it will only explore level by level
    queue = deque([(initial_state, [])])
    visited = set()

    while queue:
        print(f"Queue length: {len(queue)}")
        current_state, path = queue.popleft()
        if current_state in visited:

            continue

        visited.add(current_state)

        if check_win(Block(current_state[0][0], current_state[0][1], 200, 200, TARGET_COLOR)):
            print("Solution found by BFS!")
            return path

        for neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))


    return None

def dfs_solver(initial_state):
    stack = [(initial_state, [])]
    visited = set()

    while stack:
        current_state, path = stack.pop() # pop the latest state in the stack, which allow dps to dive deeply into a path
        if current_state in visited:
            continue

        visited.add(current_state)

        if check_win(Block(current_state[0][0], current_state[0][1], 200, 200, TARGET_COLOR)):
            print("Solution found by DFS!")
            return path
        # Generate new states to the stack
        for neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))

    print("No solution found by DFS.")
    return None



def astar_solver(initial_state):

    open_set = []
    heapq.heappush(open_set, (heuristic(initial_state), 0, initial_state, [])) #f(n), g(n), current state, path
    visited_set = set() #visited set

    while open_set:

        f, g, current_state, path = heapq.heappop(open_set) #pop the lowest f(n) state from the open set

        # Convert state to a tuple(immutable) to avoid any mistake changing the visited state
        state_tuple = tuple(tuple(pos) for pos in current_state)
        if state_tuple in visited_set:

            continue

        visited_set.add(state_tuple)

        # Check win
        if check_win(Block(current_state[0][0], current_state[0][1], 200, 200, TARGET_COLOR)):

            return path

        for neighbor in get_neighbors(current_state):
            neighbor_tuple = tuple(tuple(pos) for pos in neighbor)
            if neighbor_tuple not in visited_set:
                new_path = path + [neighbor]
                # g + 1 for the cost of moving to next state
                heapq.heappush(open_set, (g + 1 + heuristic(neighbor), g + 1, neighbor, new_path))


    return None


# Start memory and time tracking

tracemalloc.start()
start_time = time.time()

initial_state = tuple((block.rect.x, block.rect.y) for block in blocks)

# Uncomment the solver you want to use

solution = astar_solver(initial_state)
#solution = bfs_solver(initial_state)
#solution = dfs_solver(initial_state)

# Stop memory and time tracking
end_time = time.time()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

if solution:
    move_count = len(solution)
    print("Solution found!")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Move count: {move_count}")
    print(f"Peak memory usage: {peak / 1024 / 1024:.4f} MB")
else:
    print("No solution found.")


# Visualize the solution by simulating the path
def visualize_solution(solution):
    for step in solution:
        for i, (x, y) in enumerate(step):
            blocks[i].move(x, y)

        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)

        for block in blocks:
            block.draw(screen)

        draw_target_frame(screen)
        pygame.display.flip()
        time.sleep(0.3)  # Pause for a moment to visualize the move


# Solve button
def draw_solve_button():
    font = pygame.font.Font(None, 36)
    button_text = font.render("Solve", True, (0, 0, 0))
    button_rect = pygame.Rect(150, 450, 100, 40)
    pygame.draw.rect(screen, (200, 200, 200), button_rect)
    screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))
    return button_rect



running = True
selected_block = None
offset_x, offset_y = 0, 0
button_rect = draw_solve_button()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos): #if solve button is pressed, it simulates the solution
                if solution:

                    visualize_solution(solution)
            else:
                for block in blocks:
                    if block.rect.collidepoint(event.pos): # mouse click on block, mark as dragging
                        selected_block = block
                        #offset = horizontal difference and vertical difference between mouse position and tile's top-left
                        offset_x, offset_y = event.pos[0] - block.rect.x, event.pos[1] - block.rect.y
                        block.dragging = True

                        break
        elif event.type == pygame.MOUSEBUTTONUP: #if release unmark dragging
            if selected_block:
                selected_block.dragging = False
                selected_block = None

        elif event.type == pygame.MOUSEMOTION:
            if selected_block and selected_block.dragging:
                new_x = event.pos[0] - offset_x #calculate new X base on mouse movement
                new_y = event.pos[1] - offset_y #calculate new Y base on mouse movement

                new_x = round(new_x / BLOCK_SIZE) * BLOCK_SIZE #round to cloest tile size
                new_y = round(new_y / BLOCK_SIZE) * BLOCK_SIZE

                old_x, old_y = selected_block.rect.x, selected_block.rect.y #save old position in case collision occurs

                selected_block.rect.x = new_x
                selected_block.rect.y = new_y

                if (selected_block.rect.right > SCREEN_WIDTH or #check if tile out of boundaries
                        selected_block.rect.bottom > SCREEN_HEIGHT or
                        selected_block.rect.left < 0 or
                        selected_block.rect.top < 0):
                    selected_block.rect.x = old_x
                    selected_block.rect.y = old_y


                if check_collision([(block.rect.x, block.rect.y) for block in blocks], blocks.index(selected_block)):
                    #check if dragging tile collide with any tlies
                    selected_block.rect.x = old_x
                    selected_block.rect.y = old_y


    screen.fill(BACKGROUND_COLOR)
    draw_grid(screen)

    for block in blocks:
        block.draw(screen)

    draw_target_frame(screen)
    button_rect = draw_solve_button()
    pygame.display.flip()
    clock.tick(FPS)

    # Check win condition
    if check_win(blocks[0]):
        print("You win!")
        running = False

pygame.quit()
sys.exit()
