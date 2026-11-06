/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

/**
 * Software SPI functions originally from Arduino Sd2Card Library
 * Copyright (c) 2009 by William Greiman
 * Adapted to the STM32F1 HAL
 */

#ifdef __STM32F1__

#include "../../inc/MarlinConfig.h"
#include <SPI.h>

// ------------------------
// Public functions
// ------------------------

#if ENABLED(SOFTWARE_SPI)

  // ------------------------
  // Software SPI (bit-banged on the pins given by SD_SCK_PIN, SD_MISO_PIN, SD_MOSI_PIN and SD_SS_PIN)
  // Used to read the Creality V4 onboard slot in SPI mode, see SD_SPI_MODE.
  // ------------------------

  #include "../shared/Delay.h"

  void spiBegin() {
    #if PIN_EXISTS(SD_SS)
      OUT_WRITE(SD_SS_PIN, HIGH);
    #endif
    OUT_WRITE(SD_SCK_PIN, HIGH);
    SET_INPUT(SD_MISO_PIN);
    OUT_WRITE(SD_MOSI_PIN, HIGH);
  }

  // Compile-time delays so the clock rates below are actually reached.
  // At 72MHz one clock is 14ns and calling a function costs about 3 clocks.
  #define CALLING_COST_NS  (3U * 1000000000U) / (F_CPU)
  static void (*delaySPIFunc)();
  static void delaySPI_125()  { DELAY_NS(125 - CALLING_COST_NS); }
  static void delaySPI_250()  { DELAY_NS(250 - CALLING_COST_NS); }
  static void delaySPI_500()  { DELAY_NS(500 - CALLING_COST_NS); }
  static void delaySPI_1000() { DELAY_NS(1000 - CALLING_COST_NS); }
  static void delaySPI_2000() { DELAY_NS(2000 - CALLING_COST_NS); }
  static void delaySPI_4000() { DELAY_NS(4000 - CALLING_COST_NS); }

  void spiInit(uint8_t spiRate) {
    switch (spiRate) {
      case SPI_FULL_SPEED:    delaySPIFunc =  &delaySPI_125; break;  // desired: max   actual: ~1 MHz
      case SPI_HALF_SPEED:    delaySPIFunc =  &delaySPI_125; break;
      case SPI_QUARTER_SPEED: delaySPIFunc =  &delaySPI_250; break;
      case SPI_EIGHTH_SPEED:  delaySPIFunc =  &delaySPI_500; break;
      case SPI_SPEED_5:       delaySPIFunc = &delaySPI_1000; break;
      case SPI_SPEED_6:       delaySPIFunc = &delaySPI_2000; break;
      default:                delaySPIFunc = &delaySPI_4000; break;  // ~125 kHz, used while the card starts up
    }
  }

  // Clock idles high; the card samples on the rising edge (what the SD SPI mode accepts)
  static uint8_t spiTransfer(uint8_t b) {
    for (uint8_t bits = 8; bits--;) {
      WRITE(SD_SCK_PIN, LOW);
      WRITE(SD_MOSI_PIN, b & 0x80);
      delaySPIFunc();
      WRITE(SD_SCK_PIN, HIGH);
      delaySPIFunc();
      b <<= 1;
      b |= (READ(SD_MISO_PIN) != 0);
    }
    DELAY_NS(125);
    return b;
  }

  uint8_t spiRec() {
    hal.isr_off();                      // no interrupts during a byte
    const uint8_t data = spiTransfer(0xFF);
    hal.isr_on();
    return data;
  }

  void spiRead(uint8_t *buf, uint16_t nbyte) {
    for (uint16_t i = 0; i < nbyte; i++) buf[i] = spiRec();
  }

  void spiSend(uint8_t b) {
    hal.isr_off();
    spiTransfer(b);
    hal.isr_on();
  }

  void spiSendBlock(uint8_t token, const uint8_t *buf) {
    spiSend(token);
    for (uint16_t i = 0; i < 512; i++) spiSend(buf[i]);
  }

#else

