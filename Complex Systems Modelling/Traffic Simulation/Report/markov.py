import matplotlib.pyplot as plt
import matplotlib

def make_markov(nums):
    #normalize recorded cars
    for i in range(len(nums)):
        total = sum(nums[i])
        for j in range(len(nums[i])):
        #normalize
            nums[i][j] = nums[i][j]/total
    
    return nums

def cars_over_time(steps, states, M_m,u,sims = 200):

    states_dict = dict(enumerate(states))

    plot_data = {k: {} for k in states}
    
  
    for sim in range(sims):
        u = vector([randint(20,50) for i in range(M_m.ncols())])
        for i in range(steps):
            next_val = (M_m^i)*u
        #retrieve 
            for j in range(len(states)):
                if sim in plot_data[states_dict[j]].keys():
                    plot_data[states_dict[j]][sim].append(N(next_val[j], digits = 3))
                else:
                    plot_data[states_dict[j]][sim] = [next_val[j]]
    
    
    
    fig, axs = plt.subplots(2,12, sharex = True, sharey = True, figsize = (12,6))
                
    x = range(steps)
    cmap = matplotlib.cm.get_cmap('Spectral')
    
    for n,key in list(enumerate(plot_data.keys()))[:12]:
        for sim in plot_data[key].keys():
            axs[0,n-1].plot(x,plot_data[key][sim], color = cmap(1/(2*n+1)), alpha = 0.2, linewidth=0.5)
            axs[0,n-1].set_title(f"{key}")
    for n,key in list(enumerate(plot_data.keys()))[12:]:
        for sim in plot_data[key].keys():
            #color as fn of key
            axs[1,n-12].plot(x,plot_data[key][sim], color = cmap(1/2*n), alpha = 0.2, linewidth=0.5)
            axs[1,n-12].set_title(f"{key}")
    
   

    #sanity check: end values ~ graph
    print([f"{key}:{plot_data[key][1][-1]}" for key in plot_data.keys()])
    
    fig.add_subplot(111, frameon=False)
    # hide tick and tick label of the big axis
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)
    plt.xlabel("Minutes")
    plt.ylabel("Cars on Road Segment")
    

    plt.tight_layout()
    plt.savefig("longterm.png", dpi=200)


states = [
'Oranien_1', 'Oranien_2', 'Oranien_3', 'Oranien_4', 'Oranien_5', 'Oranien_6', 'Oranien_7', 'Dresden_1', 'Dresden_2', 'Orplatz_1', 'Orplatz_2', 'Orplatz_3', 'Orplatz_4', 'Orplatz_5', 'Terminal 1', 'Terminal 2', 'Terminal 3', 'Terminal 4', 'Terminal 5', 'Generator 1', 'Generator 2', 'Generator 3', 'Generator 4'
]

cars = [[1., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0.,
        0., 0., 0., 1., 0., 0., 0.],
       [0., 1., 1., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 1., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 1., 1., 0., 0., 1., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [1., 0., 0., 1., 1., 0., 0., 1., 0., 1., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 1., 1., 0., 1., 0., 0., 0., 1., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 1., 0., 0., 1., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 1., 0., 0.],
       [0., 0., 0., 0., 1., 0., 1., 0., 0., 0., 0., 0., 1., 0., 0., 1.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 1., 0., 0., 0., 1., 1., 0., 0., 0., 1., 0., 0., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 0., 0., 0.,
        1., 0., 0., 0., 0., 0., 0.],
       [0., 1., 0., 1., 0., 0., 0., 0., 0., 1., 0., 1., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 1., 0.],
       [0., 0., 0., 0., 1., 1., 0., 0., 0., 0., 1., 0., 1., 0., 0., 0.,
        0., 1., 0., 0., 0., 0., 0.],
       [1., 0., 1., 0., 0., 0., 0., 0., 0., 1., 0., 1., 0., 0., 0., 0.,
        0., 0., 1., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 1., 1., 0., 0., 1., 0., 1., 1., 0., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 1., 0., 0.,
        0., 0., 0., 0., 0., 0., 1.],
       [0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 1.,
        0., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0.,
        1., 0., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0.,
        0., 1., 0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0.,
        0., 0., 1., 0., 0., 0., 0.],
       [1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 1., 0., 0., 0.],
       [0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 1., 0., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0., 0., 0., 0., 0.,
        0., 0., 0., 0., 0., 1., 0.],
       [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1., 0., 0.,
        0., 0., 0., 0., 0., 0., 1.]]


Mark = make_markov(cars)

M_m = matrix(Mark).transpose()

#Set initial distribution
u = vector([randint(40,80) for i in range(23)])

cars_over_time(10, states, M_m, u)



