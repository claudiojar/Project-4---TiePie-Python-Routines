clear all;
close all;

%% Saving name
name = 'DM-0001-DC1_on_top ';

%% Settings ref perfect mirror
refCh = [2.340 1.123]; % Signal with perfect mirror in V [Ch1 Ch2]

%% Settings for oscilloscope
Lrec = 10000; % Recording length
Fs = 1e6; % Sampling freq

ampRange = 4; % oscillo amplitude in V

%%
global h; % make h a global variable so it can be used outside the main
          % function. Useful when you do event handling and sequential move
%% Create Matlab Figure Container
fpos    = get(0,'DefaultFigurePosition'); % figure default position
fpos(3) = 650; % figure window size;Width
fpos(4) = 450; % Height
f = figure('Position', fpos,...
           'Menu','None',...
           'Name','APT GUI');
%% Create ActiveX Controller
%h = actxcontrol('MG17Piezo1.APTPiezoCtrl.1',[20 20 600 400 ], f);
h = actxcontrol('MG17SYSTEM.MG17SystemCtrl.1', [20 20 600 400 ], f);

%% Initialize
% Start Control
% Set the Serial Number
SN = 81837345; % put in the serial number of the hardware
h_Piezo = actxcontrol('MGPIEZO.MGPiezoCtrl.1', [20 20 600 400 ], f);

h_Piezo.StartCtrl;

set(h_Piezo,'HWSerialNum', SN);
% Indentify the device

h_Piezo.Identify;
pause(2); % waiting for the GUI to load up;
%h_Piezo.SetVoltageOutputLimit
%h_Piezo.SetVoltOutput

%%
h_Piezo.SetVoltOutput(0,20)

%% TiePie stuffs
system('taskkill /im MultiChannel.exe'); % Close TiePie in case it was open

if verLessThan('matlab', '8')
    error('Matlab 8.0 (R2012b) or higher is required.');
end

% Open LibTiePie and display library info if not yet opened:
import LibTiePie.Const.*
import LibTiePie.Enum.*

if ~exist('LibTiePie', 'var')
    % Open LibTiePie:
    LibTiePie = LibTiePie.Library
end

% Enable network search:       
LibTiePie.Network.AutoDetectEnabled = true;

% Search for devices:
LibTiePie.DeviceList.update();

Vvolt = []; % Volt vector
Vch = []; % Channel signal vector

figure('Name','Live plot')

%% Set Acquire
samplerate = 1;
bufferdelay = 0.1;
df=(1.25*10^6); 
    %samplerate = 1024;
    %bufferdelay = 134.218*10^-3;
    %df=(12.2*10^4);
    %samplerate = 8192;
    %bufferdelay = 1.074;ju
    %df=(1.52*10^4);
dt = 1/df;

clear total;
iitotal=20;
for tt=1%:25
trigger=0;
voltstop=0;
hystTest = [3:1:65]
for ii = hystTest % iitotal:-0.25:3
volt=(ii-1);
%for ii = 70:-1:1

if volt>75
    volt = 75;
end
%if voltstop>0
%    volt=voltstop;
%end
h_Piezo.SetVoltOutput(0,volt)

pause(.01)
Vvolt = [Vvolt; volt];

