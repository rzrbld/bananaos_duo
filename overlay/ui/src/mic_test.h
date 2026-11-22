#pragma once
#include <atomic>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace banana {
// Owns only RAM audio. Never monitors the microphone through the speakers.
class MicTest {
public:
    ~MicTest() { stop(); }
    void start();
    void stop();
    void record() { command = 1; }
    void play() { command = 2; }
    int level() const { return meter.load(); }
    bool ready() const { return recorded.load(); }
    std::string status() const;
private:
    void run();
    void message(const std::string& text);
    std::thread worker;
    std::atomic<bool> quit{false}, recorded{false};
    std::atomic<int> command{0}, meter{0};
    mutable std::mutex lock;
    std::string state;
};
}
