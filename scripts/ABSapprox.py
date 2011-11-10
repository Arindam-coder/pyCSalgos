# -*- coding: utf-8 -*-
"""
Created on Sat Nov 05 18:08:40 2011

@author: Nic
"""

import numpy as np
import scipy.io
import math

import pyCSalgos
import pyCSalgos.GAP.GAP
import pyCSalgos.SL0.SL0_approx
import pyCSalgos.OMP.omp_QR
import pyCSalgos.RecomTST.RecommendedTST

#==========================
# Algorithm functions
#==========================
def run_gap(y,M,Omega,epsilon):
  gapparams = {"num_iteration" : 1000,\
                   "greedy_level" : 0.9,\
                   "stopping_coefficient_size" : 1e-4,\
                   "l2solver" : 'pseudoinverse',\
                   "noise_level": epsilon}
  return pyCSalgos.GAP.GAP.GAP(y,M,M.T,Omega,Omega.T,gapparams,np.zeros(Omega.shape[1]))[0]

def run_sl0(y,M,Omega,D,U,S,Vt,epsilon,lbd):
  
  N,n = Omega.shape
  #D = np.linalg.pinv(Omega)
  #U,S,Vt = np.linalg.svd(D)
  aggDupper = np.dot(M,D)
  aggDlower = Vt[-(N-n):,:]
  aggD = np.concatenate((aggDupper, lbd * aggDlower))
  aggy = np.concatenate((y, np.zeros(N-n)))
  
  sigmamin = 0.001
  sigma_decrease_factor = 0.5
  mu_0 = 2
  L = 10
  return pyCSalgos.SL0.SL0_approx.SL0_approx(aggD,aggy,epsilon,sigmamin,sigma_decrease_factor,mu_0,L)

def run_bp(y,M,Omega,D,U,S,Vt,epsilon,lbd):
  
  N,n = Omega.shape
  #D = np.linalg.pinv(Omega)
  #U,S,Vt = np.linalg.svd(D)
  aggDupper = np.dot(M,D)
  aggDlower = Vt[-(N-n):,:]
  aggD = np.concatenate((aggDupper, lbd * aggDlower))
  aggy = np.concatenate((y, np.zeros(N-n)))
  
  sigmamin = 0.001
  sigma_decrease_factor = 0.5
  mu_0 = 2
  L = 10
  return pyCSalgos.SL0.SL0_approx.SL0_approx(aggD,aggy,epsilon,sigmamin,sigma_decrease_factor,mu_0,L)

def run_ompeps(y,M,Omega,D,U,S,Vt,epsilon,lbd):
  
  N,n = Omega.shape
  #D = np.linalg.pinv(Omega)
  #U,S,Vt = np.linalg.svd(D)
  aggDupper = np.dot(M,D)
  aggDlower = Vt[-(N-n):,:]
  aggD = np.concatenate((aggDupper, lbd * aggDlower))
  aggy = np.concatenate((y, np.zeros(N-n)))
  
  opts = dict()
  opts['stopCrit'] = 'mse'
  opts['stopTol'] = epsilon**2 / aggy.size
  return pyCSalgos.OMP.omp_QR.greed_omp_qr(aggy,aggD,aggD.shape[1],opts)[0]
  
def run_tst(y,M,Omega,D,U,S,Vt,epsilon,lbd):
  
  N,n = Omega.shape
  #D = np.linalg.pinv(Omega)
  #U,S,Vt = np.linalg.svd(D)
  aggDupper = np.dot(M,D)
  aggDlower = Vt[-(N-n):,:]
  aggD = np.concatenate((aggDupper, lbd * aggDlower))
  aggy = np.concatenate((y, np.zeros(N-n)))
  
  return pyCSalgos.RecomTST.RecommendedTST.RecommendedTST(aggD, aggy, nsweep=3000, tol=epsilon / np.linalg.norm(aggy))

#==========================
# Define tuples (algorithm function, name)
#==========================
gap = (run_gap, 'GAP')
sl0 = (run_sl0, 'SL0a')
bp  = (run_bp, 'BP')
ompeps = (run_ompeps, 'OMPeps')
tst = (run_tst, 'TST')

