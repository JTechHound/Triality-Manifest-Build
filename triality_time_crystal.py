"""
Recursive Triadic Fractal Network - Time Crystal Visualizer.

Source: Recursive_Triadic_fractal_network.pdf (2026-10-03).
Transcribed 2026-10-03; indentation reconstructed from the PDF text
(extraction strips it). Repairs, all marked [REPAIRED]/[ADDED]:
  - [REPAIRED] `self.t += dt` appeared twice around a page break (once at the
    end of rk4_step, once stray at module level where `self` is undefined).
    Kept a single increment inside rk4_step.
  - [REPAIRED] duplicate 'Symmetry Shifting Edges' legend entry (listed twice).
  - [ADDED] `if __name__ == "__main__":` guard around the driver so the module
    is importable for testing (source ran everything at top level).
Validated: 729 nodes / 1092 edges built; 500 RK4 steps keep every state on
the unit sphere (max |norm-1| < 1e-12), no NaNs, t advances exactly dt/step;
headless render of update_visualization produces a valid frame.
Requires: numpy, networkx, matplotlib.
"""
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.lines import Line2D


class TrialityTimeCrystalSimulator:
    def __init__(self, N=729, omega_ctc=9.0, kappa=0.5):
        self.N = N
        self.omega_ctc = omega_ctc  # Digital root frequency anchor
        self.kappa = kappa  # Dissipative coupling constant
        self.dt = 0.05  # Time step for RK4 integration
        self.t = 0.0

        # 1. Generate the Scale-Invariant Fractal Geometry
        self.pos = {}
        self._generate_fractal_layout(list(range(1, N + 1)), np.array([0.0, 0.0]), 10.0)
        # 2. Build Sparse Hierarchical Network Graph
        self.G = nx.DiGraph()
        self.G.add_nodes_from(range(1, N + 1))
        self._build_sparse_triadic_edges(list(range(1, N + 1)))
        # 3. Initialize Semiclassical Collective Spin States (mx, my, mz)
        # Each node tracks its local 3-vector expectation value
        self.states = np.zeros((N, 3))
        # Seed with a slightly perturbed state near the global axis
        self.states[:, 0] = 0.1 * np.sin(range(N))  # mx
        self.states[:, 1] = 0.1 * np.cos(range(N))  # my
        self.states[:, 2] = 1.0  # mz (Ground state alignment)

    def _generate_fractal_layout(self, current_nodes, center, radius):
        """Recursively maps out nested 3-node clusters down to the base pixel."""
        if len(current_nodes) == 1:
            self.pos[current_nodes[0]] = center
            return
        group_size = len(current_nodes) // 3
        angles = np.radians([90, 210, 330])  # Classical 120-degree triadic symmetry
        for i in range(3):
            sub_group = current_nodes[i * group_size:(i + 1) * group_size]
            if len(sub_group) > 0:
                sub_center = center + radius * np.array([np.cos(angles[i]), np.sin(angles[i])])
                self._generate_fractal_layout(sub_group, sub_center, radius * 0.38)

    def _build_sparse_triadic_edges(self, nodes):
        """Establishes flux channels matching the multi-tiered fractal layout structure."""
        if len(nodes) <= 1:
            return
        sz = len(nodes) // 3
        g1, g2, g3 = nodes[:sz], nodes[sz:2 * sz], nodes[2 * sz:]
        # Phase-locked directional loops across the current generation boundaries
        if len(g1) > 0 and len(g2) > 0:
            self.G.add_edge(g1[0], g2[0])
        if len(g2) > 0 and len(g3) > 0:
            self.G.add_edge(g2[0], g3[0])
        if len(g3) > 0 and len(g1) > 0:
            self.G.add_edge(g3[0], g1[0])
        self._build_sparse_triadic_edges(g1)
        self._build_sparse_triadic_edges(g2)
        self._build_sparse_triadic_edges(g3)

    def derivatives(self, states):
        """Vectorized evaluation of the dissipative mean-field Lindblad master equation."""
        mx, my, mz = states[:, 0], states[:, 1], states[:, 2]
        dstatedt = np.zeros_like(states)
        # Units and latency adjustments mimicking phase-retarded interactions
        dstatedt[:, 0] = -self.omega_ctc * my - self.kappa * mx * mz
        dstatedt[:, 1] = self.omega_ctc * mx - self.kappa * my * mz
        dstatedt[:, 2] = self.kappa * (mx**2 + my**2)
        # Self-correcting trace/Hermitian re-orthogonalization constraint (The 9 Axis)
        # Prevents numeric drift from compounding across high-N iterations
        norms = np.linalg.norm(dstatedt, axis=1, keepdims=True)
        dstatedt = np.where(norms > 10.0, (dstatedt / (norms + 1e-6)) * 10.0, dstatedt)
        return dstatedt

    def rk4_step(self):
        """Executes a Fourth-Order Runge-Kutta time-stepping iteration."""
        y = self.states
        dt = self.dt
        k1 = self.derivatives(y)
        k2 = self.derivatives(y + 0.5 * dt * k1)
        k3 = self.derivatives(y + 0.5 * dt * k2)
        k4 = self.derivatives(y + dt * k3)
        self.states = y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        # Strict global boundary enforcement: project back onto the unit Bloch sphere
        state_norms = np.linalg.norm(self.states, axis=1, keepdims=True)
        self.states /= (state_norms + 1e-12)
        # [REPAIRED] source had this line twice across a page break; kept once.
        self.t += dt


