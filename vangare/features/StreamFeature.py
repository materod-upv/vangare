# Vangare: The XMPP server written in Python.
# Copyright (C) 2020 María Ten Rodríguez
# This file is part of Vangare.
# See the file LICENSE for copying permission.

from vangare.xml import BaseXML



class NonUniqueFeature(Exception):
    """Exception raised when a non unique feature is found on the manager."""
    pass

class FeatureManager():
    """Class to manage server features."""
    __slots__ = ["_features"] 

    def __init__(self):
        self._features = {}

    def register(self, feature):
        """Register a new feature."""
        if feature.name in self._features:
            raise NonUniqueFeature("Feature already registered")
        self._features[feature.name] = feature

    def unregister(self, feature):
        """Unregister a feature."""
        if feature.name in self._features:
            del self._features[feature.name]
    
    def get_features(self):
        """Returns the stream feature object."""
        features = StreamFeatures()
        for f in self._features.values():
            features[...] = f
        return features
    
    def __keys__(self):
        """Returns the server feature list."""
        return self._features.keys()
    
    def __getitem__(self, key):
        """Allow features to be accessed tghrough the manager as if it was a dictionary."""
        return self._features[key]
    
    def __iter__(self):
        """Allow features to be iterated through the manager as if it was a dictionary."""
        return iter(self._features)
    
    def __len__(self):
        """Return the number of features registered."""
        return len(self._features)