from flask_plugins import get_enabled_plugins, get_all_plugins
from flask import current_app
import pandas as pd
import matplotlib.dates as mdates
import shutil
import os
import glob


def checkplugins(enabled=True):
    """
    This function is used to populate a multiselect field. It checks which plugins are enabled and disabled
     and generates the output required for the DOM element.
    :param enabled: If true a list of enabled plugins are returned else a list of disabled plugins are returned.
    :return: Output required by DOM element
    """
    plugins = [(plugin.identifier, plugin.name) for plugin in get_all_plugins()]
    enabled_plugins = [(plugin.identifier, plugin.name) for plugin in get_enabled_plugins()]
    disabled_plugins = [x for x in plugins if x not in enabled_plugins]

    if plugins:
        if enabled:
            if enabled_plugins:
                p = [plugin for plugin in enabled_plugins]

            else:
                p = [('', 'No active plugins')]

        else:
            if disabled_plugins:
                p = [plugin for plugin in disabled_plugins]

            else:
                p = [('', 'All plugins enabled')]

    else:
        p = None

    return p


def uploaded_files():
    """
    This function is used to populate select fields and textbox fields. It checks which files are uploaded
    and generates the output required for the DOM element.
<<<<<<< HEAD
    :param textbox: Default value of True. Set to False if a select field needs to be populated.
=======
>>>>>>> origin/evertdevelop_pytest
    :return: Output required by DOM element
    """
    hdf5store = current_app.config["HDF5_STORE"]
    store = pd.HDFStore(hdf5store)
    keys = store.keys()
    store.close()
    del store

    if not keys:
        columns = [('No files uploaded', 'No files uploaded')]

    else:
        columns = [(key, key.split('/')[1]) for key in keys]

    return columns


def unique_headers(table_key, initial=False):
    """
    Get the headers for a csv file
    :param table_key: key pointing to table in HDF5 store
    :return: list of headers
    # """

    try:
        hdf5store = current_app.config["HDF5_STORE"]
        store = pd.HDFStore(hdf5store)
        data = store.get(table_key)
        store.close()
        del store

        if initial:
            fieldnames = [(fieldname, fieldname) for fieldname in data.columns.values]

        else:
            fieldnames = [fieldname for fieldname in data.columns.values]

    except KeyError:
        if initial:
            fieldnames = [('', '')]

        else:
            fieldnames = ['']

    return fieldnames


def date_parser(start_date, end_date):
    """
    This is a date parsing function to automatically determine the best date format to you for time-series data
    :param start_date: A datetime object of the start date
    :param end_date: A datetime object of the end date
    :return: Two DateFormatter objects of the major and minor date format respectively
    """

    delta = end_date - start_date
    days = delta.days
    seconds = delta.seconds

    if days > 365:
        major_fmt = '%Y'
        minor_fmt = '%m-%d'

    elif 1 < days < 365:
        major_fmt = '%Y-%m-%d'
        minor_fmt = '%Y-%m-%d %H:00'

    elif days == 0 and seconds > 3600:
        major_fmt = '%H:%M'
        minor_fmt = '%H:%M:%S'

    elif days == 0 and seconds < 3600:
        major_fmt = '%M:00'
        minor_fmt = '%M:%S'

    return mdates.DateFormatter(major_fmt), mdates.DateFormatter(minor_fmt)


def copy_files(src, dst, check_mod_time=False):
    """
    Copies subdirectories from one directory to another
    :param src:
    :param dst:
    :param check_mod_time:
    :return:
    """
    try:
        shutil.copytree(src, dst)
    except FileExistsError:
        if not check_mod_time:
            shutil.rmtree(dst)
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache*'))

        if check_mod_time:
            srctime = os.path.getmtime(src)
            dsttime = os.path.getmtime(dst)
            if srctime > dsttime:
                shutil.rmtree(dst)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache*'))
            else:
                pass
    except NotADirectoryError:
        pass


def find_plugins(app):
    """
    Synchronises the plugins in the base code with the plugins in the documents folder. This ensures the newest version
    of the plugins are always available when the server resets.
    :param app: flask application instance
    """
    docdir = app.config['USER_DOCUMENTS']
    docplugins = os.path.join(docdir, 'Evert Plugins')
    pluginfolder = os.path.isdir(docplugins)
    baseplugindir = app.config['UPLOADED_PLUGIN_DEST']

    # updating documents folder
    if pluginfolder:
        uploadedplugins = [fld for fld in os.listdir(baseplugindir) if not fld.startswith('__pyc')]
        for uploaded in uploadedplugins:
            src = os.path.join(baseplugindir, uploaded)
            dst = os.path.join(docplugins, uploaded)
            copy_files(src, dst, True)

        # updating base folder
        src_folder = glob.glob(docplugins+'/*')
        if src_folder:
            for plugin in src_folder:
                dst = os.path.join(baseplugindir, os.path.basename(plugin))
                copy_files(plugin, dst)

    elif not pluginfolder:
        try:
            os.mkdir(os.path.join(docdir, 'Evert Plugins'))

        except FileNotFoundError:
            pass