# Define which algorithms to run
#  1. Algorithms not depending on lambda
algosN = gap,   # tuple
#  2. Algorithms depending on lambda (our ABS approach)
algosL = sl0,bp,ompeps,tst   # tuple
  
#==========================
# Interface functions
#==========================
def run_multiproc(ncpus=None):
  d,sigma,deltas,rhos,lambdas,numvects,SNRdb,dosavedata,savedataname,doshowplot,dosaveplot,saveplotbase,saveplotexts = standard_params()
  run_multi(algosN, algosL, d,sigma,deltas,rhos,lambdas,numvects,SNRdb,dosavedata=dosavedata,savedataname=savedataname,\
            doparallel=True, ncpus=ncpus,\
            doshowplot=doshowplot,dosaveplot=dosaveplot,saveplotbase=saveplotbase,saveplotexts=saveplotexts)

def run():
  d,sigma,deltas,rhos,lambdas,numvects,SNRdb,dosavedata,savedataname,doshowplot,dosaveplot,saveplotbase,saveplotexts = standard_params()
  run_multi(algosN, algosL, d,sigma,deltas,rhos,lambdas,numvects,SNRdb,dosavedata=dosavedata,savedataname=savedataname,\
            doparallel=False,\
            doshowplot=doshowplot,dosaveplot=dosaveplot,saveplotbase=saveplotbase,saveplotexts=saveplotexts)
  
def standard_params():
  #Set up standard experiment parameters
  d = 50.0;
  sigma = 2.0
  #deltas = np.arange(0.05,1.,0.05)
  #rhos = np.arange(0.05,1.,0.05)
  #deltas = np.array([0.05, 0.45, 0.95])
  #rhos = np.array([0.05, 0.45, 0.95])
  deltas = np.array([0.05])
  rhos = np.array([0.05])
  #delta = 0.8;
  #rho   = 0.15;
  numvects = 100; # Number of vectors to generate
  SNRdb = 20.;    # This is norm(signal)/norm(noise), so power, not energy
  # Values for lambda
  #lambdas = [0 10.^linspace(-5, 4, 10)];
  #lambdas = np.concatenate((np.array([0]), 10**np.linspace(-5, 4, 10)))
  lambdas = np.array([0., 0.0001, 0.01, 1, 100, 10000])
  
  dosavedata = True
  savedataname = 'approx_pt_std1.mat'
  
  doshowplot = False
  dosaveplot = True
  saveplotbase = 'approx_pt_std1_'
  saveplotexts = ('png','pdf','eps')
    
  
  return d,sigma,deltas,rhos,lambdas,numvects,SNRdb,dosavedata,savedataname,\
          doshowplot,dosaveplot,saveplotbase,saveplotexts
  
