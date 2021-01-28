from connectivity import wait_for_message
from parameters import *


if __name__ == "__main__":
    param_request_read(param_id='OfsAclXOft')
    param_wait_for_param_value()

    param_request_read(param_index=2)
    param_wait_for_param_value()