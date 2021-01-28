# Parameters protocol

from connectivity import send, wait_for_message, mav, mavcommon, mavutil


def _msg_param_request_list():
    msg = mav.param_request_list_encode(1, 1)
    return msg.pack(mav)


def _msg_param_request_read(param_index=-1, param_id=''):
    if param_index < 0 and len(param_id) == 0:
        raise ValueError()

    param_id = bytearray(param_id[0:16], encoding='ascii')
    print(param_id)
    msg = mav.param_request_read_encode(1, 1, param_id, param_index)
    return msg.pack(mav)


def param_request_list():
    send(_msg_param_request_list())


def param_request_read(param_index=-1, param_id=''):
    send(_msg_param_request_read(param_index, param_id))


def param_wait_for_param_value(seconds=4, do_print=True):
    return wait_for_message((mavcommon.MAVLINK_MSG_ID_PARAM_VALUE,), seconds=seconds, do_print=do_print)
