import os
from contextlib import nullcontext as assert_does_not_raise
from tempfile import NamedTemporaryFile

from thrs.runtime.liveness import Liveness


def test_liveness_no_error():
    liveness = Liveness("/tmp/does_not_exist")

    with assert_does_not_raise:
        liveness.signal()


def test_liveness_updates_timestamp():
    with NamedTemporaryFile() as tempfile:
        os.utime(tempfile.name, (0, 0))
        mtime = os.stat(tempfile.name).st_mtime

        liveness = Liveness(tempfile.name)
        liveness.signal()

        stat = os.stat(tempfile.name)
        assert stat.st_mtime != mtime
