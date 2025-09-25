This folder contains code to:
- export an openmodelica model to an FMU 
- uses FMPy to run the model in a jupyter notebook 
- shows how the model control inputs can be given through FMPy 

To do so:

Create an FMU for the SolarTestModelSimple.mo model by running generateFMU.mos script using 
`omc generateFMU.mos`

A notebook that runs the model can be generated using 
`fmpy create-jupyter-notebook SolarTestModel.fmu`

The notebook control_test.ipynb implements a simple control on the model 

    