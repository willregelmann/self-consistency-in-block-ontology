#!/usr/bin/env python3
"""
Mixed-dimensions exploration: does the co-emergence mechanism survive
non-symmetric tensor product structures?

All prior tests used dims=(2,2,...,2). This tests asymmetric bipartitions
(2×3, 3×4, 2×5, 3×5, 4×5) and asymmetric multipartite structures
(2×2×3, 2×3×4, 2×2×5, 3×3×4).

Key questions:
1. Does the entropy excess lemma hold for rank > 2?  (2×3 has rank 2,
   3×4 has rank 3, etc.)
2. Is the ~25% imaginary fraction an artifact of symmetric dims?
3. Does composition Tr_{R2} ρ_R = ρ_{R1} hold for unequal subsystems?
4. Does destructive interference persist?
"""

import numpy as np
import sys
import time
from itertools import combinations

sys.path.insert(0, ".")
from toy_model import CoEmergenceModel


def entropy(rho):
    """Von Neumann entropy."""
    evals = np.linalg.eigvalsh(rho)
    evals = evals[evals > 1e-15]
    return -np.sum(evals * np.log(evals))


def im_frac(psi):
    """Imaginary fraction after global phase alignment."""
    # Align so that largest-magnitude component is real and positive
    idx = np.argmax(np.abs(psi))
    phase = np.exp(-1j * np.angle(psi[idx]))
    psi_aligned = psi * phase
    return np.linalg.norm(psi_aligned.imag) / np.linalg.norm(psi_aligned)


def im_re_ratio(rho):
    """Im/Re ratio of off-diagonal elements."""
    od = rho.copy()
    np.fill_diagonal(od, 0)
    im_norm = np.linalg.norm(od.imag)
    re_norm = np.linalg.norm(od.real)
    if re_norm < 1e-15:
        return 0.0
    return im_norm / re_norm


def born_rule_check(rho, n_bases=5, rng=None):
    """Check Born rule p_k = (U ρ U†)_kk in random bases.

    Returns max absolute error across all bases and outcomes.
    """
    if rng is None:
        rng = np.random.RandomState(42)
    d = rho.shape[0]
    max_err = 0.0
    for _ in range(n_bases):
        # Random unitary via QR of random complex matrix
        A = rng.randn(d, d) + 1j * rng.randn(d, d)
        U, _ = np.linalg.qr(A)
        rho_rot = U @ rho @ U.conj().T
        probs = np.real(np.diag(rho_rot))
        # Born rule: probs should be non-negative and sum to 1
        max_err = max(max_err, abs(np.sum(probs) - 1.0))
        max_err = max(max_err, max(0.0, -np.min(probs)))
    return max_err


def interference_check(rho, n_bases=10, rng=None):
    """Check for destructive interference: exists basis where
    p_quantum(k) < p_incoherent(k) for some k.

    p_incoherent = diag(ρ) in computational basis (no off-diagonal terms).
    """
    if rng is None:
        rng = np.random.RandomState(42)
    d = rho.shape[0]
    found = False
    max_deficit = 0.0
    for _ in range(n_bases):
        A = rng.randn(d, d) + 1j * rng.randn(d, d)
        U, _ = np.linalg.qr(A)
        rho_rot = U @ rho @ U.conj().T
        p_quantum = np.real(np.diag(rho_rot))
        # Incoherent: zero off-diagonal, keep diagonal
        rho_incoh = np.diag(np.diag(rho))
        rho_incoh_rot = U @ rho_incoh @ U.conj().T
        p_incoh = np.real(np.diag(rho_incoh_rot))
        deficit = p_incoh - p_quantum  # positive = destructive interference
        if np.max(deficit) > 1e-10:
            found = True
            max_deficit = max(max_deficit, np.max(deficit))
    return found, max_deficit


