from parameters import *

if __name__ == "__main__":
    param_set("BrdNmr", 501.0)
    param_wait_for_param_value(1)

    param_request_read(param_id='BrdNmr')
    param_wait_for_param_value(1)
