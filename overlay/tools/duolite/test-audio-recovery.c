/* Hardware regression: silent playback must advance after drop/prepare and XRUN recovery.
 * Build with the target ALSA SDK, run with other playback clients stopped.
 * No ROMs, recordings or changes to system configuration are required. */
#define _GNU_SOURCE
#include <alsa/asoundlib.h>
#include <errno.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
static double now(void) {struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec/1e9;}
static int open_pcm(snd_pcm_t **p) {
 int rc=snd_pcm_open(p,"default",SND_PCM_STREAM_PLAYBACK,SND_PCM_NONBLOCK);
 if(rc<0)return rc;
 return snd_pcm_set_params(*p,SND_PCM_FORMAT_S16_LE,SND_PCM_ACCESS_RW_INTERLEAVED,2,48000,1,40000);
}
static long feed(snd_pcm_t *p,double seconds) {
 short silence[480*2]={0};long written=0;double end=now()+seconds;
 while(now()<end) {
  snd_pcm_sframes_t n=snd_pcm_writei(p,silence,480);
  if(n>0)written+=n;
  else if(n==-EAGAIN)usleep(1000);
  else if(n<0) {fprintf(stderr,"write: %s (%ld)\n",snd_strerror(n),(long)n);break;}
 }
 return written;
}
int main(void) {
 snd_pcm_t *p=NULL;int rc=open_pcm(&p);
 if(rc<0){fprintf(stderr,"open: %s\n",snd_strerror(rc));return 2;}
 long initial=feed(p,.6);
 int drop=snd_pcm_drop(p),prepare=snd_pcm_prepare(p);
 long after_prepare=prepare<0?0:feed(p,.6);
 snd_pcm_close(p);p=NULL;
 rc=open_pcm(&p);if(rc<0)return 3;
 long second_initial=feed(p,.3);
 usleep(120000); // deliberately miss the hardware buffer deadline
 snd_pcm_sframes_t stalled=snd_pcm_avail(p);
 int recovered=stalled<0?snd_pcm_recover(p,(int)stalled,1):-999;
 long after_xrun=recovered<0?0:feed(p,.6);
 snd_pcm_drop(p);snd_pcm_close(p);
 printf("{\"initial_frames\":%ld,\"drop_rc\":%d,\"prepare_rc\":%d,\"after_prepare_frames\":%ld,\"second_initial_frames\":%ld,\"xrun_rc\":%ld,\"recover_rc\":%d,\"after_xrun_frames\":%ld}\n",initial,drop,prepare,after_prepare,second_initial,(long)stalled,recovered,after_xrun);
 return initial>14000 && after_prepare>14000 && second_initial>7000 && stalled==-EPIPE && recovered==0 && after_xrun>14000 ? 0 : 1;
}
