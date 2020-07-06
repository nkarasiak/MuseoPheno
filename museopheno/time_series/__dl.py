import numpy as np

from scipy.optimize import approx_fprime
from scipy.optimize import minimize, Bounds


# Taken from the README of phenotb
def double_logistique(params, t):
    """
    params[0] : A 
    params[1] : B 
    params[2] : x0 
    params[3] : x1
    params[4] : x2
    params[5] : x3

    t : time samples
    """
    A = params[0]
    B = params[1]
    x0 = params[2]
    x1 = params[3]
    x2 = params[4]
    x3 = params[5]

    f1 = 1/(1+np.exp((x0-t)/x1))
    f2 = 1/(1+np.exp((x2-t)/x3))
    f = A*(f1 - f2) + B

    return f


def double_logistique_grad(params, t):
    """
    """
    A = params[0]
    B = params[1]
    x0 = params[2]
    x1 = params[3]
    x2 = params[4]
    x3 = params[5]

    df = np.zeros((params.size, t.size))

    # w.r.t A
    df[0, :] = 1/(1+np.exp((x0-t)/x1)) - 1/(1+np.exp((x2-t)/x3))

    # w.r.t B
    df[1, :] = 1

    # w.r.t x0
    df[2, :] = -A / x1 * np.exp((x0-t)/x1) * 1/(1+np.exp((x0-t)/x1))**2

    # w.r.t. x1
    df[3, :] = A * (x0-t) / x1**2 * np.exp((x0-t)/x1) * 1/(1+np.exp((x0-t)/x1))**2

    # w.r.t x2
    df[4, :] = A / x3 * np.exp((x2-t)/x3) * 1/(1+np.exp((x2-t)/x3))**2

    # w.r.t. x3
    df[5, :] = -A * (x2 - t) / x3**2 * np.exp((x2-t)/x3) * 1/(1+np.exp((x2-t)/x3))**2

    return df


def cost_function(params, time_samples, samples):
    """
    """
    f = double_logistique(params, time_samples)
    eqm = ((f - samples)**2).mean()
    return eqm

def cost_function_grad(params, time_samples, samples):
    """
    """
    f = double_logistique(params, time_samples)
    df = double_logistique_grad(params, time_samples)
    diff = (f - samples)

    grad = 2 * (df*diff).mean(axis=1)

    return grad
