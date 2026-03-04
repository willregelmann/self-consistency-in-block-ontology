"""N=16 tests: three-level composition chain and scaling.

N=16 = 2x2x2x2 enables the three-level composition chain
rho_ABC -> rho_AB -> rho_A = rho_A (direct), which cannot be done at N=8.
"""

import numpy as np
import pytest

from .toy_model import CoEmergenceModel
from .conftest import _make_n16_h


# ── Three-level composition chain (N=16 exclusive) ─────────────────

class TestThreeLevelComposition:
    """rho_ABC -> rho_AB -> rho_A must equal direct rho_A.

    This tests composition at three levels of coarse-graining.
    """

    @pytest.mark.parametrize("triple,pair,single", [
        ((0, 1, 2), (0, 1), (0,)),  # ABC -> AB -> A
        ((0, 1, 2), (0, 2), (0,)),  # ABC -> AC -> A
        ((0, 1, 2), (1, 2), (1,)),  # ABC -> BC -> B
        ((1, 2, 3), (1, 2), (1,)),  # BCD -> BC -> B
        ((0, 2, 3), (0, 3), (0,)),  # ACD -> AD -> A
        ((0, 1, 3), (0, 1), (0,)),  # ABD -> AB -> A
    ])
    def test_three_level_chain(self, fp_n16_lor, triple, pair, single):
        dims = (2, 2, 2, 2)

        # Direct: psi -> rho_single
        rho_direct = CoEmergenceModel.partial_trace(fp_n16_lor, dims, single)

        # Via triple then pair:
        # psi -> rho_triple
        rho_triple = CoEmergenceModel.partial_trace(fp_n16_lor, dims, triple)
        triple_dims = tuple(dims[k] for k in triple)

        # rho_triple -> rho_pair
        keep_for_pair = tuple(triple.index(p) for p in pair)
        rho_pair = CoEmergenceModel.partial_trace_dm(rho_triple, triple_dims, keep_for_pair)
        pair_dims = tuple(dims[k] for k in pair)

        # rho_pair -> rho_single
        keep_for_single = (pair.index(single[0]),)
        rho_single = CoEmergenceModel.partial_trace_dm(rho_pair, pair_dims, keep_for_single)

        assert np.linalg.norm(rho_direct - rho_single) < 1e-10, (
            f"Three-level composition failed: {triple}->{pair}->{single}, "
            f"error = {np.linalg.norm(rho_direct - rho_single):.2e}"
        )


# ── Composition (same as N=8, adapted for 4 subsystems) ────────────

class TestCompositionN16:
    """Pairwise composition for N=16."""

    @pytest.mark.parametrize("pair,single", [
        ((0, 1), (0,)),
        ((0, 1), (1,)),
        ((0, 2), (0,)),
        ((2, 3), (3,)),
        ((1, 3), (1,)),
    ])
    def test_composition(self, fp_n16_lor, pair, single):
        dims = (2, 2, 2, 2)
        rho_direct = CoEmergenceModel.partial_trace(fp_n16_lor, dims, single)
        rho_pair = CoEmergenceModel.partial_trace(fp_n16_lor, dims, pair)
        pair_dims = tuple(dims[k] for k in pair)
        keep_in_pair = (pair.index(single[0]),)
        rho_via_pair = CoEmergenceModel.partial_trace_dm(rho_pair, pair_dims, keep_in_pair)
        assert np.linalg.norm(rho_direct - rho_via_pair) < 1e-10


# ── Born rule at N=16 ───────────────────────────────────────────────

class TestBornRuleN16:

    @pytest.mark.parametrize("subsystem", [0, 1, 2, 3])
    def test_born_rule_all_subsystems(self, fp_n16_lor, subsystem):
        dims = (2, 2, 2, 2)
        d = dims[subsystem]
        rng = np.random.RandomState(subsystem + 300)
        Z = rng.randn(d, d) + 1j * rng.randn(d, d)
        Q, _ = np.linalg.qr(Z)
        U = Q

        rho = CoEmergenceModel.partial_trace(fp_n16_lor, dims, (subsystem,))
        rho_rotated = U @ rho @ U.conj().T
        p_born = np.diag(rho_rotated).real

        psi_tensor = fp_n16_lor.reshape(dims)
        psi_moved = np.moveaxis(psi_tensor, subsystem, 0)
        psi_flat = psi_moved.reshape(d, -1)
        psi_rotated = U @ psi_flat
        p_direct = np.sum(np.abs(psi_rotated) ** 2, axis=1)

        np.testing.assert_allclose(p_born, p_direct, atol=1e-12)


# ── Interference at N=16 ───────────────────────────────────────────

class TestInterferenceN16:

    def test_lorentzian_has_coherence(self, fp_n16_lor):
        rho = CoEmergenceModel.partial_trace(fp_n16_lor, (2, 2, 2, 2), (0,))
        assert abs(rho[0, 1].imag) > 1e-6

    def test_destructive_interference(self, fp_n16_lor):
        rho = CoEmergenceModel.partial_trace(fp_n16_lor, (2, 2, 2, 2), (0,))
        c = rho[0, 1]
        phi = np.angle(c)
        alpha = np.pi / 4
        phase = phi + np.pi
        U = np.array([
            [np.cos(alpha), -np.sin(alpha) * np.exp(-1j * phase)],
            [np.sin(alpha) * np.exp(1j * phase), np.cos(alpha)],
        ])
        rho_rotated = U @ rho @ U.conj().T
        p_quantum = np.diag(rho_rotated).real
        rho_diag = np.diag(np.diag(rho))
        rho_diag_rotated = U @ rho_diag @ U.conj().T
        p_incoherent = np.diag(rho_diag_rotated).real
        assert np.any(p_quantum < p_incoherent - 1e-10)


# ── Robustness: multiple seeds ──────────────────────────────────────

class TestRobustness:
    """All random seeds must show Lorentzian coherence."""

    @pytest.mark.parametrize("seed", [456, 789, 1011, 1213, 1415])
    def test_coherence_across_seeds(self, seed):
        rng = np.random.RandomState(seed)
        h = rng.uniform(0.5, 1.5, size=16)
        model = CoEmergenceModel(
            dims=(2, 2, 2, 2), h=h, alphas=[0.5, 0.3, 0.4, 0.35],
            beta=0.4, gamma=-1.0 + 1j,
        )
        np.random.seed(seed + 1000)
        fps = model.find_fixed_points(n_starts=15)
        assert len(fps) > 0, f"No fixed point found for seed {seed}"

        # Check that at least one subsystem has imaginary coherence
        has_coherence = False
        for sub in range(4):
            rho = CoEmergenceModel.partial_trace(fps[0], (2, 2, 2, 2), (sub,))
            if abs(rho[0, 1].imag) > 1e-6:
                has_coherence = True
                break
        assert has_coherence, f"No coherence found for seed {seed}"


# ── Density matrix validity at N=16 ────────────────────────────────

class TestDensityMatrixN16:

    @pytest.mark.parametrize("keep", [(0,), (1,), (2,), (3,), (0, 1), (2, 3)])
    def test_valid_density_matrix(self, fp_n16_lor, keep):
        dims = (2, 2, 2, 2)
        rho = CoEmergenceModel.partial_trace(fp_n16_lor, dims, keep)
        # Hermitian
        assert np.linalg.norm(rho - rho.conj().T) < 1e-12
        # Trace 1
        assert abs(np.trace(rho) - 1.0) < 1e-12
        # PSD
        eigenvalues = np.linalg.eigvalsh(rho)
        assert np.all(eigenvalues > -1e-12)
