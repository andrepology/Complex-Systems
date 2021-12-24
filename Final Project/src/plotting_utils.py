# Import everything 
from matplotlib import pyplot as plt
from matplotlib import cm

import numpy as np
from src.CA import make_direction_dict, get_direction_idxs, get_direction_keys

def dist(
    layer,
    benchmark = None,

    ax = None,
    title = "",
    bins=20, 
    color='w', 
    edgecolor='k', 
    figsize=(5,3), 
    ):

    if ax == None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(1,1,1)

    ax.hist(
        layer.flatten(),
        bins = bins,
        color = color, 
        hatch = '///',
        edgecolor = edgecolor)

    ax.set_title(
        title)

    if benchmark:
        ax.axvline(
            benchmark,
            color = 'red',
            label = f''
        )

        ax.plot(
            0,0,',',
            label = f'')
        ax.legend(loc = "upper left")

    adjust_spines(ax, ['bottom'])
    ax.set_xlabel(f'')
    
    plt.tight_layout()
    return ax
        
def adjust_spines(ax, spines, offset = 0):
        for loc, spine in ax.spines.items():
            if loc in spines:
                spine.set_position(('outward', offset))  # outward by offset points
                #spine.set_smart_bounds(True)
            else:
                spine.set_color('none')
        # turn off ticks where there is no spine
        if 'left' in spines:
            ax.yaxis.set_ticks_position('left')
        else:
            # no yaxis ticks
            ax.yaxis.set_ticks([])

        if 'bottom' in spines:
            ax.xaxis.set_ticks_position('bottom')
        else:
            # no xaxis ticks
            ax.xaxis.set_ticks([])


def plot_dem(dem, rotation = 30,  cmap = 'binary', ax = None):
    # A function that plots a DEM (or any 2d array) in 3d

    bins = dem.shape[0]
    dem = dem.flatten()

    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

    hist, xedges, yedges = np.histogram2d(dem, dem, bins=bins, range=[[0, bins], [0, bins]])

    # Figure out anchors for each bar
    xpos, ypos = np.meshgrid(xedges[:-1] + 0.1, yedges[:-1] + 0.1, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for each bar
    dx = dy = 1 * np.ones_like(zpos)
    dz = dem

    cmap = cm.get_cmap(cmap) # discrete colormap
    max_height = np.max(dz)   # max height
    min_height = np.min(dz)    
    # normalize each z to [0,1], and get their rgb values
    rgba = [cmap((k-min_height)/max_height) for k in dz] 

    lc = ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color = rgba, zsort='average')

    # show from side
    ax.view_init(elev=rotation, azim= -90 + rotation)
    # remove axes and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    return lc

# A function that plots a DEM heightmap in 4 angles
def orbit_dem(dem, n = 4, cmap = 'Greys_r'):
    # Plot a DEM from different n angles
    # init 3d subplots
    # A figure with a grid of subplots, no margin
    fig = plt.figure(figsize=(15,15))
    for i in range(n):
        ax = fig.add_subplot(n, 4, i+1, projection='3d')
        rot = 90 * i/n
        lc = plot_dem(dem, rot, cmap, ax)

    # Make layout compact
    fig.colorbar(lc, ax = ax, shrink = 0.8)
    fig.tight_layout()

    return fig


def plot_water(dem, water, rotation = 30,  cmap = 'binary', ax = None):
    # A function that plots a DEM (or any 2d array) in 3d

    bins = dem.shape[0]
    dem = dem.flatten()

    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

    hist, xedges, yedges = np.histogram2d(dem, dem, bins=bins, range=[[0, bins], [0, bins]])

    # Figure out anchors for each bar
    xpos, ypos = np.meshgrid(xedges[:-1] + 0.1, yedges[:-1] + 0.1, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for each bar
    dx = dy = 1 * np.ones_like(zpos)
    dz = dem

    cmap = cm.get_cmap("Greys") # discrete colormap
    max_height = np.max(dz)   # max height
    min_height = np.min(dz)    
    # normalize each z to [0,1], and get their rgb values
    rgba = [cmap((k-min_height)/max_height) for k in dz] 

    lc = ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color = rgba, alpha = 1, zsort='average')

    # show from side
    ax.view_init(elev=rotation, azim= -90 + rotation)
    # remove axes and ticks
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])


    # Now stack the water map
    bins = water.shape[0]
    water = water.flatten()

    if not ax:
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')

    hist, xedges, yedges = np.histogram2d(water, water, bins=bins, range=[[0, bins], [0, bins]])

    # Figure out anchors for each bar
    xpos, ypos = np.meshgrid(xedges[:-1] + 0.1, yedges[:-1] + 0.1, indexing="ij")
    xpos = xpos.ravel()
    ypos = ypos.ravel()
    zpos = 0

    # Construct arrays with the dimensions for each bar
    dx = dy = 1 * np.ones_like(zpos)
    dz1 = water

    cmap = cm.get_cmap("Blues") # discrete colormap
    max_height = np.max(dz1)   # max height
    min_height = np.min(dz1[dz1 > 1e-5])   
    #normalize each z to [0,1], and get their rgb values
    rgba = ["blue" if k > 1e-2 else (1,1,1,0) for k in dz1] 

    # stack over previous 3d barplot
    lc = ax.bar3d(xpos, ypos, dz, dx, dy, dz1, color = rgba, alpha = 1, zsort='average')

    return lc




# transform ij indexing to cartesian xy
def ij_to_xy(ij):
    # Take an i,j tuple and return x,y tuple
    i,j = ij[0], ij[1]

    return (j, -i)


