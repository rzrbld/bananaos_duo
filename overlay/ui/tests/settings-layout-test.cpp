// Real rendered-page regression: widths, centring, and the unchanged lower panel.
#include "settings.h"
#include "soft.h"
#include "layout.h"
#include "carts.h"
#include <fstream>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <functional>
#include <vector>
#define STB_IMAGE_IMPLEMENTATION
#define STBI_ONLY_PNG
#define STBI_ONLY_JPEG
#include "../third_party/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../third_party/stb_image_write.h"

namespace banana {
struct EmptyLayoutSource : rnds::Source {
    int systemCount() override { return 0; } rnds::SysInfo system(int) override { return {}; }
    int gameCount() override { return 0; } rnds::GameInfo game(int) override { return {}; }
    std::string clockText() override { return "12:34"; } std::string dateText() override { return "23/11"; }
    float battery() override { return -1; } bool online() override { return false; }
    void selectSystem(int) override {} void selectGame(int) override {} int openLibrary(int) override { return 0; }
    void backToHome() override {} void launch(int) override {} void toggleSystemFav(int) override {}
    void toggleGameFav(int) override {} int resumeGame(int) override { return -1; }
};
struct SettingsLayoutTest {
    static void save(SoftBackend& be, const std::string& path) {
        for (int screen = 0; screen < 2; ++screen) {
            int w = be.width(screen), h = be.height();
            std::vector<unsigned char> rgb((size_t)w*h*3);
            for (size_t i=0; i<(size_t)w*h; ++i) {
                uint32_t p=be.pixels(screen)[i];
                rgb[i*3]=p>>16; rgb[i*3+1]=p>>8; rgb[i*3+2]=p;
            }
            assert(stbi_write_png((path+(screen?"-bottom.png":"-top.png")).c_str(), w,h,3,rgb.data(),w*3));
        }
    }
    static void centered(SoftBackend& be, float scale, int screen=0) {
        int lo=be.width(screen), hi=-1;
        for (int y=(int)(160*scale); y<(int)(290*scale); ++y)
            for (int x=0;x<be.width(screen);++x) {
                uint32_t p=be.pixels(screen)[(size_t)y*be.width(screen)+x];
                if (((p>>16)&255)>180 && ((p>>8)&255)>180 && (p&255)>150) {
                    lo=std::min(lo,x); hi=std::max(hi,x);
                }
            }
        assert(hi>=lo); // Missing font or missing text must not silently pass.
        double error=std::abs((lo+hi+1)/2.0-be.width(screen)/2.0);
        if(error>3*scale) fprintf(stderr,"centre error %.2f on %d px panel\n",error,be.width(screen));
        assert(error<=3*scale);
    }
    static void run(const std::string& assets, const std::string& dir) {
        std::filesystem::create_directories(dir+"/data");
        for (int height : {480,768,960}) {
            const float scale=height/480.0f;
            const int bottom=(int)std::lround(640*scale);
            std::vector<std::vector<uint32_t>> bottomReference;
            for (bool wide : {false,true}) {
                const int top=wide?(int)std::lround(height*16.0/9):bottom;
                SoftBackend be(bottom,height,top);
                Settings ui(&be,assets,dir+"/data",scale,"dark");
                assert(ui.R && ui.M);
                ui.setSystems({});
                ui.setLibraryPaths("",dir+"/roms");
                assert(std::abs(be.layoutWidth(0,scale)-top/scale)<0.01f);
                ui.installVersion="0.1.0-alpha.36";
                const std::vector<std::string> states={"checking","writing 42","verifying","done 0.1.0-alpha.36","failed: test failure"};
                for(size_t i=0;i<states.size();++i) {
                    ui.ustatus=states[i]; ui.updated=i==3; ui.applying=i<3;
                    ui.renderInstall(); centered(be,scale);
                    std::vector<uint32_t> pixels(be.pixels(1),be.pixels(1)+(size_t)bottom*height);
                    if(!wide) bottomReference.push_back(pixels);
                    else assert(pixels==bottomReference[i]);
                    if(height==480 && wide) save(be,dir+"/install-"+std::to_string(i));
                }
                ui.renderCard("Welcome", "Duo Lite",196,30); centered(be,scale);
                be.beginScreen(1);
                assert(std::abs(be.layoutWidth(scale)-640)<0.01f);
                be.endScreen();
                ui.langAsk=0; ui.renderLangAsk();
                // Prompts share the active-panel centring path too.
                if(height==480 && wide) save(be,dir+"/language");
                ui.langAsk=-1;
                for(int pattern=0;pattern<4;++pattern) {
                    ui.colPattern=pattern; ui.renderColors();
                    if(pattern==2) for(int x=1;x<top-1;++x)
                        assert((be.pixels(0)[(size_t)(200*scale)*top+x]&0xffffff)==0xffffff);
                }
                if(height==480 && wide) {
                    const std::vector<std::pair<const char*,void(Settings::*)()>> pages={
                        {"groups",&Settings::renderGroups},{"networks",&Settings::renderNetworks},
                        {"bluetooth",&Settings::renderBluetooth},{"keyboard",&Settings::renderKeyboard},
                        {"updates",&Settings::renderUpdates},{"speaker-eq",&Settings::renderEq},
                        {"microphone",&Settings::renderMic},{"box-art",&Settings::renderArt},
                        {"credits",&Settings::renderCredits},{"home-server-games",&Settings::renderPickGames},
                        {"game-options",&Settings::renderGame},{"themes",&Settings::renderThemes},{"achievements",&Settings::renderAch}};
                    for(auto p:pages) { fprintf(stderr,"render %s\n",p.first); (ui.*p.second)(); save(be,dir+"/"+p.first); }
                    ui.slides={Settings::SL_LANG,Settings::SL_WIFI,Settings::SL_TZ,Settings::SL_NAME,Settings::SL_RA,Settings::SL_ART,Settings::SL_DONE};
                    ui.wskipped.assign(ui.slides.size(),false);
                    for(size_t step=0;step<ui.slides.size();++step) {
                        ui.wsel=(int)step; ui.renderSetup(); save(be,dir+"/setup-"+std::to_string(step));
                    }
                    ui.openFiles(); ui.render(); save(be,dir+"/files");
                    ui.openSearch("layout"); ui.render(); save(be,dir+"/search");
                    EmptyLayoutSource empty;
                    CartMenu carts(&empty,&be,assets+"/../banana/fonts",scale);
                    carts.render(); centered(be,scale); save(be,dir+"/carts-empty");
                    // A theme variable using W must be recalculated for both
                    // panels, not inherited from the preceding bottom frame.
                    std::string json=dir+"/geometry.json";
                    std::ofstream(json) << R"({"vars":{"right":"=W - 20"},"screens":{"home":{
                      "top":[{"type":"rect","x":"=right","y":100,"w":10,"h":10,"fill":"#ff0000"}],
                      "bottom":[{"type":"rect","x":"=right","y":100,"w":10,"h":10,"fill":"#ff0000"}]}}})";
                    LayoutMenu layout(&empty,&be,json,scale,assets+"/fonts",assets+"/../banana/fonts");
                    assert(layout.errors().empty());
                    for(int frame=0;frame<3;++frame) {
                        layout.render();
                        for(int screen=0;screen<2;++screen) {
                            int x=be.width(screen)-15, y=105;
                            assert((be.pixels(screen)[(size_t)y*be.width(screen)+x]&0xffffff)==0xff0000);
                        }
                    }
                    save(be,dir+"/layout-theme");
                }
            }
        }
        puts("settings-layout: real install states, unequal widths, lower-panel identity, welcome and colour patterns passed");
    }
};
}
int main(int argc,char** argv) {
    if(argc!=3) { fprintf(stderr,"usage: %s assets output-directory\n",argv[0]); return 2; }
    setenv("BANANA_WIFI","/bin/false",1); setenv("BANANA_BLUETOOTH","/bin/false",1);
    setenv("BANANA_UPDATE","/bin/false",1);
    banana::SettingsLayoutTest::run(argv[1],argv[2]);
}
