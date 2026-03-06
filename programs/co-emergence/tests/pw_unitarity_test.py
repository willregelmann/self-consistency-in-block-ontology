"""
Test whether measure-theoretic PW conditioning produces approximately
unitary time evolution.

Two questions:
1. Approximate unitarity: are the magnitude profiles |mu_{S|c}(s)|
   approximately c-independent? (If so, c-dependence is mostly in phases.)
2. Hamiltonian generation: for d_clock >= 3, do the conditional states
   lie on a one-parameter unitary orbit? (Toeplitz Gram matrix test.)

Reference: exploration 2026-03-06-pw-unitarity.md
"""

import numpy as np
from toy_model import CoEmergenceModel
from measure_pw_conditioning import all_conditional_dms


def conditional_states(psi, dims, clock_idx):
    """Extract normalized conditional state vectors |phi_c> = mu_{S|c} / ||mu_{S|c}||.

    Returns
    -------
    phis : list of ndarray
        Normalized conditional state vectors
    probs : ndarray
        p(c) = ||mu_{S|c}||^2
    """
    n = len(dims)
    psi_tensor = psi.reshape(dims)
    d_clock = dims[clock_idx]

    phis = []
    probs = []
    for c in range(d_clock):
        slicing = [slice(None)] * n
        slicing[clock_idx] = c
        mu_c = psi_tensor[tuple(slicing)].ravel()
        p = np.real(np.vdot(mu_c, mu_c))
        probs.append(p)
        phis.append(mu_c / np.sqrt(p))

    return phis, np.array(probs)


def magnitude_variation(phis):
    """Measure how much magnitude profiles vary across clock values.

    If evolution is unitary, |phi_c(s)| should be c-independent.

    Returns
    -------
    mean_var : float
        Mean Frobenius distance between magnitude profiles
    max_var : float
        Max Frobenius distance
    mag_profiles : list of ndarray
        |phi_c(s)| for each c
    """
    mags = [np.abs(phi) for phi in phis]
    n = len(mags)
    dists = []
    for i in range(n):
        for j in range(i + 1, n):
            dists.append(np.linalg.norm(mags[i] - mags[j]))
    return np.mean(dists), np.max(dists), mags


def gram_matrix(phis):
    """Compute Gram matrix G_{cc'} = <phi_c | phi_c'>.

    For Hamiltonian-generated evolution, G should be Toeplitz:
    G_{cc'} = g(c - c').
    """
    n = len(phis)
    G = np.zeros((n, n), dtype=complex)
    for i in range(n):
        for j in range(n):
            G[i, j] = np.vdot(phis[i], phis[j])
    return G


def toeplitz_deviation(G):
    """Measure how far G is from being Toeplitz.

    For a Toeplitz matrix, G_{ij} depends only on |i-j|.
    Compute the variance of G entries at each diagonal offset.

    Returns
    -------
    deviation : float
        RMS of the standard deviations at each offset, normalized.
    diag_means : dict
        Mean value at each offset k.
    diag_stds : dict
        Std at each offset k.
    """
    n = G.shape[0]
    diag_means = {}
    diag_stds = {}
    deviations = []

    for k in range(n):
        # Collect all entries at offset k
        vals = []
        for i in range(n - k):
            vals.append(G[i, i + k])
        vals = np.array(vals)
        diag_means[k] = np.mean(vals)
        if len(vals) > 1:
            std = np.std(np.abs(vals))
            diag_stds[k] = std
            deviations.append(std)
        else:
            diag_stds[k] = 0.0

    deviation = np.sqrt(np.mean(np.array(deviations) ** 2)) if deviations else 0.0
    return deviation, diag_means, diag_stds


