from copy import deepcopy

import numpy as np


def _global_min_(DF):
    points = []
    headers = list(DF)
    min_vals = DF.min()
    min_index = DF.idxmin(0)

    for i, h in enumerate(headers):
        points.append([h, min_index[h], min_vals[h], 'Global Minimum'])

    return points


def _global_max_(DF):
    points = []
    headers = list(DF)
    max_vals = DF.max()
    max_index = DF.idxmax(0)

    for i, h in enumerate(headers):
        points.append([h, max_index[h], max_vals[h], 'Global Maximum'])

    return points


def _filter_peaks_(list_of_peaks, peak_width, width):
    lst = []
    features = []
    _container_ = []

    for i, v in enumerate(list_of_peaks):

        if i == 0:
            _container_.append(v)

        if i > 0:

            if list_of_peaks[i][0] - list_of_peaks[i - 1][0] < width:
                _container_.append(v)

            else:
                if len(_container_) != 0:
                    lst.append(_container_)
                _container_ = []

    for i, v in enumerate(lst):

        temp = np.array(v)

        if len(temp[:, 1]) > peak_width:
            if temp[:, 2][0] == 'max':
                _max_ = float(max(temp[:, 1]))
                index = temp[:, 0][np.argmax(temp[:, 1])]
                features.append([index, _max_, 'Local Maximum'])
            elif temp[:, 2][0] == 'min':
                _min_ = float(min(temp[:, 1]))
                index = temp[:, 0][np.argmin(temp[:, 1])]
                features.append([index, _min_, 'Local Minimum'])

    return features


def _moving_filter_(vals, config):
    threshold, width, peak_width = config
    _lst_ = []

    for i, v in enumerate(vals):
        if width <= i <= len(vals) - width:
            scope = vals[i - width: i + width]

            std_dev = np.std(scope)
            avg = sum(scope) / len(scope)

            if v > scope[0] and v > scope[-1]:

                if v > avg + std_dev * threshold:
                    _lst_.append([i, v, 'max'])

            elif v < scope[0] and v < scope[-1]:

                if v < avg - std_dev * threshold:
                    _lst_.append([i, v, 'min'])

    lst = _filter_peaks_(_lst_, peak_width, width)

    return lst


def _median_(dataframe):
    points = []
    headers = list(dataframe)
    median_vals = dataframe.median()
    for i, h in enumerate(headers):
        points.append([h, 'line', median_vals[h], 'Median'])

    return points


def _mean_(dataframe):
    points = []
    headers = list(dataframe)
    mean_vals = dataframe.mean()
    for i, h in enumerate(headers):
        points.append([h, 'line', mean_vals[h], 'Mean'])

    return points


def _format_data_(header_name, feature_name, feature_timestamp, feature_value, **kwargs):
    # This should create appropriate lists in the shape of [['timestamp', 'header_name:feature_name'],
    #                                                       [timestamp, feature_value]]
    # which is appropriate for Evert.

    if 'line' in kwargs:
        lst = [['timestamp', '{}:{}'.format(header_name, feature_name)],
               [feature_timestamp[0], feature_value],
               [feature_timestamp[1], feature_value]]
    else:
        lst = [['timestamp', '{}:{}'.format(header_name, feature_name)],
               [feature_timestamp, feature_value]]

    return lst


def extract_features(_initialdf_, config):
    """Extracts data features from a set of timeseries data.
    :param _initialdf_: A pandas.Dataframe containing timestamps as the first column, and timeseries as further columns
    :param config: Contains the following configuration variables: Threshold(std deviation),
                                                                   Window Width(Integer, halfwidth excluding centre),
                                                                   Peak Width(Minimum number of peaks in a Window Width 
                                                                   for peak to be identified).
    :return: A list of lists, containing [['timestamp', 'Col:feature_name'], [timestamp, feature_value]]
    """
    features = []
    DF_nostamp = deepcopy(_initialdf_)
    del DF_nostamp['timestamp']
    headers = list(DF_nostamp)

    for i in headers:
        minmax = _moving_filter_(_initialdf_[i].as_matrix().tolist(), config)
        for j in range(len(minmax)):
            minmax[j].insert(0, i)
            feature = _format_data_(feature_name=minmax[j][-1],
                                    feature_timestamp=_initialdf_['timestamp'].iloc[int(minmax[j][1])],
                                    feature_value=minmax[j][2], header_name=minmax[j][0])
            features.append(feature)

    _features_ = []
    _features_ += _global_max_(DF_nostamp) + _global_min_(DF_nostamp) + _median_(DF_nostamp) + _mean_(DF_nostamp)
    for i in _features_:
        if i[1] == "line":
            feature = _format_data_(feature_name=i[-1],
                                    feature_timestamp=[_initialdf_['timestamp'].iloc[0],
                                                       _initialdf_['timestamp'].iloc[-1]],
                                    feature_value=i[2], header_name=i[0], line=True)
        else:
            feature = _format_data_(feature_name=i[-1],
                                    feature_timestamp=_initialdf_['timestamp'].iloc[int(i[1])],
                                    feature_value=i[2], header_name=i[0])
        features.append(feature)

    return features
