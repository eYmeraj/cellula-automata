import numpy as np
import os, sys
import itertools
import glob


def ca_rules(alive:str, born:str, states:str = '5'):

    states = int(states)

    alive = alive.split(',')
    born = born.split(',')
    
    rule_alive = [False] * 27
    rule_born  = [False] * 27

    for alive_interval in alive:
        if '-' in alive_interval:
            lb,ub = alive_interval.split('-')
            lb,ub = int(lb), int(ub)
            for idx in range(lb, ub+1):
                rule_alive[idx] = True
        else:
            rule_alive[int(alive_interval)] = True
    
    for born_interval in born:
        if '-' in born_interval:
            lb,ub = born_interval.split('-')
            lb,ub = int(lb), int(ub)
            for idx in range(lb, ub + 1):
                rule_born[idx] = True
        else:
            rule_born[int(born_interval)] = True

    return rule_alive, rule_born, states
    

def get_random_coord(count: int):
    global size
    global ndims 
    assert (size**ndims) > count, 'Count > Grid Points'
    coord_list = set()
    lb = 1
    ub = size - 1
    for _ in range(int(count)):
        coord_list.add(tuple(np.random.randint(lb, ub, ndims)))

    return coord_list

def initialize_grid():
    global size
    global ndims 

    grid = np.zeros((tuple([size for _ in range(ndims)])))

    coord_list = itertools.product(np.arange(size//2 - 10, size//2 + 10), repeat = 3)
    for coordinates in coord_list:
        grid[coordinates] = np.random.choice([0,states - 1])

    return grid

def alive_neighbors(grid, coords):
    x,y,z = coords
    neighbors = grid[x-1:x+2,y-1:y+2,z-1:z+2].copy()
    neighbors[1,1,1] = 0

    if vn:
        number_alive_neighbors = 0
        neighbors_coords = [
            (x + 1,y,z),
            (x - 1,y,z),
            (x,y + 1,z),
            (x,y - 1,z),
            (x,y,z + 1),
            (x,y,z - 1)
        ]
        for neigh in neighbors_coords:
            number_alive_neighbors += int(grid[neigh] == states - 1)
        return number_alive_neighbors    

    number_alive_neighbors = (neighbors == (states - 1) ).sum()
    return number_alive_neighbors

def write_to_file(coordinates, iteration, current_state):
    os.makedirs('out', exist_ok=True)
    filename = f'out/ca_p{int(current_state)}_i{iteration}.obj'
    
    add_verices = np.array([[0,0,0],
                            [1,0,0],
                            [0,1,0],
                            [1,1,0],
                            [0,0,1],
                            [1,0,1],
                            [0,1,1],
                            [1,1,1]])

    if not os.path.exists(filename):
        open(filename,'w').close()
            
    with open(filename,'a') as f:
        for vertex in add_verices:
            to_write = coordinates + vertex
            f.write("v {} {} {}\n".format(*to_write/(size//3)))


def process_grid(grid, iteration):

    global rule_born
    global rule_alive
    global states

    new_grid = grid.copy()

    for i,j,k in list(itertools.product(np.arange(1,grid.shape[0]-1),repeat= 3)):
        current_state = grid[i,j,k]
        number_alive_neighbors = alive_neighbors(grid,(i,j,k))

        if current_state == states - 1 and rule_alive[number_alive_neighbors]:
            write_to_file([i,j,k], iteration, current_state)

        elif current_state == 0 and rule_born[number_alive_neighbors]:
            new_grid[i,j,k] = states - 1 
            write_to_file([i,j,k], iteration, states - 1)
    
        elif current_state > 0:
            new_grid[i,j,k] -= 1
            if new_grid[i,j,k] != 0:
                write_to_file([i,j,k], iteration, current_state - 1)
    return new_grid
    
def faces(num_cubes):
    return np.array([[6, 8, 7, 5],
            [3, 4, 8, 7],
            [1, 2, 4, 3],
            [1, 2, 6, 5],
            [2, 4, 8, 6],
            [1, 3, 7, 5]]) + (8 * num_cubes)


if __name__ == '__main__':
    size, ndims = 100, 3
    vn = False

    # ----------------------------------------------------------------
    rule_alive, rule_born, states = ca_rules('4', '4', '5')
    # ----------------------------------------------------------------
    # rule_alive, rule_born, states = ca_rules('2,6,9', '4,6,8-9', '10')
    # ----------------------------------------------------------------
    rule_alive, rule_born, states = ca_rules('9-26', '5-7,12-13,15', '5')
    # ----------------------------------------------------------------
    # rule_alive, rule_born, states = ca_rules('0-6', '1,3', '2')
    # vn = True
    # ----------------------------------------------------------------


    print('Defined Rules')
    grid = initialize_grid()
    print('Initialised Grid')

    for old in glob.glob(f"out/ca_*"):
        os.remove(old)

    print('Removed files')
    for iteration in range(1,100):
        if np.all(grid == 0):
            break
        print('============= ITERATION {} ============'.format(iteration))
        grid = process_grid(grid, iteration)
        for state_k in range(1,states):
            matched_files = glob.glob(f"out/ca_p{state_k}_i{iteration}.obj")
            print(matched_files)
            for file in matched_files:
                with open(file,'r') as f:
                    tot_cubes = len(f.readlines())//8

                with open(file,'a') as f:
                    if vn:
                        mat_to_use = (iteration - 1)%7 + 1
                        f.write(f'mtllib materials.mtl\nusemtl mat{int(mat_to_use)}\n')
                    else:
                        f.write(f'mtllib materials.mtl\nusemtl mat{int(state_k)}\n')
                    for num_cubes in range(tot_cubes):
                        for fc in faces(num_cubes):
                            to_write = "f {} {} {} {}".format(*fc)
                            f.write(to_write + '\n')