# rapidPlugin_scpi

This plugin is responsible for handling SCPI communication.

Author: Larry Colvin

Email: PCLabTools@github.io

## Installation

### Arduino

To install this library follow the standard method of installing libraries, either using the library manager or a downloaded zip file of this repository.

**Make sure to install the below listed dependencies as this library depends upon them.**

For more information on how to install libraries please visit [Installing Additional Arduino Libraries](https://www.arduino.cc/en/guide/libraries "arduino.cc").

#### Dependencies

| Name | Git Link | ZIP file |
| - | - | - |
|rapidRTOS (PCLabTools) | https://github.com/PCLabTools/rapidRTOS.git | [Download zip file](https://github.com/PCLabTools/rapidRTOS/archive/refs/heads/master.zip) |

### PlatformIO

To include this library and its dependencies simply add the following to the "platformio.ini" file:
```
[env:my_build_env]
framework = arduino
lib_deps = 
  https://github.com/Larry Colvin/scpi.git
```

## Usage

### General Usage

1. Include the scpi.h library:

``` cpp
#include <scpi.h>
```
