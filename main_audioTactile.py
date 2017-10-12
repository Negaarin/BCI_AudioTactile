# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 16:14:22 2017 

@author: Maryam Mokheri
"""

#%% import relevant toolboxes
#clear all?
get_ipython().magic('reset -sf')
from IPython import get_ipython

import mne # a toolbox to use work with bio-signals
import numpy as np
import scipy
import os
import matplotlib.pyplot as plt
import math
import gc
from autoreject import LocalAutoRejectCV
bads=['Oz','PO7','PO8','P3','P4','CP3','C3','C4','Fz','F3','F4','T7','T8']
#%% change working directory and set parameters

#path= input("Please enter the path for the data from audioTactile oddball \
#task: ")
path="E:\Biomedical.master\Data\par020_1" #TODO : go back to input design
os.chdir(path)
montage=mne.channels.read_montage('standard_1020')
layout=mne.channels.read_layout('EEG1005')
layout2=mne.channels.read_layout('EGI256')
blockNum=5
runNum=10
samp_freq=float(1000)
resamp_freq=float(256)

#%% load data files

#fname= input("Please enter the path for the data from audioTactile oddball \
#task:\n Please include the filename in the path and make sure to put double \
#quotes around the it.") #please enter the path for the data
fname="E:\Biomedical.master\Data\par020_1\AudioTactile.vhdr" #TODO: go back to input design
#file_name= input("Please enter the name of the data from audioTactile oddball \
# task: ")
#fname= [file_path, '/' ,file_name]

# load the data from matlab interdace: sequence of stimuli, oddball stimuli, 
# and correct responses
results_all= scipy.io.loadmat("results.mat")
results_firstInChain=results_all['results']
results=results_firstInChain[0] 
sequence_stim=results[0][0]
#an object of 5,1, containing 5 object of 10,1; each containing a sequence \
# of 100, of the auditory stimulus
oddball_stim=results[0][1]
#an object of 5,1, containing 5 object of 10,1; containg the oddball stimulus\
# for each run
response_is_correct=results[0][2]
#an object of 5,1,10 containing 5 object of 1,110; containing binary data of \
#the correctness of the particpants response at the end of each run

gc.collect()
#%%
AudioTactile= mne.io.read_raw_brainvision (fname, preload=True)
AudioTactile.info['bads']=bads
gc.collect() 

#%% add event list to the brainvision raw object7
exported_events=np.load("exported_events.npy")  # have manipulated \
#brainvision.py to save events as exported_events.npy from  read marker files
exported_events[:,0]=exported_events[:,0]/(samp_freq/resamp_freq)     
events=exported_events.tolist()
AudioTactile.add_events(events)
gc.collect()
#%%
#AudioTactile.notch_filter(np.arange(60, 302, 120), filter_length='auto')
AudioTactile.resample(sfreq=resamp_freq) 
#Tim zeyl used the range 0.3, 20 Hz for filetering range. Erwei used 0.1,45 HZ 
#as filtring range. P300 info is dominant in 0.1-4 HZ. Tim used 4th order butterworth (IIR)
#and Erwei did not mention the type of filter. Alborzused FIR for his p300 program.
AudioTactile=AudioTactile.filter(.3,20, method='iir') #4th order butterworth
#h-freq is 12 to be less than Nyquist freq for 25 samp-freq
#TODO: change H-freq according to samp-freq


gc.collect()
#%% preliminary data check

AudioTactile.n_times
#AudioTactile_data= AudioTactile.get_data()
#last_chan=AudioTactile_data[16,:]
#print np.sum(last_chan)

#%% Epoch the data 
#AudioTactile_Epoch=mne.Epochs(AudioTactile, exported_events, tmin=-.1, \
#tmax=.55)
#AudioTactile_Epoch_data=AudioTactile_Epoch.get_data()
#AudioTactile_Epoch.plot_image(9, cmap='interactive')
#AudioTactile_Epoch_runs=mne.Epochs(AudioTactile, exported_events, event_id={'run start':6}, tmin=-1, tmax=60)

#%% visualize event
event_id={'Baseline Start':1,'Baseline stop':2,'run start':6,'Starto''cow': 8,\
          'frog': 9,
            'bear': 10, 'mouse': 11,
            'cat': 12, 'chick': 13, 'fox':14 , 
            'horse':15}
mne.viz.plot_events(events, AudioTactile.info['sfreq'], event_id=event_id)
#%% separate blocks 
event_time_baseline=[exported_events[i,0] for i in range(len(exported_events))\
                     if exported_events[i,2] == 1]
time_endOfExp=exported_events[len(exported_events)-1, 0]+10*resamp_freq \
#end of session(=end of last block) will be definded 10 seconds after last stimulus event is last block
AudioTactile_blocks=[None]*blockNum

# create blocks : a dictionary which its  values are cropped brainvision raw 
# objects
for i in range(blockNum):
    print "preparing block#", i+1
    AudioTactileReplica = AudioTactile.copy()
    print "Whole audio-tactile task length in sec", \
        AudioTactileReplica.n_times / resamp_freq
    tmin = event_time_baseline[i] / resamp_freq                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
    if i < blockNum - 1:                         
        tmax=event_time_baseline[i+1]/resamp_freq
    else:
        tmax=time_endOfExp/resamp_freq  # end of session(=end of last block) \
        #will be definded 10 seconds after last stimulus event is last block
    #block=i+1                       
    AudioTactile_blocks[i] = AudioTactileReplica.crop(tmin=tmin, tmax=tmax)
    print "block length in sec:", AudioTactile_blocks[i].n_times / resamp_freq
#    print tmin
#    print tmax 
#    print AudioTactile_blocks[i].n_times
#    print AudioTactile_blocks[0].n_times                         
    del AudioTactileReplica   
    

gc.collect()    
#%% separate runs 
event_time_runs=[exported_events[i,0] for i in range(len(exported_events)) if \
                 exported_events[i,2] == 6]
time_endOfExp=exported_events[len(exported_events)-1, 0]+10*resamp_freq
AudioTactile_runs=[[None]*runNum]*blockNum
blockReplica=[None]*blockNum
             
for i in range(runNum*blockNum):
    #preparing variables for the dictionary 
    block=int(math.floor(i/runNum)) #variable block : actual block number -1
    run=i%10                   #variable run : actual run number -1     
    print "********preparing block", block+1,"run#", run+1,"****************\
    *********************"
#    print "run:", run
#    print "block:", block
    
    #making a replica of the AudioTactile_blocks, so we can crop it without \
#    affecting the AudioTactile_blocks   
    blockReplica[block]=AudioTactile_blocks[block].copy()
#    print blockReplica[block]
#    print AudioTactile_blocks[block].copy()
#    print "block copy length in sec:", blockReplica[block].n_times /resamp_freq
    #setting the tmin and tmax: using the timing of events
    tmin=(event_time_runs[i] - event_time_baseline[block])/resamp_freq
#    print "tmin:", tmin, "event_time_runs[i]/resamp_freq:", event_time_runs[i]/resamp_freq, "event_time_baseline[block])/resamp_freq:", event_time_baseline[block]/resamp_freq
    if (i%10)<9:                         
         tmax=(event_time_runs[i+1] - event_time_baseline[block])/resamp_freq
#         print "tmax:", tmax, "event_time_runs[i+1]:",event_time_runs[i+1]/resamp_freq,"event_time_baseline[block])/resamp_freq:", event_time_baseline[block]/resamp_freq
#    elif (i%10==9 and block==blockNum-1) : #in the last run of last block, assign tmax=time_endOfExp        
#         tmax=(tmin+ 60*resamp_freq)/resamp_freq # assuming the last run is about 60 sec
    else:
        tmax=None
        
    temprow=AudioTactile_runs[block][:]    
    temprow[run] = blockReplica[block].crop(tmin=tmin, tmax=tmax) # cropping changes the size of primary objetc; here blockReplica[block]
    AudioTactile_runs[block]=temprow #remember how assigning a value to list of list affects other values in the list. i.e.: list[i][j]=VALUE changes all the values in column j to VALUE
#    print "run length in sec: ", AudioTactile_runs[block][run].n_times/resamp_freq
#    print event_time_baseline[block]/resamp_freq
#    print event_time_runs[i]/resamp_freq
#    if (i%10)<9: print event_time_runs[i+1]/resamp_freq 
#    print tmin
#    print tmax
#    if (i%10)<9: print "(tmax-tmin)* resamp_freq:" , (tmax-tmin)* resamp_freq
##    print "AudioTactile_runs[",block,"][",run,"].n_times:" , AudioTactile_runs[block][run].n_times
    print "AudioTactile_runs[0][0] length in sec" ,\
                            AudioTactile_runs[0][0].n_times/resamp_freq
    if i>0: print "AudioTactile_runs[0][1] length in sec" , \
                                    AudioTactile_runs[0][1].n_times/resamp_freq
    if i>9: print "AudioTactile_runs[1][0] length in sec" , \
                                    AudioTactile_runs[1][0].n_times/resamp_freq
gc.collect()    
#%% delete unnecessary variables for the sake of freeing memory
del AudioTactile_blocks
del AudioTactile 
del blockReplica
del temprow
                                    
#%% preliminary plot of epochs and feature extraction

#TODO: Normalize data and reject bad channels and epochs
#TODO: windsoring the trials
#TODO: moving average
#TODO: re-reference the electodes
#TODO: check low pass filtering

#bestChans=np.array([False, False, False, True, False, False, False, True, True, \
#                            False, False, False, False, False, False, False])
bads=['Oz','PO7','PO8','Pz','P3','P4','CP3','CP4','C3','C4','Fz','F3','F4','T7','T8'] #only Cz,Pz, and CP4   
numOfChans=16
numOfBestChans=numOfChans- len(bads) #one channel is stim (marker) channel
numOfTrainBlocks=3
x_imbalanced=np.zeros((numOfTrainBlocks*runNum*8 , numOfBestChans*155)) #8 is the num of stimuli, TODO: 168 is the length of epochs in s_freq=256, 18 for s_reamp=25
y_imbalanced=np.zeros((numOfTrainBlocks*runNum*8 , 1 ))
for b in range(numOfTrainBlocks):
    for r in range(runNum):
        print "********preparing data for the stimuli in block", b+1,"run#", r+1,"****************\
        *********************"
        trial=AudioTactile_runs[b][r]
        trial.n_times
        trial.info['bads']=bads
        trial.set_montage(montage)
        trial_rerefrenced, _=mne.set_eeg_reference(trial,[])
        trial.filter(.3,20, method='iir') #4th order butterworth
        trial.resample(sfreq=resamp_freq)
        trial_Epoch=mne.Epochs(trial_rerefrenced, exported_events, tmin=-.10, tmax=.5,\
                               baseline=(-0.1,0)) #TODO: make tmin and tmax a variable, make sure thredhold for eeg is appropriate
#        trial_Epoch.plot()
    
        trial_Epoch.load_data()
#        ar = LocalAutoRejectCV()
#        epochs_clean = ar.fit_transform(test_Epoch)
        trial_Epoch.drop_channels(trial_Epoch.info['bads'])
#        trial_Epoch.plot_image(8, cmap='interactive')
        #trial_Epoch.drop_bad() # drops bad epochs automatically
       
        #######creat feature vector for all stimuli in one run(trial) ########        
        ##trial_Epoch.drop_bad() 
        trial_x=np.zeros( (8, numOfBestChans*trial_Epoch.times.shape[0] ), dtype=float)
        trial_y=np.zeros((8,1))
        
        for i in range(8) :
            stimulus_code_str=str(i+8)
            #plot average of stim_code epochs voltage + cmap of individuals

            trial_Epoch[stimulus_code_str].plot_image(0, cmap='interactive')
            stimulus_code_avg=trial_Epoch[stimulus_code_str].average()

#            stimulus_code_avg.plot()
            stimulus_code_avg_data = stimulus_code_avg.data
            stimulus_code_avg_data_norm=\
                    stimulus_code_avg_data/np.max(\
                        np.abs(stimulus_code_avg_data)) #normalization
           
            #original signal as feature (channels concatenared after each other)
            stimulus_code_concatenatedBestChans=stimulus_code_avg_data_norm.reshape(
                np.size(stimulus_code_avg_data_norm))
            
            #r-squared as feature (channels concatenared after each other)
            
            stimulus_code_avg_rsquared= np.square((stimulus_code_avg_data-np.mean(\
                                                  stimulus_code_avg_data\
                                                  )))/(float(np.size(stimulus_code_avg_data))*\
                                                    np.var(stimulus_code_avg_data))
            stimulus_code_avg_rsquared_log=np.log(stimulus_code_avg_rsquared)
#            ax1=plt.subplot(2,4,i+1)
#            ax1.plot(np.arange(np.size(stimulus_code_avg_rsquared)),\
#                     stimulus_code_avg_rsquared[0])
#            ax1.set_xlim(50,125)
#                
                                                        
            
            trial_x[i]=stimulus_code_avg_rsquared
#            ax2=plt.subplot(2,4,i+1)
#            ax2.plot(trial_x[i])
#            ax2.set_xlim(0,155)
#            ax2.set_ylim(-.05,.05)
##    

            
#            
            
            oddball=oddball_stim[b,0][r,0] #the stimcode starts from 1 here. to get the event stim, add 7. e.g. 1--> 8: cow
            if i+1==oddball:
                trial_y[i]= 1
        x_imbalanced[((10*b+r)*8):((10*b+r)*8)+8,:]=trial_x #imbalanced data
        y_imbalanced[((10*b+r)*8):((10*b+r)*8)+8,:]=trial_y

        
#oversampling the oddball stimuli to fix imabalance of the data
xy_imbalanced=np.concatenate((x_imbalanced,y_imbalanced),axis=1)
xy_balanced=np.zeros((14*numOfTrainBlocks*runNum,xy_imbalanced.shape[1]), dtype=float) # 14 is 7 non-oddball + 7*1 oddball data 
j=0
for i in range(xy_imbalanced.shape[0]):
    if xy_imbalanced[i,-1]==0:
        xy_balanced[j,:]=xy_imbalanced[i,:]
        j=j+1
    else:
        xy_balanced[j:j+7,:]=np.repeat(xy_imbalanced[i,:].reshape(1,xy_imbalanced[i,:].shape[0])
                                        , 7, axis=0)
        j=j+7
x_balanced=xy_balanced[:,0:-1]        
y_balanced=xy_balanced[:,-1]


#downsampling data points with resamp_freq=~25Hz
x_balanced=x_balanced[:,::10]
x_imbalanced=x_imbalanced[:,::10]
             
                    
                    
                    
#trial_Epoch[oddball_str].plot_image(8, cmap='interactive')
##trial_Epoch.apply_baseline()
##trial_Epoch.plot_psd
##trial_Epoch.plot_sensors
##trial_Epoch.plot_topo_image
##trial_Epoch.plot_psd_topomap
gc.collect()

#%% preparing the data for testing the classifier 
#b_test=3
#r_test=5
#test=AudioTactile_runs[b_test][r_test]
#test.n_times
#test.set_montage(montage)
#test_Epoch=mne.Epochs(test, exported_events, tmin=-.1, tmax=.55, reject=dict(eeg=8e-5), baseline=(-0.1,0)) #TODO: make tmin and tmax a variable
##        trial_Epoch.plot()
#test.filter(.3,20, method='iir') #4th order butterworth
#test.resample(sfreq=256)
#test_Epoch.load_data()
#test_Epoch.drop_channels(test_Epoch.info['bads'])
##ar = LocalAutoRejectCV()
##epochs_clean = ar.fit_transform(test_Epoch)
##        trial_Epoch.plot_image(8, cmap='interactive')
##trial_Epoch.drop_bad() # drops bad epochs automatically
#   
########creat feature vector for all stimuli in one run(trial) ########        
###trial_Epoch.drop_bad() 
#test_x=np.zeros( (8, numOfBestChans*test_Epoch.times.shape[0] ), dtype=float)
#test_x_avg=np.zeros( (8, test_Epoch.times.shape[0] ), dtype=float)
#test_y=np.zeros((8,1))
#t=(np.arange(0,168)-25.84)*3.87 # 168 data points from -100 s to 550 s to be 
##as time points in x-axis
#for i in range(8) :
#    stimulus_code_str=str(i+8)
##    test_Epoch[stimulus_code_str].plot_image(8, cmap='interactive')
#    stimulus_code_avg=test_Epoch[stimulus_code_str].average()
##    stimulus_code_avg.plot()
#
#    stimulus_code_avg_data = stimulus_code_avg.data
#
##normalizing the channels' data
#    stimulus_code_avg_data_norm=np.zeros((16, 168)) #TODO: make dimensions variable
#    for j in range(16):
#        stimulus_code_avg_data_norm[j]=\
#            stimulus_code_avg_data[j]/max(\
#                abs(stimulus_code_avg_data[j])) #normalization
#        plt.figure(j+1)
#        plt.subplot(2,4,i+1)
#        plt.plot(t,stimulus_code_avg_data_norm[j]) 
#        plt.axis([-100,550,-1,1])
#        
#    
##concatenating all channells after each other to be fed to the classifier as 
##the feature vector    
##    stimulus_code_concatenatedBestChans=stimulus_code_avg_data[bestChans].reshape(
##        np.size(stimulus_code_avg_data[bestChans]))
##    stimulus_code_concatenatedBestChans_norm= \
##        stimulus_code_concatenatedBestChans/max(\
##            abs(stimulus_code_concatenatedBestChans)) #normalization
##    
##    test_x_concatenated[i]=stimulus_code_concatenatedBestChans_norm
##          
###using the average of bestChans EEG data as the feature vector
##    stimulus_code_avgBestChans=stimulus_code_avg_data[bestChans].mean(axis=0)
##    stimulus_code_avgBestChans_norm= \
##        stimulus_code_avgBestChans/max(\
##            abs(stimulus_code_avgBestChans)) #normalization
##    
##    test_x_avg[i]=stimulus_code_avgBestChans_norm
##    plt.subplot(2,4,i+1)         
##    plt.plot(t,test_x_avg[i]) 
##    plt.axis([-100,550,-1,1])
#
#  
#    
#    oddball=oddball_stim[b_test,0][r_test,0] #the stimcode starts from 1 here. to get the event stim, add 7. e.g. 1--> 8: cow
#    if i+1==oddball:
#        test_y[i]= 1
#
#
##downsampling test_x with resamp_freq=~25HZ
##test_x_concatenated=test_x_concatenated[:,::10]
##test_x_avg=test_x_avg[:,::10]



#%% add SSP projections to 
#projs, events = mne.preprocessing.compute_proj_eog(trial_Epoch, n_grad=1, n_mag=1, average=True)
#print(projs)
#eog_projs = projs[-2:]
#mne.viz.plot_projs_topomap(eog_projs)

#%% Independent component analysis

#from mne.preprocessing import ICA
#n_components = 16  # if float, select n_components by explained variance of PCA
#method = 'fastica'  # for comparison with EEGLAB try "extended-infomax" here
#decim = 3  # we need sufficient statistics, not all time points -> saves time
#
## we will also set state of the random number generator - ICA is a
## non-deterministic algorithm, but we want to have the same decomposition
## and the same order of components each time this tutorial is run
#random_state = 23
#ica = ICA(n_components=n_components, method=method, random_state=random_state)
#print(ica)
##reject = dict(mag=5e-12, grad=4000e-13)
#ica.fit(trial, decim=decim)
#print(ica)    
#
#ica.plot_components()
#ica.plot_properties(trial,picks=1,psd_args={'fmax': 35.})

#%% Feature extraction

#one componebt of the feature vectore could be the eeg data itself




