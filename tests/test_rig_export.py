import numpy as np
import pytest

from service.bootstrap import qt_imported
from service.session import generate


def _mat(rows):
    return np.asarray(rows, dtype=np.float64)


def _lbs(rest, inverse_binds, joint_indices, weights, world_mats):
    rest = np.asarray(rest, dtype=np.float64)
    out = np.zeros_like(rest)
    for vi in range(rest.shape[0]):
        p = np.array([rest[vi, 0], rest[vi, 1], rest[vi, 2], 1.0], dtype=np.float64)
        acc = np.zeros(4, dtype=np.float64)
        for k in range(len(joint_indices[vi])):
            w = float(weights[vi][k])
            if w <= 0.0:
                continue
            j = int(joint_indices[vi][k])
            skin = world_mats[j] @ inverse_binds[j] @ p
            acc += w * skin
        out[vi] = acc[:3]
    return out


@pytest.mark.integration
def test_generate_include_rig_lbs_matches_pose_a_and_b():
    result = generate(
        {
            "height_cm": 170,
            "gender": 0.5,
            "include_rig": True,
            "pose_pair_id": "tpose-to-rest",
        }
    )
    assert "rig" in result
    rig = result["rig"]
    assert rig["schema"] == "human-rig.v1"
    assert rig["pose_pair"]["id"] == "tpose-to-rest"
    assert result["pose"]["id"] == "tpose"

    inv = [_mat(j["inverse_bind"]) for j in rig["joints"]]
    rest_g = [_mat(j["rest_global"]) for j in rig["joints"]]
    for ib, rg in zip(inv, rest_g):
        eye = ib @ rg
        assert np.max(np.abs(eye - np.eye(4))) <= 1e-5

    weights = np.asarray(rig["influences"]["weights"], dtype=np.float64)
    assert np.max(np.abs(weights.sum(axis=1) - 1.0)) <= 1e-5

    rest = rig["bind"]["rest_positions"]
    idx = rig["influences"]["joint_indices"]
    w = rig["influences"]["weights"]
    world_a = [_mat(m) for m in rig["poses"]["a"]["world_matrices"]]
    world_b = [_mat(m) for m in rig["poses"]["b"]["world_matrices"]]
    skinned_a = _lbs(rest, inv, idx, w, world_a)
    skinned_b = _lbs(rest, inv, idx, w, world_b)
    posed_a = np.asarray(rig["poses"]["a"]["posed_positions"], dtype=np.float64)
    posed_b = np.asarray(rig["poses"]["b"]["posed_positions"], dtype=np.float64)
    assert skinned_a.shape == posed_a.shape
    assert float(np.max(np.linalg.norm(skinned_a - posed_a, axis=1))) <= 1e-2
    assert float(np.max(np.linalg.norm(skinned_b - posed_b, axis=1))) <= 1e-2
    assert qt_imported() is False


@pytest.mark.integration
def test_generate_without_include_rig_omits_rig():
    result = generate({"pose": {"id": "rest"}})
    assert "rig" not in result
    assert result["pose"]["id"] == "rest"