def unitary_orbit_test(phis):
    """Test if conditional states lie on a one-parameter unitary orbit.

    For d_clock >= 3: if |phi_c> = U^c |phi_0>, then U|phi_0> = |phi_1>
    and U|phi_1> should equal |phi_2>. Test this by constructing the
    "best" unitary U mapping phi_0 -> phi_1 via polar decomposition,
    then checking U|phi_1> against |phi_2>.

    Returns
    -------
    errors : list of float
        ||U|phi_{c}> - |phi_{c+1}>||  for c = 1, ..., d_clock - 2
        (after constructing U from the c=0 -> c=1 step)
    U : ndarray
        The unitary constructed from phi_0 -> phi_1
    """
    if len(phis) < 3:
        return [], None

    d = len(phis[0])
    phi0 = phis[0]
    phi1 = phis[1]

    # Construct unitary U such that U|phi_0> = |phi_1>
    # Use the construction: rotate in the span{phi_0, phi_1} plane,
    # identity on the orthogonal complement.
    # This gives the "minimal rotation" unitary.

    overlap = np.vdot(phi0, phi1)
    # Orthogonal component of phi_1 relative to phi_0
    phi1_perp = phi1 - overlap * phi0
    norm_perp = np.linalg.norm(phi1_perp)

    if norm_perp < 1e-12:
        # phi_0 and phi_1 are nearly parallel — U is approximately identity
        U = np.eye(d, dtype=complex)
    else:
        e0 = phi0
        e1 = phi1_perp / norm_perp

        # In the {e0, e1} plane, the rotation is:
        # U e0 = overlap * e0 + norm_perp * e1 = phi_1
        # U e1 = -conj(norm_perp) * e0 + conj(overlap) * e1
        # (This is a 2x2 unitary block)

        # Build U = I + (rotation - I) projected onto {e0, e1}
        # rotation matrix in {e0, e1} basis:
        R_2x2 = np.array([
            [overlap, -np.conj(norm_perp)],
            [norm_perp, np.conj(overlap)]
        ])

        # U = I + |e0><e0| (R00-1) + |e0><e1| R01 + |e1><e0| R10 + |e1><e1| (R11-1)
        U = np.eye(d, dtype=complex)
        U += (R_2x2[0, 0] - 1) * np.outer(e0, e0.conj())
        U += R_2x2[0, 1] * np.outer(e0, e1.conj())
        U += R_2x2[1, 0] * np.outer(e1, e0.conj())
        U += (R_2x2[1, 1] - 1) * np.outer(e1, e1.conj())

    # Verify U|phi_0> = |phi_1>
    check = np.linalg.norm(U @ phi0 - phi1)
    assert check < 1e-10, f"U construction failed: ||U phi_0 - phi_1|| = {check}"

    # Now test: does U|phi_c> ≈ |phi_{c+1}> for c >= 1?
    errors = []
    for c in range(1, len(phis) - 1):
        predicted = U @ phis[c]
        # Allow global phase: minimize ||e^{ia} predicted - phi_{c+1}||
        phase = np.vdot(predicted, phis[c + 1])
        phase /= abs(phase) if abs(phase) > 1e-15 else 1.0
        err = np.linalg.norm(predicted * np.conj(phase) - phis[c + 1])
        errors.append(err)

    return errors, U


def phase_hamiltonian_test(phis, psi, dims, clock_idx):
    """Extract the effective Hamiltonian from the phase structure.

    Since psi*_sigma = |psi*_sigma| exp(i theta R_sigma), the phase
    of phi_c(s) relative to phi_0(s) is approximately
    theta * (R_{(c,s)} - R_{(0,s)}). If this is linear in c,
    then H_eff(s) = theta * dR/dc evaluated at c=0.

    Returns
    -------
    H_diag : ndarray
        Diagonal "Hamiltonian" (phase differences per unit c)
    linearity_error : float
        How well the phases are linear in c
    """
    d_clock = dims[clock_idx]
    d_sys = len(phis[0])

    # Extract phases relative to phi_0
    # phi_c(s) / phi_0(s) gives the relative phase at each s
    phases = np.zeros((d_clock, d_sys))
    for c in range(d_clock):
        ratio = phis[c] / phis[0]
        phases[c, :] = np.angle(ratio)

    # Unwrap phases (they should be continuous in c)
    for s in range(d_sys):
        phases[:, s] = np.unwrap(phases[:, s])

    # phases[0, :] should be 0
    # H_diag = phase slope with respect to c
    H_diag = np.zeros(d_sys)
    linearity_errors = []

    if d_clock >= 3:
        for s in range(d_sys):
            # Linear fit: phase_c(s) = H(s) * c
            c_vals = np.arange(d_clock)
            coeffs = np.polyfit(c_vals, phases[:, s], 1)
            H_diag[s] = coeffs[0]
            predicted = np.polyval(coeffs, c_vals)
            linearity_errors.append(np.linalg.norm(phases[:, s] - predicted))
    else:
        # d_clock = 2: H_diag = phases[1, :]
        H_diag = phases[1, :]
        linearity_errors = [0.0]

    return H_diag, np.mean(linearity_errors)


