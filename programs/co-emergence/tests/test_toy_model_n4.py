"""Regression tests for N=4 toy model.

Reproduces the results from the original 2026-03-04-toy-model.py script
and Remark 8 in the co-emergence paper.
"""

import numpy as np
import pytest

from .toy_model import CoEmergenceModel


class TestN4Riemannian:
    """Riemannian (theta=0) fixed point: no quantum coherences."""

    def test_fixed_point_converges(self, model_n4_riem, fp_n4_riem):
        Fpsi = model_n4_riem.F_map(fp_n4_riem)
        err = CoEmergenceModel.rho_distance(Fpsi, fp_n4_riem)
        assert err < 1e-10

    def test_no_imaginary_coherence(self, fp_n4_riem):
        rho = CoEmergenceModel.partial_trace(fp_n4_riem, (2, 2), (0,))
        assert abs(rho[0, 1].imag) < 1e-10

    def test_density_matrix_valid(self, fp_n4_riem):
        rho = CoEmergenceModel.partial_trace(fp_n4_riem, (2, 2), (0,))
        # Hermitian
        assert np.linalg.norm(rho - rho.conj().T) < 1e-12
        # Trace 1
        assert abs(np.trace(rho) - 1.0) < 1e-12
        # PSD
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues > -1e-12)


class TestN4Lorentzian:
    """Lorentzian (theta=1) fixed point: quantum coherences present."""

    def test_fixed_point_converges(self, model_n4_lor, fp_n4_lor):
        Fpsi = model_n4_lor.F_map(fp_n4_lor)
        err = CoEmergenceModel.rho_distance(Fpsi, fp_n4_lor)
        assert err < 1e-10

    def test_has_imaginary_coherence(self, fp_n4_lor):
        rho = CoEmergenceModel.partial_trace(fp_n4_lor, (2, 2), (0,))
        assert abs(rho[0, 1].imag) > 1e-3

    def test_density_matrix_valid(self, fp_n4_lor):
        rho = CoEmergenceModel.partial_trace(fp_n4_lor, (2, 2), (0,))
        assert np.linalg.norm(rho - rho.conj().T) < 1e-12
        assert abs(np.trace(rho) - 1.0) < 1e-12
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues > -1e-12)

    def test_spectral_radius_below_one(self, model_n4_lor, fp_n4_lor):
        sr = model_n4_lor.spectral_radius(fp_n4_lor)
        assert sr < 1.0

    def test_purity_below_one(self, fp_n4_lor):
        rho = CoEmergenceModel.partial_trace(fp_n4_lor, (2, 2), (0,))
        purity = np.trace(rho @ rho).real
        assert purity < 1.0 - 1e-6, "Lorentzian should produce entanglement (purity < 1)"
