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
            "pose": {"id": "tpose"},
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


@pytest.mark.integration
def test_include_rig_obj_follows_requested_pose_endpoint():
    """Portal sends rest-to-tpose + pose tpose — OBJ must be T, not rest (pair A)."""
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "rest-to-tpose",
            "pose": {"id": "tpose"},
        }
    )
    assert result["pose"]["id"] == "tpose"
    posed_b = result["rig"]["poses"]["b"]["posed_positions"]
    # OBJ vertices are metres; compare a sample of positions to pose B.
    lines = [ln for ln in result["obj"].splitlines() if ln.startswith("v ")]
    assert len(lines) == len(posed_b)
    first = [float(x) for x in lines[0].split()[1:4]]
    assert first == pytest.approx(posed_b[0], abs=1e-6)


@pytest.mark.integration
def test_include_rig_default_obj_is_pair_a():
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "rest-to-tpose",
        }
    )
    assert result["pose"]["id"] == "rest"


@pytest.mark.integration
def test_rest_to_left_arm_up_moves_left_wrist():
    """MH UpperArmUpLeft* only touches face bones — pair must use real arm units."""
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "rest-to-left-arm-up",
            "pose": {"id": "rest"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "rest-to-left-arm-up"
    assert "UpperArmForwardLeft" in rig["poses"]["b"]["units"]
    names = [j["name"] for j in rig["joints"]]
    wrist = names.index("wrist.L")
    ta = np.asarray(rig["poses"]["a"]["world_matrices"][wrist], dtype=np.float64)[
        :3, 3
    ]
    tb = np.asarray(rig["poses"]["b"]["world_matrices"][wrist], dtype=np.float64)[
        :3, 3
    ]
    # metres; arm-up must lift/swing wrist by several centimetres (not ~0).
    assert float(np.linalg.norm(tb - ta)) >= 0.15


@pytest.mark.integration
def test_rest_to_torso_lean_moves_spine_and_head():
    """body-poseunits TorsoLeft targets spine1–4 — must alias to spine01–04."""
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "rest-to-torso-lean",
            "pose": {"id": "rest"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "rest-to-torso-lean"
    assert rig["pose_pair"]["version"] == "2"
    assert rig["poses"]["b"]["units"].get("TorsoLeft") == pytest.approx(0.9)
    names = [j["name"] for j in rig["joints"]]
    head = names.index("head")
    spine01 = names.index("spine01")
    ha = np.asarray(rig["poses"]["a"]["world_matrices"][head], dtype=np.float64)[:3, 3]
    hb = np.asarray(rig["poses"]["b"]["world_matrices"][head], dtype=np.float64)[:3, 3]
    sa = np.asarray(rig["poses"]["a"]["world_matrices"][spine01], dtype=np.float64)[:3, 3]
    sb = np.asarray(rig["poses"]["b"]["world_matrices"][spine01], dtype=np.float64)[:3, 3]
    assert float(np.linalg.norm(hb - ha)) >= 0.15
    assert float(np.linalg.norm(sb - sa)) >= 0.05


@pytest.mark.integration
def test_rest_to_left_knee_bend_moves_left_shin():
    """MH LowerLegBendLeft* miss shin bones — pair must move foot via lowerleg."""
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "rest-to-left-knee-bend",
            "pose": {"id": "rest"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "rest-to-left-knee-bend"
    assert rig["pose_pair"]["version"] == "2"
    assert "FootTurnOutLeft" in rig["poses"]["b"]["units"]
    assert "LowerLegBendLeft1" not in rig["poses"]["b"]["units"]
    names = [j["name"] for j in rig["joints"]]
    shin = names.index("lowerleg01.L")
    foot = names.index("foot.L")
    thigh = names.index("upperleg01.L")
    ra = np.asarray(rig["poses"]["a"]["world_matrices"][shin], dtype=np.float64)[
        :3, :3
    ]
    rb = np.asarray(rig["poses"]["b"]["world_matrices"][shin], dtype=np.float64)[
        :3, :3
    ]
    fa = np.asarray(rig["poses"]["a"]["world_matrices"][foot], dtype=np.float64)[
        :3, 3
    ]
    fb = np.asarray(rig["poses"]["b"]["world_matrices"][foot], dtype=np.float64)[
        :3, 3
    ]
    tha = np.asarray(rig["poses"]["a"]["world_matrices"][thigh], dtype=np.float64)[
        :3, :3
    ]
    thb = np.asarray(rig["poses"]["b"]["world_matrices"][thigh], dtype=np.float64)[
        :3, :3
    ]
    assert float(np.linalg.norm(rb - ra)) >= 0.3
    assert float(np.linalg.norm(fb - fa)) >= 0.15
    # upperleg.L alias → upperleg01.L so thigh rotates (joint origin stays)
    assert float(np.linalg.norm(thb - tha)) >= 0.2


@pytest.mark.integration
def test_tpose_to_left_arm_down_lowers_left_keeps_right():
    """B = tpose with left arm chain from rest — not UpperArmDownLeft on tpose."""
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "tpose-to-left-arm-down",
            "pose": {"id": "tpose"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "tpose-to-left-arm-down"
    assert rig["pose_pair"]["version"] == "2"
    names = [j["name"] for j in rig["joints"]]
    wrist_l = names.index("wrist.L")
    wrist_r = names.index("wrist.R")
    la = np.asarray(rig["poses"]["a"]["world_matrices"][wrist_l], dtype=np.float64)[
        :3, 3
    ]
    lb = np.asarray(rig["poses"]["b"]["world_matrices"][wrist_l], dtype=np.float64)[
        :3, 3
    ]
    ra = np.asarray(rig["poses"]["a"]["world_matrices"][wrist_r], dtype=np.float64)[
        :3, 3
    ]
    rb = np.asarray(rig["poses"]["b"]["world_matrices"][wrist_r], dtype=np.float64)[
        :3, 3
    ]
    # Left wrist drops toward A-pose side (Y-up).
    assert float(la[1] - lb[1]) >= 0.15
    assert float(np.linalg.norm(lb - la)) >= 0.2
    # Right wrist stays near T-pose.
    assert float(np.linalg.norm(rb - ra)) < 0.05


@pytest.mark.integration
def test_tpose_to_torso_lean_moves_spine_and_head():
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "tpose-to-torso-lean",
            "pose": {"id": "tpose"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "tpose-to-torso-lean"
    assert rig["poses"]["b"]["units"].get("TorsoLeft") == pytest.approx(0.9)
    names = [j["name"] for j in rig["joints"]]
    head = names.index("head")
    spine01 = names.index("spine01")
    ha = np.asarray(rig["poses"]["a"]["world_matrices"][head], dtype=np.float64)[:3, 3]
    hb = np.asarray(rig["poses"]["b"]["world_matrices"][head], dtype=np.float64)[:3, 3]
    sa = np.asarray(rig["poses"]["a"]["world_matrices"][spine01], dtype=np.float64)[:3, 3]
    sb = np.asarray(rig["poses"]["b"]["world_matrices"][spine01], dtype=np.float64)[:3, 3]
    assert float(np.linalg.norm(hb - ha)) >= 0.15
    assert float(np.linalg.norm(sb - sa)) >= 0.05


@pytest.mark.integration
def test_tpose_to_left_knee_bend_moves_left_shin():
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "tpose-to-left-knee-bend",
            "pose": {"id": "tpose"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "tpose-to-left-knee-bend"
    assert "FootTurnOutLeft" in rig["poses"]["b"]["units"]
    assert "UpperLegForwardLeft" in rig["poses"]["b"]["units"]
    names = [j["name"] for j in rig["joints"]]
    shin = names.index("lowerleg01.L")
    foot = names.index("foot.L")
    ra = np.asarray(rig["poses"]["a"]["world_matrices"][shin], dtype=np.float64)[
        :3, :3
    ]
    rb = np.asarray(rig["poses"]["b"]["world_matrices"][shin], dtype=np.float64)[
        :3, :3
    ]
    fa = np.asarray(rig["poses"]["a"]["world_matrices"][foot], dtype=np.float64)[
        :3, 3
    ]
    fb = np.asarray(rig["poses"]["b"]["world_matrices"][foot], dtype=np.float64)[
        :3, 3
    ]
    assert float(np.linalg.norm(rb - ra)) >= 0.3
    assert float(np.linalg.norm(fb - fa)) >= 0.15


@pytest.mark.integration
def test_tpose_to_left_kick_moves_left_foot():
    result = generate(
        {
            "height_cm": 170,
            "include_rig": True,
            "pose_pair_id": "tpose-to-left-kick",
            "pose": {"id": "tpose"},
        }
    )
    rig = result["rig"]
    assert rig["pose_pair"]["id"] == "tpose-to-left-kick"
    assert rig["pose_pair"]["version"] == "2"
    assert rig["poses"]["b"]["library_pose"] == "kick"
    names = [j["name"] for j in rig["joints"]]
    foot = names.index("foot.L")
    wrist_l = names.index("wrist.L")
    wrist_r = names.index("wrist.R")
    fa = np.asarray(rig["poses"]["a"]["world_matrices"][foot], dtype=np.float64)[
        :3, 3
    ]
    fb = np.asarray(rig["poses"]["b"]["world_matrices"][foot], dtype=np.float64)[
        :3, 3
    ]
    wla = np.asarray(rig["poses"]["a"]["world_matrices"][wrist_l], dtype=np.float64)[
        :3, 3
    ]
    wlb = np.asarray(rig["poses"]["b"]["world_matrices"][wrist_l], dtype=np.float64)[
        :3, 3
    ]
    wra = np.asarray(rig["poses"]["a"]["world_matrices"][wrist_r], dtype=np.float64)[
        :3, 3
    ]
    wrb = np.asarray(rig["poses"]["b"]["world_matrices"][wrist_r], dtype=np.float64)[
        :3, 3
    ]
    assert float(np.linalg.norm(fb - fa)) >= 0.2
    # Arms stay T-pose (not rest/A from kick BVH).
    assert float(np.linalg.norm(wlb - wla)) < 0.08
    assert float(np.linalg.norm(wrb - wra)) < 0.08

