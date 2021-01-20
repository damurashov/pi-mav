import ftp
import common
import time


def lua_file_to_bytes(filename="hw.luac"):
    res = open(filename, 'rb').read()
    print(res)
    return res


def _wait_ftp_response(seconds=10, do_print=False):
    m = common.wait_for_message((common.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=seconds)
    if m is not None:
        m = ftp.FtpPayload.construct_from_bytes(m.get_payload())
    if do_print:
        print(f'Ftp response: {str(m)}')
    return m


def test():
    common.send(ftp.msg_open_file_wo('/main.lua'))
    m = common.wait_for_message((common.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=30)
    print(m)
    if m is not None:
        ftp.FtpPayload.construct_from_bytes(m.get_payload())


def open_session(filename='/main.lua') -> int:
    common.send(ftp.msg_open_file_wo(filename))
    m = common.wait_for_message((common.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=30)

    if m is not None:
        m = ftp.FtpPayload.construct_from_bytes(m.get_payload())

    assert m.opcode == ftp.OP_Ack
    return m.session


def write_chunk(session, off, data: bytearray):
    # Pack and send

    print(f'Writing chunk: \"{str(data)}\"')

    while True:
        common.send(ftp.msg_write_file(session, off, data))
        m = _wait_ftp_response(seconds=5, do_print=True)
        if m is not None:
            if m.offset == off:
                break


if __name__ == "__main__":
    # ftp.ftp_read_file()

    CHUNK_SIZE = 40
    file = lua_file_to_bytes()
    sid = open_session()

    print(f'Length: {len(file)}')

    offset = 0
    while len(file) != 0:
        # chunk = file[:ftp.MAX_Payload]
        # file = file[ftp.MAX_Payload:]
        chunk = file[:CHUNK_SIZE]
        file = file[CHUNK_SIZE:]
        write_chunk(sid, offset, chunk)
        offset += len(chunk)
        print(f'offset: {offset}')

    common.send(ftp.msg_terminate_session(sid))
    print('done')