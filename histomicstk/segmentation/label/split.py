import numpy as np

from .condense import condense


def split(im_label, conn=8):
    """Re-labels objects that have multiple non-contiguous portions to create
    a new label image where each object is contiguous.

    Parameters
    ----------
    im_label : array_like
        A uint32 type label image generated by segmentation methods.
    conn : int
        Neighborhood connectivity to define contiguity. Valid values are 4 or
        8. Default value = 4.

    Notes
    -----
    Objects are assumed to have positive nonzero values.

    Returns
    -------
    Split : array_like
        A uint32 label where discontiguous objects are split and relabeled.

    See Also
    --------
    histomicstk.segmentation.label.area_open,
    histomicstk.segmentation.label.condense,
    histomicstk.segmentation.label.shuffle

    """
    import scipy.ndimage as ndi

    # copy input image
    Split = im_label.copy()

    # define kernel for neighborhood
    if conn == 8:
        Kernel = np.ones((3, 3), dtype=bool)
    elif conn == 4:
        Kernel = np.zeros((3, 3), dtype=bool)
        Kernel[1, :] = True
        Kernel[:, 1] = True
    else:
        raise ValueError("Input 'conn' must be 4 or 8")

    # condense label image
    if np.unique(Split).size - 1 != Split.max():
        Split = condense(Split)

    # get locations of objects in initial image
    Locations = ndi.find_objects(Split)

    # initialize number of labeled objects
    Total = Split.max()

    # iterate through objects, replicating where needed
    for i in np.arange(1, len(Locations) + 1):

        # extract object from label image
        Template = Split[Locations[i - 1]]

        # label mask of object 'i'
        L, Count = ndi.label(Template == i, Kernel)

        # relabel if necessary
        if Count > 1:
            Template[L == 1] = i
            for i in np.arange(2, Count + 1):
                Template[L == i] = Total + 1
                Total += 1

    return Split
