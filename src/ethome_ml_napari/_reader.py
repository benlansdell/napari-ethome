"""
Read in json file with project data.
"""
import json
import os
import pandas as pd
import numpy as np

from ethome import create_dataset
from napari_video.napari_video import VideoReaderNP
from itertools import product

from .backend import ethomedf

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
        print("Only provide one project file.")
        return None

    if not path.endswith(".json"):
        return None

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

    ethomedf.load(path)
    df = ethomedf.df

    vid_layers = []

    #Load video data
    add_kwargs = {'visible': False}
    layer_type = "image"
    def _make_kwargs(p):
        return {**add_kwargs, 'name': 'video_' + os.path.basename(p)}
    vid_paths = [df.metadata.details[vid]['video'] for vid in df.metadata.videos]
    vid_layers += [(VideoReaderNP(p), _make_kwargs(p), layer_type) for p in vid_paths]

    #Load in tracking data 
    for idx, vid in enumerate(df.metadata.videos):
        add_kwargs = {'visible': False, 'name': 'tracks_' + os.path.basename(vid)}
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
    layer_data = []
    add_kwargs = {'visible': False, 'name': 'labels'}
    for vid in df.metadata.videos:
        if 'labels' in df.metadata.details[vid]:
            tracks = df.loc[df['filename'] == vid]
            layer_data.append(tracks.ml.labels)

    max_len = max([len(x) for x in layer_data])
    layer_data = [np.pad(x, (0, max_len - len(x)), 'constant') for x in layer_data]
    layer_data = np.stack(layer_data, axis=0)

    vid_layers.append((layer_data, add_kwargs, 'image'))
           
    #Load the likelihood data

    return vid_layers
