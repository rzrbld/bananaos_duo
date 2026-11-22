#include "../src/plane-selection.h"
#include <cassert>
#include <cstdio>
using banana::PrimaryPlaneCandidate;
using banana::selectPrimaryPlane;
int main()
{
    // QCOM primary planes can both drive either screen (actual mask 0xff).
    std::vector<PrimaryPlaneCandidate> cold = {{47,0xff,0,true},{53,0xff,0,true},{59,0xff,0,false}};
    auto top = selectPrimaryPlane(cold,65,0);
    auto bottom = selectPrimaryPlane(cold,66,1,top);
    assert(top == 47 && bottom == 53 && top != bottom);
    std::vector<PrimaryPlaneCandidate> warm = {{47,0xff,65,true},{53,0xff,66,true}};
    assert(selectPrimaryPlane(warm,66,1) == 53);
    assert(selectPrimaryPlane(warm,65,0) == 47);
    warm.pop_back();
    assert(selectPrimaryPlane(warm,66,1) == 0); // never steal the top's plane
    cold[0].possibleCrtcs = 1; cold[1].possibleCrtcs = 2;
    assert(selectPrimaryPlane(cold,66,1) == 53);
    assert(selectPrimaryPlane(cold,65,-1) == 0);
    assert(selectPrimaryPlane(cold,65,32) == 0);
    assert(selectPrimaryPlane({{59,0xff,0,false}},65,0) == 0);
    puts("primary plane selection passed");
}
