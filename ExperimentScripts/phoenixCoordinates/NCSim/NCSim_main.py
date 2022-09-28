# Generated with SMOP  0.41-beta
from smop.libsmop import *
# NCSim_main.m
from NCS_phoenix import phoenix as NCS_phoenix
from relative_error import relative_error
import time


@function
def NCSim_main(*args,**kwargs):
    time.sleep(10)
    varargin = NCSim_main.varargin
    nargin = NCSim_main.nargin

    
    # Simulator for Decentralized Network Coordinate Algorithms (NCSim)
    
    # 
# Version 1.1.0
# Updated on Jan. 3, 2016
# 
# Copyright (C) <2011-2016> by Yang Chen, Fudan University (chenyang@fudan.edu.cn)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
    
    ################# Code #################
    
    # raw distance matrix #
    
    #clear
    DATA = load('data_matrix.mat')
    print(sorted(DATA.keys()))
    print(DATA["king_matrix"])
    print("test")
    # PL: 169 * 169 PlanetLa data set
# Toread: 355 * 355 PlanetLab data set (collected in Mar.-Apr. 2010, 
#   used in our ACM ReArch'10 paper 'Taming the Triangle Inequality Violations with Network Coordinate System on Real Internet',
#   http://code.google.com/p/toread/) 
# kingmatrix: 1740 * 1740 King data set (http://pdos.csail.mit.edu/p2psim/kingdata/)
#   used in many Network Coordinate papers
    
    # DATA = PL; # PlanetLab data set (small)
    #DATA=copy(Toread)
# NCSim_main.m:45
    
    # DATA = king_matrix; # King data set
    
    # parameters of NCSim
    default_dimension=8
# NCSim_main.m:50
    
    max_round=3
# NCSim_main.m:51
    
    re_cdf_on=1
# NCSim_main.m:52
    
    vivaldi_option=0
# NCSim_main.m:53
    # selecting Vivaldi branch, 
#   0 - Vivaldi (basic), original Vivaldi
#   1 - Vivaldi (height),  original Vivaldi
#   2 - Vivaldi (TIV aware), used in "Towards Network Triangle Inequality
#   Violation Aware Distributed Systems" 
#   (Proc. of ACM IMC, 2007).
    ides_option=0
# NCSim_main.m:60
    # selecting IDES branch:
#   0 - IDES (nonnegative), ensuring all predicted distances to be nonnegative, 
#   used in "Phoenix: A Weight-based Network Coordinate System Using Matrix Factorization" 
#   (IEEE Transactions on Network and Service Management, 2011, Vol. 8, Issue 4)
#   1 - IDES (SVD)
#   2 - IDES(NMF)
    
    fprintf('\nNCSim (%d Nodes)\n',length(DATA))
    if (re_cdf_on == 1):
        #CDF of relative error (RE)
        fprintf('\nCDF of relative error (RE): \n\n',length(DATA))
        total_re_phoenix=[]
# NCSim_main.m:75
        total_rank_accuracy_phoenix=[]
# NCSim_main.m:75
        total_re_vivaldi=[]
# NCSim_main.m:76
        total_rank_accuracy_vivaldi=[]
# NCSim_main.m:76
        total_re_dmf=[]
# NCSim_main.m:77
        total_rank_accuracy_dmf=[]
# NCSim_main.m:77
        total_re_ides=[]
# NCSim_main.m:78
        total_rank_accuracy_ides=[]
# NCSim_main.m:78
        N=length(DATA)
# NCSim_main.m:80
        for round in arange(1,max_round).reshape(-1):
            # NC: Phoenix
            out_all,in_all,fpre_newhost,fpre_flashcrowd = NCS_phoenix(DATA,default_dimension,length(DATA),32,5,0,[],nargout=4)
# NCSim_main.m:84
            predicted_matrix=dot(out_all,in_all)
# NCSim_main.m:85
            real_matrix=copy(DATA)
# NCSim_main.m:85



            #DEBUG CHANGE
            #changing DATA to DATA[king_matrix]. Assuming that real_matrix is the king_matrix
            rerr=relative_error(predicted_matrix,DATA['king_matrix'])
