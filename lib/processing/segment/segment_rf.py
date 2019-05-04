"""
"""
import numpy as np
import skimage
import sklearn.ensemble

def get_model():
    rfc = sklearn.ensemble.RandomForestClassifier()
    return rfc


def get_features(image):
    im = skimage.img_as_ubyte(image).astype(np.uint8)
    meanf = skimage.filters.rank.mean(im, selem=np.ones((9, 9)))
    gradf = skimage.filters.rank.gradient(im, selem=np.ones((9, 9)))
    entropy = skimage.filters.rank.entropy(im, selem=np.ones((9, 9)))
    sim = np.dstack([meanf, gradf, entropy])
    return sim.reshape(-1, sim.shape[-1])


def get_training_set(list_of_pairs, percent_train=0.4, percent_test=0.4):
    train_x = np.empty((0, 3))
    train_y = np.empty((0, 1))
    test_x = np.empty((0, 3))
    test_y = np.empty((0, 1))
    for img, msk in list_of_pairs:
        pimg = get_features(img)
        pmsk = msk.reshape(-1, 1)
        indx = np.random.permutation(np.arange(np.prod(img.shape)))
        n = len(indx)
        train_num = int(percent_train * n)
        test_num = int(percent_test * n)
        train_idx = indx[:train_num]
        test_idx = indx[train_num : train_num + test_num]

        print(train_x.shape) 
        print(pimg[train_idx,:].shape)
        print(train_y.shape) 
        print(pmsk[train_idx,:].shape)
        train_x = np.append(train_x, pimg[train_idx,:], axis=0)
        train_y = np.append(train_y, pmsk[train_idx,:], axis=0)
        test_x = np.append(test_x, pimg[test_idx,:], axis=0)
        test_y = np.append(test_y, pmsk[test_idx,:], axis=0)
    return train_x, train_y, test_x, test_y

