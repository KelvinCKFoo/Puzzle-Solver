import pygame
import sys
import heapq
import time
from collections import deque

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
BLOCK_SIZE = 100
FPS = 60
BACKGROUND_COLOR = (240, 240, 240)
TARGET_COLOR = (220, 70, 70)
FRAME_COLOR = (0, 0, 0)
FRAME_THICKNESS = 5
BUTTON_COLOR = (200, 200, 200)
BUTTON_TEXT_COLOR = (0, 0, 0)
TARGET_RECT = pygame.Rect(100, 300, 200, 200)
BLOCK_COLORS = [
    (70, 70, 220),
    (220, 220, 70),
    (70, 220, 70),
    (220, 70, 220),
    (70, 220, 220),
    (220, 140, 70),
    (140, 70, 220),
    (220, 70, 140),
    (70, 140, 220),
    (140, 220, 70),
    (70, 70, 70)
]


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Klotski Game")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

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

# blocks
blocks = [
    Block(100, 0, 200, 200, TARGET_COLOR),  
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

# Button
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, 36)
        self.text_surf = self.font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

solve_button = Button(150, 450, 100, 40, "Solve", BUTTON_COLOR, BUTTON_TEXT_COLOR)


def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(surface, (200, 200, 200), (0, y), (SCREEN_WIDTH, y))

def draw_target_frame(surface):
    pygame.draw.rect(surface, FRAME_COLOR, TARGET_RECT, FRAME_THICKNESS)

def check_win(block):
    return block.rect.x == 100 and block.rect.y == 300

def get_state(blocks):
    return tuple((block.rect.x, block.rect.y) for block in blocks)

def set_state(blocks, state):
    for block, pos in zip(blocks, state):
        block.move(pos[0], pos[1])

def heuristic(state):
    # Manhattan distance
    target_pos = state[0]
    goal_pos = (100, 300)
    return abs(target_pos[0] - goal_pos[0]) + abs(target_pos[1] - goal_pos[1])

def get_neighbors(state):
    neighbors = []

    for i in range(len(state)):
        x, y = state[i]


        # Move left
        new_x, new_y = x - BLOCK_SIZE, y
        if new_x >= 0:
            new_state = list(state)
            new_state[i] = (new_x, new_y)
            if not check_collision(new_state, i):
                neighbors.append(tuple(new_state))

        # Move right
        new_x, new_y = x + BLOCK_SIZE, y
        if new_x < SCREEN_WIDTH:
            new_state = list(state)
            new_state[i] = (new_x, new_y)
            if not check_collision(new_state, i):
                neighbors.append(tuple(new_state))

        # Move up
        new_x, new_y = x, y - BLOCK_SIZE
        if new_y >= 0:
            new_state = list(state)
            new_state[i] = (new_x, new_y)
            if not check_collision(new_state, i):
                neighbors.append(tuple(new_state))

        # Move down
        new_x, new_y = x, y + BLOCK_SIZE
        if new_y < SCREEN_HEIGHT:
            new_state = list(state)
            new_state[i] = (new_x, new_y)
            if not check_collision(new_state, i):
                neighbors.append(tuple(new_state))


    return neighbors

def check_collision(state, moving_index):
    moving_rect = pygame.Rect(state[moving_index][0], state[moving_index][1], blocks[moving_index].rect.width, blocks[moving_index].rect.height)
    for i, (x, y) in enumerate(state):
        if i != moving_index:
            rect = pygame.Rect(x, y, blocks[i].rect.width, blocks[i].rect.height)
            if moving_rect.colliderect(rect):
                return True
    return False

def bfs_solve(initial_state):
    queue = deque([(initial_state, [])])
    visited = set()
    iteration_count = 0
    while queue:
        iteration_count += 1
        if iteration_count % 1000 == 0:
            print(f"BFS iteration: {iteration_count}, Queue size: {len(queue)}")

        current_state, path = queue.popleft()
        set_state(blocks, current_state)
        if check_win(blocks[0]):
            return path
        visited.add(current_state)
        for neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
                visited.add(neighbor)
    return None


