# Generated with SMOP  0.41-beta
from smop.libsmop import *
# NCS_phoenix.m

    # a simplified Phoenix NC system without considering node churn, distance variation, etc
    
@function
def phoenix(D,dim,N,K,C,converge_on,new_hosts,*args,**kwargs):
    varargin = phoenix.varargin
    nargin = phoenix.nargin

    # N: Number of nodes
# K: Number of Neighbors
    
    D_change=copy(D)
# NCS_phoenix.m:7
    fpre_newhost=0
# NCS_phoenix.m:9
    fpre_flashcrowd=0
# NCS_phoenix.m:10
    # Parameters
    C=10
# NCS_phoenix.m:13
    #new_host_scale = 20;
    if (converge_on == 1):
        new_host_scale=length(new_hosts)
# NCS_phoenix.m:16
    
    # Per Round -> Per Second ...
    
    # evaluate the convergence? #
    if (converge_on == 0):
        # no: only run for 30 rounds
        round_bound=30
# NCS_phoenix.m:24
    else:
        # yes: run more 30 rounds and see the convergence procedure of 10 newly
    # joinging hosts
        round_bound=60
# NCS_phoenix.m:29
    
    # 30*64 =
    closest_num=0
# NCS_phoenix.m:33
    result_matrix_seq=[]
# NCS_phoenix.m:34
    if (N == 1):
        #    [out_host, in_host] = NMF(D, dim);
        out_host=zeros(1,dim)
# NCS_phoenix.m:38
        in_host=zeros(dim,1)
# NCS_phoenix.m:39
        result_matrix_seq=[]
# NCS_phoenix.m:40
        if (converge_on == 1):
            predicted_matrix=dot(out_host,in_host)
# NCS_phoenix.m:42
            for round in arange(1,round_bound).reshape(-1):
                result_matrix_seq=concat([[result_matrix_seq],[D(1,1)]])
# NCS_phoenix.m:44
        return out_host,in_host,fpre_newhost,fpre_flashcrowd
    
    if (N < K):
        # NMF Directly #
        length(D)
        out_host,in_host=NMF(D,dim,nargout=2)
# NCS_phoenix.m:53
        result_matrix_seq=[]
# NCS_phoenix.m:54
        if (converge_on == 1):
            predicted_matrix=dot(out_host,in_host)
# NCS_phoenix.m:56
            for round in arange(1,round_bound).reshape(-1):
                result_matrix_seq=concat([[result_matrix_seq],[predicted_matrix]])
# NCS_phoenix.m:58
        return out_host,in_host,fpre_newhost,fpre_flashcrowd
    
    neighbor=zeros(N,K)
# NCS_phoenix.m:65
    error_in=zeros(1,N)
# NCS_phoenix.m:66
    error_out=zeros(1,N)
# NCS_phoenix.m:67
    for i in arange(1,N).reshape(-1):
        out_host[i,arange()]=rand(1,dim)
# NCS_phoenix.m:69
        in_host[arange(),i]=rand(dim,1)
# NCS_phoenix.m:70
        tmp=randperm(N)
# NCS_phoenix.m:73
        point=1
# NCS_phoenix.m:75
        for j in arange(1,K).reshape(-1):
            neighbor[i,j]=- 1
# NCS_phoenix.m:77
        for j in arange(1,K).reshape(-1):
            # fill in neighbor(i, j) #
            if (i != tmp(point) and D_change(i,tmp(point)) > 0):
                neighbor[i,j]=tmp(point)
# NCS_phoenix.m:82
                point=point + 1
# NCS_phoenix.m:83
            else:
                while (i == tmp(point) or D_change(i,tmp(point)) <= 0):

                    point=point + 1
# NCS_phoenix.m:86
                    if (point > N):
                        break

                #              printf('#d ', j);
#              neighbor(i, j) = tmp(point);
#              point = point+1;
            if (point > N):
                break
    
    # Out : X in the paper, In : Y in the paprt
#delta_out = delta;
#delta_in = delta;
    
    #for j=1:15
    
    w=zeros(N,K,dim)
# NCS_phoenix.m:110
    h=zeros(N,dim,K)
# NCS_phoenix.m:111
    D_host2landmark=zeros(N,K)
# NCS_phoenix.m:112
    D_host2landmark_out=zeros(N,K)
# NCS_phoenix.m:113
    D_host2landmark_in=zeros(N,K)
# NCS_phoenix.m:114
    #for j = 1:100
#for j = 1:(iteration/2)
    fpre_newhost=[]
# NCS_phoenix.m:118
    fpre_flashcrowd=[]
# NCS_phoenix.m:119
    for round in arange(1,round_bound).reshape(-1):
        #    fprintf('22');
        if (round == round_bound):
            # Stat #
            average_node_weight=zeros(1,N)
# NCS_phoenix.m:125
            node_weight_count=zeros(1,N)
# NCS_phoenix.m:126
        if (converge_on == logical_and(1,round) == floor(round_bound / 2)):
            #        rand_seq = randperm(N);
