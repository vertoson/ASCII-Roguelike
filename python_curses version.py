from readchar import readchar
import os
from random import *
from collections import defaultdict, deque
import time
import curses
import math

########################################################################################################### SECTION INITIALIZE





stdscr = curses.initscr()
refresh = stdscr.refresh
curses.curs_set(0)  
# Start color
curses.start_color()
curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)

EnemyCharList = [' S ']

WIDTH = 56
HEIGHT = 40



obj = ' · '
game = True

class Enemy():
    def __init__(self, save_obj, char, x, y, health, damage):
        self.x = x
        self.y = y
        self.health = health
        self.damage = damage
        self.char = char
        self.save_obj = save_obj



class CurrentPlayer():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = ' ☻ '
        self.continue_game = True
        self.same_floor = True
        self.floor = 1
        self.fighting = False
        self.opponent = None
        self.health = 1000
        self.damage = 50

        


class Room():
    def __init__(self, x, y, width, length):
        self.x = x
        self.y = y
        self.width = width ## width = x + calculated width
        self.length = length ## width = y + calculated length
        self.show = False



class AllRooms():
    def __init__(self):
        self.rooms = []
        self.room_count = 0

class Node:
    def __init__(self, x, y, came_from):
        self.x = x
        self.y = y
        self.came_from = came_from



def clear():
	stdscr.clear()
        



def MakeGrid():
    base = [[' 0 ' for x in range(WIDTH)] for y in range(HEIGHT)]
    return base

########################################################################################################### SECTION ENTITIES


def PlayerMovement():
    global obj, game

    
    move = readchar()
    savex, savey = Player.x, Player.y
    MAP[savey][savex] = obj
    if move.lower() == 'w':
        Player.y -= 1
    elif move.lower() == 'a':
        Player.x -= 1
    elif move.lower() == 's':
        Player.y += 1
    elif move.lower() == 'd':
        Player.x += 1
    elif move.lower() == 'f':
        game = False
        Player.same_floor = False
    if MAP[Player.y][Player.x] == ' | ' or MAP[Player.y][Player.x] == '---' or MAP[Player.y][Player.x] == ' 0 ': 
        Player.x = savex
        Player.y = savey
        if MAP[Player.y][Player.x] == '###':
            MAP[Player.y][Player.x] = '>' + Player.char[1] + '<'
        else:
            MAP[Player.y][Player.x] = Player.char
    else:
        obj = MAP[Player.y][Player.x]
        if MAP[Player.y][Player.x] == '###':
            MAP[Player.y][Player.x] = '>' + Player.char[1] + '<'
        else:
            MAP[Player.y][Player.x] = Player.char

    

def SpawnEnemy():
    global CurrentEnemies
    available_rooms = []
    for room in room_total.rooms:
        if room.show:
            available_rooms.append(room)
    if len(available_rooms) < 3:
        return None
    shuffle(available_rooms)
    cur_room = available_rooms[0]
    x = randint(cur_room.x+1, cur_room.width-2)
    y = randint(cur_room.y+1, cur_room.length-2)
    while MAP[y][x] == Player.char:
        x = randint(cur_room.x+1, cur_room.width-2)
        y = randint(cur_room.y+1, cur_room.length-2)
    char = ' S '
    
    CurrentEnemies.append(Enemy(' · ', char, x, y, 10, 10))
    MAP[y][x] = char





def MoveEnemy():
    not_available_pos = [' | ', '---', ' 0 '] 
    copy_enemies = CurrentEnemies.copy()
    max_repeats = math.factorial(len(CurrentEnemies))
    count_repeats = defaultdict(int)
    while copy_enemies:
        enemy = copy_enemies.pop(0)
        Q = deque([Node(enemy.x, enemy.y, None)])
        SEEN = set()
        new_map = MAP.copy()
        backtrack = []
        new_map = [list(a) for a in new_map]
        count_repeats[enemy] += 1

        while Q:

            cur = Q.popleft()
            x = cur.x
            y = cur.y

            if (x, y) in SEEN:
                continue
            if MAP[y][x][1] == Player.char[1]:

                while cur.came_from:
                    backtrack.append(cur)
                    cur = cur.came_from
                break

            if MAP[y][x+1] not in not_available_pos:
                Q.append(Node(x+1, y, cur))
            if MAP[y][x-1] not in not_available_pos:
                Q.append(Node(x-1, y, cur))
            if MAP[y+1][x] not in not_available_pos:
                Q.append(Node(x, y+1, cur))
            if MAP[y-1][x] not in not_available_pos:
                Q.append(Node(x, y-1, cur))
            
        
            SEEN.add((x, y))

        #print(backtrack[-1].x, backtrack[-1].y, enemy.save_obj)
        #print(enemy.x, enemy.y, enemy.save_obj)

        if count_repeats[enemy] > max_repeats:
            continue
        first_node = backtrack[-1]
        if MAP[first_node.y][first_node.x] in EnemyCharList:
            copy_enemies.append(enemy)
            continue
        MAP[enemy.y][enemy.x] = enemy.save_obj
        
        enemy.save_obj = BASE[first_node.y][first_node.x]
        MAP[first_node.y][first_node.x] = enemy.char
        enemy.x = first_node.x
        enemy.y = first_node.y

        


