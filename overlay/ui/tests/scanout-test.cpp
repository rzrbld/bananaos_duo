#include "scanout.h"
#include <cassert>
#include <cstdio>
#include <vector>

static void check(int width, int height, int rotation, const std::vector<uint32_t>& expected)
{
	const uint32_t source[] = { 1, 2, 3, 4, 5, 6 };
	const size_t stride = width + 3;
	std::vector<uint32_t> pixels(stride * height + 2, 0xdeadbeef);
	banana::fitScanout(reinterpret_cast<uint8_t*>(pixels.data() + 1), stride * 4,
		width, height, rotation, source, 3, 2);
	assert(pixels.front() == 0xdeadbeef && pixels.back() == 0xdeadbeef);
	for (int y = 0; y < height; y++)
	{
		for (int x = 0; x < width; x++) assert(pixels[1 + y * stride + x] == expected[y * width + x]);
		for (size_t x = width; x < stride; x++) assert(pixels[1 + y * stride + x] == 0xdeadbeef);
	}
}

int main()
{
	check(3, 2, 0, { 1, 2, 3, 4, 5, 6 });
	check(2, 3, 90, { 4, 1, 5, 2, 6, 3 });
	check(3, 2, 180, { 6, 5, 4, 3, 2, 1 });
	check(2, 3, 270, { 3, 6, 2, 5, 1, 4 });
	check(6, 4, 0, { 1, 1, 2, 2, 3, 3, 1, 1, 2, 2, 3, 3,
		4, 4, 5, 5, 6, 6, 4, 4, 5, 5, 6, 6 });
	check(3, 4, 0, { 0, 0, 0, 1, 2, 3, 4, 5, 6, 0, 0, 0 });
	check(5, 2, 0, { 0, 1, 2, 3, 0, 0, 4, 5, 6, 0 });
	check(1, 1, 0, { 1 });
	check(2, 1, 0, { 1, 2 });

	std::vector<uint32_t> source(1280 * 960, 0x12345678), panel(1080 * 1920);
	banana::fitScanout(reinterpret_cast<uint8_t*>(panel.data()), 1080 * 4, 1080, 1920, 270,
		source.data(), 1280, 960);
	size_t lit = 0;
	for (uint32_t p : panel) { assert(p == 0 || p == 0x12345678); lit += p != 0; }
	assert(lit == 1440 * 1080);
	// Distinct outer/inner dot textures must remain periodic all the way
	// across the rounded widescreen canvas, without a brighter right region.
	for (int logicalWidth : {1706, 1707}) {
		std::vector<uint32_t> dots((size_t)logicalWidth * 960);
		for (int y = 0; y < 960; y++) for (int x = 0; x < logicalWidth; x++) {
			bool inner = x >= 36 && x < logicalWidth - 36 && y >= 120 && y < 920;
			bool dot = x % 8 < 2 && y % 8 < 2;
			dots[(size_t)y * logicalWidth + x] = inner ? (dot ? 0xffa05050 : 0xff502020) : (dot ? 0xff606060 : 0xff202020);
		}
		banana::fitScanout(reinterpret_cast<uint8_t*>(panel.data()), 1080 * 4, 1080, 1920, 270,
			dots.data(), logicalWidth, 960);
		auto pixel = [&](int x, int y) { return panel[(size_t)(1919 - x) * 1080 + y]; };
		for (int y : {18, 270}) for (int x = 100; x + 9 < 1800; x++) {
			assert(pixel(x, y) == pixel(x + 9, y));
			uint32_t p = pixel(x, y);
			assert(y == 18 ? (p == 0xff606060 || p == 0xff202020) : (p == 0xffa05050 || p == 0xff502020));
		}
	}
	puts("scanout: rotation, scaling, borders, stride and Duo Lite dimensions passed");
}
