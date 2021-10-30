from numpy import array

def transpose_to_plot(data):
    return list(zip(*data))


def mins_to_hours(times):
    t = array(times)

    return t//60 