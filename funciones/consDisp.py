import sounddevice as sd

def consDisp():
    disp = sd.query_devices() # funcion principal

    dispNameInputStr=[]
    dispNameInputNum=[]

    dispNameOutputStr=[]
    dispNameOutputNum=[]

    frecMuestreo=[]


    for i in range(0,len(disp)):
        if disp[i].get('max_input_channels') > 0:
            dispNameInputStr.append(disp[i].get('name'))
            dispNameInputNum.append(i)
        if disp[i].get('max_output_channels') > 0:
            dispNameOutputStr.append(disp[i].get('name'))
            dispNameOutputNum.append(i)
        frecMuestreo.append(disp[i].get('default_samplerate'))

    return (dispNameInputStr, dispNameInputNum, dispNameOutputStr, dispNameOutputNum)


# DispInputStr    = {};DispOutputStr   = {};DispInOutStr    = {}; % Variables STRINGS
# DispInputSer    = {};DispOutputSer   = {};DispInOutSer    = {}; % Variables Servidor
# DispMuestreo    = {};DispServidor    = {};                      % Valiables Varias
# Entrada         = [];Salida          = [];EntSal          = [];
# DispInputNum    = [];DispOutputNum   = [];DispInOutNum    = []; % Variables Numero de ID

# for i = 1:length(disp)
#     if(disp(1,i).NrInputChannels > 0) 
#         DispInputStr = [DispInputStr(:); sprintf('ID: %i - Nombre: %s',disp(1,i).DeviceIndex, disp(1,i).DeviceName)];
#         DispInputNum = [DispInputNum(:); disp(1,i).DeviceIndex;];
#         DispInputSer = [DispInputSer(:); disp(1,i).HostAudioAPIName;];
#     end
#     if(disp(1,i).NrOutputChannels > 0) 
#         DispOutputStr = [DispOutputStr(:) ; sprintf('ID: %i - Nombre: %s',disp(1,i).DeviceIndex, disp(1,i).DeviceName)];   
#         DispOutputNum = [DispOutputNum(:); disp(1,i).DeviceIndex;];
#         DispOutputSer = [DispOutputSer(:); disp(1,i).HostAudioAPIName];
#     end
#     if(disp(1,i).HostAudioAPIId==3)
#         DispInOutStr = [DispInOutStr(:); sprintf('ID: %i - Nombre: %s',disp(1,i).DeviceIndex, disp(1,i).DeviceName)];
#         DispInOutNum = [DispInOutNum(:); disp(1,i).DeviceIndex;];
#         DispInOutSer = [DispInOutSer(:); disp(1,i).HostAudioAPIName];
#     end
#     DispServidor     = [DispServidor(:); disp(1,i).HostAudioAPIName];
#     DispMuestreo = [DispMuestreo(:); num2str(disp(1,i).DefaultSampleRate)];
# end

# %Datos generales
# Muestreo = unique(DispMuestreo);
# Servidor = unique(DispServidor);
# % Datos de entrada
# Entrada.Str = DispInputStr;
# Entrada.Num = DispInputNum';
# Entrada.Ser = DispInputSer;
# % Datos de salida
# Salida.Str = DispOutputStr;
# Salida.Num = DispOutputNum';
# Salida.Ser = DispOutputSer;
# %Datos de entrada - salida
# EntSal.Str = DispInOutStr;
# EntSal.Num = DispInOutNum';

# Objeto = disp; %Objeto general