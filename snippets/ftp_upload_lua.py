import ftp
import common

def lua_file_to_bytes(filename="nice_color.lua"):
    with open(filename, 'rb') as file:
        return file.read()


def test():
    common.send(ftp.msg_open_file_wo('./main.lua'))
    m = common.wait_for_message((common.mavcommon.MAVLINK_MSG_ID_FILE_TRANSFER_PROTOCOL,), seconds=30)
    print(m)
    if m is not None:
        ftp.FtpPayload.unpack(m.get_payload())


if __name__ == "__main__":
    test()