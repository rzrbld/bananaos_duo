#pragma once
#include <algorithm>
#include <cstdint>
#include <cstddef>
#include <cstdlib>
#include <vector>

namespace banana
{
	// Fit a logical canvas into a native panel, with clockwise rotation and black borders.
	inline void fitScanout(uint8_t* dst, size_t pitch, int width, int height, int rotation,
		const uint32_t* src, int sw, int sh)
	{
		bool sideways = rotation == 90 || rotation == 270;
		int ow = sideways ? height : width, oh = sideways ? width : height;
		int fw = ow, fh = (int)((int64_t)ow * sh / sw);
		if (fh > oh) { fh = oh; fw = (int)((int64_t)oh * sw / sh); }
		// Rounded logical widths (1707x960 -> 1920x1080) need one common
		// scale. Scaling X by 1707/1920 but Y by 960/1080 changes which
		// dither columns get duplicated partway across the panel: a bright seam.
		const bool uniformScale = std::abs(fw - ow) <= 1 && std::abs(fh - oh) <= 1 &&
			std::abs((int64_t)sw * oh - (int64_t)sh * ow) * 1000 <= (int64_t)sh * ow;
		if (uniformScale) { fw = ow; fh = oh; }
		fw = std::max(fw, 1); fh = std::max(fh, 1);
		int left = (ow - fw) / 2, top = (oh - fh) / 2;
		auto sourceX = [&](int at, int span) {
			return std::min(sw - 1, (int)((int64_t)at * (uniformScale ? sh : sw) / (uniformScale ? oh : span)));
		};
		std::vector<int> columns(width, -1), rows(height, -1);
		for (int x = 0; x < width; x++)
		{
			int at = rotation == 90 || rotation == 180 ? width - 1 - x : x;
			at -= sideways ? top : left;
			int span = sideways ? fh : fw;
			if (at >= 0 && at < span)
				columns[x] = sideways ? (int)((int64_t)at * sh / span) * sw : sourceX(at, span);
		}
		for (int y = 0; y < height; y++)
		{
			int at = rotation == 180 || rotation == 270 ? height - 1 - y : y;
			at -= sideways ? left : top;
			int span = sideways ? fw : fh;
			if (at >= 0 && at < span)
				rows[y] = sideways ? sourceX(at, span) : (int)((int64_t)at * sh / span) * sw;
		}
		for (int y = 0; y < height; y++)
		{
			auto row = reinterpret_cast<uint32_t*>(dst + (size_t)y * pitch);
			for (int x = 0; x < width; x++)
				row[x] = rows[y] >= 0 && columns[x] >= 0 ? src[(size_t)rows[y] + columns[x]] : 0;
		}
	}
}
