from rocketcea.cea_obj_w_units import CEA_Obj

class RocketEngineAnalyzerByNasaCEA():
    ceaObj = None

    def __init__(self):
        print("This is constructor")

    def __del__(self):
        print("This is destructor")

    @staticmethod
    def getNasaCeaObject_Stat(oxName=None, fuelName=None):
        ceaObj = CEA_Obj( oxName=oxName, fuelName=fuelName, pressure_units='MPa', cstar_units='m/s', temperature_units='K')
        return ceaObj

    def getNasaCeaObject(self,oxName=None, fuelName=None):
        if self.ceaObj==None:
            self.ceaObj = CEA_Obj( oxName=oxName, fuelName=fuelName, pressure_units='MPa', cstar_units='m/s', temperature_units='K')

    @staticmethod
    def getProperty_Stat(ceaObj,Pc,MR,expRatio):
        IspVac, Cstar, Tc, MW, gamma = ceaObj.get_IvacCstrTc_ChmMwGam(Pc=Pc, MR=MR, eps=expRatio)
        return IspVac, Cstar, Tc, MW, gamma

    def getProperty(self,Pc,MR,expRatio):
        IspVac, Cstar, Tc, MW, gamma = self.ceaObj.get_IvacCstrTc_ChmMwGam(Pc=Pc, MR=MR, eps=expRatio)
        return IspVac, Cstar, Tc, MW, gamma

from proptools import nozzle

class RocketEngineHandler():
    oxName   = None
    fuelName = None
    MR       = None

    At       = None
    Ae       = None
    expRatio = None
    Pc       = None

    Tc       = None
    gamma    = None
    m_molar  = None

    Cstar    = None
    IspVac   = None

    def __init__(self):
        print("This is constructor")

    def __del__(self):
        print("This is destructor")

    def setNozzleThroatArea(self,At):
        self.At = At

    def setNozzleExitArea(self,Ae):
        self.Ae = Ae

    def setNozzleExpansionRatio(self,expRatio):
        self.expRatio = expRatio

    def setChamberPressure(self,Pc):
        self.Pc = Pc

    def setNozzleExitAreaByExpansionRatio(self):
        if self.At!=None:
            self.Ae = self.expRatio * self.At

    def getExpansionRatio(self):
        return self.Ae/self.At

    @staticmethod
    def getNozzleExitPressure(Pc,gamma,expRatio):
        Pe = Pc * nozzle.pressure_from_er(expRatio, gamma)

    def getNozzleExitPressure(self):
        Pe = self.Pc * nozzle.pressure_from_er(self.getExpansionRatio(), self.gamma)
        return Pe

    @staticmethod
    def getThrust_Stat(At,Pc,Pe,Pa,gamma):
        F = nozzle.thrust(At, Pc, Pe, gamma, p_a=Pa, er=nozzle.er_from_p(Pc, Pe, gamma)) 
        return F

    def getThrust(self,Pa):
        Pe = self.getNozzleExitPressure()
        F  = RocketEngineHandler.getThrust_Stat(self.At,self.Pc,Pe=Pe,Pa=Pa,gamma=self.gamma)
        return F

    @staticmethod
    def getCstar_Stat(gamma,m_molar,Tc):
        cStar = nozzle.c_star(gamma, m_molar, Tc)
        return cStar

    @staticmethod
    def getMassFlowRate_Stat(At,Pc,Tc,gamma,m_molar):
        mDot = nozzle.mass_flow(At, Pc, Tc, gamma, m_molar)
        return mDot

    def getMassFlowRate(self):
        mDot = nozzle.mass_flow(self.At, self.Pc, self.Tc, self.gamma, self.m_molar)
        return mDot

    def setPropertyByNasaCEA(self,oxName=None,fuelName=None,Pc=None,MR=None,expRatio=None):
        ceaObj = RocketEngineAnalyzerByNasaCEA.getNasaCeaObject_Stat(oxName=oxName, fuelName=fuelName)
        IspVac, Cstar, Tc, MW, gamma = RocketEngineAnalyzerByNasaCEA.getProperty_Stat(ceaObj, Pc=Pc, MR=MR, expRatio=expRatio)

        print("MW:"+str(MW))

        self.oxName   = oxName
        self.fuelName = fuelName
        self.MR       = MR
        self.Tc       = Tc
        self.gamma    = gamma
        self.m_molar  = MW/1000
        self.Cstar    = Cstar
        self.IspVac   = IspVac
        del ceaObj

if __name__ == '__main__':
    import numpy as np
    engineHdl = RocketEngineHandler()
    engineHdl.setNozzleExpansionRatio(expRatio=2.3)
    engineHdl.setNozzleThroatArea(At=np.pi*(0.01**2)) #np.pi*0.01**2
    engineHdl.setNozzleExitAreaByExpansionRatio()
    engineHdl.setChamberPressure(1.0*10e+6)
    engineHdl.setPropertyByNasaCEA(oxName='LOX', fuelName='C2H5OH',Pc=engineHdl.Pc,MR=1.45,expRatio=engineHdl.expRatio)
    Pa   = 0.0
    mDot = engineHdl.getMassFlowRate()
    F    = engineHdl.getThrust(Pa=Pa)
    print("mDot[kg/s]:"+str(mDot))
    print("F[kN]:"+str(F/1000))