#        new_hosts =  rand_seq(1:new_host_scale);
        # Remove the NC values of the 10 new hosts
            for ii in arange(1,new_host_scale).reshape(-1):
                out_host[new_hosts(ii),arange()]=rand(1,dim)
# NCS_phoenix.m:134
                in_host[arange(),new_hosts(ii)]=rand(dim,1)
# NCS_phoenix.m:135
            # new
        #
        if (round == 1):
            # First round : Joining #
            for i in arange(1,N).reshape(-1):
                tmp=randperm(N)
# NCS_phoenix.m:145
                neighbor[i,arange()]=tmp(arange(1,K))
# NCS_phoenix.m:146
        for i in arange(1,N).reshape(-1):
            # K: number of landmarks
        # w: Kxd, h: dxK. The position vectors of all landmarks
            #         if (round == 1 & i < K)
#             continue; # Already has NC
#         end
            new_hit=0
# NCS_phoenix.m:161
            if (converge_on == logical_and(1,round) == floor(round_bound / 2)):
                for kk in arange(1,new_host_scale).reshape(-1):
                    if (new_hosts(kk) == i):
                        new_hit=1
# NCS_phoenix.m:166
                        break
            if (round == logical_or(1,new_hit) == 1):
                target_host=neighbor(i,arange())
# NCS_phoenix.m:173
                target_host=target_host(find(target_host > 0))
# NCS_phoenix.m:175
                target_host=target_host(find(D(i,target_host) >= 0))
# NCS_phoenix.m:176
                weight_out_vec=zeros(1,length(target_host))
# NCS_phoenix.m:179
                weight_in_vec=zeros(1,length(target_host))
# NCS_phoenix.m:180
                temp_w=out_host(target_host,arange())
# NCS_phoenix.m:182
                temp_h=in_host(arange(),target_host)
# NCS_phoenix.m:183
                temp_D_host2landmark=D_change(i,target_host)
# NCS_phoenix.m:184
                temp_D_host2landmark_out=temp_D_host2landmark(arange(1,length(target_host)))
# NCS_phoenix.m:185
                temp_D_host2landmark_in=temp_D_host2landmark(arange(1,length(target_host)))
# NCS_phoenix.m:186
                for ii in arange(1,length(target_host),1).reshape(-1):
                    if (D(i,target_host(ii)) < 0):
                        weight_out_vec[ii]=eps
# NCS_phoenix.m:190
                        weight_in_vec[ii]=eps
# NCS_phoenix.m:191
                    else:
                        weight_out_vec[ii]=1
# NCS_phoenix.m:193
                        weight_in_vec[ii]=1
# NCS_phoenix.m:194
                #             size(temp_h')
#             size(temp_D_host2landmark_in')
#             size(sqrt(weight_in_vec)')
                t=weight_lsqnonneg(temp_h.T,temp_D_host2landmark_in.T,sqrt(weight_in_vec).T)
# NCS_phoenix.m:200
                out_host[i,arange()]=t.T
# NCS_phoenix.m:201
                in_host[arange(),i]=weight_lsqnonneg(temp_w,temp_D_host2landmark_out.T,sqrt(weight_out_vec).T)
# NCS_phoenix.m:202
            # target
            target_host=neighbor(i,arange())
# NCS_phoenix.m:207
            #target_host
            target_host=target_host(find(target_host > 0))
# NCS_phoenix.m:210
            actual_K=length(target_host)
# NCS_phoenix.m:213
            temp_w=out_host(target_host,arange())
# NCS_phoenix.m:215
            temp_h=in_host(arange(),target_host)
# NCS_phoenix.m:216
            temp_D_host2landmark=D_change(i,target_host)
# NCS_phoenix.m:217
            score_out_vec=zeros(1,actual_K)
# NCS_phoenix.m:222
            score_in_vec=zeros(1,actual_K)
# NCS_phoenix.m:223
            score_aver_vec=zeros(1,actual_K)
# NCS_phoenix.m:224
            weight_out_vec=zeros(1,actual_K)
# NCS_phoenix.m:226
            weight_in_vec=zeros(1,actual_K)
# NCS_phoenix.m:227
            for index_nb in arange(1,actual_K).reshape(-1):
                predict_ii_in=dot(temp_w(index_nb,arange()),in_host(arange(),i))
# NCS_phoenix.m:232
                predict_ii_out=dot(out_host(i,arange()),temp_h(arange(),index_nb))
# NCS_phoenix.m:233
                s1=abs(predict_ii_out - D_change(i,target_host(index_nb)))
# NCS_phoenix.m:236
                s2=abs(predict_ii_in - D_change(i,target_host(index_nb)))
# NCS_phoenix.m:237
                score_out_vec[index_nb]=s1
# NCS_phoenix.m:239
                score_in_vec[index_nb]=s2
# NCS_phoenix.m:240
            out_threshold=median(score_out_vec)
# NCS_phoenix.m:244
            in_threshold=median(score_in_vec)
