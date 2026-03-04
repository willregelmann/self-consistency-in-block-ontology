#!/usr/bin/env python3
"""
Finite toy model for the co-emergence thesis.

Tests whether self-consistency with Lorentzian phases produces quantum
coherences (complex off-diagonal density matrix elements) that vanish
in the Riemannian limit.

Model: N=4 smooth structures on S = S_R x S_C (|S_R|=|S_C|=2).
  - State: psi in C^4, L2-normalized
  - Mean-field curvature: R_{rc}(psi) = h_{rc} + alpha_R*P_r + alpha_C*Q_c + beta*|psi_{rc}|^2
  - Weight: w_{rc} = exp(gamma*R_{rc}), gamma = -1 + i*theta
  - Self-consistency: psi* = F(psi*) = w(psi*)/||w(psi*)||_2
  - Observable: rho_R = Tr_C(|psi*><psi*|), test Im(rho_{01}) != 0

The external field h_{rc} represents the intrinsic Einstein-Hilbert action
of each smooth structure (different smooth structures have different
curvature contributions). The Hartree term beta*|psi_{rc}|^2 represents
the back-reaction of a smooth structure on its own curvature. Both terms
break the symmetry that forces the uniform fixed point in the marginal-only
model.

Reference: programs/co-emergence/index.tex, Section 3.6 and Open Problem 2.
"""

import numpy as np
from scipy.optimize import root
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


# ── Model definition ─────────────────────────────────────────────────

# Default external field: intrinsic curvature of each smooth structure.
# Different values break the permutation symmetry that forces uniformity.
H_DEFAULT = np.array([
    [1.0, 0.7],   # smooth structures (r=0, c=0) and (r=0, c=1)
    [0.5, 1.2],   # smooth structures (r=1, c=0) and (r=1, c=1)
])


def curvature(psi, h, alpha_R, alpha_C, beta):
    """Mean-field curvature R_{rc}(psi) for the 2x2 configuration space.

    R_{rc} = h_{rc} + alpha_R * P_r + alpha_C * Q_c + beta * |psi_{rc}|^2

    h_{rc}: intrinsic curvature of smooth structure (r,c)
    P_r = sum_c |psi_{rc}|^2: region marginal
    Q_c = sum_r |psi_{rc}|^2: complement marginal
    beta * |psi_{rc}|^2: Hartree self-coupling
    """
    psi2 = np.abs(psi)**2
    P = psi2.reshape(2, 2)
    P_r = P.sum(axis=1)  # shape (2,)
    Q_c = P.sum(axis=0)  # shape (2,)
    R = h + alpha_R * P_r[:, None] + alpha_C * Q_c[None, :] + beta * P
    return R.ravel()


def weights(psi, gamma, h, alpha_R, alpha_C, beta):
    """Weight function w_{rc} = exp(gamma * R_{rc})."""
    R = curvature(psi, h, alpha_R, alpha_C, beta)
    return np.exp(gamma * R)


def F_map(psi, gamma, h, alpha_R, alpha_C, beta):
    """Self-consistency map F(psi) = w(psi) / ||w(psi)||_2."""
    w = weights(psi, gamma, h, alpha_R, alpha_C, beta)
    norm = np.linalg.norm(w)
    if norm < 1e-30:
        return psi
    return w / norm


# ── Fixed-point solver ───────────────────────────────────────────────

def rho_distance(psi_a, psi_b):
    """Phase-invariant convergence criterion: ||rho(a) - rho(b)||_F.

    The density matrix rho = |psi><psi| is invariant under global phase
    rotations, so this avoids the phase-alignment problem entirely.
    """
    rho_a = np.outer(psi_a, psi_a.conj())
    rho_b = np.outer(psi_b, psi_b.conj())
    return np.linalg.norm(rho_a - rho_b)


def find_fixed_point_iteration(gamma, h, alpha_R, alpha_C, beta,
                                psi0=None, max_iter=50000, tol=1e-12):
    """Find fixed point by direct iteration psi_{n+1} = F(psi_n).

    Convergence is measured by ||rho(F(psi)) - rho(psi)||_F, which is
    invariant under global phase rotations.
    """
    if psi0 is None:
        psi0 = np.random.randn(4) + 1j * np.random.randn(4)
        psi0 /= np.linalg.norm(psi0)

    psi = psi0.copy()
    for i in range(max_iter):
        psi_new = F_map(psi, gamma, h, alpha_R, alpha_C, beta)
        err = rho_distance(psi_new, psi)
        if err < tol:
            return psi_new, err, i + 1
        psi = psi_new
    return psi, err, max_iter


