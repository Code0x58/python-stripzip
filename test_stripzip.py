import os
import time
import zipfile
from subprocess import run

import pytest

from stripzip import cli, NonZipFileError, _zero_zip_date_time as strip


@pytest.fixture
def file(tmp_path_factory):
    path = tmp_path_factory.mktemp("file-") / "file.txt"
    path.write_text("hello")
    return path


@pytest.fixture
def g7z_factory(tmp_path_factory, file, request):
    default_options = {
        "x": "1",
        "m": "Deflate",
        "tc": "off",
    }

    def generate(*options):
        """Take a list of 7z -m parameters and use them to compress the input file."""
        opts = default_options.copy()
        opts.update(o.split("=", 1) for o in options)
        args = ["-m%s=%s" % i for i in opts.items()]
        out_file = tmp_path_factory.mktemp("zip-") / "archive.zip"
        run(["7z", "a", str(out_file), str(file)] + args, check=True)
        return out_file

    return generate


@pytest.fixture
def zip_factory(tmp_path_factory, file):
    """Generate a zip which varies by input modification time."""

    def generate():
        out_file = tmp_path_factory.mktemp("zip-") / "archive.zip"
        date_time = time.gmtime(file.stat().st_mtime)
        # strict_timestamp=False didn't work around this in 3.8
        date_time = time.struct_time((max(date_time.tm_year, 1980), *date_time[1:]))
        with zipfile.ZipFile(str(out_file), "w") as z:
            with z.open(zipfile.ZipInfo("file.txt", date_time), "w", force_zip64=False) as f:
                f.write(file.read_bytes())
        return out_file

    return generate


@pytest.fixture
def zip_creation_time_factory(g7z_factory):
    """Generate a zip which varies by input creation time."""

    def generate():
        return g7z_factory("tc=on")

    return generate


@pytest.fixture
def zip64_factory(tmp_path_factory, file):
    """Generate a zip which uses the 64bit extension."""

    def generate():
        out_file = tmp_path_factory.mktemp("zip-") / "archive.zip"
        date_time = time.gmtime(file.stat().st_mtime)
        # strict_timestamp=False didn't work around this in 3.8
        date_time = time.struct_time((max(date_time.tm_year, 1980), *date_time[1:]))
        with zipfile.ZipFile(str(out_file), "w") as z:
            with z.open(zipfile.ZipInfo("file.txt", date_time), "w", force_zip64=True) as f:
                f.write(file.read_bytes())
        return out_file

    return generate


@pytest.fixture
def zip_comment_factory(tmp_path_factory, file):
    """Generate a zip which contains extended data."""

    def generate():
        out_file = tmp_path_factory.mktemp("zip-") / "archive.zip"
        comment = "comment: %s" % file.stat().st_mtime_ns
        run(["zip", "-X", "--archive-comment", str(out_file), str(file)], input=comment.encode(),
            check=True)
        return out_file

    return generate


@pytest.fixture
def zip_extended_factory(tmp_path_factory, file):
    """Generate a zip which contains extended data."""

    def generate():
        out_file = tmp_path_factory.mktemp("zip-") / "archive.zip"
        run(["zip", "-X-", str(out_file), str(file)], check=True)
        return out_file

    return generate


def test_zip_not_zip64(zip_factory, zip64_factory, file):
    """Sanity check that zip and zip64 are not identical."""
    deflate = zip_factory()
    deflate64 = zip64_factory()
    assert deflate.read_bytes() != deflate64.read_bytes()


def check_strip(factory, file):
    """Check that the inputs vary with timestamps, but have same outputs."""

    def make_archive_and_stripped():
        """Return an archive before and after stripping."""
        archive = factory()
        archive_bak = archive.with_suffix(".zip.bak")
        archive_bak.write_bytes(archive.read_bytes())
        with archive.open("r+b") as f:
            strip(f)
        return archive_bak, archive

    archive1, stripped1 = make_archive_and_stripped()
    os.utime(str(file), (0, 0))
    archive2, stripped2 = make_archive_and_stripped()

    assert archive1.read_bytes() != archive2.read_bytes()
    assert stripped1.read_bytes() == stripped2.read_bytes()


def test_strip_zip(zip_factory, file):
    check_strip(zip_factory, file)


@pytest.mark.xfail(reason="stripped archives differ even without updating input file", strict=True)
def test_strip_zip_creation_time(zip_creation_time_factory, file):
    check_strip(zip_creation_time_factory, file)


def test_strip_zip64(zip64_factory, file):
    check_strip(zip64_factory, file)


def test_strip_zip_extended(zip_extended_factory, file):
    check_strip(zip_extended_factory, file)


@pytest.mark.xfail(reason="comments are not stripped", strict=True)
def test_strip_zip_comment(zip_comment_factory, file):
    check_strip(zip_comment_factory, file)


def test_strip_junk(file):
    """Non-zip file input raises an exception."""
    with pytest.raises(NonZipFileError):
        strip(file.open("r+b"))


def test_cli(zip_factory, file):
    """CLI exits when given invalid input."""
    archive = zip_factory()
    cli([str(archive)])

    with pytest.raises(SystemExit):
        cli([])

    with pytest.raises(SystemExit):
        cli([str(file)])
