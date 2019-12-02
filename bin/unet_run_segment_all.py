import numpy as np
import scipy.io
import skimage.exposure
import skimage.util
from keras import backend as K
import keras.models

def proc_image(img):
    gimg = skimage.filters.gaussian(img, sigma=1.2).astype(np.float32)
    ri_img = skimage.exposure.rescale_intensity(gimg, in_range="image", out_range=(0, 1))
    return ri_img

def creat_data_sets_steps(im, size = 64, rotations=4, step=64):
    im = np.atleast_3d(im)
    dims = im.shape[-1]
    sliceup = skimage.util.view_as_windows(im, (size,size, dims), step=step)
        
    Xlist = []
    out_put_shape = (dims, 64, 64)
    def reshape(_, r, c, i):
        rotated = np.rot90(sliceup[r, c, 0, :, :, :], k=i, axes=(0,1))
        swapped = np.empty(out_put_shape)
        for d in range(dims):
            swapped[d, :, :] = rotated[:,:,d]
        return swapped 
    grid_r, grid_c = sliceup.shape[:2]
    cords = [ (r, c) for c in range(grid_c) for r in range(grid_r)]

    for i in range(rotations):
        al_the_ims = [ reshape(sliceup, r, c, i)  for r, c in cords]
        Xlist += [ np.stack(al_the_ims, axis = 0) ] 
        
    return np.vstack(Xlist), sliceup.shape

def stich_up_with_step(Y, grid_shape, step, orig_shape):
    grid_r, grid_c, _, rows, cols, _ = grid_shape
    #print(Y.shape)
    dims = Y.shape[1]
    output = np.zeros((dims, *orig_shape), Y.dtype)
    #print(output.shape)
    locations = [ (r, c) for c in range(grid_c) for r in range(grid_r)]
    #print(locations)
    for x, (r, c) in enumerate(locations):
        #print((c*size),(c+1)*size)
        output[:, r*step:(r*step)+rows, (c*step):(c*step)+1*cols] = Y[x, :, :,:]
    #print(x)
    return output

def predict_on_shifted_images(img, model):
    test_images = {}
    pred_images = {}
    r_start = 0
    r_end = 16
    c_start = 0 
    c_end = 32

    for r_shift in [0, 32]:
        for c_shift in [0, 32]:
            test_sub_section = proc_image(img)#[r_start*64+r_shift:r_end*64+r_shift, c_start*64+c_shift:c_end*64+c_shift])
            X_test, test_shape = creat_data_sets_steps(test_sub_section, size=64, rotations=1, step=64)
            test_images[(r_shift, c_shift)] = test_sub_section
            Y_pred = model.predict(X_test)
            pred_restitch = stich_up_with_step(Y_pred, test_shape, 64, test_sub_section.shape)
            pred_images[(r_shift, c_shift)] = pred_restitch

    combine_test = np.ones((1, *test_images[(0,0)].shape, len(test_images)), test_images[(0,0)].dtype) * np.nan
    combine_pred = np.ones((2, *test_images[(0,0)].shape, len(test_images)), test_images[(0,0)].dtype) * np.nan
    print(combine_test.shape)

    for i, (shifts, image) in enumerate(test_images.items()):
        print(i)
        pred = pred_images[shifts]
        r_shift, c_shift = shifts
        r, c, = test_images[(0,0)].shape
        r_start, r_end = r_shift, r
        c_start, c_end = c_shift, c
        print((r_start,r_end), (c_start,c_end), (0,r-r_shift), (0,c-c_shift))
        combine_test[0, r_start:r_end, c_start:c_end, i] = image[0:r-r_shift, 0:c-c_shift]
        combine_pred[:, r_start:r_end, c_start:c_end, i] = pred[:, 0:r-r_shift, 0:c-c_shift]


    #test_cells = np.nanmax(combine_test[0,:,:,:],axis=2)
    pred_cells = np.nanmean(combine_pred[0,:,:,:],axis=2)
    pred_cents = np.nanmean(combine_pred[1,:,:,:],axis=2)
    return np.stack([pred_cells, pred_cents], axis=0)

# #%%
# import numpy as np
# #%%
# a = np.array([[1,2,3], [4,5,6], [7,8,9]])
# b = np.array([[1,2,3], [4,5,6], [7,8,9]])*10

# print(a.shape)
# print(b.shape)
# #%%

def load_model():
    K.set_image_data_format("channels_first")
    img_rows, img_cols = 64, 64
    input_size = (1, img_rows, img_cols)

    #model = try_model(input_size=input_size, output_dim=2)
    model = keras.models.load_model("unet_2d/model_2.h5")
    return model


def simple_seg(im, model):
    X_test, test_shape = creat_data_sets_steps(proc_image(im), size=64, rotations=1, step=64)
    Y_pred = model.predict(X_test)
    test_restitch = stich_up_with_step(Y_pred, test_shape, 64, im.shape)
    return test_restitch #[0,:,:], test_restitch[1,:,:]

def main():
    basedir="/media/nmurphy/BF_Data_Orange/proc_data/iphox_movies/"
    dataset="BF10_timelapse"
    lookat="Column_2"

    model = load_model()

    image_path= "{basedir}/{dataset}/{lookat}/{lookat}_t{{0:03d}}_ch00.tif".format(**{"basedir":basedir, "dataset":dataset, "lookat":lookat})
    out_path= "{basedir}/{dataset}/{lookat}/{{type}}/{lookat}_t{{frame:03d}}.tif".format(**{"basedir":basedir, "dataset":dataset, "lookat":lookat})
    for frame in range(0, 560):
        print(frame)
        im = skimage.io.imread(image_path.format(frame))
        # pred_tile = predict_on_shifted_images(im, model)
        # print(out_path.format(**{"frame":frame, "seg":"cell", "type":"tile"}))
        # skimage.io.imsave(out_path.format(**{"frame":frame, "type":"tile"}), pred_tile) 
        print("did tile")
        pred_simp = simple_seg(im, model)
        skimage.io.imsave(out_path.format(**{"frame":frame, "type":"simp"}), pred_simp) 
 
if __name__ == "__main__":
    main()