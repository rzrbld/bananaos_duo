/* Exercise the real daemon helpers against a synthetic sysfs, never main(). */
#define main bananad_main
#include "../bananad.c"
#undef main
#include <assert.h>

static const char *sysroot;
static const char *redirect(const char *path, char *buf, size_t n)
{
	if (strncmp(path, "/sys/", 5)) return path;
	snprintf(buf, n, "%s%s", sysroot, path);
	return buf;
}
FILE *__real_fopen(const char *, const char *);
FILE *__wrap_fopen(const char *path, const char *mode)
{
	char buf[1024];
	return __real_fopen(redirect(path, buf, sizeof buf), mode);
}
DIR *__real_opendir(const char *);
DIR *__wrap_opendir(const char *path)
{
	char buf[1024];
	return __real_opendir(redirect(path, buf, sizeof buf));
}
int __real_open(const char *, int, ...);
int __wrap_open(const char *path, int flags, ...)
{
	char buf[1024];
	mode_t mode = 0;
	if (flags & O_CREAT) { va_list ap; va_start(ap, flags); mode = va_arg(ap, int); va_end(ap); }
	return __real_open(redirect(path, buf, sizeof buf), flags, mode);
}
int __real_access(const char *, int);
int __wrap_access(const char *path, int mode)
{
	char buf[1024];
	return __real_access(redirect(path, buf, sizeof buf), mode);
}
int main(int argc, char **argv)
{
	assert(argc == 6 || argc == 7);
	sysroot = argv[1];
	duolite = 1;
	snprintf(led_mode, sizeof led_mode, "%s", argv[2]);
	cfg.led_brightness = atoi(argv[3]);
	snprintf(fan_profile, sizeof fan_profile, "%s", argv[4]);
	leds_update();
	fan_apply();
	if (argc == 7) { load_conf(argv[6]); rumble_apply(); assert(rumble_applied); }
	backlights_power(0);
	int pct = atoi(argv[5]);
	assert(battery_capacity() == pct);
	assert(battery_discharging_pct() == (charger_online() ? -1 : pct));
	return 0;
}
