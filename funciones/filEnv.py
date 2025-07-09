# --------------------------------------------------------
# %                 General Enveloped                    %
# %              with MATLAB Implementation              %
# %                                                      %
# % Author: Ing. Facundo Lopez                  17/05/21 %
# --------------------------------------------------------

import numpy as np

from funciones.filtPond import filtA, filtC

def filEnv(x, fs, gainAuxZ, gainAuxC, gainAuxA ,ATT,RLS, env):
    T = 1/fs;    #% Periodo de muestreo T.
    consAT = 1-2.7182**(-1*T/ATT) # Constante tiempo de ataque
    consRL = 1-2.7182**(-1*T/RLS) # Constante tiempo de relaje
    xZ = x                          # Aplicacion de filtro Z
    xA = filtA(x,fs)                # Aplicacion de filtro A
    xC = filtC(x,fs)                # Aplicacion de filtro C
# Para encontrar envuelta le aplico un FPB con Fc en 80Hz a la señal original 
# tal como lo recomienda el libro de Zolzer, en este caso esa informacion me la da "env"
    gainZ = np.zeros(len(x)-1) # la ganancia inicialmente es un vector de ceros
    gainC = gainZ # la ganancia inicialmente es un vector de ceros
    gainA = gainZ # la ganancia inicialmente es un vector de ceros
# debido a que nosotros trabajamos con vectores de corta duracion, siempre se esta reseteando a cero la ganancia
    gainZ[0] = gainAuxZ     
    gainC[0] = gainAuxC     
    gainA[0] = gainAuxA     
    for i in range(1, len(x)-1):
        # condicionales para filtro Z
        if np.absolute(xZ[i-1]) == env[i-1]:
            gainZ[i] = gainZ[i-1]*(1-consRL) + np.absolute(xZ[i])
        else:
            if np.absolute(xZ[i-1]) > env[i-1]:     # si la envuelta es menor a la señal entonces aplico ataque
                gainZ[i] = gainZ[i-1]*(1-consAT) + np.absolute(xZ[i]) 
            else:                                   # por el contrario aplico relaje   
                gainZ[i] = gainZ[i-1]*(1-consRL)
        # condicionale para filtro C
        if np.absolute(xC[i-1]) == env[i-1]:
            gainC[i] = gainC[i-1]*(1-consRL) + np.absolute(xC[i])
        else:
            if np.absolute(xC[i-1]) > env[i-1]:
                gainC[i] = gainC[i-1]*(1-consAT) + np.absolute(xC[i])
            else:
                gainC[i] = gainC[i-1]*(1-consRL)

        # condicionale para filtro A
        if np.absolute(xA[i-1]) == env[i-1]:
            gainA[i] = gainA[i-1]*(1-consRL) + np.absolute(xA[i])
        else:
            if np.absolute(xA[i-1]) > env[i-1]:
                gainA[i] = gainA[i-1]*(1-consAT) + np.absolute(xA[i])
            else:
                gainA[i] = gainA[i-1]*(1-consRL)

    xAInstZ = gainZ*consAT
    gainUltZ = gainZ[-1]    #envio el ultimo valor del vector de la ganancia 
    xAInstC = gainC*consAT
    gainUltC = gainC[-1]
    xAInstA = gainA*consAT
    gainUltA = gainA[-1]

    return (xAInstZ, gainUltZ, xAInstC, gainUltC, xAInstA, gainUltA)

def filEnvPico(x, fs, gainPico, env):
    ATT = 0.000005
    RLS = 0.000005
    T = 1/fs;    #% Periodo de muestreo T.
    consAT = 1-2.7182**(-1*T/ATT) # Constante tiempo de ataque
    consRL = 1-2.7182**(-1*T/RLS) # Constante tiempo de relaje
    # print(consAT)
    # print(consRL)
# Para encontrar envuelta le aplico un FPB con Fc en 80Hz a la señal original 
# tal como lo recomienda el libro de Zolzer, en este caso esa informacion me la da "env"
    gain = np.zeros(len(x)) # la ganancia inicialmente es un vector de ceros
