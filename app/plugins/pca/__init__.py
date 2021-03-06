from flask import Blueprint
from evertcore.plugins import connect_listener, AppPlugin
import pandas as pd
from evertcore.plugins import emit_addon_plot_data, register_plugin
from .pca import apply_pca

__plugin__ = "PCA"
__plugin_type__ = 'add_on'

pca = Blueprint('pca', __name__)


def run_plugin(data, name):
    print('event_emitted')
    if name == 'pca':
        if not isinstance(data, pd.DataFrame):
            raise TypeError('Expected input of type: pandas.DataFrame for argument: data_before, instead got: {}'.
                            format(type(data)))

        data, layout = apply_pca(data)
        if not data and not layout:
            emit_addon_plot_data(data, layout, 'PCA add-on requires more than one dataset')
        else:
            emit_addon_plot_data(data, layout, '')
        return
    else:
        return


class PCA(AppPlugin):

    def setup(self):
        self.register_blueprint(pca)
        register_plugin(__plugin__, __plugin_type__)
        connect_listener("add_on_event", run_plugin)