def PlayerAttackingEnemy(enemy):


    while enemy.health > 0 and Player.health > 0:
        UpdateGame()
        enemy.health -= Player.damage
        Player.health -= enemy.damage
        time.sleep(1)
        
    Player.fighting = False
    UpdateGame()
    if enemy.health <= 0:
        MAP[enemy.y][enemy.x] = enemy.save_obj
        CurrentEnemies.remove(enemy)
    if Player.health <= 0:
        return False
    
    return True



def CheckAttacking():
    attack_pos = []
    for y in range(Player.y-1, Player.y+2):
        for x in range(Player.x-1, Player.x+2):
            attack_pos.append((x, y))

    
    
    for enemy in CurrentEnemies:
        #print(attack_pos, enemy.x, enemy.y)
        if (enemy.x, enemy.y) in attack_pos:
            
            Player.fighting = True
            Player.opponent = enemy
            alive = PlayerAttackingEnemy(enemy)
            if not alive:
                return False
    return True

            
                
    
    
########################################################################################################### SECTION ROOMS


def FirstRoomCreation():
    global BASE
    x = randint(0, WIDTH-1)
    y = randint(0, HEIGHT-1)
    length = randint(6, 12)
    width = randint(6, 12)
    while x+width >= WIDTH:
        x = randint(0, WIDTH-1)
        width = randint(6, 12)
    while y+length >= HEIGHT:   
        y = randint(0, HEIGHT-1)
        length = randint(6, 12)
    
    length = y + length
    width = x + width
    Player.x = randint(x+1, width-2)
    Player.y = randint(y+1, length-2)


    #BASE[Player.y][Player.x] = Player.char
    MAP[Player.y][Player.x] = Player.char
    new_room = Room(x, y, width, length)
    room_total.rooms.append(new_room)

def CreateNextRooms():
    pos_y = randint(0, HEIGHT-7)
    pos_x = randint(0, WIDTH-7)
    size_y = pos_y+randint(6, 12)
    size_x = pos_x+randint(6, 12)
    loop_times = 0
    flag = True
    while flag:
        loop_times += 1
        if size_y >= HEIGHT:
            pos_y = randint(0, HEIGHT-7)
            size_y = pos_y+randint(4, 12)
            
            continue

        if size_x >= WIDTH:
            pos_x = randint(0, WIDTH-7)
            size_x = pos_x+randint(4, 12)
            
            continue
        else:
            
            count = 0
            total = len(room_total.rooms)
            check_room = []
            for y in range(pos_y, size_y):
                for x in range(pos_x, size_x):
                    check_room.append((x, y))

            for room in room_total.rooms:
                iter_room = []

                for y in range(room.y-1, room.length+1):
                    for x in range(room.x-1, room.width+1):
                        iter_room.append((x, y))
                combined = iter_room + check_room
                if len(combined) == len(set(combined)):
                    count += 1
                else:
                    pos_y = randint(0, HEIGHT-7)
                    size_y = pos_y+randint(4, 12)
                    pos_x = randint(0, WIDTH-7)
                    size_x = pos_x+randint(4, 12)
                    continue
            if count == total:
                flag = False
        

        if loop_times > 250:
            return False
    
    new_room = Room(pos_x, pos_y, size_x, size_y)
    room_total.rooms.append(new_room)
    
