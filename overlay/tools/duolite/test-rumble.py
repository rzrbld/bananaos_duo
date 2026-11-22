#!/usr/bin/env python3
"""Run actual rumble routing/policy functions against an instrumented motor."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

aw = Path(sys.argv[1]).read_text()
rs = Path(sys.argv[2]).read_text()

def function(source, name):
    match = re.search(r'(?:static )?(?:int|void|ssize_t) ' + name + r'\(', source)
    assert match, name
    start = match.start(); opening = source.index('{', start); depth = 1; end = opening + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}'); end += 1
    return source[start:end]

names = ['aw86927_set_level', 'aw86927_rumble', 'aw86927_haptics_play',
         'rumble_enabled_store', 'aw86927_close', 'aw86927_suspend', 'aw86927_resume']
code = '\n'.join(function(aw, n) for n in names) + '\n' + function(rs, 'rsinput_play_rumble')
harness = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <sys/types.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
typedef uint16_t u16;
#define EPROBE_DEFER 517
#define READ_ONCE(x) (x)
#define WRITE_ONCE(x,v) ((x)=(v))
#define max(a,b) ((a)>(b)?(a):(b))
static unsigned int locked, hardware_level, hardware_calls;
#define spin_lock_irqsave(lock,flags) do { (void)(lock); (flags)=0; assert(!locked); locked=1; } while(0)
#define spin_unlock_irqrestore(lock,flags) do { (void)(lock); (void)(flags); assert(locked); locked=0; } while(0)
struct aw86927_data;
struct work_struct { bool pending; struct aw86927_data *owner; };
struct aw86927_data {
 u16 level,direct_level,gamepad_level;
 bool ready,rumble_enabled,suspended;
 int control_lock;
 struct work_struct play_work;
};
struct device { struct aw86927_data *data; };
struct device_attribute { int unused; };
struct input_dev { void *data; };
struct ff_effect { union { struct { u16 strong_magnitude,weak_magnitude; } rumble; } u; };
struct rsinput_driver { struct device *haptics; int (*play_rumble)(struct device *,u16,u16); };
static void *dev_get_drvdata(struct device *d) { return d->data; }
static void *input_get_drvdata(struct input_dev *d) { return d->data; }
static void schedule_work(struct work_struct *w) { w->pending=true; }
static void flush_work(struct work_struct *w) {
 assert(!locked);
 if(w->pending) { hardware_level=w->owner->level; hardware_calls++; w->pending=false; }
}
static void cancel_work_sync(struct work_struct *w) { assert(!locked); w->pending=false; }
static int aw86927_stop(struct aw86927_data *p) { (void)p; assert(!locked); hardware_level=0; hardware_calls++; return 0; }
static int kstrtobool(const char *v, bool *out) {
 if(!strcmp(v,"1") || !strcmp(v,"yes")) {*out=true;return 0;}
 if(!strcmp(v,"0") || !strcmp(v,"no")) {*out=false;return 0;}
 return -EINVAL;
}
'''
harness += code + r'''
int main(void) {
 struct aw86927_data p={.ready=true,.rumble_enabled=true};
 struct device dev={.data=&p}; struct input_dev direct={.data=&p};
 struct rsinput_driver rs={.haptics=&dev,.play_rumble=aw86927_rumble};
 struct input_dev pad={.data=&rs};
 struct ff_effect effect={.u.rumble={.strong_magnitude=1000,.weak_magnitude=9000}};
 p.play_work.owner=&p;
 assert(rsinput_play_rumble(&pad,NULL,&effect)==0);
 assert(p.level==9000 && !hardware_calls); /* callback only schedules, never touches I2C */
 flush_work(&p.play_work); assert(hardware_level==9000);
 effect.u.rumble.strong_magnitude=12000;
 aw86927_haptics_play(&direct,NULL,&effect); flush_work(&p.play_work);
 assert(hardware_level==12000);
 aw86927_close(&direct); assert(hardware_level==9000); /* standalone close keeps gamepad effect */
 assert(rumble_enabled_store(&dev,NULL,"no",2)==2); assert(!hardware_level);
 aw86927_rumble(&dev,65535,65535); aw86927_haptics_play(&direct,NULL,&effect);
 flush_work(&p.play_work); assert(!hardware_level && !p.level);
 assert(rumble_enabled_store(&dev,NULL,"yes",3)==3); flush_work(&p.play_work);
 assert(!hardware_level); /* enabling never replays stale requests */
 aw86927_rumble(&dev,0,4000); flush_work(&p.play_work); assert(hardware_level==4000);
 assert(aw86927_suspend(&dev)==0 && !hardware_level);
 aw86927_rumble(&dev,60000,60000); flush_work(&p.play_work); assert(!hardware_level);
 assert(aw86927_resume(&dev)==0); flush_work(&p.play_work); assert(!hardware_level);
 aw86927_rumble(&dev,5000,0); flush_work(&p.play_work); assert(hardware_level==5000);
 assert(rumble_enabled_store(&dev,NULL,"invalid",7)==-EINVAL && p.rumble_enabled);
 p.ready=false; assert(aw86927_rumble(&dev,1,1)==-EPROBE_DEFER);
 assert(hardware_level==5000);
 puts("PASS: controller forwarding, channel mixing, global off, no stale replay, sleep and provider readiness");
}
'''
with tempfile.TemporaryDirectory(prefix='banana-rumble-test-') as tmp:
    source = Path(tmp)/'test.c'; binary = Path(tmp)/'test'
    source.write_text(harness)
    subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Wno-unused-parameter', '-Werror',
                    '-fsanitize=undefined', '-o', str(binary), str(source)], check=True)
    subprocess.run([str(binary)], check=True)
