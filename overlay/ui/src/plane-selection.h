#pragma once
#include <cstdint>
#include <vector>

namespace banana {
struct PrimaryPlaneCandidate {
    uint32_t id, possibleCrtcs, crtc;
    bool primary;
};

// A plane already bound to another CRTC must not be stolen. On cold start,
// reserve each selected free plane before choosing the other screen's plane.
inline uint32_t selectPrimaryPlane(const std::vector<PrimaryPlaneCandidate>& planes,
                                  uint32_t crtc, int index, uint32_t reserved = 0)
{
    if (index < 0 || index >= 32) return 0;
    uint32_t freePlane = 0;
    for (const auto& plane : planes) {
        if (!plane.primary || plane.id == reserved || !(plane.possibleCrtcs & (1u << index))) continue;
        if (plane.crtc == crtc) return plane.id;
        if (!plane.crtc && !freePlane) freePlane = plane.id;
    }
    return freePlane;
}
}
