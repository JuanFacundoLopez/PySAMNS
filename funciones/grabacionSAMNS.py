import numpy as np 
from filEnv import filEnv, filEnvPico, filEnvInst, filEnvFast, filEnvSlow, filtA, filtC
from scipy.signal import  lfilter


def grabacion(ctrl):

    ctrl.cModel.setSignalData(ctrl.wf_data)   #Guardo en modelo
    wf_dataZ = ctrl.wf_data
    env = lfilter(ctrl.b, ctrl.a, wf_dataZ)

    # Encontramos el valor de la envuelta Pico
    
    (recorderPicoZ, ctrl.gainZP) = filEnvPico(wf_dataZ, ctrl.RATE, ctrl.gainZP, env)
    (recorderInstZ, ctrl.gainZI) = filEnvInst(wf_dataZ, ctrl.RATE, ctrl.gainZI, env)
    (recorderFastZ, ctrl.gainZF) = filEnvFast(wf_dataZ, ctrl.RATE, ctrl.gainZF, env)
    (recorderSlowZ, ctrl.gainZS) = filEnvSlow(wf_dataZ, ctrl.RATE, ctrl.gainZS, env)

    rmsPicoZ = np.sqrt(np.mean(recorderPicoZ**2))
    rmsPicoZLog = 20*np.log10(rmsPicoZ)
    rmsInstZ = np.sqrt(np.mean(recorderInstZ**2))
    rmsInstZLog = 20*np.log10(rmsInstZ)
    rmsFastZ = np.sqrt(np.mean(recorderFastZ**2))
    rmsFastZLog = 20*np.log10(rmsFastZ)
    rmsSlowZ = np.sqrt(np.mean(recorderSlowZ**2))
    rmsSlowZLog = 20*np.log10(rmsSlowZ)

    wf_dataC = filtC(wf_dataZ, ctrl.RATE)

    (recorderPicoC, ctrl.gainCP) = filEnvPico(wf_dataC, ctrl.RATE, ctrl.gainCP, env)
    (recorderInstC, ctrl.gainCI) = filEnvInst(wf_dataC, ctrl.RATE, ctrl.gainCI, env)
    (recorderFastC, ctrl.gainCF) = filEnvFast(wf_dataC, ctrl.RATE, ctrl.gainCF, env)
    (recorderSlowC, ctrl.gainCS) = filEnvSlow(wf_dataC, ctrl.RATE, ctrl.gainCS, env)


    rmsPicoC = np.sqrt(np.mean(recorderPicoC**2))
    rmsPicoCLog = 20*np.log10(rmsPicoC)
    rmsInstC = np.sqrt(np.mean(recorderInstC**2))
    rmsInstCLog = 20*np.log10(rmsInstC)
    rmsFastC = np.sqrt(np.mean(recorderFastC**2))
    rmsFastCLog = 20*np.log10(rmsFastC)
    rmsSlowC = np.sqrt(np.mean(recorderSlowC**2))
    rmsSlowCLog = 20*np.log10(rmsSlowC)

    wf_dataA = filtA(wf_dataZ, ctrl.RATE)

    (recorderPicoA, ctrl.gainAP) = filEnvPico(wf_dataA, ctrl.RATE, ctrl.gainAP,env)
    (recorderInstA, ctrl.gainAI) = filEnvInst(wf_dataA, ctrl.RATE, ctrl.gainAI,env)
    (recorderFastA, ctrl.gainAF) = filEnvFast(wf_dataA, ctrl.RATE, ctrl.gainAF,env)
    (recorderSlowA, ctrl.gainAS) = filEnvSlow(wf_dataA, ctrl.RATE, ctrl.gainAS,env)

    rmsPicoA = np.sqrt(np.mean(recorderPicoA**2))
    rmsPicoALog = 20*np.log10(rmsPicoA)
    rmsInstA = np.sqrt(np.mean(recorderInstA**2))
    rmsInstALog = 20*np.log10(rmsInstA)
    rmsFastA = np.sqrt(np.mean(recorderFastA**2))
    rmsFastALog = 20*np.log10(rmsFastA)
    rmsSlowA = np.sqrt(np.mean(recorderSlowA**2))
    rmsSlowALog = 20*np.log10(rmsSlowA)

    # Encontramos el valor de la envuelta Istantanea

    # Guardo los valores en modelo

    ctrl.cModel.setNivelesZ( rmsPicoZLog, rmsInstZLog, rmsFastZLog, rmsSlowZLog)
    ctrl.cModel.setNivelesC( rmsPicoCLog, rmsInstCLog, rmsFastCLog, rmsSlowCLog)
    ctrl.cModel.setNivelesA( rmsPicoALog, rmsInstALog, rmsFastALog, rmsSlowALog)
