import pygame
import sys
import time

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
GRID_SIZE = 100
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

# Initialize Pygame
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

# Initialize blocks
blocks = [
    Block(100, 0, 200, 200, TARGET_COLOR),  # Target block
    Block(0, 0, 100, 200, BLOCK_COLORS[0]),  # Left upper block
    Block(300, 0, 100, 200, BLOCK_COLORS[1]),  # Right upper block
    Block(0, 200, 100, 100, BLOCK_COLORS[2]),  # Left middle block
    Block(300, 200, 100, 100, BLOCK_COLORS[3]),  # Right middle block
    Block(100, 200, 100, 100, BLOCK_COLORS[4]),  # Center top block
    Block(200, 200, 100, 100, BLOCK_COLORS[5]),  # Center bottom block
    Block(0, 300, 100, 200, BLOCK_COLORS[6]),  # Left lower block
    Block(300, 300, 100, 200, BLOCK_COLORS[7]),  # Right lower block
    Block(100, 400, 100, 100, BLOCK_COLORS[8]),  # Bottom left block
    Block(200, 400, 100, 100, BLOCK_COLORS[9])   # Bottom right block
]

# Button class
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

# Helper functions
def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, (200, 200, 200), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
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

def get_neighbors(state):
    neighbors = []
    for i, (x, y) in enumerate(state):
        for dx, dy in [(-GRID_SIZE, 0), (GRID_SIZE, 0), (0, -GRID_SIZE), (0, GRID_SIZE)]:
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT:
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

def dfs_solve(initial_state):
    stack = [(initial_state, [])]
    visited = set()
    while stack:
        current_state, path = stack.pop()
        set_state(blocks, current_state)
        if check_win(blocks[0]):
            return path
        visited.add(current_state)
        for neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))
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

# Main game loop
running = True
selected_block = None
offset_x, offset_y = 0, 0
solution = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if solve_button.is_clicked(event.pos):
                initial_state = get_state(blocks)
                start_time = time.time()  # Record start time
                solution = dfs_solve(initial_state)
                end_time = time.time()  # Record end time
                if solution:
                    print(f"Solution found in {end_time - start_time:.2f} seconds")  # Print the duration
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

                # Snap to grid
                new_x = round(new_x / GRID_SIZE) * GRID_SIZE
                new_y = round(new_y / GRID_SIZE) * GRID_SIZE

                # Store old position
                old_x, old_y = selected_block.rect.x, selected_block.rect.y

                # Move block to new position
                selected_block.rect.x = new_x
                selected_block.rect.y = new_y

                # Check boundaries
                if selected_block.rect.right > SCREEN_WIDTH or selected_block.rect.bottom > SCREEN_HEIGHT or selected_block.rect.left < 0 or selected_block.rect.top < 0:
                    selected_block.rect.x = old_x
                    selected_block.rect.y = old_y

                # Check collision
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
