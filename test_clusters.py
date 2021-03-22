import unittest
import cluster_players


class ClusterTest(unittest.TestCase):
    def setUp(self):
        self.data = cluster_players.load_data()

    def testClustering(self):
        options = {
            'num_clusters': 20,
            'position': None,
            'data_filename': None,
            'unwanted_columns': cluster_players.default_unwanted_columns,
            'output_json': False
        }
        # num_clusters = 20
        # clustered = cluster_players.cluster_players(self.data, k=num_clusters)

        results = cluster_players.run_clusters(options)
        grouped_results = cluster_players.group_annotated_list_by_labels(
            results)

        # right number of clusters?
        assert(len(grouped_results.keys()) == options['num_clusters'])

        # no clusters should be empty
        for cluster in grouped_results.values():
            assert(len(cluster))


if __name__ == "__main__":
    unittest.main()
