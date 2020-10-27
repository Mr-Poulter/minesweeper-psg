import PySimpleGUI as sg
from random import randint

width, height = 20, 10

diff = 0.1
num_mines = int(width * height * diff)

grid = []
mines = {}
first_move = True
moves_left = (width * height) - num_mines
running = True

for i in range(height):
    grid.append([])
    mines[i] = {}
    for j in range(width):
        grid[i].append(sg.Button(key=f"{i}_{j}", size=(3, 2), auto_size_button=False,
                       button_color=("white","gray")))
        mines[i][j] = 0

frame = sg.Frame("Game Grid", grid) # this contains all the grid buttons within a lined frame
layout = [
        [frame],
        [sg.Button("Exit"), sg.Button("New Game"), sg.Text(f"{num_mines} mines, {moves_left} moves left", key="MOVESLEFT")],
    ]

window = sg.Window("Minesweeper", layout, finalize=True)
for i in range(height):
    for j in range(width):
        grid[i][j].bind('<Button-3>', f"+FLAG")

def new_game():
    global first_move, mines, moves_left, running

    for row in grid:
        for cell in row:
            cell.update("", button_color=("white", "gray"))
    for row in mines:
        for cell in mines[row]:
            mines[row][cell] = 0

    moves_left = (width * height) - num_mines
    first_move = True
    running = True
    window["MOVESLEFT"].update(f"{num_mines} mines, {moves_left} moves left")

def lose_game():
    global running
    running = False
    show_mines()
    window["MOVESLEFT"].update("YOU LOSE!")

def win_game():
    global running
    running = False
    show_mines()
    window["MOVESLEFT"].update("YOU WIN!")

def spider(row, col):
    """
    Spider out from 0 surrounded tiles.
    Update the moves.
    """
    global moves_left

    touching = count_mines(row, col)
    try:
        if mines[row][col] == 1: # don't spider from mine blocks!
            return
    except:
        pass
    
    if grid[row][col].ButtonColor[1] in ("green", "red"): # already discovered
        return
    
    # mark this block as discovered
    grid[row][col].update(str(touching), button_color=("white","green"))
    moves_left -= 1

    # check surrounding tiles
    for r,c in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
        try:
            if row+r == -1 or col+c == -1:
                continue
            total = count_mines(row+r, col+c)
            # print(f"Check {row+r}, {col+c}: {total} {grid[row+r][col+c].ButtonColor[1]}")
            # check if already been coloured
            if grid[row+r][col+c].ButtonColor[1] == "gray":
                if total == 0:
                    spider(row+r, col+c)
                else:
                    grid[row+r][col+c].update(str(total), button_color=("white","green"))
                    moves_left -= 1
        except IndexError:
            continue

def deploy_mines(row, col):
    """
    row, col is the first move, and thus safe
    """
    num_deployed = 0
    while num_deployed <= num_mines:
        r, c = randint(0, height-1), randint(0, width-1)
        if (r == row and c == col) or mines[r][c] == 1:
            continue
        mines[r][c] = 1
        num_deployed += 1

def count_mines(row, col):
    """
    Count the mines surrounding the given coordinates.
    """
    total = 0
    for r,c in ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)):
        try:
            if mines[row+r][col+c] == 1:
                total += 1
        except KeyError:
            pass
    return total

def show_mines():
    for i in mines:
        for j in mines[i]:
            if mines[i][j] == 1:
                grid[i][j].update("*", button_color=("white","red"))

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    elif event == "New Game":
        new_game()
    elif "FLAG" in event and running:
        # annoyingly this generates TWO events: i_jFLAG_i_j
        row, col = map(int, event.split("+")[0].split("_"))
        if grid[row][col].ButtonColor[1] == "gray":
            grid[row][col].update("?")
    elif "_" in event and running:
        row, col = map(int, event.split("_"))
        if first_move:
            deploy_mines(row, col)
            first_move = False
        if mines[row][col] == 1:
            grid[row][col].update("*", button_color=("white","red"))
            lose_game()
        elif mines[row][col] == 0:
            moves_left -= 1
            surrounding = count_mines(row, col)
            if surrounding == 0:
                spider(row, col)
            grid[row][col].update(str(surrounding), button_color=("white", "green"))
            window["MOVESLEFT"].update(f"{num_mines} mines, {moves_left} moves left")
            if moves_left == 0:
                win_game()

window.close()
