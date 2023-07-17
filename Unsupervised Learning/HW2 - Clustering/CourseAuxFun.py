
# Import Packages
import numpy as np
import scipy as sp
from scipy.spatial.distance import cdist
from scipy.stats import multivariate_normal as MVN


#===========================Fill This===========================#
def InitKMeans(mX: np.ndarray, K: int, initMethod: int = 0, seedNum: int = 123) -> np.ndarray:
    '''
    K-Means algorithm initialization.
    Args:
        mX          - Input data with shape N x d.
        K           - Number of clusters.
        initMethod  - Initialization method: 0 - Random, 1 - K-Means++.
        seedNum     - Seed number used.
    Output:
        mC          - The initial centroids with shape K x d.
    Remarks:
        - Given the same parameters, including the `seedNum` the algorithm must be reproducible.
    '''

    np.random.seed(seedNum)
    if initMethod == 0:
        return mX[np.random.randint(mX.shape[0], size=K)]
    else:
        centroids = np.expand_dims(mX[np.random.randint(mX.shape[0])],axis=0)
        for i in range(K-1):
            distances = cdist(centroids, mX)
            centroid_index =np.argmax(distances.min(axis=0))
            centroids = np.vstack((centroids, mX[centroid_index]))
        return centroids

    pass
#===============================================================#

#===========================Fill This===========================#
def CalcKMeansObj(mX: np.ndarray, mC: np.ndarray, vL: np.ndarray) -> float:
    '''
    K-Means algorithm.
    Args:
        mX          - The data with shape N x d.
        mC          - The centroids with shape K x d.
        vL          - The labels (0, 1, .., K - 1) per sample with shape (N, )
    Output:
        objVal      - The value of the objective function of the KMeans.
    Remarks:
        - The objective function uses the squared euclidean distance.
    '''
    total_sum = 0
    for k in range(len(mC)):
        total_sum = total_sum + cdist(mX[vL== k], np.expand_dims(mC[k],axis=0)).sum()
    return total_sum
#===============================================================#

#===========================Fill This===========================#
def KMeans(mX: np.ndarray, mC: np.ndarray, numIter: int = 1000, stopThr: float = 0) -> np.ndarray:
    '''
    K-Means algorithm.
    Args:
        mX          - Input data with shape N x d.
        mC          - The initial centroids with shape K x d.
        numIter     - Number of iterations.
        stopThr     - Stopping threshold.
    Output:
        mC          - The final centroids with shape K x d.
        vL          - The labels (0, 1, .., K - 1) per sample with shape (N, )
        lO          - The objective value function per iterations (List).
    Remarks:
        - The maximum number of iterations must be `numIter`.
        - If the objective value of the algorithm doesn't improve by at least `stopThr` the iterations should stop.
    '''

    last_KMeansObj = 0
    lO = []
    for i in range(numIter):
        vL = cdist(mC, mX).argmin(axis=0)
        KMeansObj = CalcKMeansObj(mX, mC, vL)
        lO.append(KMeansObj)  
        if (KMeansObj-last_KMeansObj) == stopThr:
            break
        mC = np.array([mX[vL == k].mean(axis=0) for k in range(len(mC))])
        last_KMeansObj = KMeansObj
    return mC, vL, lO 
#===============================================================#

### GMM ###

#===========================Fill This===========================#
def InitGmm(mX: np.ndarray, K: int, seedNum: int = 123) -> np.ndarray:
    '''
    GMM algorithm initialization.
    Args:
        mX          - Input data with shape N x d.
        K           - Number of clusters.
        seedNum     - Seed number used.
    Output:
        mμ          - The initial mean vectors with shape K x d.
        tΣ          - The initial covariance matrices with shape (d x d x K).
        vW          - The initial weights of the GMM with shape K.
    Remarks:
        - Given the same parameters, including the `seedNum` the algorithm must be reproducible.
        - mμ Should be initialized by the K-Means++ algorithm.
    '''
    d=mX.shape[1]
    mμ = InitKMeans(mX,K,seedNum)
    a = np.eye(d) * mX.var()
    tΣ =  np.zeros((d,d,K)) + np.expand_dims(a,axis=2)
    vW = np.ones(K) * 1/K
    return mμ, tΣ, vW
#===============================================================#

#===========================Fill This===========================#
def CalcGmmObj(mX: np.ndarray, mμ: np.ndarray, tΣ: np.ndarray, vW: np.ndarray) -> float:
    '''
    GMM algorithm objective function.
    Args:
        mX          - The data with shape N x d.
        mμ          - The initial mean vectors with shape K x d.
        tΣ          - The initial covariance matrices with shape (d x d x K).
        vW          - The initial weights of the GMM with shape K.
    Output:
        objVal      - The value of the objective function of the GMM.
    Remarks:
        - A
    '''
    GmmObj = np.zeros(mX.shape[0])
    for i, weight in enumerate(vW):
        GmmObj = GmmObj + MVN.pdf(mX,mμ[i], tΣ[...,i]) * weight
    return -np.log(GmmObj).sum()
#===============================================================#

#===========================Fill This===========================#
def GMM(mX: np.ndarray, mμ: np.ndarray, tΣ: np.ndarray, vW: np.ndarray, numIter: int = 1000, stopThr: float = 1e-5) -> np.ndarray:
    '''
    GMM algorithm.
    Args:p
        mX          - Input data with shape N x d.
        mμ          - The initial mean vectors with shape K x d.
        tΣ          - The initial covariance matrices with shape (d x d x K).
        vW          - The initial weights of the GMM with shape K.
        numIter     - Number of iterations.
        stopThr     - Stopping threshold.
    Output:
        mμ          - The final mean vectors with shape K x d.
        tΣ          - The final covariance matrices with shape (d x d x K).
        vW          - The final weights of the GMM with shape K.
        vL          - The labels (0, 1, .., K - 1) per sample with shape (N, )
        lO          - The objective function value per iterations (List).
    Remarks:
        - The maximum number of iterations must be `numIter`.
        - If the objective value of the algorithm doesn't improve by at least `stopThr` the iterations should stop.
    '''
    last_Obj = 0
    lO = []
    for i in range(numIter):
        Obj = CalcGmmObj(mX, mμ, tΣ, vW)
        lO.append(Obj)
        x = np.array([MVN.pdf(mX, mμ[w], tΣ[...,w])* weight for w, weight in enumerate(vW)])
        if abs(Obj-last_Obj) < stopThr:
            vL = x.argmax(axis=0)
            break
        last_Obj = Obj
        p_x = (x/ x.sum(axis=0))
        N_k = p_x.sum(axis=1)
        vW = N_k / p_x.shape[1]
        mμ = (p_x @ mX) / N_k[:,None]
        tΣ = np.array([(p_x[i][:,None] * (mX - mμ[i])).T @ (mX - mμ[i]) /n for i, n in enumerate(N_k)]).T

    return mμ, tΣ, vW, vL, lO 
#===============================================================#