def ChooseDirection(current_room, closest_room):
    manhattan_dist_right_wall = abs((current_room.width)-closest_room.x)+abs((current_room.y)-closest_room.y) ## +1 COMES FROM Y POS OF DOOR OF ROOM
    manhattan_dist_bottom_wall = abs((current_room.x)-closest_room.x)+abs((current_room.length)-closest_room.y) ## +1 COMES FROM Y POS OF DOOR OF ROOM
    manhattan_dist_left_wall = abs((current_room.x)-closest_room.width)+abs((current_room.y)-closest_room.y) ## +1 COMES FROM Y POS OF DOOR OF ROOM
    manhattan_dist_top_wall = abs((current_room.x)-closest_room.x)+abs((current_room.y)-closest_room.length) ## +1 COMES FROM Y POS OF DOOR OF ROOM

    if min([manhattan_dist_bottom_wall, manhattan_dist_left_wall, manhattan_dist_right_wall, manhattan_dist_top_wall]) == manhattan_dist_right_wall:
        return 'R'
    elif min([manhattan_dist_bottom_wall, manhattan_dist_left_wall, manhattan_dist_right_wall, manhattan_dist_top_wall]) == manhattan_dist_bottom_wall:
        return 'D'
    elif min([manhattan_dist_bottom_wall, manhattan_dist_left_wall, manhattan_dist_right_wall, manhattan_dist_top_wall]) == manhattan_dist_left_wall:
        return 'L'
    elif min([manhattan_dist_bottom_wall, manhattan_dist_left_wall, manhattan_dist_right_wall, manhattan_dist_top_wall]) == manhattan_dist_top_wall:
        return 'U'
        

