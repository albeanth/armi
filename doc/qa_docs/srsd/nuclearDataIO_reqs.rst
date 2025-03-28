.. _armi_nuc_data:

Nuclear Data I/O Package
------------------------

This section provides requirements for the :py:mod:`armi.nuclearDataIO` package within the framework, which
handles reading and writing of standard interface files for reactor physics software (e.g., cross section data).

Functional Requirements
+++++++++++++++++++++++

.. req:: The nuclearDataIO package shall be capable of reading and writing ISOTXS files into and out of mutable data structures.
    :id: R_ARMI_NUCDATA_ISOTXS
    :subtype: functional
    :basis: These files are the MC2 output format.
    :acceptance_criteria: Read one or more ISOTXS files and its basic input data correctly, and correctly write that data back out to a single file.
    :status: accepted

.. req:: The nuclearDataIO package shall be capable of reading and writing GAMISO files into and out of mutable data structures.
    :id: R_ARMI_NUCDATA_GAMISO
    :subtype: functional
    :basis: These files are generated by MCC-v3.
    :acceptance_criteria: Read a GAMISO file and its basic input data correctly, and correctly write that data back out.
    :status: accepted

.. req:: The nuclearDataIO package shall be capable of reading and writing GEODST files into and out of mutable data structures.
    :id: R_ARMI_NUCDATA_GEODST
    :subtype: functional
    :basis: These files are generated by DIF3D.
    :acceptance_criteria: Read a GEODST file and its basic input data correctly, and correctly write that data back out.
    :status: accepted

.. req:: The nuclearDataIO package shall be capable of reading and writing DIF3D files into and out of mutable data structures.
    :id: R_ARMI_NUCDATA_DIF3D
    :subtype: functional
    :basis: These files are used in DIF3D.
    :acceptance_criteria: Read a DIF3D file and its basic input data correctly, and correctly write that data back out.
    :status: accepted

.. req:: The nuclearDataIO package shall be capable of reading and writing PMATRX files into and out of mutable data structures.
    :id: R_ARMI_NUCDATA_PMATRX
    :subtype: functional
    :basis: These files are generated by MCC-v3 and used in GAMSOR.
    :acceptance_criteria: Read a PMATRX file and its basic input data correctly, and correctly write that data back out.
    :status: accepted

.. req:: The nuclearDataIO package shall be capable of reading and writing DLAYXS files into and out of mutable data structures.
    :id: R_ARMI_NUCDATA_DLAYXS
    :subtype: functional
    :basis: These files are used to generate kinetics parameters.
    :acceptance_criteria: Read a DLAYXS file and its basic input data correctly, and correctly write that data back out.
    :status: accepted

.. req:: The nuclearDataIO package shall be able to compute macroscopic cross sections from microscopic cross sections and number densities.
    :id: R_ARMI_NUCDATA_MACRO
    :subtype: functional
    :basis: Macroscopic cross sections are needed by many analysts.
    :acceptance_criteria: Compute macroscopic cross sections from microscopic cross sections and number densities.
    :status: accepted
