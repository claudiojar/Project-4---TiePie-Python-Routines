% OscilloscopeStream.m
close all
clear all
tic

%% Parameters
name = 'DM-0001_afterUV_drift'; % Saving name
time = 1; % pause time to add between measurements (5.5 s min)  [s]
range = 4; % range in V (CAREFUL think about changing it !!!!)

system('taskkill /im MultiChannel.exe'); % Close TiePie in case it was open

ButtonHandle = uicontrol('Style', 'PushButton', 'String', 'Stop measurement', 'Callback', 'delete(gcbf)');

MeanKulite=[];
DC2=[];
DC1=[];

timeline = [];
while ishandle(ButtonHandle)
    
    %
    % This example performs a stream mode measurement and writes the data to OscilloscopeStream.csv.
    %
    % Find more information on http://www.tiepie.com/LibTiePie .
    
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
    
    
    % Try to open an oscilloscope with stream measurement support:
    clear scp;
    for k = 0 : LibTiePie.DeviceList.Count - 1
        item = LibTiePie.DeviceList.getItemByIndex(k);
        if item.canOpen(DEVICETYPE.OSCILLOSCOPE)
            scp = item.openOscilloscope();
            if ismember(MM.STREAM, scp.MeasureModes)
                break;
            else
                clear scp;
            end
        end
    end
    
    
    if exist('scp', 'var')
        % Set measure mode:
        scp.MeasureMode = MM.STREAM;
        
        % Set sample frequency:
        scp.SampleFrequency = 1e2; % 1 kHz
        
        % Set record length:
        scp.RecordLength = 500; % 1 kS
        
        % For all channels:
        for ch = scp.Channels
            % Enable channel to measure it:
            ch.Enabled = true;
            
            % Set range:
            ch.Range = range; %  V
            
            % Set coupling:
            ch.Coupling = CK.DCV; % DC Volt
            
            clear ch;
        end
        
        % Print oscilloscope info:
        % display(scp);
        
        % Prepeare CSV writing:
        filename = 'OscilloscopeStream26.bis.csv';
        if exist(filename, 'file')
            delete(filename)
        end
        data = [];
        
        % Start measurement:
        scp.start();
        
        % Measure 10 chunks:
        for k = 1 : 1
            % Display a message, to inform the user that we still do something:
            % fprintf('Data chunk %u\n', k);
            
            % Wait for measurement to complete:
            while ~(scp.IsDataReady || scp.IsDataOverflow)
                pause(10e-3) % 10 ms delay, to save CPU time.
            end
            
            if scp.IsDataOverflow
                error('Data overflow!')
            end
            
            % Get data:
            newData = scp.getData();
            
            % Apped new data to plot:
            data = [data ; newData];
            %     figure(123);
            %     plot(data);
            
            % Append new data to CSV file:
            %      dlmwrite(filename, newData, '-append');
        end
        
        %   fprintf('Data written to: %s\n', filename);
        
        % Stop stream:
        scp.stop();
        
        % Close oscilloscope:
        clear scp;
    else
        error('No oscilloscope available with stream measurement support!');
    end
    
    format long
    MeanKulite=[MeanKulite mean(data(:,1))/(4.012/1000)*0.0689476];
    
    DC2=[DC2 mean(data(:,2))*1e3];
    
    DC1=[DC1 mean(data(:,1))*1e3];
    
    timeline = [timeline datetime];
    
    figure(1)
    subplot(2,1,1)
    plot(timeline,DC1,'b.-')
    hold on
    grid on
    title('Signal')
    xlabel(['Time [s]']); 
    ylabel('Signal amplitude [mV]');

    subplot(2,1,2)
    plot(timeline,DC2,'r.-')
    hold on
    grid on
    title('Ref')
    xlabel(['Time [s]']); 
    ylabel('Signal amplitude [mV]');
    
    pause(time)
end
Ref=MeanKulite;
mean(Ref);
std(Ref)/mean(Ref);

%% Post process
clear LibTiePie item % necessary to use TiePie after MatLab

system('cd C:\Users\cri\Documents\Etienne & start MatLab.tps'); % Reopen TiePie

DC = [DC1' DC2']*1e3; % 1e3 temporary
avg = mean(DC); % avg value in mV
var = max(DC)-min(DC); % min max values of the signal
varPercentage = var./avg*100; % percentage of the variation compared to signal

%% Plot
close all
figure
subplot(2,1,1)
plot(timeline,DC1,'b.-')
hold on
grid on
title('Signal')
xlabel(['Time [s]']); 
ylabel('Signal amplitude [mV]');

subplot(2,1,2)
plot(timeline,DC2,'r.-')
hold on
grid on
title('Ref')
xlabel(['Time [s]']); 
ylabel('Signal amplitude [mV]');

%% Saving data
save([name,' - Signal tracking - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS')]);
saveas(gcf,[name,' - Signal tracking - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS'),'.png']);

%% Test plot 
% figure
% plot(DC./avg)
% hold on
% grid on
% xlabel(['Measurement points (every ' num2str(time) ' s)']); 
% ylabel('Signal amplitude [mV]');