def CreateSingularPath(current_room, closest_room):

    closest_room = FindClosestRoom(current_room)
    totalrooms_for_changerooms = room_total.rooms.copy()
    current_room_array_pos = room_placements[current_room.y][current_room.x]
    closest_room_array_pos = room_placements[closest_room.y][closest_room.x]
    #print(current_room_array_pos)
    #print(closest_room_array_pos)
    c = 0
    available_space = ['###', ' 0 ']
    path = ChooseDirection(current_room, closest_room)
    #UpdateGame()
    #UpdateGame2()
    if path == 'R':
        
        startx = current_room.width
        starty = randint(current_room.y+1, current_room.length-2)
        endx = closest_room.x-1
        endy = randint(closest_room.y+1, closest_room.length-2)

        start_pos_x = min([startx, endx])
        start_pos_y = min([starty, endy])
        end_pos_x = max([startx, endx])
        end_pos_y = max([starty, endy])

        for y in range(start_pos_y, end_pos_y+1):
            for x in range(start_pos_x, end_pos_x+1):
                if room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] in SEEN:
                    SEEN.add(room_placements[y][x])
                    #UpdateGame2()
                    CreateSingularPath(totalrooms_for_changerooms[int(room_placements[y][x])], closest_room)

                    #print(SEEN)
                    return closest_room
                elif room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] not in SEEN:
                    SEEN.add(current_room)
                    closest_room = CreateSingularPath(current_room, totalrooms_for_changerooms[int(room_placements[y][x])])


                    return closest_room
        BASE[starty][startx-1] = ' + '
        BASE[endy][endx+1] = ' + '
        DOORS_CREATING_ROOM[(endx+1, endy)] = closest_room
        DOORS_CREATING_ROOM[(startx-1, starty)] = current_room
        b = 0
        while startx != endx or starty != endy:

            b += 1
            if b == 1000:
                print(starty, endy, startx, endx)
                UpdateGame()
            BASE[starty][startx] = '###'
            #UpdateGame()
            #print("R")




            if startx > endx and BASE[starty][startx-1] in available_space:
                startx -= 1
            elif startx < endx and BASE[starty][startx+1] in available_space:
                startx += 1  
            elif starty > endy and BASE[starty-1][startx] in available_space:
                starty -= 1
            elif starty < endy and BASE[starty+1][startx] in available_space:
                starty += 1
        BASE[starty][startx] = '###'
            
    elif path == 'D':

        starty = current_room.length
        startx = randint(current_room.x+1, current_room.width-2)
        endy = closest_room.y-1
        endx = randint(closest_room.x+1, closest_room.width-2)
        start_pos_x = min([startx, endx])
        start_pos_y = min([starty, endy])
        end_pos_x = max([startx, endx])
        end_pos_y = max([starty, endy])
        for y in range(start_pos_y, end_pos_y+1):
            for x in range(start_pos_x, end_pos_x+1):
                if room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] in SEEN:
                    SEEN.add(room_placements[y][x])
                    #UpdateGame2()
                    CreateSingularPath(totalrooms_for_changerooms[int(room_placements[y][x])], closest_room)
                    #print(SEEN)
                    return closest_room
                elif room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] not in SEEN:
                    SEEN.add(current_room)
                    closest_room = CreateSingularPath(current_room, totalrooms_for_changerooms[int(room_placements[y][x])])

                    return closest_room
        BASE[starty-1][startx] = ' + '
        BASE[endy+1][endx] = ' + '
        DOORS_CREATING_ROOM[(endx, endy+1)] = closest_room
        DOORS_CREATING_ROOM[(startx, starty-1)] = current_room
        b = 0
        while startx != endx or starty != endy:

            b += 1
            if b == 1000:
                print(starty, endy, startx, endx)
                UpdateGame()
            BASE[starty][startx] = '###'

            #UpdateGame()
            #print("D")

                    



            if starty > endy and BASE[starty-1][startx] in available_space:
                starty -= 1
            elif starty < endy and BASE[starty+1][startx] in available_space:
                starty += 1
            elif startx > endx and BASE[starty][startx-1] in available_space:
                startx -= 1
            elif startx < endx and BASE[starty][startx+1] in available_space:
                startx += 1
        BASE[starty][startx] = '###'
    
    elif path == 'L':

        starty = randint(current_room.y+1, current_room.length-2)
        startx = current_room.x-1
        endy = randint(closest_room.y+1, closest_room.length-2)
        endx = closest_room.width

        start_pos_x = min([startx, endx])
        start_pos_y = min([starty, endy])
        end_pos_x = max([startx, endx])
        end_pos_y = max([starty, endy])
        for y in range(start_pos_y, end_pos_y+1):
            for x in range(start_pos_x, end_pos_x+1):
                if room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] in SEEN:
                    SEEN.add(room_placements[y][x])
                    #UpdateGame2()
                    CreateSingularPath(totalrooms_for_changerooms[int(room_placements[y][x])], closest_room)
                    #print(SEEN)
                    return closest_room
                elif room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] not in SEEN:
                    SEEN.add(current_room)
                    closest_room = CreateSingularPath(current_room, totalrooms_for_changerooms[int(room_placements[y][x])])
                    
                    return closest_room
        BASE[starty][startx+1] = ' + '
        BASE[endy][endx-1] = ' + '
        DOORS_CREATING_ROOM[(endx-1, endy)] = closest_room
        DOORS_CREATING_ROOM[(startx+1, starty)] = current_room
        b = 0
        while startx != endx or starty != endy:
          
            b += 1
            if b == 1000:
                print(starty, endy, startx, endx)
                UpdateGame()

            BASE[starty][startx] = '###'
            #UpdateGame()
            #print("L")




            if startx > endx and BASE[starty][startx-1] in available_space:
                startx -= 1
            elif startx < endx and BASE[starty][startx+1] in available_space:
                startx += 1

            elif starty > endy and BASE[starty-1][startx] in available_space:
                starty -= 1
            elif starty < endy and BASE[starty+1][startx] in available_space:
                starty += 1
        BASE[starty][startx] = '###'

    elif path == 'U':

        starty = current_room.y-1
        startx = randint(current_room.x+1, current_room.width-2)
        endy = closest_room.length
        endx = randint(closest_room.x+1, closest_room.width-2)

        start_pos_x = min([startx, endx])
        start_pos_y = min([starty, endy])
        end_pos_x = max([startx, endx])
        end_pos_y = max([starty, endy])

        for y in range(start_pos_y, end_pos_y+1):
            for x in range(start_pos_x, end_pos_x+1):
                if room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] in SEEN:
                    SEEN.add(room_placements[y][x])
                    #UpdateGame2()
                    CreateSingularPath(totalrooms_for_changerooms[int(room_placements[y][x])], closest_room)
                    #print(SEEN)
                    return closest_room
                elif room_placements[y][x].isdigit() and room_placements[y][x] != current_room_array_pos and room_placements[y][x] != closest_room_array_pos and totalrooms_for_changerooms[int(room_placements[y][x])] not in SEEN:
                    SEEN.add(current_room)
                    closest_room = CreateSingularPath(current_room, totalrooms_for_changerooms[int(room_placements[y][x])])
                    
                    return closest_room
                
        BASE[starty+1][startx] = ' + '
        BASE[endy-1][endx] = ' + '
        DOORS_CREATING_ROOM[(endx, endy-1)] = closest_room
        DOORS_CREATING_ROOM[(startx, starty+1)] = current_room
        b = 0
        while startx != endx or starty != endy:
            
            b += 1
            if b == 1000:
                print(starty, endy, startx, endx)
                UpdateGame()

         
            BASE[starty][startx] = '###'
            #UpdateGame()
            #print("U")
                




            if starty > endy and BASE[starty-1][startx] in available_space:
                starty -= 1
            elif starty < endy and BASE[starty+1][startx] in available_space:
                starty += 1
            elif startx > endx and BASE[starty][startx-1] in available_space:
                startx -= 1
            elif startx < endx and BASE[starty][startx+1] in available_space:
                startx += 1 
        BASE[starty][startx] = '###'
    

    #UpdateGame()
    
    return closest_room

