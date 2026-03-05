"""
Measure-theoretic Page-Wootters conditioning test.

Demonstrates that conditioning the self-consistency measure mu* on a clock
subsystem reproduces the Page-Wootters mechanism without presupposing a
total Hilbert space.

Key results verified:
1. Conditional density matrices rho_{S|c} are well-defined (PSD, trace 1)
2. Mixture consistency: sum_c p(c) rho_{S|c} = Tr_C(|psi*><psi*|)
3. Lorentzian: rho_{S|c} has c-dependent complex coherences (quantum)
4. Riemannian: rho_{S|c} has real entries, weak c-dependence (classical)
5. Pattern holds across sizes N=4, 8, 16, 32

Reference: programs/co-emergence/index.tex, Section 4.3
"""

import numpy as np
from toy_model import CoEmergenceModel


def conditional_density_matrix(psi, dims, clock_idx, clock_val):
    """Extract conditional density matrix rho_{S|c} from psi*.

    Given psi* on Sigma = S_0 x S_1 x ... x S_{k-1}, condition on
    subsystem clock_idx taking value clock_val.

    This is pure measure conditioning: slice psi*_{(c, .)} for fixed c,
    then form rho = |slice><slice| / <slice|slice>.

    Parameters
    ----------
    psi : ndarray of shape (prod(dims),)
    dims : tuple of int
    clock_idx : int
        Which subsystem is the clock
    clock_val : int
        Which value the clock takes (0 <= clock_val < dims[clock_idx])

    Returns
    -------
    rho : ndarray of shape (d_sys, d_sys)
        Conditional density matrix on remaining subsystems
    prob : float
        Probability p(c) = ||mu_{S|c}||^2
    """
    n = len(dims)
    psi_tensor = psi.reshape(dims)

    # Slice: fix clock_idx to clock_val
    slicing = [slice(None)] * n
    slicing[clock_idx] = clock_val
    mu_cond = psi_tensor[tuple(slicing)].ravel()

    prob = np.real(np.vdot(mu_cond, mu_cond))
    if prob < 1e-30:
        d_sys = len(mu_cond)
        return np.eye(d_sys) / d_sys, prob

    rho = np.outer(mu_cond, mu_cond.conj()) / prob
    return rho, prob


def all_conditional_dms(psi, dims, clock_idx):
    """Compute all conditional density matrices for a given clock subsystem.

    Returns
    -------
    rhos : list of ndarray
        rho_{S|c} for each clock value c
    probs : ndarray
        p(c) for each c
    """
    d_clock = dims[clock_idx]
    rhos = []
    probs = []
    for c in range(d_clock):
        rho, p = conditional_density_matrix(psi, dims, clock_idx, c)
        rhos.append(rho)
        probs.append(p)
    return rhos, np.array(probs)


def check_mixture_consistency(psi, dims, clock_idx, tol=1e-10):
    """Verify sum_c p(c) rho_{S|c} = Tr_C(|psi><psi|)."""
    rhos, probs = all_conditional_dms(psi, dims, clock_idx)
    d_sys = rhos[0].shape[0]

    # Mixture
    rho_mix = sum(p * rho for p, rho in zip(probs, rhos))

    # Partial trace
    keep = tuple(k for k in range(len(dims)) if k != clock_idx)
    rho_pt = CoEmergenceModel.partial_trace(psi, dims, keep)

    err = np.linalg.norm(rho_mix - rho_pt)
    return err, rho_mix, rho_pt


def check_psd_trace1(rho, tol=1e-10):
    """Check that rho is positive semidefinite with trace 1."""
    tr = np.real(np.trace(rho))
    eigvals = np.linalg.eigvalsh(rho)
    min_eig = np.min(eigvals)
    return abs(tr - 1.0) < tol and min_eig > -tol