def dfs_solve(state, depth_limit, visited):
    stack = [(state, [], 0)]
    iteration_count = 0
    while stack:
        iteration_count += 1
        if iteration_count % 1000 == 0:
            print(f"DFS iteration: {iteration_count}, Stack size: {len(stack)}")

        current_state, path, depth = stack.pop()
        set_state(blocks, current_state)
        if depth > depth_limit:
            continue
        if check_win(blocks[0]):
            return path
        if current_state in visited:
            continue
        visited.add(current_state)
        neighbors = get_neighbors(current_state)

        neighbors.sort(key=lambda s: abs(s[0][0] - 100) + abs(s[0][1] - 300))
        for neighbor in neighbors:
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor], depth + 1))
    return None

def iddfs_solve(initial_state):
    depth_limit = 1
    while True:
        print(f"Trying depth limit: {depth_limit}")
        visited = set()
        path = dfs_solve(initial_state, depth_limit, visited)
        if path is not None:
            return path
        depth_limit += 1
def astar_solve(initial_state):
    open_set = []
    heapq.heappush(open_set, (0 + heuristic(initial_state), 0, initial_state, []))

    closed_set = set()

    while len(open_set) > 0:
        f_cost, cost, current_state, path = heapq.heappop(open_set)

        set_state(blocks, current_state)

        if check_win(blocks[0]):
            return path

        if current_state in closed_set:
            continue

        closed_set.add(current_state)

        neighbors = get_neighbors(current_state)


        for neighbor in neighbors:
            if neighbor not in closed_set:
                new_cost = cost + 1

                heuristic_cost = heuristic(neighbor)

                new_f_cost = new_cost + heuristic_cost

                new_path = path + [neighbor]

                heapq.heappush(open_set, (new_f_cost, new_cost, neighbor, new_path))

    return None

def simulate_solution(path):
    for state in path:
        set_state(blocks, state)
        screen.fill(BACKGROUND_COLOR)
        draw_grid(screen)
        for block in blocks:
            block.draw(screen)
        draw_target_frame(screen)
        pygame.display.flip()
        pygame.time.wait(200)

# game loop
running = True
selected_block = None
offset_x, offset_y = 0, 0

solution = 3

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if solve_button.is_clicked(event.pos):
                initial_state = get_state(blocks)
                start_time = time.time()
                if solution == 3:
                    solution = astar_solve(initial_state)
                if solution == 1:
                    solution = bfs_solve(initial_state)
                if solution == 2:
                    solution = iddfs_solve(initial_state)
                end_time = time.time()
                if solution:
                    print(f"Solution found in {end_time - start_time:.2f} seconds")
                    simulate_solution(solution)
            for block in blocks:
                if block.rect.collidepoint(event.pos):
                    selected_block = block
                    offset_x, offset_y = event.pos[0] - block.rect.x, event.pos[1] - block.rect.y
                    block.dragging = True
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            if selected_block:
                selected_block.dragging = False
                selected_block = None
        elif event.type == pygame.MOUSEMOTION:
            if selected_block and selected_block.dragging:
                new_x = event.pos[0] - offset_x
                new_y = event.pos[1] - offset_y


                new_x = round(new_x / BLOCK_SIZE) * BLOCK_SIZE
                new_y = round(new_y / BLOCK_SIZE) * BLOCK_SIZE


                old_x, old_y = selected_block.rect.x, selected_block.rect.y


                selected_block.rect.x = new_x
                selected_block.rect.y = new_y


                if selected_block.rect.right > SCREEN_WIDTH or selected_block.rect.bottom > SCREEN_HEIGHT or selected_block.rect.left < 0 or selected_block.rect.top < 0:
                    selected_block.rect.x = old_x
                    selected_block.rect.y = old_y


                if check_collision(get_state(blocks), blocks.index(selected_block)):
                    selected_block.rect.x = old_x
                    selected_block.rect.y = old_y

    screen.fill(BACKGROUND_COLOR)
    draw_grid(screen)

    for block in blocks:
        block.draw(screen)

    draw_target_frame(screen)
    solve_button.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

    # Check win condition
    if check_win(blocks[0]):
        print("You win!")
        running = False

pygame.quit()
sys.exit()
