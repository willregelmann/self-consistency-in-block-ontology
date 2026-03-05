#!/usr/bin/env python3
"""
Numerical exploration for general-rank entropy excess lemma (#31).

Tests two candidate proof strategies:
1. Squared singular-value majorization: σ₁²+...+σⱼ² ≤ σ₁(0)²+...+σⱼ(0)²
   for all j (combined with equal total = full majorization → Schur concavity
   → S(θ) ≥ S(0))
2. Convexity of S(θ): d²S/dθ² ≥ 0 everywhere, combined with dS/dθ|₀ = 0

Also tests adversarial edge cases: near-rank-1, degenerate SVs, extreme
aspect ratios, extreme θ.
"""

import numpy as np
from collections import defaultdict
import time
import sys


def make_M_theta(M, theta):
    """Apply the phase map M → M(θ) entrywise.

    M(θ)_{ij} = m_{ij}^{1+iθ} / ||m^{1+iθ}||_F
    = m_{ij} · exp(iθ log m_{ij}) / ||...||_F

    M must have strictly positive entries.
    """
    log_M = np.log(M)
    M_theta = M * np.exp(1j * theta * log_M)
    M_theta /= np.linalg.norm(M_theta, 'fro')
    return M_theta


def squared_sv(M):
    """Squared singular values, sorted descending."""
    s = np.linalg.svd(M, compute_uv=False)
    return np.sort(s**2)[::-1]


def entropy_from_sv2(sv2):
    """Von Neumann entropy from squared singular values."""
    sv2 = sv2[sv2 > 1e-30]
    return -np.sum(sv2 * np.log(sv2))


def check_majorization(sv2_0, sv2_theta):
    """Check if sv2_0 majorizes sv2_theta.

    Majorization: for all j, sum of top-j of sv2_0 ≥ sum of top-j of sv2_theta,
    with equality at j=r (full sum).

    Returns (holds: bool, min_margin: float, worst_j: int).
    """
    r = len(sv2_0)
    min_margin = float('inf')
    worst_j = -1
    for j in range(1, r):  # skip j=r where they're equal
        partial_0 = np.sum(sv2_0[:j])
        partial_theta = np.sum(sv2_theta[:j])
        margin = partial_0 - partial_theta
        if margin < min_margin:
            min_margin = margin
            worst_j = j
    return min_margin >= -1e-12, min_margin, worst_j


def compute_S_theta(M, theta):
    """Compute S(θ) for given M and θ."""
    Mt = make_M_theta(M, theta)
    sv2 = squared_sv(Mt)
    return entropy_from_sv2(sv2)


def check_convexity(M, n_points=200, theta_max=10.0):
    """Check d²S/dθ² ≥ 0 via finite differences.

    Returns (convex: bool, min_d2S: float, worst_theta: float).
    """
    thetas = np.linspace(0, theta_max, n_points)
    S_vals = np.array([compute_S_theta(M, t) for t in thetas])

    dt = thetas[1] - thetas[0]
    d2S = np.diff(S_vals, 2) / dt**2

    min_d2S = np.min(d2S)
    worst_idx = np.argmin(d2S)
    worst_theta = thetas[worst_idx + 1]  # center point of stencil

    return min_d2S >= -1e-8, min_d2S, worst_theta


def random_positive_matrix(d_sub, d_env, rng, mode='lognormal'):
    """Generate random positive matrix, Frobenius-normalized."""
    if mode == 'lognormal':
        M = np.exp(rng.randn(d_sub, d_env))
    elif mode == 'uniform':
        M = rng.uniform(0.01, 2.0, size=(d_sub, d_env))
    elif mode == 'near_rank1':
        # Dominant rank-1 + small perturbation
        u = rng.uniform(0.1, 1.0, size=d_sub)
        v = rng.uniform(0.1, 1.0, size=d_env)
        M = np.outer(u, v) + 0.01 * rng.uniform(0.01, 1.0, size=(d_sub, d_env))
    elif mode == 'degenerate':
        # Near-degenerate singular values
        M = np.ones((d_sub, d_env)) + 0.01 * rng.uniform(0.0, 1.0, size=(d_sub, d_env))
    elif mode == 'extreme_spread':
        # Extreme spread in entries
        M = np.exp(5.0 * rng.randn(d_sub, d_env))
    else:
        raise ValueError(f"Unknown mode: {mode}")

    M /= np.linalg.norm(M, 'fro')
    return M


