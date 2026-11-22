#include "original_game_menu.h"
extern "C" {
#include "../third_party/banana_menu/menu.h"
}
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <fstream>
#include <sstream>
#include <poll.h>
#include <signal.h>
#include <unistd.h>
#include <linux/input.h>

namespace banana {
namespace {
long long now() {
    return std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now().time_since_epoch()).count();
}
struct Host {
    Display& display; SoftBackend& backend; Input& input;
    pid_t game; int commands, replies, signals;
    std::string rom, stateBase, incoming;
    bool stopped = false, quit = false, advanced = false, resume = false;
    bool interrupted = false, fast = false, noSave = false;
    int next = -1;
    std::deque<bmenu_ev> events;
    bool write(const std::string& s) {
        size_t off = 0;
        while (off < s.size()) {
            ssize_t n = ::write(commands, s.data() + off, s.size() - off);
            if (n <= 0) return false;
            off += n;
        }
        return true;
    }
    void stop() {
        if (!stopped && kill(-game, SIGSTOP) == 0) { stopped = true; usleep(20000); }
    }
    bool request(const std::string& message, std::string* value = nullptr) {
        if (stopped) { kill(-game, SIGCONT); stopped = false; }
        const std::string op = message.substr(0, message.find(' '));
        if (!write("BANANA_MENU " + message + "\n")) return false;
        const long long until = now() + 10000;
        while (now() < until) {
            size_t at;
            while ((at = incoming.find('\n')) != std::string::npos) {
                std::string line = incoming.substr(0, at); incoming.erase(0, at + 1);
                const std::string prefix = "BANANA_MENU " + op + " ";
                const size_t prefixAt = line.find(prefix);
                if (prefixAt == std::string::npos) continue;
                const std::string answer = line.substr(prefixAt + prefix.size());
                if (value) *value = answer;
                if (op != "INFO") stop();
                return op == "INFO" || answer == "OK";
            }
            pollfd p{replies, POLLIN, 0};
            if (poll(&p, 1, 20) > 0) {
                char b[4096]; ssize_t n = read(replies, b, sizeof b);
                if (n > 0) incoming.append(b, n);
            }
            pollfd signal{signals, POLLIN, 0};
            if (poll(&signal, 1, 0) > 0 || kill(game, 0)) { interrupted = true; break; }
        }
        fprintf(stderr, "original menu: no acknowledgement for %s\n", op.c_str());
        if (!interrupted && !kill(game, 0)) stop();
        return false;
    }
    void finish() {
        // Do not resume the lessee while our last top-screen flip is pending.
        const auto until = now() + 1000;
        while (display.flipPending() && now() < until) {
            pollfd fd{display.pollFd(), POLLIN, 0};
            if (poll(&fd, 1, 5) > 0) display.handleEvents();
        }
        display.originalMenu(false);
        if (stopped) { kill(-game, SIGCONT); stopped = false; }
        if (quit) write(noSave ? "BANANA_MENU QUIT_NOSAVE\n" : "BANANA_MENU QUIT\n");
        else {
            // No synchronous wait on return: the normal game-panel loop drains replies.
            write(advanced ? "BANANA_MENU ADVANCED\n" : "BANANA_MENU RESUME\n");
            if (fast) write("FAST_FORWARD\n");
        }
    }
    void panelTap(float x, float y) {
        if (y < 300 || y >= 420) return;
        if (x < 135) next = 1;
        else if (x < 257) next = 2;
        else if (x < 379) next = -1;
        else if (x < 501) { next = -1; fast = true; }
        else next = 4;
        events.push_back({BM_EV_KEY, BM_START, 1, 0, 0});
    }
};
int canvas(void* p, int panel, uint32_t** px, int* pitch, int* w, int* h) {
    if (!panel) return -1; // The original one-screen frontend layout, on the game screen.
    Host& c = *(Host*)p;
    *w = c.backend.screenWidth(0); *h = c.backend.height();
    *pitch = *w * 4; *px = c.backend.canvas(0); return 0;
}
void show(void* p, int, int) {
    Host& c = *(Host*)p;
    const auto until = now() + 200;
    while (c.display.flipPending() && now() < until) {
        pollfd fd{c.display.pollFd(), POLLIN, 0};
        if (poll(&fd, 1, 5) > 0) c.display.handleEvents();
    }
    const uint32_t* screens[2] = {c.backend.pixels(0), c.backend.pixels(1)};
    Damage damage[2] = {{0, 0, c.backend.screenWidth(0), c.backend.height()}, {}};
    c.display.present(screens, damage);
}
int key(int code) {
    switch (code) {
    case BTN_EAST: case KEY_ENTER: return BM_A;
    case BTN_SOUTH: case KEY_BACKSPACE: return BM_B;
    case BTN_WEST: return BM_Y;
    case BTN_NORTH: return BM_X;
    case BTN_TL: return BM_L; case BTN_TR: return BM_R;
    case BTN_START: return BM_START;
    case BTN_DPAD_UP: case KEY_UP: return BM_UP;
    case BTN_DPAD_DOWN: case KEY_DOWN: return BM_DOWN;
    case BTN_DPAD_LEFT: case KEY_LEFT: return BM_LEFT;
    case BTN_DPAD_RIGHT: case KEY_RIGHT: return BM_RIGHT;
    case BTN_MODE: case KEY_ESC: return BM_MENU;
    default: return -1;
    }
}
int pollEvent(void* p, bmenu_ev* ev) {
    Host& c = *(Host*)p;
    pollfd signal{c.signals, POLLIN, 0};
    if (c.interrupted || c.advanced || poll(&signal, 1, 0) > 0 || kill(c.game, 0)) {
        *ev = {BM_EV_KEY, BM_START, 1, 0, 0}; return 1;
    }
    pollfd drm{c.display.pollFd(), POLLIN, 0};
    if (poll(&drm, 1, 0) > 0) c.display.handleEvents();
    // Reuse the existing OS touch-test path; coordinates refer to the bottom game panel.
    if (access("/run/banana/panel-tap", F_OK) == 0) {
        float x, y; std::ifstream f("/run/banana/panel-tap");
        if (f >> x >> y) c.panelTap(x, y);
        unlink("/run/banana/panel-tap");
    }
    int fds[32]; const int n = c.input.fds(fds, 32);
    for (int i = 0; i < n; i++) {
        pollfd fd{fds[i], POLLIN, 0};
        if (poll(&fd, 1, 0) <= 0) continue;
        c.input.read(fd.fd, [&](const InputEvent& e) {
            if (e.type == InputEvent::PRESS || e.type == InputEvent::RELEASE) {
                const int k = key(e.code);
                if (k >= 0) c.events.push_back({BM_EV_KEY, k, e.type == InputEvent::PRESS, 0, 0});
            } else if (e.type == InputEvent::TOUCH_UP && e.screen == 1) {
                const float scale = c.backend.height() / 480.0f;
                c.panelTap(e.x / scale, e.y / scale);
            }
        });
    }
    if (c.events.empty()) return 0;
    *ev = c.events.front(); c.events.pop_front(); return 1;
}
int save(void* p, int slot) { return ((Host*)p)->request("SAVE " + std::to_string(slot)) ? 0 : -1; }
int load(void* p, int slot) { return ((Host*)p)->request("LOAD " + std::to_string(slot)) ? 0 : -1; }
void stateFile(void* p, int slot, char* out, int size) {
    Host& c = *(Host*)p;
    snprintf(out, size, "%s%s", c.stateBase.c_str(), slot ? std::to_string(slot).c_str() : "");
}
void quit(void* p) { ((Host*)p)->quit = true; }
void quitNoSave(void* p) { Host& c = *(Host*)p; c.quit = c.noSave = true; }
void restart(void* p) { ((Host*)p)->request("RESET"); }
void log(void*, const char* s) { fprintf(stderr, "stock menu: %s", s); }
int count(void*) { return 1; }
const char* label(void*, int) { return "Advanced menu"; }
int values(void*, int) { return 2; }
const char* name(void*, int, int v) { return v ? "RetroArch" : "BananaOS"; }
int get(void*, int) { return 0; }
void set(void* p, int, int v) { if (v) ((Host*)p)->advanced = true; }
int hotkey(void*, int i, const char** a, const char** b) {
    static const char* keys[] = {"F + X", "F + R", "F + L", "F + START", "F + volume"};
    static const char* text[] = {"Menu", "Save state", "Load state", "Quit game", "Brightness"};
    if (i >= 5) return 0;
    *a = keys[i]; *b = text[i]; return 1;
}
}
bool originalGameMenu(Display& d, SoftBackend& b, Input& i, pid_t game,
                      int commands, int replies, const std::string& rom, int signals) {
    if (replies < 0) return false;
    Host c{d, b, i, game, commands, replies, signals, rom};
    std::string info;
    if (!c.request("INFO", &info)) return false;
    const size_t split = info.find('\t');
    if (split == std::string::npos) return false;
    c.resume = info.substr(0, split) == "1"; c.stateBase = info.substr(split + 1);
    if (!c.request("PAUSE")) { c.finish(); return false; }
    d.originalMenu(true);
    bmenu_host h{}; h.ctx = &c; h.rom = c.rom.c_str(); h.resume_on = c.resume;
    h.canvas = canvas; h.show = show; h.poll = pollEvent;
    h.save = save; h.load = load; h.state_file = stateFile;
    h.quit = quit; if (c.resume) h.quit_nosave = quitNoSave; h.restart = restart; h.log = log; h.hotkey = hotkey;
    h.opt_count = count; h.opt_label = label; h.opt_values = values;
    h.opt_value_name = name; h.opt_get = get; h.opt_set = set;
    bmenu_init(&h);
    static pid_t previous = 0;
    if (previous != game) { bmenu_session_start(); previous = game; }
    int start = 0, ok;
    do { c.next = -1; ok = bmenu_run(start); start = c.next; } while (ok && start >= 0 && !c.quit);
    c.finish();
    b.invalidate();
    return ok != 0;
}
}
