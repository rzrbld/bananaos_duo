#pragma once
#include <algorithm>

namespace banana
{
    struct TouchPoint { float x, y; };

    // Inverse of fitScanout's clockwise rotation, in the screen's own canvas.
    inline TouchPoint touchPoint(float x, float y, int rotation, int width, int height)
    {
        x = std::clamp(x, 0.0f, 1.0f);
        y = std::clamp(y, 0.0f, 1.0f);
        float oldX = x;
        if (rotation == 270) { x = 1 - y; y = oldX; }
        else if (rotation == 90) { x = y; y = 1 - oldX; }
        else if (rotation == 180) { x = 1 - x; y = 1 - y; }
        return { x * std::max(0, width - 1), y * std::max(0, height - 1) };
    }
}
