.. _getting_started:

Getting Started
===============

Whether you are developer or an end-user, this page will help you get started with the **surface-apps**.

.. contents::

.. toctree::
   :maxdepth: 2

Installation
------------

Install Conda
~~~~~~~~~~~~~

Install Conda for Python 3.9 or higher. Follow this link to download its Windows installer (~140 MB of disk space):

`Miniforge <https://github.com/conda-forge/miniforge#download>`_ `(Windows x86_64) <https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe>`_

.. figure:: /images/getting_started/Miniforge3_Setup-1.png
    :align: center
    :width: 200

.. figure:: /images/getting_started/Miniforge3_Setup-3.png
    :align: center
    :width: 200

Registering the Conda distribution as the default Python 3.10 interpreter is totally optional.
Preferably uncheck that box if you already have Python 3 installed on your system.

.. note:: We recommend installing **Miniforge**: beyond being smaller,
    it also installs packages from the conda-forge repository by default,
    which has no restriction for commercial use, while both Miniconda and Anaconda distributions use
    the Anaconda repository by default: see `Anaconda Terms of Service <https://www.anaconda.com/terms-of-service>`_ for details.
    In any case, the installation of **surface-apps** forces the usage of the conda-forge repository,
    and is thus not affected by the Anaconda Terms of Service.

Download the latest surface-apps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Follow this link to `download from the GitHub repository <https://github.com/MiraGeoscience/surface-apps/archive/refs/heads/main.zip>`_.

Extract the package to your drive (SSD if available)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Extract the package to your drive, preferably an SSD if available.

.. figure:: /images/getting_started/extract.png
    :align: center
    :width: 50%


Run ``Install_or_Update.bat``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The same batch file can be used to install or update **surface-apps**.
A conda environment named ``surface_apps`` will be created to prevent conflicts with other software that may rely on Python.

.. figure:: /images/getting_started/install_or_update.png
    :align: center
    :width: 50%

.. note:: The assumption is made that Conda has been installed in one
   of the default directories, depending on the distribution
   (miniforge3, mambaforge, miniconda3, anaconda3):

   - %LOCALAPPDATA%\\
   - %USERPROFILE%\\
   - %LOCALAPPDATA%\\Continuum\\
   - %PROGRAMDATA%\\

If Conda gets installed in a different directory, users will need to add/edit a
``get_custom_conda.bat`` file to add their custom path to the ``conda.bat`` file:

.. figure:: /images/getting_started/Install_start_bat.png
    :align: center
    :width: 75%


At this point, you will have all required packages to run the applications.
See the :ref:`Basic usage <usage>` section for more details.
