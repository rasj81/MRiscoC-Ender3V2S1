#include <stdio.h>
#include <pigpio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
#include <signal.h>
#include <termios.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdint.h>
#include <pthread.h>
#include <sched.h>
#include <stdatomic.h>

#define FIFO_CTL       0x38
#define FIFO_STATUS    0x39
#define FIFO_DEPTH     32
#define FIFO_STREAM_WM 0x90   /* stream mode (D7:D6 = 10), watermark 16 */
#define DATA_FORMAT    0x31
#define DATA_FORMAT_B  0x0B
#define READ_BIT       0x80
#define MULTI_BIT      0x40
#define BW_RATE        0x2C
#define POWER_CTL      0x2D
#define DATAX0         0x32
#define DEVID          0x00
#define EXPECTED_DEVID 0xE5

#define CODE_VERSION "0.4-fifo1"

const int freqDefault = 250;
const int freqMax = 3200;
const int speedSPI = 2000000;
const int coldStartSamples = 2;
const double coldStartDelay = 0.1;
const double accConversion = 2 * 16.0 / 8192.0;

volatile sig_atomic_t keepRunning = 1;

void intHandler(int dummy) {
    keepRunning = 0;
}

void printUsage() {
    printf("adxl345spi (version %s)\n"
           "Usage: adxl345spi [OPTION]...\n"
           "  -s, --save FILE     Save data to specified FILE\n"
           "  -f, --freq FREQ     Sampling rate in Hz (default: %d, max: %d)\n"
           "  -t, --time SECONDS  Stop after SECONDS seconds\n",
           CODE_VERSION, freqDefault, freqMax);
}

int kbhit() {
    struct termios oldt, newt;
    int ch;
    int oldf;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~(ICANON | ECHO);
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
    fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
    ch = getchar();
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    fcntl(STDIN_FILENO, F_SETFL, oldf);
    if (ch != EOF) {
        ungetc(ch, stdin);
        return 1;
    }
    return 0;
}

int readBytes(int handle, char *data, int count) {
    char address = data[0];
    data[0] |= READ_BIT;
 
    // Set MUTI_BIT only for sequential reads from DATAX0
    if (address == DATAX0) {
        data[0] |= MULTI_BIT;
    }

    return spiXfer(handle, data, data, count);
}

int writeBytes(int handle, char *data, int count) {
    // MULTI_BIT is only used for multi-byte READs.
    return spiWrite(handle, data, count);
}

/* ---- FIFO capture (save mode at a native ADXL345 output data rate) ------
 *
 * The sensor samples on its own clock into its 32-entry FIFO (stream mode);
 * the host drains it every <= 2 ms, so host stalls shorter than the FIFO
 * depth (10 ms at 3200 Hz) lose nothing.  Each sample is timestamped as
 * index / rate, so the time column is evenly spaced.  A writer thread
 * formats rows from a ring buffer so file I/O never blocks sampling.
 */

/* BW_RATE code for a native output data rate, or -1 if none matches. */
static int odrCode(double freq) {
    static const double rates[] = {3200, 1600, 800, 400, 200, 100, 50, 25};
    static const int codes[] = {0x0F, 0x0E, 0x0D, 0x0C, 0x0B, 0x0A, 0x09, 0x08};
    int k;
    for (k = 0; k < (int)(sizeof(rates) / sizeof(rates[0])); k++) {
        if (fabs(freq - rates[k]) < 1e-9) return codes[k];
    }
    return -1;
}

