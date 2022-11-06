"""
This module is an example of a barebones numpy reader plugin for napari.

It implements the Reader specification, but your plugin may choose to
implement multiple readers or even other plugin contributions. see:
https://napari.org/stable/plugins/guides.html?#readers
"""
import json
from ethome import create_dataset
from napari_video.napari_video import VideoReaderNP
import pandas as pd
from itertools import product
import os

def napari_get_reader(path):
    """A basic implementation of a Reader contribution.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, list):
        # reader plugins may be handed single path, or a list of paths.
        # if it is a list, it is assumed to be an image stack...
        # so we are only going to look at the first file.
        print("Only provide one project file.")
        return None

    # if we know we cannot read the file, we immediately return None.
    if not path.endswith(".json"):
        return None

    # otherwise we return the *function* that can read ``path``.
    return reader_function

def reader_function(path):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer. Both "meta", and "layer_type" are optional. napari will
        default to layer_type=="image" if not provided
    """
    # handle both a string and a list of strings
    paths = [path] if isinstance(path, str) else path

    #Load metadata from json file
    with open(path) as f:
        metadata = json.load(f)

    df = create_dataset(metadata)

    add_kwargs = {'visible': False}
    layer_type = "image"
    def make_kwargs(p):
        return {**add_kwargs, 'name': os.path.basename(p)}
    vid_paths = [df.metadata.details[vid]['video'] for vid in df.metadata.videos]
    vid_layers = [(VideoReaderNP(p), make_kwargs(p), layer_type) for p in vid_paths]

    #Load in tracking data 
    for vid in df.metadata.videos:
        add_kwargs = {'visible': False, 'name': os.path.basename(vid)}
        layer_type = "tracks"
        tracks = df.loc[df['filename'] == vid, df.pose.raw_track_columns].reset_index(drop=True)
        this_vids_data = pd.DataFrame()
        for track_idx, (animal, bp) in enumerate(product(df.pose.animals, df.pose.body_parts)):
            data = tracks.loc[:, [f'{animal}_x_{bp}', f'{animal}_y_{bp}']]
            data.columns = ['x', 'y']
            data['track_idx'] = track_idx
            data['frame'] = data.index
            data = data.loc[:,['track_idx', 'frame', 'y', 'x']]
            this_vids_data = pd.concat([this_vids_data, data])
        vid_layers.append((this_vids_data.to_numpy(), add_kwargs, layer_type))

    #If there are labels, add that data too
    label_data = []
    if 'labels' in df.metadata.details:
        add_kwargs = {'visible': False, 'name': os.path.basename(df.metadata.details['labels'])}
        layer_type = "labels"
        label_data.append((df.ml.label.to_numpy(), add_kwargs, layer_type))

    #Load the likelihood data

    return vid_layers
