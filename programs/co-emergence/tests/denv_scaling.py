#!/usr/bin/env python3
"""
d_env → ∞ experiment: does the Im/Re plateau survive as environment dimension grows?

For each d_env in {2, 3, 4, 6, 8, 12}, run dims = (d_sub, d_env) with d_sub
large enough to be clearly in the plateau regime. Measure Im/Re ratio of the
subsystem (index 0) partial trace.

Then fit:
  (a) saturating: plateau = a / (1 + b * d_env)
  (b) power law: plateau = c * d_env^(-alpha)
"""

import numpy as np
import sys
import time

sys.path.insert(0, ".")
from toy_model import CoEmergenceModel


def im_re_ratio(rho):
    """Im/Re ratio of off-diagonal Frobenius norms."""
    od = rho.copy()
    np.fill_diagonal(od, 0)
    im_norm = np.linalg.norm(od.imag)
    re_norm = np.linalg.norm(od.real)
    if re_norm < 1e-15:
        return 0.0
    return im_norm / re_norm


def entropy(rho):
    """Von Neumann entropy."""
    evals = np.linalg.eigvalsh(rho)
    evals = evals[evals > 1e-15]
    return -np.sum(evals * np.log(evals))


def run_single(d_sub, d_env, seed):
    """Run one (d_sub, d_env) configuration. Returns dict or None."""
    dims = (d_sub, d_env)
    N = d_sub * d_env

    rng = np.random.RandomState(seed)
    h = rng.uniform(0.5, 1.5, size=N)
    alphas = [0.4, 0.4]
    beta = 0.4

    model_lor = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                                  gamma=-1.0 + 1j)
    model_riem = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=beta,
                                   gamma=-1.0 + 0j)

    np.random.seed(seed * 1000 + d_env * 100 + d_sub)
    n_starts = max(10, 25 - d_sub // 4)

    fps_lor = model_lor.find_fixed_points(n_starts=n_starts)
    fps_riem = model_riem.find_fixed_points(n_starts=n_starts)

    if not fps_lor or not fps_riem:
        return None

    fp_lor = fps_lor[0]
    fp_riem = fps_riem[0]

    # Partial trace over environment (keep subsystem 0)
    rho_lor = CoEmergenceModel.partial_trace(fp_lor, dims, (0,))
    rho_riem = CoEmergenceModel.partial_trace(fp_riem, dims, (0,))

    return {
        "d_sub": d_sub,
        "d_env": d_env,
        "N": N,
        "seed": seed,
        "im_re": im_re_ratio(rho_lor),
        "im_re_riem": im_re_ratio(rho_riem),
        "S_lor": entropy(rho_lor),
        "S_riem": entropy(rho_riem),
    }


def main():
    print("=" * 80)
    print("d_env SCALING: DOES Im/Re PLATEAU SURVIVE AS d_env → ∞?")
    print("=" * 80)

    seeds = [42, 123, 456, 789, 1011]

    # For each d_env, pick d_sub values that are clearly in the plateau regime
    # From previous work: plateau starts at d_sub ~ 4 for d_env=2,3
    # Use d_sub large enough to be well into plateau for each d_env
    configs = [
        # (d_env, [d_sub values])
        (2,  [4, 8, 16, 24, 32]),
        (3,  [4, 8, 12, 16, 20]),
        (4,  [4, 8, 12, 16]),
        (6,  [4, 8, 12]),
        (8,  [4, 8, 12]),
        (12, [4, 8]),
    ]

    all_results = []

    for d_env, d_subs in configs:
        print(f"\n{'='*60}")
        print(f"d_env = {d_env}")
        print(f"{'='*60}")

        for d_sub in d_subs:
            N = d_sub * d_env
            t0 = time.time()
            seed_results = []
            for seed in seeds:
                r = run_single(d_sub, d_env, seed)
                if r is not None:
                    seed_results.append(r)
                    all_results.append(r)

            dt = time.time() - t0
            if seed_results:
                im_res = [r["im_re"] for r in seed_results]
                s_ratios = [r["S_lor"] / r["S_riem"] if r["S_riem"] > 1e-10 else 0
                            for r in seed_results]
                print(f"  d_sub={d_sub:>3d}  N={N:>4d}  "
                      f"Im/Re={np.mean(im_res):.4f}±{np.std(im_res):.4f}  "
                      f"S_lor/S_riem={np.mean(s_ratios):.3f}±{np.std(s_ratios):.3f}  "
                      f"({len(seed_results)}/5 seeds)  {dt:.1f}s")
            else:
                print(f"  d_sub={d_sub:>3d}  N={N:>4d}  FAILED all seeds")

    # Extract plateau values (use largest d_sub for each d_env)
    print("\n\n" + "=" * 80)
    print("PLATEAU VALUES (from largest d_sub at each d_env)")
    print("=" * 80)

    plateau_data = []
    for d_env, d_subs in configs:
        # Use the largest d_sub as the plateau estimate
        d_sub_max = d_subs[-1]
        rs = [r for r in all_results if r["d_env"] == d_env and r["d_sub"] == d_sub_max]
        if rs:
            im_res = [r["im_re"] for r in rs]
            s_lors = [r["S_lor"] for r in rs]
            s_riems = [r["S_riem"] for r in rs]
            s_ratios = [r["S_lor"] / r["S_riem"] if r["S_riem"] > 1e-10 else 0
                        for r in rs]
            plateau_data.append({
                "d_env": d_env,
                "d_sub": d_sub_max,
                "im_re_mean": np.mean(im_res),
                "im_re_std": np.std(im_res),
                "s_ratio_mean": np.mean(s_ratios),
                "s_ratio_std": np.std(s_ratios),
            })
            print(f"  d_env={d_env:>3d}  (d_sub={d_sub_max:>3d})  "
                  f"Im/Re={np.mean(im_res):.4f}±{np.std(im_res):.4f}  "
                  f"S_lor/S_riem={np.mean(s_ratios):.3f}±{np.std(s_ratios):.3f}")

    # Fit models
    if len(plateau_data) >= 4:
        from scipy.optimize import curve_fit

        d_envs = np.array([p["d_env"] for p in plateau_data], dtype=float)
        im_res = np.array([p["im_re_mean"] for p in plateau_data])
        im_stds = np.array([p["im_re_std"] for p in plateau_data])
        # Use max(std, 0.005) to avoid zero-weight issues
        weights = np.maximum(im_stds, 0.005)

        print("\n\n" + "=" * 80)
        print("FIT: Im/Re plateau vs d_env")
        print("=" * 80)

        # (a) Saturating: a / (1 + b * d_env)
        def saturating(x, a, b):
            return a / (1 + b * x)

        # (b) Power law: c * x^(-alpha)
        def power_law(x, c, alpha):
            return c * x ** (-alpha)

        # (c) Saturating with offset: a / (1 + b * d_env) + c
        def saturating_offset(x, a, b, c):
            return a / (1 + b * x) + c

        try:
            popt_sat, pcov_sat = curve_fit(saturating, d_envs, im_res,
                                            p0=[0.5, 0.1], sigma=weights)
            resid_sat = np.sum(((im_res - saturating(d_envs, *popt_sat)) / weights) ** 2)
            print(f"\n  Saturating: Im/Re = {popt_sat[0]:.4f} / (1 + {popt_sat[1]:.4f} * d_env)")
            print(f"    d_env→∞ limit: 0")
            print(f"    χ²/dof = {resid_sat / (len(d_envs) - 2):.4f}")
        except Exception as e:
            print(f"  Saturating fit failed: {e}")
            popt_sat = None

        try:
            popt_pow, pcov_pow = curve_fit(power_law, d_envs, im_res,
                                            p0=[0.4, 0.3], sigma=weights)
            resid_pow = np.sum(((im_res - power_law(d_envs, *popt_pow)) / weights) ** 2)
            print(f"\n  Power law: Im/Re = {popt_pow[0]:.4f} * d_env^(-{popt_pow[1]:.4f})")
            print(f"    d_env→∞ limit: 0")
            print(f"    χ²/dof = {resid_pow / (len(d_envs) - 2):.4f}")
        except Exception as e:
            print(f"  Power law fit failed: {e}")
            popt_pow = None

        try:
            popt_so, pcov_so = curve_fit(saturating_offset, d_envs, im_res,
                                          p0=[0.3, 0.1, 0.1], sigma=weights)
            resid_so = np.sum(((im_res - saturating_offset(d_envs, *popt_so)) / weights) ** 2)
            print(f"\n  Saturating+offset: Im/Re = {popt_so[0]:.4f} / (1 + {popt_so[1]:.4f} * d_env) + {popt_so[2]:.4f}")
            print(f"    d_env→∞ limit: {popt_so[2]:.4f}")
            print(f"    χ²/dof = {resid_so / (len(d_envs) - 3):.4f}")
        except Exception as e:
            print(f"  Saturating+offset fit failed: {e}")
            popt_so = None

        # Also fit entropy ratio
        s_ratios = np.array([p["s_ratio_mean"] for p in plateau_data])
        s_stds = np.array([p["s_ratio_std"] for p in plateau_data])
        s_weights = np.maximum(s_stds, 0.01)

        print("\n\n" + "=" * 80)
        print("FIT: S_lor/S_riem vs d_env")
        print("=" * 80)

        try:
            popt_sp, _ = curve_fit(power_law, d_envs, s_ratios,
                                    p0=[1.7, 0.01], sigma=s_weights)
            resid_sp = np.sum(((s_ratios - power_law(d_envs, *popt_sp)) / s_weights) ** 2)
            print(f"\n  Power law: S_ratio = {popt_sp[0]:.4f} * d_env^(-{popt_sp[1]:.4f})")
            print(f"    χ²/dof = {resid_sp / (len(d_envs) - 2):.4f}")
        except Exception as e:
            print(f"  Power law fit failed: {e}")

        # Log-log for Im/Re
        print("\n\n" + "=" * 80)
        print("LOG-LOG FIT (simple)")
        print("=" * 80)
        log_d = np.log(d_envs)
        log_ir = np.log(im_res)
        coeffs = np.polyfit(log_d, log_ir, 1)
        print(f"  Im/Re ~ d_env^({coeffs[0]:.4f})")
        print(f"  If exponent ≈ 0: plateau survives")
        print(f"  If exponent < -0.5: decay, mechanism may fail")
        print(f"  If exponent ≈ -0.5: 1/sqrt dilution")

    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)
    if len(plateau_data) >= 3:
        ir_2 = plateau_data[0]["im_re_mean"]
        ir_last = plateau_data[-1]["im_re_mean"]
        ratio = ir_last / ir_2
        print(f"\n  Im/Re at d_env=2: {ir_2:.4f}")
        print(f"  Im/Re at d_env={plateau_data[-1]['d_env']}: {ir_last:.4f}")
        print(f"  Ratio: {ratio:.4f}")

        if ratio > 0.5:
            print("\n  POSITIVE: Im/Re ratio decays slowly. Mechanism likely survives.")
        elif ratio > 0.2:
            print("\n  MIXED: Significant decay. Need larger d_env to determine fate.")
        else:
            print("\n  NEGATIVE: Im/Re ratio collapses. Mechanism may not survive d_env → ∞.")
    print("=" * 80)


if __name__ == "__main__":
    main()