%% tiepie in the loop
% Try to open an oscilloscope with block measurement support and a generator in the same device:
    clear scp;
    clear gen;
    for k = 0 : LibTiePie.DeviceList.Count - 1
        item = LibTiePie.DeviceList.getItemByIndex(k);
        if item.canOpen(DEVICETYPE.OSCILLOSCOPE) && item.canOpen(DEVICETYPE.GENERATOR)
            scp = item.openOscilloscope();
            if ismember(MM.BLOCK, scp.MeasureModes)
                gen = item.openGenerator();
                break;
            else
                clear scp;
            end
        end
    end
    clear item



    if exist('scp', 'var') && exist('gen', 'var')
        % Oscilloscope settings:

        % Set measure mode:
        scp.MeasureMode = MM.BLOCK;

        % Set sample frequency:
        scp.SampleFrequency = Fs; % 1 MHz

        % Set record length:
        scp.RecordLength = Lrec; % 10000 Samples

        % Set pre sample ratio:
        scp.PreSampleRatio = 0; % 0 %

        % For all channels:
        for ch = scp.Channels
            % Enable channel to measure it:
            ch.Enabled = true;

            % Set range:
            ch.Range = ampRange; 

            % Set coupling:
            ch.Coupling = CK.DCV; % DC Volt

            % Release reference:
            clear ch;
        end

        % Set trigger timeout:
        scp.TriggerTimeOut = 1; % 1 s

        % Disable all channel trigger sources:
        for ch = scp.Channels
            ch.Trigger.Enabled = false;
            clear ch;
        end

        % Locate trigger input:
        triggerInput = scp.getTriggerInputById(TIID.GENERATOR_NEW_PERIOD); % or TIID.GENERATOR_START or TIID.GENERATOR_STOP

        if triggerInput == false
            clear triggerInput;
            clear scp;
            clear gen;
            error('Unknown trigger input!');
        end

        % Enable trigger input:
        triggerInput.Enabled = true;

        % Release reference to trigger input:
        clear triggerInput;

        % Generator settings:

        % Set signal type:
        gen.SignalType = ST.SINE;

        % Set frequency:
        gen.Frequency = 1e3; 

        % Set amplitude:
        gen.Amplitude = 2; % 2 V

        % Set offset:
        gen.Offset = 0; % 0 V

        % Enable output:
        gen.OutputOn = true;

        % Print oscilloscope info:
        %display(scp);

        % Print generator info:
        %display(gen);

        % Start measurement:
        scp.start();

        % Start signal generation:
        gen.start();

        % Wait for measurement to complete:
        while ~scp.IsDataReady
            pause(10e-3) % 10 ms delay, to save CPU time.
        end

        % Stop generator:
        gen.stop();

        % Disable output:
        gen.OutputOn = false;

        % Get data:
        arData = scp.getData();
        Vch = [Vch; mean(arData)];

        % Get all channel data value ranges (which are compensated for probe gain/offset):
        clear darRangeMin;
        clear darRangeMax;
        for i = 1 : length(scp.Channels)
            [darRangeMin(i), darRangeMax(i)] = scp.Channels(i).getDataValueRange();
        end

%         % Plot results:
%         if mod(incre,40) == 1
%             figure
%             plot((1:scp.RecordLength) / scp.SampleFrequency, arData);
%             xlabel('Time [s]');
%             ylabel('Amplitude [V]');
%             legend('Channel 1','Channel 2');
%             grid on;
%         end

        % Close oscilloscope:
        clear scp;

        % Close generator:
        clear gen;
    else
        error('No oscilloscope available with block measurement support or generator available in the same unit!');
    end
    
    plot(Vvolt,Vch*1e3);
    grid on;
    xlabel('Input piezo voltage (to be converted in length) [V]');
    ylabel('Output voltage [mV]');
    legend('Channel 1','Channel 2')

end
end

h_Piezo.SetVoltOutput(0,20)

clear LibTiePie % necessary to use TiePie after MatLab

system('cd C:\Users\julie\OneDrive\Documents\MATLAB & start MatLab.tps'); % Reopen TiePie

%% Plot 
close all 

dist = Vvolt*0.32; % convert in micrometers

subplot(2,2,1)
title('Percentage of Ref')
plot(dist,Vch./refCh*100);
grid on;
xlabel('Distance from mirror (arbitrary 0) [\mum]');
ylabel('Coupling [%]');
legend('Channel 1','Channel 2')


subplot(2,2,2)
title('Real voltage value')
plot(Vvolt,Vch*1e3);
grid on;
xlabel('Input piezo voltage (to be converted in length) [V]');
ylabel('Output voltage [mV]');
legend('Channel 1','Channel 2')

max(Vch(:,1)./refCh(1)*100)

% figure
% dist = Vvolt*25/75; % Distance en micron
% plot(dist,Vch*1e3);
% grid on;
% xlabel('Distance from the starting point (close to the mirror) [\mum]');
% ylabel('Output voltage [mV]');
% legend('Channel 1','Channel 2')

subplot(2,2,3)
title('Gradient with distance')
plot(dist,gradient(Vch(:,1)/refCh(1)*100,25/75));
grid on; hold on;
plot(dist,gradient(Vch(:,2)/refCh(2)*100,25/75));
xlabel('Distance from mirror (arbitrary 0) [\mum]');
ylabel('Sensitivity [%/\mum]');
legend('Channel 1','Channel 2')


subplot(2,2,4)
title('voltage values')
plot(dist,Vch*1e3);
grid on;
xlabel('Distance from mirror (arbitrary 0) [\mum]');
ylabel('Output voltage [mV]');
legend('Channel 1','Channel 2')

saveas(gcf,[name,' - Coupling - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS'),'.png']);

% figure
% plot(dist,-gradient(Vch(:,2)/0.227*70,25/75));
% grid on;
% xlabel('Distance from the starting point (close to the mirror) [\mum]');
% ylabel('Output voltage [mV]');
% legend('Channel 1','Channel 2')

%% Saving variables
save([name,' - Fiber char - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS')]);

return 
