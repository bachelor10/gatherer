import intersect
import math, uuid, os
import numpy as np
import keras
from itertools import cycle, combinations
from PIL import Image, ImageDraw

from time import time

class Boundingbox:
    def __init__(self, traces):
        
        max_x = 0
        min_x = math.inf
        max_y = 0
        min_y = math.inf

        for trace in traces:
            y = np.array(trace).astype(np.float)
            x, y = y.T

            if max_x < x.max():
                max_x = x.max()

            if max_y < y.max():
                max_y = y.max()

            if min_x > x.min():
                min_x = x.min()

            if min_y > y.min():
                min_y = y.min()
            
        self.mid_x = (max_x + min_x)/2
        self.mid_y = (max_y + min_y)/2
        self.max_x = max_x
        self.max_y = max_y
        self.min_x = min_x
        self.min_y = min_y
        self.width = max_x - min_x
        self.height = max_y - min_y


class Group:
    def __init__(self, mid_x):
        self.mid_x = mid_x


class Regular(Group):
    def __init__(self, id, mid_x):
        Group.__init__(self, mid_x)
        self.id = id
    
    @staticmethod
    def asLatex(truth):
        if truth == 'sqrt' or truth == 'alpha' or truth == 'beta' or truth == 'Delta' or truth == 'gamma' or truth == 'infty' or truth == 'lambda' or truth == 'pi' or truth == 'mu' or truth == 'phi' or truth == 'sigma' or truth == 'sum' or truth == 'times' or truth == 'rightarrow':
            return '\\' + truth
        elif truth == 'gt':
            return '>'
        elif truth == 'lt':
            return '<'
        
        else:
            return truth


class Fraction(Group):
    def __init__(self, numerator, denominator, mid_x):
        Group.__init__(self, mid_x)
        self.numerator = numerator
        self.denominator = denominator


class Power:
    def __init__(self, base=None, exponent=None):
        self.base = base
        self.exponent = exponent

    def is_power(base, exponent):
        pass


class Trace:
    def __init__(self, points):
        self.points = points
        self.boundingbox = Boundingbox(points)

    def add_points(amount):
        pass

    def remove_points(amount):
        pass

    def check_overlap(trace):
        pass


class Segment:
    def __init__(self, traces, id, truth=''):
        self.traces = traces
        self.boundingbox = Boundingbox(traces)
        self.id = id
        self.truth = truth

    def print_info(self):
        print("\nSegment info for", self.id)
        print("Truth:", self.truth)
        print("Amount of traces:", len(self.traces))
        print("Length of traces", [len(t) for t in self.traces])
        b = self.boundingbox
        print("Boundingbox (x, y, w, h):", b.mid_x, b.mid_y, b.width, b.height)
        print("max_x, min_x, max_y, min_y", b.max_x, b.min_x, b.max_y, b.min_y)


    def add_trace(trace):
        # might be useful for live feedback
        pass


class Segmentgroup:
    def __init__(self, segments):
        self.segments = segments

    