def run_test(dims, theta, clock_idx=0, seed=42, verbose=True):
    """Run unitarity tests for a single configuration."""
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

    phis, probs = conditional_states(psi, dims, clock_idx)
    d_clock = dims[clock_idx]

    sig = "Lorentzian" if theta > 0 else "Riemannian"
    if verbose:
        print(f"\n{'='*65}")
        print(f"dims={dims}, {sig} (theta={theta}), clock=subsystem {clock_idx}")
        print(f"d_clock={d_clock}, d_sys={N // d_clock}")
        print(f"p(c) = {['%.4f' % p for p in probs]}")

    # Test 1: magnitude variation
    mean_var, max_var, mags = magnitude_variation(phis)
    if verbose:
        print(f"\n  MAGNITUDE VARIATION (unitarity requires ~0):")
        print(f"    mean ||mag_c - mag_c'||: {mean_var:.6f}")
        print(f"    max  ||mag_c - mag_c'||: {max_var:.6f}")

    # Test 2: Gram matrix and Toeplitz property
    G = gram_matrix(phis)
    if verbose:
        print(f"\n  GRAM MATRIX |<phi_c|phi_c'>|:")
        for i in range(d_clock):
            row = ' '.join(f'{abs(G[i,j]):.4f}' for j in range(d_clock))
            print(f"    {row}")

    if d_clock >= 3:
        toep_dev, diag_means, diag_stds = toeplitz_deviation(G)
        if verbose:
            print(f"\n  TOEPLITZ DEVIATION (Hamiltonian requires ~0):")
            print(f"    RMS deviation: {toep_dev:.6f}")
            for k, std in diag_stds.items():
                print(f"    offset {k}: mean |G| = {abs(diag_means[k]):.4f}, "
                      f"std = {std:.6f}")

    # Test 3: unitary orbit (d_clock >= 3)
    if d_clock >= 3:
        orbit_errors, U = unitary_orbit_test(phis)
        if verbose:
            print(f"\n  UNITARY ORBIT TEST (U|phi_c> = |phi_{{c+1}}>):")
            for c, err in enumerate(orbit_errors):
                print(f"    c={c+1} -> c={c+2}: ||U phi_c - phi_{{c+1}}|| = {err:.6f}")

    # Test 4: phase Hamiltonian
    if theta > 0:
        H_diag, lin_err = phase_hamiltonian_test(phis, psi, dims, clock_idx)
        if verbose:
            print(f"\n  PHASE HAMILTONIAN (linearity of phase in c):")
            print(f"    H_eff diagonal: {['%.4f' % h for h in H_diag]}")
            print(f"    mean linearity error: {lin_err:.6f}")

    return {
        'dims': dims, 'theta': theta, 'clock_idx': clock_idx,
        'mag_mean_var': mean_var, 'mag_max_var': max_var,
        'gram': G, 'probs': probs, 'phis': phis,
        'toep_dev': toeplitz_deviation(G)[0] if d_clock >= 3 else None,
        'orbit_errors': unitary_orbit_test(phis)[0] if d_clock >= 3 else None,
    }


def run_weak_coupling_sweep(verbose=True):
    """Test how unitarity improves as clock-system coupling weakens.

    Sweep alpha_clock from 0.5 (strong) to 0.01 (weak) while keeping
    system couplings fixed.
    """
    if verbose:
        print(f"\n{'='*65}")
        print("WEAK COUPLING SWEEP: alpha_clock -> 0")
        print("dims=(3, 4), Lorentzian, clock=subsystem 0")
        print(f"{'='*65}")

    dims = (3, 4)
    N = 12
    rng = np.random.RandomState(42)
    h = rng.uniform(0.5, 1.5, size=N)
    theta = 1.0

    alpha_clocks = [0.5, 0.2, 0.1, 0.05, 0.01, 0.001]

    if verbose:
        print(f"\n  {'alpha_clock':>12} {'mag_var':>10} {'toep_dev':>10} "
              f"{'orbit_err':>10} {'lin_err':>10}")
        print(f"  {'-'*52}")

    for alpha_c in alpha_clocks:
        alphas = [alpha_c, 0.3]
        gamma = -1.0 + 1j * theta
        model = CoEmergenceModel(dims=dims, h=h, alphas=alphas, beta=0.4, gamma=gamma)
        np.random.seed(42)
        psi, err, iters = model.find_fixed_point()
        assert err < 1e-10

        phis, probs = conditional_states(psi, dims, clock_idx=0)
        mean_var, _, _ = magnitude_variation(phis)
        toep_dev, _, _ = toeplitz_deviation(gram_matrix(phis))
        orbit_errors, _ = unitary_orbit_test(phis)
        _, lin_err = phase_hamiltonian_test(phis, psi, dims, clock_idx=0)
        orbit_err = max(orbit_errors) if orbit_errors else 0.0

        if verbose:
            print(f"  {alpha_c:>12.3f} {mean_var:>10.6f} {toep_dev:>10.6f} "
                  f"{orbit_err:>10.6f} {lin_err:>10.6f}")


