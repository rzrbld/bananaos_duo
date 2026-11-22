#include "mic_test.h"
#ifdef BANANA_ALSA
#include <alsa/asoundlib.h>
#endif
#include <algorithm>
#include <cmath>
#include <chrono>

namespace banana {
std::string MicTest::status() const { std::lock_guard<std::mutex> guard(lock); return state; }
void MicTest::message(const std::string& text) { std::lock_guard<std::mutex> guard(lock); state = text; }
void MicTest::start() {
    stop(); quit = false; recorded = false; command = 0; meter = 0;
    message("Opening microphone..."); worker = std::thread(&MicTest::run, this);
}
void MicTest::stop() {
    quit = true;
    if (worker.joinable()) worker.join();
    recorded = false; meter = 0;
}
void MicTest::run() {
#ifndef BANANA_ALSA
    message("Microphone testing is unavailable in this build.");
#else
    constexpr unsigned rate = 48000, frames = 960, duration = 5 * rate;
    snd_pcm_t* capture = nullptr;
    std::vector<short> recording;
    recording.reserve(duration);
    bool saving = false;
    auto open = [&](snd_pcm_t** pcm, snd_pcm_stream_t stream, unsigned channels) {
        int err = snd_pcm_open(pcm, "default", stream, SND_PCM_NONBLOCK);
        if (err >= 0) err = snd_pcm_set_params(*pcm, SND_PCM_FORMAT_S16_LE,
            SND_PCM_ACCESS_RW_INTERLEAVED, channels, rate, 1, 60000);
        if (err >= 0 && stream == SND_PCM_STREAM_CAPTURE) err = snd_pcm_start(*pcm);
        if (err < 0) {
            message(std::string(stream == SND_PCM_STREAM_CAPTURE ? "Microphone: " : "Playback: ") + snd_strerror(err));
            if (*pcm) { snd_pcm_close(*pcm); *pcm = nullptr; }
        }
        return err >= 0;
    };
    if (!open(&capture, SND_PCM_STREAM_CAPTURE, 1)) return;
    message("Speak to test the microphone.");
    short samples[frames];
    while (!quit) {
        int action = command.exchange(0);
        if (action == 1) {
            recording.clear(); recorded = false; saving = true;
            message("Recording 5 seconds...");
        }
        if (action == 2 && recorded && !saving) {
            snd_pcm_close(capture); capture = nullptr; meter = 0;
            snd_pcm_t* playback = nullptr;
            if (open(&playback, SND_PCM_STREAM_PLAYBACK, 2)) {
                message("Playing recording...");
                std::vector<short> stereo(recording.size() * 2);
                for (size_t i = 0; i < recording.size(); ++i) stereo[2*i] = stereo[2*i+1] = recording[i];
                size_t pos = 0;
                while (!quit && pos < recording.size()) {
                    auto n = snd_pcm_writei(playback, stereo.data() + pos*2, std::min<size_t>(frames, recording.size()-pos));
                    if (n > 0) pos += n;
                    else if (n == -EAGAIN) snd_pcm_wait(playback, 50);
                    else if (snd_pcm_recover(playback, n, 1) < 0) { message("Recording playback failed."); break; }
                }
                // Nonblocking drain, bounded so leaving the page always stops promptly.
                for (int i = 0; !quit && i < 20 && snd_pcm_drain(playback) == -EAGAIN; ++i)
                    std::this_thread::sleep_for(std::chrono::milliseconds(10));
                snd_pcm_drop(playback); snd_pcm_close(playback);
            }
            if (quit || !open(&capture, SND_PCM_STREAM_CAPTURE, 1)) break;
            message("Speak to test the microphone.");
        }
        auto n = snd_pcm_readi(capture, samples, frames);
        if (n == -EAGAIN) { snd_pcm_wait(capture, 50); continue; }
        if (n < 0) {
            if (snd_pcm_recover(capture, n, 1) < 0) { message("Microphone capture failed."); break; }
            continue;
        }
        double energy = 0;
        for (int i = 0; i < n; ++i) energy += double(samples[i]) * samples[i];
        double rms = n ? std::sqrt(energy / n) / 32768.0 : 0;
        // dB scale: silence stays empty, quiet speech is visible without boosting the recording.
        meter = rms > 0 ? std::clamp(int((20*std::log10(rms)+60)*100/60), 0, 100) : 0;
        if (saving) {
            size_t count = std::min<size_t>(n, duration - recording.size());
            recording.insert(recording.end(), samples, samples + count);
            if (recording.size() == duration) {
                saving = false; recorded = true; message("Recording ready. Press X to listen.");
            }
        }
    }
    if (capture) snd_pcm_close(capture);
    meter = 0;
#endif
}
}