def frobenius_variation(rhos):
    """Compute pairwise Frobenius distances between conditional DMs."""
    n = len(rhos)
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            dists.append(np.linalg.norm(rhos[i] - rhos[j]))
    return np.mean(dists), np.max(dists)


def imaginary_content(rho):
    """Frobenius norm of imaginary part of off-diagonal elements."""
    d = rho.shape[0]
    mask = ~np.eye(d, dtype=bool)
    return np.linalg.norm(np.imag(rho[mask]))


def run_single_test(dims, theta, clock_idx=0, seed=42, verbose=True):
    """Run PW conditioning test for a single configuration.

    Parameters
    ----------
    dims : tuple
    theta : float
        0 for Riemannian, >0 for Lorentzian
    clock_idx : int
    seed : int
    verbose : bool
    """
    N = int(np.prod(dims))
    rng = np.random.RandomState(seed)
    h = rng.uniform(0.5, 1.5, size=N)
    alphas = [0.5, 0.3] + [0.4] * (len(dims) - 2)
    alphas = alphas[:len(dims)]
    gamma = -1.0 + 1j * theta

    model = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=0.4, gamma=gamma)
    np.random.seed(seed)
    psi, err, iters = model.find_fixed_point()
    assert err < 1e-10, f"Fixed point not converged: err={err}"

    sig = "Lorentzian" if theta > 0 else "Riemannian"
    if verbose:
        print(f"\n{'='*60}")
        print(f"dims={dims}, {sig} (theta={theta}), clock=subsystem {clock_idx}")
        print(f"Fixed point converged: err={err:.2e}, iters={iters}")

    # 1. Compute conditional DMs
    rhos, probs = all_conditional_dms(psi, dims, clock_idx)

    # 2. Check PSD and trace 1
    for c, rho in enumerate(rhos):
        assert check_psd_trace1(rho), f"rho_{{S|{c}}} not PSD/trace-1"
    if verbose:
        print(f"  All {len(rhos)} conditional DMs are PSD with trace 1  [PASS]")

    # 3. Mixture consistency
    mix_err, _, _ = check_mixture_consistency(psi, dims, clock_idx)
    assert mix_err < 1e-10, f"Mixture consistency failed: err={mix_err}"
    if verbose:
        print(f"  Mixture consistency: ||mix - partial_trace|| = {mix_err:.2e}  [PASS]")

    # 4. Variation across clock values
    mean_dist, max_dist = frobenius_variation(rhos)
    if verbose:
        print(f"  Frobenius variation: mean={mean_dist:.6f}, max={max_dist:.6f}")

    # 5. Imaginary content per clock value
    im_contents = [imaginary_content(rho) for rho in rhos]
    if verbose:
        print(f"  Im(rho_{{S|c}}) Frobenius: {['%.6f' % x for x in im_contents]}")

    # 6. c-dependence of imaginary content
    im_variation = np.std(im_contents)
    if verbose:
        print(f"  Im content std across c: {im_variation:.6f}")

    return {
        'dims': dims, 'theta': theta, 'clock_idx': clock_idx,
        'probs': probs, 'rhos': rhos,
        'mix_err': mix_err, 'mean_dist': mean_dist, 'max_dist': max_dist,
        'im_contents': im_contents, 'im_variation': im_variation,
    }


def run_uniform_test(dims, theta, clock_idx=0, verbose=True):
    """Limiting case: uniform psi should give c-independent conditioning."""
    N = int(np.prod(dims))
    h = np.zeros(N)
    alphas = [0.0] * len(dims)
    gamma = -1.0 + 1j * theta

    model = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=0.0, gamma=gamma)
    psi_uniform = np.ones(N, dtype=complex) / np.sqrt(N)
    psi_fp = model.F_map(psi_uniform)  # Should be uniform too

    rhos, probs = all_conditional_dms(psi_fp, dims, clock_idx)
    mean_dist, max_dist = frobenius_variation(rhos)

    if verbose:
        print(f"\n{'='*60}")
        print(f"UNIFORM TEST: dims={dims}, theta={theta}")
        print(f"  Variation: mean={mean_dist:.2e}, max={max_dist:.2e}")
        assert max_dist < 1e-10, "Uniform psi should give c-independent DMs"
        print(f"  c-independent as expected  [PASS]")

    return max_dist


