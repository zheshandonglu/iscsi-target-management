#include <stdio.h>
#include <stdlib.h>
#include <python2.7/Python.h>
#include <stdbool.h>
#include <string.h>



#define MAXNAMELEN 100
#define MAXIPLEN 16
#define MAXCHAPPWD 16
#define MAXCHAPUSER 100
#define MAXLUNS 10
#define MAXACLS 100
#define MAXPORTALS 21
#define MAXWWNLEN 100

/*****************************define the struct**************************************/
typedef struct storage_obj
{
    char dev[MAXNAMELEN];  // "/home/admin/sparcedata",
    char name[MAXNAMELEN]; // "vol4",
    int  plugin;            // "fileio", "blockio"
    uint64_t size;          // 2147483648,
    int write_back;         // true,
    char wwn[MAXNAMELEN];    // "dffc64ce-1e34-4410-9531-b71bb7b44848"
} storage_obj_t;


typedef struct portals
{    
    char ip_address[MAXIPLEN];
    int iser;   // true or false
    int port;
} portals_t;



typedef struct  parameters
{
    int AuthMethod;   // "CHAP = 1,None = 2", "CHAP mutual = 3", etc
#if 0
        "DataDigest": "CRC32C,None",
        "DataPDUInOrder": "Yes",
        "DataSequenceInOrder": "Yes",
        "DefaultTime2Retain": "20",
        "DefaultTime2Wait": "2",
        "ErrorRecoveryLevel": "0",
        "FirstBurstLength": "65536",
        "HeaderDigest": "CRC32C,None",
        "IFMarkInt": "2048~65535",
        "IFMarker": "No",
        "ImmediateData": "Yes",
        "InitialR2T": "Yes",
        "MaxBurstLength": "262144",
        "MaxConnections": "1",
        "MaxOutstandingR2T": "1",
        "MaxRecvDataSegmentLength": "8192",
        "MaxXmitDataSegmentLength": "262144",
        "OFMarkInt": "2048~65535",
        "OFMarker": "No",
#endif
    char TargetAlias[MAXNAMELEN];  //"LIO Target"
} parameters_t;



typedef struct attributes
{
    bool authentication;
    bool cache_dynamic_acls;
    int default_cmdsn_depth;
    bool demo_mode_write_protect;
    bool generate_node_acls;
    int login_timeout; // 15,
    int netif_timeout; // 2,
    int prod_mode_write_protect;  // 0
} attributes_t;



typedef struct iscsitarget
{
    attributes_t    attr;
    char chap_mutual_password[MAXCHAPPWD];  //: "aeae2e26-f043-42a7",
    char chap_mutual_userid[MAXCHAPUSER];   // "mutual-rts-user",
    char chap_password[MAXCHAPPWD];         //: "b492785e-bc91-4710",
    char chap_userid[MAXCHAPUSER];          // "rts-user",

    bool         enable;
    char            luns[MAXLUNS][MAXNAMELEN];  // a list of backstores -- "/backstores/fileio/vol4"
    char            node_acls[MAXACLS][MAXNAMELEN]; // a list of initiators -- "iqn.1991-05.com.microsoft:ibm-t410s"; we don't support mapped luns for now.
    parameters_t    param;
    portals_t       portals[MAXPORTALS];
    int             tag;        //always 0; which implies one target has one TPG only.
    char            wwn[MAXWWNLEN]; //specified by user
} iscsitarget_t;


/*
 *  create and enable an iscsi target
 *
 *  @sobj   storage obj for the target; create the obj if it doesn't exist
 *  @target iscsi target definition
 *
 *  @return wwn of the storage obj in sobj->wwn if was created
 *          1 success, 0 otherwise.
 */
