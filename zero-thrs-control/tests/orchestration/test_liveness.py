import os
from contextlib import nullcontext as assert_does_not_raise
from pathlib import Path
from tempfile import NamedTemporaryFile

from thrs.runtime.liveness import Liveness


def test_liveness_no_error():
    liveness = Liveness(Path("/tmp/does_not_exist"))  # noqa: S108

    with assert_does_not_raise():
        liveness.signal()


def test_liveness_updates_timestamp():
    with NamedTemporaryFile() as tempfile:
        tempfile_path = Path(tempfile.name)
        os.utime(tempfile_path, (0, 0))
        mtime = tempfile_path.stat().st_mtime

        liveness = Liveness(tempfile_path)
        liveness.signal()

        stat = tempfile_path.stat()
        assert stat.st_mtime != mtime
