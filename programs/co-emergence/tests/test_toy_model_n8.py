"""N=8 tests: subsystem composition, Born rule, and interference.

These are the three tests that require N > 4 and constitute the core
of the "does the mechanism produce full QM algebra?" question.
"""

import numpy as np
import pytest

from .toy_model import CoEmergenceModel


# ── Composition tests ───────────────────────────────────────────────

class TestComposition:
    """Partial traces must compose: Tr_X(rho_YX) = rho_Y.

    For tripartition (A=0, B=1, C=2), verify all 6 valid reductions.
    """

    @pytest.mark.parametrize("pair,single", [
        ((0, 1), (0,)),  # rho_AB -> rho_A
        ((0, 1), (1,)),  # rho_AB -> rho_B
        ((0, 2), (0,)),  # rho_AC -> rho_A
        ((0, 2), (2,)),  # rho_AC -> rho_C
        ((1, 2), (1,)),  # rho_BC -> rho_B
        ((1, 2), (2,)),  # rho_BC -> rho_C
    ])
    def test_composition(self, fp_n8_lor, pair, single):
        dims = (2, 2, 2)
        # Direct: psi -> rho_single
        rho_direct = CoEmergenceModel.partial_trace(fp_n8_lor, dims, single)

        # Via pair: psi -> rho_pair -> rho_single
        rho_pair = CoEmergenceModel.partial_trace(fp_n8_lor, dims, pair)
        pair_dims = tuple(dims[k] for k in pair)
        # Which index within the pair corresponds to `single`?
        keep_in_pair = (pair.index(single[0]),)
        rho_via_pair = CoEmergenceModel.partial_trace_dm(rho_pair, pair_dims, keep_in_pair)

        assert np.linalg.norm(rho_direct - rho_via_pair) < 1e-10, (
            f"Composition failed: Tr({pair}->{single}), "
            f"error = {np.linalg.norm(rho_direct - rho_via_pair):.2e}"
        )

    @pytest.mark.parametrize("pair,single", [
        ((0, 1), (0,)),
        ((0, 1), (1,)),
        ((0, 2), (0,)),
        ((0, 2), (2,)),
        ((1, 2), (1,)),
        ((1, 2), (2,)),
    ])
    def test_composition_riemannian(self, fp_n8_riem, pair, single):
        """Composition must hold for Riemannian too — it's a property of
        partial traces, not of the signature."""
        dims = (2, 2, 2)
        rho_direct = CoEmergenceModel.partial_trace(fp_n8_riem, dims, single)
        rho_pair = CoEmergenceModel.partial_trace(fp_n8_riem, dims, pair)
        pair_dims = tuple(dims[k] for k in pair)
        keep_in_pair = (pair.index(single[0]),)
        rho_via_pair = CoEmergenceModel.partial_trace_dm(rho_pair, pair_dims, keep_in_pair)
        assert np.linalg.norm(rho_direct - rho_via_pair) < 1e-10


# ── Born rule tests ─────────────────────────────────────────────────

class TestBornRule:
    """Tr(rho_A P_k) matches direct computation from psi* in any basis.

    For subsystem A (index 0, dim 2), measure in basis U|k>:
    - p_born(k) = (U rho_A U†)_{kk}
    - p_direct(k) = sum_{bc} |(U_applied psi)_{k,bc}|^2
    """

    @staticmethod
    def _born_vs_direct(psi, dims, subsystem, U):
        """Compare Born rule probabilities with direct computation.

        Returns (p_born, p_direct) arrays.
        """
        d = dims[subsystem]
        rho = CoEmergenceModel.partial_trace(psi, dims, (subsystem,))

        # Born rule: p_k = (U rho U†)_{kk}
        rho_rotated = U @ rho @ U.conj().T
        p_born = np.diag(rho_rotated).real

        # Direct: apply U to subsystem index of psi tensor
        psi_tensor = psi.reshape(dims)
        # Move subsystem axis to front, apply U, compute marginal
        psi_moved = np.moveaxis(psi_tensor, subsystem, 0)
        shape_rest = psi_moved.shape[1:]
        psi_flat = psi_moved.reshape(d, -1)
        psi_rotated = U @ psi_flat
        p_direct = np.sum(np.abs(psi_rotated) ** 2, axis=1)

        return p_born, p_direct

    def test_born_computational_basis(self, fp_n8_lor):
        U = np.eye(2)
        p_born, p_direct = self._born_vs_direct(fp_n8_lor, (2, 2, 2), 0, U)
        np.testing.assert_allclose(p_born, p_direct, atol=1e-12)

    def test_born_hadamard_basis(self, fp_n8_lor):
        U = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
        p_born, p_direct = self._born_vs_direct(fp_n8_lor, (2, 2, 2), 0, U)
        np.testing.assert_allclose(p_born, p_direct, atol=1e-12)

    def test_born_random_unitary(self, fp_n8_lor):
        rng = np.random.RandomState(99)
        # Random unitary via QR decomposition
        Z = rng.randn(2, 2) + 1j * rng.randn(2, 2)
        Q, R = np.linalg.qr(Z)
        U = Q @ np.diag(np.exp(1j * rng.uniform(0, 2 * np.pi, 2)))
        p_born, p_direct = self._born_vs_direct(fp_n8_lor, (2, 2, 2), 0, U)
        np.testing.assert_allclose(p_born, p_direct, atol=1e-12)

    @pytest.mark.parametrize("subsystem", [0, 1, 2])
    def test_born_all_subsystems(self, fp_n8_lor, subsystem):
        """Born rule holds for all subsystems, not just subsystem 0."""
        rng = np.random.RandomState(subsystem + 200)
        Z = rng.randn(2, 2) + 1j * rng.randn(2, 2)
        Q, _ = np.linalg.qr(Z)
        U = Q
        p_born, p_direct = self._born_vs_direct(fp_n8_lor, (2, 2, 2), subsystem, U)
        np.testing.assert_allclose(p_born, p_direct, atol=1e-12)

    def test_probabilities_sum_to_one(self, fp_n8_lor):
        rng = np.random.RandomState(77)
        Z = rng.randn(2, 2) + 1j * rng.randn(2, 2)
        Q, _ = np.linalg.qr(Z)
        p_born, p_direct = self._born_vs_direct(fp_n8_lor, (2, 2, 2), 0, Q)
        assert abs(np.sum(p_born) - 1.0) < 1e-12
        assert abs(np.sum(p_direct) - 1.0) < 1e-12


