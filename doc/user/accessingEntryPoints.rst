**********************
Accessing Entry Points 
**********************

Reports Entry Point
===================

There are two ways to access the reports entry point in ARMI.

The first way is through a yaml settings file.
Here, the call is as follows::

    (venv) $ armi report anl-afci-177.yaml

It is also possible to call this on an h5 file::

    (venv) $ armi report -h5db refTestBase.h5

.. note:: When working with a h5 file, -h5db must be included

Once these are called, a report is generated and outputted as an html file in reportsOutputFiles.
