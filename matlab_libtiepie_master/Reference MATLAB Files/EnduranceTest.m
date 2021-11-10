clear all
close all

%% Settings
name = 'Debugging';

freq = 2100;
TestDuration = 10; % Duration of the test
MeasFreq = 1; % time interval between measurements (approximative)

Lrec = 10000; % Recording length
Fs = 1e6; % Sampling freq

ampIn = 12; % input amplitude in V
ampRange = 2; % oscillo amplitude in V


%% Getting the data
system('taskkill /im MultiChannel.exe'); % Close TiePie in case it was open

if verLessThan('matlab', '8')
    error('Matlab 8.0 (R2012b) or higher is required.');
end

% Open LibTiePie and display library info if not yet opened:
import LibTiePie.Const.*
import LibTiePie.Enum.*

if ~exist('LibTiePie', 'var')
    % Open LibTiePie:
    LibTiePie = LibTiePie.Library;
end

% Enable network search:       
LibTiePie.Network.AutoDetectEnabled = true;

% Search for devices:
LibTiePie.DeviceList.update();

% figure('Name','Live plot')

figure('Name','Live plot')
vamprms = [];
ave = []; % average signal value
DatStor = {};



item = LibTiePie.DeviceList.getItemByIndex(0);
gen = item.openGenerator();


    
% Generator settings:

        % Set signal type:
        gen.SignalType = ST.SINE;

        % Set frequency:
        gen.Frequency = freq; 

        % Set amplitude:
        gen.Amplitude = ampIn; % 2 V

        % Set offset:
        gen.Offset = 0; % 0 V

        % Enable output:
        gen.OutputOn = true;
        
        % recover some information from generator
        % vGenFreq(incre) = gen.Frequency;

        % Start signal generation:
        gen.start();


tic
duration = 0;
vDuration = [];
while duration < TestDuration

%     for k = 0 : LibTiePie.DeviceList.Count - 1
%         item = LibTiePie.DeviceList.getItemByIndex(k);
%         if item.canOpen(DEVICETYPE.OSCILLOSCOPE) && item.canOpen(DEVICETYPE.GENERATOR)
%             scp = item.openOscilloscope();
%             if ismember(MM.BLOCK, scp.MeasureModes)
%                 gen = item.openGenerator();
%                 break;
%             else
%                 clear scp;
%             end
%         end
%     end
    item = LibTiePie.DeviceList.getItemByIndex(0);
    scp = item.openOscilloscope();
    
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

        % Start measurement:
        scp.start();

        % Wait for measurement to complete:
        while ~scp.IsDataReady
            pause(10e-3) % 10 ms delay, to save CPU time.
        end

        % Get data:
        arData = scp.getData();
        ave = [ave; mean(arData)];
        arData = arData - mean(arData);

        % Get all channel data value ranges (which are compensated for probe gain/offset):
        clear darRangeMin;
        clear darRangeMax;
        for i = 1 : length(scp.Channels)
            [darRangeMin(i), darRangeMax(i)] = scp.Channels(i).getDataValueRange();
        end

        % Plot results:
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

    else
        error('No oscilloscope available with block measurement support or generator available in the same unit!');
    end

    DatStor = {DatStor arData};
    
    % Plot
    amprms = rms(arData-mean(arData));
    vamprms = [vamprms; amprms];
    
    duration = toc;
    vDuration = [vDuration duration];
    plot(vDuration, vamprms*1e3)
    grid on;
    xlabel('Duration [s]');
    ylabel('Oscillation amplitude [mV]');
    legend('Channel 1','Channel 2');
    
%     plot(Vvolt,rms(arData-mean(arData)));
%     grid on;
%     xlabel('Input piezo voltage (to be converted in length) [V]');
%     ylabel('Output voltage [mV]');
%     legend('Channel 1','Channel 2')

    pause(MeasFreq);
end

% Stop generator:
gen.stop();

% Disable output:
gen.OutputOn = false;

% Close generator:
clear gen;


save([name,' - Endurance Test - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS')]);

clear all % necessary to use TiePie after MatLab

system('cd C:\Users\cri\Documents\Etienne & start MatLab.tps'); % Reopen TiePie

return

%% Post process 

% % Amplitude
% vamp = [];
% for k = 1:length(DatStor)
%     amp = max(DatStor{1,k})-min(DatStor{1,k});
%     vamp = [vamp; amp];
% end
% 
% % Plot
% figure('Name','min max')
% plot(vfreq,vamp,'-o')
% grid on;
% xlabel('Frequency [Hz]');
% ylabel('Amplitude [V]');
% legend('Channel 1','Channel 2');

