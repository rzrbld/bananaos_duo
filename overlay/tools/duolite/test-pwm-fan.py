#!/usr/bin/env python3
"""Exercise the built kernel's actual __set_pwm with an instrumented PWM backend."""
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[3] / 'work/duolite/native/build/linux-custom/drivers/hwmon/pwm-fan.c'
text = source.read_text()
function = text[text.index('static int  __set_pwm('):text.index('static int set_pwm(')]
harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdio.h>
#include <stdint.h>
typedef uint64_t u64;
#define MAX_PWM 255
#define min(a,b) ((a) < (b) ? (a) : (b))
#define max(a,b) ((a) > (b) ? (a) : (b))
#define DIV_ROUND_UP(a,b) (((a)+(b)-1)/(b))
enum { pwm_off_reg_off, pwm_disable_reg_enable };
struct pwm_state { unsigned long period, duty_cycle; };
struct pwm_fan_ctx {
 struct pwm_state pwm_state;
 unsigned int pwm_floor, pwm_value, pwm_usec_from_stopped;
 unsigned int quiet_max_pwm, emergency_state, pwm_fan_state;
 unsigned int *pwm_fan_cooling_levels;
 unsigned long pwm_duty_cycle_from_stopped;
 bool enabled;
 int enable_mode;
 void *pwm;
};
static unsigned int boosts, applies;
static unsigned long peak;
static int pwm_apply_might_sleep(void *pwm, struct pwm_state *s) {
 (void)pwm; applies++; if (s->duty_cycle > peak) peak=s->duty_cycle; return 0;
}
static int pwm_fan_power_on(struct pwm_fan_ctx *c) { c->enabled=true; return 0; }
static int pwm_fan_power_off(struct pwm_fan_ctx *c, bool force) {
 (void)force; c->enabled=false; c->pwm_state.duty_cycle=0; return 0;
}
static void usleep_range(unsigned int low, unsigned int high) {
 (void)low; (void)high; boosts++;
}
'''
harness += function + r'''
int main(void) {
 struct pwm_fan_ctx c = {
  .pwm_state={.period=20000}, .pwm_duty_cycle_from_stopped=10000,
  .pwm_usec_from_stopped=250000, .enable_mode=pwm_disable_reg_enable
 };
 assert(__set_pwm(&c,32)==0); assert(boosts==1 && peak==10000);
 peak=0;
 for (unsigned int i=0;i<30;i++) assert(__set_pwm(&c,32)==0);
 assert(boosts==1 && peak<10000); // Repeated thermal updates / floor writes.
 assert(__set_pwm(&c,64)==0); assert(__set_pwm(&c,32)==0);
 assert(boosts==1); // Both low speeds are below the starting duty.
 assert(__set_pwm(&c,191)==0 && c.pwm_value==191); // Cooling still wins.
 c.pwm_floor=64;
 assert(__set_pwm(&c,0)==0 && c.pwm_value==64 && c.enabled);
 assert(__set_pwm(&c,191)==0 && c.pwm_value==191);
 c.pwm_floor=0;
 assert(__set_pwm(&c,0)==0 && !c.enabled);
 assert(__set_pwm(&c,32)==0 && boosts==2); // Real stop/start needs a boost.
 assert(pwm_fan_power_off(&c,true)==0); // Same power-off used by suspend.
 assert(__set_pwm(&c,c.pwm_value)==0 && boosts==3);
 c.enable_mode=pwm_off_reg_off;
 assert(pwm_fan_power_off(&c,true)==0);
 assert(__set_pwm(&c,32)==0 && !c.enabled && boosts==3);
 assert(applies>30);
 unsigned int levels[]={0,32,32,36,40,169,191};
 struct pwm_fan_ctx q = {
  .pwm_state={.period=20000}, .pwm_duty_cycle_from_stopped=10000,
  .pwm_usec_from_stopped=250000, .enable_mode=pwm_disable_reg_enable,
  .quiet_max_pwm=40, .emergency_state=5, .pwm_fan_cooling_levels=levels
 };
 peak=0;
 assert(__set_pwm(&q,255)==0 && q.pwm_value==40);
 assert(peak <= DIV_ROUND_UP((u64)40*19999,255)); // Start boost also capped.
 q.pwm_floor=200;
 assert(__set_pwm(&q,0)==0 && q.pwm_value==40); // A user minimum cannot evade the cap.
 q.pwm_floor=0; q.pwm_fan_state=5;
 assert(__set_pwm(&q,0)==0 && q.pwm_value==169); // Raw writes cannot disable emergency cooling.
 q.pwm_fan_state=6;
 assert(__set_pwm(&q,32)==0 && q.pwm_value==191);

 puts("PASS: repeated updates, speed changes, thermal override, floor, stop/start and resume");
}
'''
with tempfile.TemporaryDirectory(prefix='banana-pwm-test-') as tmp:
    src=Path(tmp)/'test.c'; binary=Path(tmp)/'test'
    src.write_text(harness)
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-fsanitize=undefined','-o',str(binary),str(src)],check=True)
    subprocess.run([str(binary)],check=True)