# NCSim_main.m:85
            output_re=store_re(rerr.T,1,1000)
# NCSim_main.m:86
            total_re_phoenix=concat([[total_re_phoenix],[output_re]])
# NCSim_main.m:86
            fprintf('Phoenix: %.2f ',NPRE(rerr))
            phoenix_rank_accuracy=rank_accuracy(predicted_matrix,DATA)
# NCSim_main.m:88
            total_rank_accuracy_phoenix=concat([[total_rank_accuracy_phoenix],[phoenix_rank_accuracy]])
# NCSim_main.m:89
            # 0- basic Vivaldi, 1- Vivaldi (height), 2-Vivaldi TIV aware
            predicted_matrix=NCS_vivaldi_all(DATA,default_dimension,length(DATA),32,vivaldi_option)
# NCSim_main.m:94
            rerr=relative_error(predicted_matrix,DATA)
# NCSim_main.m:95
            output_re=store_re(rerr.T,1,1000)
# NCSim_main.m:96
            total_re_vivaldi=concat([[total_re_vivaldi],[output_re]])
# NCSim_main.m:96
            fprintf('Vivaldi: %.2f ',NPRE(rerr))
            vivaldi_rank_accuracy=rank_accuracy(predicted_matrix,DATA)
# NCSim_main.m:98
            total_rank_accuracy_vivaldi=concat([[total_rank_accuracy_vivaldi],[vivaldi_rank_accuracy]])
# NCSim_main.m:99
            #[out_all, in_all, fperr] = NCS_DMF(DATA, default_dimension, 32, 100, 50, 0);
            out_all,in_all=NCS_DMFSGD(DATA,32,nargout=2)
# NCSim_main.m:104
            predicted_matrix=dot(out_all,in_all)
# NCSim_main.m:105
            rerr=relative_error(predicted_matrix,DATA)
# NCSim_main.m:106
            output_re=store_re(rerr.T,1,1000)
# NCSim_main.m:108
            total_re_dmf=concat([[total_re_dmf],[output_re]])
# NCSim_main.m:108
            fprintf('DMFSGD: %.2f ',NPRE(rerr))
            dmf_rank_accuracy=rank_accuracy(predicted_matrix,DATA)
# NCSim_main.m:110
            total_rank_accuracy_dmf=concat([[total_rank_accuracy_dmf],[dmf_rank_accuracy]])
# NCSim_main.m:111
            #         
        # IDES
            tmp=randperm(N)
# NCSim_main.m:114
            landmarks=tmp(arange(1,32))
# NCSim_main.m:115
            hosts=tmp(arange(32 + 1,N))
# NCSim_main.m:116
            D_landmark=DATA(landmarks,landmarks)
# NCSim_main.m:117
            D_host2landmark=DATA(hosts,landmarks)
# NCSim_main.m:118
            out_l,in_l,out_h,in_h=NCS_IDES_all(D_landmark,D_host2landmark,default_dimension,ides_option,nargout=4)
# NCSim_main.m:120
            predicted_matrix=dot(out_h,in_h)
# NCSim_main.m:121
            real_matrix=DATA(hosts,hosts)
# NCSim_main.m:122
            rerr=relative_error(predicted_matrix,real_matrix)
# NCSim_main.m:123
            npre_ides=NPRE(rerr)
# NCSim_main.m:124
            output_re=store_re(rerr.T,1,1000)
# NCSim_main.m:125
            total_re_ides=concat([[total_re_ides],[output_re]])
# NCSim_main.m:125
            fprintf('IDES: %.2f ',NPRE(rerr))
            ides_rank_accuracy=rank_accuracy(predicted_matrix,real_matrix)
# NCSim_main.m:127
            total_rank_accuracy_ides=concat([[total_rank_accuracy_ides],[ides_rank_accuracy]])
# NCSim_main.m:128
            fprintf('\n')
        figure
        h1=plot(arange(0,1 - 1 / 1000,1 / 1000),mean(total_re_phoenix),'b--')
# NCSim_main.m:134
        set(h1,'LineWidth',2)
        hold('on')
        h2=plot(arange(0,1 - 1 / 1000,1 / 1000),mean(total_re_vivaldi),'g:')
