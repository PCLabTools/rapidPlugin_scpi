/**
 * @file rapidPlugin_scpi.h
 * @author your name (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2023-10-22
 * 
 * @copyright Copyright (c) 2023
 * 
 */

 #ifndef rapidPlugin_scpi_h
 #define rapidPlugin_scpi_h
 
 #ifndef rapidPlugin_scpi_stack_size
 #define rapidPlugin_scpi_stack_size 64
 #endif
 
 #include "rapidRTOS.h"
 
 /*
 // STATus
 //     :OPERation
 //         :CONDition?
 //         :ENABle
 //         [:EVENt]?
 //     :QUEStionable
 //         :CONDition?
 //         :ENABle
 //         [:EVENt]?
 //     :PRESet
 SYSTem
     :ERRor - {numeric},{string}
     //     [:NEXT]?
     // :VERSion?
 *CLS - clear errors and other events
 // *ESE
 // *ESE?
 // *ESR?
 *IDN? - identity <company name>, <model number>, <serial number>, <firmware revision>
 // *OPC
 *OPC? - query operation complete
 *RST - factory reset
 // *SRE
 // *SRE?
 // *STB
 *TST? - self test (0: pass, 1: fail)
 // *WAI
 */
 
 /*
 Largest branch needed
 or
 Max number of parameters
 */
 #ifndef SCPI_ARRAY_SYZE
 #define SCPI_ARRAY_SYZE 3
 #endif
 
 /*
 Count of unique commands (eg OPC and OPC? are 1 token)
 */
 #ifndef SCPI_MAX_TOKENS
 #define SCPI_MAX_TOKENS 21
 #endif
 
 /*
 Total number of valid commands (includes tree categories base excluded)
 e.g. STATus:OPERation? but not STATus?
 */
 #ifndef SCPI_MAX_COMMANDS
 #define SCPI_MAX_COMMANDS 25
 #endif
 
 /*
 Refer to documentation in Vrekrer_scpi_parser.h as to how special commands are used
 */
 #ifndef SCPI_MAX_SPECIAL_COMMANDS
 #define SCPI_MAX_SPECIAL_COMMANDS 0
 #endif
 
 /*
 The message buffer should be large enough to fit all the incoming message
 For example, the multicommand message
 "*RST; *cls; status:operation:enable; status:questionable:enable;\n"
 will need at least 67 byte buffer length.
 */
 #ifndef SCPI_BUFFER_LENGTH
 #define SCPI_BUFFER_LENGTH 128
 #endif
 
 /*
 In order to reduce RAM usage, Vrekrer_scpi_parser library (ver. 0.42 and later)
 uses a hash algorithm to store and compare registered commands. In very rare 
 situations this might end in hash crashes (two commands have the same hash)
 
 If needed, to avoid hash crashes, change SCPI_HASH_TYPE to uint16_t or uint32_t
 */
 #ifndef SCPI_HASH_TYPE
 #define SCPI_HASH_TYPE uint8_t
 #endif
 
 /*
 To fix hash crashes, the hashing magic numbers can be changed before 
 registering commands.
 Use prime numbers up to the SCPI_HASH_TYPE size.
 */
 #ifndef SCPI_HAS_MAGIC_NUMBER
 #define SCPI_HAS_MAGIC_NUMBER 37
 #endif
 
 /*
 To fix hash crashes, the hashing magic numbers can be changed before 
 registering commands.
 Use prime numbers up to the SCPI_HASH_TYPE size.
 */
 #ifndef SCPI_HASH_MAGIC_OFFSET
 #define SCPI_HASH_MAGIC_OFFSET 7
 #endif
 
 /*
 Timeout time can be changed even during program execution
 See Error_Handling example for further details.
 */
 #ifndef SCPI_TIMEOUT
 #define SCPI_TIMEOUT 10
 #endif
 
 #include "Vrekrer_scpi_parser.h"
 
 SCPI_Parser scpi_parser;
 
 void SCPI_Error_Handler(SCPI_C commands, SCPI_P parameters, Stream& interface) {
   //This function is called every time an error occurs
 
   /* For BufferOverflow errors, the rest of the message, still in the interface
   buffer or not yet received, will be processed later and probably 
   trigger another kind of error.
   Here we flush the incomming message*/
   if (currentError.error == rapidError::SCPI_BUFFER_OVERFLOW) {
     delay(2);
     while (interface.available()) {
       delay(2);
       interface.read();
     }
   }
 }
 
 #include "scpi.h"
 
 /**
  * @brief rapidPlugin top level description
  * 
  */
 class rapidPlugin_scpi : public rapidPlugin
 {
   public:
     rapidPlugin_scpi(const char* identity, Stream& stream = Serial);
     BaseType_t run();
     BaseType_t runCore(BaseType_t core);
 
   private:
     static void main_loop(void*);
     uint8_t interface(rapidFunction incoming, char messageBuffer[]);
     Stream& _stream = Serial;
 };
 
 /**
  * @brief Construct a new rapidPlugin_scpi object
  * 
  * @param identity string literal containing task name
  */
 rapidPlugin_scpi::rapidPlugin_scpi(const char* identity, Stream& stream)
 {
   _pID = identity;
   _stream = stream;
   scpi_parser.hash_magic_number = SCPI_HAS_MAGIC_NUMBER;
   scpi_parser.hash_magic_offset = SCPI_HASH_MAGIC_OFFSET;
   scpi_parser.timeout = SCPI_TIMEOUT;
 }
 
 /**
  * @brief Runs the main loop task.
  * rapidRTOS registers the task with the manager and creates the interface handlers
  * 
  * @return BaseType_t 1 = task run successful | 0 = task failed to start
  */
 BaseType_t rapidPlugin_scpi::run()
 {
   return rapidPlugin::run(&main_loop, rapidPlugin_scpi_stack_size);
 }
 
 /**
  * @brief Runs the main loop task on the specified core.
  * rapidRTOS registers the task with the manager and creates the interface handlers
  * using the same core as the main loop
  * 
  * @param core core ID
  * @return BaseType_t 1 = task run successful | 0 = task failed to start
  */
 BaseType_t rapidPlugin_scpi::runCore(BaseType_t core)
 {
   return rapidPlugin::runCore(core, &main_loop, rapidPlugin_scpi_stack_size);
 }
 
 #ifndef rapidPlugin_scpi_override_main_loop
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
     scpi_parser.last_error = SCPI_Parser::ErrorCode(currentError.error);
     scpi_parser.ProcessInput(plugin->_stream, "\n");
     vTaskDelay(10 / portTICK_PERIOD_MS);
   }
 }
 #endif
 
 #ifndef rapidPlugin_scpi_override_interface
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
 
 #include "scpi.h"
 
 #endif // rapidPlugin_scpi_h