def FindClosestRoom(current_room):
    global total_rooms

    closest = 999
    save_close = closest
    for room in total_rooms:
        closest = min(closest, (abs(current_room.x-room.x)+abs(current_room.y-room.y)))
        if closest != save_close:
            closest_room = room
        save_close = closest
    return closest_room

def CreatePaths():
    global total_rooms

    times = 0
    while total_rooms and len(total_rooms) > 1:
        
        if times == 0:
            current_room = total_rooms.pop(0)
        else:
            current_room = closest_room
            #print(current_room.x, current_room.y, current_room.width, current_room.length)
            total_rooms.remove(current_room)
            #print(len(total_rooms))
        SEEN.add(current_room)
        closest_room = FindClosestRoom(current_room)

        #print(closest_room.x, closest_room.y, closest_room.width, closest_room.length)
        try:
            closest_room = CreateSingularPath(current_room, closest_room)
        except RecursionError as err:
            return False
        times += 1
    return True
        
def UpdateRooms():
    
        
    for _, room in enumerate(room_total.rooms):
        
        for y in range(room.y, room.length):
            for x in range(room.x, room.width):
                
                if y == room.y or y == room.length-1:
                    BASE[y][x] = '---'
                elif x == room.x or x == room.width-1:
                    BASE[y][x] = ' | '
                elif BASE[y][x] == Player.char:
                    continue
                else:

                    BASE[y][x] = ' · '
   
    for _, room in enumerate(room_total.rooms):
    
        for y in range(room.y, room.length):
            for x in range(room.x, room.width):
                room_placements[y][x] = str(_)


def UpdateCorridorsAndDoors():
    available = ['###', ' + ']
    if BASE[Player.y][Player.x+1] in available:
        MAP[Player.y][Player.x+1] = BASE[Player.y][Player.x+1]
    if BASE[Player.y][Player.x-1] in available:
        MAP[Player.y][Player.x-1] = BASE[Player.y][Player.x-1]
    if BASE[Player.y+1][Player.x] in available:
        MAP[Player.y+1][Player.x] = BASE[Player.y+1][Player.x]
    if BASE[Player.y-1][Player.x] in available:
        MAP[Player.y-1][Player.x] = BASE[Player.y-1][Player.x]

def CheckOpenRoom():
    if (Player.x, Player.y) in DOORS_CREATING_ROOM:
        room = DOORS_CREATING_ROOM[(Player.x, Player.y)]
        UpdateSpecificRoom(room)

def UpdateSpecificRoom(room):
 
    global count_room, new_floor_pos
    
    if room.show == False:
    
        count_room += 1
        room.show = True
        SpawnEnemy()

    if count_room == room_total.room_count:
        count_room += 1
        randx = randint(room.x+1, room.width-2)
        randy = randint(room.y+1, room.length-2)
        MAP[randy][randx] = ' ■ '
        BASE[randy][randx] = ' ■ '
        new_floor_pos = (randx, randy)
    for y in range(room.y, room.length):
        for x in range(room.x, room.width):

            if MAP[y][x] == Player.char or MAP[y][x] == ' ■ ':
                continue
            elif BASE[y][x] == ' + ':
                MAP[y][x] = ' + '
            elif y == room.y or y == room.length-1:
                MAP[y][x] = '---'
            elif x == room.x or x == room.width-1:
                MAP[y][x] = ' | '

            else:

                MAP[y][x] = ' · '
   
