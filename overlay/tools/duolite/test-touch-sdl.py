#!/usr/bin/env python3
"""Execute the built SDL source's touch mapper with known physical panel paths."""
from pathlib import Path
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).read_text()
start = source.index('int BP_MapTouch(')
end = source.index('\n}\n', start) + 3
function = source[start:end]
test = r'''
#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int bp_on, bp_single, bp_rotation, bp_W=1920, bp_H=960;
static struct { int w, h; } bp_p[2]={{640,960},{1280,960}};
#define SDL_getenv getenv
static char *fake_path(const char *path, char *out) {
    strcpy(out, strstr(path,"event8") ? "/soc/4a88000.i2c/input/event8" : "/soc/4c80000.i2c/input/event6");
    return out;
}
#define realpath fake_path
static void bp_rect(int s,int*x,int*y) { *x=s?640:0; *y=0; }
'''+function+r'''
static void check(const char* node,float x,float y,float ex,float ey,int expected) {
    assert(BP_MapTouch(&x,&y,node)==expected);
    if(expected) { assert(fabsf(x-ex)<.0001f); assert(fabsf(y-ey)<.0001f); }
}
int main(void) {
    setenv("BANANA_TOUCH_TOP","4a88000.i2c",1);
    check("/dev/input/event8",.2f,.7f,.2f,.7f,1); /* ordinary SDL unchanged */
    bp_on=bp_single=1; bp_rotation=270;
    check("/dev/input/event8",0,0,1,0,1);
    check("/dev/input/event8",1,1,0,1,1);
    check("/dev/input/event8",.2f,.7f,.3f,.2f,1);
    check("/dev/input/event6",.2f,.7f,0,0,0); /* dark bottom cannot click top */
    bp_rotation=90;
    check("/dev/input/event8",.2f,.7f,.7f,.8f,1);
    bp_single=0;
    check("/dev/input/event8",1,1,1.0f/3,1,1);
    check("/dev/input/event6",0,0,1.0f/3,0,1);
    unsetenv("BANANA_TOUCH_TOP");
    check("/dev/input/event8",0,0,1.0f/3,0,1); /* legacy bottom-only mapping */
}
'''
with tempfile.TemporaryDirectory() as d:
    path = Path(d)
    (path/'test.c').write_text(test)
    subprocess.run(['cc', '-std=gnu99', str(path/'test.c'), '-o', str(path/'test'), '-lm'], check=True)
    subprocess.run([str(path/'test')], check=True)
print('SDL touch mapping passed: native paths, rotated top, unequal dual panels and legacy behavior')
