"""Decoder coverage: exact MWPM table-lookup against the live lattice.

For every data qubit, inject a fault into RotatedSurfaceCodeLattice,
measure the syndrome arrays, and assert the decoder returns that exact
qubit for both correction channels. Also covers the clean (no-fault)
case and the unknown-syndrome (multi-error) fail-open behavior.
"""
import pytest

from triality_pipeline.error_mitigation.decoder import (
    MinimumWeightPerfectMatchingDecoder,
)
from triality_pipeline.error_mitigation.stabilizers import (
    RotatedSurfaceCodeLattice,
)


@pytest.fixture
def decoder():
    return MinimumWeightPerfectMatchingDecoder(lattice_distance=3)


@pytest.fixture
def lattice():
    lat = RotatedSurfaceCodeLattice()
    lat.clear_lattice_fabric()
    return lat


def test_clean_lattice_no_corrections(decoder, lattice):
    syndromes = lattice.measure_syndrome_array()
    plan = decoder.decode_syndrome_vectors(
        syndromes["vertex_z_syndromes"], syndromes["plaquette_x_syndromes"])
    assert plan == {"apply_x_restore": [], "apply_z_restore": []}
    assert decoder.process_closed_loop_stabilization(
        syndromes["vertex_z_syndromes"],
        syndromes["plaquette_x_syndromes"]) is False


@pytest.mark.parametrize("data_node", list(range(9)))
@pytest.mark.parametrize("error_type", ["X", "Z"])
def test_single_fault_exact_recovery(decoder, lattice, data_node, error_type,
                                     capsys):
    lattice.inject_phase_noise_fault(data_index=data_node,
                                     error_type=error_type)
    capsys.readouterr()  # silence the lattice's injection print
    syndromes = lattice.measure_syndrome_array()
    plan = decoder.decode_syndrome_vectors(
        syndromes["vertex_z_syndromes"], syndromes["plaquette_x_syndromes"])
    # The lattice flips the data sign, which both stabilizer types see:
    # the exact decoder must name the injected qubit on both channels.
    assert plan["apply_x_restore"] == [data_node]
    assert plan["apply_z_restore"] == [data_node]
    assert decoder.process_closed_loop_stabilization(
        syndromes["vertex_z_syndromes"],
        syndromes["plaquette_x_syndromes"]) is True


def test_unknown_syndrome_returns_no_correction(decoder):
    # Find a 4-bit pattern absent from both tables (multi-error signature).
    known = set(decoder._x_table) | set(decoder._z_table)
    unknown = next(k for k in
                   [tuple(int(b) for b in f"{i:04b}") for i in range(16)]
                   if k not in known and any(k))
    plan = decoder.decode_syndrome_vectors(list(unknown), list(unknown))
    assert plan == {"apply_x_restore": [], "apply_z_restore": []}