# NCS_phoenix.m:245
            for ii in arange(1,actual_K).reshape(-1):
                if (score_out_vec(ii) < out_threshold):
                    weight_out_vec[ii]=1
# NCS_phoenix.m:250
                else:
                    if (score_out_vec(ii) < dot(out_threshold,C)):
                        weight_out_vec[ii]=(out_threshold / score_out_vec(ii)) ** 2
# NCS_phoenix.m:253
                    else:
                        weight_out_vec[ii]=eps
# NCS_phoenix.m:255
                if (score_in_vec(ii) < in_threshold):
                    weight_in_vec[ii]=1
# NCS_phoenix.m:259
                else:
                    if (score_in_vec(ii) < dot(in_threshold,C)):
                        weight_in_vec[ii]=(in_threshold / score_in_vec(ii)) ** 2
# NCS_phoenix.m:262
                        #                    weight_in_vec(ii) = 1 - score_in_vec(ii);
                    else:
                        weight_in_vec[ii]=eps
# NCS_phoenix.m:265
            #         if (round == round_bound)                
#             
#             for ii=1:actual_K
#                 tmp_seq = target_host(ii);
#                 #tmp_seq
#                 average_node_weight(tmp_seq) = average_node_weight(tmp_seq) + weight_in_vec(ii) + weight_out_vec(ii);
#                 node_weight_count(tmp_seq) = node_weight_count(tmp_seq) + 1;
#             end
#         end
            #         temp_w = temp_w(index_nblist_out, :);
#         temp_h = temp_h(:, index_nblist_in);
#         temp_D_host2landmark = temp_D_host2landmark(index_nblist);
            temp_D_host2landmark_out=temp_D_host2landmark(arange(1,actual_K))
# NCS_phoenix.m:286
            temp_D_host2landmark_in=temp_D_host2landmark(arange(1,actual_K))
# NCS_phoenix.m:287
            # x = lsqnonneg(C,d) 
        # returns the vector x that minimizes norm(C*x-d) subject to x >= 0. C and d must be real.
            #  out_host(i, :) [1*d] * In_NCs[d*K] = D_host2landmark[1*K];        
        #  => out_host(i, :) * h = D_hosts2landmark[1*K];
        #  => h' * out_host(i, :)' = D_host2landmark';
#        size(temp_h)
#        size(temp_D_host2landmark)
            #        t = lsqnonneg(temp_h', temp_D_host2landmark_in');
            t=weight_lsqnonneg(temp_h.T,temp_D_host2landmark_in.T,sqrt(weight_in_vec).T)
# NCS_phoenix.m:303
            out_host[i,arange()]=t.T
# NCS_phoenix.m:304
            #  => w * in_host(:, i) = D_hosts2landmark'[K*1];
            #        in_host(:, i) = lsqnonneg(temp_w, temp_D_host2landmark_out');
            in_host[arange(),i]=weight_lsqnonneg(temp_w,temp_D_host2landmark_out.T,sqrt(weight_out_vec).T)
# NCS_phoenix.m:310
            #         w = backup_w;
#         h = backup_h;
#         D_host2landmark = backup_D_host2landmark;
        #     if (converge_on == 1 & round <= floor(round_bound/2))
#         predicted_matrix = out_host*in_host;
#         rerr = absolute_error(predicted_matrix, D);        
#         fpre_flashcrowd = [fpre_flashcrowd; median(rerr)];
#     end
        if (converge_on == logical_and(1,round) >= floor(round_bound / 2)):
            #predicted_matrix = out_host*in_host;
            predicted_matrix=dot(out_host(new_hosts,arange()),in_host(arange(),arange()))
# NCS_phoenix.m:326
            rerr=absolute_error(predicted_matrix,D(new_hosts,arange()))
# NCS_phoenix.m:327
            fpre_newhost=concat([[fpre_newhost],[median(rerr)]])
# NCS_phoenix.m:329
    
    # normalize_weight = average_node_weight ./ (node_weight_count+eps)
# all_err = Detailed_Error_SVD(D, dim);
# 
# for i=1:N
#     fprintf('(#.3f, #.3f) ', all_err(i), normalize_weight(i));
# end
    
    # Error - Weight - Relationship
#average_node_weight./node_weight_count
    
    #re=(abs(out_host * in_host-D)./(D+0.1));
#mean(re)
    
    #figure;
#plot(mean(re), average_node_weight./node_weight_count)
    
    if (converge_on == 1):
        fprintf('New Host: ')
        for i in arange(1,floor(round_bound / 2)).reshape(-1):
            fprintf('%.3f ',fpre_newhost(i))
        fprintf('\n')
        #     fprintf('FlashCrowd: ');
#     for i=1:floor(round_bound/2)
#         fprintf('#.3f ', fpre_flashcrowd(i));
#     end
#     fprintf('\n');
    
    # rerr=relative_error(out_host * in_host, D);
# fprintf('Lambda = #.3f, Relative Error: #.3f\n', lambda, NPRE(rerr));
    fpre_flashcrowd=[]
# NCS_phoenix.m:365