def quiver_directions(dir_grid):
    # iterate through dir_grid
    scale = dir_grid.shape[0]*1.4
    length = dir_grid.shape[0]
    N = dir_grid.size

    X, Y = np.meshgrid(np.arange(length), np.arange(length))
    U = np.zeros(N)
    V = np.zeros(N)

    ij_dict = make_direction_dict()

    for i in range(length):
        for j in range(length):
            cell = int(dir_grid[i,j])


            # get first key
            keys = get_direction_keys(cell)
            if not keys:
                continue

            # get i,j of key
            ii = 0
            jj = 0
            for key in keys:
                t_ii, t_jj = get_direction_idxs(key, ij_dict)
                ii += t_ii
                jj += t_jj

            # nomalize
            magnitude = np.sqrt(ii**2 + jj**2)
            ii /= magnitude
            jj /= magnitude

          
            

            # get arrow direction
            u, v = ij_to_xy((ii,jj))

            idx = np.ravel_multi_index((i,j), dir_grid.shape)

            U[idx] = u 
            V[idx] = v 

    # quiver plot small arrows
    plt.quiver(X, Y, U, V, scale = scale)
    # set title
    plt.title('Flow Directions')

    return u,v


#### DEPRECATED ####

# DEPRECATED

LAYER_NAMES = {
    0 : "Digital Elevation Model",
    1 : "Water Column Height (m)",
    2 : "FLOODED? (bool)",
    3 : "Direction (int)",
    4 : "Slope (degrees)"
}

def view_layer(grid, layer):
    fig = plt.figure(figsize=(6,5))
    N = grid.shape[0]

    ax = fig.add_subplot(1,1,1)
    lc = ax.contourf(range(N), range(N), grid[:,:,layer], 50, cmap = 'magma')
    fig.colorbar(lc, ax=ax, shrink = 0.8)

    ax.set_xticks(range(0,grid.shape[1]))
    ax.set_yticks(range(0,grid.shape[0]))
    ax.grid(alpha = 0.2)

def view_3d_layer(grid, layer):
    fig = plt.figure(figsize=(6,5))

    N = grid.shape[0]

    ax = fig.add_subplot(1,1,1, projection = '3d')
    lc = ax.contourf(range(N), range(N), grid[:,:,layer], 50, cmap = 'magma')
    fig.colorbar(lc, ax=ax, shrink = 0.8)

    ax.set_xticks(range(0,grid.shape[1]))
    ax.set_yticks(range(0,grid.shape[0]))
    ax.grid(alpha = 0.2)

def view_slice(grid, slice = None, ax = None):

    # Plot a bar chart of heights
    # Brown: elevation 
    # Blue: water
    if slice == None:
        slice = grid.shape[0]//2

    if ax == None:
        fig, ax = plt.subplots()

    N = grid.shape[0]
    ground    = grid[slice,:,0]
    water_col = grid[slice,:,1]

    # Plot Ground
    # plot a bar chart of heights with wave hatching

    ax.bar(
        x = range(1,N+1), 
        height = ground,
        hatch = '///',
        color = 'brown')

    # Plot water column
    ax.bar(
        x = range(1,N+1),
        height  = water_col,
        bottom  = ground,
        hatch = '~'
    )

    lower = 0.95*(min(ground) + min(water_col))
    upper = 1.05*(max(ground) + max(water_col))
    ax.set_ylim((lower,upper))

    # For anim
    return ax



# plot each column in res['frac_flooded']
def flood_plot(results):
    # init figure
    fig, ax = plt.subplots(1,1, figsize = (6,4), dpi = 100)
    # for each column in frac flooded, plot
    for i in range(results['frac_flooded'].shape[1]):
        ax.plot(
            results['frac_flooded'][:,i], 
            '-',
            linewidth = 1,
            label = f'{results["thresholds"][i]} m')

    ax.legend()
    # add labels
    t = results['t']
    ax.set_xlabel(f'Iterations ({ t }s)')
    ax.set_ylabel('Fraction of Cells Flooded')
    
    cells = results["N"] * results["N"]
    area = results["area"] * cells / 1e6
    # add commas to area
    area = f'{area:,}'
    cells = f'{cells:,}'
    sim_params = f' Fraction Flooded vs Time \n  Cells = { cells  } Area = {area} km^2 '

    ax.set_title(f'{sim_params}')
    plt.close()
    return fig


# plot with 2 y axis
def diagnostic_plot(results):
    # plot mean flow late and totmass (should be conserved)
    # results is dict of sim variables
    fig, ax = plt.subplots(1,1, figsize = (5,5), dpi = 100)
    p1 = ax.plot(
        results['tot_mass'],
        '-',
        linewidth = 0.5,
        label = 'Total Water Volume $(m^3)$')
    # on different y axis plot flow_rate
    twin = ax.twinx()

    p2 = twin.plot(
        results['flow_rate'], 
        '-g',
        linewidth = 0.8,
        label = 'Mean Flow Rate $(m^3/t)$',
    )
    # make left yaxis labels red
    ax.yaxis.label.set_color('red')
    ax.legend(handles = [p1[0], p2[0]])


    # set twin ylabel
    ax.set_ylabel('Total Water Volume $(m^3)$', color = 'black')
    twin.set_ylabel('Mean Flow Rate $(m^3/t)$', color = 'green')

    t = results['t']
    # set xlabel
    ax.set_xlabel(f'Iterations $({ t } s)$')

    cells = results["N"] * results["N"]
    area = results["area"] * cells / 1e6
    # add commas to area
    area = f'{area:,}'
    cells = f'{cells:,}'
    sim_params = f' Total Water & Mean Flow Rate vs Time \n  Cells = { cells  } Area = {area} km^2 '

    # pad title
    ax.set_title(f'{sim_params}', pad = 15)

    # do not show figure
    plt.close(fig)

    return fig
