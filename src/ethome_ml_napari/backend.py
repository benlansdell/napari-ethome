from ethome import create_dataset
from ethome.features import FEATURE_MAKERS
import json 
import datetime
import pandas as pd

IMPORTED = 0
PREDICTED = 1

FEATURE_MAKERS_DESCRIPTION = [
    ['MARS', 'mars', 'MARS mouse resident-intruder features'],
    ['MARS Reduced', 'mars_reduced', 'MARS mouse resident-intruder features, reduced to 10 features'],
    ['CNN1D Prob', 'cnn1d_prob', 'CNN1D probability features'],
    ['Social', 'social', 'Social features'],
    ['Centroids Interanimal', 'centroids_interanimal', 'Centroids interanimal features'],
    ['Centroids Interanimal Speed', 'centroids_interanimal_speed', 'Centroids interanimal speed features'],
    ['Centroids', 'centroids', 'Centroids features'],
    ['Centroids Velocity', 'centroids_velocity', 'Centroids velocity features'],
    ['Intrabodypart Speeds', 'intrabodypartspeeds', 'Intrabodypart speeds features'],
    ['Intrabodypart Distances', 'intrabodypartdistances', 'Intrabodypart distances features']
]

#Each row of models list is a Model
class Model:
    def __init__(self, model, name, df):
        self.df = df
        self.trained_date = None
        self.name = name
        self.model = model
        self.predictions = None
        self.feature_sets = []
        self.labelset = None

    def train(self, feature_sets, labelset):
        self.feature_sets = feature_sets
        self.labelset = labelset
        self.trained_date = datetime.time()

        #Activate feature sets in df 

        #Fit to data
        self.model.fit(feature_sets, labelset)

        self.predictions = self.model.predict(feature_sets)

#Each row of features list is a FeatureSet
class FeatureSet:
    def __init__(self, name, df, nicename = None, description = ''):
        self.df = df
        self.name = name
        self.cols = None
        self.description = description
        if nicename is None:
            self.nicename = name
        else:
            self.nicename = nicename 

    def add(self):
        if self.cols is None:
            self.cols = self.df.features.add(self.name)

#Each row of labels is a LabelSet
class LabelSet:
    def __init__(self, name, id, behaviors = set(), description = '', type = IMPORTED):
        #Set to now
        self.name = name
        self.description = description
        self.id = id
        self.type = type
        self.behaviors = behaviors
        self.last_edited = datetime.time()
        self.ancenstry = []

class EthomeDF:
    def __init__(self):
        self.df = None
        self.behaviors = pd.DataFrame([['', '']], columns = ['name', 'keymap'])
        self.label_sets = {}
        self.feature_sets = {}
        self.models = {}
        self.fps = 1
        self.is_recording = False 
        self.recording_state = {}

    @property
    def nbehaviors(self):
        return len(self.behaviors) - 1

    @property
    def hotkeys(self):
        return self.behaviors.keymap

    def get_featurecols(self, feature_set):
        cols = []
        for f in feature_set:
            cols += self.feature_sets[f].cols
        return cols

    def get_features(self, feature_set):
        return self.df[self.get_featurecols(feature_set)]

    def add_features(self, feature_name):
        self.feature_sets[feature_name].add()

    def get_labels(self, nicename):
        return self.df[self.label_sets[nicename]]

    def load(self, path):
        with open(path) as f:
            metadata = json.load(f)
        self.df = create_dataset(metadata)
        self.feature_sets = {n: FeatureSet(k, self.df, nicename = n, description = d) for n,k,d in FEATURE_MAKERS_DESCRIPTION}

        fn = list(self.df.metadata.details.keys())[0]
        self.fps = self.df.metadata.details[fn]['fps']

        #Get label names from the imported data
        label_names = {self.df.ml.label_cols}

        for idx, name in enumerate(label_names):
            key = self._find_free_key(name)
            self.behaviors.iloc[idx, :] = [name, key]
        self.behaviors.loc[len(self.behaviors)] = ['', '']

        self.recording_state = {k: False for k in self.behaviors['name']}

        now = datetime.datetime.now()
        nicename = f'{now.strftime("%m/%d/%Y,%H:%M:%S")} Imported'
        self.label_sets = {nicename: LabelSet(nicename, label_names)}

    def update_key_maps(self, keymap):
        pass

    def add_behavior(self, name, keymap = None):
        pass

    def update_behavior(self, name, keymap):
        pass

    def _find_free_key(self, name):
        for l in name:
            if l not in self.hotkeys:
                return l
        raise Exception("No unique key availale. Devise a better default lettering scheme.")

#Create a blank backend object
ethomedf = EthomeDF()