# debido a que nosotros trabajamos con vectores de corta duracion, siempre se esta reseteando a cero la ganancia
    gain[0] = gainPico     
      
    for i in range(1, len(x)):
        if np.absolute(x[i-1]) == env[i-1]:
            gain[i] = gain[i-1]*(1-consRL) + np.absolute(x[i])
        else:
            if np.absolute(x[i-1]) > env[i-1]:
                gain[i] = gain[i-1]*(1-consAT) + np.absolute(x[i])
            else:
                gain[i] = gain[i-1]*(1-consRL)

    x = gain*consAT
    gainUlt = gain[-1]

    return (x, gainUlt)
 
def filEnvInst(x, fs, gainInst, env):
    ATT = 0.035
    RLS = 0.75
    T = 1/fs;    #% Periodo de muestreo T.
    consAT = 1-2.7182**(-1*T/ATT) # Constante tiempo de ataque
    consRL = 1-2.7182**(-1*T/RLS) # Constante tiempo de relaje
    # print(consAT)
    # print(consRL)
# Para encontrar envuelta le aplico un FPB con Fc en 80Hz a la señal original 
# tal como lo recomienda el libro de Zolzer, en este caso esa informacion me la da "env"
    gain = np.zeros(len(x)) # la ganancia inicialmente es un vector de ceros
# debido a que nosotros trabajamos con vectores de corta duracion, siempre se esta reseteando a cero la ganancia
    gain[0] = gainInst     
      
    for i in range(1, len(x)):
        # condicionale para filtro A
        if np.absolute(x[i-1]) == env[i-1]:
            gain[i] = gain[i-1]*(1-consRL)
        else:
            if np.absolute(x[i-1]) > env[i-1]:
                gain[i] = gain[i-1]*(1-consAT) + np.absolute(x[i])
            else:
                gain[i] = gain[i-1]*(1-consRL)

    x = gain*consAT
    gainUlt = gain[-1]

    return (x, gainUlt)

def filEnvFast(x, fs, gainFast, env):
    ATT = 0.125
    RLS = 0.125
    T = 1/fs;    #% Periodo de muestreo T.
    consAT = 1-2.7182**(-1*T/ATT) # Constante tiempo de ataque
    consRL = 1-2.7182**(-1*T/RLS) # Constante tiempo de relaje
    # print(consAT)
    # print(consRL)
# Para encontrar envuelta le aplico un FPB con Fc en 80Hz a la señal original 
# tal como lo recomienda el libro de Zolzer, en este caso esa informacion me la da "env"
    gain = np.zeros(len(x)) # la ganancia inicialmente es un vector de ceros
# debido a que nosotros trabajamos con vectores de corta duracion, siempre se esta reseteando a cero la ganancia
    gain[0] = gainFast     
      
    for i in range(1, len(x)):
        # condicionale para filtro A
        if np.absolute(x[i-1]) == env[i-1]:
            gain[i] = gain[i-1]*(1-consRL) 
        else:
            if np.absolute(x[i-1]) > env[i-1]:
                gain[i] = gain[i-1]*(1-consAT) + np.absolute(x[i])
            else:
                gain[i] = gain[i-1]*(1-consRL)

    x = gain*consAT
    gainUlt = gain[-1]

    return (x, gainUlt)

def filEnvSlow(x, fs, gainSlow, env):
    ATT = 1.0
    RLS = 1.0
    T = 1/fs;    #% Periodo de muestreo T.
    consAT = 1-2.7182**(-1*T/ATT) # Constante tiempo de ataque
    consRL = 1-2.7182**(-1*T/RLS) # Constante tiempo de relaje
    # print(consAT)
    # print(consRL)
# Para encontrar envuelta le aplico un FPB con Fc en 80Hz a la señal original 
# tal como lo recomienda el libro de Zolzer, en este caso esa informacion me la da "env"
    gain = np.zeros(len(x)) # la ganancia inicialmente es un vector de ceros
# debido a que nosotros trabajamos con vectores de corta duracion, siempre se esta reseteando a cero la ganancia
    gain[0] = gainSlow     
      
    for i in range(1, len(x)):
        # condicionale para filtro A
        if np.absolute(x[i-1]) == env[i-1]:
            gain[i] = gain[i-1]*(1-consRL) 
        else:
            if np.absolute(x[i-1]) > env[i-1]:
                gain[i] = gain[i-1]*(1-consAT) + np.absolute(x[i])
            else:
                gain[i] = gain[i-1]*(1-consRL)

    x = gain*consAT
    gainUlt = gain[-1]

    return (x, gainUlt)