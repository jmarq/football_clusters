import unittest
import cluster_players

class ClusterTest(unittest.TestCase):
    def setUp(self):
        self.data = cluster_players.load_data()

    def testClustering(self):
        num_clusters = 20
        clustered = cluster_players.cluster_players(self.data, k=num_clusters)
    
        # right number of clusters?
        assert(len(clustered)==num_clusters)

        # no clusters should be empty
        for cluster in clustered:
            assert(len(cluster))


if __name__ == "__main__":
    unittest.main()
