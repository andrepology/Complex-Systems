import numpy as np
from scipy.ndimage import generic_filter
import scipy.stats as sts
import time
import matplotlib.pyplot as plt
import tqdm



############################ Init a DEM with Direction, Slope Layers ###########################

def init_water(layer, fill = 1, kind = 'border'):
    # later is slice of CA with water heights

    water_layer = layer.copy()

    if kind == 'border':
    
        water_layer[0,:], water_layer[-1,:] = fill, fill
        water_layer[:,0], water_layer[:, -1] = fill, fill

    elif kind == 'everywhere':
        water_layer[:] = fill

    elif kind == 'circle':
        # generate a circle of rainfall in center
        pass
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
    

def resize_array(a, new_rows, new_cols): 
    '''
    This function takes an 2D numpy array a and produces a smaller array 
    of size new_rows, new_cols. new_rows and new_cols must be less than 
    or equal to the number of rows and columns in a.

    From https://stackoverflow.com/questions/8090229/resize-with-averaging-or-rebin-a-numpy-2d-array

    '''
    rows = len(a)
    cols = len(a[0])
    yscale = float(rows) / new_rows 
    xscale = float(cols) / new_cols

    # first average across the cols to shorten rows    
    new_a = np.zeros((rows, new_cols)) 
    for j in range(new_cols):
        # get the indices of the original array we are going to average across
        the_x_range = (j*xscale, (j+1)*xscale)
        firstx = int(the_x_range[0])
        lastx = int(the_x_range[1])
        # figure out the portion of the first and last index that overlap
        # with the new index, and thus the portion of those cells that 
        # we need to include in our average
        x0_scale = 1 - (the_x_range[0]-int(the_x_range[0]))
        xEnd_scale =  (the_x_range[1]-int(the_x_range[1]))
        # scale_line is a 1d array that corresponds to the portion of each old
        # index in the_x_range that should be included in the new average
        scale_line = np.ones((lastx-firstx+1))
        scale_line[0] = x0_scale
        scale_line[-1] = xEnd_scale
        # Make sure you don't screw up and include an index that is too large
        # for the array. This isn't great, as there could be some floating
        # point errors that mess up this comparison.
        if scale_line[-1] == 0:
            scale_line = scale_line[:-1]
            lastx = lastx - 1
        # Now it's linear algebra time. Take the dot product of a slice of
        # the original array and the scale_line
        new_a[:,j] = np.dot(a[:,firstx:lastx+1], scale_line)/scale_line.sum()

    # Then average across the rows to shorten the cols. Same method as above.
    # It is probably possible to simplify this code, as this is more or less
    # the same procedure as the block of code above, but transposed.
    # Here I'm reusing the variable a. Sorry if that's confusing.
    a = np.zeros((new_rows, new_cols))
    for i in range(new_rows):
        the_y_range = (i*yscale, (i+1)*yscale)
        firsty = int(the_y_range[0])
        lasty = int(the_y_range[1])
        y0_scale = 1 - (the_y_range[0]-int(the_y_range[0]))
        yEnd_scale =  (the_y_range[1]-int(the_y_range[1]))
        scale_line = np.ones((lasty-firsty+1))
        scale_line[0] = y0_scale
        scale_line[-1] = yEnd_scale
        if scale_line[-1] == 0:
            scale_line = scale_line[:-1]
            lasty = lasty - 1
        a[i:,] = np.dot(scale_line, new_a[firsty:lasty+1,])/scale_line.sum() 

    return a 





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


def init_grid(grid, **kwargs):
    # Initialise each layer of the grid
    # Check number of features in last column 
    # if 1, then it is a DEM

    if len(grid.shape) == 2:
        # Add additional columns for water column, direction, and slope
        dem  = grid
        grid = np.zeros((grid.shape[0], grid.shape[1], 4))
        grid[...,0] = dem    

    grid = grid.copy()

    fill = kwargs.get('fill', 1)
    kind = kwargs.get('kind', 'border')

    grid[...,1] = init_water(grid[...,1], fill = fill, kind = kind)
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

def get_direction_idxs(key, ij_dict):
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

def generate_flow_acc(dir_grid, n_iters = 10000, max_visits = 5, random = True):
    # Generate flow accumulation grid

    # Take a direction grid and generate flow accumulation grid
    N = dir_grid.shape[0]
    # Init flow accumulation matrix
    flow_acc = np.zeros((N,N))


    ij_dict = make_direction_dict()

    # pick a random cell
    x = np.random.randint(0, N)
    y = np.random.randint(0, N)

    for i in range(n_iters):

        # pick a random cell
        if random:
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
                dx, dy = get_direction_idxs(key, ij_dict)

                downstream_neighbor = [i+dx, j+dy]


                curr_cell = downstream_neighbor
                # if within limits
                try: 
                    flow_acc[curr_cell[0], curr_cell[1]] += 1
                    lim += 1
                except:
                    break
            else:
                # reached boundary/outlet, break
                break 

    return flow_acc