% FFT
vfour = [];
for k = 1:length(DatStor)
    four = abs(fft(DatStor{1,k}-mean(DatStor{1,k})));
    four = four(1:Lrec/2+1,:);
    vfour = [vfour four];
end

% Plot
% figure('Name','fft')
% plot(Fs*(0:Lrec/2)/Lrec*1e-3,vfour);
% grid on;
% xlabel('Frequency [kHz]');
% ylabel('Amplitude');


% RMS
vamprms = [];
for k = 1:length(DatStor)
    amprms = rms(DatStor{1,k}-mean(DatStor{1,k}));
    vamprms = [vamprms; amprms];
end

% Plot
figure('Name','RMS')
plot(vfreq/1e3,vamprms*1e3)
grid on;
xlabel('Frequency [kHz]');
ylabel('Oscillation amplitude [mV]');
legend('Channel 1','Channel 2');

% Plot
figure('Name','Average signal')
plot(vfreq/1e3,ave*1e3)
grid on;
xlabel('Frequency [kHz]');
ylabel('Amplitude [mV]');
legend('Channel 1','Channel 2');

mean(ave)

% % Plot
normal = vamprms(:,1)./vamprms(:,2);
% figure('Name','RMS normalised')
% plot(vfreq/1e3,normal)
% grid on;
% xlabel('Frequency [kHz]');
% ylabel('Amplification factor');

%% Peaks
figure('Name','RMS peaks')
findpeaks(normal,vfreq/1e3,'MinPeakHeight',2*mean(normal))
grid on;
xlabel('Frequency [kHz]');
ylabel('Amplification factor');

[pks,loc] = findpeaks(normal,vfreq/1e3,'MinPeakHeight',2*mean(normal));
cond = sum(loc >= (target-tolerance)/1e3 & loc <= (target+tolerance)/1e3);
if cond == 0
    disp('Failed chip')
else
    disp('Passed chip')
end


%% test
vamp = [];
for k = 1:length(DatStor)
    amp = mean(DatStor{1,k});
    vamp = [vamp; amp];
end

% % Plot
% figure('Name','amp mean')
% plot(vfreq/1e3,vamp-mean(vamp))
% grid on;
% xlabel('Frequency [kHz]');
% ylabel('Amplitude [V]');
% legend('Channel 1','Channel 2');
% 
% % Plot
% figure('Name','amp mean 2')
% plot(vfreq/1e3,vamp)
% grid on;
% xlabel('Frequency [kHz]');
% ylabel('Amplitude [V]');
% legend('Channel 1','Channel 2');

% % RMS
% vamprms = [];
% for k = 1:length(DatStor)
%     amprms = rms(DatStor{1,k}(Lrec/2:end,:)-mean(DatStor{1,k}(Lrec/2:end,:)));
%     vamprms = [vamprms; amprms];
% end

% % Plot
% figure('Name','RMS')
% plot(vfreq/1e3,vamprms)
% grid on;
% xlabel('Frequency [kHz]');
% ylabel('Amplitude [V]');
% legend('Channel 1','Channel 2');
% 
% % FFT
% vfour = [];
% for k = 1:length(DatStor)
%     four = abs(fft(DatStor{1,k}(Lrec/2:end,:)-mean(DatStor{1,k}(Lrec/2:end,:))));
%     four = four(1:Lrec/4+1,:);
%     vfour = [vfour four];
% end
% 
% % Plot
% figure('Name','fft')
% plot(Fs*(0:Lrec/4)/Lrec*2,vfour);
% grid on;
% xlabel('Frequency [Hz]');
% ylabel('Amplitude');

save([name,' - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS')]);
loc

%% Finder 
% [f,dummy] = ginput(1);
% point = round((f*1e3 - start)*(points-1)/(stop-start) + 1);
% 
% % Plot
% figure
% plot((0:Lrec-1)/Fs, DatStor{1,point});
% xlabel('Time [s]');
% ylabel('Amplitude [V]');
% legend('Channel 1','Channel 2');
% grid on;

%% Test 07/05/2021
% pos = 90;
% 
% figure
% plot((1:Lrec) / Fs, DatStor{1,pos}-mean(DatStor{1,pos}));
% xlabel('Time [s]');
% ylabel('Amplitude [V]');
% legend('Channel 1','Channel 2');
% grid on;