// ------------------------
// Hardware SPI
// ------------------------

/**
 * VGPV SPI speed start and F_CPU/2, by default 72/2 = 36Mhz
 */

/**
 * @brief  Begin SPI port setup
 *
 * @return Nothing
 *
 * @details Only configures SS pin since libmaple creates and initialize the SPI object
 */
void spiBegin() {
  #if PIN_EXISTS(SD_SS)
    OUT_WRITE(SD_SS_PIN, HIGH);
  #endif
}

/**
 * @brief  Initialize SPI port to required speed rate and transfer mode (MSB, SPI MODE 0)
 *
 * @param  spiRate Rate as declared in HAL.h (speed do not match AVR)
 * @return Nothing
 *
 * @details
 */
void spiInit(uint8_t spiRate) {
  /**
   * STM32F1 APB2 = 72MHz, APB1 = 36MHz, max SPI speed of this MCU if 18Mhz
   * STM32F1 has 3 SPI ports, SPI1 in APB2, SPI2/SPI3 in APB1
   * so the minimum prescale of SPI1 is DIV4, SPI2/SPI3 is DIV2
   */
  #if SPI_DEVICE == 1
    #define SPI_CLOCK_MAX SPI_CLOCK_DIV4
  #else
    #define SPI_CLOCK_MAX SPI_CLOCK_DIV2
  #endif
  uint8_t  clock;
  switch (spiRate) {
    case SPI_FULL_SPEED:    clock = SPI_CLOCK_MAX ;  break;
    case SPI_HALF_SPEED:    clock = SPI_CLOCK_DIV4 ; break;
    case SPI_QUARTER_SPEED: clock = SPI_CLOCK_DIV8 ; break;
    case SPI_EIGHTH_SPEED:  clock = SPI_CLOCK_DIV16; break;
    case SPI_SPEED_5:       clock = SPI_CLOCK_DIV32; break;
    case SPI_SPEED_6:       clock = SPI_CLOCK_DIV64; break;
    default:                clock = SPI_CLOCK_DIV2;  // Default from the SPI library
  }
  SPI.setModule(SPI_DEVICE);
  SPI.begin();
  SPI.setClockDivider(clock);
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
}

/**
 * @brief  Receive a single byte from the SPI port.
 *
 * @return Byte received
 *
 * @details
 */
uint8_t spiRec() {
  uint8_t returnByte = SPI.transfer(0xFF);
  return returnByte;
}

/**
 * @brief  Receive a number of bytes from the SPI port to a buffer
 *
 * @param  buf   Pointer to starting address of buffer to write to.
 * @param  nbyte Number of bytes to receive.
 * @return Nothing
 *
 * @details Uses DMA
 */
void spiRead(uint8_t *buf, uint16_t nbyte) {
  SPI.dmaTransfer(0, const_cast<uint8_t*>(buf), nbyte);
}

/**
 * @brief  Send a single byte on SPI port
 *
 * @param  b Byte to send
 *
 * @details
 */
void spiSend(uint8_t b) {
  SPI.send(b);
}

/**
 * @brief  Write token and then write from 512 byte buffer to SPI (for SD card)
 *
 * @param  buf   Pointer with buffer start address
 * @return Nothing
 *
 * @details Use DMA
 */
void spiSendBlock(uint8_t token, const uint8_t *buf) {
  SPI.send(token);
  SPI.dmaSend(const_cast<uint8_t*>(buf), 512);
}

#if ENABLED(SPI_EEPROM)

// Read single byte from specified SPI channel
uint8_t spiRec(uint32_t chan) { return SPI.transfer(0xFF); }

// Write single byte to specified SPI channel
void spiSend(uint32_t chan, byte b) { SPI.send(b); }

// Write buffer to specified SPI channel
void spiSend(uint32_t chan, const uint8_t *buf, size_t n) {
  for (size_t p = 0; p < n; p++) spiSend(chan, buf[p]);
}

#endif // SPI_EEPROM

#endif // SOFTWARE_SPI

#endif // __STM32F1__