static double monoNow(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

#define RING_SIZE (1u << 16)   /* 65536 samples, ~20 s of slack at 3200 Hz */

typedef struct { double t; int16_t x, y, z; } sample_t;

static sample_t ring[RING_SIZE];
static atomic_uint ringHead;      /* advanced by the sampler */
static atomic_uint ringTail;      /* advanced by the writer */
static atomic_int samplerDone;

static void *writerThread(void *arg) {
    FILE *f = (FILE *)arg;
    double lastFlush = monoNow();
    for (;;) {
        unsigned tail = atomic_load_explicit(&ringTail, memory_order_relaxed);
        unsigned head = atomic_load_explicit(&ringHead, memory_order_acquire);
        if (tail == head) {
            if (atomic_load_explicit(&samplerDone, memory_order_acquire) &&
                head == atomic_load_explicit(&ringHead, memory_order_acquire)) {
                break;
            }
            fflush(f);
            lastFlush = monoNow();
            usleep(5000);
            continue;
        }
        while (tail != head) {
            const sample_t *s = &ring[tail & (RING_SIZE - 1)];
            fprintf(f, "%.5f,%.5f,%.5f,%.5f\n", s->t,
                    s->x * accConversion, s->y * accConversion, s->z * accConversion);
            tail++;
        }
        atomic_store_explicit(&ringTail, tail, memory_order_release);
        if (monoNow() - lastFlush > 0.05) {
            fflush(f);
            lastFlush = monoNow();
        }
    }
    fflush(f);
    return NULL;
}

static int writeReg(int h, char reg, char value) {
    char d[2] = { reg, value };
    return writeBytes(h, d, 2) == 2 ? 0 : -1;
}

static int fifoSave(int h, double rate, int code, const char *path, int duration) {
    char d[7];
    int rc = 0;

    printf("Press Q to stop\n");

    FILE *f = fopen(path, "w");
    if (!f) {
        perror("Failed to open file");
        return 1;
    }
    fprintf(f, "time,x,y,z\n");
    fflush(f);

    /* Standby, set the output data rate, clear the FIFO (bypass), then
     * stream mode, then measure.  DATA_FORMAT was set by the caller. */
    if (writeReg(h, POWER_CTL, 0x00) || writeReg(h, BW_RATE, (char)code) ||
        writeReg(h, FIFO_CTL, 0x00) || writeReg(h, FIFO_CTL, FIFO_STREAM_WM) ||
        writeReg(h, POWER_CTL, 0x08)) {
        fprintf(stderr, "Device error: failed to configure ADXL345 FIFO\n");
        fclose(f);
        return 1;
    }

    atomic_store(&ringHead, 0);
    atomic_store(&ringTail, 0);
    atomic_store(&samplerDone, 0);
    pthread_t writer;
    if (pthread_create(&writer, NULL, writerThread, f) != 0) {
        fprintf(stderr, "Device error: failed to start writer thread\n");
        writeReg(h, FIFO_CTL, 0x00);
        fclose(f);
        return 1;
    }

    /* Real-time priority for the sampling loop only; harmless if refused. */
    struct sched_param sp;
    memset(&sp, 0, sizeof(sp));
    sp.sched_priority = 50;
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &sp);

    const double period = 1.0 / rate;
    double poll = 8 * period;
    if (poll > 0.002) poll = 0.002;

    unsigned long idx = 0;          /* sample index; timestamp = idx * period */
    unsigned long total = 0;        /* samples written */
    unsigned long overruns = 0, lostEstimate = 0, ringDropped = 0;
    double baseline = 0;            /* host-vs-sensor offset, tracks clock drift */
    int haveBaseline = 0;
    int k;
    double tStart = monoNow();

    while (keepRunning) {
        double now = monoNow();
        if (duration > 0 && now - tStart >= duration) break;
        if (kbhit()) {
            char ch = getchar();
            if (ch == 'q' || ch == 'Q') break;
        }

        d[0] = FIFO_STATUS;
        d[1] = 0;
        if (readBytes(h, d, 2) != 2) {
            fprintf(stderr, "Device error: FIFO_STATUS read failed\n");
            rc = 1;
            break;
        }
        int n = d[1] & 0x3F;
        double behind = (now - tStart) * rate - (double)(idx + n);

        if (n >= FIFO_DEPTH) {
            /* FIFO full: newer samples may have overwritten unread ones.
             * Skip the index forward by the estimated loss so the time
             * column shows a real gap instead of silently compressing. */
            long lost = haveBaseline ? (long)(behind - baseline + 0.5) : 0;
            overruns++;
            if (lost > 0) {
                idx += (unsigned long)lost;
                lostEstimate += (unsigned long)lost;
            }
            if (overruns <= 5) {
                fprintf(stderr, "Warning: ADXL345 FIFO overrun at %.3f s (~%ld samples lost)\n",
                        now - tStart, lost > 0 ? lost : 0);
            }
        } else {
            baseline = haveBaseline ? 0.98 * baseline + 0.02 * behind : behind;
            haveBaseline = 1;
        }

        for (k = 0; k < n; k++) {
            d[0] = DATAX0;
            if (readBytes(h, d, 7) != 7) {
                fprintf(stderr, "Device error: FIFO data read failed\n");
                rc = 1;
                break;
            }
            const unsigned char *u = (const unsigned char *)d;
            int16_t x = (int16_t)((u[2] << 8) | u[1]);
            int16_t y = (int16_t)((u[4] << 8) | u[3]);
            int16_t z = (int16_t)((u[6] << 8) | u[5]);
            unsigned head = atomic_load_explicit(&ringHead, memory_order_relaxed);
            unsigned tail = atomic_load_explicit(&ringTail, memory_order_acquire);
            if (head - tail >= RING_SIZE) {
                ringDropped++;       /* writer fell behind; leave a gap */
                idx++;
                continue;
            }
            sample_t *s = &ring[head & (RING_SIZE - 1)];
            s->t = idx * period;
            s->x = x;
            s->y = y;
            s->z = z;
            atomic_store_explicit(&ringHead, head + 1, memory_order_release);
            idx++;
            total++;
        }
        if (rc) break;
        time_sleep(poll);
    }

    double tElapsed = monoNow() - tStart;
    writeReg(h, FIFO_CTL, 0x00);    /* leave the sensor in bypass mode */

    atomic_store_explicit(&samplerDone, 1, memory_order_release);
    pthread_join(writer, NULL);
    if (fclose(f) != 0) {
        perror("Failed to close file");
        rc = 1;
    }

    if (overruns) {
        fprintf(stderr, "Warning: ADXL345 FIFO overrun %lu time(s), ~%lu samples lost\n",
                overruns, lostEstimate);
    }
    if (ringDropped) {
        fprintf(stderr, "Warning: writer fell behind, %lu samples dropped\n", ringDropped);
    }
    printf("Saved %lu samples in %.2f seconds (%.1f Hz) to %s\n",
           total, tElapsed, total / tElapsed, path);
    return rc;
}

