// Exercise real library order/persistence, collection mapping and home UI input.
#include "library.h"
#include "soft.h"
#include "../rnds/HomeGrid.h"
#include <cassert>
#include <filesystem>
#include <fstream>
#include <iostream>
#define STB_IMAGE_IMPLEMENTATION
#define STBI_ONLY_PNG
#define STBI_ONLY_JPEG
#include "../third_party/stb_image.h"
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "../third_party/stb_image_write.h"
using namespace banana;
static rnds::Bitmap decode(const std::string& path) {
 rnds::Bitmap b;int w,h,n;auto px=stbi_load(path.c_str(),&w,&h,&n,4);
 if(px) {b.w=w;b.h=h;b.px.assign(px,px+(size_t)w*h*4);stbi_image_free(px);}return b;
}
static void selectedAccent(SoftBackend& be,const rnds::HomeGrid& g,int at) {
 int left=be.width(1),right=-1,pixels=0;
 for(int y=std::max(0,(int)g.y(at)-8);y<std::min(be.height(),(int)(g.y(at)+g.icon)+8);++y)
  for(int x=std::max(0,(int)g.x(at)-8);x<std::min(be.width(1),(int)(g.x(at)+g.icon)+8);++x)
   if((be.pixels(1)[(size_t)y*be.width(1)+x]&0xffffff)==rnds::accent.base) {left=std::min(left,x);right=std::max(right,x);++pixels;}
 assert(right-left+1>g.icon); // Selected tile extends beyond the normal tile footprint.
 assert(pixels>g.icon*8); // A substantial colored outline, not a tiny colored marker.
}

