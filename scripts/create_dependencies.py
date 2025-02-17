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

#include "rapidPlugin_scpi.h"

void SCPI_Identity(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Error(SCPI_C commands, SCPI_P parameters, Stream& interface);
void SCPI_Version(SCPI_C commands, SCPI_P parameters, Stream& interface);

void register_scpi_commands()
{
  scpi.RegisterCommand(F("*IDN?"), &SCPI_Identity);
  SetCommandTreeBase(F("SYSTem"));
  scpi.RegisterCommand(F(":ERRor?"), &SCPI_Error);
  scpi.RegisterCommand(F(":ERRor"), &SCPI_Error);
  scpi.RegisterCommand(F(":VERSion?"), &SCPI_Version);
}

void SCPI_Identity(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  interface.println(F("Vrekrer,SCPI Example,#00," VREKRER_SCPI_VERSION));
}

void SCPI_Error(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  //
}

void SCPI_Version(SCPI_C commands, SCPI_P parameters, Stream& interface)
{
  //
}

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
  for ( ;; )
  {
    scpi_parser.ProcessInput(_stream, "\n");
    vTaskDelay(1000 / portTICK_PERIOD_MS);
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