def find_fixed_point_root(gamma, h, alpha_R, alpha_C, beta, psi0=None):
    """Find fixed point via scipy.optimize.root on F(psi)-psi=0."""
    if psi0 is None:
        psi0 = np.random.randn(4) + 1j * np.random.randn(4)
        psi0 /= np.linalg.norm(psi0)

    def residual(x):
        psi = x[:4] + 1j * x[4:]
        psi /= np.linalg.norm(psi)
        Fpsi = F_map(psi, gamma, h, alpha_R, alpha_C, beta)
        # Fix global phase: rotate so psi[0] is real positive
        phase = np.exp(-1j * np.angle(psi[0]))
        psi = psi * phase
        Fpsi = Fpsi * phase
        diff = Fpsi - psi
        return np.concatenate([diff.real, diff.imag])

    x0 = np.concatenate([psi0.real, psi0.imag])
    sol = root(residual, x0, method='hybr', tol=1e-14)
    psi_sol = sol.x[:4] + 1j * sol.x[4:]
    psi_sol /= np.linalg.norm(psi_sol)
    Fpsi = F_map(psi_sol, gamma, h, alpha_R, alpha_C, beta)
    err = rho_distance(Fpsi, psi_sol)
    return psi_sol, err, sol.success


def find_fixed_points(gamma, h, alpha_R, alpha_C, beta, n_starts=20):
    """Try multiple starting points, return all distinct fixed points."""
    fps = []

    def try_add(psi, err):
        if err > 1e-10:
            return
        for fp in fps:
            if abs(np.vdot(psi, fp)) > 1 - 1e-8:
                return
        fps.append(psi)

    for _ in range(n_starts):
        psi, err, _ = find_fixed_point_iteration(gamma, h, alpha_R, alpha_C, beta)
        try_add(psi, err)

    for _ in range(n_starts // 2):
        psi, err, _ = find_fixed_point_root(gamma, h, alpha_R, alpha_C, beta)
        try_add(psi, err)

    return fps


# ── Density matrix analysis ─────────────────────────────────────────

def partial_trace(psi):
    """Compute rho_R = Tr_C(|psi><psi|) for psi on S_R x S_C.

    psi indexed as (r,c) with r,c in {0,1}, flattened as 2r + c.
    (rho_R)_{rr'} = sum_c psi_{rc} psi*_{r'c}
    """
    psi_mat = psi.reshape(2, 2)
    return psi_mat @ psi_mat.conj().T


def analyze_density_matrix(rho):
    """Analyze a 2x2 density matrix."""
    trace = np.trace(rho).real
    purity = np.trace(rho @ rho).real
    eigenvalues = np.linalg.eigvalsh(rho)

    evals_pos = eigenvalues[eigenvalues > 1e-15]
    entropy = -np.sum(evals_pos * np.log2(evals_pos)) if len(evals_pos) > 0 else 0.0

    coherence = rho[0, 1]
    return {
        'trace': trace,
        'purity': purity,
        'eigenvalues': eigenvalues,
        'entropy': entropy,
        'coherence': coherence,
        'coherence_mag': abs(coherence),
        'coherence_im': coherence.imag,
        'hermiticity_error': np.linalg.norm(rho - rho.conj().T),
        'is_psd': np.all(eigenvalues > -1e-12),
    }


# ── Spectral analysis ───────────────────────────────────────────────

def jacobian_numerical(psi, gamma, h, alpha_R, alpha_C, beta, eps=1e-7):
    """Numerical Jacobian of F at psi in real coordinates."""
    n = len(psi)
    x = np.concatenate([psi.real, psi.imag])
    f0 = F_map(psi, gamma, h, alpha_R, alpha_C, beta)
    f0_real = np.concatenate([f0.real, f0.imag])
    J = np.zeros((2 * n, 2 * n))

    for i in range(2 * n):
        x_p = x.copy()
        x_p[i] += eps
        psi_p = x_p[:n] + 1j * x_p[n:]
        f_p = F_map(psi_p, gamma, h, alpha_R, alpha_C, beta)
        J[:, i] = (np.concatenate([f_p.real, f_p.imag]) - f0_real) / eps

    return J


def spectral_analysis(psi, gamma, h, alpha_R, alpha_C, beta):
    """Compute eigenvalues of dF at fixed point."""
    J = jacobian_numerical(psi, gamma, h, alpha_R, alpha_C, beta)
    eigenvalues = np.linalg.eigvals(J)
    mags = np.sort(np.abs(eigenvalues))[::-1]
    spectral_radius = mags[0]
    spectral_gap = mags[0] - mags[1] if len(mags) > 1 else mags[0]
    return eigenvalues, spectral_radius, spectral_gap


# ── Sweeps ───────────────────────────────────────────────────────────

def sweep_theta(thetas, h, alpha_R, alpha_C, beta, n_starts=10):
    """Sweep Lorentzian phase theta, compute coherence at each value."""
    results = []
    for theta in thetas:
        gamma = -1.0 + 1j * theta
        fps = find_fixed_points(gamma, h, alpha_R, alpha_C, beta, n_starts=n_starts)
        if not fps:
            results.append({'theta': theta, 'coherence_im': 0.0,
                            'coherence_mag': 0.0, 'purity': 1.0, 'entropy': 0.0,
                            'n_fps': 0})
            continue

        # Use fixed point with largest |Im(rho[0,1])|
        best = None
        best_coh_im = -1
        for fp in fps:
            rho = partial_trace(fp)
            info = analyze_density_matrix(rho)
            if abs(info['coherence_im']) > best_coh_im:
                best_coh_im = abs(info['coherence_im'])
                best = info
                best['fp'] = fp

        results.append({
            'theta': theta,
            'coherence_im': best['coherence_im'],
            'coherence_mag': best['coherence_mag'],
            'purity': best['purity'],
            'entropy': best['entropy'],
            'n_fps': len(fps),
        })
    return results


# ── Display helpers ──────────────────────────────────────────────────

def print_separator():
    print("=" * 70)


def print_fixed_point(fp, gamma, h, alpha_R, alpha_C, beta, label=""):
    """Print detailed analysis of a fixed point."""
    Fpsi = F_map(fp, gamma, h, alpha_R, alpha_C, beta)
    err = rho_distance(Fpsi, fp)
    rho = partial_trace(fp)
    info = analyze_density_matrix(rho)
    R = curvature(fp, h, alpha_R, alpha_C, beta)

    if label:
        print(f"\n   {label}:")
    print(f"     psi* = {fp}")
    print(f"     |psi*|^2 = {np.abs(fp)**2}")
    print(f"     R(psi*) = {R}")
    print(f"     ||rho(F(psi*)) - rho(psi*)|| = {err:.2e}")
    print(f"     rho_R =")
    print(f"       [{rho[0,0]:.6f}  {rho[0,1]:.6f}]")
    print(f"       [{rho[1,0]:.6f}  {rho[1,1]:.6f}]")
    print(f"     Tr(rho) = {info['trace']:.10f}")
    print(f"     Purity Tr(rho^2) = {info['purity']:.6f}")
    print(f"     Eigenvalues: {info['eigenvalues']}")
    print(f"     Entropy: {info['entropy']:.6f} bits")
    print(f"     rho[0,1] = {info['coherence']:.6e}")
    print(f"     |Im(rho[0,1])| = {abs(info['coherence_im']):.6e}")
    print(f"     Hermitian: {info['hermiticity_error']:.2e}, PSD: {info['is_psd']}")
    return info


# ── Main ─────────────────────────────────────────────────────────────

def main():
    np.random.seed(42)

    # Parameters
    h = H_DEFAULT.copy()
    alpha_R = 0.5
    alpha_C = 0.3
    beta = 0.4       # Hartree self-coupling
    theta = 1.0

    print_separator()
    print("FINITE TOY MODEL FOR THE CO-EMERGENCE THESIS")
    print("N=4 smooth structures on S_R x S_C, |S_R|=|S_C|=2")
    print_separator()
    print(f"\nParameters:")
    print(f"  h (external field) = {h.ravel()}")
    print(f"  alpha_R = {alpha_R}, alpha_C = {alpha_C}, beta = {beta}")
    print(f"  theta = {theta} (Lorentzian phase)")

    # ── 1. Riemannian case (theta=0) ─────────────────────────────────
    print("\n\n1. RIEMANNIAN CASE (theta = 0, gamma = -1)")
    print("-" * 50)
    gamma_riem = -1.0 + 0j
    fps_riem = find_fixed_points(gamma_riem, h, alpha_R, alpha_C, beta)
    print(f"   Fixed points found: {len(fps_riem)}")
    infos_riem = []
    for i, fp in enumerate(fps_riem):
        info = print_fixed_point(fp, gamma_riem, h, alpha_R, alpha_C, beta,
                                  f"Fixed point {i+1}")
        infos_riem.append(info)

    # ── 2. Lorentzian case (theta=1) ─────────────────────────────────
    print(f"\n\n2. LORENTZIAN CASE (theta = {theta}, gamma = -1 + {theta}i)")
    print("-" * 50)
    gamma_lor = -1.0 + 1j * theta
    fps_lor = find_fixed_points(gamma_lor, h, alpha_R, alpha_C, beta)
    print(f"   Fixed points found: {len(fps_lor)}")
    infos_lor = []
    for i, fp in enumerate(fps_lor):
        info = print_fixed_point(fp, gamma_lor, h, alpha_R, alpha_C, beta,
                                  f"Fixed point {i+1}")
        infos_lor.append(info)

    # ── 3. Comparison ────────────────────────────────────────────────
    print("\n\n3. COMPARISON: RIEMANNIAN vs LORENTZIAN")
    print("-" * 50)
    if fps_riem and fps_lor:
        info_riem = infos_riem[0]
        info_lor = infos_lor[0]
        riem_im = abs(info_riem['coherence_im'])
        lor_im = abs(info_lor['coherence_im'])

        print(f"   Riemannian |Im(rho[0,1])| = {riem_im:.6e}")
        print(f"   Lorentzian |Im(rho[0,1])| = {lor_im:.6e}")
        print(f"   Riemannian |rho[0,1]|     = {info_riem['coherence_mag']:.6e}")
        print(f"   Lorentzian |rho[0,1]|     = {info_lor['coherence_mag']:.6e}")
        print(f"   Riemannian purity         = {info_riem['purity']:.6f}")
        print(f"   Lorentzian purity         = {info_lor['purity']:.6f}")
        print(f"   Riemannian entropy        = {info_riem['entropy']:.6f} bits")
        print(f"   Lorentzian entropy        = {info_lor['entropy']:.6f} bits")

        if lor_im > 1e-10 and riem_im < 1e-10:
            print("\n   POSITIVE: Lorentzian phases generate quantum coherences")
            print("   absent in the Riemannian case.")
        elif lor_im < 1e-10 and riem_im < 1e-10:
            print("\n   NEGATIVE: No quantum coherences in either case.")
        elif lor_im > riem_im * 10:
            print(f"\n   PARTIAL POSITIVE: Lorentzian coherence {lor_im/max(riem_im,1e-30):.1f}x Riemannian.")
        else:
            print(f"\n   MIXED: Lor/Riem ratio = {lor_im/max(riem_im,1e-30):.2f}")

    # ── 4. Spectral analysis ─────────────────────────────────────────
    print("\n\n4. SPECTRAL ANALYSIS")
    print("-" * 50)
    for label, gamma, fps in [("Riemannian", gamma_riem, fps_riem),
                               ("Lorentzian", gamma_lor, fps_lor)]:
        if fps:
            evals, sr, sg = spectral_analysis(fps[0], gamma, h, alpha_R, alpha_C, beta)
            print(f"\n   {label} (first fixed point):")
            print(f"     |eigenvalues| = {np.sort(np.abs(evals))[::-1]}")
            print(f"     Spectral radius: {sr:.6f}")
            print(f"     Spectral gap: {sg:.6f}")
            print(f"     {'Stable' if sr < 1 else 'UNSTABLE'} (radius {'<' if sr < 1 else '>='} 1)")

    # ── 5. Phase diagram: sweep theta ────────────────────────────────
    print("\n\n5. PHASE DIAGRAM: sweeping theta from 0 to 3")
    print("-" * 50)
    thetas = np.linspace(0, 3.0, 31)
    results = sweep_theta(thetas, h, alpha_R, alpha_C, beta, n_starts=8)

    print(f"   {'theta':>6s}  {'|Im(rho12)|':>12s}  {'|rho12|':>12s}  "
          f"{'Purity':>8s}  {'S(bits)':>8s}  {'#FP':>4s}")
    for r in results[::6]:
        print(f"   {r['theta']:6.2f}  {abs(r['coherence_im']):12.6e}  "
              f"{r['coherence_mag']:12.6e}  {r['purity']:8.4f}  "
              f"{r['entropy']:8.4f}  {r['n_fps']:4d}")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle('Co-emergence toy model: phase diagram over theta', fontsize=14)

    th = [r['theta'] for r in results]
    coh_im = [abs(r['coherence_im']) for r in results]
    coh_mag = [r['coherence_mag'] for r in results]
    pur = [r['purity'] for r in results]
    ent = [r['entropy'] for r in results]

    axes[0, 0].plot(th, coh_im, 'b.-')
    axes[0, 0].set_xlabel('theta (Lorentzian phase)')
    axes[0, 0].set_ylabel('|Im(rho_R[0,1])|')
    axes[0, 0].set_title('Quantum coherence vs signature parameter')
    axes[0, 0].axvline(x=0, color='r', linestyle='--', alpha=0.5, label='Riemannian')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(th, coh_mag, 'g.-')
    axes[0, 1].set_xlabel('theta')
    axes[0, 1].set_ylabel('|rho_R[0,1]|')
    axes[0, 1].set_title('Off-diagonal magnitude')
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(th, pur, 'm.-')
    axes[1, 0].set_xlabel('theta')
    axes[1, 0].set_ylabel('Tr(rho^2)')
    axes[1, 0].set_title('Purity (1=pure, 0.5=maximally mixed)')
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(th, ent, 'r.-')
    axes[1, 1].set_xlabel('theta')
    axes[1, 1].set_ylabel('S (bits)')
    axes[1, 1].set_title('Entanglement entropy')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('programs/co-emergence/explorations/2026-03-04-toy-model-phase-diagram.png',
                dpi=150)
    print("\n   Saved: 2026-03-04-toy-model-phase-diagram.png")

    # ── 6. Parameter sensitivity ─────────────────────────────────────
    print("\n\n6. PARAMETER SENSITIVITY")
    print("-" * 50)

    fig2, axes2 = plt.subplots(2, 2, figsize=(12, 9))
    fig2.suptitle('Parameter sensitivity (Lorentzian, theta=1.0 unless varied)', fontsize=14)

    param_sweeps = [
        ('alpha_R', np.linspace(0.05, 1.5, 15), 'alpha_R'),
        ('alpha_C', np.linspace(0.05, 1.5, 15), 'alpha_C'),
        ('beta', np.linspace(0.0, 2.0, 15), 'beta'),
        ('theta', np.linspace(0.0, 3.0, 15), 'theta'),
    ]

    for ax_idx, (pname, pvals, plabel) in enumerate(param_sweeps):
        ax = axes2[ax_idx // 2, ax_idx % 2]
        coh_vals = []
        sg_vals = []
        for val in pvals:
            kw = {'h': h, 'alpha_R': alpha_R, 'alpha_C': alpha_C, 'beta': beta}
            if pname == 'theta':
                gamma_p = -1.0 + 1j * val
            else:
                kw[pname] = val
                gamma_p = -1.0 + 1j * theta

            fps = find_fixed_points(gamma_p, **kw, n_starts=6)
            if fps:
                rho = partial_trace(fps[0])
                info = analyze_density_matrix(rho)
                _, _, sg = spectral_analysis(fps[0], gamma_p, **kw)
                coh_vals.append(abs(info['coherence_im']))
                sg_vals.append(sg)
            else:
                coh_vals.append(np.nan)
                sg_vals.append(np.nan)

        ax.plot(pvals, coh_vals, 'b.-', label='|Im(rho12)|')
        ax.set_xlabel(plabel)
        ax.set_ylabel('|Im(rho[0,1])|', color='b')
        ax.tick_params(axis='y', labelcolor='b')
        ax.grid(True, alpha=0.3)
        ax.set_title(f'Sensitivity to {plabel}')

        ax_r = ax.twinx()
        ax_r.plot(pvals, sg_vals, 'r.--', alpha=0.7)
        ax_r.set_ylabel('spectral gap', color='r')
        ax_r.tick_params(axis='y', labelcolor='r')

    plt.tight_layout()
    plt.savefig('programs/co-emergence/explorations/2026-03-04-toy-model-sensitivity.png',
                dpi=150)
    print("   Saved: 2026-03-04-toy-model-sensitivity.png")

    # ── 7. Diagnostic: uniform h (confirm the original model's failure) ──
    print("\n\n7. DIAGNOSTIC: UNIFORM h (original model, should give trivial result)")
    print("-" * 50)
    h_uniform = np.ones((2, 2)) * 1.0
    gamma_lor_diag = -1.0 + 1j * theta
    fps_diag = find_fixed_points(gamma_lor_diag, h_uniform, alpha_R, alpha_C, 0.0)
    if fps_diag:
        rho_diag = partial_trace(fps_diag[0])
        info_diag = analyze_density_matrix(rho_diag)
        print(f"   |psi*|^2 = {np.abs(fps_diag[0])**2}")
        print(f"   |Im(rho[0,1])| = {abs(info_diag['coherence_im']):.6e}")
        print(f"   Purity = {info_diag['purity']:.6f}")
        print(f"   (Confirming: uniform h + no Hartree => trivial fixed point)")

    # ── 8. Summary ───────────────────────────────────────────────────
    print("\n")
    print_separator()
    print("SUMMARY")
    print_separator()

    if fps_riem and fps_lor:
        rho_riem = partial_trace(fps_riem[0])
        rho_lor = partial_trace(fps_lor[0])
        info_riem = analyze_density_matrix(rho_riem)
        info_lor = analyze_density_matrix(rho_lor)
        riem_im = abs(info_riem['coherence_im'])
        lor_im = abs(info_lor['coherence_im'])

        print(f"\nRiemannian (theta=0):")
        print(f"  rho_R = [{rho_riem[0,0]:.6f}  {rho_riem[0,1]:.6f}]")
        print(f"          [{rho_riem[1,0]:.6f}  {rho_riem[1,1]:.6f}]")
        print(f"  |Im(rho[0,1])| = {riem_im:.6e}")
        print(f"  Purity = {info_riem['purity']:.6f}, Entropy = {info_riem['entropy']:.6f} bits")

        print(f"\nLorentzian (theta={theta}):")
        print(f"  rho_R = [{rho_lor[0,0]:.6f}  {rho_lor[0,1]:.6f}]")
        print(f"          [{rho_lor[1,0]:.6f}  {rho_lor[1,1]:.6f}]")
        print(f"  |Im(rho[0,1])| = {lor_im:.6e}")
        print(f"  Purity = {info_lor['purity']:.6f}, Entropy = {info_lor['entropy']:.6f} bits")

        print("\nVERDICT:")
        if lor_im > 1e-10 and riem_im < 1e-10:
            print("  POSITIVE: Lorentzian self-consistency generates quantum")
            print("  coherences (complex off-diagonal rho) that are absent in the")
            print("  Riemannian case. The quantum/classical boundary coincides")
            print("  with the Lorentzian/Riemannian boundary.")
        elif lor_im < 1e-10 and riem_im < 1e-10:
            print("  NEGATIVE: Self-consistency produces only real fixed points")
            print("  in both cases. No quantum coherences emerge from the model.")
            print("  Additional structure is needed to generate complex amplitudes.")
        elif lor_im > riem_im * 10:
            print(f"  PARTIAL POSITIVE: Lorentzian coherence is {lor_im/max(riem_im,1e-30):.1f}x")
            print("  larger than Riemannian. Signature enhances coherence.")
        else:
            print(f"  INCONCLUSIVE: Both cases have comparable coherence.")
            print(f"  Lor/Riem ratio: {lor_im/max(riem_im,1e-30):.2f}")
    else:
        print("  FAILED: Could not find fixed points in one or both cases.")

    print_separator()


if __name__ == '__main__':
    main()