def run_separable_h_test(verbose=True):
    """Test with h_{(c,s)} = h^C_c + h^S_s (separable external field).

    In the separable limit, conditional states should be c-independent
    (only global phase varies).
    """
    if verbose:
        print(f"\n{'='*65}")
        print("SEPARABLE h TEST: h_{(c,s)} = h^C_c + h^S_s")
        print(f"{'='*65}")

    dims = (3, 4)
    N = 12
    rng = np.random.RandomState(42)
    h_C = rng.uniform(0.5, 1.5, size=3)
    h_S = rng.uniform(0.5, 1.5, size=4)

    # Build separable h
    h_sep = np.zeros(N)
    for c in range(3):
        for s in range(4):
            h_sep[c * 4 + s] = h_C[c] + h_S[s]

    gamma = -1.0 + 1j
    model = CoEmergenceModel(dims=dims, h=h_sep, alphas=[0.5, 0.3], beta=0.4, gamma=gamma)
    np.random.seed(42)
    psi, err, iters = model.find_fixed_point()
    assert err < 1e-10

    phis, probs = conditional_states(psi, dims, clock_idx=0)

    # With separable h, the conditional density matrices should be very similar
    # (not identical because of marginal couplings and self-coupling)
    rhos = [np.outer(phi, phi.conj()) for phi in phis]
    dists = []
    for i in range(3):
        for j in range(i+1, 3):
            dists.append(np.linalg.norm(rhos[i] - rhos[j]))

    if verbose:
        print(f"  Conditional DM distances: {['%.6f' % d for d in dists]}")
        print(f"  p(c) = {['%.4f' % p for p in probs]}")

    # Now add a non-separable interaction
    if verbose:
        print(f"\n  Adding non-separable interaction: h -> h + epsilon * random")

    for eps in [0.0, 0.1, 0.3, 0.5, 1.0]:
        h_int = h_sep + eps * rng.uniform(-0.5, 0.5, size=N)
        model = CoEmergenceModel(dims=dims, h=h_int, alphas=[0.5, 0.3],
                                 beta=0.4, gamma=gamma)
        np.random.seed(42)
        psi, err, iters = model.find_fixed_point()
        assert err < 1e-10

        phis, probs = conditional_states(psi, dims, clock_idx=0)
        mean_var, _, _ = magnitude_variation(phis)
        G = gram_matrix(phis)
        toep_dev, _, _ = toeplitz_deviation(G)
        orbit_errors, _ = unitary_orbit_test(phis)
        orbit_err = max(orbit_errors) if orbit_errors else 0.0

        if verbose:
            print(f"    eps={eps:.1f}: mag_var={mean_var:.6f}, "
                  f"toep_dev={toep_dev:.6f}, orbit_err={orbit_err:.6f}")


def main():
    print("=" * 65)
    print("PW UNITARITY TEST: IS c-DEPENDENCE APPROXIMATELY UNITARY?")
    print("=" * 65)

    # --- d_clock = 3 tests ---
    print("\n" + "=" * 65)
    print("d_clock = 3 TESTS")
    print("=" * 65)

    for dims in [(3, 4), (3, 8), (3, 2, 2)]:
        run_test(dims, theta=1.0, clock_idx=0)
        run_test(dims, theta=0.0, clock_idx=0)

    # --- d_clock = 4 test ---
    print("\n" + "=" * 65)
    print("d_clock = 4 TEST")
    print("=" * 65)
    run_test((4, 4), theta=1.0, clock_idx=0)
    run_test((4, 2, 2), theta=1.0, clock_idx=0)

    # --- d_clock = 2 baseline ---
    print("\n" + "=" * 65)
    print("d_clock = 2 BASELINE (orbit test not applicable)")
    print("=" * 65)
    run_test((2, 2, 2), theta=1.0, clock_idx=0)

    # --- Weak coupling sweep ---
    run_weak_coupling_sweep()

    # --- Separable h test ---
    run_separable_h_test()

    # --- Summary ---
    print("\n" + "=" * 65)
    print("SUMMARY")
    print("=" * 65)
    print("""
Key findings:
- Magnitude variation: measures deviation from unitarity
  (unitary evolution preserves |phi_c(s)|, so mag_var should be ~0)
- Toeplitz deviation: measures deviation from Hamiltonian generation
  (G_{cc'} = g(c-c') iff evolution is generated by a single H)
- Orbit error: direct test of U|phi_c> = |phi_{c+1}>
- Phase linearity: whether phase_c(s) = H(s) * c

See exploration for interpretation.
""")


if __name__ == "__main__":
    main()
