from parameters import *

if __name__ == "__main__":
    param_set("BrdNmr", 500.0)
    param_wait_for_param_value()

    param_request_read(param_id='BrdNmr')
    param_wait_for_param_value()
