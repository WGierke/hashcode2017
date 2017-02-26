import itertools
import numpy as np
import operator
from tqdm import tqdm
from os import listdir
from os.path import isfile, join

class Network:
    def __init__(self, path):
        self.path = path
        self.V = -1
        self.E = -1
        self.R = -1
        self.C = -1
        self.X = -1
        self.video_sizes = None

        self.read_static_data()
        self.datacenter_latencies = np.zeros(self.E)
        self.latencies = -np.ones((self.E, self.C))
        self.requests = np.zeros((self.V, self.E))
        self.savings = np.zeros((self.E, self.C))

        self.read_data()

    def read_static_data(self):
        with open(self.path) as f:
            data = f.readlines()
        first_row = data[0].split(' ')
        second_row = data[1].split(' ')
        self.V, self.E, self.R, self.C, self.X = [int(x) for x in first_row]
        self.video_sizes = [int(x) for x in second_row]

    def read_data(self):
        with open(self.path) as f:
            data = f.readlines()
        i = 2
        for endpoint_index in range(self.E):
            self.datacenter_latencies[
                endpoint_index], number_connected_caches = [int(x) for x in
                                                            data[i].split(' ')]
            i += 1
            for _ in range(1, number_connected_caches + 1):
                cache_id, latency = [int(x) for x in data[i].split(' ')]
                i += 1
                self.latencies[endpoint_index, cache_id] = latency
        for line in data[i:]:
            video_id, endpoint_id, r = [int(x) for x in line.split(' ')]
            self.requests[video_id, endpoint_id] = r
        for e, c in itertools.product(range(self.E), range(self.C)):
            if self.latencies[e, c] >= 0:
                self.savings[e, c] = self.datacenter_latencies[e] - \
                                     self.latencies[e, c]

    def solve(self):
        video_improvements = dict() # Endpoint_ID -> Video_ID -> (Requests * Average Saving) / Video_Size
        for endpoint_id in tqdm(range(self.requests.shape[1])):
            video_improvements[endpoint_id] = dict()
            for video_id in range(self.requests.shape[0]):
                requests = self.requests[video_id][endpoint_id]
                if np.count_nonzero(self.savings[endpoint_id]) > 0:
                    average_saving = self.savings[endpoint_id].sum() / np.count_nonzero(self.savings[endpoint_id])
                else:
                    average_saving = 0
                # Milliseconds improvement if video would be cached divided by video size
                video_improvements[endpoint_id][video_id] = (requests * average_saving) / self.video_sizes[video_id]

        transformed_improvements = dict() # Video_value -> Endpoint_ID -> [Video_IDs]
        for endpoint_id in tqdm(video_improvements.keys()):
            for video_id in video_improvements[endpoint_id].keys():
                video_value = video_improvements[endpoint_id][video_id]
                if video_value in transformed_improvements.keys():
                    if endpoint_id in transformed_improvements[video_value].keys():
                        transformed_improvements[video_value][endpoint_id].append(video_id)
                    else:
                        transformed_improvements[video_value][endpoint_id] = [video_id]
                else:
                    transformed_improvements[video_value] = {endpoint_id: [video_id]}
        transformed_improvements[0] = dict()
        sorted_transformed_improvements = sorted(transformed_improvements.items(), key=operator.itemgetter(0), reverse=True)

        free_cache_space = np.full(self.C, self.X)
        cached_videos = np.zeros((self.C, self.V))
        for video_value, endpoint_videos in tqdm(sorted_transformed_improvements):
            for endpoint_id in endpoint_videos.keys():
                cache_servers = np.nonzero(self.latencies[endpoint_id] > -1)[0]
                for video_id in endpoint_videos[endpoint_id]:
                    # Check if video is already in a cache server of the endpoint
                    for cache_id in cache_servers:
                        if cached_videos[cache_id][video_id] == 0:
                            if free_cache_space[cache_id] >= self.video_sizes[video_id]:
                                cached_videos[cache_id][video_id] = 1
                                free_cache_space[cache_id] -= self.video_sizes[video_id]
                                break


        with open(self.path.replace("in", "out"), 'w') as f:
            f.write('{}'.format(self.C))
            for c in range(cached_videos.shape[0]):
                f.write('\n{} {}'.format(str(c), ' '.join([str(x) for x in np.nonzero(cached_videos[c])[0]])))


if __name__ == "__main__":
    INPUT_PATH = "data"
    input_files = [f for f in listdir(INPUT_PATH) if isfile(join(INPUT_PATH, f))]
    for f in input_files:
        file_path = INPUT_PATH + '/' + f
        print("Solving " + file_path)
        n = Network(file_path)
        n.solve()
