#pragma once
#include "kms.h"
#include "soft.h"
#include "input.h"
#include <sys/types.h>
#include <string>
namespace banana {
// Reuses BananaOS/BananaFront's original menu.c. No alternate UI layout.
bool originalGameMenu(Display& display, SoftBackend& backend, Input& input,
                      pid_t game, int commands, int replies,
                      const std::string& rom, int signalFd);
}
