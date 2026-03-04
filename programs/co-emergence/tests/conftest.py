"""Fixtures for co-emergence toy model tests."""

import numpy as np
import pytest

from .toy_model import CoEmergenceModel


# ── N=4 (2x2) — matches original paper parameters ──────────────────

@pytest.fixture(scope="session")
def model_n4_lor():
    h = np.array([1.0, 0.7, 0.5, 1.2])
    return CoEmergenceModel(
        dims=(2, 2), h=h, alphas=[0.5, 0.3], beta=0.4, gamma=-1.0 + 1j
    )


@pytest.fixture(scope="session")
def model_n4_riem():
    h = np.array([1.0, 0.7, 0.5, 1.2])
    return CoEmergenceModel(
        dims=(2, 2), h=h, alphas=[0.5, 0.3], beta=0.4, gamma=-1.0 + 0j
    )


@pytest.fixture(scope="session")
def fp_n4_lor(model_n4_lor):
    np.random.seed(42)
    fps = model_n4_lor.find_fixed_points(n_starts=20)
    assert len(fps) > 0, "No N=4 Lorentzian fixed point found"
    return fps[0]


@pytest.fixture(scope="session")
def fp_n4_riem(model_n4_riem):
    np.random.seed(42)
    fps = model_n4_riem.find_fixed_points(n_starts=20)
    assert len(fps) > 0, "No N=4 Riemannian fixed point found"
    return fps[0]


# ── N=8 (2x2x2) — seeded random h ──────────────────────────────────

def _make_n8_h(seed=123):
    rng = np.random.RandomState(seed)
    return rng.uniform(0.5, 1.5, size=8)


@pytest.fixture(scope="session")
def model_n8_lor():
    return CoEmergenceModel(
        dims=(2, 2, 2), h=_make_n8_h(), alphas=[0.5, 0.3, 0.4],
        beta=0.4, gamma=-1.0 + 1j,
    )


@pytest.fixture(scope="session")
def model_n8_riem():
    return CoEmergenceModel(
        dims=(2, 2, 2), h=_make_n8_h(), alphas=[0.5, 0.3, 0.4],
        beta=0.4, gamma=-1.0 + 0j,
    )


@pytest.fixture(scope="session")
def fp_n8_lor(model_n8_lor):
    np.random.seed(42)
    fps = model_n8_lor.find_fixed_points(n_starts=20)
    assert len(fps) > 0, "No N=8 Lorentzian fixed point found"
    return fps[0]


@pytest.fixture(scope="session")
def fp_n8_riem(model_n8_riem):
    np.random.seed(42)
    fps = model_n8_riem.find_fixed_points(n_starts=20)
    assert len(fps) > 0, "No N=8 Riemannian fixed point found"
    return fps[0]


# ── N=16 (2x2x2x2) — seeded random h ───────────────────────────────

def _make_n16_h(seed=456):
    rng = np.random.RandomState(seed)
    return rng.uniform(0.5, 1.5, size=16)


@pytest.fixture(scope="session")
def model_n16_lor():
    return CoEmergenceModel(
        dims=(2, 2, 2, 2), h=_make_n16_h(), alphas=[0.5, 0.3, 0.4, 0.35],
        beta=0.4, gamma=-1.0 + 1j,
    )


@pytest.fixture(scope="session")
def model_n16_riem():
    return CoEmergenceModel(
        dims=(2, 2, 2, 2), h=_make_n16_h(), alphas=[0.5, 0.3, 0.4, 0.35],
        beta=0.4, gamma=-1.0 + 0j,
    )


@pytest.fixture(scope="session")
def fp_n16_lor(model_n16_lor):
    np.random.seed(42)
    fps = model_n16_lor.find_fixed_points(n_starts=20)
    assert len(fps) > 0, "No N=16 Lorentzian fixed point found"
    return fps[0]


@pytest.fixture(scope="session")
def fp_n16_riem(model_n16_riem):
    np.random.seed(42)
    fps = model_n16_riem.find_fixed_points(n_starts=20)
    assert len(fps) > 0, "No N=16 Riemannian fixed point found"
    return fps[0]