class Expression:
    def __init__(self, predictor):
        start = time()
        self.groups = []
        self.segments = dict()
        self.predictor = predictor
        self.processed = []
        print("Created expression", str(time() - start) + "s")

    def create_tracegroups(self, traces, trace_pairs):
        tracegroups = []
        
        for i, trace in enumerate(traces):

            flag = False
            for j, group in enumerate(tracegroups):

                common = []
                for p in trace_pairs:
                    if i in p:
                        common = common + list(p)
                common = list(set(common))

                if len(set(common).intersection(group)) > 0:
                     tracegroups[j] = list(set(common + group))
                     flag = True

            if not flag:
                new_group = [i]
                for pair in trace_pairs:
                    if i in pair:
                        new_group = new_group + list(pair)
                
                new_group = list(set(new_group))
                tracegroups.append(new_group)
            
        sorted_tracegroups = sorted(tracegroups, key=lambda m:next(iter(m)))

        return sorted_tracegroups

    def find_overlap_pairs(self, traces):
        overlap_pairs = set()

        for i, trace in enumerate(traces[:-1]):
            for j, trace2 in enumerate(traces[i+1:]):
                for coord1 in trace:
                    for coord2 in trace2:
                        if math.hypot(coord2[0] - coord1[0], coord2[1] - coord1[1]) < 10:
                            overlap_pairs.add((i, i+j+1))

                # Check lines between endpoints
                overlap = intersect.intersect(trace[0], trace[-1], trace2[0], trace2[-1])
                if(overlap):
                    overlap_pairs.add((i, i+j+1))
        
        return overlap_pairs


    def feed_traces(self, traces):
        start = time()
        overlap_pairs = self.find_overlap_pairs(traces)
        tracegroups = self.create_tracegroups(traces, overlap_pairs)
        self.create_segments(traces, tracegroups)
        print("Feed traces time", str(time() - start) + "ms")

        #for id, segment in self.segments.items():
        #    segment.print_info()


    def create_segments(self, traces, tracegroups):
        for i, group in enumerate(tracegroups):
            traces_for_segment = [traces[j] for j in list(group)]
            id = str(i)
            segment = Segment(traces_for_segment, id)
            self.segments[id] = segment

    def join_segments(self, id1, id2, truth=''):
        segment1 = self.segments.pop(id1, None)
        segment2 = self.segments.pop(id2, None)

        traces = segment1.traces + segment2.traces
        id = segment1.id

        new_segment = Segment(traces, id, truth)
        self.segments[id] = new_segment
        
    
    def find_segments_in_area(self, max_x, min_x, max_y, min_y, ignore=[]):
        # Searches through segments and look for middle points inside area
        segments_in_area = []

        for id, segment in self.segments.items():
            if min_x <= segment.boundingbox.mid_x <= max_x and min_y <= segment.boundingbox.mid_y <= max_y:
                if segment.id not in ignore:
                    segments_in_area.append(segment.id)

        return segments_in_area


    def sort_id_list_x(self, ids):
        return [seg.id for seg in sorted([self.segments[id] for id in ids], key=lambda x: x.boundingbox.mid_x, reverse=False)]


    def sort_groups(self):
        self.groups.sort(key=lambda group: group.mid_x, reverse=False)


    def is_fraction(self, id):
        coords = self.segments[id].boundingbox
        ignore = [id]
        over = self.find_segments_in_area(coords.max_x, coords.min_x, coords.min_y, coords.min_y - 200, ignore)
        under = self.find_segments_in_area(coords.max_x, coords.min_x, coords.max_y + 200, coords.max_y, ignore)

        print("Found fractions", len(over), len(under))
        return len(over) > 0 and len(under) > 0, over, under


    def find_fractions(self, ids):
        new_ids = []

        for minus_id in ids:
            is_frac, over, under = self.is_fraction(minus_id)

            if is_frac:
                # Create new fraction
                over = self.sort_id_list_x(over)
                under = self.sort_id_list_x(under)
                self.segments[minus_id].truth = 'frac'

                mid_x = self.segments[minus_id].boundingbox.mid_x

                fraction = Fraction(over, under, mid_x)
                self.groups.append(fraction)

                # Set minus_id, over and under to processed
                self.processed.append(minus_id)
                self.processed = self.processed + over + under

            else:
                new_ids.append(minus_id)

        return new_ids


    def is_equalsign(self, id1, id2):
        
        coords1 = self.segments[id1].boundingbox
        coords2 = self.segments[id2].boundingbox

        return np.abs(coords1.mid_x - coords2.mid_x) < 50


    def find_equalsigns(self, ids):

        still_equalsigns = True
        while still_equalsigns:
            for pair in combinations(ids, r=2):
                if self.is_equalsign(pair[0], pair[1]):
                    self.join_segments(pair[0], pair[1], truth='=')
                    del ids[ids.index(pair[0])]
                    del ids[ids.index(pair[1])]
                    break
            else:
                still_equalsigns = False


    def classify_segments(self):

        minus_ids = []
        for id, segment in self.segments.items():
            segment.truth = self.predictor.predict(segment.traces)

            if segment.truth == '-':
                minus_ids.append(segment.id)
        
        # Check if minus signs is fractions
        start = time()
        updated_ids = self.find_fractions(minus_ids)

        # Check if minus signs is equalsigns
        if len(updated_ids) > 1:
            self.find_equalsigns(updated_ids)

        #for id, segment in self.segments.items():
        #    segment.print_info()
        for id, segment in self.segments.items():
            if id not in self.processed:

                mid_x = self.segments[id].boundingbox.mid_x

                self.groups.append(Regular(id, mid_x))
                self.processed.append(id)
        
        # Sort groups
        self.sort_groups()
        print("Post processing", str(time() - start) + "ms")



    def search_horizontal(self):
        
        pass


    def create_segmentgroups(self):
        pass


    def  get_latex_pwr(self, power):
        pass


    def get_latex_frac(self, frac):

        print(frac.numerator)
        print(frac.denominator)

        numerator = ''.join([self.segments[seg].truth for seg in frac.numerator])
        denominator = ''.join([self.segments[seg].truth for seg in frac.denominator])

        return '\\frac{' + numerator + '}{' + denominator + '}'


    def get_latex(self):
        latex = ''
        for group in self.groups:
            if type(group) is Fraction:
                latex += self.get_latex_frac(group)
            elif type(group) is Regular:
                latex += Regular.asLatex(self.segments[group.id].truth)
                #latex += self.segments[group.id].truth
        
        print(latex)
        return latex

    def get_truth(self):

        pass