static void write(const std::filesystem::path& p,const std::string& s) {std::filesystem::create_directories(p.parent_path());std::ofstream(p)<<s;}
static int find(Library& lib,const std::string& id) {for(int i=0;i<lib.systemCount();++i)if(lib.system(i).id==id)return i;return -1;}
static void save(SoftBackend& be,const std::string& path) {
 for(int s=0;s<2;++s) {
  int w=be.width(s),h=be.height();
  size_t visible=0;for(size_t i=0;i<(size_t)w*h;++i) if(be.pixels(s)[i]&0xffffff)++visible;
  assert(visible>(size_t)w*h/2); // Catch a view that forgot to commit its frame.
  std::vector<unsigned char> rgb((size_t)w*h*3);
  for(size_t i=0;i<(size_t)w*h;++i) {auto p=be.pixels(s)[i];rgb[i*3]=p>>16;rgb[i*3+1]=p>>8;rgb[i*3+2]=p;}
  assert(stbi_write_png((path+(s?"-bottom.png":"-top.png")).c_str(),w,h,3,rgb.data(),w*3));
 }
}
int main(int argc,char**argv) {
 rnds::setDecoder(decode);assert(rnds::setAccent("blue"));
 assert(argc==3);namespace fs=std::filesystem;fs::path out=argv[2];fs::create_directories(out);
 fs::path root=out/"fixture";fs::remove_all(root);fs::create_directories(root/"banana");
 std::string conf="[storeapps]\nfolder="+(root/"tiles").string()+"\next=sh\nflat=yes\nrun=test-app %ROM%\n";
 write(root/"tiles/Reader.sh", "#!/bin/sh\n");write(root/"tiles/Player.sh","#!/bin/sh\n");
 for(int i=0;i<11;++i) conf+="[sys"+std::to_string(i)+"]\nname=System "+std::to_string(i)+"\nfolder=sys"+std::to_string(i)+"\next=gba\nalways=yes\nrun=test-game %ROM%\n";
 conf+="[ports]\nfolder=ports\next=sh\nflat=yes\nrun=test-port %ROM%\n";
 write(root/"roms/ports/Quake.sh","#!/bin/sh\n");write(root/"roms/ports/PortMaster.sh","#!/bin/sh\n");write(root/"systems.conf",conf);
 Library lib((root/"systems.conf").string(),(root/"roms").string(),(root/"banana").string(),argv[1]);lib.scan();
 assert(lib.homeRows()==1 && !lib.homePorts());assert(lib.systemCount()==15);
 // Store section deliberately precedes emulators in conf: default home still groups emulators first.
 bool app=false;for(int i=0;i<lib.systemCount();++i) {if(lib.system(i).app)app=true;else assert(!app);}
 lib.setHomePorts(true);assert(find(lib,"port:Quake.sh")>=0 && find(lib,"port:PortMaster.sh")==-1);
 int port=find(lib,"port:Quake.sh");lib.openLibrary(port);assert(lib.gameKey(0)=="ports/Quake.sh");lib.toggleGameFav(0);lib.recordPlay(0,8);lib.arrange();
 for(int i=0;i<lib.systemCount();++i)if(lib.shelf(i).favorites) {
  assert(lib.shelf(i).games.size()==1);assert(lib.system(lib.shelf(i).sysOf[0]).id=="ports");
 }
 assert(lib.countMatches("Quake")==1);
 int reader=find(lib,"app:Reader.sh");assert(lib.moveHome(reader,0));assert(lib.system(0).id=="app:Reader.sh");lib.arrange();assert(lib.system(0).id=="app:Reader.sh");
 // Collection indices must follow a custom reorder, including moving a collection.
 int fav=find(lib,"favorites");assert(fav>=0);assert(lib.moveHome(fav,1));
 fav=find(lib,"favorites");assert(lib.system(lib.shelf(fav).sysOf[0]).id=="ports");
 lib.setHomeRows(9);assert(lib.homeRows()==4);lib.scan();assert(lib.system(0).id=="app:Reader.sh" && lib.homePorts() && lib.homeRows()==4);
 Library again((root/"systems.conf").string(),(root/"roms").string(),(root/"banana").string(),argv[1]);again.scan();assert(again.homeRows()==4 && again.homePorts());assert(again.system(0).id=="app:Reader.sh");
 lib.setHomeRows(1);lib.testPower.percent=70;
 SoftBackend be(640,480,854);rnds::UI ui(&lib,&be,argv[1],1,"dark");ui.setHome(0);ui.update(1000);
 assert(ui.press(rnds::UI::X) && ui.editingHome());assert(lib.pendingLaunch()==-1);
 ui.press(rnds::UI::A);ui.press(rnds::UI::RIGHT);ui.press(rnds::UI::B);assert(ui.systemIndex()==0 && lib.system(0).id=="app:Reader.sh");
 ui.press(rnds::UI::A);ui.press(rnds::UI::RIGHT);ui.press(rnds::UI::A);assert(lib.system(1).id=="app:Reader.sh");
 // Picking up/placing an internal app also stays in edit mode: the host must not open it.
 ui.press(rnds::UI::Y);assert(!lib.homePorts());
 for(int rows=1;rows<=4;++rows) {
  lib.setHomeRows(rows);ui.setHome(0);ui.update(2000+rows*1000);ui.render();
  ui.finishWork();ui.update(2500+rows*1000);ui.render();save(be,(out/("rows-"+std::to_string(rows))).string());
  rnds::HomeGrid g(rows,lib.systemCount(),0,640);
  if(rows>1) selectedAccent(be,g,0);
  for(int i=0;i<std::min(g.capacity,lib.systemCount());++i) {
   assert(g.x(i)>=20 && g.x(i)+g.icon<=620);assert(g.y(i)>=90 && g.y(i)+g.icon+20<=376);
   assert(g.hit(g.x(i)+g.icon/2,g.y(i)+g.icon/2)==i);
  }
  ui.touch(1,48,442,true);ui.touch(1,48,442,false);assert(lib.homeRows()==std::min(4,rows+1));
 }
 ui.press(rnds::UI::R);assert(lib.homeRows()==3);ui.press(rnds::UI::L);assert(lib.homeRows()==4);
 ui.press(rnds::UI::X);assert(!ui.editingHome());ui.press(rnds::UI::DOWN);assert(ui.systemIndex()==rnds::HomeGrid(4,lib.systemCount(),0,640).columns);
 // Zoom is edit-only; the normal footer's X face enters editing in every density.
 for(int rows=1;rows<=4;++rows) {
  lib.setHomeRows(rows);ui.setHome(0);ui.update(20000+rows*1000);ui.render();ui.finishWork();ui.render();
  save(be,(out/("normal-rows-"+std::to_string(rows))).string());
  ui.touch(1,48,410,true);ui.touch(1,48,410,false);
  assert(lib.homeRows()==rows && !ui.editingHome());
  ui.touch(1,590,442,true);ui.touch(1,590,442,false);assert(ui.editingHome());
  ui.press(rnds::UI::B);assert(!ui.editingHome());
 }

 // The multi-row rail moves across pages without changing density or entering edit mode.
 lib.setHomeRows(2);ui.setHome(0);ui.touch(1,600,401,true);ui.touch(1,600,401,false);
 assert(ui.systemIndex()>=rnds::HomeGrid(2,lib.systemCount(),0,640).capacity && lib.homeRows()==2 && !ui.editingHome());
 ui.touch(1,25,401,true);ui.touch(1,25,401,false);assert(ui.systemIndex()<rnds::HomeGrid(2,lib.systemCount(),0,640).capacity);
 // Red accent and light theme must use the same selection contract.
 assert(rnds::setAccent("red"));lib.setHomeRows(4);SoftBackend lightBe(640,480,854);
 rnds::UI light(&lib,&lightBe,argv[1],1,"light");light.setHome(0);light.update(50000);light.render();light.finishWork();light.render();
 save(lightBe,(out/"light-red-grid").string());selectedAccent(lightBe,rnds::HomeGrid(4,lib.systemCount(),0,640),0);
 // Removing/reinstalling an app preserves stable identity and unrelated positions.
 fs::remove(root/"tiles/Reader.sh");lib.scan();write(root/"tiles/Reader.sh","#!/bin/sh\n");lib.scan();assert(find(lib,"app:Reader.sh")==1);
 for(int rows=1;rows<=4;++rows)for(int n:{0,1,5,31,103})for(int at=0;at<std::max(1,n);++at) {
  rnds::HomeGrid g(rows,n,at,640);assert(g.first<=at && at<g.first+g.capacity);
  if(n) {assert(g.vertical(at,1)>=0 && g.vertical(at,1)<n);assert(g.vertical(at,-1)>=0);}
 }
 std::cout<<"PASS: home grouping, persistent order/density, optional ports, collections, edit/cancel, touch and grid geometry\n";
}
