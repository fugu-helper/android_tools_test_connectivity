#!/usr/bin/env python3.4
#
#   Copyright 2016 - Google
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""
    Test Script for Telephony Pre Flight check.
"""

import time
from queue import Empty
from acts.test_utils.tel.TelephonyBaseTest import TelephonyBaseTest
from acts.test_utils.tel.tel_defines import AOSP_PREFIX
from acts.test_utils.tel.tel_defines import CAPABILITY_PHONE
from acts.test_utils.tel.tel_defines import CAPABILITY_VOLTE
from acts.test_utils.tel.tel_defines import CAPABILITY_VT
from acts.test_utils.tel.tel_defines import CAPABILITY_WFC
from acts.test_utils.tel.tel_defines import CAPABILITY_MSIM
from acts.test_utils.tel.tel_defines import CAPABILITY_OMADM
from acts.test_utils.tel.tel_defines import INVALID_SUB_ID
from acts.test_utils.tel.tel_defines import MAX_WAIT_TIME_NW_SELECTION
from acts.test_utils.tel.tel_defines import PRECISE_CALL_STATE_LISTEN_LEVEL_BACKGROUND
from acts.test_utils.tel.tel_defines import PRECISE_CALL_STATE_LISTEN_LEVEL_FOREGROUND
from acts.test_utils.tel.tel_defines import PRECISE_CALL_STATE_LISTEN_LEVEL_RINGING
from acts.test_utils.tel.tel_defines import WAIT_TIME_AFTER_REBOOT
from acts.test_utils.tel.tel_lookup_tables import device_capabilities
from acts.test_utils.tel.tel_lookup_tables import operator_capabilities
from acts.test_utils.tel.tel_test_utils import WifiUtils
from acts.test_utils.tel.tel_test_utils import ensure_phones_default_state
from acts.test_utils.tel.tel_test_utils import ensure_wifi_connected
from acts.test_utils.tel.tel_test_utils import get_operator_name
from acts.test_utils.tel.tel_test_utils import setup_droid_properties
from acts.test_utils.tel.tel_test_utils import set_phone_screen_on
from acts.test_utils.tel.tel_test_utils import set_phone_silent_mode
from acts.test_utils.tel.tel_test_utils import toggle_airplane_mode
from acts.test_utils.tel.tel_test_utils import verify_http_connection
from acts.test_utils.tel.tel_test_utils import wait_for_voice_attach_for_subscription
from acts.test_utils.tel.tel_test_utils import wait_for_wifi_data_connection
from acts.test_utils.tel.tel_voice_utils import phone_setup_volte
from acts.asserts import abort_all
from acts.asserts import fail


class TelLivePreflightTest(TelephonyBaseTest):
    def __init__(self, controllers):
        TelephonyBaseTest.__init__(self, controllers)

        self.wifi_network_ssid = self.user_params.get(
              "wifi_network_ssid") or self.user_params.get("wifi_network_ssid_2g")
        self.wifi_network_pass = self.user_params.get(
              "wifi_network_pass") or self.user_params.get("wifi_network_pass_2g")

    """ Tests Begin """

    @TelephonyBaseTest.tel_test_wrap
    def test_check_environment(self):
        ad = self.android_devices[0]
        # Check WiFi environment.
        # 1. Connect to WiFi.
        # 2. Check WiFi have Internet access.
        toggle_airplane_mode(self.log, ad, False, strict_checking=False)
        try:
            if not ensure_wifi_connected(self.log, ad, self.wifi_network_ssid,
                                         self.wifi_network_pass):
                self._preflight_fail("{}: WiFi connect fail.".format(
                    ad.serial))
            if (not wait_for_wifi_data_connection(self.log, ad, True) or
                    not verify_http_connection(self.log, ad)):
                self._preflight_fail("{}: Data not available on WiFi.".format(
                    ad.serial))
        finally:
            WifiUtils.wifi_toggle_state(self.log, ad, False)
        # TODO: add more environment check here.
        return True

    @TelephonyBaseTest.tel_test_wrap
    def test_pre_flight_check(self):
        for ad in self.android_devices:
            #check for sim and service
            subInfo = ad.droid.subscriptionGetAllSubInfoList()
            if not subInfo or len(subInfo) < 1:
                self._preflight_fail(
                    "{}: Unable to find A valid subscription!".format(
                        ad.serial))
            toggle_airplane_mode(self.log, ad, False, strict_checking=False)
            if ad.droid.subscriptionGetDefaultDataSubId() <= INVALID_SUB_ID:
                self._preflight_fail("{}: No Default Data Sub ID".format(
                    ad.serial))
            elif ad.droid.subscriptionGetDefaultVoiceSubId() <= INVALID_SUB_ID:
                self._preflight_fail("{}: No Valid Voice Sub ID".format(
                    ad.serial))
            sub_id = ad.droid.subscriptionGetDefaultVoiceSubId()
            if not wait_for_voice_attach_for_subscription(
                    self.log, ad, sub_id, MAX_WAIT_TIME_NW_SELECTION):
                self._preflight_fail(
                    "{}: Did Not Attach For Voice Services".format(ad.serial))
        return True

    @TelephonyBaseTest.tel_test_wrap
    def test_check_crash(self):
        for ad in self.android_devices:
            ad.crash_report = ad.check_crash_report()
            if ad.crash_report:
                msg = "Find crash reports %s" % (ad.crash_report)
                ad.log.error(msg)
                fail(msg)

    def _preflight_fail(self, message):
        self.log.error(
            "Aborting all ongoing tests due to preflight check failure.")
        abort_all(message)


""" Tests End """

