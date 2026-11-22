// The emulator and banana-ui keep their existing achievements session.
#include "ra.h"
int ra_progress(unsigned* a, unsigned* b) { *a = *b = 0; return 0; }
int ra_recent(ra_recent_t* out, int n) { (void)out; (void)n; return 0; }
int ra_popup_take(char* a,int b,char* c,int d,char* e,int f,unsigned* g,int* h) {
 (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;(void)h;return 0;
}
