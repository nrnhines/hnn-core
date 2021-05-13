import pytest

from neuron import h

from hnn_core.cells_default import pyramidal, basket
from hnn_core.cell import Cell
from hnn_core.network_builder import load_custom_mechanisms


def test_cells_default():
    """Test default cell objects."""
    load_custom_mechanisms()

    with pytest.raises(ValueError, match='Unknown pyramidal cell type'):
        p_secs, p_syn, topology, sect_loc = pyramidal(cell_name='blah')

    p_secs, p_syn, topology, sect_loc = pyramidal(cell_name='L5Pyr')
    l5p = Cell(name='L5Pyr', pos=(0, 0, 0))
    l5p.build(p_secs, p_syn, topology, sect_loc=sect_loc)
    l5p.insert_dipole(p_secs, 'apical_trunk')
    assert len(l5p.sections) == 9
    assert 'apical_2' in l5p.sections

    # smoke test to check if cell can be used in simulation
    h.load_file("stdrun.hoc")
    h.tstop = 40
    h.dt = 0.025
    h.celsius = 37

    vsoma = l5p.rec_v.record(l5p.sections['soma'](0.5)._ref_v)
    times = h.Vector().record(h._ref_t)

    stim = h.IClamp(l5p.sections['soma'](0.5))
    stim.delay = 5
    stim.dur = 5.
    stim.amp = 2.

    h.finitialize()
    h.fcurrent()
    h.run()

    times = times.to_python()
    vsoma = vsoma.to_python()
    assert len(times) == len(vsoma)

    with pytest.raises(ValueError, match='Unknown basket cell type'):
        p_secs, p_syn, topology, sect_loc = basket(cell_name='blah')