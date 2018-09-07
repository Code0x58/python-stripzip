import mmap
import os
import sys
from struct import Struct


def _zero_zip_date_time(source):
    archive_size = os.stat(source).st_size

    signature_struct = Struct("<L")
    local_file_header_struct = Struct("<LHHHHHLLLHH")
    central_directory_header_struct = Struct("<LHHHHHHLLLHHHHHLL")

    offset = 0

    with open(source, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)
        while offset < archive_size:
            if signature_struct.unpack_from(mm, offset) != (0x04034b50,):
                break
            values = list(local_file_header_struct.unpack_from(mm, offset))
            signature, _, _, _, time, date, _, a, _, b, c = values
            values[4] = 0
            values[5] = 0x21
            local_file_header_struct.pack_into(mm, offset, *values)
            offset += local_file_header_struct.size + a + b + c

        while offset < archive_size:
            if signature_struct.unpack_from(mm, offset) != (0x02014b50,):
                break
            values = list(central_directory_header_struct.unpack_from(mm, offset))
            signature, _, _, _, _, time, date, _, _, _, a, b, c, _, _, _, _ = values
            values[5] = 0
            values[6] = 0x21
            central_directory_header_struct.pack_into(mm, offset, *values)
            offset += central_directory_header_struct.size + a + b + c


def cli(args=sys.argv):
    _zero_zip_date_time(args[1])
