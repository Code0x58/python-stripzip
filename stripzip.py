import argparse
import mmap
import os
import sys
from struct import Struct


class NonZipFileError(ValueError):
    """Raised when a given file does not appear to be a zip"""


ZIP64_EXTRA_DATA_ID = 0x0001


def _zero_zip_date_time(zip_):
    def purify_extra_data(mm, offset, length):
        extra_header_struct = Struct("<HH")
        # 0. id
        # 1. length
        STRIPZIP_OPTION_HEADER = 0xFFFF
        EXTENDED_TIME_DATA = 0x5455
        # Some sort of extended time data, see
        # ftp://ftp.info-zip.org/pub/infozip/src/zip30.zip ./proginfo/extrafld.txt
        # fallthrough
        UNIX_EXTRA_DATA = 0x7875
        # Unix extra data; UID / GID stuff, see
        # ftp://ftp.info-zip.org/pub/infozip/src/zip30.zip ./proginfo/extrafld.txt
        mlen = offset + length

        while offset < mlen:
            values = list(extra_header_struct.unpack_from(mm, offset))
            _, header_length = values
            extra_struct = Struct("<HH" + "B"*header_length)
            values = list(extra_struct.unpack_from(mm, offset))
            header_id, header_length, rest = values[0], values[1], values[2:]

            if header_id in (EXTENDED_TIME_DATA, UNIX_EXTRA_DATA):
                values[0] = STRIPZIP_OPTION_HEADER
                for i in range(2, len(values)):
                    values[i] = 0xff
                extra_struct.pack_into(mm, offset, *values)
            elif header_id == ZIP64_EXTRA_DATA_ID:
                # The Zip64 block must stay intact so the parser can recover
                # compressed/uncompressed sizes stored there for large files.
                pass
            elif header_id != STRIPZIP_OPTION_HEADER:
                return False

            offset += extra_header_struct.size + header_length

        return True

    def _read_zip64_sizes(mm, offset, length, compressed_size, uncompressed_size):
        """Return actual compressed/uncompressed sizes from a Zip64 extra field."""
        extra_header_struct = Struct("<HH")
        end = offset + length
        while offset < end:
            header_id, header_length = extra_header_struct.unpack_from(mm, offset)
            offset += extra_header_struct.size
            if header_id == ZIP64_EXTRA_DATA_ID:
                data_offset = offset
                if uncompressed_size == 0xFFFFFFFF:
                    uncompressed_size = int.from_bytes(mm[data_offset:data_offset + 8], "little")
                    data_offset += 8
                if compressed_size == 0xFFFFFFFF:
                    compressed_size = int.from_bytes(mm[data_offset:data_offset + 8], "little")
                break
            offset += header_length
        return compressed_size, uncompressed_size

    FILE_HEADER_SIGNATURE = 0x04034b50
    CENDIR_HEADER_SIGNATURE = 0x02014b50

    archive_size = os.fstat(zip_.fileno()).st_size
    signature_struct = Struct("<L")
    local_file_header_struct = Struct("<LHHHHHLLLHH")
    # 0. L signature
    # 1. H version_needed
    # 2. H gp_bits
    # 3. H compression_method
    # 4. H last_mod_time
    # 5. H last_mod_date
    # 6. L crc32
    # 7. L compressed_size
    # 8. L uncompressed_size
    # 9. H name_length
    # 10. H extra_field_length
    central_directory_header_struct = Struct("<LHHHHHHLLLHHHHHLL")
    # 0. L signature
    # 1. H version_made_by
    # 2. H version_needed
    # 3. H gp_bits
    # 4. H compression_method
    # 5. H last_mod_time
    # 6. H last_mod_date
    # 7. L crc32
    # 8. L compressed_size
    # 9. L uncompressed_size
    # 10. H file_name_length
    # 11. H extra_field_length
    # 12. H file_comment_length
    # 13. H disk_number_start
    # 14. H internal_attr
    # 15. L external_attr
    # 16. L rel_offset_local_header
    offset = 0

    mm = mmap.mmap(zip_.fileno(), 0)
    while offset < archive_size:
        if signature_struct.unpack_from(mm, offset) != (FILE_HEADER_SIGNATURE,):
            break
        values = list(local_file_header_struct.unpack_from(mm, offset))
        (
            _,
            _,
            _,
            _,
            _,
            _,
            _,
            compressed_size,
            uncompressed_size,
            name_length,
            extra_field_length,
        ) = values
        # reset last_mod_time
        values[4] = 0
        # reset last_mod_date
        values[5] = 0x21
        local_file_header_struct.pack_into(mm, offset, *values)
        offset += local_file_header_struct.size + name_length
        extra_offset = offset
        offset += extra_field_length
        if extra_field_length != 0:
            purify_extra_data(mm, extra_offset, extra_field_length)
            compressed_size, uncompressed_size = _read_zip64_sizes(
                mm, extra_offset, extra_field_length, compressed_size, uncompressed_size
            )
        offset += compressed_size

    while offset < archive_size:
        if signature_struct.unpack_from(mm, offset) != (CENDIR_HEADER_SIGNATURE,):
            break
        values = list(central_directory_header_struct.unpack_from(mm, offset))
        _, _, _, _, _, _, _, _, _, _, file_name_length, extra_field_length, file_comment_length, _, _, _, _ = values
        # reset last_mod_time
        values[5] = 0
        # reset last_mod_date
        values[6] = 0x21
        central_directory_header_struct.pack_into(mm, offset, *values)
        offset += central_directory_header_struct.size + file_name_length + extra_field_length + file_comment_length
        if extra_field_length != 0:
            purify_extra_data(mm, offset-extra_field_length, extra_field_length)

    if offset == 0:
        raise NonZipFileError(zip_.name)


def cli(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("zips", metavar="zip", nargs="+", type=argparse.FileType("r+b"))

    options = parser.parse_args(args)
    try:
        for zip_ in options.zips:
            _zero_zip_date_time(zip_)
            zip_.close()
    except NonZipFileError as e:
        sys.stderr.write("Invalid file format: %r\n" % e.args[0])
        sys.exit(1)
