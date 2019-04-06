from lib.cell_tracking.track_data import TrackData
import skimage.io
import argparse
import lib.cell_tracking.cell_dimensions as cell_dimensions
import scipy.optimize
import numpy as np
    
from scipy import interpolate
    
import skimage.exposure
import skimage.filters
import skimage.morphology

def cell_fit_func_1(image, row, col, length, width, angle):
    pix = cell_dimensions.get_cell_pixels((row,col), length, width, angle, image.shape)
    return np.mean(image[pix])

# b = (10, 20)
# x = (b, 1,2,3,4,5)
# y = (x[0][0], x[0][1]) +  x[1:]
# a = np.array([1,2, 3])
# na = tuple(a)
# (b, *na)
# print(y)

def fit_cell(image, location_guess):
    def opt_func(x):
        print("trying", x)
        score = cell_fit_func_1(image, *x)
        print("score", score)
        return score
    center = location_guess[0]
    initial = center + location_guess[1:]
    bounds = [ (st-v, st + v) for (st, v) in zip(initial, [2, 2, 2, 1, 10])]
    print(bounds)
    # TNC #  sucked, didnt take big enough steps so never moved
    result = scipy.optimize.minimize(opt_func, initial, bounds=bounds, method="SLSQP", tol=1e-1)
    print(result.x)
    print("----------------")
    new_guess = result.x
    center = (new_guess[0], new_guess[1])
    rest = tuple(new_guess[2:])
    return (center, *rest)


def fit_cell_2(image, location_guess):
    center = location_guess[0]
    initial = center + location_guess[1:]
    bounds = [ (st-v, st + v) for (st, v) in zip(initial, [3, 3, 2, 1, 5])]
    testparams = [ np.linspace(a, b, 6) for a, b in bounds]
    
    pix = cell_dimensions.get_cell_pixels(*location_guess, image.shape)
    # print("INIT", np.mean(image[pix]))
    # print(len(testparams)) 
    ml = np.meshgrid(*testparams)
    #print(ml)
    #print(len(ml))
    zt = np.vstack([ m.flatten() for m in ml])
    result = np.zeros(zt.shape[1])
    #print(zt.shape)
    for i in range(zt.shape[1]):
        z = zt[:,i]
        pix = cell_dimensions.get_cell_pixels((z[0], z[1]), z[2], z[3], z[4], image.shape)
        result[i] = np.mean(image[pix])
    maxi = np.argmax(result)
    res = zt[:,maxi]
    cent = (res[0], res[1])
    rest = tuple(res[2:])
    #print("INIT", result[maxi])
    return  (cent, *rest )#,  result, zt

def np2ellipse(a):
    return (a[0], a[1]), a[2], a[3], a[4]

def fit_cell_4(image, previous_step, guess):
    res = guess
    cent = (res[0], res[1])
    rest = tuple(res[2:])
    return  (cent, *rest )

def fit_cell_3(image, previous_step, guess, width_bounds=(5.5, 7), grow_only=False):
    a_initial = np.array(previous_step[0] + previous_step[1:])
    print("P", a_initial)    
    mean_guess = np.vstack([a_initial, guess])
    print("I", guess)    
    mean_guess = mean_guess.mean(axis=0)
    print("M", mean_guess)
    bounds = [ (st-v, st + v) for (st, v) in zip(mean_guess, [2, 2, 2, 1, 5])]
    if width_bounds:
        min_width, max_width = width_bounds
        bounds[3] = (max(bounds[3][0],min_width), min(bounds[3][1], max_width))
    if grow_only:
        bounds[2] = (max(bounds[2][0], mean_guess[1]), bounds[2][1])

    #bounds = [ width bound 
    testparams = [ np.linspace(a, b, 5) for a, b in bounds]

    #pix = cell_dimensions.get_cell_pixels(*initial, image.shape)
    # print("INIT", np.mean(image[pix]))
    # print(len(testparams)) 
    ml = np.meshgrid(*testparams)
    #print(ml)
    #print(len(ml))
    zt = np.vstack([ m.flatten() for m in ml])
    result = np.zeros(zt.shape[1])
    #print(zt.shape)
    for i in range(zt.shape[1]):
        z = zt[:,i]
        pix = cell_dimensions.get_cell_pixels((z[0], z[1]), z[2], z[3], z[4], image.shape)
        result[i] = np.mean(image[pix])
    maxi = np.max(result)
    print("matches", np.sum(result==maxi))
    #print(zt.shape)
    res = zt[:, result==maxi].mean(axis=1)
    print("R", res)
    #res = zt[:,maxi]
    print(res)
    cent = (res[0], res[1])
    rest = tuple(res[2:])
    #print("INIT", result[maxi])
    return  (cent, *rest )#,  result, zt