#==========================
# Main functions  
#==========================
def run_multi(algosN, algosL, d, sigma, deltas, rhos, lambdas, numvects, SNRdb,
            doparallel=False, ncpus=None,\
            doshowplot=False, dosaveplot=False, saveplotbase=None, saveplotexts=None,\
            dosavedata=False, savedataname=None):

  print "This is analysis recovery ABS approximation script by Nic"
  print "Running phase transition ( run_multi() )"
  
  if doparallel:
    from multiprocessing import Pool
    
  if dosaveplot or doshowplot:
    try:
      import matplotlib
      if doshowplot:
        print "Importing matplotlib with default (GUI) backend... ",
      else:
        print "Importing matplotlib with \"Cairo\" backend... ",
        matplotlib.use('Cairo')
      import matplotlib.pyplot as plt
      import matplotlib.cm as cm
      print "OK"        
    except:
      print "FAIL"
      print "Importing matplotlib.pyplot failed. No figures at all"
      print "Try selecting a different backend"
      doshowplot = False
      dosaveplot = False
  
  # Print summary of parameters
  print "Parameters:"
  if doparallel:
    if ncpus is None:
      print "  Running in parallel with default threads using \"multiprocessing\" package"
    else:
      print "  Running in parallel with",ncpus,"threads using \"multiprocessing\" package"
  else:
    print "Running single thread"
  if doshowplot:
    print "  Showing figures"
  else:
    print "  Not showing figures"
  if dosaveplot:
    print "  Saving figures as "+saveplotbase+"* with extensions ",saveplotexts
  else:
    print "  Not saving figures"
  print "  Running algorithms",[algotuple[1] for algotuple in algosN],[algotuple[1] for algotuple in algosL]
  
  nalgosN = len(algosN)  
  nalgosL = len(algosL)
  
  meanmatrix = dict()
  for i,algo in zip(np.arange(nalgosN),algosN):
    meanmatrix[algo[1]]   = np.zeros((rhos.size, deltas.size))
  for i,algo in zip(np.arange(nalgosL),algosL):
    meanmatrix[algo[1]]   = np.zeros((lambdas.size, rhos.size, deltas.size))
  
  # Prepare parameters
  jobparams = []
  print "  (delta, rho) pairs to be run:"
  for idelta,delta in zip(np.arange(deltas.size),deltas):
    for irho,rho in zip(np.arange(rhos.size),rhos):
      
      # Generate data and operator
      Omega,x0,y,M,realnoise = generateData(d,sigma,delta,rho,numvects,SNRdb)
      
      #Save the parameters, and run after
      print "    delta = ",delta," rho = ",rho
      jobparams.append((algosN,algosL, Omega,y,lambdas,realnoise,M,x0))

  print "End of parameters"
  
  # Run
  jobresults = []
  if doparallel:
    pool = Pool(4)
    jobresults = pool.map(run_once_tuple,jobparams)
  else:
    for jobparam in jobparams:
      jobresults.append(run_once(algosN,algosL,Omega,y,lambdas,realnoise,M,x0))

  # Read results
  idx = 0
  for idelta,delta in zip(np.arange(deltas.size),deltas):
    for irho,rho in zip(np.arange(rhos.size),rhos):
      mrelerrN,mrelerrL = jobresults[idx]
      idx = idx+1
      for algotuple in algosN: 
        meanmatrix[algotuple[1]][irho,idelta] = 1 - mrelerrN[algotuple[1]]
        if meanmatrix[algotuple[1]][irho,idelta] < 0 or math.isnan(meanmatrix[algotuple[1]][irho,idelta]):
          meanmatrix[algotuple[1]][irho,idelta] = 0
      for algotuple in algosL:
        for ilbd in np.arange(lambdas.size):
          meanmatrix[algotuple[1]][ilbd,irho,idelta] = 1 - mrelerrL[algotuple[1]][ilbd]
          if meanmatrix[algotuple[1]][ilbd,irho,idelta] < 0 or math.isnan(meanmatrix[algotuple[1]][ilbd,irho,idelta]):
            meanmatrix[algotuple[1]][ilbd,irho,idelta] = 0
   
  #  # Prepare matrices to show
  #  showmats = dict()
  #  for i,algo in zip(np.arange(nalgosN),algosN):
  #    showmats[algo[1]]   = np.zeros(rhos.size, deltas.size)
  #  for i,algo in zip(np.arange(nalgosL),algosL):
  #    showmats[algo[1]]   = np.zeros(lambdas.size, rhos.size, deltas.size)

    # Save
    if dosavedata:
      tosave = dict()
      tosave['meanmatrix'] = meanmatrix
      tosave['d'] = d
      tosave['sigma'] = sigma
      tosave['deltas'] = deltas
      tosave['rhos'] = rhos
      tosave['numvects'] = numvects
      tosave['SNRdb'] = SNRdb
      tosave['lambdas'] = lambdas
      try:
        scipy.io.savemat(savedataname, tosave)
      except:
        print "Save error"
  # Show
  if doshowplot or dosaveplot:
    for algotuple in algosN:
      algoname = algotuple[1]
      plt.figure()
      plt.imshow(meanmatrix[algoname], cmap=cm.gray, interpolation='nearest',origin='lower')
      if dosaveplot:
        for ext in saveplotexts:
          plt.savefig(saveplotbase + algoname + '.' + ext)
    for algotuple in algosL:
      algoname = algotuple[1]
      for ilbd in np.arange(lambdas.size):
        plt.figure()
        plt.imshow(meanmatrix[algoname][ilbd], cmap=cm.gray, interpolation='nearest',origin='lower')
        if dosaveplot:
          for ext in saveplotexts:
            plt.savefig(saveplotbase + algoname + ('_lbd%.0e' % lambdas[ilbd]) + '.' + ext)
    if doshowplot:
      plt.show()
    
  print "Finished."
  