def run_majorization_tests(n_samples=20000, seed=42):
    """Test squared-SV majorization across many random matrices."""
    print("=" * 80)
    print("TEST 1: SQUARED SINGULAR-VALUE MAJORIZATION")
    print("=" * 80)

    rng = np.random.RandomState(seed)
    dims_list = [
        (3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (4, 6),
        (5, 5), (5, 6), (5, 8), (6, 6), (6, 8), (8, 8),
        (8, 10), (10, 10), (10, 16), (16, 16),
    ]
    thetas = [0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0]
    modes = ['lognormal', 'uniform', 'near_rank1', 'degenerate', 'extreme_spread']

    n_tests = 0
    n_violations = 0
    min_margin_global = float('inf')
    worst_case = None

    # Stats by rank
    stats_by_rank = defaultdict(lambda: {'n': 0, 'min_margin': float('inf')})

    samples_per_config = max(1, n_samples // (len(dims_list) * len(modes)))

    t0 = time.time()

    for d_sub, d_env in dims_list:
        rank = min(d_sub, d_env)
        for mode in modes:
            for _ in range(samples_per_config):
                M = random_positive_matrix(d_sub, d_env, rng, mode)
                sv2_0 = squared_sv(M)

                for theta in thetas:
                    Mt = make_M_theta(M, theta)
                    sv2_t = squared_sv(Mt)

                    holds, margin, worst_j = check_majorization(sv2_0, sv2_t)
                    n_tests += 1

                    rb = stats_by_rank[rank]
                    rb['n'] += 1
                    rb['min_margin'] = min(rb['min_margin'], margin)

                    if margin < min_margin_global:
                        min_margin_global = margin
                        worst_case = (d_sub, d_env, theta, mode, margin, worst_j)

                    if not holds:
                        n_violations += 1
                        print(f"  VIOLATION: dims=({d_sub},{d_env}) θ={theta} "
                              f"mode={mode} margin={margin:.2e} j={worst_j}")

    dt = time.time() - t0

    print(f"\nResults: {n_tests} tests, {n_violations} violations, {dt:.1f}s")
    print(f"Global min margin: {min_margin_global:.6e}")
    if worst_case:
        d_sub, d_env, theta, mode, margin, worst_j = worst_case
        print(f"  Closest approach: dims=({d_sub},{d_env}) θ={theta} "
              f"mode={mode} margin={margin:.6e} j={worst_j}")

    print("\nBy rank:")
    for rank in sorted(stats_by_rank.keys()):
        rb = stats_by_rank[rank]
        print(f"  rank {rank}: {rb['n']} tests, min_margin={rb['min_margin']:.6e}")

    return n_violations == 0


def run_convexity_tests(n_samples=500, seed=123):
    """Test convexity of S(θ)."""
    print("\n" + "=" * 80)
    print("TEST 2: CONVEXITY OF S(θ)")
    print("=" * 80)

    rng = np.random.RandomState(seed)
    dims_list = [(3, 3), (4, 4), (5, 5), (3, 5), (4, 6), (8, 8)]
    modes = ['lognormal', 'uniform', 'near_rank1', 'degenerate', 'extreme_spread']

    n_tests = 0
    n_violations = 0
    min_d2S_global = float('inf')
    worst_case = None

    samples_per_config = max(1, n_samples // (len(dims_list) * len(modes)))

    t0 = time.time()

    for d_sub, d_env in dims_list:
        for mode in modes:
            for _ in range(samples_per_config):
                M = random_positive_matrix(d_sub, d_env, rng, mode)
                convex, min_d2S, worst_theta = check_convexity(M)
                n_tests += 1

                if min_d2S < min_d2S_global:
                    min_d2S_global = min_d2S
                    worst_case = (d_sub, d_env, mode, min_d2S, worst_theta)

                if not convex:
                    n_violations += 1
                    print(f"  VIOLATION: dims=({d_sub},{d_env}) mode={mode} "
                          f"min_d2S={min_d2S:.2e} at θ={worst_theta:.2f}")

    dt = time.time() - t0

    print(f"\nResults: {n_tests} tests, {n_violations} violations, {dt:.1f}s")
    print(f"Global min d²S/dθ²: {min_d2S_global:.6e}")
    if worst_case:
        d_sub, d_env, mode, min_d2S, worst_theta = worst_case
        print(f"  Closest approach: dims=({d_sub},{d_env}) mode={mode} "
              f"d²S={min_d2S:.6e} at θ={worst_theta:.2f}")

    return n_violations == 0


def run_entropy_excess_tests(n_samples=20000, seed=42):
    """Direct test of S(θ) ≥ S(0) — the actual conjecture."""
    print("\n" + "=" * 80)
    print("TEST 3: DIRECT ENTROPY EXCESS S(θ) ≥ S(0)")
    print("=" * 80)

    rng = np.random.RandomState(seed)
    dims_list = [
        (2, 2), (2, 3), (3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (4, 6),
        (5, 5), (5, 6), (5, 8), (6, 6), (6, 8), (8, 8),
        (8, 10), (10, 10), (10, 16), (16, 16),
    ]
    thetas = [0.01, 0.1, 0.3, 0.5, 1.0, 2.0, 5.0, 10.0]
    modes = ['lognormal', 'uniform', 'near_rank1', 'degenerate', 'extreme_spread']

    n_tests = 0
    n_violations = 0
    min_excess_global = float('inf')
    worst_case = None
    stats_by_rank = defaultdict(lambda: {'n': 0, 'min_excess': float('inf')})

    samples_per_config = max(1, n_samples // (len(dims_list) * len(modes)))

    t0 = time.time()

    for d_sub, d_env in dims_list:
        rank = min(d_sub, d_env)
        for mode in modes:
            for _ in range(samples_per_config):
                M = random_positive_matrix(d_sub, d_env, rng, mode)
                S0 = entropy_from_sv2(squared_sv(M))

                for theta in thetas:
                    S_t = compute_S_theta(M, theta)
                    excess = S_t - S0
                    n_tests += 1

                    rb = stats_by_rank[rank]
                    rb['n'] += 1
                    rb['min_excess'] = min(rb['min_excess'], excess)

                    if excess < min_excess_global:
                        min_excess_global = excess
                        worst_case = (d_sub, d_env, theta, mode, excess)

                    if excess < -1e-12:
                        n_violations += 1
                        print(f"  VIOLATION: dims=({d_sub},{d_env}) θ={theta} "
                              f"mode={mode} excess={excess:.2e}")

    dt = time.time() - t0

    print(f"\nResults: {n_tests} tests, {n_violations} violations, {dt:.1f}s")
    print(f"Global min excess: {min_excess_global:.6e}")
    if worst_case:
        d_sub, d_env, theta, mode, excess = worst_case
        print(f"  Closest approach: dims=({d_sub},{d_env}) θ={theta} mode={mode}")

    print("\nBy rank:")
    for rank in sorted(stats_by_rank.keys()):
        rb = stats_by_rank[rank]
        print(f"  rank {rank}: {rb['n']} tests, min_excess={rb['min_excess']:.6e}")

    return n_violations == 0


def run_perturbative_analysis(seed=42):
    """Compute d²S/dθ²|₀ analytically and compare with finite differences.

    At θ=0, M(θ) = M · diag(e^{iθ log m_j}), so dM/dθ|₀ = i M ∘ log(M).
    The perturbation is purely imaginary (anti-Hermitian in phase space).

    For S = -Tr(ρ log ρ) with ρ = M†M / Tr(M†M):
    dS/dθ|₀ = 0 (by symmetry: phase perturbation is anti-Hermitian)
    d²S/dθ²|₀ should be ≥ 0.
    """
    print("\n" + "=" * 80)
    print("TEST 4: PERTURBATIVE ANALYSIS AT θ=0")
    print("=" * 80)

    rng = np.random.RandomState(seed)
    dims_list = [(3, 3), (4, 4), (5, 5), (3, 5), (4, 6), (8, 8), (10, 10)]

    for d_sub, d_env in dims_list:
        M = random_positive_matrix(d_sub, d_env, rng, 'lognormal')

        # Finite differences for dS/dθ and d²S/dθ² at θ=0
        eps = 1e-5
        S_0 = compute_S_theta(M, 0.0)
        S_p = compute_S_theta(M, eps)
        S_m = compute_S_theta(M, -eps)
        S_2p = compute_S_theta(M, 2 * eps)
        S_2m = compute_S_theta(M, -2 * eps)

        dS = (S_p - S_m) / (2 * eps)
        d2S = (S_p - 2 * S_0 + S_m) / eps**2
        # Higher-order check
        d2S_ho = (-S_2p + 16 * S_p - 30 * S_0 + 16 * S_m - S_2m) / (12 * eps**2)

        print(f"  dims=({d_sub},{d_env}): dS/dθ|₀ = {dS:.6e}  "
              f"d²S/dθ²|₀ = {d2S:.6e}  (HO: {d2S_ho:.6e})")

    # Also compute analytically for a specific case
    print("\n  Analytical derivation for d²S/dθ²|₀:")
    print("  At θ=0, the Gram matrix ρ = M†M is real symmetric.")
    print("  The perturbation dρ/dθ|₀ is purely imaginary (anti-Hermitian).")
    print("  By standard perturbation theory, dS/dθ|₀ = -Tr(dρ/dθ · (log ρ + I)) = 0")
    print("  since dρ/dθ is anti-Hermitian and (log ρ + I) is Hermitian → Tr = purely imaginary,")
    print("  but S is real → dS/dθ|₀ = 0. ✓")
    print("  d²S/dθ²|₀ ≥ 0 requires careful second-order perturbation theory.")


def run_ky_fan_analysis(seed=42):
    """Test Ky Fan inequality structure.

    The j-th Ky Fan norm is σ₁ + ... + σⱼ (singular values, not squared).
    We need partial sums of SQUARED singular values.

    The partial sum σ₁² + ... + σⱼ² = max over rank-j projections P of
    Tr(P M†M P) = max Tr(P ρ P) where ρ = M†M.

    For j=1: σ₁² = largest eigenvalue of ρ = M†M.
    The Perron-Frobenius argument works: ρ = M†M has non-negative entries
    when M has positive entries, so the top eigenvector is non-negative.
    Adding phases can only decrease Tr(v ρ(θ) v) for non-negative v.

    For j>1: need to show max_{rank-j P} Tr(P ρ(θ) P) ≤ max_{rank-j P} Tr(P ρ P).
    """
    print("\n" + "=" * 80)
    print("TEST 5: KY FAN / PARTIAL SUM STRUCTURE")
    print("=" * 80)

    rng = np.random.RandomState(seed)

    # Examine whether the optimal rank-j subspace for ρ(0) is spanned by
    # non-negative vectors (this would make the Perron argument extend)
    dims_list = [(3, 3), (4, 4), (5, 5), (3, 5), (6, 6)]

    for d_sub, d_env in dims_list:
        M = random_positive_matrix(d_sub, d_env, rng, 'lognormal')
        rho = M.T @ M  # d_env × d_env Gram matrix (real, non-negative entries)

        evals, evecs = np.linalg.eigh(rho)
        # Sort descending
        idx = np.argsort(evals)[::-1]
        evals = evals[idx]
        evecs = evecs[:, idx]

        r = min(d_sub, d_env)
        print(f"\n  dims=({d_sub},{d_env}), rank={r}")
        print(f"  Eigenvalues: {evals[:r]}")

        for j in range(1, r + 1):
            # Check: are the top-j eigenvectors non-negative?
            top_j = evecs[:, :j]
            min_entry = np.min(top_j)
            has_neg = min_entry < -1e-10
            print(f"    j={j}: min entry in top-{j} eigenvectors = {min_entry:.6e}"
                  f"  {'HAS NEGATIVES' if has_neg else 'all non-negative'}")

    print("\n  Key finding: Only the top eigenvector (j=1) is guaranteed non-negative")
    print("  by Perron-Frobenius. Higher eigenvectors MUST have sign changes")
    print("  (orthogonality to the Perron vector forces this).")
    print("  → Direct Ky Fan argument via non-negativity does NOT extend to j>1.")
    print("  → Need a different approach for the general case.")


def run_compound_matrix_test(seed=42):
    """Test compound matrix approach.

    The j-th antisymmetric power Λ^j(M) has entries that are j×j minors of M.
    σ₁²...σⱼ² of M = σ₁² of Λ^j(M).

    If M has positive entries, Λ^j(M) has entries that are determinants of
    j×j submatrices — these can be negative for j ≥ 2.

    But we need partial SUMS, not products. The relation is:
    σ₁² + ... + σⱼ² = ||Λ^j(M)||²_F / ||Λ^{j-1}(M)||²_F  ... no, that's wrong.

    Actually: σ₁² + ... + σⱼ² = max_{V: dim=j} ||MV||²_F / ||V||²_F
    This is the variational characterization.
    """
    print("\n" + "=" * 80)
    print("TEST 6: COMPOUND MATRIX / EXTERIOR POWER ANALYSIS")
    print("=" * 80)

    rng = np.random.RandomState(seed)

    # For a 3×3 case, explicitly compute Λ²(M)
    M = random_positive_matrix(3, 3, rng, 'lognormal')

    # Λ²(M) is 3×3: entries are 2×2 minors
    # Rows indexed by {1,2}, {1,3}, {2,3}; same for columns
    from itertools import combinations
    rows = list(combinations(range(3), 2))
    cols = list(combinations(range(3), 2))

    L2 = np.zeros((3, 3))
    for i, r in enumerate(rows):
        for j, c in enumerate(cols):
            L2[i, j] = np.linalg.det(M[np.ix_(list(r), list(c))])

    print(f"  M (3×3):\n{M}")
    print(f"  Λ²(M) (3×3):\n{L2}")
    print(f"  Λ²(M) has negative entries: {np.any(L2 < -1e-15)}")
    print(f"  σ₁(M)² · σ₂(M)² = {np.prod(np.linalg.svd(M, compute_uv=False)[:2]**2):.6f}")
    print(f"  σ₁(Λ²(M))² = {np.linalg.svd(L2, compute_uv=False)[0]**2:.6f}")

    # Test with θ
    for theta in [0.5, 1.0, 2.0]:
        Mt = make_M_theta(M, theta)
        L2t = np.zeros((3, 3), dtype=complex)
        for i, r in enumerate(rows):
            for j, c in enumerate(cols):
                L2t[i, j] = np.linalg.det(Mt[np.ix_(list(r), list(c))])

        sv_M = np.linalg.svd(M, compute_uv=False)
        sv_Mt = np.linalg.svd(Mt, compute_uv=False)

        print(f"\n  θ={theta}:")
        print(f"    σ₁²+σ₂²(0) = {np.sum(sv_M[:2]**2):.6f}  "
              f"σ₁²+σ₂²(θ) = {np.sum(np.abs(sv_Mt[:2])**2):.6f}  "
              f"diff = {np.sum(sv_M[:2]**2) - np.sum(np.abs(sv_Mt[:2])**2):.6e}")

    print("\n  Compound matrix entries can be negative → Perron-Frobenius")
    print("  does not directly apply to Λ^j(M).")


def run_interlacing_test(seed=42):
    """Test whether eigenvalue interlacing provides the needed bound.

    ρ(θ) = M(θ)†M(θ) where M(θ) = M ∘ E(θ) with E(θ)_{ij} = e^{iθ log m_{ij}}.

    ρ(θ) = (M ∘ Ē(θ))ᵀ (M ∘ E(θ)) = Mᵀ D̄(θ) D(θ) M ... no, Hadamard products
    don't factor this way.

    Key identity: ρ(θ)_{jk} = Σᵢ m_{ij} m_{ik} exp(iθ(log m_{ik} - log m_{ij}))
                             = Σᵢ m_{ij} m_{ik} exp(iθ log(m_{ik}/m_{ij}))

    At θ=0: ρ(0)_{jk} = Σᵢ m_{ij} m_{ik} (always ≥ 0 since m > 0)

    The diagonal is preserved: ρ(θ)_{jj} = Σᵢ m_{ij}² = ρ(0)_{jj}
    So Tr(ρ(θ)) = Tr(ρ(0)) — this is Fact 1.
    """
    print("\n" + "=" * 80)
    print("TEST 7: GRAM MATRIX STRUCTURE ANALYSIS")
    print("=" * 80)

    rng = np.random.RandomState(seed)

    for d_sub, d_env in [(3, 3), (4, 4), (5, 5)]:
        M = random_positive_matrix(d_sub, d_env, rng, 'lognormal')

        rho_0 = M.T @ M  # Real, non-negative entries
        print(f"\n  dims=({d_sub},{d_env})")
        print(f"  ρ(0) diagonal: {np.diag(rho_0)}")
        print(f"  ρ(0) all entries ≥ 0: {np.all(rho_0 >= -1e-15)}")

        for theta in [0.5, 1.0, 2.0]:
            Mt = make_M_theta(M, theta)
            rho_t = Mt.conj().T @ Mt

            # Diagonal preserved?
            diag_diff = np.max(np.abs(np.diag(rho_t).real - np.diag(rho_0)))
            print(f"  θ={theta}: diag preserved (max diff={diag_diff:.2e})")

            # Off-diagonal magnitudes decreased?
            od_0 = np.abs(rho_0.copy())
            np.fill_diagonal(od_0, 0)
            od_t = np.abs(rho_t.copy())
            np.fill_diagonal(od_t, 0)
            print(f"    ||off-diag||_F: ρ(0)={np.linalg.norm(od_0):.6f}  "
                  f"ρ(θ)={np.linalg.norm(od_t):.6f}  "
                  f"ratio={np.linalg.norm(od_t)/np.linalg.norm(od_0):.6f}")

            # Entrywise: |ρ(θ)_{jk}| ≤ ρ(0)_{jk} for each j,k?
            entrywise_holds = True
            max_violation = 0.0
            for j in range(d_env):
                for k in range(d_env):
                    if j != k:
                        diff = np.abs(rho_t[j, k]) - rho_0[j, k]
                        if diff > 1e-12:
                            entrywise_holds = False
                            max_violation = max(max_violation, diff)
            print(f"    |ρ(θ)_{{jk}}| ≤ ρ(0)_{{jk}} entrywise: "
                  f"{'YES' if entrywise_holds else f'NO (max viol={max_violation:.2e})'}")


def main():
    print("ENTROPY EXCESS GENERAL RANK — NUMERICAL EXPLORATION")
    print(f"{'='*80}\n")

    # Test 1: Majorization (the strong structural result)
    maj_ok = run_majorization_tests(n_samples=20000, seed=42)

    # Test 2: Convexity (the fallback proof strategy)
    conv_ok = run_convexity_tests(n_samples=500, seed=123)

    # Test 3: Direct entropy excess (the actual claim)
    excess_ok = run_entropy_excess_tests(n_samples=20000, seed=42)

    # Test 4: Perturbative analysis at θ=0
    run_perturbative_analysis(seed=42)

    # Test 5: Ky Fan / non-negativity analysis
    run_ky_fan_analysis(seed=42)

    # Test 6: Compound matrix approach
    run_compound_matrix_test(seed=42)

    # Test 7: Gram matrix structure
    run_interlacing_test(seed=42)

    # Final verdict
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    print(f"  Majorization holds:     {'YES' if maj_ok else 'NO'}")
    print(f"  Convexity holds:        {'YES' if conv_ok else 'NO'}")
    print(f"  Entropy excess holds:   {'YES' if excess_ok else 'NO'}")

    if maj_ok:
        print("\n  → MAJORIZATION is viable proof strategy")
        print("    (implies entropy excess via Schur concavity)")
    elif conv_ok:
        print("\n  → CONVEXITY is viable proof strategy")
        print("    (combined with dS/dθ|₀ = 0)")
    elif excess_ok:
        print("\n  → Entropy excess holds numerically but neither")
        print("    majorization nor convexity provides the route")
    else:
        print("\n  → COUNTEREXAMPLE FOUND — conjecture is FALSE")

    print("=" * 80)


if __name__ == "__main__":
    main()
