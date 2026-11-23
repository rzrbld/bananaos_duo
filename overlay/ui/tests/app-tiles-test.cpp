// Exercise the actual library scan: apps are home tiles, ports remain ports.
#include "library.h"
#include <cassert>
#include <filesystem>
#include <fstream>
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../third_party/stb_image_write.h"
namespace banana { std::string themedIcon(const std::string&, const std::string& def) { return def; } }
int main(int argc, char** argv) {
    assert(argc == 2);
    namespace fs = std::filesystem;
    fs::path root = argv[1]; fs::remove_all(root); fs::create_directories(root/"banana");
    auto write = [](const fs::path& path, const std::string& text) {
        fs::create_directories(path.parent_path()); std::ofstream(path) << text;
    };
    write(root/"store/tiles/GBA DS.sh", "#!/bin/bash\n");
    write(root/"roms/ports/Quake.sh", "#!/bin/bash\n");
    write(root/"roms/ports/PortMaster.sh", "#!/bin/bash\n");
    write(root/"builtin/Slopetanium.app", "");
    write(root/"assets/systems.cfg", "slopetanium slopetanium.png #2eae62 Slopetanium [app]\nstoreapps apps.png #2eae62 Store\nports ports.png #3d8ec4 PortMaster\n");
    write(root/"systems.conf", "[slopetanium]\nname=Slopetanium\nfolder="+(root/"builtin").string()+"\next=app\nrun=/usr/libexec/banana/run-slopetanium %ROM%\n[storeapps]\nfolder="+(root/"store/tiles").string()+"\next=sh\nflat=yes\nrun=/usr/libexec/banana/run-store-app %ROM%\n[ports]\nfolder=ports\next=sh\nflat=yes\nrun=/usr/libexec/banana/run-port %ROM%\n[files]\nfolder=absent-files\next=app\n");
    banana::Library lib((root/"systems.conf").string(), (root/"roms").string(), (root/"banana").string(), (root/"assets").string());
    lib.scan();
    assert(lib.systemCount() == 3);
    int apps=0, ports=0, managers=0;
    for (int i=0;i<lib.systemCount();++i) {
        auto sys=lib.system(i);
        if (sys.id=="slopetanium") { assert(sys.app); ++managers; }
        if (sys.id=="app:GBA DS.sh") { assert(sys.app); assert(sys.name=="GBA DS"); assert(lib.shelf(i).games.size()==1); ++apps; }
        if (sys.id=="ports") { assert(!sys.app); assert(lib.shelf(i).games.size()==2); ++ports; }
        assert(sys.id!="storeapps");
    }
    assert(apps==1 && ports==1 && managers==1);
    // Returning from the manager must notice installs and removals immediately.
    write(root/"store/tiles/Reader.sh", "#!/bin/bash\n"); lib.scan(); assert(lib.systemCount()==4);
    for (int i=0;i<lib.systemCount();++i) if (lib.system(i).id=="app:Reader.sh") { lib.openLibrary(i); lib.toggleGameFav(0); break; }
    lib.scan();
    bool checked=false;
    for (int i=0;i<lib.systemCount();++i) if (lib.shelf(i).favorites) {
        const auto& fav=lib.shelf(i); assert(fav.games.size()==1);
        assert(lib.system(fav.sysOf[0]).id=="app:Reader.sh"); checked=true;
    }
    assert(checked);
    // Remove the favorite again before checking the normal shelf count.
    for (int i=0;i<lib.systemCount();++i) if (lib.system(i).id=="app:Reader.sh") { assert(lib.shelf(i).games[0].fav); lib.openLibrary(i); lib.toggleGameFav(0); break; }
    fs::remove(root/"store/tiles/GBA DS.sh"); lib.scan(); assert(lib.systemCount()==3);
    fs::remove_all(root);
}