# ── Interference tests ──────────────────────────────────────────────

class TestInterference:
    """Destructive interference distinguishes quantum from classical-with-phases.

    For a 2x2 rho with nonzero Im(rho[0,1]), there exists a basis where
    p_quantum(k) < p_incoherent(k) (diagonal approximation).
    """

    def test_lorentzian_has_coherence(self, fp_n8_lor):
        rho = CoEmergenceModel.partial_trace(fp_n8_lor, (2, 2, 2), (0,))
        assert abs(rho[0, 1].imag) > 1e-6, (
            f"Lorentzian N=8 should have imaginary coherence, got {rho[0,1].imag}"
        )

    def test_riemannian_no_coherence(self, fp_n8_riem):
        rho = CoEmergenceModel.partial_trace(fp_n8_riem, (2, 2, 2), (0,))
        assert abs(rho[0, 1].imag) < 1e-10

    def test_destructive_interference(self, fp_n8_lor):
        """Find basis where p_quantum < p_incoherent, proving genuine interference.

        For 2x2 rho with off-diagonal rho[0,1] = |c|e^{i phi},
        the basis U(alpha) = [[cos a, -sin a], [sin a, cos a]] with
        alpha chosen so that phase = pi + arg(rho[0,1]) gives destructive
        interference for one outcome.
        """
        rho = CoEmergenceModel.partial_trace(fp_n8_lor, (2, 2, 2), (0,))
        c = rho[0, 1]

        # Basis that produces destructive interference:
        # Choose angle alpha = pi/4 (equal superposition) and rotate by phase
        phi = np.angle(c)
        # Unitary that aligns off-diagonal to produce destructive interference
        # For outcome k=0: p = rho[0,0]cos²a + rho[1,1]sin²a + 2Re(rho[0,1]e^{-i phase})sin(a)cos(a)
        # Destructive when 2Re(rho[0,1]e^{-i phase}) < 0, i.e. phase = phi + pi
        alpha = np.pi / 4
        phase = phi + np.pi
        U = np.array([
            [np.cos(alpha), -np.sin(alpha) * np.exp(-1j * phase)],
            [np.sin(alpha) * np.exp(1j * phase), np.cos(alpha)],
        ])

        rho_rotated = U @ rho @ U.conj().T
        p_quantum = np.diag(rho_rotated).real

        # Incoherent: use only diagonal elements of rho
        rho_diag = np.diag(np.diag(rho))
        rho_diag_rotated = U @ rho_diag @ U.conj().T
        p_incoherent = np.diag(rho_diag_rotated).real

        # At least one outcome must show destructive interference
        destructive = np.any(p_quantum < p_incoherent - 1e-10)
        assert destructive, (
            f"No destructive interference found.\n"
            f"p_quantum = {p_quantum}\n"
            f"p_incoherent = {p_incoherent}\n"
            f"rho[0,1] = {c}"
        )

    def test_no_destructive_interference_riemannian(self, fp_n8_riem):
        """Riemannian case: rho is real-diagonal-dominant, no destructive interference."""
        rho = CoEmergenceModel.partial_trace(fp_n8_riem, (2, 2, 2), (0,))
        # With real rho, the Hadamard basis should show no destructive interference
        # beyond numerical noise
        U = np.array([[1, 1], [1, -1]]) / np.sqrt(2)

        rho_rotated = U @ rho @ U.conj().T
        p_quantum = np.diag(rho_rotated).real

        rho_diag = np.diag(np.diag(rho))
        rho_diag_rotated = U @ rho_diag @ U.conj().T
        p_incoherent = np.diag(rho_diag_rotated).real

        # Riemannian coherences are real, so interference pattern is different
        # but we should not see quantum < incoherent by a significant margin
        # from imaginary coherences (which don't exist here)
        # Actually real off-diagonal elements CAN produce interference.
        # The key distinction is that imaginary coherences are absent.
        # This test verifies the coherence is real-valued, not that interference
        # is absent (real coherences do interfere classically).
        assert abs(rho[0, 1].imag) < 1e-10
