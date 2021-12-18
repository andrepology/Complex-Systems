import numpy as np
from scipy.ndimage import generic_filter
import scipy.stats as sts

############################ Init a DEM with Direction, Slope Layers ###########################

def init_water(layer, fill = 1):
    # grid is a 1D slice
    # fill is the water column height to fill perimeter with
    water_layer = layer.copy()
   
    water_layer[0,:], water_layer[-1,:] = fill, fill
    water_layer[:,0], water_layer[:, -1] = fill, fill

    return water_layer

directions = {
    0: 1,
    1: 2,
    2: 4,
    3: 8,
    5: 16,
    6: 32, 
    7: 64, 
    8: 128}

def find_direction(window, method  = 'Dinf'):
    # alias: Dinf in literature. Direct flow to lowest neighbor(s)

    # Keys for neighbor positions relative to kernel
    # 0 1 2
    # 3 4 5
    # 6 7 8 
    
    # window has flat array positions
    center = window[4]
    lower_cells = np.where(window < center, window, float('inf'))
    
    # Get indices of downstream cells
    idxs = np.where(lower_cells < float('inf'))
    idxs = list(*idxs)
    
    return np.sum([directions[i] for i in idxs]) if len(idxs) > 0 else 0

def init_directions(layer, method = 'Dinf'):
    # idx for elevation values
    moore_kernel = np.ones((3,3)) 
    
    # TODO: better cval for constant mode
    # maybe repeat? 
    directions = generic_filter(
                    layer,
                    find_direction,
                    footprint = moore_kernel,  
                    mode = 'constant',
                    cval = np.nan)

    # Set border of directions to 0
    directions[0,:] = 0
    directions[:,0] = 0
    directions[-1,:] = 0
    directions[:,-1] = 0
    
    return directions

def calculate_slope(window, d = 1, degrees = True):
    # d is width of a cell

    # 0 1 2 3 [4] 5 6 7 8
    # 0 1 2 3     4 5 6 7

    # if central cell is no_data, return itself
    if window[4] == np.nan or window[4] < 0:
        return window[4]
    
    df_dx = (np.sum(window[[2, 5, 5, 8]])  - np.sum(window[[0, 3, 3, 6]]))/8*d
    df_dy = (np.sum(window[[6, 7, 7, 8]])  - np.sum(window[[0, 1, 1, 2]]))/8*d

    rise_run = np.sqrt(df_dx**2 + df_dy**2)

    if degrees:
        # rise/run -> value in degrees 
        # 57.29578 ~ 180/pi (acceptable precision)
        return np.arctan(rise_run) * 57.29578

    else:
        #return absolute value of rise/run
        return rise_run

def init_slope(dem_layer):
    # Fill out gradients (degrees) for each cell in grid
    # idx for elevation values

    moore_kernel = np.ones((3,3))    
    slopes = generic_filter(
                dem_layer,
                calculate_slope,
                footprint = moore_kernel,  
                mode = 'nearest',
                cval = 0)

    return slopes
    

############################ Init a toy DEM ###################################################


def create_basin(N = 5, layers = 4, seed = 1):
    # Return a toy elevation model
    # layers can be :[DEM, WaterCol, Flooded?, Direction, Slope]
    
    #set seed for reproducibility
    np.random.seed(seed)

    grid = np.zeros((N,N,layers))

    for i in range(N):
        for j in range(N):
            # Use small scale as tally is easier for testing
            grid[i,j,0] -= 50**2*sts.norm.pdf(i*2, loc = N/2, scale = N) + \
                        50**2*sts.norm.pdf(j*2, loc = N/2, scale = N) - 500

    '''
    dem = np.array(
    [
        [10,10,10,10,10],
        [10,8 ,8 ,8 ,10],
        [10,8 ,5,8 ,10],
        [10,8 ,8 ,8 ,10],
        [10,10,10,10,10],
    ]
    )

    grid[...,0] = dem'''

    return init_grid(grid)

def create_pyramid(N = 5):
    pass

def init_grid(grid):
    # Initialise each layer of the grid
    grid = grid.copy()

    grid[...,1] = init_water(grid[...,1])
    grid[...,2] = init_slope(grid[...,0])
    grid[...,3] = init_directions(grid[...,0])
    
    return grid
    


############################ Testing ###########################################################

def get_direction_keys(num):
    # get direction key(s) of lowest neighbor(s)
    binary = np.binary_repr(num, width=8)
    # invert binary convert to list
    binary = list(map(int, binary[::-1]))
    # find all 1s
    indices = np.where(np.array(binary) == 1)

    return list(indices[0]) if len(indices[0]) > 0 else None

def get_direction_idxs(key):
    # unpack ij_dict to displacement indices
    return ij_dict[key][0], ij_dict[key][1]

def make_direction_dict():
        # 3x3 array 0 to 8
    i = np.array([-1,-1,-1, 0, 0, 0, 1, 1, 1])
    j = np.array([-1, 0, 1,-1, 0, 1,-1, 0, 1])

    # stack i and j
    ij = np.stack((i,j), axis = 1)

    # save each row as value in dict
    ij_dict = {k:list(v) for k,v in enumerate(ij)}

    return ij_dict

def generate_flow_acc(dir_grid, n_iters = 10000, max_visits = 5):

    # Take a direction grid and generate flow accumulation grid
    N = dir_grid.shape[0]
    # Init flow accumulation matrix
    flow_acc = np.zeros((N,N))

    global ij_dict

    ij_dict = make_direction_dict()

    for i in range(n_iters):

        # pick a random cell
        x = np.random.randint(0, N)
        y = np.random.randint(0, N)

        curr_cell = [x,y]
    
        lim = 0
        while lim < max_visits:
            i,j  = curr_cell[0], curr_cell[1]
            direction = int(dir_grid[i,j])
            # Get directions of flow
            dir_keys = get_direction_keys(direction)

            if dir_keys:
                # performance: choose a neighbor to flow to first
                key_idx = np.random.choice(len(dir_keys))
                key = dir_keys[key_idx]
                dx, dy = get_direction_idxs(key)

                downstream_neighbor = [i+dx, j+dy]

                curr_cell = downstream_neighbor
                flow_acc[curr_cell[0], curr_cell[1]] += 1
                lim += 1
            else:
                # reached boundary/outlet, break
                break 

    return flow_acc