# --- Initialize Simulator Instance ---
# [ADDED] __main__ guard so the module can be imported for testing.
if __name__ == "__main__":
    sim = TrialityTimeCrystalSimulator(N=729, omega_ctc=9.0, kappa=0.4)
    # Setup high-performance dark-mode display frame
    fig, ax = plt.subplots(figsize=(11, 11), facecolor='#090D16')
    ax.set_facecolor('#090D16')
    # Extract coordinates for drawing
    nodes_list = list(sim.G.nodes())
    edges_list = list(sim.G.edges())
    pos_array = np.array([sim.pos[n] for n in nodes_list])
    # Optimized rendering scatter plot for N=729 nodes
    node_scatter = ax.scatter(
        pos_array[:, 0], pos_array[:, 1],
        s=18, c='#38BDF8', edgecolors='none', zorder=4, alpha=0.9
    )
    # Initialize lines array for edge flux visualization
    edge_lines = []
    for u, v in edges_list:
        p1, p2 = sim.pos[u], sim.pos[v]
        line, = ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#F59E0B', lw=0.6, alpha=0.15, zorder=2)
        edge_lines.append(line)

    def update_visualization(frame):
        # Step the physics engine forward via RK4
        sim.rk4_step()
        # Map the internal expectations into a visual pulsing parameter
        mx_amplitudes = sim.states[:, 0]
        my_amplitudes = sim.states[:, 1]
        # 1. Update Node Colors and Intensities via Phase Shift
        intensities = 0.5 + 0.5 * np.sin(sim.omega_ctc * sim.t + mx_amplitudes * 2.0)
        colors = plt.cm.plasma(intensities)  # Plasma map shifts cleanly from Indigo to Yellow
        node_scatter.set_facecolors(colors)
        # 2. Update Edge Colors to show Phase-Retarded Energy Flux pulsing
        for idx, (u, v) in enumerate(edges_list):
            # Calculate local difference in coupling alignment
            phase_diff = np.abs(mx_amplitudes[u - 1] - my_amplitudes[v - 1])
            pulse_alpha = 0.1 + 0.6 * np.sin(sim.omega_ctc * sim.t - phase_diff)
            pulse_alpha = np.clip(pulse_alpha, 0.05, 0.8)
            edge_lines[idx].set_alpha(pulse_alpha)
            # Shift colors along the fire spectrum as the flux surges
            if pulse_alpha > 0.4:
                edge_lines[idx].set_color('#EF4444')  # High-energy operational flux (Red)
            else:
                edge_lines[idx].set_color('#F59E0B')  # Baseline structural flux (Amber)
        return [node_scatter] + edge_lines

    # Build the structural annotation legends
    # [REPAIRED] source listed 'Symmetry Shifting Edges' twice; deduped.
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Lattice Nodes (N=729)',
               markerfacecolor='#EC4899', markersize=8),
        Line2D([0], [0], color='#F59E0B', lw=1.5, label='Symmetry Shifting Edges'),
        Line2D([0], [0], color='#EF4444', lw=1.5, label='Active RK4 Phase-Lock Flux')
    ]
    ax.legend(handles=legend_elements, loc='upper right', facecolor='#111827',
              edgecolor='#1F2937', labelcolor='w')
    ax.set_title(f"Macroscopic Continuous Time Crystal Phase ($N={sim.N}$ Nodes)\n"
                 "Vectorized RK4 Master Equation Integration",
                 color='#FFFFFF', fontsize=14, fontweight='bold', pad=15)
    plt.axis('off')
    plt.tight_layout()
    # Initialize the live structural frame loops
    ani = animation.FuncAnimation(fig, update_visualization, frames=200, interval=30, blit=True)
    plt.show()
