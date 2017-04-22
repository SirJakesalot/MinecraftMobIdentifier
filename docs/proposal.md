---
layout: default
title: Proposal
---

## Summary of the Project ##
In a paragraph or so, mention the main idea behind your project. At the very least, you should have a sentence
that clearly explains the input/output semantics of your project, i.e. what information will it take as input, and
what will it produce. Mention any applications, if any, for your project.

**ANS:** From an enclosed world containing a variety of unique mobs, find a specific mob using computer vision object recognition. The input for our AI will be the players current view of the Minecraft world. Our goal is to find the mob in the world specified by the user or randomly generated. The output will be the accuracy that the AI correctly finds and classifies in the mob in the world.
The technologies used will be OpenCV with haar cascade classifiers and manually created datasets cropped for each object.


## AI/ML Algorithms ##
In a single sentence, mention the AI and ML algorithm(s) you anticipate using for your project. It does not
have to be a detailed description of the algorithm, even the sub-area of the field is sufficient. Examples of this
include “planning with dynamic programming”, “reinforcement learning with neural function approximator”,
“deep learning for images”, “min-max tree search with pruning”, and so on.

**ANS:** Feature detection using Haar Feature-based Cascade Classifiers. We will apply convolution to the image to assist in feature detection, line detection and other image processing functions. 

## Evaluation Plan ##
As described in class, mention how you will evaluate the success of your project. In a paragraph, focus on the
quantitative evaluation: what are the metrics, what are the baselines, how much you expect your approach to
improve the metric by, what data will you evaluate on, etc. In another paragraph, describe what qualitative analysis
you will show to verify the project works, such as what are the sanity cases for the approach, how will you visualize
the internals of the algorithm to verify it works, what’s your moonshot case, i.e. it’ll be awesome and impressive if
you get there. Note that these are not promises, we’re not going to hold you to what you say here, but we want to
see if you are able to think about evaluation of your project in a critical manner.

** ANS:** Our accuracy will be determined by how well the AI correctly classifies the mob in the world. We will create a graph the performance of the AI, comparing the performace with other classifiers trained with different datasets (i.e. more or less possitive and negative images). This will determine the best type of dataset. 
To verify that the algorithm is working, we plan to display a bounding box with the type of mob.
Our moonshot case will be spawning an enclosed with randomly generated mobs randomly walking around. The AI will then be tasked with classifing each mob, and ultimately locate a specific mob. Our accuracy measure will then be how quickly the AI can locate the mob, using reinforcement learning to navigate the world.

## Appointment with the Instructor ##
One member of the group should take an appointment with the instructor in the week starting 4/23 (or 4/30, if
no slots are available). Select a time such that all members of the group can attend, unless one or more members
of your group can absolutely not make any of the available times. In the proposal page, mention the date and time
you have reserved the appointment for.
Use the following link to make your appointment: [quickref]: https://calendly.com/sameersingh/office-hours

**ANS:** Made an appointment for Tuesday at 11:45am
