.. _getting_started:

Getting Started
===============

Install `Pixi <https://pixi.sh/>`_ 0.84.2 or newer, then download or clone
`surface-apps <https://github.com/MiraGeoscience/surface-apps>`_.
From the extracted repository root, install the locked application environment::

    pixi install --locked --environment runtime
    pixi run --frozen --environment runtime install

On Windows, use ``install_in_analyst.bat`` to install in Geoscience Analyst.
Pass ``-e`` for an editable installation.

See the :ref:`Basic usage <usage>` section for running the applications.