def run_once_tuple(t):
  return run_once(*t)

def run_once(algosN,algosL,Omega,y,lambdas,realnoise,M,x0):
  
  d = Omega.shape[1]  
  
  nalgosN = len(algosN)  
  nalgosL = len(algosL)
  
  xrec = dict()
  err = dict()
  relerr = dict()

  # Prepare storage variables for algorithms non-Lambda
  for i,algo in zip(np.arange(nalgosN),algosN):
    xrec[algo[1]]   = np.zeros((d, y.shape[1]))
    err[algo[1]]    = np.zeros(y.shape[1])
    relerr[algo[1]] = np.zeros(y.shape[1])
  # Prepare storage variables for algorithms with Lambda    
  for i,algo in zip(np.arange(nalgosL),algosL):
    xrec[algo[1]]   = np.zeros((lambdas.size, d, y.shape[1]))
    err[algo[1]]    = np.zeros((lambdas.size, y.shape[1]))
    relerr[algo[1]] = np.zeros((lambdas.size, y.shape[1]))
  
  # Run algorithms non-Lambda
  for iy in np.arange(y.shape[1]):
    for algofunc,strname in algosN:
      epsilon = 1.1 * np.linalg.norm(realnoise[:,iy])
      xrec[strname][:,iy] = algofunc(y[:,iy],M,Omega,epsilon)
      err[strname][iy]    = np.linalg.norm(x0[:,iy] - xrec[strname][:,iy])
      relerr[strname][iy] = err[strname][iy] / np.linalg.norm(x0[:,iy])
  for algotuple in algosN:
    print algotuple[1],' : avg relative error = ',np.mean(relerr[strname])  

  # Run algorithms with Lambda
  for ilbd,lbd in zip(np.arange(lambdas.size),lambdas):
    for iy in np.arange(y.shape[1]):
      D = np.linalg.pinv(Omega)
      U,S,Vt = np.linalg.svd(D)
      for algofunc,strname in algosL:
        epsilon = 1.1 * np.linalg.norm(realnoise[:,iy])
        gamma = algofunc(y[:,iy],M,Omega,D,U,S,Vt,epsilon,lbd)
        xrec[strname][ilbd,:,iy] = np.dot(D,gamma)
        err[strname][ilbd,iy]    = np.linalg.norm(x0[:,iy] - xrec[strname][ilbd,:,iy])
        relerr[strname][ilbd,iy] = err[strname][ilbd,iy] / np.linalg.norm(x0[:,iy])
    print 'Lambda = ',lbd,' :'
    for algotuple in algosL:
      print '   ',algotuple[1],' : avg relative error = ',np.mean(relerr[strname][ilbd,:])

  # Prepare results
  mrelerrN = dict()
  for algotuple in algosN:
    mrelerrN[algotuple[1]] = np.mean(relerr[algotuple[1]])
  mrelerrL = dict()
  for algotuple in algosL:
    mrelerrL[algotuple[1]] = np.mean(relerr[algotuple[1]],1)
  
  return mrelerrN,mrelerrL

def generateData(d,sigma,delta,rho,numvects,SNRdb):

  # Process parameters
  noiselevel = 1.0 / (10.0**(SNRdb/10.0));
  p = round(sigma*d);
  m = round(delta*d);
  l = round(d - rho*m);
  
  # Generate Omega and data based on parameters
  Omega = pyCSalgos.GAP.GAP.Generate_Analysis_Operator(d, p);
  # Optionally make Omega more coherent
  U,S,Vt = np.linalg.svd(Omega);
  Sdnew = S * (1+np.arange(S.size)) # Make D coherent, not Omega!
  Snew = np.vstack((np.diag(Sdnew), np.zeros((Omega.shape[0] - Omega.shape[1], Omega.shape[1]))))
  Omega = np.dot(U , np.dot(Snew,Vt))

  # Generate data  
  x0,y,M,Lambda,realnoise = pyCSalgos.GAP.GAP.Generate_Data_Known_Omega(Omega, d,p,m,l,noiselevel, numvects,'l0');
  
  return Omega,x0,y,M,realnoise
  
# Script main
if __name__ == "__main__":
  #import cProfile
  #cProfile.run('mainrun()', 'profile')    
  run()