##### Run CA ##################################################################################

# Optimization stratgies:
# Cache neighbors. You will *never* need to look at taller neighbors, even when full. So, cache downstream neighbors instead of iterating through all.
def run_sim(basin, **kwargs):

    #### Parameters ####
    # difference threshold to limit oscillations
    tau = kwargs.get('tau', 0.1)
    t = kwargs.get('t', 1)

    edgel = 1
    area = edgel*edgel
    dist = edgel

    g = 10
    # Manning's roughness coefficient
    n = kwargs.get('n', 0.02)

    iter  = kwargs.get('iter', 60)
    tot_mass = np.zeros(iter)
    
    target_cell = kwargs.get('target_cell', [5,5])
    cell_water = np.zeros(iter)

    plot = kwargs.get('plot', False)

    if plot:
        interval = kwargs.get('interval', 10)
        frames = []
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        frames.append([plot_water(basin[...,0],basin[...,1], ax = ax)])

    else:
        frames  = None
        fig = None

    start = time.time()

    N = basin[...,0].shape[0]
    for it in tqdm.tqdm(range(iter)):
        water_heights = basin[...,0] + basin[...,1]

        # make a copy of basin
        basin_copy = basin[...,1].copy()

        for i in range(N):
            for j in range(N):
                central_height = water_heights[i,j]
                
                # store downstream neighbors
                v = []
                # calculate height difference between central cell and neighbors
                for dx in range(-1,2):
                    for dy in range(-1,2):
                        # if neighbor is in bounds
                        if 0 <= i+dx < N and 0 <= j+dy < N:
                            neighbor_height = water_heights[i+dx,j+dy]
                            # if neighbor is not no_data
                            if neighbor_height > 0:
                                # calculate difference
                                diff = central_height - neighbor_height
                                # exclude self
                                if diff - tau > 0:
                                    v.append(((i + dx, j + dy), diff * area))
                    
                # sum up differences to find total available volume
                v_tot_avail = np.sum([x[1] for x in v])

                # minimum in v
                try: 
                    v_min = min([x[1] for x in v])
                except: 
                    v_min = 0.01
                try:
                    v_max = max([x[1] for x in v])
                except:
                    # possibly np.inf
                    v_max = 1e4
                
                # calculate weight for each downstream neighbor
                weights = [(x[0], x[1]/(v_tot_avail + v_min)) for x in v]
                min_weight = v_min/(v_tot_avail + v_min)
                weights.append(((i,j),  min_weight))
        
                w_max = max([x[1] for x in weights])

                # do weights sum to 1
                #assert round(np.array([x[1] for x in weights]).sum()) == 1

                

                central_depth = basin[i,j,1]

                manning = 1/n * central_depth**(2/3) * np.sqrt(v_max / dist)
                # maximum permissible velocity
                vm = min(np.sqrt(central_depth*g), manning)

                inter_cell_max = vm * central_depth * t * edgel

                v_incell = central_depth * area

                ic_vol = min(v_incell, inter_cell_max/w_max, v_min)

                # update water column in neighbors
                for x in weights:
                    ii,jj = x[0]
                    if i == ii and j == jj:
                        # update water column in central cell
                        basin_copy[ii,jj] -= ic_vol/area
                    # update water column in neighbors
                    basin_copy[ii,jj] += ic_vol * x[1] / area

        # merge copy into basin
        basin[...,1] = basin_copy


        ##### For Analysis #####
        if plot:
            if it % interval == 0:
                frames.append([plot_water(basin[...,0],basin[...,1], ax = ax)])
        
        tot_mass[it]  = basin[...,1].sum()
        cell_water[it] = basin[target_cell[0], target_cell[1], 1]

    stop = time.time()
    duration = stop - start
    # write results to new line in results.txt
    with open('perf_results.txt', 'a') as f:
        f.write((f'{duration},{N},{iter},{tot_mass[0]},{tau},{t},{area} \n'))

    return {
        'tot_mass': tot_mass,
        'cell_water': cell_water,
        'duration': duration,
        'N': N,
        'iter': iter,
        'tau': tau,
        't': t,
        'area': area,
        'frames': frames,
        'fig': fig
    }