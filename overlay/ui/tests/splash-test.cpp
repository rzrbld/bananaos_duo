#define STB_IMAGE_IMPLEMENTATION
#include "../third_party/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../third_party/stb_image_write.h"
#include "splash.h"
#include "scanout.h"
#include "../rnds/RndsRaster.h"
#include <algorithm>
#include <cassert>
#include <cstdio>
#include <vector>

static rnds::Bitmap decode(const std::string& path)
{
    rnds::Bitmap bitmap;
    int w, h, channels;
    auto pixels = stbi_load(path.c_str(), &w, &h, &channels, 4);
    if (!pixels) return bitmap;
    bitmap.w = w; bitmap.h = h;
    bitmap.px.assign(pixels, pixels + (size_t)w * h * 4);
    stbi_image_free(pixels);
    return bitmap;
}

static void save(const std::string& path, const uint32_t* pixels, int width, int height)
{
    std::vector<uint8_t> rgba((size_t)width * height * 4);
    for (size_t i = 0; i < (size_t)width * height; i++) {
        rgba[i * 4] = pixels[i] >> 16;
        rgba[i * 4 + 1] = pixels[i] >> 8;
        rgba[i * 4 + 2] = pixels[i];
        rgba[i * 4 + 3] = pixels[i] >> 24;
    }
    assert(stbi_write_png(path.c_str(), width, height, 4, rgba.data(), width * 4));
}

int main(int argc, char** argv)
{
    std::string assets = argc > 1 ? argv[1] : "assets";
    rnds::setDecoder(decode);
    banana::Splash splash;
    for (int width : { 640, 1024, 1280 }) {
        int height = width * 3 / 4;
        size_t n = (size_t)width * height;
        for (auto palette : { "dark", "light" }) {
            assert(splash.load(assets + "/splash", assets + "/banana/banana-48.png", palette, width, height));
            assert(splash.played());
            std::vector<uint32_t> top(n + 2, 0xdeadbeef), bottom(n + 2, 0xdeadbeef);
            for (double t : { 0., 300., 600., 900., 1400. }) {
                splash.draw(top.data() + 1, bottom.data() + 1, t, true);
                assert(top.front() == 0xdeadbeef && top.back() == 0xdeadbeef);
                assert(bottom.front() == 0xdeadbeef && bottom.back() == 0xdeadbeef);
                assert(std::find(top.begin() + 1, top.end() - 1, 0xdeadbeef) == top.end() - 1);
                assert(std::find(bottom.begin() + 1, bottom.end() - 1, 0xdeadbeef) == bottom.end() - 1);
                assert(!std::equal(top.begin() + 1, top.end() - 1, bottom.begin() + 1));
            }
            if (argc > 2 && width == 1280 && std::string(palette) == "dark") {
                std::vector<uint32_t> wide(1920 * 1080);
                banana::fitScanout(reinterpret_cast<uint8_t*>(wide.data()), 1920 * 4,
                    1920, 1080, 0, top.data() + 1, width, height);
                save(std::string(argv[2]) + "-top.png", wide.data(), 1920, 1080);
                save(std::string(argv[2]) + "-bottom.png", bottom.data() + 1, width, height);
            }
            for (double t : { 0., 300., 600., 1000., 1300. }) {
                splash.drawOutro(top.data() + 1, bottom.data() + 1, t);
                assert(top.front() == 0xdeadbeef && top.back() == 0xdeadbeef);
                assert(bottom.front() == 0xdeadbeef && bottom.back() == 0xdeadbeef);
            }
        }
    }
    banana::PanelSplash pair;
    assert(pair.load(assets + "/splash", assets + "/banana/banana-48.png", "dark", 1280, 960, 1707));
    std::vector<uint32_t> wt(1707 * 960 + 2, 0xdeadbeef), wb(1280 * 960 + 2, 0xdeadbeef);
    for (double t : { 0., 600., 1400. }) {
        pair.draw(wt.data() + 1, wb.data() + 1, t, true);
        assert(wt.front() == 0xdeadbeef && wt.back() == 0xdeadbeef);
        assert(wb.front() == 0xdeadbeef && wb.back() == 0xdeadbeef);
        assert(std::find(wt.begin()+1, wt.end()-1, 0xdeadbeef) == wt.end()-1);
    }
    if (argc > 2) save(std::string(argv[2]) + "-widescreen.png", wt.data()+1, 1707, 960);
    for (double t : { 0., 600., 1100., 1300. }) {
        pair.drawOutro(wt.data()+1, wb.data()+1, t);
        assert(wt.front() == 0xdeadbeef && wt.back() == 0xdeadbeef);
        assert(wb.front() == 0xdeadbeef && wb.back() == 0xdeadbeef);
    }
    assert(!splash.load("/missing-splash", "missing.png", "dark", 1280, 960));
    assert(!splash.played());
    assert(!splash.load(assets + "/splash", "missing.png", "dark", 1280, 960));
    assert(!splash.played());
    puts("splash: distinct top/bottom, boot/shutdown, three resolutions and failed loads passed");
}
