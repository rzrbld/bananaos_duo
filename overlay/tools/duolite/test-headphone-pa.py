#!/usr/bin/env python3
"""Exercise actual WCD937x PA helpers with instrumented registers and IRQs."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

source = Path(sys.argv[1])
text = source.read_text()
names = ('wcd937x_codec_enable_hphr_pa', 'wcd937x_codec_enable_hphl_pa', 'wcd937x_codec_mute_stream')
functions = []
for name in names:
    start = text.index('static ', text.index(name) - 15)
    end = text.index('\nstatic ', start + 10)
    functions.append(text[start:end])
functions = '\n'.join(functions)
constants = sorted(set(re.findall(r'\b(?:WCD937X_|WCD_CLSH_|WCD_EVENT_)[A-Z0-9_]+\b', functions)))
harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#define BIT(n) (1u << (n))
#define SNDRV_PCM_STREAM_PLAYBACK 0
#define CLS_AB 3
#define CLS_AB_HIFI 4
#define HPH_PA_DELAY 0
struct wcd937x_priv {
 void *clsh_info, *wcd_mbhc;
 int hph_mode, hphl_pdm_wd_int, hphr_pdm_wd_int;
 unsigned long status_mask;
 bool comp1_enable, comp2_enable, hphl_enable, hphr_enable;
 bool hphl_pa_enabled, hphr_pa_enabled;
};
struct snd_soc_component { struct wcd937x_priv *priv; };
struct snd_soc_dai { struct wcd937x_priv *dev; struct snd_soc_component *component; };
static unsigned int analog, settled, irq_balance[2], changes;
static bool stream_enabled;
static struct wcd937x_priv *snd_soc_component_get_drvdata(struct snd_soc_component *c) { return c->priv; }
static struct wcd937x_priv *dev_get_drvdata(struct wcd937x_priv *p) { return p; }
static void set_bit(unsigned int b, unsigned long *p) { *p |= BIT(b); }
static void clear_bit(unsigned int b, unsigned long *p) { *p &= ~BIT(b); }
static bool test_bit(unsigned int b, unsigned long *p) { return !!(*p & BIT(b)); }
static void usleep_range(unsigned int low, unsigned int high) { (void)high; settled += low; }
static void enable_irq(unsigned int irq) { assert(irq < 2 && irq_balance[irq] == 0); irq_balance[irq]++; }
static void disable_irq_nosync(unsigned int irq) { assert(irq < 2 && irq_balance[irq] == 1); irq_balance[irq]--; }
'''
harness += '\nenum { ' + ', '.join(constants) + ' };\n'
harness += r'''
static void snd_soc_component_update_bits(struct snd_soc_component *c, int reg, unsigned int mask, unsigned int value) {
 (void)c;
 if (reg == WCD937X_ANA_HPH) {
  if ((mask & (BIT(6)|BIT(7))) && value) {
   assert(stream_enabled); assert(settled >= 20000); changes++;
  }
  if ((mask & (BIT(6)|BIT(7))) && !value) { assert(stream_enabled); changes++; }
  analog = (analog & ~mask) | (value & mask);
 }
}
static void wcd_clsh_ctrl_set_state(void *p, int event, int state, int mode) {
 (void)p; (void)mode;
 if (event == WCD_CLSH_EVENT_PRE_DAC) settled = 0;
 if (event == WCD_CLSH_EVENT_POST_PA) {
  assert(!(analog & (state == WCD_CLSH_STATE_HPHL ? BIT(7) : BIT(6))));
 }
}
static void wcd_mbhc_event_notify(void *p, int event) { (void)p; (void)event; }
'''
harness += functions + r'''
int main(void) {
 struct wcd937x_priv p = {.hphl_pdm_wd_int=0, .hphr_pdm_wd_int=1, .hphl_enable=true, .hphr_enable=true};
 struct snd_soc_component c = {.priv=&p};
 struct snd_soc_dai dai = {.dev=&p, .component=&c};
 stream_enabled = true;
 assert(wcd937x_codec_mute_stream(&dai,0,0)==0);
 assert((analog & (BIT(6)|BIT(7))) == (BIT(6)|BIT(7)) && changes==2);
 wcd937x_codec_mute_stream(&dai,0,0); assert(changes==2); /* repeated prepare */
 wcd937x_codec_mute_stream(&dai,1,1); assert(changes==2); /* capture must not mute playback */
 p.hphl_enable=p.hphr_enable=false; /* disable must still release an already-on PA */
 wcd937x_codec_mute_stream(&dai,1,0);
 assert(!(analog & (BIT(6)|BIT(7))) && changes==4);
 assert(!irq_balance[0] && !irq_balance[1]);
 stream_enabled=false;
 wcd937x_codec_mute_stream(&dai,1,0); assert(changes==4);
 p.hphl_enable=true; stream_enabled=true;
 wcd937x_codec_mute_stream(&dai,0,0);
 assert((analog & (BIT(6)|BIT(7)))==BIT(7));
 wcd937x_codec_mute_stream(&dai,1,0);
 assert(!analog && !irq_balance[0] && !irq_balance[1]);
 puts("PASS: PA settle ordering, stream window, repeated mute, capture isolation and mono output");
}
'''
with tempfile.TemporaryDirectory(prefix='banana-pa-test-') as tmp:
    src = Path(tmp)/'test.c'
    binary = Path(tmp)/'test'
    src.write_text(harness)
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=undefined', '-o', str(binary), str(src)], check=True)
    subprocess.run([str(binary)], check=True)
