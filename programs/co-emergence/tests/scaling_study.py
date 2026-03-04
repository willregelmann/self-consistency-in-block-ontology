#!/usr/bin/env python3
"""
Scaling study: does coherence survive as N → ∞?

Measures coherence magnitude |Im(ρ[0,1])| and interference visibility
as functions of N = 2^k for k = 2, 3, ..., 7 (N = 4 to 128).

Each N uses dims = (2, 2, ..., 2) with k factors.
External field h drawn from Uniform[0.5, 1.5] with multiple seeds.
All subsystem couplings α_j drawn uniformly from [0.3, 0.5].

The critical question: does coherence vanish, saturate, or grow with N?
"""

import numpy as np
import time
import sys

sys.path.insert(0, ".")
from toy_model import CoEmergenceModel


def interference_visibility(rho, n_bases=20, rng=None):
    """Measure maximum interference visibility for a 2x2 density matrix.

    visibility = max over bases of (p_incoherent(k) - p_quantum(k))
    Positive visibility means destructive interference exists.

    Also computes the analytical visibility from the off-diagonal element.
    """
    if rng is None:
        rng = np.random.RandomState(0)

    c = rho[0, 1]
    # Analytical: max visibility = 2|c| achieved at optimal basis
    analytical_vis = 2 * abs(c)

    # Numerical check with random bases
    max_vis = 0.0
    for _ in range(n_bases):
        Z = rng.randn(2, 2) + 1j * rng.randn(2, 2)
        Q, _ = np.linalg.qr(Z)
        U = Q

        rho_rot = U @ rho @ U.conj().T
        p_quantum = np.diag(rho_rot).real

        rho_diag = np.diag(np.diag(rho))
        rho_diag_rot = U @ rho_diag @ U.conj().T
        p_incoherent = np.diag(rho_diag_rot).real

        vis = np.max(p_incoherent - p_quantum)
        max_vis = max(max_vis, vis)

    # Also try the analytically optimal basis
    if abs(c) > 1e-15:
        phi = np.angle(c)
        alpha = np.pi / 4
        phase = phi + np.pi
        U_opt = np.array([
            [np.cos(alpha), -np.sin(alpha) * np.exp(-1j * phase)],
            [np.sin(alpha) * np.exp(1j * phase), np.cos(alpha)],
        ])
        rho_rot = U_opt @ rho @ U_opt.conj().T
        p_q = np.diag(rho_rot).real
        rho_diag_rot = U_opt @ np.diag(np.diag(rho)) @ U_opt.conj().T
        p_inc = np.diag(rho_diag_rot).real
        vis_opt = np.max(p_inc - p_q)
        max_vis = max(max_vis, vis_opt)

    return max_vis, analytical_vis


def run_single(k, seed, verbose=False):
    """Run model for N = 2^k with given seed. Returns dict of metrics."""
    N = 2 ** k
    dims = tuple([2] * k)

    rng = np.random.RandomState(seed)
    h = rng.uniform(0.5, 1.5, size=N)
    alphas = rng.uniform(0.3, 0.5, size=k).tolist()
    beta = 0.4

    # Lorentzian
    model_lor = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                                  gamma=-1.0 + 1j)
    # Riemannian
    model_riem = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                                   gamma=-1.0 + 0j)

    np.random.seed(seed * 1000 + k)
    t0 = time.time()
    fps_lor = model_lor.find_fixed_points(n_starts=max(15, 30 - 2 * k))
    t_lor = time.time() - t0

    t0 = time.time()
    fps_riem = model_riem.find_fixed_points(n_starts=max(15, 30 - 2 * k))
    t_riem = time.time() - t0

    if not fps_lor or not fps_riem:
        return None

    fp_lor = fps_lor[0]
    fp_riem = fps_riem[0]

    # Measure coherence and interference for EVERY single-subsystem partial trace
    # Report max and mean across subsystems
    lor_im_vals = []
    lor_vis_vals = []
    riem_im_vals = []

    vis_rng = np.random.RandomState(seed + 5000)
    for sub in range(k):
        rho_lor = CoEmergenceModel.partial_trace(fp_lor, dims, (sub,))
        rho_riem = CoEmergenceModel.partial_trace(fp_riem, dims, (sub,))

        lor_im_vals.append(abs(rho_lor[0, 1].imag))
        riem_im_vals.append(abs(rho_riem[0, 1].imag))

        vis_num, vis_ana = interference_visibility(rho_lor, n_bases=30, rng=vis_rng)
        lor_vis_vals.append(vis_num)

    # Also measure purity of the first subsystem
    rho_lor_0 = CoEmergenceModel.partial_trace(fp_lor, dims, (0,))
    purity_lor = np.trace(rho_lor_0 @ rho_lor_0).real

    result = {
        "k": k,
        "N": N,
        "seed": seed,
        "n_fps_lor": len(fps_lor),
        "n_fps_riem": len(fps_riem),
        "coherence_max": max(lor_im_vals),
        "coherence_mean": np.mean(lor_im_vals),
        "coherence_min": min(lor_im_vals),
        "coherence_riem_max": max(riem_im_vals),
        "visibility_max": max(lor_vis_vals),
        "visibility_mean": np.mean(lor_vis_vals),
        "purity_sub0": purity_lor,
        "time_lor": t_lor,
        "time_riem": t_riem,
    }

    if verbose:
        print(f"  N={N:>4d} (k={k}) seed={seed}: "
              f"|Im(ρ)|_max={result['coherence_max']:.6e}  "
              f"|Im(ρ)|_mean={result['coherence_mean']:.6e}  "
              f"vis_max={result['visibility_max']:.6e}  "
              f"purity={purity_lor:.4f}  "
              f"t={t_lor:.1f}s")

    return result


