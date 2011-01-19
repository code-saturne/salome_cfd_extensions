
#include "FSI_SATURNE.hxx"
#include <string>
#include <unistd.h>

#include <Calcium.hxx>
#include <calcium.h>
#include <signal.h>
#include <SALOME_NamingService.hxx>
#include <Utils_SALOME_Exception.hxx>
#include <pthread.h>
#include <execinfo.h>

typedef void (*sighandler_t)(int);
sighandler_t setsig(int sig, sighandler_t handler)
{
  struct sigaction context, ocontext;
  context.sa_handler = handler;
  sigemptyset(&context.sa_mask);
  context.sa_flags = 0;
  if (sigaction(sig, &context, &ocontext) == -1)
    return SIG_ERR;
  return ocontext.sa_handler;
}

static void AttachDebugger()
{
  void *array[20];
  size_t size=20;
  char **strings;
  size_t i;
  std::string _what;
  size = backtrace (array, size);
  strings = backtrace_symbols (array, size);
  for (i = 0; i < size; i++)
     _what=_what+strings[i]+ '\n';
  free (strings);

  std::cerr << pthread_self() << std::endl;
  std::cerr << _what << std::endl;

  if(getenv ("DEBUGGER"))
    {
      std::stringstream exec;
#if 0
      exec << "$DEBUGGER " << "None " << getpid() << "&";
#else
      exec << "$DEBUGGER SALOME_Container " << getpid() << "&";
#endif
      std::cerr << exec.str() << std::endl;
      system(exec.str().c_str());
      while(1);
    }
}

static void THandler(int theSigId)
{
  std::cerr << "SIGSEGV: "  << std::endl;
  AttachDebugger();
  //to exit or not to exit
  _exit(1);
}

static void terminateHandler(void)
{
  std::cerr << "Terminate: not managed exception !"  << std::endl;
  AttachDebugger();
  throw SALOME_Exception("Terminate: not managed exception !");
}

static void unexpectedHandler(void)
{
  std::cerr << "Unexpected: unexpected exception !"  << std::endl;
  AttachDebugger();
  throw SALOME_Exception("Unexpected: unexpected exception !");
}


#define  _(A,B)   A##B
#ifdef _WIN32
#define F_FUNC(lname,uname) __stdcall uname
#define F_CALL(lname,uname) uname
#define STR_PSTR(str)       char *str, int _(Len,str)
#define STR_PLEN(str)
#define STR_PTR(str)        str
#define STR_LEN(str)        _(Len,str)
#define STR_CPTR(str)        str,strlen(str)
#define STR_CLEN(str)
#else
#define F_FUNC(lname,uname) _(lname,_)        /* Fortran function name */
#define F_CALL(lname,uname) _(lname,_)        /* Fortran function call */
#define STR_PSTR(str)       char *str         /* fortran string arg pointer */
#define STR_PLEN(str)       , int _(Len,str)  /* fortran string arg length */
#define STR_PTR(str)        str               /* fortran string pointer */
#define STR_LEN(str)        _(Len,str)        /* fortran string length */
#define STR_CPTR(str)        str              /* fortran string calling arg pointer */
#define STR_CLEN(str)       , strlen(str)     /* fortran string calling arg length */
#endif

//DEFS
#include <cfd_proxy_api.h>
#include <cfd_proxy_api.h>
//ENDDEF

extern "C" void cp_exit(int err);

extern "C" void F_FUNC(cpexit,CPEXIT)(int *err)
{
  if(*err==-1)
    _exit(-1);
  else
    cp_exit(*err);
}

using namespace std;

//! Constructor for component "FSI_SATURNE" instance
/*!
 *
 */
FSI_SATURNE_i::FSI_SATURNE_i(CORBA::ORB_ptr orb,
                     PortableServer::POA_ptr poa,
                     PortableServer::ObjectId * contId,
                     const char *instanceName,
                     const char *interfaceName)
          : Superv_Component_i(orb, poa, contId, instanceName, interfaceName)
{
#if 0
  setsig(SIGSEGV,&THandler);
  set_terminate(&terminateHandler);
  set_unexpected(&unexpectedHandler);
#endif
  _thisObj = this ;
  _id = _poa->activate_object(_thisObj);
}

FSI_SATURNE_i::FSI_SATURNE_i(CORBA::ORB_ptr orb,
                     PortableServer::POA_ptr poa,
                     Engines::Container_ptr container,
                     const char *instanceName,
                     const char *interfaceName)
          : Superv_Component_i(orb, poa, container, instanceName, interfaceName)
{
#if 0
  setsig(SIGSEGV,&THandler);
  set_terminate(&terminateHandler);
  set_unexpected(&unexpectedHandler);
#endif
  _thisObj = this ;
  _id = _poa->activate_object(_thisObj);
}

