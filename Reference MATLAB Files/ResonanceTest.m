clear all
close all

%% Settings
name = 'wf9148x12KxXXXX';

start = 5e3; % Sweep starting frequency in Hz
stop = 20e3; % Sweep stop frequency in Hz
points = 150; % Number of points for the sweep

ampIn = 2; % input amplitude in V
ampRange = 3; % oscillo amplitude in V

Lrec = 10000; % Recording length
Fs = 1e6; % Sampling freq

target = 12e3; % target resonance frequency in Hz
tolerance = 3e3; % tolerance for the past fail in Hz

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
for incre = 1:points
    freq = start + (stop - start)/(points-1)*(incre-1);
    vfreq(incre) = freq;
    
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
        gen.Frequency = freq; 

        % Set amplitude:
        gen.Amplitude = ampIn; % 2 V

        % Set offset:
        gen.Offset = 0; % 0 V

        % Enable output:
        gen.OutputOn = true;

        % Print oscilloscope info:
        %display(scp);

        % Print generator info:
        %display(gen);
        
        % recover some information from generator
        vGenFreq(incre) = gen.Frequency;

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

        % Close generator:
        clear gen;
    else
        error('No oscilloscope available with block measurement support or generator available in the same unit!');
    end

    DatStor{incre} = arData;
    
    % Plot
    amprms = rms(arData-mean(arData));
    vamprms = [vamprms; amprms];
    
    plot(vfreq/1e3,vamprms*1e3)
    grid on;
    xlabel('Frequency [kHz]');
    ylabel('Oscillation amplitude [mV]');
    legend('Channel 1','Channel 2');
    
%     plot(Vvolt,rms(arData-mean(arData)));
%     grid on;
%     xlabel('Input piezo voltage (to be converted in length) [V]');
%     ylabel('Output voltage [mV]');
%     legend('Channel 1','Channel 2')
end

clear LibTiePie % necessary to use TiePie after MatLab

system('cd C:\Users\cri\Documents\Etienne & start MatLab.tps'); % Reopen TiePie

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

[M,I] = max(vamprms(:,1));
normal = vamprms(:,1)/M;

cutofff = [interp1(normal(1:I),vfreq(1:I),0.5) interp1(normal(I:end),vfreq(I:end),0.5)];
Qfactor = vfreq(I)/(cutofff(2)-cutofff(1));
DampingRatio = 1/2/Qfactor;

% Plot
figure('Name','RMS')
subplot(6,3,[1:15])
plot(vfreq/1e3,vamprms*1e3)
grid on; hold on;
xlabel('Frequency [kHz]');
ylabel('Oscillation amplitude [mV]');
scatter(cutofff/1e3,[0.5 0.5]*M*1e3,'rx');
legend('Channel 1','Channel 2','Bandwidth frequency');

subplot(6,3,16); axis off;
text(0,0,['Resonance frequency :',newline,num2str(vfreq(I)/1e3),' kHz'])
subplot(6,3,17); axis off;
text(0,0,['Q factor : ',num2str(Qfactor)])
subplot(6,3,18); axis off;
text(0,0,['Damping ratio : ',num2str(DampingRatio)])

saveas(gcf,[name,' - RMS - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS'),'.png']);

% % Plot
% figure('Name','Average signal')
% plot(vfreq/1e3,ave*1e3)
% grid on;
% xlabel('Frequency [kHz]');
% ylabel('Amplitude [mV]');
% legend('Channel 1','Channel 2');
% 
% mean(ave)
% 
% % % Plot
% normal = vamprms(:,1)./vamprms(:,2);
% % figure('Name','RMS normalised')
% % plot(vfreq/1e3,normal)
% % grid on;
% % xlabel('Frequency [kHz]');
% % ylabel('Amplification factor');

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

save([name,' - Resonance test - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS')]);

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