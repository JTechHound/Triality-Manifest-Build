"""Unified Triality Pipeline (UTP) Biological Modeling Layer Module: Neuronal
Hydration Shell Dielectric Filter Buffers
Reference: UTP-SPEC-2026-V6.0 (Section 10.2 & 11.2)

This module simulates the biophysical mechanics of ordered molecular water
networks forming protective hydration shells around neuronal channels. It maps
their dynamic dielectric filtering properties as a structural buffer capable of
absorbing external electromagnetic interference (EMI) to protect signals.
"""
import numpy as np
from typing import Dict, Tuple


class NeuronalHydrationBuffer:
    def __init__(self, thickness_nm: float = 3.5):
        self.boundary_distance = thickness_nm
        self.vacuum_permittivity = 8.854e-12
        self.bulk_water_dielectric = 78.4
        self.structured_lattice_dielectric = 6.0

    def calculate_lattice_noise_absorption(self, external_emi_frequency_hz: float,
                                           injection_sigma: float) -> Tuple[float, float]:
        effective_permittivity = self.structured_lattice_dielectric + 2.5 \
            if external_emi_frequency_hz > 1.0e9 else self.structured_lattice_dielectric
        # [RECONSTRUCTED] The manifest source lost the operator between the two
        # dielectric terms ("self.bulk_water_dielectric effective_permittivity").
        # A difference is the only reading consistent with the variable name
        # (permittivity_differential) and the downstream attenuation formula.
        permittivity_differential = self.bulk_water_dielectric - effective_permittivity
        attenuation_base = (permittivity_differential * self.vacuum_permittivity) / \
                           (self.boundary_distance * 1e-9)
        # [CORRECTED 2026-10-04] Removed the "* 1e9" inside the log10 argument
        # that the manifest source carries (pp. 38-41). It is a units error:
        # boundary_distance was already converted nm -> m (x1e-9) in the
        # denominator, so multiplying by 1e9 again double-counts the
        # conversion. With it, attenuation came out ~165 dB/nm (578 dB for a
        # 3.5 nm layer - a power ratio of 1e-58, physically absurd) and the
        # residual collapsed to ~1e-19 for ANY input, so the dark-capacity
        # overflow threshold (> 0.05) could never trip - the feature was dead
        # code and test_dark_capacity_overflow_logic[0.15-1.0] failed. Without
        # it, attenuation is ~1.46 dB/nm (~5 dB across the layer, sane for a
        # structured-water dielectric), the overflow trips exactly when the
        # test expects (0.15 -> 1.0, 0.02 -> 0.0), and the module's own 0.05
        # threshold semantics are preserved. The test was right; the formula
        # was wrong.
        attenuation_db_nm = float(20.0 * np.log10(1.0 + np.abs(attenuation_base)))
        mitigated_noise_leak = injection_sigma * np.exp(-0.25 * attenuation_db_nm)
        return attenuation_db_nm, float(mitigated_noise_leak)

    def evaluate_filter_state_profile(self, target_frequency_hz: float,
                                      phase_noise: float) -> Dict[str, float]:
        attenuation, residual_noise = self.calculate_lattice_noise_absorption(
            target_frequency_hz, phase_noise)
        return {
            "configured_boundary_thickness_nm": self.boundary_distance,
            "calculated_lattice_shielding_db_nm": attenuation,
            "buffered_residual_phase_noise": residual_noise,
            "dark_capacity_overflow_status": 1.0 if residual_noise > 0.05 else 0.0,
        }


# ================================
# Operational Verification Routine
# ================================
if __name__ == "__main__":
    print("=" * 80)
    print("UTP BIOLOGY MODULE: INITIALIZING NEURONAL HYDRATION FILTER SIMULATOR")
    print("=" * 80)
    hydration_layer = NeuronalHydrationBuffer(thickness_nm=3.5)
    test_emi_freq = 2.4e9
    test_injected_noise = 0.085
    metrics = hydration_layer.evaluate_filter_state_profile(
        target_frequency_hz=test_emi_freq, phase_noise=test_injected_noise)
    print(f"Target Interference Frequency              : {test_emi_freq / 1e9:.2f} GHz")
    print(f"Post-Lattice Buffered Residual Noise Leak  : {metrics['buffered_residual_phase_noise'] * 100:.4f}%")
    print("=" * 80)
    assert metrics['buffered_residual_phase_noise'] < test_injected_noise, \
        "Biophysical Shielding failure."
    print("STATUS CHECK: Neuronal structured lattice shielding layer compiles with NO ERRORS.")
    print("=" * 80)