def main():
    print("=" * 80)
    print("SCALING STUDY: COHERENCE AND INTERFERENCE vs N")
    print("=" * 80)

    seeds = [42, 123, 456, 789, 1011]
    ks = [2, 3, 4, 5, 6, 7]  # N = 4, 8, 16, 32, 64, 128

    all_results = []

    for k in ks:
        N = 2 ** k
        print(f"\n--- N = {N} (k = {k}, {k} subsystems of dim 2) ---")
        for seed in seeds:
            r = run_single(k, seed, verbose=True)
            if r is not None:
                all_results.append(r)
            else:
                print(f"  N={N} seed={seed}: FAILED (no fixed point)")

    # Aggregate by N
    print("\n\n" + "=" * 80)
    print("AGGREGATE RESULTS (mean ± std across seeds)")
    print("=" * 80)
    print(f"{'N':>6s}  {'|Im(ρ)|_max':>14s}  {'|Im(ρ)|_mean':>14s}  "
          f"{'vis_max':>14s}  {'purity':>8s}  {'time(s)':>8s}")
    print("-" * 80)

    for k in ks:
        N = 2 ** k
        rs = [r for r in all_results if r["k"] == k]
        if not rs:
            print(f"{N:>6d}  {'FAILED':>14s}")
            continue

        coh_maxs = [r["coherence_max"] for r in rs]
        coh_means = [r["coherence_mean"] for r in rs]
        vis_maxs = [r["visibility_max"] for r in rs]
        purities = [r["purity_sub0"] for r in rs]
        times = [r["time_lor"] for r in rs]

        print(f"{N:>6d}  "
              f"{np.mean(coh_maxs):>7.6f}±{np.std(coh_maxs):.0e}  "
              f"{np.mean(coh_means):>7.6f}±{np.std(coh_means):.0e}  "
              f"{np.mean(vis_maxs):>7.6f}±{np.std(vis_maxs):.0e}  "
              f"{np.mean(purities):>8.4f}  "
              f"{np.mean(times):>8.1f}")

    # Check scaling: fit log(coherence) vs log(N)
    print("\n\n" + "=" * 80)
    print("SCALING ANALYSIS")
    print("=" * 80)

    for metric_name, metric_key in [
        ("max coherence |Im(ρ)|", "coherence_max"),
        ("mean coherence |Im(ρ)|", "coherence_mean"),
        ("max interference visibility", "visibility_max"),
    ]:
        log_ns = []
        log_vals = []
        for k in ks:
            rs = [r for r in all_results if r["k"] == k]
            if rs:
                val = np.mean([r[metric_key] for r in rs])
                if val > 1e-15:
                    log_ns.append(np.log(2 ** k))
                    log_vals.append(np.log(val))

        if len(log_ns) >= 3:
            coeffs = np.polyfit(log_ns, log_vals, 1)
            alpha = coeffs[0]
            print(f"\n{metric_name}:")
            print(f"  Power law fit: metric ~ N^({alpha:.4f})")
            if alpha > -0.05:
                print(f"  --> SATURATES or GROWS (exponent ≈ {alpha:.3f})")
            elif alpha > -0.5:
                print(f"  --> SLOW DECAY (exponent ≈ {alpha:.3f})")
            else:
                print(f"  --> DECAYS (exponent ≈ {alpha:.3f}) — mechanism may not survive continuum limit")

            # Also report the actual values
            print(f"  Values by N:")
            for k in ks:
                rs = [r for r in all_results if r["k"] == k]
                if rs:
                    vals = [r[metric_key] for r in rs]
                    print(f"    N={2**k:>4d}: {np.mean(vals):.6e} ± {np.std(vals):.2e}")

    # Purity scaling
    print(f"\nSubsystem purity (entanglement indicator):")
    for k in ks:
        rs = [r for r in all_results if r["k"] == k]
        if rs:
            vals = [r["purity_sub0"] for r in rs]
            print(f"  N={2**k:>4d}: {np.mean(vals):.4f} ± {np.std(vals):.4f}")

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    # Determine verdict from the max coherence scaling
    rs_4 = [r for r in all_results if r["k"] == 2]
    rs_last = [r for r in all_results if r["k"] == ks[-1]]
    if rs_4 and rs_last:
        coh_4 = np.mean([r["coherence_max"] for r in rs_4])
        coh_last = np.mean([r["coherence_max"] for r in rs_last])
        ratio = coh_last / coh_4

        vis_4 = np.mean([r["visibility_max"] for r in rs_4])
        vis_last = np.mean([r["visibility_max"] for r in rs_last])
        vis_ratio = vis_last / vis_4

        print(f"\nCoherence ratio N={2**ks[-1]}/N=4: {ratio:.4f}")
        print(f"Visibility ratio N={2**ks[-1]}/N=4: {vis_ratio:.4f}")

        if ratio > 0.5:
            print("\nPOSITIVE: Coherence does not vanish with N.")
            print("The mechanism survives scaling toward the continuum limit.")
        elif ratio > 0.1:
            print("\nWEAK POSITIVE: Coherence decays slowly.")
            print("May survive continuum limit depending on rate.")
        else:
            print("\nNEGATIVE: Coherence decays rapidly with N.")
            print("The mechanism is likely a finite-size artifact.")

    print("=" * 80)


if __name__ == "__main__":
    main()
