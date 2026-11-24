#!/usr/bin/env python3
"""Exercise the actual ath10k key routine: skip only the missing WCN3990 ack."""
from pathlib import Path
import subprocess
import sys
import tempfile
import re

root = Path(sys.argv[1])
mac = (root/'mac.c').read_text()
core = (root/'core.c').read_text()
start = mac.index('static int ath10k_install_key(')
end = mac.index('\nstatic int ', start+1)
function = mac[start:end]
wcn = core[core.index('.id = WCN3990_HW_1_0_DEV_VERSION'):]
wcn = wcn[:wcn.index('\n\t},')]
assert core.count('.no_pairwise_key_del_ind = true') == 1
assert '.no_pairwise_key_del_ind = true' in wcn
wmi = (root/'wmi.h').read_text()
mac80211 = (root.parents[4]/'include/net/mac80211.h').read_text()
constants = '\n'.join(re.search(r'^#define ' + name + r'\s+.+$', wmi, re.M).group(0) for name in ('WMI_KEY_PAIRWISE', 'WMI_KEY_GROUP'))
pairwise = re.search(r'IEEE80211_KEY_FLAG_PAIRWISE\s*=\s*(BIT\(\d+\))', mac80211).group(1)
constants += '\n#define IEEE80211_KEY_FLAG_PAIRWISE '+pairwise+'\n'
source = constants + r'''
#include <assert.h>
#include <stdbool.h>
#include <errno.h>
#include <stddef.h>
#define HZ 100
#define BIT(x) (1U << (x))
#define lockdep_assert_held(x) ((void)0)
struct ieee80211_key_conf { unsigned flags; };
enum set_key_cmd { SET_KEY, DISABLE_KEY };
struct ath10k { int conf_mutex, install_key_done; struct { bool no_pairwise_key_del_ind; } hw_params; };
struct ath10k_vif { struct ath10k *ar; bool nohwcrypt; };
typedef unsigned char u8;
typedef unsigned int u32;
static int sends, waits, send_status, ack = 1;
static void reinit_completion(int *done) { *done = 0; }
static int ath10k_send_key(struct ath10k_vif *v, struct ieee80211_key_conf *k, enum set_key_cmd c, const u8 *m, u32 f) { sends++; return send_status; }
static unsigned long wait_for_completion_timeout(int *c, int timeout) { assert(timeout == 3*HZ); waits++; return ack; }
'''+function+r'''
static void check(bool quirk, bool software, enum set_key_cmd cmd, u32 flags,
                  int send_error, int completion, int expected, int expected_sends, int expected_waits) {
    struct ath10k ar = { .hw_params.no_pairwise_key_del_ind = quirk };
    struct ath10k_vif v = { .ar = &ar, .nohwcrypt = software };
    struct ieee80211_key_conf key = { .flags = (flags & WMI_KEY_GROUP) ? 0 : IEEE80211_KEY_FLAG_PAIRWISE };
    sends = waits = 0; send_status = send_error; ack = completion;
    assert(ath10k_install_key(&v, &key, cmd, NULL, flags) == expected);
    assert(sends == expected_sends && waits == expected_waits);
}
int main(void) {
    check(true, false, DISABLE_KEY, WMI_KEY_PAIRWISE, 0, 0, 0, 1, 0);
    check(true, false, SET_KEY, WMI_KEY_PAIRWISE, 0, 0, -ETIMEDOUT, 1, 1);
    check(true, false, SET_KEY, WMI_KEY_PAIRWISE, 0, 1, 0, 1, 1);
    check(true, false, DISABLE_KEY, WMI_KEY_GROUP, 0, 0, -ETIMEDOUT, 1, 1);
    check(false, false, DISABLE_KEY, WMI_KEY_PAIRWISE, 0, 0, -ETIMEDOUT, 1, 1);
    check(true, false, DISABLE_KEY, WMI_KEY_PAIRWISE|WMI_KEY_GROUP, 0, 0, -ETIMEDOUT, 1, 1);
    check(true, false, DISABLE_KEY, WMI_KEY_PAIRWISE, -EIO, 0, -EIO, 1, 0);
    check(true, true, DISABLE_KEY, WMI_KEY_PAIRWISE, 0, 0, 1, 0, 0);
}
'''
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp)
    (path/'keys.c').write_text(source)
    subprocess.run(['cc', '-std=c11', str(path/'keys.c'), '-o', str(path/'keys')], check=True)
    subprocess.run([str(path/'keys')], check=True)
print('PASS: WCN3990 pairwise deletion still sent; new/group keys, other hardware and errors retain checks')
