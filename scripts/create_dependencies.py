FILEPATH_DEPENDENCY_H = project_path + '/include/scpi.h'

contents = '''/**
 * @file scpi.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2025-02-08
 * 
 * @copyright Copyright (c) 2025
 * 
 */

// #define rapidPlugin_scpi_override_main_loop
// #define rapidPlugin_scpi_override_interface

#ifndef scpi_h
#define scpi_h

#include "errors.h"

#ifndef COMPANY_NAME
#define COMPANY_NAME "MyCompany"
#endif

#ifndef MODEL_NAME
#define MODEL_NAME "MyModel"
#endif

#ifndef SERIAL_NUMBER
#define SERIAL_NUMBER "123456"
#endif

void register_scpi_commands();

#include "rapidPlugin_scpi.h"


/*
! Function Prototypes
*/

void SCPI_Identity(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Clear_Error(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Operation_Complete(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Reset(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Self_Test(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Error(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Version(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Debug(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Software_Reset(SCPI_C commands, SCPI_P parameters, Stream& interface);


/*
! Command Registry
*/

/**
 * @brief Registers the SCPI commands
 * 
 * @details
 * 
 * Command | Description                  | Parameters | Return
 * ------- | ---------------------------- | ---------- | ----------------------------------------------------------------------------
 * *IDN?   | Queries firmware identity    | none       | [str] "<company name>, <model number>, <serial number>, <firmware version>"
 * *CLS    | Resets the error             | none       | none
 * *OPC?   | Queries operation complete   | none       | [int] <status>
 * *RST    | Factory resets the board     | none       | none
 * *TST?   | Perform self test and report | none       | [int] <result>
 * 
 * **SYSTem**
 * 
 * Command   | Description              | Parameters          | Return
 * --------- | ------------------------ | ------------------- | ----------------------------------
 * :ERRor?   | Queries current error    | none                | [str] "<error code>,<description>"
 * :ERRor    | Asserts an error         | [int] <error code>  | none
 * :VERSion? | Queries the SCPI version | none                | [str] "<version>"
 * :DEBug?   | Queries the debug level  | none                | [int] <debug level>
 * :DEBug    | Sets the debug level     | [int] <debug level> | none
 * :RESet    | Initiates software reset | none                | none
 * 
 */
void register_scpi_commands()
{
  scpi_parser.RegisterCommand(F("*IDN?"), &SCPI_Identity);
  scpi_parser.RegisterCommand(F("*CLS"), &SCPI_Clear_Error);
  scpi_parser.RegisterCommand(F("*OPC?"), &SCPI_Operation_Complete);
  scpi_parser.RegisterCommand(F("*RST"), &SCPI_Reset);
  scpi_parser.RegisterCommand(F("*TST?"), &SCPI_Self_Test);
  scpi_parser.SetCommandTreeBase(F("SYSTem"));
  scpi_parser.RegisterCommand(F(":ERRor?"), &SCPI_Error);
  scpi_parser.RegisterCommand(F(":ERRor"), &SCPI_Error);
  scpi_parser.RegisterCommand(F(":VERSion?"), &SCPI_Version);
  scpi_parser.RegisterCommand(F(":DEBug?"), &SCPI_Debug);
  scpi_parser.RegisterCommand(F(":DEBug"), &SCPI_Debug);
}


/*
! SCPI Commands
*/

/**
 * @brief Queries the identity of the microcontroller
 * 
 * @return "MyCompany, MyModel, 123456, vX.X.X"
 * 
 */
void SCPI_Identity(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  interface.printf("%s, %s, %s, v%d.%d.%d\\n", \
    COMPANY_NAME, \
    MODEL_NAME, \
    SERIAL_NUMBER, \
    SOFTWARE_VERSION_MAJOR, \
    SOFTWARE_VERSION_MINOR, \
    SOFTWARE_VERSION_FIX);
}

/**
 * @brief Resets the currently held error.
 * This is useful is clearing a critical error since
 * reading standard errors clear the error
 * 
 */
void SCPI_Clear_Error(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  setCurrentError(rapidError::NO_ERROR);
}

/**
 * @brief Queries if operation is complete
 * 
 * @return "1": complete | "0": pending"
 * 
 */
void SCPI_Operation_Complete(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  interface.println(F("1"));
}

/**
 * @brief Resets the microcontroller.
 * If using rapidPlugin_memory reset the memory to default
 * 
 */
void SCPI_Reset(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  #ifdef rapidPlugin_memory_h
  Memory_t* Memory = new Memory_t;  // reset memory
  delay(1000);                      // wait for memory to update
  #endif
  SCPI_Software_Reset(commands, parameters, interface);
}

/**
 * @brief Perform a self test
 * 
 * @return "1": pass | "0": fail
 * 
 */
void SCPI_Self_Test(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  interface.println(F("1"));
}

/**
 * @brief Queries or asserts the last error.
 * If querying the error and it returns a standard error
 * the last error is cleared
 * 
 * @param uint8_t error code
 * 
 * @return "0, no error"
 * 
 */
void SCPI_Error(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  String last_header = String(commands.Last());
  if (last_header.endsWith(F("?")))
  {
    bool criticalError = false;
    interface.print(int(currentError.error));
    interface.print(F(","));
    switch(rapidError(scpi_parser.last_error)){
      case rapidError::SCPI_BUFFER_OVERFLOW: 
        interface.println(F("Buffer overflow error"));
        break;
      case rapidError::SCPI_COMMUNICATION_TIMEOUT:
        interface.println(F("Communication timeout error"));
        break;
      case rapidError::UNKNOWN_SCPI_COMMAND:
        interface.println(F("Unknown command received"));
        break;
      case rapidError::NO_ERROR:
        interface.println(F("No Error"));
        break;
      default:
        interface.println(F("Unknown error"));
        break;
    }
    if (!criticalError)
    {
      currentError.error = rapidError::NO_ERROR;
    }
  }
  else
  {
    setCurrentError(rapidError(SCPI_Parser::ErrorCode(atoi(parameters.First()))));
  }
}

/**
 * @brief Queries the SCPI version
 * 
 * @return "vX.X.X"
 */
void SCPI_Version(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  interface.printf(VREKRER_SCPI_VERSION);
}

/**
 * @brief Queries or sets the debug level
 * 
 * @param int <debug level>
 * 
 * @return int <debug level>
 * 
 */
void SCPI_Debug(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  String last_header = String(commands.Last());
  if (last_header.endsWith(F("?")))
  {
    interface.println(rapidRTOS.getDebugLevel());
  }
  else
  {
    #ifdef rapidPlugin_memory_h
    Memory.DEBUG_LEVEL = atoi(parameters[0]);
    #endif
    rapidRTOS.setDebugLevel(atoi(parameters[0]));
  }
}

/**
 * @brief Resets the microcontroller.
 * 
 */
void SCPI_Software_Reset(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  #ifdef BOARD_AVR
  resetFunc();
  #endif
  #ifdef BOARD_ESP32
  ESP.restart();
  #endif
  #ifdef BOARD_RP2040
  #define AIRCR_Register (*((volatile uint32_t*)(PPB_BASE + 0x0ED0C)))
  AIRCR_Register = 0x5FA0004;
  #endif
  #ifdef BOARD_STM32
  NVIC_SystemReset();
  #endif
}


/*
! rapidPlugin_scpi Overrides
*/

#ifdef rapidPlugin_scpi_override_main_loop
/**
 * @brief main loop task
 * 
 * @param pModule pointer to the calling object
 */
void rapidPlugin_scpi::main_loop(void* pModule)
{
  rapidPlugin_scpi* plugin = (rapidPlugin_scpi*)pModule;
  register_scpi_commands();
  scpi_parser.SetErrorHandler(&SCPI_Error_Handler);
  for ( ;; )
  {
    scpi_parser.ProcessInput(plugin->_stream, "\\n");
    vTaskDelay(10 / portTICK_PERIOD_MS);
  }
}
#endif

#ifdef rapidPlugin_scpi_override_interface
/**
 * @brief Interface handler extended functions.
 * This function is to be used for creating custom states 
 * that are called when rapidFunction commands are received
 * 
 * @param incoming message broken into 2 strings: function and parameters
 * @param messageBuffer buffer to store return message
 * @return uint8_t return 0 if the function was handled, 1 if not
 */
uint8_t rapidPlugin_scpi::interface(rapidFunction incoming, char messageBuffer[])
{
  do
  {
    if (!strcmp(incoming.function, "print_debug"))
    {
      scpi_parser.PrintDebugInfo(_stream);
      sprintf(messageBuffer, "OK");
      continue;
    }
    rapidPlugin::interface(incoming, messageBuffer);
    return 0;
  } while (false);
  return 1;
}
#endif

#endif // scpi_h

'''

try:
  open(FILEPATH_DEPENDENCY_H, "r+")
  print(info + '\'scpi.h\' already present')
except:
  print(warning + '\'scpi.h\' not present, generating default...')
  try:
    with open(FILEPATH_DEPENDENCY_H, 'x') as f:
      f.write(contents)
  except:
    print(error + '\'scpi.h\' could not be written to')