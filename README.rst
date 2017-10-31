################################
pl-geretrieve
################################


Abstract
********

An app to retrieve data of interest from GE cloud

Run
***

Using ``docker run``
====================

Assign an "input" directory to ``/incoming`` and an output directory to ``/outgoing``

.. code-block:: bash

    docker run -v /tmp/input:/incoming -v /tmp/output:/outgoing   \
            local/pl-geretrieve geretrieve.py --prefix demo-upload          \
            /incoming /outgoing

This will retrieve a copy of each file/folder inside the demo-upload "folder" in GE storage
into the local /outgoing directory. Some metadata files should have previously been read
from /incoming directory.

Make sure that the host ``/tmp/input`` directory is world readable and ``/tmp/output``
directory is world writable!







