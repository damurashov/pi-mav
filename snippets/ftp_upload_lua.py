import ftp
import common
import time


def lua_file_to_bytes(filename="nice_color.lua"):
    with open(filename, 'rb') as file:
        return file.read()


def _wait_ftp_response(seconds = 10, do_print=False):
    m = common.wait_for_message((common.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=seconds)
    if m is not None:
        m = ftp.FtpPayload.construct_from_bytes(m.get_payload())
    print(m)
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


def write_chunk(sid, offset, chunk: bytearray):
    while True:
        # Pack and send
        common.send(ftp.msg_write_file(sid, offset, chunk))

        # Wait response
        msg = _wait_ftp_response(20)
        if msg is None:
            continue

        if msg.opcode == ftp.OP_Ack:
            break

    return


if __name__ == "__main__":
    sid = open_session()
    file = lua_file_to_bytes()

    offset = 0
    while len(file) != 0:
        # chunk = file[:ftp.MAX_Payload]
        # file = file[ftp.MAX_Payload:]
        chunk = file[:100]
        file = file[100:]
        write_chunk(sid, offset, chunk)
        offset += len(chunk)