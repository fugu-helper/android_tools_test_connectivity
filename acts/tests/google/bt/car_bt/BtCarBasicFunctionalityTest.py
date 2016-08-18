#/usr/bin/env python3.4
#
# Copyright (C) 2016 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

"""
Test script to execute Bluetooth basic functionality test cases relevant to car.
"""

import time

from queue import Empty
from acts.test_utils.bt.BluetoothBaseTest import BluetoothBaseTest
from acts.test_utils.bt.BtEnum import BluetoothScanModeType
from acts.test_utils.bt.bt_test_utils import check_device_supported_profiles
from acts.test_utils.bt.bt_test_utils import log_energy_info
from acts.test_utils.bt.bt_test_utils import reset_bluetooth
from acts.test_utils.bt.bt_test_utils import set_device_name
from acts.test_utils.bt.bt_test_utils import set_bt_scan_mode
from acts.test_utils.bt.bt_test_utils import setup_multiple_devices_for_bt_test
from acts.test_utils.bt.bt_test_utils import take_btsnoop_logs


class BtCarBasicFunctionalityTest(BluetoothBaseTest):
    default_timeout = 10
    scan_discovery_time = 5

    def __init__(self, controllers):
        BluetoothBaseTest.__init__(self, controllers)
        self.droid_ad = self.android_devices[0]

    def setup_class(self):
        return setup_multiple_devices_for_bt_test(self.android_devices)

    def setup_test(self):
        self.log.debug(log_energy_info(self.android_devices, "Start"))
        for a in self.android_devices:
            a.ed.clear_all_events()
        return True

    def teardown_test(self):
        self.log.debug(log_energy_info(self.android_devices, "End"))
        return True

    def on_fail(self, test_name, begin_time):
        take_btsnoop_logs(self.android_devices, self, test_name)
        reset_bluetooth(self.android_devices)

    @BluetoothBaseTest.bt_test_wrap
    def test_if_support_a2dp_sink_profile(self):
        """ Test that a single device can support A2DP SNK profile.
        Steps
        1. Initialize one android devices
        2. Check devices support profiles and return a dictionary
        3. Check the value of key 'a2dp_sink'
        :return: test_result: bool
        """
        profiles = check_device_supported_profiles(self.droid_ad.droid)
        if not profiles['a2dp_sink']:
            self.log.debug("Android device do not support A2DP SNK profile.")
            return False
        return True

    @BluetoothBaseTest.bt_test_wrap
    def test_if_support_hfp_client_profile(self):
        """ Test that a single device can support HFP HF profile.
        Steps
        1. Initialize one android devices
        2. Check devices support profiles and return a dictionary
        3. Check the value of key 'hfp_client'
        :return: test_result: bool
        """
        profiles = check_device_supported_profiles(self.droid_ad.droid)
        if not profiles['hfp_client']:
            self.log.debug("Android device do not support HFP Client profile.")
            return False
        return True

    @BluetoothBaseTest.bt_test_wrap
    def test_if_support_pbap_client_profile(self):
        """ Test that a single device can support PBAP PCE profile.
        Steps
        1. Initialize one android devices
        2. Check devices support profiles and return a dictionary
        3. Check the value of key 'pbap_client'
        :return: test_result: bool
        """
        profiles = check_device_supported_profiles(self.droid_ad.droid)
        if not profiles['pbap_client']:
            self.log.debug("Android device do not support PBAP Client profile.")
            return False
        return True