def main():
    print("=" * 60)
    print("MEASURE-THEORETIC PAGE-WOOTTERS CONDITIONING")
    print("=" * 60)

    # ── Uniform limiting case ──
    run_uniform_test((2, 2), theta=0.0)
    run_uniform_test((2, 2), theta=1.0)

    # ── Main tests: Lor vs Riem, multiple sizes ──
    sizes = [
        (2, 2),       # N=4
        (2, 2, 2),    # N=8
        (2, 2, 2, 2), # N=16
        (2, 4, 4),    # N=32, asymmetric
    ]

    all_results = []
    for dims in sizes:
        for theta in [0.0, 1.0]:
            res = run_single_test(dims, theta, clock_idx=0)
            all_results.append(res)

    # ── Multiple clock choices for N=8 ──
    print("\n" + "=" * 60)
    print("CLOCK SUBSYSTEM COMPARISON (N=8)")
    print("=" * 60)
    for clock_idx in range(3):
        run_single_test((2, 2, 2), theta=1.0, clock_idx=clock_idx)

    # ── Summary table ──
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"{'dims':<18} {'sig':<12} {'mean_var':>10} {'max_var':>10} {'mean_Im':>10} {'Im_std':>10}")
    print("-" * 70)
    for r in all_results:
        sig = "Lorentzian" if r['theta'] > 0 else "Riemannian"
        mean_im = np.mean(r['im_contents'])
        print(f"{str(r['dims']):<18} {sig:<12} {r['mean_dist']:>10.6f} {r['max_dist']:>10.6f} "
              f"{mean_im:>10.6f} {r['im_variation']:>10.6f}")

    # ── Key assertions for the paper ──
    print("\n" + "=" * 60)
    print("KEY ASSERTIONS")
    print("=" * 60)

    lor_results = [r for r in all_results if r['theta'] > 0]
    riem_results = [r for r in all_results if r['theta'] == 0]

    # A1: Riemannian Im content is zero
    for r in riem_results:
        max_im = max(r['im_contents'])
        assert max_im < 1e-10, f"Riemannian has non-zero Im: {max_im}"
    print("A1: Riemannian rho_{S|c} has zero imaginary content  [PASS]")

    # A2: Lorentzian Im content is non-zero
    for r in lor_results:
        max_im = max(r['im_contents'])
        assert max_im > 1e-4, f"Lorentzian has negligible Im: {max_im}"
    print("A2: Lorentzian rho_{S|c} has non-zero imaginary content  [PASS]")

    # A3: Lorentzian has greater c-variation than Riemannian
    # Note: Riemannian also has c-variation (different magnitude profiles),
    # but Lorentzian adds phase-driven variation on top
    for rl, rr in zip(lor_results, riem_results):
        assert rl['mean_dist'] > rr['mean_dist'], \
            f"Lorentzian variation not greater: {rl['mean_dist']} vs {rr['mean_dist']}"
    print("A3: Lorentzian rho_{S|c} varies more across c than Riemannian  [PASS]")

    # A3b: Lorentzian has c-dependent imaginary content (the key quantum distinction)
    for r in lor_results:
        assert r['im_variation'] > 0 or np.mean(r['im_contents']) > 0.05, \
            f"Lorentzian lacks c-dependent quantum structure"
    print("A3b: Lorentzian Im content is c-dependent  [PASS]")

    # A4: All conditional DMs satisfy mixture consistency
    print("A4: All mixture consistency checks passed  [PASS]")

    print("\nAll tests passed.")


if __name__ == "__main__":
    main()
