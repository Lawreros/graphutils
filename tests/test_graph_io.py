import os
import shutil
from pathlib import Path
import re

import pytest
import numpy as np
import networkx as nx
from graphutils.graph_io import NdmgDirectory
from graphutils import graph_io


DATAPATH = "/Users/alex/Dropbox/NeuroData/graphutils/tests/test_data"
# TODO : make sure pass_to_ranks does what I think it does


@pytest.fixture
def basedir(tmp_path):
    # populate tmpdir with file
    # TODO : figure out how to not have to instantiate this every time
    #        a test is run
    for filename in Path(DATAPATH).iterdir():
        shutil.copy(filename, tmp_path)
    return tmp_path


@pytest.fixture
def ND(basedir):
    # so that I don't have to instantiate all the time
    return NdmgDirectory(basedir)


class TestNdmgDirectory:
    def test_dir(self, basedir):
        assert isinstance(basedir, Path)

    def test_object_has_attributes(self, ND):
        assert all(
            hasattr(ND, attr) for attr in ["delimiter", "directory", "name", "files", "vertices", "graphs", "subjects"]
        )

        assert ND.directory, "directory doesn't exist"
        assert ND.files, "no files found"
        assert ND.vertices, "vertices not calculated properly"
        assert ND.graphs, "graphs doesn't exist"
        assert ND.subjects, "subjects doesn't exist"


    def test_files_has_data(self, ND):
        # check if there are files
        assert len(ND.files) != 0, f"{dir(ND)}"

        # check if all files have data in them
        for filename in ND.files:
            # TODO : dynamic delimiter, should be ND.delimiter
            array = np.genfromtxt(str(filename), delimiter=" ")
            assert array.shape[1] == 3
        

    def test_ordering(self, ND):
        # test if ordering of all properties correspond
        for i, _ in enumerate(ND.files):
            graphi_file = ND.files[i]
            graphi_subject = ND.subjects[i]
            graphi_graph = ND.graphs[i]
            # graphi_X = ND.X[i].reshape(
            #     int(np.sqrt(ND.X.shape[1])), int(np.sqrt(ND.X.shape[1]))
            # )  # TODO

            # graphs/X-rows correspond to same scan
            # assert np.array_equal(graphi_graph, graphi_X)  # TODO

            # subject/files correspond to same scan
            pattern = r"(?<=sub-)(\w*)(?=_ses)"
            assert re.findall(pattern, str(graphi_file))[0] == graphi_subject
            # subject/files and graphs/X-rows correspond to the same scan
            current_NX = nx.read_weighted_edgelist(
                graphi_file, nodetype=int, delimiter=ND.delimiter
            )
            graph_from_file_i = nx.to_numpy_array(
                current_NX, nodelist=ND.vertices, dtype=np.float
            )
            assert np.array_equal(graph_from_file_i, graphi_graph)

# TODO : tests for NdmgDiscrim
    # def test_PTR(self, ND):
    #     # TODO : make sure I can recreate X and Y from the files in `save_X_and_Y`
    #     # TODO : make sure I refresh the NdmgDirectory object after testing _pass_to_ranks
    #     pass

    # def test_save_X_and_Y(self, ND, tmp_path_factory):  # TODO
    #     # assert we can recreate X and Y from the csv's
    #     tmp = tmp_path_factory.mktemp("savedir")
    #     saveloc = ND.save_X_and_Y(tmp)

    #     X = np.loadtxt(saveloc.X, delimiter=",")
    #     Y = np.loadtxt(saveloc.Y, dtype=str)

    #     assert np.array_equal(ND.X, X)
    #     assert np.array_equal(ND.Y, Y)

