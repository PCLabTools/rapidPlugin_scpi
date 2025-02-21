FILEPATH_ERRORS_H = project_path + '/include/errors.h'

header = '''/**
 * @file errors.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2025-02-08
 * 
 * @copyright Copyright (c) 2025
 * 
 */

#ifndef errors_h
#define errors_h

/**
 * @brief 
 * 
 */
enum class rapidPluginErrors_t
{
  NO_ERROR = 0,             // No error has occured
  UNKNOWN_ERROR,            // Unknown error is a catch to be used when no other error is applicable
'''

custom_errors = '''  // scpi ERRORS
  SCPI_BUFFER_OVERFLOW,     // Template error 1
  SCPI_COMMUNICATION_TIMEOUT,  // Template error 2
  UNKNOWN_SCPI_COMMAND,     // Template error 3
'''

footer = '''};

/**
 * @brief Short-hand define for rapidPluginErrors_t
 * 
 */
#define rapidError rapidPluginErrors_t

/**
 * @brief Struct containing the currently held error and the time it was set
 * 
 */
struct currentError_t
{
  time_t time;
  rapidPluginErrors_t error;
} currentError  = {0, rapidPluginErrors_t::NO_ERROR};

/**
 * @brief Set the current error and the time it was set
 * 
 * @param rapidError error 
 */
void setCurrentError(rapidPluginErrors_t error)
{
  currentError.time = millis();
  currentError.error = error;
}

#endif // errors_h
'''

try:
  open(FILEPATH_ERRORS_H, "r+")
  print(info + '\'errors.h\' already present')
  with open(FILEPATH_ERRORS_H, "r") as f:
    lines = f.readlines()
    if any(custom_errors.split('\n')[1].strip() in line for line in lines):
      print(info + '\'errors.h\' already contains scpi custom errors')
    else:
      with open(FILEPATH_ERRORS_H, "w") as f_write:
        for line in lines:
          if line.strip() == footer.split('\n')[0].strip():
            f_write.write(custom_errors)
          f_write.write(line)
      print(info + '\'errors.h\' updated with scpi custom errors')

except:
  print(warning + '\'errors.h\' not present, generating default...')
  try:
    with open(FILEPATH_ERRORS_H, 'x') as f:
      f.write(header + custom_errors + footer)
  except:
    print(error + '\'errors.h\' could not be written to')