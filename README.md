# EvaluateSegmentation
A Slicer module for Evaluate segmentation/labelmap
you can download the module and add it to 3D Slicer-->Edit-->Application Settings-->Modules, then add the path of the module to "Additional module paths" and restart. It will appear somewhere in module lists in Example.
The module needs tensorflow, scikit,.... that automatically installs them. if you receive an error, push apply again might solve it.

if you need a fast processing, you should increase the voxel size using "resample scaler volume" tool.

if you received an error about permission to run: 

$ chmod +x EvaluationSegmentation_linux/EvaluateSegmentation/Resources/EvaluateSegmentation
![Alt text](Screenshot1.jpg?raw=true "Using Slicer for label evaluation")
Help:
If you used this module in your research or need more details about the metrics please cite these papers:


https://doi.org/10.1016/j.mri.2019.11.002 

https://doi.org/10.1186/s12880-015-0068-x
