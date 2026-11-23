#pragma once
#include <algorithm>
#include <cmath>
namespace rnds {
// Shared by rendering, hit testing and D-pad navigation; dimensions are logical
// panel units, not pixels or the other display's resolution.
struct HomeGrid {
    int rows, columns, capacity, first, count;
    float width, icon, cellWidth, cellHeight;
    HomeGrid(int requestedRows, int items, int selected, float panelWidth)
        : rows(std::clamp(requestedRows,1,4)), count(std::max(0,items)), width(panelWidth) {
        icon = rows==1 ? 96 : rows==2 ? 80 : rows==3 ? 64 : 48;
        columns = std::max(1, int((width-40)/(icon+20)));
        capacity = rows*columns;
        first = std::max(0,selected)/capacity*capacity;
        cellWidth = (width-40)/columns; cellHeight = 286.0f/rows;
    }
    float x(int i) const { return 20 + ((i-first)%columns)*cellWidth + (cellWidth-icon)/2; }
    float y(int i) const { return 90 + ((i-first)/columns)*cellHeight + (cellHeight-icon-20)/2; }
    int hit(float px,float py) const {
        for(int i=first;i<std::min(count,first+capacity);++i)
            if(px>=x(i)-5 && px<x(i)+icon+5 && py>=y(i)-5 && py<y(i)+icon+21) return i;
        return -1;
    }
    int vertical(int at,int direction) const {
        int to=at+direction*columns;
        if(to<0) return at;
        if(to>=count) return direction>0 && at/columns<(count-1)/columns ? count-1 : at;
        return to;
    }
};
}
