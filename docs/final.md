---
layout: default
title:  Final Report
---

# Video
## Main Project - MobIdentifier Iterative Image Dataset
<iframe width="560" height="315" src="https://www.youtube.com/embed/Mk08YsEHYyY" frameborder="0" allowfullscreen></iframe>
### Video Description
This video is showing the progress of our main project, being able to successfully identify mobs in an image based on pixel values alone (not using Malmo). We use Malmo to generate a static superflat world and use console commands to spawn mobs at varying distances around the user. We then take screenshots, crop the mob out, resize it to 24x24, and save it to our master dataset. We have several models that are testing at the same time, each instance using its own subset of the master image dataset. These subsets have their own model trained on varying image manipulations of the dataset (e.g. grayscale, edge detection). We show/graph these image manipulations along with the number of times the model classified correctly / the total number of times the model has made a prediction. Everytime the model incorrectly classifies a mob, it adds to the models training data. You can see in the video that at the start the graph the predictions are very sparatic but as the model build its dataset it starts learning and smooths out.

**NOTE**: There are 3 open subplots in the bottom right of the video because we were planning on adding more features to test.

## Moonshot Project - Identifying Multiple Mobs
<iframe width="560" height="315" src="https://www.youtube.com/embed/Tm9INZ2ytA4" frameborder="0" allowfullscreen></iframe>
### Video Description
We were experimenting with ways to find and identify multiple mobs in the same image. The video describes how we segmented the image into a 3x3. We also trained a model using segments of each mob (as opposed to the whole mob). We then took a cropping with multiple mobs in it, segmented it, then predicted the probabilities of each segment being each mob. Using these 9 different prediction probabilites, we tried to logically reason where the centroids of each mob were in the image. We then draw circles in the image where we thought these mobs were.

# STOP



We reduced our problem of finding the centroids of each Minecraft MOB in an agents view to finding the centroids of each Minecraft MOB in the individual image croppings (of the agents view) generated using our cropper program. Our cropping program will generate two types of croppings: 1) A cropping containing one MOB (in which one centroid must be found), and 2) A cropping containing multiple MOBs (in which multiple centroids must be found). Below is a breakdown of the complications, methods and accuracies for both categories.

Single MOB croppings- Single MOB croppings were the easiest to find the centroid. There were next to no issues finding the correct location of the centroid, as essentially all of the cropping contained the MOB of interest and any parts of the cropping not belonging to MOB of interest, was deemed as background with near perfet accuracy. The only issue with finding a centroid for a single MOB cropping was a misclassification of the MOB. If the MOB belonged to the set {Cow, Mushroom cow, Pig}, then our random forest classifier predicted the MOB correctly close to 100% of the time. The only time that the random forest classifier had a harder time correctly classifying the MOB was when the MOB belonged to the set {Chicken, Sheep}, as both chickens and sheeps were of the color white, and were not always easily distinguishable.

Multiple MOB croppings- Multiple MOB croppings had essentially the same issues as single MOB croppings in terms of MOB classification. Hence, where our centroid program struggled the most, was not classifying the MOBs correctly, but in determing where and how many centroids to create. The way we determined the locations of our centroids is as follows: We split up the image cropping into 9 (3x3) equally sized image segments, and ran each segment through our random forest classifier to obtain the confidences that the classifier had, that each segment contained each particular MOB. We then created a centroid for every MOB and discarded the centroid if the total confidence of any particular MOB (Sum_over_all_segments(confidence_of_segment(MOB_type)) was below a particular threshold. After obtaining the believed to correct number of centroids, we proceeded to find the locations of each. This was done by placing the centroid in the center of the segment that had the highest confidence that the MOB was in that segment, and then adjusted the location based on the confidences of the segments around it. Since it was common that there were extra and/or misclassified centroids for MOBs in set {Chicken, Sheep}, we increased the threshold that the total confidences must exceed in order to keep the centroid for both chicken and sheeps. This led to better accuracy in MOB classifications and a reduction in amount of incorrect centroids being created, at the expense of not always finding a centroid of each MOB.






# Project Summary
Every model has its tradeoffs which can be seen in the statistics. For instance, using RGB values requires feature vectors of size 24x24x3 and has

These models initially start with **EMPTY** datasets. When the model sees a label it has not seen before, it simply adds the label and its image to its subset. If the model has seen the label before, it tries to classify that cropping. If it classifys **WRONG**, it adds the cropping to that subset. If it classifys **RIGHT**, it simply moves on. By doing this, you can see 
apply several image manipulations to this cropping and use 

add each result to their respective model (e.g. grayscale, edges, etc). 

# Approaches
# Evaluation
# References
