/**
  * @swcomponent OTA
  * @{
  * @file        OtaCommon.h
  * @brief       Common Header file for OTA.
  * @authors     hrd3kor, gur6kor
  * @copyright   (C) 2020 Robert Bosch Engineering and Business Solutions Limited.
  *              The reproduction, distribution and utilization of this file as
  *              well as the communication of its contents to others without express
  *              authorization is prohibited. Offenders will be held liable for the
  *              payment of damages. All rights reserved in the event of the grant
  *              of a patent, utility model or design.
  * @}
  */

#pragma once

// #include "Logger.h"
// #include "swupd_trace.h"

namespace  fcota {

typedef uint32_t tU32;
typedef uintptr_t act_t;
typedef unsigned short tU16;
typedef unsigned char tBool;

typedef unsigned char tU8;
typedef signed char tS8;
typedef char tChar;

typedef tChar tC8;
typedef tU8 tUChar;
typedef unsigned int tC16;

typedef char*tString;
typedef const char*tCString;

typedef unsigned short tU16;
typedef short tS16;

typedef unsigned short tUShort;
typedef short tShort;

typedef unsigned int tUInt;
typedef int tInt;

typedef unsigned long tULong;
typedef long tLong;

typedef void tVoid;

typedef tU32* tPU32;
typedef const tU8* tPCU8;

template < typename Enumeration >
auto enum_as_integer( Enumeration const value )->typename std::underlying_type < Enumeration >::type {
   return ( static_cast < typename std::underlying_type < Enumeration >::type >( value ) );
}

#define RETURN_IF_FAILED( expression_to_evaluate )                          \
   {                                                                        \
      status_t returnStatus = expression_to_evaluate;                       \
      if ( returnStatus ) {                                                   \
         return returnStatus;                                               \
      }                                                                     \
   }

}

// namespace fcota {


// # define SHA256_DIGEST_LENGTH    32

// #ifndef __OTAS_UNIT_TESTING__
// #define ETG_TRACE_USR1(ARGS) LOG_OTA_INFO ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_USR2(ARGS) LOG_OTA_INFO ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_USR3(ARGS) LOG_OTA_INFO ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_USR4(ARGS) LOG_OTA_INFO ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_DEBUG(ARGS) LOG_OTA_DEBUG ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_COMP(ARGS) LOG_OTA_INFO ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_ERR(ARGS) LOG_OTA_ERROR ARGS ; // LOG_OTA_INFO("\n")
// #else
// #define ETG_TRACE_USR1(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #define ETG_TRACE_USR2(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #define ETG_TRACE_USR3(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #define ETG_TRACE_USR4(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #define ETG_TRACE_DEBUG(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #define ETG_TRACE_COMP(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #define ETG_TRACE_ERR(...) do { /* LCOV_EXCL_LINE */ } while(0)
// #endif

// #define ETG_TRACE_FATAL(ARGS) LOG_OTA_ERROR ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_TRACE_ERRMEM(ARGS) LOG_OTA_ERROR ARGS ; // LOG_OTA_INFO("\n")
// #define ETG_I_CMD_DEFINE(ARGS) ;
// #define ETG_ENUM(ARG1,ARG2) ARG2
// #define ETG_CENUM(ARG1,ARG2) ARG2
// #define ETG_I_REGISTER_FILE();
// #define ETG_I_UNREGISTER_FILE();
// #define ETG_T8
// #define ETG_LIST_LEN(ARG1) ARG1
// #define ETG_LIST_PTR_T8(ARG1) ARG1
// #define ETG_LIST(ARG1,ARG2,ARG3) ARG1 ARG2 ARG3

// }//Namespace

