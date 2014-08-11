"""
analysis_by_synthesis.py

Perform analysis-based recovery based on synthesis recovery
"""

import numpy as np

from base import AnalysisSparseSolver, SparseSolver


class AnalysisBySynthesis(AnalysisSparseSolver):

    # All parameters related to the algorithm itself are given here.
    # The data and dictionary are given to the solve() method
    def __init__(self, synthesis_solver, nullspace_multiplier=1):

        assert isinstance(synthesis_solver, SparseSolver)
        self.synthsolver = synthesis_solver
        self.nullspace_multiplier = nullspace_multiplier

    def __str__(self):
        return "AbS (" + str(self.synthsolver) + ", " + str(self.nullspace_multiplier) + ")"

    def solve(self, measurements, acqumatrix, operator):

        # Ensure measurements 2D
        if len(measurements.shape) == 1:
            data = np.atleast_2d(measurements)
            if measurements.shape[0] < measurements.shape[1]:
                measurements = np.transpose(measurements)

        operatorsize, signalsize = operator.shape
        # Find nullspace
        dictionary = np.linalg.pinv(operator)
        U,S,Vt = np.linalg.svd(dictionary)
        nullspace = Vt[-(operatorsize-signalsize):, :]
        # Create aggregate dictionary
        mul = self.computeMultiplier(measurements, acqumatrix, operator)
        Atilde = np.vstack((np.dot(acqumatrix, dictionary), mul * nullspace))
        ytilde = np.concatenate((measurements, np.zeros((operatorsize-signalsize, measurements.shape[1]))))

        return np.squeeze(np.dot(dictionary, self.synthsolver.solve(ytilde, Atilde)))

    def computeMultiplier(self, measurements, acqumatrix, operator):
        """
        Computes the value of the nullspace multipler

        :param measurements: Measurements matrix
        :param acqumatrix: Acquisition matrix
        :param operator: Operator
        :return: Value of the multiplier
        """

        mul = self.nullspace_multiplier
        #mul = self.nullspace_multiplier *\
        #      np.linalg.norm(np.dot(acqumatrix, dictionary), 'fro') / np.linalg.norm(nullspace, 'fro')
        #mul = self.nullspace_multiplier * \
        #    np.linalg.norm(dictionary, 'fro') / np.linalg.norm(nullspace, 'fro')

        return mul