def run_bipartite(dims, seed, theta=1.0):
    """Run one bipartite configuration. Returns dict."""
    N = int(np.prod(dims))
    n_sub = len(dims)

    rng = np.random.RandomState(seed)
    h = rng.uniform(0.5, 1.5, size=N)
    alphas = [0.4] * n_sub
    beta = 0.4

    model_lor = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                                  gamma=-1.0 + 1j * theta)
    model_riem = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                                   gamma=-1.0 + 0j)

    np.random.seed(seed * 1000 + N)
    fps_lor = model_lor.find_fixed_points(n_starts=20)
    fps_riem = model_riem.find_fixed_points(n_starts=20)

    if not fps_lor or not fps_riem:
        return None

    fp_lor = fps_lor[0]
    fp_riem = fps_riem[0]

    result = {
        "dims": dims,
        "N": N,
        "seed": seed,
        "n_lor_fps": len(fps_lor),
        "n_riem_fps": len(fps_riem),
        "im_frac_lor": im_frac(fp_lor),
        "im_frac_riem": im_frac(fp_riem),
    }

    # For each bipartition into (keep, trace_out), compute entropy
    for keep_idx in range(n_sub):
        keep = (keep_idx,)
        rho_lor = CoEmergenceModel.partial_trace(fp_lor, dims, keep)
        rho_riem = CoEmergenceModel.partial_trace(fp_riem, dims, keep)

        S_lor = entropy(rho_lor)
        S_riem = entropy(rho_riem)

        result[f"S_lor_{keep_idx}"] = S_lor
        result[f"S_riem_{keep_idx}"] = S_riem
        result[f"S_ratio_{keep_idx}"] = S_lor / S_riem if S_riem > 1e-15 else float('inf')
        result[f"im_re_{keep_idx}"] = im_re_ratio(rho_lor)
        result[f"im_re_riem_{keep_idx}"] = im_re_ratio(rho_riem)

        # Born rule check
        rng_born = np.random.RandomState(seed + keep_idx)
        result[f"born_err_{keep_idx}"] = born_rule_check(rho_lor, n_bases=5, rng=rng_born)

        # Interference check
        rng_int = np.random.RandomState(seed + keep_idx + 100)
        has_interf, max_def = interference_check(rho_lor, n_bases=20, rng=rng_int)
        has_interf_r, _ = interference_check(rho_riem, n_bases=20,
                                              rng=np.random.RandomState(seed + keep_idx + 200))
        result[f"interference_{keep_idx}"] = has_interf
        result[f"interference_riem_{keep_idx}"] = has_interf_r
        result[f"max_deficit_{keep_idx}"] = max_def

    # Phase-stripping test
    fp_nophase = np.abs(fp_lor)
    fp_nophase /= np.linalg.norm(fp_nophase)
    for keep_idx in range(n_sub):
        keep = (keep_idx,)
        rho_nophase = CoEmergenceModel.partial_trace(fp_nophase, dims, keep)
        result[f"S_nophase_{keep_idx}"] = entropy(rho_nophase)

    return result


def run_composition_check(dims, seed, theta=1.0):
    """Check composition: Tr_{R2} ρ_{R1R2} = ρ_{R1} for multipartite systems.

    Returns list of (keep_pair, keep_single, error) tuples.
    """
    N = int(np.prod(dims))
    n_sub = len(dims)
    if n_sub < 3:
        return []

    rng = np.random.RandomState(seed)
    h = rng.uniform(0.5, 1.5, size=N)
    alphas = [0.4] * n_sub
    beta = 0.4

    model = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                              gamma=-1.0 + 1j * theta)

    np.random.seed(seed * 1000 + N)
    fps = model.find_fixed_points(n_starts=20)
    if not fps:
        return []

    fp = fps[0]
    results = []

    # For each pair of subsystems
    for pair in combinations(range(n_sub), 2):
        rho_pair = CoEmergenceModel.partial_trace(fp, dims, pair)
        # Dims of the pair
        pair_dims = tuple(dims[k] for k in pair)
        for i, single in enumerate(pair):
            # Trace out the other member of the pair
            keep_in_pair = (i,)
            rho_from_pair = CoEmergenceModel.partial_trace_dm(rho_pair, pair_dims, keep_in_pair)
            # Direct single-subsystem trace
            rho_direct = CoEmergenceModel.partial_trace(fp, dims, (single,))
            err = np.linalg.norm(rho_from_pair - rho_direct)
            results.append((pair, single, err))

    return results


