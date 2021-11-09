clear all
close all

%% Settings
name = '12KferruleH70e';  
file = uigetfile('*.csv');
Vch = readmatrix(file);
test = readtable(file);
timeline = table2array(test(1:end-1,1));

%% Code
Vch1 = Vch(1:end-1,2);
Vch2 = Vch(1:end-1,4);

figure
subplot(2,1,1)
plot(timeline,Vch1,'b.-')
grid on
title('Signal')
xlabel(['Time [s]']); 
ylabel('Signal amplitude [??]');

subplot(2,1,2)
plot(timeline,Vch2,'r.-')
grid on
title('Ref')
xlabel(['Time [s]']); 
ylabel('Signal amplitude [??]');

save([name,' - csv2graph - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS')]);
saveas(gcf,[name,' - csv2graph - ',datestr(now, 'dd-mmm-yyyy HH-MM-SS'),'.png']);