int creat_block_target(storage_obj_t *sobj, iscsitarget_t *target)
{

    PyObject *pName, *pModule, *pDict, *pFunc, *pArgs, *pRetVal;
    
    Py_Initialize();
    if(!Py_IsInitialized())   
    {  
        printf("cannot find rts");
        getchar();
        return -1;  
    }

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('./')");

    pName = PyString_FromString("rtslib_def"); 
    if ( !pName)
    {
        printf("cannot find rtslibname");
        getchar();
        return -1;
    }

    pModule = PyImport_Import(pName);
    if ( !pModule)
    {
        printf("cannot find rtslib_def.py");
        getchar();
        return -1;

    }

    pDict = PyModule_GetDict(pModule);
    if (!pDict)
    {
        printf("cannot find rtslib_def_dict");
        getchar();
        return -1;
    }


    pFunc = PyDict_GetItemString(pDict,"create_block_backstore");
    if ( !pFunc || !PyCallable_Check(pFunc) )  
    {
        printf("can't find block");  
        getchar();  
        return -1;  
    }

    pArgs = PyTuple_New(2);
    PyTuple_SetItem(pArgs, 0, Py_BuildValue("s",sobj->dev));
    PyTuple_SetItem(pArgs, 1, Py_BuildValue("s",sobj->name));


    pRetVal = PyObject_CallObject(pFunc, pArgs);

    strcpy(sobj->wwn,PyString_AsString(pRetVal));




    //return PyString_AsString(pRetVal);
    //PyArg_Parse(pRetVal, "s", &string )
    //return(string)

    Py_DECREF(pName);
    Py_DECREF(pArgs);
    Py_DECREF(pModule);
    Py_DECREF(pRetVal);

    Py_Finalize();
    printf("wwn return value %s\n", sobj->wwn); 
    
}



int delete_all_targets(void)
{
    PyObject *pName, *pModule, *pDict, *pFunc, *pRetVal;  
    
    Py_Initialize();
    if(!Py_IsInitialized())   
    {  
        return -1;  
    }

    PyRun_SimpleString("import sys");
    PyRun_SimpleString("sys.path.append('./')");

    pName = PyString_FromString("rtslib_def"); 
    if ( !pName)
    {
        printf("cannot find rtslibname");
        getchar();
        return -1;
    }

    pModule = PyImport_Import(pName);
    if ( !pModule)
    {
        printf("cannot find rtslib_def.py");
        getchar();
        return -1;

    }

    pDict = PyModule_GetDict(pModule);
    if (!pDict)
    {
        printf("cannot find rtslib_def_dict");
        getchar();
        return -1;
    }

    pFunc = PyDict_GetItemString(pDict,"delete_all_targets");
    if ( !pFunc || !PyCallable_Check(pFunc) )  
    {
        printf("can't find func");  
        getchar();  
        return -1;  
    }

    pRetVal = PyObject_CallObject(pFunc,NULL);
    printf("return 1 for sucess : %d\n", PyInt_AsLong(pRetVal)); 


    Py_DECREF(pName);
    Py_DECREF(pModule);
    Py_DECREF(pRetVal);
    Py_Finalize();
}




int main(int argc, char* argv[])
{

    //delete_all_targets();

    /* initialize the portals */
    portals_t *port;
    port = (portals_t*)malloc(sizeof(portals_t));
    strcpy(port->ip_address, "192.168.1.55"); 
    port->iser = 1;
    port->port = 3260;

    /* initialize the parameters */
    parameters_t *para;
    para = (parameters_t*)malloc(sizeof(parameters_t));
    para->AuthMethod = 2;

    /* initialize the attributes */
    attributes_t *attri;
    attri = (attributes_t*)malloc(sizeof(attributes_t));
    attri->authentication = 0;
    attri->cache_dynamic_acls = 1;

    /* initialize the target */
    iscsitarget_t *target;
    target = (iscsitarget_t*)malloc(sizeof(iscsitarget_t));
    strcpy(target->chap_mutual_password, "123455432112");
    strcpy(target->chap_mutual_userid, "iqn.2003-01.org.linux-iscsi.localhost.x8664:sn.e16787b68bb4");
    strcpy(target->chap_password, "567899876556");
    strcpy(target->chap_userid, "iqn.1991-05.com.microsoft:ibm-t410s");
    target->enable = 1;

    /* initialize the target */
    storage_obj_t *sobj;
    sobj = (storage_obj_t*)malloc(sizeof(storage_obj_t));
    strcpy(sobj->dev,"/dev/sdd");
    strcpy(sobj->name,"disk_d");
    sobj->plugin = 2;
    sobj->size = 2147483648;



    creat_block_target(sobj, target);

    /* free the memory */
    free(target);
    free(sobj);
    free(para);
    free(attri);
    free(port);

}