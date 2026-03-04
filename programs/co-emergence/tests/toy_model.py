"""
Generalized co-emergence toy model for arbitrary tensor product structures.

Supports N = prod(dims) smooth structures on S = S_1 x S_2 x ... x S_k,
where dims = (d_1, d_2, ..., d_k).

Refactored from the N=4 model (2026-03-04-toy-model.py) to support:
- Arbitrary tensor product structures (N=4, 8, 16, ...)
- Partial traces of pure states and density matrices
- Multiple subsystem marginals and couplings

Reference: programs/co-emergence/index.tex, Section 3.6 and Open Problem 2.
"""

import numpy as np
from scipy.optimize import root


class CoEmergenceModel:
    """Self-consistency model on a tensor product configuration space.

    Parameters
    ----------
    dims : tuple of int
        Dimensions of each subsystem. N = prod(dims).
    h : ndarray of shape (N,)
        External field (intrinsic curvature per smooth structure).
    alphas : list of float
        Marginal coupling for each subsystem.
    beta : float
        Hartree self-coupling.
    gamma : complex
        Weight exponent. gamma = -1 + i*theta.
    """

    def __init__(self, dims, h, alphas, beta, gamma):
        self.dims = tuple(dims)
        self.N = int(np.prod(self.dims))
        self.n_subsystems = len(self.dims)
        self.h = np.asarray(h, dtype=complex).ravel()
        assert self.h.shape == (self.N,), f"h has shape {self.h.shape}, expected ({self.N},)"
        assert len(alphas) == self.n_subsystems
        self.alphas = list(alphas)
        self.beta = beta
        self.gamma = gamma

    def marginals(self, psi):
        """Compute M_j(i) = sum_{sigma: sigma_j=i} |psi_sigma|^2 for each subsystem j.

        Returns list of arrays, one per subsystem.
        """
        psi2 = np.abs(psi) ** 2
        psi_tensor = psi2.reshape(self.dims)
        result = []
        for j in range(self.n_subsystems):
            # Sum over all axes except j
            axes = tuple(k for k in range(self.n_subsystems) if k != j)
            result.append(psi_tensor.sum(axis=axes))
        return result

    def curvature(self, psi):
        """Mean-field curvature R_sigma(psi) for all sigma.

        R_sigma = h_sigma + sum_j alpha_j * M_j(sigma_j) + beta * |psi_sigma|^2
        """
        psi2 = np.abs(psi) ** 2
        margs = self.marginals(psi)

        # Build the marginal contribution as a tensor, then flatten
        R_tensor = self.h.reshape(self.dims).copy()
        for j, (alpha_j, marg_j) in enumerate(zip(self.alphas, margs)):
            # Broadcast marg_j along axis j
            shape = [1] * self.n_subsystems
            shape[j] = self.dims[j]
            R_tensor = R_tensor + alpha_j * marg_j.reshape(shape)

        R = R_tensor.ravel() + self.beta * psi2
        return R

    def weights(self, psi):
        """Weight function w_sigma = exp(gamma * R_sigma)."""
        R = self.curvature(psi)
        return np.exp(self.gamma * R)

    def F_map(self, psi):
        """Self-consistency map F(psi) = w(psi) / ||w(psi)||_2."""
        w = self.weights(psi)
        norm = np.linalg.norm(w)
        if norm < 1e-30:
            return psi.copy()
        return w / norm

    def find_fixed_point(self, psi0=None, max_iter=50000, tol=1e-12):
        """Find fixed point by direct iteration.

        Returns (psi, error, iterations).
        """
        if psi0 is None:
            psi0 = np.random.randn(self.N) + 1j * np.random.randn(self.N)
            psi0 /= np.linalg.norm(psi0)

        psi = psi0.copy()
        err = np.inf
        for i in range(max_iter):
            psi_new = self.F_map(psi)
            err = self.rho_distance(psi_new, psi)
            if err < tol:
                return psi_new, err, i + 1
            psi = psi_new
        return psi, err, max_iter

    def find_fixed_point_root(self, psi0=None):
        """Find fixed point via scipy.optimize.root."""
        if psi0 is None:
            psi0 = np.random.randn(self.N) + 1j * np.random.randn(self.N)
            psi0 /= np.linalg.norm(psi0)

        def residual(x):
            psi = x[: self.N] + 1j * x[self.N :]
            psi /= np.linalg.norm(psi)
            Fpsi = self.F_map(psi)
            phase = np.exp(-1j * np.angle(psi[0]))
            psi = psi * phase
            Fpsi = Fpsi * phase
            diff = Fpsi - psi
            return np.concatenate([diff.real, diff.imag])

        x0 = np.concatenate([psi0.real, psi0.imag])
        sol = root(residual, x0, method="hybr", tol=1e-14)
        psi_sol = sol.x[: self.N] + 1j * sol.x[self.N :]
        psi_sol /= np.linalg.norm(psi_sol)
        err = self.rho_distance(self.F_map(psi_sol), psi_sol)
        return psi_sol, err, sol.success

    def find_fixed_points(self, n_starts=20):
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
            psi, err, _ = self.find_fixed_point()
            try_add(psi, err)

        for _ in range(n_starts // 2):
            psi, err, _ = self.find_fixed_point_root()
            try_add(psi, err)

        return fps

    @staticmethod
    def partial_trace(psi, dims, keep):
        """Partial trace of a pure state: Tr_{others}(|psi><psi|).

        Parameters
        ----------
        psi : ndarray of shape (prod(dims),)
        dims : tuple of int
        keep : tuple of int
            Indices of subsystems to keep.

        Returns
        -------
        rho : ndarray of shape (d_keep, d_keep) where d_keep = prod(dims[k] for k in keep)
        """
        keep = tuple(sorted(keep))
        n = len(dims)
        psi_tensor = psi.reshape(dims)

        # Axes to trace out
        trace_axes = tuple(k for k in range(n) if k not in keep)

        # rho_{i,j} = sum_{traced} psi_{...i...} * psi*_{...j...}
        # Use einsum: psi has indices 0..n-1, psi* has indices n..2n-1
        # Contract traced axes: k and n+k for k in trace_axes
        # Free axes: k for keep (bra) and n+k for keep (ket)

        psi_conj = psi_tensor.conj()

        # Build einsum subscripts
        bra_indices = list(range(n))
        ket_indices = list(range(n, 2 * n))

        # For traced axes, ket index = bra index (contraction)
        for k in trace_axes:
            ket_indices[k] = bra_indices[k]

        # Output indices: kept bra indices, then kept ket indices
        out_indices = [bra_indices[k] for k in keep] + [ket_indices[k] for k in keep]

        rho = np.einsum(psi_tensor, bra_indices, psi_conj, ket_indices, out_indices)

        d_keep = int(np.prod([dims[k] for k in keep]))
        return rho.reshape(d_keep, d_keep)

    @staticmethod
    def partial_trace_dm(rho, dims, keep):
        """Partial trace of a density matrix.

        Parameters
        ----------
        rho : ndarray of shape (D, D) where D = prod(dims)
        dims : tuple of int
        keep : tuple of int
            Indices of subsystems to keep.

        Returns
        -------
        rho_reduced : ndarray of shape (d_keep, d_keep)
        """
        keep = tuple(sorted(keep))
        n = len(dims)

        # Reshape rho into tensor with 2n indices: (d0, d1, ..., d_{n-1}, d0, d1, ..., d_{n-1})
        rho_tensor = rho.reshape(dims + dims)

        # Trace over non-kept axes: contract axis k with axis n+k
        trace_axes = sorted([k for k in range(n) if k not in keep], reverse=True)

        result = rho_tensor
        # We need to trace pairs. Use einsum for clarity.
        bra_indices = list(range(n))
        ket_indices = list(range(n, 2 * n))

        for k in trace_axes:
            ket_indices[k] = bra_indices[k]  # contract

        out_indices = [bra_indices[k] for k in keep] + [ket_indices[k] for k in keep]

        result = np.einsum(rho_tensor, bra_indices + ket_indices, out_indices)

        d_keep = int(np.prod([dims[k] for k in keep]))
        return result.reshape(d_keep, d_keep)

    @staticmethod
    def rho_distance(psi_a, psi_b):
        """Phase-invariant distance: ||rho(a) - rho(b)||_F."""
        rho_a = np.outer(psi_a, psi_a.conj())
        rho_b = np.outer(psi_b, psi_b.conj())
        return np.linalg.norm(rho_a - rho_b)

    def jacobian_numerical(self, psi, eps=1e-7):
        """Numerical Jacobian of F at psi in real coordinates."""
        n = len(psi)
        x = np.concatenate([psi.real, psi.imag])
        f0 = self.F_map(psi)
        f0_real = np.concatenate([f0.real, f0.imag])
        J = np.zeros((2 * n, 2 * n))

        for i in range(2 * n):
            x_p = x.copy()
            x_p[i] += eps
            psi_p = x_p[:n] + 1j * x_p[n:]
            f_p = self.F_map(psi_p)
            J[:, i] = (np.concatenate([f_p.real, f_p.imag]) - f0_real) / eps

        return J

    def spectral_radius(self, psi):
        """Spectral radius of dF at a fixed point."""
        J = self.jacobian_numerical(psi)
        eigenvalues = np.linalg.eigvals(J)
        return np.max(np.abs(eigenvalues))