def test_fit_cell_3():
    import matplotlib.pyplot as plt
    from matplotlib.patches import Ellipse
    test_pattern = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106//mean5/img_{:03d}_r.tif"
    initial_cell = ((472.7452535609982, 123.28937254520167), 11.466763546116828, 5.024010909687916, 73.73979529168807)
    guess_cell = np.array([470., 123, 10, 5, 73])

    image = skimage.io.imread(test_pattern.format(39))
    image = exagerate_image(image)

    fig, ax = plt.subplots(1, 1)
    e1 = Ellipse(*initial_cell, facecolor="none", edgecolor="blue")
    ax.add_patch(e1)
    new_cell = fit_cell_3(image, initial_cell, guess_cell)
    
    # pix = cell_dimensions.get_cell_pixels(*new_cell, image.shape)
    # image[pix] = 255//2
    ax.imshow(image, cmap=plt.cm.hot)

    print(new_cell)
    e2 = Ellipse(*new_cell, facecolor="none", edgecolor="green")
    ax.add_patch(e2)
    # ax.set_ylim(180, 60)
    # ax.set_xlim(350, 600)
    plt.show()

def test_fit_cell():
    import matplotlib.pyplot as plt
    #import cell_dimensions
    from matplotlib.patches import Ellipse
    test_pattern = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106//mean5/img_{:03d}_r.tif"
    #test_pattern = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/images/img_{:03d}_r.tif"
    #startframe = 39
    #cellid = 3
    #trackpath = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/cell_track.json"
    #td = TrackData(trackpath)
    #initial_cell = td.get_cell_params(startframe, cellid)
    # this is x, y
    initial_cell = ((472.7452535609982, 123.28937254520167), 11.466763546116828, 5.024010909687916, 73.73979529168807)
    print(initial_cell)
    #initial_cell

    image = skimage.io.imread(test_pattern.format(39))
    img_gauss = skimage.filters.gaussian(image, 1.1)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
    cell_disc = skimage.morphology.disk(7.5/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
    image = skimage.exposure.rescale_intensity(img_hat, out_range=(0, 255)).astype(np.uint8)
    #image = np.invert(image)

    # pix = cell_dimensions.get_cell_pixels(*initial_cell, image.shape)
    # image = np.zeros_like(image)
    # image[pix] = 255

    fig, ax = plt.subplots(1, 1)
    e1 = Ellipse(*initial_cell, facecolor="none", edgecolor="blue")
    ax.add_patch(e1)
    #new_cell, scores, pmap = fit_cell_2(image, initial_cell)
    new_cell = fit_cell_2(image, initial_cell)
    
    # pix = cell_dimensions.get_cell_pixels(*new_cell, image.shape)
    # image[pix] = 255//2
    ax.imshow(image, cmap=plt.cm.hot)

    print(new_cell)
    e2 = Ellipse(*new_cell, facecolor="none", edgecolor="green")
    ax.add_patch(e2)
    # ax.set_ylim(180, 60)
    # ax.set_xlim(350, 600)
    plt.show()

def exagerate_image(image):
    img_gauss = skimage.filters.gaussian(image, 1.1)
    img_gauss_01 = skimage.exposure.rescale_intensity(img_gauss, out_range=(0, 1.0))
    cell_disc = skimage.morphology.disk(7.5/2)
    img_hat = skimage.morphology.white_tophat(img_gauss_01, selem=cell_disc)
    image = skimage.exposure.rescale_intensity(img_hat, out_range=(0, 255)).astype(np.uint8)
    return image

def track_cell(track_data, cell_id, start_frame, end_frame, image_pattern):
    if not track_data.get_cell_state(start_frame, cell_id):
        raise ValueError("Start cell not defined")

    previous = track_data.get_cell_params(start_frame, cell_id)

    linear_guess = interpolate_tracks(track_data, cell_id, start_frame, end_frame)

    stop_states = ["sporulating", "spore", "divided", "disapeared"]
    n_stop_state = [ track_data.states[s] for s in stop_states]
    growing = int(track_data.states["growing"])

    for frame in range(start_frame+1, end_frame+1):
        print(frame)
        cell_state = track_data.get_cell_state(frame, cell_id)
        if cell_state == growing:
            previous = track_data.get_cell_params(frame, cell_id)
            #print("r")
        elif cell_state == 0:
            image = exagerate_image(skimage.io.imread(image_pattern.format(frame)))
             
            #new_cell = fit_cell_3(image, previous, linear_guess[:, frame])
            new_cell = fit_cell_4(image, previous, linear_guess[:, frame])
            track_data.set_cell_params(frame, cell_id, new_cell)
            track_data.set_cell_state(frame, cell_id, 1)
            previous = new_cell
        elif cell_state in n_stop_state: 
            stname = track_data.metadata["cell_states"][str(cell_state)]
            print("stopping because cell is '{0}' at frame {1}".format(stname, frame))
            break
        # else:
        #     print("unhandeld cell state")

    return track_data

keys = [(0, "col"), (1, "row"), (2, "length"), (3, "width"), (4, "angle")]
    
def cli_interpolate(track_data, cell_id, start_frame, end_frame):
    print("requested end frame")
    cid = str(cell_id)
    tr = interpolate_tracks(track_data, cell_id, start_frame, end_frame)
    print("the states of {0} are".format(end_frame, track_data.cells[cid]["state"][end_frame])) 
    print("the states of {0} are".format(end_frame +1, track_data.cells[cid]["state"][end_frame+1])) 
    for i, key in keys:
        track_data.cells[cid][key][start_frame:end_frame+1] = tr[i,start_frame:end_frame+1]
        print("setting props up to ", end_frame+1)
    
    print("length {0}, vs {1}".format(len(track_data.cells[cid]["state"][start_frame:end_frame]), len([1]*((end_frame+1)-start_frame))))
    track_data.cells[cid]["state"][start_frame:end_frame] = [1]*((end_frame)-start_frame)
    print("setting state up to ", end_frame)
    return track_data

def gui_interpolate(track_data, cell_id, end_frame):
    start_frame = track_data.cells[str(cell_id)]["state"].index(1)
    track_data = cli_interpolate(track_data, cell_id, start_frame, end_frame)
    return track_data

def test_gui_interpolate():
    trackpath = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/cell_track.json"
    td = TrackData(trackpath)
    cell_id = 9
    print(td.cells["9"]["length"])
    ntd = gui_interpolate(td, cell_id, 385)
    print(ntd.cells.keys())
    print(ntd.cells["9"]["length"])


def interpolate_tracks(track_data, cell_id, start_frame, end_frame):
    cell_states = np.array(track_data.cells[str(cell_id)]["state"])
    known_states = cell_states > 0
    known_states[:start_frame] = False
    known_states[end_frame+1:] = False

    ## angles are special with dicontinuities so we smooth them first
    angles = np.array(track_data.cells[str(cell_id)]["angle"])
    key_angles = angles[angles!=0]
    key_smooth = angle_discontinuity_smoother(key_angles)
    angles[angles!=0] = key_smooth
    track_data.cells[str(cell_id)]["angle"] = list(angles)

    known_frames, = np.where(known_states)
    print("KNOWN", known_frames)
    if known_frames < 2:
        return None
    results = np.zeros((5, len(cell_states)))
    fill = np.arange(start_frame, end_frame+1, 1)
    for i, k in keys:
        points = np.array(track_data.cells[str(cell_id)][k])[known_frames]
        func_interp = interpolate.interp1d(known_frames, points)
        results[i, start_frame:end_frame+1] = func_interp(fill)
    print("iterpolating up to last three ", fill[-3:])
    i = 4 #keys["angle"]
    ## convert back to 90 to -90
    for f in range(results.shape[1]):
        results[i, f] = cell_dimensions.limit_angle(results[i,f])
    
    return results
    
def monodirection(pa, ca, na):
    """
    The point of this function is as part of angle_discontinuity_smoother
    given a seqence of angles between 90 and -90 it returns a smoothed 
    function with no massive discontinuities so a sequence 
        [ 60, 80, -80, -60]  becomes  
        [ 60, 80, 100, 120] 
    """
    ## I feel this function is way to complicated and 
    ## there is probably one line of maths to do it perfectly and clearly.
    ## This was written while sick and evolved to the point where it worked. :()
    # def d(a):
    #     return np.rad2deg(a)
    # print("previous {0}, corrected {1}, new {2}".format(d(pa), d(ca), d(na)))
    diff = na - pa ## This differece is normall ok and the sign is the direction 
    direction = 1 # anticlockwise
    if (pa * na) < 0: # if there is a sign change
        if abs(pa) > np.pi/3 and abs(na) > np.pi/3: # if it was close to the vertical
            diff = (np.pi - abs(pa) - abs(na))
            if (pa < 0) and (na > 0):
                direction = -1 # discontinuity is going clockwise but diffence is not right
    ca = ca + (direction * diff)
    #print("new angle is {0}".format(d(ca)))
    return ca

def angle_discontinuity_smoother(sample_angles):
    pa = sample_angles[0]
    ca = pa
    compensated_angles = sample_angles.copy()
    for i, a in enumerate(sample_angles[1:], start=1):
        ca = monodirection(pa, ca, a)
        pa = a
        compensated_angles[i] = ca
    return compensated_angles


def test_interpolate_tracks():
    import matplotlib.pyplot as plt
    #startframe = 39
    cell_id = 3
    trackpath = "data/bio_film_data/data_local_cache/sp8_movies//del_fast_slow//time_lapse_sequence/fast_img_2_106/cell_track.json"
    td = TrackData(trackpath)
    #initial_cell = td.get_cell_params(startframe, cellid)
    # this is x, y
    #initial_cell = ((472.7452535609982, 123.28937254520167), 11.466763546116828, 5.024010909687916, 73.73979529168807)
    st = 24
    ed = 176
    interped = interpolate_tracks(td, cell_id, st, ed)
    
    cell_states = np.array(td.cells[str(cell_id)]["state"])
    known_states = cell_states > 0
    known_states[:st] = False
    known_states[ed+1:] = False
    known_frames, = np.where(known_states)
    points = np.array(td.cells[str(cell_id)]["length"])[known_frames]

    plt.plot(np.arange(st, ed, 1), interped[2,st:ed])
    plt.plot(known_frames, points, "o", color="red")
    plt.show()
    #initial_cell
    

def main():
    parser = argparse.ArgumentParser()
    #parser.add_argument('--image_pattern', type=str, required=True)
    parser.add_argument('--trackdata', type=str, required=True)
    parser.add_argument('--cell', type=int, required=True)
    parser.add_argument('--start_frame', type=int, default=0)
    parser.add_argument('--end_frame', type=int, default=None)
    pa = parser.parse_args()
        
    trackdata = TrackData(pa.trackdata)
    if pa.end_frame is None:
        pa.end_frame = trackdata.metadata["max_frame"]
    #new_track_data = track_cell(trackdata, pa.cell, pa.start_frame, pa.end_frame, pa.image_pattern)
    new_track_data = cli_interpolate(trackdata, pa.cell, pa.start_frame, pa.end_frame)
    new_track_data.save(pa.trackdata)


if __name__ == '__main__':
    test_angle_discontinuity_corrections()
    #smain()
    #test_gui_interpolate()
    #test_fit_cell_3()
    #test_interpolate_tracks()