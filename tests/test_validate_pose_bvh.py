from pathlib import Path

import pytest

from service.pose_bvh_validate import validate_pose_bvh_file

_REPO = Path(__file__).resolve().parents[1]
_TPOSE = _REPO / "makehuman" / "data" / "poses" / "tpose.bvh"

_MINIMAL_BAD_BVH = """\
HIERARCHY
ROOT root
{
\tOFFSET 0 0 0
\tCHANNELS 6 Xposition Yposition Zposition Xrotation Yrotation Zrotation
\tJOINT pelvis.L
\t{
\t\tOFFSET 0 0 0
\t\tCHANNELS 3 Xrotation Yrotation Zrotation
\t\tEnd Site
\t\t{
\t\t\tOFFSET 0 0.1 0
\t\t}
\t}
}
MOTION
Frames: 1
Frame Time: 0.033333
0 0 0 0 0 0 0 0 0
"""


@pytest.mark.integration
@pytest.mark.skipif(not _TPOSE.is_file(), reason="bundled tpose.bvh not present locally")
def test_validate_tpose_bvh_passes():
    result = validate_pose_bvh_file(_TPOSE)
    assert result.ok, result.errors
    assert not result.errors


def test_validate_missing_file_fails():
    result = validate_pose_bvh_file(_REPO / "makehuman" / "data" / "poses" / "not-a-pose.bvh")
    assert not result.ok
    assert any("not found" in item for item in result.errors)


def test_validate_wrong_rig_fails(tmp_path: Path):
    bad = tmp_path / "wrong-rig.bvh"
    bad.write_text(_MINIMAL_BAD_BVH, encoding="utf-8")
    result = validate_pose_bvh_file(bad)
    assert not result.ok
    assert result.errors
