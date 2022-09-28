# Generated with SMOP  0.41-beta
from smop.libsmop import *
# relative_error.m

    
@function
def relative_error(estimate=None,real=None,*args,**kwargs):
    varargin = relative_error.varargin
    nargin = relative_error.nargin

    #    rerr=abs(estimate-real)./(min(estimate,real)+1);
    #rerr=abs(log((estimate+0.01)./(real+0.01))./log(2));
    
    estimate=max(estimate,0)
# relative_error.m:5
    
    
    rerr=abs(estimate - real) / (min(real,estimate) + 0.1)
# relative_error.m:7
    
    #clear estimate;
    real=ravel(real)
# relative_error.m:10
    tmp=(real <= 0).nonzero()
# relative_error.m:11
    rerr=ravel(rerr)
# relative_error.m:12
    
    rerr[tmp]=[]
# relative_error.m:14
    #mask  = (real>0) | (abs(estimate-real)>10);
    
    
    #     mask  = (real>0);  
#     rerr=abs(estimate-real)./(real+0.1);
#    
#     rerr= rerr.*mask; 
#     rerr = rerr(:);
    
    ## square -> line ##
    #a=estimate(:);b=real(:);
    
    #    a(1:10)'
#    b(1:10)'
    