def main():
    seeds = [42, 123, 456, 789, 1011]

    # ================================================================
    # PART 1: Bipartite mixed dimensions
    # ================================================================
    print("=" * 80)
    print("PART 1: BIPARTITE MIXED DIMENSIONS")
    print("=" * 80)

    bipartite_configs = [
        (2, 2),   # baseline (symmetric, rank 2)
        (2, 3),   # asymmetric, rank 2
        (2, 5),   # asymmetric, rank 2
        (3, 3),   # symmetric, rank 3
        (3, 4),   # asymmetric, rank 3
        (3, 5),   # asymmetric, rank 3
        (4, 4),   # symmetric, rank 4
        (4, 5),   # asymmetric, rank 4
        (5, 5),   # symmetric, rank 5
        (4, 6),   # asymmetric, rank 4
        (5, 6),   # asymmetric, rank 5
        (6, 6),   # symmetric, rank 6
    ]

    all_bipartite = []

    for d1, d2 in bipartite_configs:
        dims = (d1, d2)
        rank = min(d1, d2)
        t0 = time.time()
        seed_results = []
        for seed in seeds:
            r = run_bipartite(dims, seed)
            if r is not None:
                seed_results.append(r)
                all_bipartite.append(r)

        dt = time.time() - t0
        if seed_results:
            im_fracs = [r["im_frac_lor"] for r in seed_results]
            im_fracs_r = [r["im_frac_riem"] for r in seed_results]
            # Use subsystem 0 for entropy ratio
            s_ratios = [r["S_ratio_0"] for r in seed_results]
            s_nophase = [r.get("S_nophase_0", 0) for r in seed_results]
            s_riem = [r["S_riem_0"] for r in seed_results]
            nophase_ratios = [sn / sr if sr > 1e-15 else 0
                              for sn, sr in zip(s_nophase, s_riem)]
            interf = [r.get("interference_0", False) for r in seed_results]
            interf_r = [r.get("interference_riem_0", False) for r in seed_results]
            born = [r.get("born_err_0", 0) for r in seed_results]

            print(f"\n  dims={dims}  rank={rank}  N={d1*d2}")
            print(f"    im_frac:  Lor={np.mean(im_fracs):.4f}±{np.std(im_fracs):.4f}"
                  f"  Riem={np.mean(im_fracs_r):.6f}")
            print(f"    S_lor/S_riem = {np.mean(s_ratios):.4f}±{np.std(s_ratios):.4f}")
            print(f"    S_nophase/S_riem = {np.mean(nophase_ratios):.6f}"
                  f"  (1.0 = phases explain all excess)")
            print(f"    interference: Lor={sum(interf)}/{len(interf)}"
                  f"  Riem={sum(interf_r)}/{len(interf_r)}")
            print(f"    Born rule err: {np.max(born):.2e}")
            print(f"    ({len(seed_results)}/5 seeds, {dt:.1f}s)")
        else:
            print(f"\n  dims={dims}  FAILED all seeds")

    # ================================================================
    # Summary table: entropy excess by rank
    # ================================================================
    print("\n\n" + "=" * 80)
    print("SUMMARY: ENTROPY EXCESS BY RANK (subsystem 0)")
    print("=" * 80)
    print(f"{'dims':>10s}  {'rank':>4s}  {'S_lor/S_riem':>14s}  {'S_noph/S_riem':>14s}"
          f"  {'im_frac':>10s}  {'interf_Lor':>10s}  {'interf_Riem':>10s}")
    print("-" * 85)

    for d1, d2 in bipartite_configs:
        dims = (d1, d2)
        rank = min(d1, d2)
        rs = [r for r in all_bipartite if r["dims"] == dims]
        if rs:
            sr = [r["S_ratio_0"] for r in rs]
            sn = [r.get("S_nophase_0", 0) / r["S_riem_0"]
                  if r["S_riem_0"] > 1e-15 else 0 for r in rs]
            imf = [r["im_frac_lor"] for r in rs]
            il = [r.get("interference_0", False) for r in rs]
            ir = [r.get("interference_riem_0", False) for r in rs]
            print(f"{str(dims):>10s}  {rank:>4d}  {np.mean(sr):>8.4f}±{np.std(sr):.4f}"
                  f"  {np.mean(sn):>8.6f}"
                  f"  {np.mean(imf):>8.4f}±{np.std(imf):.3f}"
                  f"  {sum(il):>5d}/{len(il):<4d}"
                  f"  {sum(ir):>5d}/{len(ir):<4d}")

    # ================================================================
    # PART 2: Multipartite mixed dimensions — composition check
    # ================================================================
    print("\n\n" + "=" * 80)
    print("PART 2: MULTIPARTITE MIXED DIMENSIONS — COMPOSITION CHECK")
    print("=" * 80)

    multipartite_configs = [
        (2, 2, 2),   # baseline
        (2, 2, 3),   # one asymmetric factor
        (2, 3, 4),   # all different
        (2, 2, 5),   # large asymmetry
        (3, 3, 4),   # larger subsystems
        (2, 3, 5),   # all different, coprime
    ]

    for dims in multipartite_configs:
        N = int(np.prod(dims))
        print(f"\n  dims={dims}  N={N}")
        t0 = time.time()

        for seed in seeds[:3]:  # fewer seeds for expensive multipartite
            comp_results = run_composition_check(dims, seed)
            if comp_results:
                max_err = max(err for _, _, err in comp_results)
                print(f"    seed={seed}: max composition error = {max_err:.2e}"
                      f"  ({'PASS' if max_err < 1e-8 else 'FAIL'})")
            else:
                print(f"    seed={seed}: no fixed points found")

            # Also run bipartite diagnostics on each single-subsystem marginal
            r = run_bipartite(dims, seed)
            if r:
                for k in range(len(dims)):
                    sr = r.get(f"S_ratio_{k}", 0)
                    interf = r.get(f"interference_{k}", False)
                    interf_r = r.get(f"interference_riem_{k}", False)
                    print(f"      sub {k} (d={dims[k]}): S_lor/S_riem={sr:.4f}"
                          f"  interf={'Y' if interf else 'N'}(Lor)"
                          f" {'Y' if interf_r else 'N'}(Riem)")

        dt = time.time() - t0
        print(f"    ({dt:.1f}s)")

    # ================================================================
    # PART 3: Asymmetry test — does d_sub vs d_env matter?
    # ================================================================
    print("\n\n" + "=" * 80)
    print("PART 3: ASYMMETRY TEST — TRANSPOSE COMPARISON")
    print("=" * 80)
    print("Do dims=(a,b) and dims=(b,a) give the same entropy ratio?")

    asymmetric_pairs = [(2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]

    for d1, d2 in asymmetric_pairs:
        if d1 == d2:
            continue
        rs_fwd = [r for r in all_bipartite if r["dims"] == (d1, d2)]
        rs_rev = [r for r in all_bipartite if r["dims"] == (d2, d1)]

        if rs_fwd and rs_rev:
            # For (d1,d2): subsystem 0 has dim d1, subsystem 1 has dim d2
            # For (d2,d1): subsystem 0 has dim d2, subsystem 1 has dim d1
            # Compare same-dim subsystem entropy ratios
            sr_fwd_0 = np.mean([r["S_ratio_0"] for r in rs_fwd])
            sr_fwd_1 = np.mean([r["S_ratio_1"] for r in rs_fwd])
            sr_rev_0 = np.mean([r["S_ratio_0"] for r in rs_rev])
            sr_rev_1 = np.mean([r["S_ratio_1"] for r in rs_rev])
            print(f"\n  ({d1},{d2}): sub0(d={d1}) S_ratio={sr_fwd_0:.4f}"
                  f"  sub1(d={d2}) S_ratio={sr_fwd_1:.4f}")
            print(f"  ({d2},{d1}): sub0(d={d2}) S_ratio={sr_rev_0:.4f}"
                  f"  sub1(d={d1}) S_ratio={sr_rev_1:.4f}")
        else:
            print(f"\n  ({d1},{d2}) or ({d2},{d1}): insufficient data")

    # ================================================================
    # VERDICT
    # ================================================================
    print("\n\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    # Check if any rank > 2 configuration violated S_lor > S_riem
    violations = []
    for r in all_bipartite:
        rank = min(r["dims"])
        for k in range(len(r["dims"])):
            sr = r.get(f"S_ratio_{k}", 1.0)
            if sr < 1.0:
                violations.append((r["dims"], k, sr, r["seed"]))

    if violations:
        print(f"\n  VIOLATIONS of S_lor > S_riem: {len(violations)}")
        for dims, k, sr, seed in violations:
            print(f"    dims={dims} sub={k} S_ratio={sr:.6f} seed={seed}")
    else:
        n_tests = sum(len(r["dims"]) for r in all_bipartite)
        print(f"\n  S_lor > S_riem: {n_tests} subsystem tests, 0 violations")

    # Rank breakdown
    ranks_tested = sorted(set(min(r["dims"]) for r in all_bipartite))
    print(f"\n  Ranks tested: {ranks_tested}")
    for rank in ranks_tested:
        rs_rank = [r for r in all_bipartite if min(r["dims"]) == rank]
        srs = [r["S_ratio_0"] for r in rs_rank]
        imfs = [r["im_frac_lor"] for r in rs_rank]
        print(f"    rank {rank}: S_lor/S_riem = {np.mean(srs):.4f}±{np.std(srs):.4f}"
              f"  im_frac = {np.mean(imfs):.4f}±{np.std(imfs):.4f}"
              f"  ({len(rs_rank)} configs)")

    # Riemannian im_frac
    all_riem_imf = [r["im_frac_riem"] for r in all_bipartite]
    print(f"\n  Riemannian im_frac: max = {max(all_riem_imf):.2e}"
          f"  (should be ~0)")

    # Phase stripping
    nophase_ratios = []
    for r in all_bipartite:
        for k in range(len(r["dims"])):
            sn = r.get(f"S_nophase_{k}", 0)
            sr = r.get(f"S_riem_{k}", 0)
            if sr > 1e-15:
                nophase_ratios.append(sn / sr)
    if nophase_ratios:
        print(f"\n  Phase-stripping: S_nophase/S_riem = "
              f"{np.mean(nophase_ratios):.6f}±{np.std(nophase_ratios):.6f}"
              f"  (1.000000 = phases explain all excess)")

    print("=" * 80)


if __name__ == "__main__":
    main()