def CreateNewFloor():
    global new_floor_pos
    if (Player.x, Player.y) == new_floor_pos:
        Player.same_floor = False


########################################################################################################### SECTION DISPLAY


def UpdateGame():
    clear()
    #string = ''
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pos_x = x*3
            if MAP[y][x][1] == Player.char[1]:
                color_pair = curses.color_pair(3)
            elif MAP[y][x] == ' + ':
                color_pair = curses.color_pair(4)
            else:
                color_pair = curses.color_pair(1)
            if MAP[y][x] == ' 0 ':
                stdscr.addch(y, pos_x, ' ', color_pair)
                stdscr.addch(y, pos_x+1, ' ', color_pair)
                stdscr.addch(y, pos_x+2, ' ', color_pair)

            else:
      
                stdscr.addch(y, pos_x, MAP[y][x][0], color_pair)
                stdscr.addch(y, pos_x+1, MAP[y][x][1], color_pair)
                stdscr.addch(y, pos_x+2, MAP[y][x][2],   color_pair)
  
                    
    
    stdscr.addstr(40, 0, f"Floor: {Player.floor}", curses.color_pair(2))

    if Player.health <= 0:

        stdscr.addstr(40, 20, f"You have Died!", curses.color_pair(1))
        refresh()
        time.sleep(3)

    elif Player.health > 0:
        stdscr.addstr(40, 20, f"Player: Health:{Player.health} | Damage:{Player.damage}", curses.color_pair(1))
    if Player.opponent != None:
        if Player.opponent.health <= 0:
            stdscr.addstr(41, 20, f"You have killed the Enemy!", curses.color_pair(1))
            Player.opponent = None
            refresh()
            time.sleep(3)
        elif Player.fighting:
            stdscr.addstr(41, 20, f"Enemy: Health:{Player.opponent.health} | Damage:{Player.opponent.damage}", curses.color_pair(1))




    refresh()
    #print(f"Floor {Player.floor}")

def UpdateGame2():
    #os.system('cls')
    string = ''
    for y in range(HEIGHT):
        for x in range(HEIGHT):
            if ' ' not in room_placements[y][x]:
                print(f" {room_placements[y][x]} ", end='')
            else:
                print(room_placements[y][x], end='')
        print()

def UpdateGame3():
    #os.system('cls')
    string = ''
    for y in range(HEIGHT):
        for x in range(HEIGHT):
            if BASE[y][x] == ' 0 ':
                print('   ', end='')
            else:
                print(BASE[y][x], end='')
        print()

########################################################################################################### SECTION MAIN

def Main():
    global total_rooms, room_placements, MAP, BASE, DOORS_CREATING_ROOM, SEEN, count_room, new_floor_pos, obj, game


    FirstRoomCreation()
    num_rooms = randint(17, 20)
    for i in range(num_rooms):
        CreateNextRooms()
    room_total.room_count = len(room_total.rooms)
    total_rooms = room_total.rooms.copy()
    UpdateRooms()
    check_restart = CreatePaths()
    if check_restart:
        UpdateSpecificRoom(room_total.rooms[0])
        UpdateGame()
        #UpdateGame3()
        while Player.same_floor:
            time.sleep(0.01)
            PlayerMovement()

            check = CheckAttacking()
            if not check:
                game = False
                break

            UpdateCorridorsAndDoors()
            CheckOpenRoom()
            MoveEnemy()

            check = CheckAttacking()
            if not check:
                game = False
                break

            CreateNewFloor()
            UpdateGame()

        Player.floor += 1
        Player.x = 1
        Player.y = 1
        Player.same_floor = True    

if __name__ == '__main__':
    Player = CurrentPlayer(1, 1)
    while game:
        CurrentEnemies = []
        obj = ' · '
        new_floor_pos = (10000, 10000)
        count_room = 0
        SEEN = set()
        DOORS_CREATING_ROOM = defaultdict(tuple)
        BASE = MakeGrid()
        MAP = MakeGrid()
        room_placements = MakeGrid()
        room_total = AllRooms()
        total_rooms = None
        Main()

    clear()
    refresh()