int main(int argc, char *argv[]) {
    int i;
    signal(SIGINT, intHandler);  // handle Ctrl+C

    int bSave = 0;
    int duration = 0;
    char vSave[256] = "";
    double vFreq = freqDefault;

    for (i = 1; i < argc; i++) {
        if ((strcmp(argv[i], "-s") == 0) || (strcmp(argv[i], "--save") == 0)) {
            bSave = 1;
            if (i + 1 < argc) {
                strcpy(vSave, argv[++i]);
            } else {
                printUsage();
                return 1;
            }
        } else if ((strcmp(argv[i], "-f") == 0) || (strcmp(argv[i], "--freq") == 0)) {
            if (i + 1 < argc) {
                vFreq = atof(argv[++i]);
                if (vFreq < 1 || vFreq > freqMax) {
                    printf("Invalid frequency. Must be between 1 and %d Hz.\n", freqMax);
                    return 1;
                }
            } else {
                printUsage();
                return 1;
            }
        } else if ((strcmp(argv[i], "-t") == 0) || (strcmp(argv[i], "--time") == 0)){
            if (i + 1 < argc) {
                duration = atoi(argv[++i]);
                if (duration < 1) {
                    printf("Invalid duration.\n");
                    return 1;
                }
            } else {
                printUsage();
                return 1;
            }
        } else {
            printUsage();
            return 1;
        }
    }

    if (gpioInitialise() < 0) {
        printf("GPIO initialization failed.\n");
        return 1;
    }

    int h = spiOpen(0, speedSPI, 3);

    char devid_check[2] = { DEVID | READ_BIT, 0x00 };
    if (spiXfer(h, devid_check, devid_check, 2) != 2) {
        fprintf(stderr, "Failed to read device ID from ADXL345.\n");
        spiClose(h);
        gpioTerminate();
        return 1;
    }
    if ((unsigned char)devid_check[1] != EXPECTED_DEVID) {
        fprintf(stderr, "Unexpected device ID: 0x%02X (expected 0x%02X)\n",
                (unsigned char)devid_check[1], EXPECTED_DEVID);
        spiClose(h);
        gpioTerminate();
        return 1;
    }

    char data[7];

    // Configure ADXL345
    data[0] = BW_RATE;
    data[1] = 0x0F;
    if (writeBytes(h, data, 2) != 2) {
        fprintf(stderr, "Failed to write BW_RATE register (0x%02X)\n", BW_RATE);
        spiClose(h);
        gpioTerminate();
        return 1;
    }

    data[0] = DATA_FORMAT;
    data[1] = DATA_FORMAT_B;
    if (writeBytes(h, data, 2) != 2) {
        fprintf(stderr, "Failed to write DATA_FORMAT register (0x%02X)\n", DATA_FORMAT);
        spiClose(h);
        gpioTerminate();
        return 1;
    }

    data[0] = POWER_CTL;
    data[1] = 0x08;
    if (writeBytes(h, data, 2) != 2) {
        fprintf(stderr, "Failed to write POWER_CTL register (0x%02X)\n", POWER_CTL);
        spiClose(h);
        gpioTerminate();
        return 1;
    }

    // Polling modes read DATAX directly; make sure the FIFO is bypassed
    // even if an earlier FIFO capture was interrupted.
    writeReg(h, FIFO_CTL, 0x00);

    double delay = 1.0 / vFreq;

    if (bSave && odrCode(vFreq) >= 0) {
        int rc = fifoSave(h, vFreq, odrCode(vFreq), vSave, duration);
        spiClose(h);
        gpioTerminate();
        return rc;
    }

    if (!bSave) {
        for (i = 0; i < coldStartSamples; i++) {
            data[0] = DATAX0;
            readBytes(h, data, 7);
            time_sleep(coldStartDelay);
        }

        printf("Press Q to stop");
        printf("\n");
        double tStart = time_time();
        double tNow, tElapsed = 0;
        int samples = 0;
        double t = 0;
        int16_t x, y, z;

        while (keepRunning) {
            tNow = time_time();
            tElapsed = tNow - tStart;
            if (duration > 0 && tElapsed >= duration) break;
            if (kbhit()) {
                char ch = getchar();
                if (ch == 'q' || ch == 'Q') break;
            }

            data[0] = DATAX0;
            if (readBytes(h, data, 7) == 7) {
                x = (data[2] << 8) | data[1];
                y = (data[4] << 8) | data[3];
                z = (data[6] << 8) | data[5];
                t = time_time() - tStart;
                printf("time = %.3f, x = %.3f, y = %.3f, z = %.3f\n",
                       t, x * accConversion, y * accConversion, z * accConversion);
                samples++;
            }
            time_sleep(delay);
        }

        tElapsed = time_time() - tStart;
        printf("Captured %d samples in %.2f seconds (%.1f Hz)\n", samples, tElapsed, samples / tElapsed);
        spiClose(h);
        gpioTerminate();
        return 0;

    } else {
        printf("Press Q to stop\n");

        FILE *f = fopen(vSave, "w");
        if (!f) {
            perror("Failed to open file");
            spiClose(h);
            gpioTerminate();
            return 1;
        }
        fprintf(f, "time,x,y,z\n");

        const int flushEvery = 16; /* was 1000: writing 1000 rows inline stalled sampling ~5.6 ms */
        int bufferIndex = 0;
        int totalSamples = 0;

        double *bt = malloc(sizeof(double) * flushEvery);
        double *bx = malloc(sizeof(double) * flushEvery);
        double *by = malloc(sizeof(double) * flushEvery);
        double *bz = malloc(sizeof(double) * flushEvery);

        if (!bt || !bx || !by || !bz) {
            perror("Failed to allocate buffer");
            fclose(f);
            spiClose(h);
            gpioTerminate();
            return 1;
        }

        int16_t x, y, z;
        double tStart = time_time();
        double tNow, tElapsed = 0, nextSample = 0;

        while (keepRunning) {
            tNow = time_time();
            tElapsed = tNow - tStart;
            if (duration > 0 && tElapsed >= duration) break;
            tNow = time_time() - tStart;
            if (tNow < nextSample)
                continue;

            if (kbhit()) {
                char ch = getchar();
                if (ch == 'q' || ch == 'Q') break;
            }

            nextSample += delay; // exact next sampling time

            // Read one sample
            data[0] = DATAX0;
            if (readBytes(h, data, 7) == 7) {
                x = (data[2] << 8) | data[1];
                y = (data[4] << 8) | data[3];
                z = (data[6] << 8) | data[5];

                double t = time_time() - tStart;
                bt[bufferIndex] = t;
                bx[bufferIndex] = x * accConversion;
                by[bufferIndex] = y * accConversion;
                bz[bufferIndex] = z * accConversion;
                bufferIndex++;
                totalSamples++;
            }

            if (bufferIndex >= flushEvery) {
                for (i = 0; i < flushEvery; i++) {
                    fprintf(f, "%.5f,%.5f,%.5f,%.5f\n", bt[i], bx[i], by[i], bz[i]);
                }
                fflush(f);
                bufferIndex = 0;
            }
        }

        // Write remaining samples
        for (i = 0; i < bufferIndex; i++) {
            fprintf(f, "%.5f,%.5f,%.5f,%.5f\n", bt[i], bx[i], by[i], bz[i]);
        }
        fflush(f);
        fclose(f);

        free(bt); free(bx); free(by); free(bz);
        tElapsed = time_time() - tStart;
        spiClose(h);
        gpioTerminate();
        printf("Saved %d samples in %.2f seconds (%.1f Hz) to %s\n",
               totalSamples, tElapsed, totalSamples / tElapsed, vSave);
    }

    return 0;
}