//! Destructor for component "FSI_SATURNE" instance
FSI_SATURNE_i::~FSI_SATURNE_i()
{
}

void FSI_SATURNE_i::destroy()
{
#if 0
  _remove_ref();
  if(!CORBA::is_nil(_orb))
    _orb->shutdown(0);
#else
  Engines_Component_i::destroy();
#endif
}

//! Register datastream ports for a component service given its name
/*!
 *  \param service_name : service name
 *  \return true if port registering succeeded, false if not
 */
CORBA::Boolean
FSI_SATURNE_i::init_service(const char * service_name) {
  CORBA::Boolean rtn = false;
  string s_name(service_name);

  if (s_name == "load_run")
    {
      try
        {
          //initialization CALCIUM ports IN
          create_calcium_port(this,(char *)"DEPSAT",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"EPSILO",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"DTCALC",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"TTINIT",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"PDTREF",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"NBPDTM",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"NBSSIT",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"ISYNCP",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"NTCHRO",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"ICVEXT",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          //initialization CALCIUM ports OUT
          create_calcium_port(this,(char *)"DTSAT",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"FORSAT",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"ALMAXI",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COONOD",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COOFAC",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COLNOD",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COLFAC",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"ICV",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"DONGEO",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
        }
      catch(const PortAlreadyDefined& ex)
        {
          std::cerr << "FSI_SATURNE: " << ex.what() << std::endl;
          //Ports already created : we use them
        }
      catch ( ... )
        {
          std::cerr << "FSI_SATURNE: unknown exception" << std::endl;
        }
      rtn = true;
    }


  if (s_name == "spawn_run")
    {
      try
        {
          //initialization CALCIUM ports IN
          create_calcium_port(this,(char *)"DEPSAT",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"EPSILO",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"DTCALC",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"TTINIT",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"PDTREF",(char *)"CALCIUM_double",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"NBPDTM",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"NBSSIT",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"ISYNCP",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"NTCHRO",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          create_calcium_port(this,(char *)"ICVEXT",(char *)"CALCIUM_integer",(char *)"IN",(char *)"I");
          //initialization CALCIUM ports OUT
          create_calcium_port(this,(char *)"DTSAT",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"FORSAT",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"ALMAXI",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COONOD",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COOFAC",(char *)"CALCIUM_double",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COLNOD",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"COLFAC",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"ICV",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
          create_calcium_port(this,(char *)"DONGEO",(char *)"CALCIUM_integer",(char *)"OUT",(char *)"I");
        }
      catch(const PortAlreadyDefined& ex)
        {
          std::cerr << "FSI_SATURNE: " << ex.what() << std::endl;
          //Ports already created : we use them
        }
      catch ( ... )
        {
          std::cerr << "FSI_SATURNE: unknown exception" << std::endl;
        }
      rtn = true;
    }

  return rtn;
}


void FSI_SATURNE_i::load_run(const char* exec_dir,const char* library,const char* args,CORBA::Long& retval)
{
  beginService("FSI_SATURNE_i::load_run");
  Superv_Component_i * component = dynamic_cast<Superv_Component_i*>(this);
  char       nom_instance[INSTANCE_LEN];
  int info = cp_cd(component,nom_instance);
  try
    {
//BODY
cfd_proxy_set_component(component, 0);
cfd_proxy_set_dir(exec_dir);
cfd_proxy_set_lib(library);
cfd_proxy_set_args(args);
retval = cfd_proxy_run_all();
//ENDBODY
      cp_fin(component,CP_ARRET);
    }
  catch ( const CalciumException & ex)
    {
      std::cerr << ex.what() << std::endl;
      cp_fin(component,CP_ARRET);
      SALOME::ExceptionStruct es;
      es.text=CORBA::string_dup(ex.what());
      es.type=SALOME::INTERNAL_ERROR;
      throw SALOME::SALOME_Exception(es);
    }
  catch ( const SALOME_Exception & ex)
    {
      cp_fin(component,CP_ARRET);
      SALOME::ExceptionStruct es;
      es.text=CORBA::string_dup(ex.what());
      es.type=SALOME::INTERNAL_ERROR;
      throw SALOME::SALOME_Exception(es);
    }
  catch ( const SALOME::SALOME_Exception & ex)
    {
      cp_fin(component,CP_ARRET);
      throw;
    }
  catch (...)
    {
      std::cerr << "unknown exception" << std::endl;
#if 0
      _exit(-1);
#endif
      cp_fin(component,CP_ARRET);
      SALOME::ExceptionStruct es;
      es.text=CORBA::string_dup(" unknown exception");
      es.type=SALOME::INTERNAL_ERROR;
      throw SALOME::SALOME_Exception(es);
    }
  endService("FSI_SATURNE_i::load_run");
}



void FSI_SATURNE_i::spawn_run(const char* exec_dir,const char* optional_launcher,const char* executable,const char* args,CORBA::Long& retval)
{
  beginService("FSI_SATURNE_i::spawn_run");
  Superv_Component_i * component = dynamic_cast<Superv_Component_i*>(this);
  char       nom_instance[INSTANCE_LEN];
  int info = cp_cd(component,nom_instance);
  try
    {
//BODY
cfd_proxy_set_component(component, 0);
cfd_proxy_set_dir(exec_dir);
cfd_proxy_set_launcher(optional_launcher);
cfd_proxy_set_exe(executable);
cfd_proxy_set_args(args);
retval = cfd_proxy_run_all();
//ENDBODY
      cp_fin(component,CP_ARRET);
    }
  catch ( const CalciumException & ex)
    {
      std::cerr << ex.what() << std::endl;
      cp_fin(component,CP_ARRET);
      SALOME::ExceptionStruct es;
      es.text=CORBA::string_dup(ex.what());
      es.type=SALOME::INTERNAL_ERROR;
      throw SALOME::SALOME_Exception(es);
    }
  catch ( const SALOME_Exception & ex)
    {
      cp_fin(component,CP_ARRET);
      SALOME::ExceptionStruct es;
      es.text=CORBA::string_dup(ex.what());
      es.type=SALOME::INTERNAL_ERROR;
      throw SALOME::SALOME_Exception(es);
    }
  catch ( const SALOME::SALOME_Exception & ex)
    {
      cp_fin(component,CP_ARRET);
      throw;
    }
  catch (...)
    {
      std::cerr << "unknown exception" << std::endl;
#if 0
      _exit(-1);
#endif
      cp_fin(component,CP_ARRET);
      SALOME::ExceptionStruct es;
      es.text=CORBA::string_dup(" unknown exception");
      es.type=SALOME::INTERNAL_ERROR;
      throw SALOME::SALOME_Exception(es);
    }
  endService("FSI_SATURNE_i::spawn_run");
}



extern "C"
{
  PortableServer::ObjectId * FSI_SATURNEEngine_factory( CORBA::ORB_ptr orb,
                                                    PortableServer::POA_ptr poa,
                                                    PortableServer::ObjectId * contId,
                                                    const char *instanceName,
                                                    const char *interfaceName)
  {
    MESSAGE("PortableServer::ObjectId * FSI_SATURNEEngine_factory()");
    FSI_SATURNE_i * myEngine = new FSI_SATURNE_i(orb, poa, contId, instanceName, interfaceName);
    return myEngine->getId() ;
  }
  void yacsinit()
  {
    int argc=0;
    char *argv=0;
    CORBA::ORB_var orb = CORBA::ORB_init( argc , &argv ) ;
    PortableServer::POAManager_var pman;
    CORBA::Object_var obj;
    try
      {
        SALOME_NamingService * salomens = new SALOME_NamingService(orb);
        obj = orb->resolve_initial_references("RootPOA");
        PortableServer::POA_var  poa = PortableServer::POA::_narrow(obj);
        PortableServer::POAManager_var pman = poa->the_POAManager();
        std::string containerName(getenv("SALOME_CONTAINERNAME"));
        std::string instanceName(getenv("SALOME_INSTANCE"));
        obj=orb->string_to_object(getenv("SALOME_CONTAINER"));
        Engines::Container_var container = Engines::Container::_narrow(obj);
        FSI_SATURNE_i * myEngine = new FSI_SATURNE_i(orb, poa, container, instanceName.c_str(), "FSI_SATURNE");
        pman->activate();
        obj=myEngine->POA_FSI_ORB::FSI_SATURNE::_this();
        Engines::Component_var component = Engines::Component::_narrow(obj);
        string component_registerName = containerName + "/" + instanceName;
        salomens->Register(component,component_registerName.c_str());
        orb->run();
        orb->destroy();
      }
    catch(CORBA::Exception&)
      {
        std::cerr << "Caught CORBA::Exception."<< std::endl;
      }
    catch(std::exception& exc)
      {
        std::cerr << "Caught std::exception - "<<exc.what() << std::endl;
      }
    catch(...)
      {
        std::cerr << "Caught unknown exception." << std::endl;
      }
  }

  void F_FUNC(yacsinit,YACSINIT)()
  {
    yacsinit();
  }
}
