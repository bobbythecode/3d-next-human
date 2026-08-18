import numpy as np
import pytest

from service.mesh_export import export_basemesh, fan_triangles, place_feet_on_ground, scale_dm_to_m


def test_scale_divides_by_ten():
    scaled = scale_dm_to_m(np.array([[10.0, 17.2, 0.0]]))
    np.testing.assert_allclose(scaled[0], [1.0, 1.72, 0.0])


def test_fan_triangles_quad_and_stored_triangle():
    assert fan_triangles([0, 1, 2, 3]) == [(0, 1, 2), (0, 2, 3)]
    assert fan_triangles([0, 1, 2, 0]) == [(0, 1, 2)]


def test_export_obj_is_metres_triangles_and_skips_masked():
    coords = np.array(
        [
            [0.0, 0.0, 0.0],
            [10.0, 0.0, 0.0],
            [10.0, 10.0, 0.0],
            [0.0, 10.0, 0.0],
        ],
        dtype=np.float64,
    )
    fvert = np.array([[0, 1, 2, 3], [0, 1, 2, 0]], dtype=np.int32)
    mask = np.array([True, False])
    obj = export_basemesh(coords, fvert, mask)
    assert "v 1.000000 1.000000 0.000000" in obj
    assert "f 1 2 3" in obj
    assert "f 1 3 4" in obj
    faces = [line for line in obj.splitlines() if line.startswith("f ")]
    assert len(faces) == 2


def test_export_rejects_all_masked():
    coords = np.zeros((3, 3))
    fvert = np.array([[0, 1, 2, 0]])
    with pytest.raises(ValueError, match="triangle"):
        export_basemesh(coords, fvert, np.array([False]))


def test_place_feet_on_ground_subtracts_lowest_used_y():
    coords = np.array([[0.0, 5.0, 0.0], [1.0, 8.0, 0.0], [0.0, 99.0, 0.0]])
    shifted = place_feet_on_ground(coords, [0, 1])
    np.testing.assert_allclose(shifted[0, 1], 0.0)
    np.testing.assert_allclose(shifted[1, 1], 3.0)
    np.testing.assert_allclose(shifted[2, 1], 94.0)


def test_export_puts_feet_on_ground_and_drops_helpers():
    coords = np.array(
        [
            [0.0, 5.0, 0.0],
            [10.0, 5.0, 0.0],
            [10.0, 15.0, 0.0],
            [0.0, 15.0, 0.0],
            [0.0, 99.0, 0.0],
        ],
        dtype=np.float64,
    )
    fvert = np.array([[0, 1, 2, 3], [4, 4, 4, 4]], dtype=np.int32)
    mask = np.array([True, False])
    obj = export_basemesh(coords, fvert, mask)
    ys = [float(line.split()[2]) for line in obj.splitlines() if line.startswith("v ")]
    assert min(ys) == pytest.approx(0.0)
    assert max(ys) == pytest.approx(1.0)
    assert len(ys) == 4
    assert "9.900000" not in obj
