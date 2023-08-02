# EvaluateSegmentation
A Slicer module for Evaluate segmentation/labelmap
you can download the module and add it to 3D Slicer-->Edit-->Application Settings-->Modules, then add the path of the module to "Additional module paths" and restart. It will appear somewhere in module lists in Example.
The module needs tensorflow, scikit,.... that automatically installs them. if you receive an error, push apply again might solve it.

if you need a fast processing, you should increase the voxel size using "resample scaler volume" tool.

if you received an error about permission to run: 

$ chmod +x EvaluationSegmentation_linux/EvaluateSegmentation/Resources/EvaluateSegmentation

if you want to run on folders, I suggest to use shell script as:

touch temp.txt

touch temp2.txt

touch temp3.txt

touch results.txt

for l in {1,2,4}; do 
    pred='labels'$l1'.nii.gz'
    orig='orig'$l2'.nii.gz'
    /path to/EvaluateSegmentation $orig $pred |sed -n 2,32p | awk '{print $3}'>$channel'/'temp.txt
	    cp -v  'results.txt' 'temp2.txt'
	    awk '{getline l <"temp2.txt"; print $0"\t"l} ' temp.txt > temp3.txt
	    cp -v 'temp3.txt' 'results.txt'	
done


![Alt text](Screenshot1.jpg?raw=true "Using Slicer for label evaluation")
Help:
If you used this module in your research or need more details about the metrics please cite these papers:


https://doi.org/10.1016/j.mri.2019.11.002 

https://doi.org/10.1186/s12880-015-0068-x