# NCSim_main.m:135
        set(h2,'LineWidth',2)
        hold('on')
        h3=plot(arange(0,1 - 1 / 1000,1 / 1000),mean(total_re_dmf),'k-')
# NCSim_main.m:136
        set(h3,'LineWidth',2)
        hold('on')
        h4=plot(arange(0,1 - 1 / 1000,1 / 1000),mean(total_re_ides),'r-.')
# NCSim_main.m:137
        set(h4,'LineWidth',2)
        hold('on')
        h0=plot(arange(0,1),concat([0.9,0.9]),'r:')
# NCSim_main.m:138
        hold('on')
        xlabel('Relative Error','FontSize',16)
        ylabel('Cumulative Distribution Function','FontSize',16)
        axis(concat([0,1,0,1]))
        h5=legend('Phoenix','Vivaldi','DMFSGD','IDES','Location','SouthEast')
# NCSim_main.m:141
        set(h5,'FontSize',16)
        RE_filename='NCSim_RECDF_'
# NCSim_main.m:142
        tmp_size=length(DATA)
# NCSim_main.m:143
        RE_filename=strcat(RE_filename,num2str(tmp_size))
# NCSim_main.m:144
        saveas(gcf,RE_filename,'eps')
        figure
        percentage_vec=concat([arange(0.01,0.1,0.01),arange(0.2,1,0.1)])
# NCSim_main.m:150
        h1=semilogx(percentage_vec,mean(total_rank_accuracy_phoenix),'b--')
# NCSim_main.m:151
        set(h1,'LineWidth',2)
        hold('on')
        h2=semilogx(percentage_vec,mean(total_rank_accuracy_vivaldi),'g:')
# NCSim_main.m:152
        set(h2,'LineWidth',2)
        hold('on')
        h3=semilogx(percentage_vec,mean(total_rank_accuracy_dmf),'k-')
# NCSim_main.m:153
        set(h3,'LineWidth',2)
        hold('on')
        h4=semilogx(percentage_vec,mean(total_rank_accuracy_ides),'r-.')
# NCSim_main.m:154
        set(h4,'LineWidth',2)
        hold('on')
        xlabel('Fraction of Shortest Paths to Predict (Log Scale)','FontSize',16)
        ylabel('Cumulative Distribution Function','FontSize',16)
        axis(concat([dot(1 / 100,0.9),1,0,1]))
        h5=legend('Phoenix','Vivaldi','DMFSGD','IDES','Location','SouthEast')
# NCSim_main.m:157
        set(h5,'FontSize',16)
        RE_filename='Ranking_Accuracy_'
# NCSim_main.m:158
        tmp_size=length(DATA)
# NCSim_main.m:159
        RE_filename=strcat(RE_filename,num2str(tmp_size))
# NCSim_main.m:160
        saveas(gcf,RE_filename,'eps')
        phoenix_fpre=seek_percentage(mean(total_re_phoenix),0.5)
# NCSim_main.m:164
        phoenix_npre=seek_percentage(mean(total_re_phoenix),0.9)
# NCSim_main.m:164
        vivaldi_fpre=seek_percentage(mean(total_re_vivaldi),0.5)
# NCSim_main.m:165
        vivaldi_npre=seek_percentage(mean(total_re_vivaldi),0.9)
# NCSim_main.m:165
        dmf_fpre=seek_percentage(mean(total_re_dmf),0.5)
# NCSim_main.m:166
        dmf_npre=seek_percentage(mean(total_re_dmf),0.9)
# NCSim_main.m:166
        ides_fpre=seek_percentage(mean(total_re_ides),0.5)
# NCSim_main.m:167
        ides_npre=seek_percentage(mean(total_re_ides),0.9)
# NCSim_main.m:167
        fprintf('\nVivaldi|IDES|DMFSGD|Phoenix')
        fprintf('\n50th Percentile RE: %.3f %.3f %.3f %.3f\n',vivaldi_fpre,ides_fpre,dmf_fpre,phoenix_fpre)
        fprintf('90th Percentile RE: %.3f %.3f %.3f %.3f\n',vivaldi_npre,ides_npre,dmf_npre,phoenix_npre)
    
NCSim_main()