class Predictor:
    MODEL_PATH = os.getcwd() + '/machine_learning/my_model.h5'
    #CLASSES = ["+", "-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "="]#os.listdir(os.getcwd() + '/machine_learning' + '/train')    
    #MODEL_PATH = os.getcwd() + '/my_model.h5'
    #CLASSES = os.listdir(os.getcwd() + '/machine_learning/train2')
    CLASS_INDICES = {']': 17, 'z': 38, 'int': 23, 'sqrt': 32, '3': 7, 'infty': 22, 'neq': 27, '6': 10, '0': 4, '[': 16, '7': 11, '4': 8, '(': 0, 'x': 36, 'alpha': 18, 'lambda': 24, 'beta': 19, 'rightarrow': 30, '8': 12, ')': 1, '=': 14, 'y': 37, 'phi': 28, 'times': 35, '1': 5, 'lt': 25, 'Delta': 15, 'gamma': 20, '9': 13, 'pi': 29, '2': 6, 'sum': 33, 'theta': 34, 'mu': 26, '-': 3, 'gt': 21, '+': 2, 'sigma': 31, '5': 9}

    def __init__(self):
        self.model = keras.models.load_model(Predictor.MODEL_PATH)

    def predict(self, segment_traces):
        start = time()
        processed = self.pre_process(segment_traces)
        print("Preprocess time", str(time() - start) + "ms")
        start = time()
        output = self.model.predict_proba(processed)
        print("Predicted", output)
        print("Predict Time", str(time() - start) + "ms")
        
        proba_index = np.argmax(output[0])
        for key, value in Predictor.CLASS_INDICES.items():
            if value == proba_index:
                return key
        """
        for i, p in enumerate(output[0]):

            if p > best_pred[1]:
                best_pred = (i, p)
                Predictor.CLASS_INDICES
                prediction = Predictor.CLASSES[i]
        """
        #return prediction
        
    #https://gist.github.com/perrygeo/4512375
    def scale_linear_bycolumn(self, rawpoints, high=24, low=0, ma=0, mi=0):
        mins = mi
        maxs = ma

        rng = maxs - mins

        output = high - (((high - low) * (maxs - rawpoints)) / rng)

        return output

    def pre_process(self, traces):
        resolution = 24
        image_resolution = 26

        image = Image.new('L', (image_resolution, image_resolution), "white")
        draw = ImageDraw.Draw(image)

        max_x = 0
        min_x = math.inf
        max_y = 0
        min_y = math.inf


        for trace in traces:
            y = np.array(trace).astype(np.float)
            x, y = y.T

            if max_x < x.max():
                max_x = x.max()

            if max_y < y.max():
                max_y = y.max()

            if min_x > x.min():
                min_x = x.min()

            if min_y > y.min():
                min_y = y.min()

        width = max_x - min_x
        height = max_y - min_y
        scale = width / height

        width_scale = 0
        height_scale = 0

        if scale > 1:
            # width > height
            height_scale = resolution / scale
        else:
            # width < height
            width_scale = resolution * scale

        for trace in traces:

            y = np.array(trace).astype(np.float)

            x, y = y.T

            if width_scale > 0:
                # add padding in x-direction
                new_y = self.scale_linear_bycolumn(y, high=resolution, low=0, ma=max_y, mi=min_y)
                side = (resolution - width_scale) / 2
                new_x = self.scale_linear_bycolumn(x, high=(resolution - side), low=(side), ma=max_x, mi=min_x)
            else:
                # add padding in y-direction
                new_x = self.scale_linear_bycolumn(x, high=resolution, low=0, ma=max_x, mi=min_x)  # , maximum=(max_x, max_y), minimum=(min_x, min_y))
                side = (resolution - height_scale) / 2
                new_y = self.scale_linear_bycolumn(y, high=(resolution - side), low=(side), ma=max_y, mi=min_y)  # , maximum=(max_x, max_y), minimum=(min_x, min_y))

            coordinates = list(zip(new_x, new_y))
            xy_cycle = cycle(coordinates)

            next(xy_cycle)

            for x_coord, y_coord in coordinates[:-1]:
                next_coord = next(xy_cycle)
                draw.line([x_coord, y_coord, next_coord[0], next_coord[1]], fill="black", width=1)


        i = image.convert('LA')

        arr = np.asarray(i)

        formatted = []
        for row in arr:
            new_row = []
            for col in row:
                new_row.append(col[0])

            formatted.append(new_row)

        return np.asarray([np.asarray(formatted).reshape((26, 26, 1))])

if __name__ == '__main__':

    traces = [0,1,2,3,4,5,6,7]
    overlap = [(1,2),(2,3),(4,5),(0,7)]

    exp = Expression()

    b = exp.create_tracegroups(traces, overlap)

    print(b)
    