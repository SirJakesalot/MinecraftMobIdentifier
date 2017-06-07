#This program returns the centroids of each MOB in a cropped image
image1 = [[.5,.3,.2,0,0], [.2,.1,.4,.3,0], [0,0,.9,.1,0], [.1,.9,0,0,0], [.1,.4,.4,0,.1], [.1,.1,.8,0,0], [0,1,0,0,0], [0,.6,.4,0,0]]
image2 = [[0,0,0,0,0], [0,0,0,0,0], [.2,.1,0,0,.7], [.2,0,0,.5,.3], [.9,0,0,0,.1], [0,0,0,0,1], [.4,.1,.1,.4,0], [.8,0,0,0,.2], [0,0,0,.1,.9]]
image3 = [[0,1,0,0,0], [0,.9,.1,0,0], [.4,0,0,.1,.5], [.6,0,.1,0,.3], [.1,.3,.4,.2,0], [.5,.4,0,.1,0], [.5,0,0,.2,.3], [.4,.2,0,.1,.3], [0,0,0,0,0]]
image4 = [[0,0,.4,.6,0], [0,.1,0,.9,0], [0,0,0,.9,.1], [.1,0,0,.9,0], [0,0,0,1,0], [.2,0,0,.8,0], [0,0,.1,.7,.2], [0,0,0,1,0]]

import numpy as np

class locate_identify:
    def __init__(self, image, segment_size):
        self.image = image
        self.segment_size = segment_size
        self.label_key = ['chicken', 'cow', 'mushroom_cow', 'pig', 'sheep']
        self.segment_location = {'0': (segment_size *.5, segment_size*2.5),
                                 '1': (segment_size*1.5, segment_size*2.5),
                                 '2': (segment_size*2.5, segment_size*2.5),
                                 '3': (segment_size *.5, segment_size*1.5),
                                 '4': (segment_size*1.5, segment_size*1.5),
                                 '5': (segment_size*2.5, segment_size*1.5),
                                 '6': (segment_size *.5, segment_size *.5),
                                 '7': (segment_size*1.5, segment_size *.5),
                                 '8': (segment_size*2.5, segment_size *.5),}
        self.adjacent_segments = {'0': [(1,'right'), (3,'down'), (4,'downright')],
                                  '1': [(0,'left'), (2,'right'), (3,'downleft'), (4,'down'), (5,'downright')],
                                  '2': [(1,'left'), (4,'downleft'), (5,'down')],
                                  '3': [(0,'up'), (1,'upright'), (4,'right'), (6,'down'), (7,'downright')],
                                  '4': [(0,'upleft'), (1,'up'), (2,'upright'), (3,'left'), (5,'right'), (6,'downleft'), (7,'down'), (8,'downright')],
                                  '5': [(1,'upleft'), (2,'up'), (4,'left'), (7,'downleft'), (8,'down')],
                                  '6': [(3,'up'), (4,'upright'), (7,'right')],
                                  '7': [(3,'upleft'), (4,'up'), (5,'upright'), (6,'left'), (8,'right')],
                                  '8': [(4,'upleft'), (5,'up'), (7,'left')]}
        self.move_value = {'up': (0,segment_size),
                           'down': (0,segment_size*-1),
                           'left': (segment_size*-1,0),
                           'right': (segment_size,0),
                           'upleft': (segment_size*-1, segment_size),
                           'upright': (segment_size, segment_size),
                           'downleft': (segment_size*-1, segment_size*-1),
                           'downright': (segment_size, segment_size*-1)}
        self.centroids = {}

    def initialize_centroids(self):
        '''Create a centroid for every unique MOB, with highest confidence in a segment'''
        total_confidences = [0, 0, 0, 0, 0]
        for segment in self.image:
            self.centroids[self.label_key[np.argmax((segment))]] = (0, 0)
            for index, value in enumerate(total_confidences):
                total_confidences[index] = total_confidences[index] + segment[index]
        return total_confidences

    def remove_bad_centroids(self, total_confidences):
        '''Remove all centroids in which total MOB confidence is less than 1'''
        remove_list = []
        for key, value in self.centroids.items():
            if total_confidences[self.label_key.index(key)] < 1:
                remove_list.append(key)
        for key in remove_list:
            del self.centroids[key]

    def find_starting_centroids(self):
        '''Initialize centroid coordinates to center of segment with highest confidence for each unique MOB'''
        initial_segment = {}
        for key, value in self.centroids.items():
            max_confidence = 0
            location = 0
            index = self.label_key.index(key)
            for count, segment in enumerate(self.image):
                if segment[index] > max_confidence:
                    max_confidence = segment[index]
                    location = count
            self.centroids[key] = self.segment_location[str(location)]
            initial_segment[key] = location
        return initial_segment

    def find_best_centroids(self, initial_segment):
        '''Adjust the coordinates of each centroid according to adjacent segments'''
        for key, value in self.centroids.items():
            for segment, direction in self.adjacent_segments[str(initial_segment[key])]:
                direction_tuple = self.move_value[direction]
                segment_confidence = self.image[segment][self.label_key.index(key)] * .5
                self.centroids[key] = (self.centroids[key][0] + direction_tuple[0] * segment_confidence,
                                  self.centroids[key][1] + direction_tuple[1] * segment_confidence)

    def find_centroids(self):
        '''Find centroids of each MOB in the view'''
        self.remove_bad_centroids(self.initialize_centroids())
        self.find_best_centroids(self.find_starting_centroids())
        return self.centroids





if __name__ == '__main__':
    identifier = locate_identify(image1,24)
    centroids = identifier.find_centroids()
    print(centroids)
